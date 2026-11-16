"""Mixed-role energy swarm: batteries, solar farms with curtailment, and demand response.

Three roles share one goal (flatten the net load the grid sees) but act on different levers:

* **battery** agents store and release energy (state of charge limits);
* **solar** agents feed in irradiance-driven output and may curtail it when net load is very low;
* **demand-response (DR)** agents shift flexible load out of the highest hours into later
  low hours, within a daily energy budget that must be paid back.

Each agent sees only the current net load, a 24 h rolling set point, its own state, and the mean
state of other agents of the same role (alignment within the role). Roles never coordinate
centrally: the batteries respond to the net load that solar and DR have already changed, which is
how a decentralised swarm would see it. Rule-based policies here; the role structure is the one
the learned version (plan phase 3: shared weights per role, team reward) will train.

Data, in order of preference (all real):
  * Ontario IESO hourly demand  data/universal/raw/ieso/PUB_Demand_<year>.csv   (manual download)
  * Alberta AESO hourly load     data/universal/raw/aeso/*.csv                   (manual download)
  * ERCOT COAST 2020 + NREL irradiance (repo sample; used until the Canadian files are present)
Solar for Ontario/Alberta needs an irradiance series; until then a clear-sky profile is used and
the result is labelled as such.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from ..fetch import raw_dir

REPO = Path(__file__).resolve().parents[2]


def load_ieso(year: int | None = None) -> pd.DataFrame | None:
    files = sorted((raw_dir() / "ieso").glob("PUB_Demand_*.csv"))
    if year:
        files = [f for f in files if str(year) in f.name]
    if not files:
        return None
    d = pd.read_csv(files[-1], comment="\\", skiprows=3)  # IESO puts 3 header lines before the column names
    d.columns = [c.strip() for c in d.columns]
    ts = pd.to_datetime(d["Date"]) + pd.to_timedelta(d["Hour"] - 1, unit="h")
    return pd.DataFrame({"timestamp": ts, "demand_mw": d["Ontario Demand"].astype(float)})


def load_aeso() -> pd.DataFrame | None:
    files = sorted((raw_dir() / "aeso").glob("*.csv"))
    if not files:
        return None
    d = pd.read_csv(files[-1])
    tcol = next(c for c in d.columns if "date" in c.lower() or "time" in c.lower())
    lcol = next(c for c in d.columns if "load" in c.lower() or "demand" in c.lower())
    return pd.DataFrame({"timestamp": pd.to_datetime(d[tcol]), "demand_mw": d[lcol].astype(float)})


def load_region(region: str) -> tuple[pd.DataFrame, str]:
    if region == "ontario" and (d := load_ieso()) is not None:
        return d, "IESO Ontario demand (real)"
    if region == "alberta" and (d := load_aeso()) is not None:
        return d, "AESO Alberta load (real)"
    d = pd.read_csv(REPO / "apps" / "energy" / "data" / "sample" / "ercot_nrel_2020.csv")
    return d, "ERCOT COAST 2020 + NREL irradiance (real; Canadian files not downloaded yet)"


def simulate(load, ghi, roles=("battery", "solar", "dr"), n_batt=10, p_batt=100.0, e_batt=400.0,
             solar_mw=1000.0, n_dr=20, dr_mw=25.0, dr_daily_mwh=100.0):
    T = len(load)
    soc = np.full(n_batt, 0.5 * e_batt)
    debt = np.zeros(n_dr)  # energy each DR agent has shifted and still owes
    used = np.zeros(n_dr)
    net = np.empty(T)
    curtailed = 0.0
    for t in range(T):
        if t % 24 == 0:
            used[:] = 0
        target = load[max(0, t - 24):t + 1].mean()
        x = load[t]
        if "solar" in roles:
            pv = solar_mw * ghi[t] / 1000.0
            # curtail only the part that would push net load below 85% of the set point
            floor = 0.85 * target
            keep = min(pv, max(0.0, x - floor))
            curtailed += pv - keep
            x -= keep
        if "dr" in roles:
            if x > 1.05 * target:  # shift out of high hours, equal share (alignment within the role)
                room = np.minimum(dr_mw, dr_daily_mwh - used)
                cut = min(x - 1.05 * target, room.sum())
                share = room / room.sum() * cut if room.sum() > 0 else np.zeros(n_dr)
                used += share
                debt += share
                x -= cut
            elif x < 0.97 * target and debt.sum() > 0:  # pay back in low hours
                back = np.minimum(debt, dr_mw)
                add = min(back.sum(), 0.97 * target - x)
                share = back / back.sum() * add
                debt -= share
                x += add
        if "battery" in roles:
            want = x - target
            room = soc if want > 0 else e_batt - soc
            share = room / room.sum() if room.sum() > 1e-9 else np.full(n_batt, 1.0 / n_batt)
            power = np.clip(want * share, -p_batt, p_batt)
            power = np.where(power > 0, np.minimum(power, soc), -np.minimum(-power, e_batt - soc))
            soc -= power
            x -= power.sum()
        net[t] = x
    return net, curtailed


def demo(region: str = "ontario") -> dict:
    d, label = load_region(region)
    load = d["demand_mw"].to_numpy(float)
    ghi = d["GHI"].to_numpy(float) if "GHI" in d else np.zeros_like(load)
    load, ghi = load[-24 * 92:], ghi[-24 * 92:]
    out = {"data": label, "hours": int(len(load))}
    for name, roles in [("solar only (no control)", ("solar",)), ("solar + batteries", ("solar", "battery")),
                        ("solar + demand response", ("solar", "dr")),
                        ("mixed swarm: solar + DR + batteries", ("solar", "dr", "battery"))]:
        net, curt = simulate(load, ghi, roles)
        out[name] = {"peak_MW": float(net.max()), "std_MW": float(net.std()),
                     "peak_cut_vs_load_MW": float(load.max() - net.max()), "curtailed_MWh": float(curt)}
    out["raw load"] = {"peak_MW": float(load.max()), "std_MW": float(load.std())}
    return out
