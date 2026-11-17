"""Ontario mixed-role energy swarm at real fleet size, on real IESO data, tested against rules.

Data (real, public): IESO hourly Ontario Demand and transmission-connected solar output, 2024 and 2025,
from reports-public.ieso.ca (PUB_Demand_<year>.csv, PUB_GenOutputbyFuelHourly_<year>.xml), kept as a
small CSV in apps/energy/data/sample/ieso_ontario_2024_2025.csv. Net load = Ontario Demand - solar.
Embedded (distribution) solar and the Industrial Conservation Initiative are already inside the IESO
demand figure, so they are not added again.

Protocol (rule first): every controller's few settings are tuned on 2024 only. 2025 (8,760 hours,
including the 24,862 MW peak of 24 June) is held out and run once. The swarm counts only if it beats
the best rule on 2025.

Controllers, all acting on the same fleet:
  * no control;
  * time-of-day rule: batteries charge 00-06 and discharge 16-21 evenly, DR fires 17-20 on hot days;
  * threshold rule: batteries close the gap to the trailing 24 h mean, DR fires above mean x (1 + band);
  * swarm: each battery and DR agent sees only the net load now, the last 7 days of net load (public),
    its own state and its role's mean state. From those it forecasts the next 24 h (yesterday and last
    week, corrected by today's error), works out the level its role's energy can shave down to, and
    acts on its own share. No central dispatcher; agents of a role agree because they see the same data;
  * bound: each day's peak cut with perfect knowledge of the day (not reachable, for scale only).

Fleet sizes and their sources are in FLEETS. Run:  python -m universal.applications.ontario_fleet
"""
from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "apps" / "energy" / "data" / "sample" / "ieso_ontario_2024_2025.csv"
OUT = REPO / "results" / "universal"
EFF = 0.85  # battery round-trip efficiency (charge side)


@dataclass(frozen=True)
class Fleet:
    name: str
    n_batt: int
    batt_mw: float          # total storage power
    hours: float            # storage duration
    solar_scale: float      # multiplier on real transmission-connected solar output
    n_dr: int
    dr_mw: float            # total demand-response power
    dr_hours: float         # max activation per day (hours at full power)
    note: str


FLEETS = {
    "2025": Fleet("Ontario 2025 (in service)", 15, 1217.0, 4.0, 1.0, 50, 516.0, 4.0,
                  "Storage: IESO expected at least 1,217 MW on its system by end of 2025 (energy-storage.news, "
                  "Expedited LT1 awards), 4 h (LT1 rule). Solar: real transmission-connected output (peak 432 MW "
                  "in 2025). DR: 316 MW Capacity Auction DR delivered at the 2025 peak + 200 MW Peak Perks "
                  "(IESO 2025 Year in Review)."),
    "2028": Fleet("Ontario 2028 (contracted)", 30, 3001.0, 4.0, (478.0 + 915.0) / 478.0, 50, 516.0, 4.0,
                  "Storage: 1,217 MW + 1,784 MW LT1 batteries due 2026-2028 (IESO, May 2024), 4 h. Solar: real "
                  "profile scaled from ~478 MW to ~1,393 MW for the 915 MW of solar backed in April 2026 "
                  "(pv-magazine). DR kept at 2025 level (conservative)."),
}
SOURCES = [
    ("IESO hourly demand", "https://reports-public.ieso.ca/public/Demand/"),
    ("IESO generator output by fuel, hourly", "https://reports-public.ieso.ca/public/GenOutputbyFuelHourly/"),
    ("IESO 2025 Year in Review (peak 24,862 MW; 316 MW DR, 200 MW Peak Perks, 1,600 MW ICI at peak; 451 MW new storage)",
     "https://ieso.ca/Corporate-IESO/Media/Year-End-Data"),
    ("IESO, 1,784 MW of LT1 battery storage, in service 2026-2028",
     "https://ieso.ca/Sector-Participants/IESO-News/2024/05/Resource-Adequacy-Update-Adding-2195-MW-of-Capacity-to-the-Grid"),
    ("energy-storage.news, 739 MW Expedited LT1 storage; IESO expects at least 1,217 MW by end 2025",
     "https://www.energy-storage.news/ontario-awards-739mw-of-battery-storage-contracts-in-canadas-biggest-procurement-to-date"),
    ("pv-magazine, Ontario backs 12 solar projects totalling 915 MW (April 2026)",
     "https://www.pv-magazine.com/2026/04/10/ontario-backs-12-solar-projects-totaling-915-mw/"),
]


def load_data() -> pd.DataFrame:
    d = pd.read_csv(DATA, parse_dates=["timestamp"])
    return d.set_index("timestamp").asfreq("h").interpolate().reset_index()


# ---------------------------------------------------------------- shared physics

def _level_down(f: np.ndarray, energy: float, power: float) -> float:
    """Lowest level L with sum(min(max(f - L, 0), power)) <= energy (shave peaks of forecast f)."""
    if energy <= 0 or f.size == 0:
        return float(f.max()) if f.size else np.inf
    lo, hi = float(f.min()) - power, float(f.max())
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if np.minimum(np.maximum(f - mid, 0), power).sum() > energy:
            lo = mid
        else:
            hi = mid
    return hi


def _level_up(f: np.ndarray, energy: float, power: float) -> float:
    """Highest level V with sum(min(max(V - f, 0), power)) <= energy (fill valleys of forecast f)."""
    if energy <= 0 or f.size == 0:
        return -np.inf
    lo, hi = float(f.min()), float(f.max()) + power
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if np.minimum(np.maximum(mid - f, 0), power).sum() > energy:
            hi = mid
        else:
            lo = mid
    return lo


class Batteries:
    def __init__(self, fl: Fleet, alive: np.ndarray | None = None):
        self.n = fl.n_batt
        self.p = np.full(self.n, fl.batt_mw / fl.n_batt)
        self.e = self.p * fl.hours
        if alive is not None:  # failed units: no power, no energy, and nobody is told
            self.p, self.e = self.p * alive, self.e * alive
        self.soc = 0.5 * self.e
        self.throughput = 0.0

    def act(self, want: float) -> float:
        """Fleet tries to deliver `want` MW (>0 discharge, <0 charge), split by room. Returns MW delivered."""
        if want > 0:
            room = np.minimum(self.p, self.soc)
        else:
            room = np.minimum(self.p, (self.e - self.soc) / EFF)
        tot = room.sum()
        if tot <= 1e-9 or abs(want) < 1e-9:
            return 0.0
        mw = min(abs(want), tot)
        share = room / tot * mw
        self.soc += -share if want > 0 else share * EFF
        self.throughput += mw
        return mw if want > 0 else -mw


class DemandResponse:
    def __init__(self, fl: Fleet):
        self.p = np.full(fl.n_dr, fl.dr_mw / fl.n_dr)
        self.budget = self.p * fl.dr_hours
        self.used = np.zeros(fl.n_dr)
        self.debt = np.zeros(fl.n_dr)

    def new_day(self):
        self.used[:] = 0

    def cut(self, mw: float) -> float:
        room = np.minimum(self.p, self.budget - self.used)
        mw = min(mw, room.sum())
        if mw <= 1e-9:
            return 0.0
        share = room / room.sum() * mw
        self.used += share
        self.debt += 0.5 * share  # half of shifted load comes back later (pre/post cooling etc.)
        return mw

    def payback(self, room_mw: float) -> float:
        back = np.minimum(self.debt, self.p)
        mw = min(back.sum(), max(room_mw, 0.0))
        if mw <= 1e-9:
            return 0.0
        self.debt -= back / back.sum() * mw
        return mw


# ---------------------------------------------------------------- controllers

def run(load: np.ndarray, hours: np.ndarray, fl: Fleet, ctrl: str, prm: dict, alive=None) -> dict:
    T = len(load)
    bat, dr = Batteries(fl, alive), DemandResponse(fl)
    net = np.empty(T)
    soc = np.empty(T)
    for t in range(T):
        soc[t] = bat.soc.sum() / max(bat.e.sum(), 1e-9)
        h = hours[t]
        if h == 0:
            dr.new_day()
        x = load[t]
        if ctrl == "none":
            net[t] = x
            continue
        hist = load[max(0, t - 24):t + 1]
        target = hist.mean()
        if ctrl == "time-of-day":
            if 17 <= h <= 20 and t >= 24 and load[t - 24:t].max() > prm["dr_hot"]:
                x -= dr.cut(dr.p.sum())
            elif h < 6:
                x += dr.payback(dr.p.sum())
            if 16 <= h <= 20:
                x -= bat.act(bat.e.sum() / 5)
            elif h < 6:
                x -= bat.act(-bat.e.sum() / 6 / EFF)
        elif ctrl == "threshold":
            if x > target * (1 + prm["band"]):
                x -= dr.cut(x - target * (1 + prm["band"]))
            elif x < target * (1 - prm["band"]):
                x += dr.payback(target * (1 - prm["band"]) - x)
            x -= bat.act(prm["gain"] * (x - target))
        elif ctrl == "swarm":
            # Forecast next 24 h from public history only: yesterday and last week, corrected by today's error.
            if t < 168:
                f = np.full(24, x)
            else:
                k = np.arange(24)  # hours t .. t+23
                f = prm["w"] * load[t - 24 + k] + (1 - prm["w"]) * load[t - 168 + k]
                err = x - f[0]
                f = f + err * prm["decay"] ** k
                f[0] = x
            # DR agents: shave the highest hours of today that their remaining budget can cover.
            left = 24 - h
            dr_room = (dr.budget - dr.used).sum()
            L_dr = _level_down(f[:left], dr_room * (1 - prm["dr_res"]), dr.p.sum())
            if x > L_dr:
                c = dr.cut(x - L_dr)
                x -= c
                f = f.copy(); f[0] = x
            else:
                V = _level_up(f, max(bat.e.sum() - bat.soc.sum(), 0) / EFF, bat.p.sum())
                x += dr.payback(V - x)
                f = f.copy(); f[0] = x
            # Battery agents: each knows its own state and the role mean, so the role's energy and power.
            n = bat.n
            e_avail = n * bat.soc.mean() * (1 - prm["res"])
            head = n * (bat.e.mean() - bat.soc.mean()) / EFF
            L = _level_down(f, e_avail, bat.p.sum())
            V = min(_level_up(f, head, bat.p.sum()), L - prm["gap"])
            if x > L:
                x -= bat.act(x - L)
            elif x < V:
                x -= bat.act(-(V - x))
        net[t] = x
    return {"net": net, "soc": soc, "cycles": bat.throughput / max(bat.e.sum(), 1e-9) / 2}


def daily_bound(load: np.ndarray, fl: Fleet) -> np.ndarray:
    """Per-day peak with perfect knowledge of the day: full fleet energy, power-capped (upper bound)."""
    out = []
    for d in range(len(load) // 24):
        f = load[24 * d:24 * d + 24]
        L = _level_down(f, fl.batt_mw * fl.hours + fl.dr_mw * fl.dr_hours, fl.batt_mw + fl.dr_mw)
        out.append(min(f.max(), L))
    return np.array(out)


def metrics(load: np.ndarray, net: np.ndarray) -> dict:
    d = len(load) // 24
    lp, np_ = load[:24 * d].reshape(d, 24).max(1), net[:24 * d].reshape(d, 24).max(1)
    top = np.argsort(load)[-50:]
    return {"annual_peak_MW": float(net.max()), "annual_peak_cut_MW": float(load.max() - net.max()),
            "mean_daily_peak_cut_MW": float((lp - np_).mean()),
            "top50_hours_cut_MW": float((load[top] - net[top]).mean()),
            "swing_cut_pct": float(100 * (1 - np.abs(np.diff(net)).mean() / np.abs(np.diff(load)).mean())),
            "std_cut_pct": float(100 * (1 - net.std() / load.std()))}


GRIDS = {
    "time-of-day": [{"dr_hot": q} for q in (19000, 20000, 21000, 22000)],
    "threshold": [{"band": b, "gain": g} for b in (0.03, 0.05, 0.08) for g in (0.5, 1.0)],
    "swarm": [{"w": 0.85, "decay": dc, "res": r, "dr_res": dr, "gap": g}
              for dc in (0.8, 0.9) for r in (0.0, 0.15, 0.3) for dr in (0.0, 0.25) for g in (0.0, 500.0, 1500.0)],
}


def score(m: dict) -> float:  # tuning objective: mean daily peak cut, plus the 50 highest hours
    return m["mean_daily_peak_cut_MW"] + m["top50_hours_cut_MW"]


def series(d: pd.DataFrame, year: int, fl: Fleet):
    s = d[d.timestamp.dt.year == year]
    net = s.ontario_demand_mw.to_numpy(float) - fl.solar_scale * s.tx_solar_mw.to_numpy(float)
    return net, s.timestamp.dt.hour.to_numpy()


def verdict(c: dict) -> dict:
    """Rule first: the swarm counts only if it beats the best rule on the held-out year."""
    rules = ("time-of-day", "threshold")
    best_rule = max(rules, key=lambda k: score(c[k]))
    return {"best_rule_on_2025": best_rule,
            "metric_by_metric_vs_each_rule": {
                rule: {m: bool(c["swarm"][m] > c[rule][m]) for m in
                       ("annual_peak_cut_MW", "mean_daily_peak_cut_MW", "top50_hours_cut_MW", "swing_cut_pct")}
                for rule in rules},
            "swarm_beats_best_rule": bool(score(c["swarm"]) > score(c[best_rule])),
            "swarm_minus_rule_daily_peak_cut_MW": c["swarm"]["mean_daily_peak_cut_MW"]
            - c[best_rule]["mean_daily_peak_cut_MW"],
            "swarm_minus_rule_annual_peak_cut_MW": c["swarm"]["annual_peak_cut_MW"]
            - c[best_rule]["annual_peak_cut_MW"]}


def experiment(fleet_key: str, d: pd.DataFrame | None = None) -> dict:
    d = load_data() if d is None else d
    fl = FLEETS[fleet_key]
    tr, trh = series(d, 2024, fl)
    te, teh = series(d, 2025, fl)
    res = {"fleet": fl.__dict__, "train": "2024 (8,784 h)", "test": "2025 (8,760 h, held out)",
           "raw_2025": {"peak_MW": float(te.max()), "std_MW": float(te.std())}, "controllers": {}}
    for ctrl in ("none", "time-of-day", "threshold", "swarm"):
        grid = GRIDS.get(ctrl, [{}])
        best = max(grid, key=lambda p: score(metrics(tr, run(tr, trh, fl, ctrl, p)["net"])))
        r = run(te, teh, fl, ctrl, best)
        res["controllers"][ctrl] = {"params": best, **metrics(te, r["net"]), "battery_cycles": r["cycles"]}
    b = daily_bound(te, fl)
    d24 = len(te) // 24
    res["controllers"]["bound (perfect daily foresight)"] = {
        "annual_peak_cut_MW": float(te.max() - b.max()),
        "mean_daily_peak_cut_MW": float((te[:24 * d24].reshape(d24, 24).max(1) - b).mean())}
    # Robustness: 30% of batteries silently fail; same settings, nobody re-tuned.
    rng = np.random.default_rng(0)
    alive = (rng.random(fl.n_batt) > 0.3).astype(float)
    res["failure_30pct"] = {"alive_units": int(alive.sum())}
    for ctrl in ("threshold", "swarm", "time-of-day"):
        r = run(te, teh, fl, ctrl, res["controllers"][ctrl]["params"], alive)
        res["failure_30pct"][ctrl] = metrics(te, r["net"])
    res["verdict"] = verdict(res["controllers"])
    return res


def write(results: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ontario-fleet.json").write_text(json.dumps(results, indent=1, default=float))
    L = ["# Ontario energy swarm at real fleet size (IESO 2024-2025)", "",
         "Generated by `python -m universal.applications.ontario_fleet` (runs locally in about 5 minutes; not in CI).",
         "Settings tuned on 2024 only; 2025 held out and run once. Net load = Ontario Demand - transmission solar.", ""]
    for k, r in results.items():
        fl = r["fleet"]
        L += [f"## {fl['name']}", "",
              f"{fl['batt_mw']:,.0f} MW / {fl['batt_mw'] * fl['hours']:,.0f} MWh storage in {fl['n_batt']} agents, "
              f"{fl['dr_mw']:,.0f} MW demand response in {fl['n_dr']} agents (max {fl['dr_hours']:.0f} h/day), "
              f"solar x{fl['solar_scale']:.2f} of real output. {fl['note']}", "",
              f"2025 raw net-load peak: {r['raw_2025']['peak_MW']:,.0f} MW.", "",
              "| Controller (2025, held out) | Annual peak cut MW | Mean daily peak cut MW | 50 highest hours cut MW "
              "| Hour-to-hour swing cut % | Spread (std) cut % | Battery cycles/yr |", "|---|---|---|---|---|---|---|"]
        for name, m in r["controllers"].items():
            if name == "none":
                continue
            L.append(f"| {name} | {m['annual_peak_cut_MW']:,.0f} | {m['mean_daily_peak_cut_MW']:,.0f} | "
                     + (f"{m['top50_hours_cut_MW']:,.0f} | {m['swing_cut_pct']:.1f} | {m['std_cut_pct']:.1f} | {m['battery_cycles']:.0f} |"
                        if "top50_hours_cut_MW" in m else "n/a | n/a | n/a | n/a |"))
        f30 = r["failure_30pct"]
        L += ["", f"30% of batteries fail without notice ({f30['alive_units']}/{fl['n_batt']} left), same settings: "
              + "; ".join(f"{k} daily peak cut {v['mean_daily_peak_cut_MW']:,.0f} MW, annual {v['annual_peak_cut_MW']:,.0f} MW"
                          for k, v in f30.items() if isinstance(v, dict)) + ".", "",
              f"Verdict: best rule on 2025 = {r['verdict']['best_rule_on_2025']}; swarm beats it: "
              f"**{r['verdict']['swarm_beats_best_rule']}** (daily peak cut "
              f"{r['verdict']['swarm_minus_rule_daily_peak_cut_MW']:+,.0f} MW, annual peak cut "
              f"{r['verdict']['swarm_minus_rule_annual_peak_cut_MW']:+,.0f} MW vs that rule).", "",
              "Metric by metric (does the swarm beat this rule?): " + "; ".join(
                  f"{rule}: " + ", ".join(f"{m.replace('_MW', '').replace('_pct', '').replace('_', ' ')} "
                                          f"{'yes' if w else 'no'}" for m, w in ws.items())
                  for rule, ws in r["verdict"]["metric_by_metric_vs_each_rule"].items()) + ".", ""]
    L += ["## Sources", ""] + [f"- {a}: {u}" for a, u in SOURCES] + [
        "", "Alberta (AESO) data could not be reached from the cloud runner; it stays a manual download "
        "(docs/universal-swarm/TODO-manual.md).", ""]
    (OUT / "ontario-fleet.md").write_text("\n".join(L))


def main() -> None:
    import sys

    if "--from-json" in sys.argv:  # rewrite the markdown from the saved results without rerunning
        res = json.loads((OUT / "ontario-fleet.json").read_text())
        for r in res.values():
            r["verdict"] = verdict(r["controllers"])
        (OUT / "ontario-fleet.json").write_text(json.dumps(res, indent=1, default=float))
        write(res)
        return
    d = load_data()
    res = {k: experiment(k, d) for k in FLEETS}
    write(res)
    print(json.dumps({k: {c: {m: round(v, 1) for m, v in x.items() if isinstance(v, float)}
                          for c, x in r["controllers"].items()} for k, r in res.items()}, indent=1))
    print(json.dumps({k: r["verdict"] for k, r in res.items()}, indent=1))


if __name__ == "__main__":
    main()
