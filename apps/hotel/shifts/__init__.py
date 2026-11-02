"""H2-01: open shifts filled by staff across the five hotels, as a market.

Every open shift (a call-out, a busy night) is announced; every employee is an
agent that knows its own week and bids its own cost of taking the shift:
pay at its rate (time and a half past 44 hours), travel time to a sister hotel,
and a fairness charge for each extra shift it already took this week. Agents
that may not take it do not bid: not qualified for the department, already
working then, less than 8 hours off between shifts, or over 48 hours in the
week (Ontario Employment Standards Act, ss. 17-18 and 22). The lowest bid wins
(``swarm.market.contract_net``); a shift nobody bids on goes to an agency.

Scenarios are generated from the five sample hotels; the rates and sizes are
assumptions in ``DEFAULTS``.
"""

import numpy as np
import pandas as pd
from swarm.market import contract_net

from ..energy.loads import HOTELS_CSV

KEY_METRICS = ["total_cost", "fill_rate_pct", "agency_hours", "overtime_hours", "cross_property", "max_extra_shifts"]

DEPTS = ["housekeeping", "front desk", "food and beverage"]
STARTS = [7, 15, 23]
SHIFT_H = 8

DEFAULTS = {
    "scenarios": 50,
    "seed": 0,
    "rooms_per_employee": 25,
    "open_shifts": 25,          # per week across the group
    "agency_rate": 40.0,        # $ per hour, all-in
    "travel_cost": 25.0,        # $ per cross-property shift, plus 0.5 paid hours
    "fairness": 20.0,           # $ bid charge per extra shift already taken this week
    "overtime_after": 44,       # hours per week (ESA s.22)
    "max_week_hours": 48,       # without a written agreement (ESA s.17)
    "min_rest": 8,              # hours off between shifts (ESA s.18(3))
}


def scenario(rng, hotels, p):
    staff = []
    for h, hotel in enumerate(hotels.itertuples()):
        for _ in range(max(4, int(hotel.rooms) // p["rooms_per_employee"])):
            dept = int(rng.choice(3, p=[0.5, 0.25, 0.25]))
            quals = {dept} | ({int(rng.integers(3))} if rng.random() < 0.2 else set())
            n = int(rng.choice([4, 5], p=[0.4, 0.6]))
            days = np.sort(rng.choice(7, n, replace=False))
            start = int(rng.choice(STARTS))
            shifts = [(int(d) * 24 + start, int(d) * 24 + start + SHIFT_H) for d in days]
            staff.append({"hotel": h, "quals": quals, "wage": float(rng.uniform(18, 26)), "shifts": shifts})
    open_ = []
    for _ in range(int(p["open_shifts"])):
        h = int(rng.integers(len(hotels)))
        d, s = int(rng.integers(7)), int(rng.choice(STARTS))
        open_.append({"hotel": h, "dept": int(rng.choice(3, p=[0.5, 0.25, 0.25])), "start": d * 24 + s, "end": d * 24 + s + SHIFT_H})
    open_.sort(key=lambda o: o["start"])
    return {"staff": staff, "open": open_}


def _hours(e):
    return sum(b - a for a, b in e["shifts"])


def eligible(e, o, p) -> bool:
    if o["dept"] not in e["quals"]:
        return False
    travel = 0.5 if e["hotel"] != o["hotel"] else 0.0
    if _hours(e) + SHIFT_H + travel > p["max_week_hours"]:
        return False
    rest = p["min_rest"]
    return all(o["start"] >= b + rest or o["end"] + travel + rest <= a for a, b in e["shifts"])


def shift_cost(e, o, p) -> float:
    """Pay for this shift, with overtime past ``overtime_after`` hours, plus travel."""
    travel = e["hotel"] != o["hotel"]
    paid = SHIFT_H + 0.5 * travel
    before = _hours(e)
    over = max(0.0, before + paid - p["overtime_after"]) - max(0.0, before - p["overtime_after"])
    return e["wage"] * (paid + 0.5 * over) + p["travel_cost"] * travel


def _run(s, p, choose):
    staff = [{**e, "shifts": list(e["shifts"]), "extra": 0} for e in s["staff"]]
    base_hours = [_hours(e) for e in staff]
    picks = choose(staff, s["open"], p)
    cost = agency = cross = 0.0
    for o, a in zip(s["open"], picks):
        if a is None:
            cost += p["agency_rate"] * SHIFT_H
            agency += SHIFT_H
        else:
            cross += staff[a]["hotel"] != o["hotel"]
    for e in staff:
        if e.get("added_cost"):
            cost += e["added_cost"]
    over = sum(max(0.0, _hours(e) - p["overtime_after"]) - max(0.0, h0 - p["overtime_after"])
               for e, h0 in zip(staff, base_hours))
    filled = sum(a is not None for a in picks)
    return {"total_cost": cost, "fill_rate_pct": 100 * filled / len(picks), "agency_hours": agency,
            "overtime_hours": over, "cross_property": cross,
            "max_extra_shifts": max(e["extra"] for e in staff)}


def _take(e, o, p):
    e["added_cost"] = e.get("added_cost", 0.0) + shift_cost(e, o, p)
    travel = 0.5 if e["hotel"] != o["hotel"] else 0.0
    e["shifts"].append((o["start"], o["end"] + travel))
    e["extra"] += 1


def agency_only(staff, open_, p):
    return [None] * len(open_)


def first_to_accept(staff, open_, p, rng_seed=0):
    """Offer goes out to everyone; the first qualified, rested employee to reply takes it."""
    rng = np.random.default_rng(rng_seed)
    picks = []
    for o in open_:
        order = rng.permutation(len(staff))
        a = next((int(i) for i in order if eligible(staff[i], o, p)), None)
        if a is not None:
            _take(staff[a], o, p)
        picks.append(a)
    return picks


def swarm_market(staff, open_, p):
    """Contract net: each eligible employee bids its own cost; the lowest bid wins."""
    def bid(e, o):
        if not eligible(e, o, p):
            return None
        c = shift_cost(e, o, p) + p["fairness"] * e["extra"]
        return c if c < p["agency_rate"] * SHIFT_H else None  # nobody beats the agency: let it go

    res = contract_net(open_, staff, bid, lambda e, o: _take(e, o, p))
    return [res[t] for t in range(len(open_))]


def optimal(staff, open_, p):
    """Lowest-cost plan for the whole week (integer program), for reference. It sees every
    shift at once, which the market (shifts announced as they come up) does not."""
    import pulp

    prob = pulp.LpProblem("shifts", pulp.LpMinimize)
    x = {(t, a): pulp.LpVariable(f"x_{t}_{a}", cat="Binary")
         for t, o in enumerate(open_) for a, e in enumerate(staff) if eligible(e, o, p)}
    agency = {t: pulp.LpVariable(f"g_{t}", cat="Binary") for t in range(len(open_))}
    over = {a: pulp.LpVariable(f"ot_{a}", lowBound=0) for a in range(len(staff))}
    prob += (pulp.lpSum(p["agency_rate"] * SHIFT_H * g for g in agency.values())
             + pulp.lpSum(v * (staff[a]["wage"] * (SHIFT_H + 0.5 * (staff[a]["hotel"] != open_[t]["hotel"]))
                               + p["travel_cost"] * (staff[a]["hotel"] != open_[t]["hotel"])) for (t, a), v in x.items())
             + pulp.lpSum(0.5 * staff[a]["wage"] * over[a] for a in over))
    for t in range(len(open_)):
        prob += pulp.lpSum(v for (tt, a), v in x.items() if tt == t) + agency[t] == 1
    for a, e in enumerate(staff):
        mine = [(t, v) for (t, aa), v in x.items() if aa == a]
        if not mine:
            continue
        added = pulp.lpSum(v * (SHIFT_H + 0.5 * (e["hotel"] != open_[t]["hotel"])) for t, v in mine)
        prob += _hours(e) + added <= p["max_week_hours"]
        prob += over[a] >= _hours(e) + added - p["overtime_after"] - max(0.0, _hours(e) - p["overtime_after"])
        for i, (t1, v1) in enumerate(mine):
            for t2, v2 in mine[i + 1:]:
                o1, o2 = open_[t1], open_[t2]
                if not (o2["start"] >= o1["end"] + 0.5 + p["min_rest"] or o1["start"] >= o2["end"] + 0.5 + p["min_rest"]):
                    prob += v1 + v2 <= 1
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    picks = [None] * len(open_)
    for (t, a), v in sorted(x.items(), key=lambda kv: open_[kv[0][0]]["start"]):
        if v.value() and v.value() > 0.5:
            picks[t] = a
    for t, a in enumerate(picks):
        if a is not None:
            _take(staff[a], open_[t], p)
    return picks


METHODS = {"agency for every shift": agency_only, "first to accept": first_to_accept,
           "swarm market": swarm_market, "optimal plan (reference)": optimal}


def benchmark_rows(cfg: dict) -> list[dict]:
    p = {**DEFAULTS, **(cfg.get("env") or {})}
    hotels = pd.read_csv(cfg.get("hotels_csv") or HOTELS_CSV)
    rng = np.random.default_rng(int(p["seed"]))
    scenarios = [scenario(rng, hotels, p) for _ in range(int(p["scenarios"]))]
    rows = []
    for name, method in METHODS.items():
        res = [_run(s, p, method) for s in scenarios]
        rows.append({"app": "hotel-shifts", "policy": name,
                     **{k: float(np.mean([r[k] for r in res])) for k in res[0]}, "scenarios": len(scenarios)})
    return rows
