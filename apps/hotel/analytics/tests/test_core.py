"""Unit tests for calendar logic, pace reconstruction, the schedule rule checker,
the optimizer and the warehouse quality checks. Run with: pytest analytics/tests"""

import sys
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hbi import calendar as cal  # noqa: E402
from hbi import demand as D  # noqa: E402
from hbi import schedule as S  # noqa: E402


def test_canadian_holidays_2026():
    h = cal.canadian_holidays(2026)
    assert h[date(2026, 10, 12)] == "Thanksgiving (Canada)"
    assert h[date(2026, 5, 18)] == "Victoria Day"
    assert h[date(2026, 2, 16)] == "Family Day"
    assert h[date(2026, 4, 3)] == "Good Friday"


def test_us_thanksgiving_and_memorial_day():
    h = cal.us_holidays(2026)
    assert h[date(2026, 11, 26)] == "Thanksgiving (US)"
    assert h[date(2026, 5, 25)] == "Memorial Day (US)"


def test_same_day_last_year_keeps_weekday():
    d = pd.Timestamp("2026-10-10")
    assert cal.same_day_last_year(d).dayofweek == d.dayofweek


def test_otb_matrix_respects_booking_and_cancel_dates():
    nights = pd.DataFrame({
        "hotel_id": [1, 1, 1],
        "stay_date": pd.to_datetime(["2026-07-10"] * 3),
        "rooms": [1, 2, 4],
        "booking_date": pd.to_datetime(["2026-06-01", "2026-07-05", "2026-05-01"]),
        "cancel_date": pd.to_datetime([None, None, "2026-07-01"]),
    })
    m = D.otb_matrix(nights, leads=[0, 7, 30])
    row = m.loc[(1, pd.Timestamp("2026-07-10"))]
    assert row["otb_30"] == 1 + 4          # third booking still active 30 days out
    assert row["otb_7"] == 1               # second not yet made, third already cancelled
    assert row["otb_0"] == 1 + 2


@pytest.mark.parametrize("ratio,label", [(1.2, "Compression"), (0.9, "High"), (0.7, "Shoulder"), (0.3, "Need")])
def test_tier_label(ratio, label):
    assert D.tier_label(ratio) == label


def _staff():
    return [S.Employee("E1", "Test One", "FT", ["AM", "MID", "PM"], 20.0, 3),
            S.Employee("E2", "Test Two", "FT", ["AM", "MID"], 20.0, 5, requested_off=[6])]


def test_rule_checker_flags_short_rest():
    grid = {"E1": ["PM", "AM", "OFF", "OFF", "OFF", "OFF", "OFF"], "E2": ["OFF"] * 7}
    rules = {r["rule"]: r["violations"] for r in S.check_rules(_staff(), grid)}
    rest_rule = next(k for k in rules if k.startswith("At least 11 hours"))
    assert rules[rest_rule] == 1


def test_rule_checker_flags_seven_day_week():
    grid = {"E1": ["AM"] * 7, "E2": ["OFF"] * 7}
    rules = {r["rule"]: r["violations"] for r in S.check_rules(_staff(), grid)}
    weekly = next(k for k in rules if k.startswith("At least 24"))
    assert rules[weekly] == 1


def test_optimizer_output_passes_all_rules():
    staff = S.roster()
    demand = pd.DataFrame([{"date": f"2026-01-{19 + i}", "day": d, "occupied_last_night": 400, "departures": 160,
                            "stayovers": 240, "cleaning_hours": 160.0, "attendants_needed": 22,
                            "inspectors_needed": 3, "evening_needed": 3}
                           for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])])
    out = S.optimize(staff, demand, time_limit=30)
    assert out["status"] == "Optimal"
    assert all(r["passed"] for r in S.check_rules(staff, out["grid"]))
    ev = S.evaluate(staff, out["grid"], demand)
    assert ev["shortfall_hours"] <= 1.0
    assert ev["overtime_hours"] == 0
