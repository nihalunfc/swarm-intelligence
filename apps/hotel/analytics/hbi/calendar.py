"""Calendar utilities: Canadian and US holidays, a fictional event calendar,
and same-day-last-year alignment."""

from datetime import date, timedelta

import pandas as pd
from dateutil.easter import easter


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """n-th given weekday of a month (weekday: Mon=0). n=-1 means last."""
    if n > 0:
        d = date(year, month, 1)
        d += timedelta(days=(weekday - d.weekday()) % 7)
        return d + timedelta(weeks=n - 1)
    nxt = date(year + (month == 12), month % 12 + 1, 1)
    d = nxt - timedelta(days=1)
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def _victoria_day(year: int) -> date:
    d = date(year, 5, 24)
    return d - timedelta(days=d.weekday())


def canadian_holidays(year: int) -> dict:
    gf = easter(year) - timedelta(days=2)
    return {
        date(year, 1, 1): "New Year's Day",
        _nth_weekday(year, 2, 0, 3): "Family Day",
        gf: "Good Friday",
        _victoria_day(year): "Victoria Day",
        date(year, 7, 1): "Canada Day",
        _nth_weekday(year, 8, 0, 1): "Civic Holiday",
        _nth_weekday(year, 9, 0, 1): "Labour Day",
        _nth_weekday(year, 10, 0, 2): "Thanksgiving (Canada)",
        date(year, 12, 25): "Christmas Day",
        date(year, 12, 26): "Boxing Day",
    }


def us_holidays(year: int) -> dict:
    return {
        _nth_weekday(year, 1, 0, 3): "Martin Luther King Jr. Day (US)",
        _nth_weekday(year, 2, 0, 3): "Presidents' Day (US)",
        _nth_weekday(year, 5, 0, -1): "Memorial Day (US)",
        date(year, 7, 4): "Independence Day (US)",
        _nth_weekday(year, 11, 3, 4): "Thanksgiving (US)",
    }


def event_calendar(start: date, end: date) -> pd.DataFrame:
    """Fictional recurring local events with an expected demand uplift."""
    rows = []
    for year in range(start.year, end.year + 1):
        def add(d, name, kind, uplift, days=1):
            for i in range(days):
                rows.append((d + timedelta(days=i), name, kind, uplift))

        add(_nth_weekday(year, 1, 5, 3), "Regional Youth Hockey Tournament", "Sport", 1.35, 2)
        add(_nth_weekday(year, 2, 5, 2), "Winter Lights Weekend", "Festival", 1.25, 2)
        add(_nth_weekday(year, 3, 1, 3), "Trade Convention", "Convention", 1.30, 3)
        add(_nth_weekday(year, 5, 4, 2), "Spring Music Weekend", "Concert", 1.30, 3)
        add(_nth_weekday(year, 6, 5, 3), "Stadium Concert", "Concert", 1.45, 1)
        add(_nth_weekday(year, 7, 4, 3), "Waterfront Summer Festival", "Festival", 1.25, 3)
        add(_nth_weekday(year, 8, 5, 2), "Stadium Concert", "Concert", 1.45, 1)
        add(_nth_weekday(year, 9, 4, 3), "Wine and Harvest Festival", "Festival", 1.30, 3)
        add(_nth_weekday(year, 10, 5, 4), "City Marathon Weekend", "Sport", 1.35, 2)
        add(_nth_weekday(year, 11, 4, 3), "Winter Lights Opening", "Festival", 1.20, 3)
    ev = pd.DataFrame(rows, columns=["date", "event", "event_type", "uplift"])
    ev["date"] = pd.to_datetime(ev["date"])
    ev = ev[(ev["date"] >= pd.Timestamp(start)) & (ev["date"] <= pd.Timestamp(end))]
    return ev.sort_values("date").drop_duplicates("date").reset_index(drop=True)


def date_dimension(start: date, end: date) -> pd.DataFrame:
    """One row per date with holiday and event flags (dim_date)."""
    days = pd.date_range(start, end, freq="D")
    ca, us = {}, {}
    for y in range(start.year, end.year + 1):
        ca.update(canadian_holidays(y))
        us.update(us_holidays(y))
    ev = event_calendar(start, end).set_index("date")
    df = pd.DataFrame({"date": days})
    df["date_key"] = df["date"].dt.strftime("%Y%m%d").astype(int)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day_of_week"] = df["date"].dt.dayofweek
    df["day_name"] = df["date"].dt.day_name()
    df["is_weekend_night"] = df["day_of_week"].isin([4, 5]).astype(int)
    df["holiday_ca"] = df["date"].dt.date.map(ca).fillna("")
    df["holiday_us"] = df["date"].dt.date.map(us).fillna("")
    df["event"] = df["date"].map(ev["event"]).fillna("")
    df["event_type"] = df["date"].map(ev["event_type"]).fillna("")
    df["event_uplift"] = df["date"].map(ev["uplift"]).fillna(1.0)
    # Long-weekend nights: the Friday to Sunday before a Monday holiday.
    hol = set(pd.to_datetime(list(ca) + list(us)))
    df["long_weekend"] = df["date"].apply(
        lambda d: int(any((d + pd.Timedelta(days=k)) in hol and (d + pd.Timedelta(days=k)).dayofweek == 0
                          for k in (1, 2, 3)) and d.dayofweek in (4, 5, 6))
    )
    df["season"] = df["month"].map({12: "Winter", 1: "Winter", 2: "Winter", 3: "Spring", 4: "Spring",
                                    5: "Spring", 6: "Summer", 7: "Summer", 8: "Summer",
                                    9: "Autumn", 10: "Autumn", 11: "Autumn"})
    return df


def same_day_last_year(d: pd.Timestamp) -> pd.Timestamp:
    """Weekday-aligned comparison date (364 days earlier)."""
    return d - pd.Timedelta(days=364)
