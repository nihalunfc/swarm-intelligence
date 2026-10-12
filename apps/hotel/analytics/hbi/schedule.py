"""Housekeeping schedule builder (H2-05).

Demand comes from the shared sample dataset: departures and stayovers per day
are converted into labour hours with room standards. A mixed-integer model
then assigns shifts to employees. An independent rule checker validates any
schedule, optimized or manual, against the Ontario Employment Standards Act
hours-of-work rules.
"""

from dataclasses import dataclass, field
from math import ceil

import numpy as np
import pandas as pd
import pulp

from . import config

HOTEL_ID = 1
CHECKOUT_MIN = 30           # minutes per departure room
STAYOVER_MIN = 20           # minutes per stayover room
PRODUCTIVE_HOURS = 7.5      # cleaning hours in an 8-hour attendant shift
RA_PER_INSPECTOR = 8
OCCUPIED_PER_EVENING = 150  # evening attendant per occupied rooms (turndown, requests)
MIN_REST_HOURS = 11         # stricter than the 8-hour between-shift rule; also satisfies 11 hours off per day
WEEKLY_OT_THRESHOLD = 44
WEEKLY_MAX_HOURS = 48

# code: (label, role, start hour, end hour, paid hours)
SHIFTS = {
    "AM": ("Room attendant 07:00-15:30", "RA", 7.0, 15.5, 8.0),
    "MID": ("Room attendant 09:00-17:30", "RA", 9.0, 17.5, 8.0),
    "SH": ("Room attendant 09:00-13:00", "RA", 9.0, 13.0, 4.0),
    "INS": ("Inspector 07:00-15:30", "INSP", 7.0, 15.5, 8.0),
    "PM": ("Evening attendant 15:00-23:00", "EVE", 15.0, 23.0, 7.5),
}

FIRST = ["Amara", "Ben", "Carmen", "Deepa", "Elena", "Farid", "Grace", "Hiro", "Isabel", "Jamal", "Kavya", "Liam",
         "Maria", "Nadia", "Omar", "Priya", "Quinn", "Rosa", "Samir", "Tara", "Uma", "Victor", "Wei", "Ximena",
         "Yusuf", "Zara", "Ana", "Bogdan", "Chloe", "Dinesh", "Esther", "Femi", "Gloria", "Hamid", "Irene",
         "Jorge", "Ken", "Lucia", "Mei", "Nikhil", "Olga", "Pedro", "Rania", "Sofia"]
LAST = list("ABCDEFGHJKLMNPRSTVWY")


@dataclass
class Employee:
    emp_id: str
    name: str
    contract: str               # FT or PT
    shifts: list                # allowed shift codes
    wage: float
    seniority: int
    unavailable: list = field(default_factory=list)   # day indexes 0..6
    requested_off: list = field(default_factory=list)
    prefers_printed: bool = False

    @property
    def min_hours(self):
        return 32 if self.contract == "FT" else 0

    @property
    def max_shifts(self):
        return 5 if self.contract == "FT" else 4


def roster(seed: int = config.SEED) -> list:
    rng = np.random.default_rng(seed + 7)
    people = []
    plan = ([("FT", ["AM", "MID"], 19.75)] * 26 + [("FT", ["AM", "MID", "INS"], 21.50)] * 4
            + [("FT", ["INS", "AM"], 23.00)] * 3 + [("FT", ["PM"], 20.25)] * 4
            + [("PT", ["SH", "AM"], 19.25)] * 5 + [("PT", ["PM", "SH"], 19.25)] * 2)
    for i, (contract, allowed, wage) in enumerate(plan):
        sen = int(rng.integers(0, 26))
        unavailable = sorted(rng.choice(7, size=int(rng.integers(0, 2)), replace=False).tolist()) if contract == "PT" else []
        requested = sorted(rng.choice(7, size=int(rng.choice([0, 1, 1, 2])), replace=False).tolist())
        requested = [d for d in requested if d not in unavailable]
        people.append(Employee(
            emp_id=f"HK{101 + i}", name=f"{FIRST[i]} {LAST[i % len(LAST)]}.", contract=contract, shifts=allowed,
            wage=round(wage + 0.18 * min(sen, 15), 2), seniority=sen, unavailable=unavailable,
            requested_off=requested, prefers_printed=bool(sen >= 22 or rng.random() < 0.08)))
    return people


def demand_for_week(nights: pd.DataFrame, bookings: pd.DataFrame, start: pd.Timestamp,
                    forecast_occ: pd.Series | None = None) -> pd.DataFrame:
    """Occupied rooms, departures and stayovers per day for the scheduled hotel."""
    days = pd.date_range(start, periods=7, freq="D")
    n = nights[(nights["hotel_id"] == HOTEL_ID) & nights["status"].isin(["Checked out", "Confirmed"])]
    occ = n.groupby("stay_date")["rooms"].sum()
    b = bookings[(bookings["hotel_id"] == HOTEL_ID) & bookings["status"].isin(["Checked out", "Confirmed"])].copy()
    b["departure"] = b["arrival_date"] + pd.to_timedelta(b["nights"], unit="D")
    dep = b.groupby("departure")["rooms"].sum()
    rows = []
    for d in days:
        occupied_prev = float(occ.get(d - pd.Timedelta(days=1), 0))
        departures = float(dep.get(d, 0))
        if forecast_occ is not None and d in forecast_occ.index:
            scale = forecast_occ[d] / max(float(occ.get(d, 0)), 1.0)
            occupied_prev *= max(scale, 1.0)
            departures *= max(scale, 1.0)
        stayovers = max(occupied_prev - departures, 0)
        ra_hours = (departures * CHECKOUT_MIN + stayovers * STAYOVER_MIN) / 60
        ra_needed = ceil(ra_hours / PRODUCTIVE_HOURS)
        rows.append({"date": d.strftime("%Y-%m-%d"), "day": d.strftime("%a"),
                     "occupied_last_night": round(occupied_prev), "departures": round(departures),
                     "stayovers": round(stayovers), "cleaning_hours": round(ra_hours, 1),
                     "attendants_needed": ra_needed,
                     "inspectors_needed": ceil(ra_needed / RA_PER_INSPECTOR),
                     "evening_needed": ceil(float(occ.get(d, occupied_prev)) / OCCUPIED_PER_EVENING)})
    return pd.DataFrame(rows)


def optimize(staff: list, demand: pd.DataFrame, time_limit: int = 60) -> dict:
    days = range(7)
    prob = pulp.LpProblem("housekeeping_week", pulp.LpMinimize)
    x = {(e.emp_id, d, s): pulp.LpVariable(f"x_{e.emp_id}_{d}_{s}", cat="Binary")
         for e in staff for d in days for s in e.shifts if d not in e.unavailable}
    by_emp = {e.emp_id: e for e in staff}

    hrs = lambda s: SHIFTS[s][4]
    ra_hours = {d: pulp.lpSum(v * (hrs(s) if s != "SH" else 4.0) * (PRODUCTIVE_HOURS / 8.0)
                              for (eid, dd, s), v in x.items() if dd == d and SHIFTS[s][1] == "RA") for d in days}
    short_ra = {d: pulp.LpVariable(f"short_ra_{d}", lowBound=0) for d in days}
    over_ra = {d: pulp.LpVariable(f"over_ra_{d}", lowBound=0) for d in days}
    short_ins = {d: pulp.LpVariable(f"short_ins_{d}", lowBound=0) for d in days}
    short_eve = {d: pulp.LpVariable(f"short_eve_{d}", lowBound=0) for d in days}
    ot = {e.emp_id: pulp.LpVariable(f"ot_{e.emp_id}", lowBound=0, upBound=WEEKLY_MAX_HOURS - WEEKLY_OT_THRESHOLD)
          for e in staff}
    under = {e.emp_id: pulp.LpVariable(f"under_{e.emp_id}", lowBound=0) for e in staff}
    wk = {e.emp_id: pulp.LpVariable(f"wk_{e.emp_id}", lowBound=0) for e in staff}
    max_wk = pulp.LpVariable("max_weekend_shifts", lowBound=0)

    for _, r in demand.iterrows():
        d = int(_)
        need = r["cleaning_hours"]
        prob += ra_hours[d] + short_ra[d] - over_ra[d] == need
        prob += pulp.lpSum(v for (eid, dd, s), v in x.items() if dd == d and s == "INS") + short_ins[d] >= r["inspectors_needed"]
        prob += pulp.lpSum(v for (eid, dd, s), v in x.items() if dd == d and s == "PM") + short_eve[d] >= r["evening_needed"]

    for e in staff:
        mine = {(d, s): v for (eid, d, s), v in x.items() if eid == e.emp_id}
        for d in days:
            prob += pulp.lpSum(v for (dd, s), v in mine.items() if dd == d) <= 1
        for d in range(6):
            for s1 in e.shifts:
                for s2 in e.shifts:
                    rest = 24 + SHIFTS[s2][2] - SHIFTS[s1][3]
                    if rest < MIN_REST_HOURS and (d, s1) in mine and (d + 1, s2) in mine:
                        prob += mine[(d, s1)] + mine[(d + 1, s2)] <= 1
        total = pulp.lpSum(v * hrs(s) for (d, s), v in mine.items())
        prob += pulp.lpSum(mine.values()) <= e.max_shifts
        prob += total <= WEEKLY_OT_THRESHOLD + ot[e.emp_id]
        prob += total + under[e.emp_id] >= e.min_hours
        prob += wk[e.emp_id] == pulp.lpSum(v for (d, s), v in mine.items() if d in (5, 6))
        if e.contract == "FT":
            prob += wk[e.emp_id] <= max_wk

    request_breaks = pulp.lpSum(v for (eid, d, s), v in x.items() if d in by_emp[eid].requested_off)
    wage_cost = pulp.lpSum(v * hrs(s) * by_emp[eid].wage for (eid, d, s), v in x.items())
    prob += (wage_cost
             + pulp.lpSum(ot[e.emp_id] * e.wage * 0.5 for e in staff)
             + 250 * pulp.lpSum(short_ra.values()) + 2500 * pulp.lpSum(short_ins.values())
             + 2500 * pulp.lpSum(short_eve.values()) + 18 * pulp.lpSum(over_ra.values())
             + 60 * pulp.lpSum(under.values()) + 45 * request_breaks + 25 * max_wk)
    status = prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit))
    grid = {e.emp_id: ["OFF"] * 7 for e in staff}
    for (eid, d, s), v in x.items():
        if v.value() and v.value() > 0.5:
            grid[eid][d] = s
    for e in staff:
        for d in e.unavailable:
            grid[e.emp_id][d] = "N/A"
    return {"status": pulp.LpStatus[status], "grid": grid, "objective": pulp.value(prob.objective)}


def manual_baseline(staff: list) -> dict:
    """A typical fixed pattern: the same shifts every week, regardless of demand."""
    grid = {}
    ft_ra = [e for e in staff if e.contract == "FT" and e.shifts[0] in ("AM",)]
    ft_ra_sorted = sorted(ft_ra, key=lambda e: -e.seniority)
    senior = {e.emp_id for e in ft_ra_sorted[: len(ft_ra_sorted) // 2]}
    for e in staff:
        g = ["OFF"] * 7
        if e.contract == "FT" and e.shifts[0] == "PM":
            for d in (2, 3, 4, 5, 6):
                g[d] = "PM"
        elif e.contract == "FT" and e.shifts[0] == "INS":
            for d in range(5):
                g[d] = "INS"
        elif e.contract == "FT":
            work = range(5) if e.emp_id in senior else (2, 3, 4, 5, 6)
            for d in work:
                g[d] = "AM"
        else:
            for d in (5, 6):
                g[d] = "SH" if "SH" in e.shifts else "PM"
        for d in e.unavailable:
            g[d] = "N/A"
        grid[e.emp_id] = g
    return {"status": "Manual pattern", "grid": grid}


def check_rules(staff: list, grid: dict) -> list:
    """Independent check of Ontario ESA hours-of-work rules for any schedule."""
    by_emp = {e.emp_id: e for e in staff}
    results = {k: 0 for k in ("eleven_hours_rest", "one_shift_per_day", "weekly_rest_24h", "weekly_max_48",
                             "three_hour_minimum", "availability")}
    ot_hours = 0.0
    for eid, g in grid.items():
        e = by_emp[eid]
        work = [(d, s) for d, s in enumerate(g) if s in SHIFTS]
        for (d1, s1), (d2, s2) in zip(work, work[1:]):
            gap = (d2 - d1) * 24 + SHIFTS[s2][2] - SHIFTS[s1][3]
            if gap < MIN_REST_HOURS:
                results["eleven_hours_rest"] += 1
        if len(work) > 6:
            results["weekly_rest_24h"] += 1
        hours = sum(SHIFTS[s][4] for _, s in work)
        if hours > WEEKLY_MAX_HOURS:
            results["weekly_max_48"] += 1
        ot_hours += max(0.0, hours - WEEKLY_OT_THRESHOLD)
        results["three_hour_minimum"] += sum(1 for _, s in work if SHIFTS[s][4] < 3)
        results["availability"] += sum(1 for d, s in work if d in e.unavailable)
    labels = {
        "eleven_hours_rest": "At least 11 hours off between shifts (covers the daily-rest and between-shift rules)",
        "one_shift_per_day": "No more than one shift per day",
        "weekly_rest_24h": "At least 24 consecutive hours off in the week",
        "weekly_max_48": "No more than 48 hours in the week",
        "three_hour_minimum": "No shift shorter than three hours",
        "availability": "No shifts on days the employee is unavailable",
    }
    return [{"rule": labels[k], "violations": v, "passed": v == 0} for k, v in results.items()]


def evaluate(staff: list, grid: dict, demand: pd.DataFrame) -> dict:
    by_emp = {e.emp_id: e for e in staff}
    cover = []
    for d, r in demand.iterrows():
        ra_h = sum((SHIFTS[g[d]][4] if g[d] != "SH" else 4.0) * PRODUCTIVE_HOURS / 8.0
                   for g in grid.values() if g[d] in SHIFTS and SHIFTS[g[d]][1] == "RA")
        ins = sum(1 for g in grid.values() if g[d] == "INS")
        eve = sum(1 for g in grid.values() if g[d] == "PM")
        cover.append({"day": r["day"], "cleaning_hours_needed": r["cleaning_hours"],
                      "cleaning_hours_scheduled": round(ra_h, 1),
                      "gap_hours": round(ra_h - r["cleaning_hours"], 1),
                      "inspectors_needed": int(r["inspectors_needed"]), "inspectors_scheduled": ins,
                      "evening_needed": int(r["evening_needed"]), "evening_scheduled": eve})
    cov = pd.DataFrame(cover)
    shortfall = float(-cov["gap_hours"].clip(upper=0).sum())
    surplus = float(cov["gap_hours"].clip(lower=0).sum())
    hours = {eid: sum(SHIFTS[s][4] for s in g if s in SHIFTS) for eid, g in grid.items()}
    wages = sum(SHIFTS[s][4] * by_emp[eid].wage for eid, g in grid.items() for s in g if s in SHIFTS)
    ot = sum(max(0.0, h - WEEKLY_OT_THRESHOLD) for h in hours.values())
    missing_ins = int(sum(max(0, c["inspectors_needed"] - c["inspectors_scheduled"]) for c in cover))
    missing_eve = int(sum(max(0, c["evening_needed"] - c["evening_scheduled"]) for c in cover))
    # Uncovered work must be filled by call-ins at overtime pay (1.5 times the regular rate).
    avg_wage = float(np.mean([e.wage for e in staff if "AM" in e.shifts]))
    callin_hours = shortfall / (PRODUCTIVE_HOURS / 8.0) + 8.0 * missing_ins + 7.5 * missing_eve
    callin_cost = callin_hours * avg_wage * 1.5
    requests = [(eid, d) for eid, e in by_emp.items() for d in e.requested_off]
    honoured = sum(1 for eid, d in requests if grid[eid][d] not in SHIFTS)
    weekend = [sum(1 for d in (5, 6) if grid[e.emp_id][d] in SHIFTS) for e in staff if e.contract == "FT"]
    return {
        "coverage": cover,
        "scheduled_hours": round(sum(hours.values()), 1),
        "wage_cost": round(wages, 2),
        "shortfall_hours": round(shortfall, 1),
        "missing_inspector_shifts": missing_ins,
        "missing_evening_shifts": missing_eve,
        "extra_shifts_needed": int(ceil(shortfall / PRODUCTIVE_HOURS) + missing_ins + missing_eve),
        "surplus_hours": round(surplus, 1),
        "callin_overtime_cost": round(callin_cost, 2),
        "total_cost": round(wages + callin_cost, 2),
        "overtime_hours": round(ot, 1),
        "requests_total": len(requests),
        "requests_honoured": honoured,
        "max_weekend_shifts": int(max(weekend)),
        "employees_scheduled": sum(1 for h in hours.values() if h > 0),
    }
