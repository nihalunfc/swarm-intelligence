"""Export analysis results as JSON and Excel files for the static site."""

import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from . import config, demand as D, schedule as S
from .excel import write_schedule

SCENARIOS = [
    ("coming", "Coming week (forecast)", "The week of October 5, leading into the Canadian Thanksgiving long weekend, built from bookings on hand plus expected late bookings",
     "2026-10-05", True),
    ("summer", "Peak summer week", "A busy August week from last summer's actual bookings", "2026-08-10", False),
    ("winter", "Quiet winter week", "A January week from last winter's actual bookings", "2026-01-19", False),
]


def _clean(o):
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if np.isnan(o) else round(float(o), 4)
    if isinstance(o, (pd.Timestamp,)):
        return o.strftime("%Y-%m-%d")
    return o


def _dump(name: str, obj) -> None:
    config.SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    (config.SITE_DATA_DIR / name).write_text(json.dumps(_clean(obj), separators=(",", ":")))


def revenue(X: dict, otb: pd.DataFrame) -> dict:
    k = D.summary_kpis(X["daily"], X["hotels"])
    unc = D.unconstrain(otb, X["daily"])
    fc = D.pickup_forecast(otb, X["daily"], unc)
    events = D.event_uplift(X["daily"], X["dates"])
    fwd = D.forward_calendar(X["nights"], X["daily"], X["dates"], X["hotels"], fc["pickup_u"], events)
    cal = D.portfolio_calendar(fwd, X["dates"])
    fwd["forecast_occ"] = np.minimum(fwd["expected_demand"], fwd["capacity"]) / fwd["capacity"]
    by_hotel = fwd.pivot(index="date", columns="hotel_id", values="forecast_occ")

    u = unc[unc["stay_date"] >= D.LTM_START].copy()
    lost_true = float((u["true_demand"] - u["rooms_sold"]).sum())
    lost_est = float((u["estimated_demand"] - u["rooms_sold"]).sum())
    u["lost_est"] = u["estimated_demand"] - u["rooms_sold"]
    top = u.sort_values("lost_est", ascending=False).head(8)
    names = X["hotels"].set_index("hotel_id")["hotel_name"]

    calendar = []
    for _, r in cal.iterrows():
        calendar.append({
            "date": r["date"].strftime("%Y-%m-%d"), "tier": r["tier"],
            "forecast": round(float(r["forecast_occ"]), 3), "on_books": round(float(r["otb_occ"]), 3),
            "last_year": round(float(r["stly_occ"]), 3),
            "note": ", ".join(x for x in (r["holiday_ca"], r["holiday_us"], r["event"]) if isinstance(x, str) and x),
            "hotels": [round(float(by_hotel.at[r["date"], h]), 3) for h in by_hotel.columns],
        })
    trend = D.monthly_trend(X["daily"])
    return {
        "as_of": str(config.AS_OF),
        "ltm": k["ltm"], "prior": k["prior"], "hotels": k["by_hotel"],
        "monthly": trend[["month", "occupancy", "adr", "revpar", "rev"]].rename(columns={"rev": "revenue"}).to_dict("records"),
        "weekday": D.weekday_profile(X["daily"])[["day", "occupancy", "adr"]].to_dict("records"),
        "calendar": calendar,
        "tier_counts": cal["tier"].value_counts().to_dict(),
        "brief": D.selling_brief(cal),
        "booking_curves": D.booking_curves(otb, X["daily"], X["dates"]),
        "unconstrained": {
            "sold_out_nights": int(len(u)),
            "rooms_turned_away_true": lost_true,
            "rooms_turned_away_estimated": lost_est,
            "recovery_share": lost_est / lost_true if lost_true else None,
            "night_level_error": float(((u["estimated_demand"] - u["true_demand"]).abs() / u["true_demand"]).mean()),
            "value_estimated": float((u["lost_est"] * u["adr"]).sum()),
            "top_nights": [{"date": r["stay_date"].strftime("%a %b %d, %Y"), "hotel": names[r["hotel_id"]],
                            "rooms_sold": int(r["rooms_sold"]), "estimated_demand": int(round(r["estimated_demand"])),
                            "true_demand": int(r["true_demand"]), "adr": float(r["adr"])} for _, r in top.iterrows()],
        },
        "forecast_backtest": fc["backtest"],
        "channels": D.channel_mix(X["bookings"], X["channels"])[
            ["channel", "channel_name", "room_nights", "share", "adr", "acquisition_cost", "net_adr", "acquisition_spend"]
        ].to_dict("records"),
        "cancellations": D.cancellations(X["bookings"]),
        "length_of_stay": D.length_of_stay(X["bookings"]),
        "events": events[["event", "nights", "occ", "occ_base", "adr", "adr_base", "adr_uplift"]].to_dict("records"),
        "hotel_names": names.to_dict(),
    }, fwd


def schedules(X: dict, fwd: pd.DataFrame) -> dict:
    staff = S.roster()
    config.SITE_DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    f1 = fwd[fwd["hotel_id"] == S.HOTEL_ID].set_index("date")
    forecast_rooms = np.minimum(f1["expected_demand"], f1["capacity"])
    out = []
    for key, title, subtitle, start, is_forecast in SCENARIOS:
        dem = S.demand_for_week(X["nights"], X["bookings"], pd.Timestamp(start),
                                forecast_rooms if is_forecast else None)
        opt = S.optimize(staff, dem)
        base = S.manual_baseline(staff)
        res = {}
        for label, grid in (("optimized", opt["grid"]), ("manual", base["grid"])):
            ev = S.evaluate(staff, grid, dem)
            rules = S.check_rules(staff, grid)
            res[label] = {"grid": grid, "evaluation": ev, "rules": rules}
        xlsx = f"schedule_{key}_week.xlsx"
        write_schedule(config.SITE_DOWNLOADS_DIR / xlsx, f"Housekeeping schedule, Summit Tower Hotel: {title}",
                       staff, opt["grid"], dem, res["optimized"]["evaluation"]["coverage"], res["optimized"]["rules"])
        payload = []
        for e in staff[:3]:
            for d, s in enumerate(opt["grid"][e.emp_id]):
                if s in S.SHIFTS:
                    day = pd.Timestamp(start) + pd.Timedelta(days=d)
                    st, en = S.SHIFTS[s][2], S.SHIFTS[s][3]
                    payload.append({"employee_ref": e.emp_id, "department": "HSKP-TOWER",
                                    "job": S.SHIFTS[s][1],
                                    "start": (day + pd.Timedelta(hours=st)).strftime("%Y-%m-%dT%H:%M:00"),
                                    "end": (day + pd.Timedelta(hours=en)).strftime("%Y-%m-%dT%H:%M:00")})
        out.append({"key": key, "title": title, "subtitle": subtitle, "week_start": start,
                    "solver_status": opt["status"], "demand": dem.to_dict("records"),
                    "optimized": res["optimized"], "manual": res["manual"],
                    "excel": f"downloads/{xlsx}", "payload_preview": payload[:6]})
    return {
        "hotel": "Summit Tower Hotel", "department": "Housekeeping",
        "standards": {"checkout_minutes": S.CHECKOUT_MIN, "stayover_minutes": S.STAYOVER_MIN,
                      "productive_hours": S.PRODUCTIVE_HOURS, "attendants_per_inspector": S.RA_PER_INSPECTOR,
                      "occupied_rooms_per_evening_attendant": S.OCCUPIED_PER_EVENING},
        "shifts": {k: {"label": v[0], "role": v[1], "paid_hours": v[4]} for k, v in S.SHIFTS.items()},
        "staff": [{"id": e.emp_id, "name": e.name, "contract": e.contract, "shifts": e.shifts,
                   "requested_off": e.requested_off, "unavailable": e.unavailable,
                   "prefers_printed": e.prefers_printed, "seniority": e.seniority} for e in staff],
        "scenarios": out,
    }


def proposals_index() -> list:
    """Title, one-sentence summary and path of every proposal, read from the repository."""
    repo = "https://github.com/nihalunfc/hotel-business/blob/main/"
    items = []
    groups = [("Project HARLTON", "Revenue, profit and expense"), ("Project H2", "Operations")]
    for folder, group in groups:
        base = config.ROOT / folder
        paths = sorted(base.glob("[0-9][0-9]-*/proposal.md"))
        lead = base / ("proposal/proposal.md" if folder == "Project HARLTON" else "proposal.md")
        for p in [lead] + paths:
            lines = p.read_text().splitlines()
            title = lines[0].lstrip("# ").strip()
            summary = next((l for l in lines if l.startswith("> **In short:")), "")
            summary = summary.replace("> **In short:", "").rstrip("*").strip()
            summary = summary[:1].upper() + summary[1:]
            if p == lead:
                title = f"{title}: overview" if folder == "Project HARLTON" else title
            rel = p.relative_to(config.ROOT).as_posix()
            items.append({"group": group, "title": title, "summary": summary,
                          "url": repo + rel.replace(" ", "%20")})
    for folder in ("Data Foundation/proposal.md", "Further Ideas/README.md"):
        p = config.ROOT / folder
        lines = p.read_text().splitlines()
        summary = next((l for l in lines if l.startswith("> **In short:")), "")
        summary = summary.replace("> **In short:", "").rstrip("*").strip()
        items.append({"group": "Shared", "title": lines[0].lstrip("# ").strip(),
                      "summary": summary[:1].upper() + summary[1:],
                      "url": repo + folder.replace(" ", "%20")})
    return items


def export_all(X: dict, otb: pd.DataFrame, checks: pd.DataFrame, profile: dict) -> dict:
    rev, fwd = revenue(X, otb)
    sch = schedules(X, fwd)
    _dump("proposals.json", proposals_index())
    meta = {"generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "as_of": str(config.AS_OF), "profile": profile,
            "quality_checks": checks[["check_name", "failures", "passed"]].to_dict("records")}
    _dump("revenue.json", rev)
    _dump("schedule.json", sch)
    _dump("meta.json", meta)
    return {"revenue": rev, "schedule": sch, "meta": meta}
