"""Synthetic booking history for the fictional portfolio.

Booking requests are drawn per hotel and arrival date from a demand model
(season, weekday, holidays, events, trend). They are then replayed in the
order they were made against room inventory. Requests that do not fit are
recorded as denials, so true unconstrained demand is known and the
unconstraining analysis can be validated against it. Cancellations release
inventory at their cancellation time. Requests made after the as-of date
have not happened yet and are dropped, which leaves a realistic
on-the-books position for future dates.
"""

import heapq
from datetime import timedelta

import numpy as np
import pandas as pd

from . import config
from .calendar import date_dimension

MONTH_DEMAND = {1: 0.62, 2: 0.68, 3: 0.76, 4: 0.80, 5: 0.95, 6: 1.12,
                7: 1.32, 8: 1.35, 9: 1.00, 10: 0.92, 11: 0.74, 12: 0.76}
MONTH_RATE = {1: 0.80, 2: 0.82, 3: 0.86, 4: 0.88, 5: 0.97, 6: 1.10,
              7: 1.28, 8: 1.30, 9: 1.04, 10: 0.98, 11: 0.85, 12: 0.88}
DOW_DEMAND = {0: 0.70, 1: 0.74, 2: 0.80, 3: 0.95, 4: 1.70, 5: 1.10, 6: 0.55}
DOW_RATE = {0: 0.92, 1: 0.92, 2: 0.94, 3: 0.98, 4: 1.22, 5: 1.28, 6: 0.90}
ARRIVALS_PER_ROOM = 0.36
ANNUAL_TREND = 0.03
MISSING_REVENUE_SHARE = 0.015


def _segment_weights(dow: int, month: int) -> dict:
    weekday = dow <= 3
    winter = month in (12, 1, 2, 3)
    peak = month in (6, 7, 8)
    return {
        "TRN": 0.50 if peak else 0.44,
        "TDS": 0.14 if winter else 0.10,
        "COR": 0.18 if weekday else 0.02,
        "GRT": 0.05 if not winter else 0.02,
        "GRA": 0.07 if (winter and not weekday) else 0.03,
        "WHL": 0.08,
    }


CHANNEL_MIX = {
    "TRN": (["WEB", "OTA", "VOI"], [0.38, 0.47, 0.15]),
    "TDS": (["WEB", "OTA", "VOI"], [0.45, 0.35, 0.20]),
    "COR": (["GDS", "WEB", "VOI"], [0.50, 0.30, 0.20]),
    "GRT": (["SAL"], [1.0]),
    "GRA": (["SAL"], [1.0]),
    "WHL": (["WHS"], [1.0]),
}
CHANNEL_CANCEL_FACTOR = {"WEB": 1.0, "OTA": 1.8, "VOI": 0.8, "GDS": 1.0, "SAL": 0.6, "WHS": 1.0}


def _requests(rng: np.random.Generator, dim: pd.DataFrame) -> pd.DataFrame:
    """Draw booking requests for every hotel and arrival date."""
    dim = dim.copy()
    boost = np.ones(len(dim))
    boost[dim["long_weekend"].to_numpy() == 1] *= 1.30
    md = dim["date"].dt.strftime("%m-%d")
    boost[md.isin(["12-24", "12-25"]).to_numpy()] *= 0.45
    boost[md.isin(["12-27", "12-28", "12-29", "12-30", "12-31"]).to_numpy()] *= 1.35
    us_tg = dim["holiday_us"].str.startswith("Thanksgiving")
    for k in (-1, 0, 1, 2):
        boost[np.roll(us_tg.to_numpy(), k)] *= 1.15
    years = (dim["date"] - pd.Timestamp(config.HISTORY_START)).dt.days / 365.25
    trend = (1 + ANNUAL_TREND) ** years
    base = (dim["month"].map(MONTH_DEMAND) * dim["day_of_week"].map(DOW_DEMAND)
            * dim["event_uplift"] * boost * trend).to_numpy()

    frames = []
    for hid, _name, _style, rooms, _rate in config.HOTELS:
        lam = base * rooms * ARRIVALS_PER_ROOM * rng.lognormal(0, 0.10, len(dim))
        n = rng.poisson(lam)
        arr = np.repeat(dim["date"].to_numpy(), n)
        dow = np.repeat(dim["day_of_week"].to_numpy(), n)
        mon = np.repeat(dim["month"].to_numpy(), n)
        frames.append(pd.DataFrame({"hotel_id": hid, "arrival_date": arr, "dow": dow, "month": mon}))
    req = pd.concat(frames, ignore_index=True)

    seg = np.empty(len(req), dtype=object)
    for (dw, mo), idx in req.groupby(["dow", "month"]).indices.items():
        w = _segment_weights(dw, mo)
        keys, p = list(w), np.array(list(w.values()))
        seg[idx] = rng.choice(keys, size=len(idx), p=p / p.sum())
    req["segment"] = seg

    group = req["segment"].isin(["GRT", "GRA"]).to_numpy()
    # Group requests represent blocks; scale their count down so room volume stays realistic.
    keep = ~group | (rng.random(len(req)) < 0.10)
    req = req[keep].reset_index(drop=True)
    group = req["segment"].isin(["GRT", "GRA"]).to_numpy()

    mean_n = req["segment"].map({k: v[3] for k, v in config.SEGMENTS.items()}).to_numpy()
    nights = 1 + rng.poisson(np.maximum(mean_n - 1, 0.1))
    nights = np.where(req["dow"].to_numpy() == 4, np.maximum(nights, rng.choice([1, 2, 2, 2], len(req))), nights)
    req["nights"] = np.clip(nights, 1, 7)

    rooms = rng.choice([1, 2, 3], size=len(req), p=[0.88, 0.10, 0.02])
    rooms = np.where(group, rng.integers(8, 36, len(req)), rooms)
    req["rooms"] = rooms

    med = req["segment"].map({k: v[2] for k, v in config.SEGMENTS.items()}).to_numpy()
    lead = np.where(group, rng.integers(45, 300, len(req)),
                    np.round(rng.lognormal(np.log(med), 0.95)))
    req["lead_days"] = np.clip(lead, 0, 365).astype(int)

    chan = np.empty(len(req), dtype=object)
    for s, idx in req.groupby("segment").indices.items():
        opts, p = CHANNEL_MIX[s]
        chan[idx] = rng.choice(opts, size=len(idx), p=p)
    req["channel"] = chan
    return req


def generate(seed: int = config.SEED):
    rng = np.random.default_rng(seed)
    start, end = config.HISTORY_START, config.HORIZON_END
    dim = date_dimension(start - timedelta(days=400), end + timedelta(days=10))
    dim_core = dim[(dim["date"] >= pd.Timestamp(start)) & (dim["date"] <= pd.Timestamp(end))]
    req = _requests(rng, dim_core)

    epoch = pd.Timestamp(start) - pd.Timedelta(days=400)
    arr_day = ((req["arrival_date"] - epoch).dt.days).to_numpy()
    book_t = arr_day - req["lead_days"].to_numpy() + rng.random(len(req))
    as_of_t = (pd.Timestamp(config.AS_OF) - epoch).days
    happened = book_t < as_of_t
    req = req[happened].reset_index(drop=True)
    arr_day, book_t = arr_day[happened], book_t[happened]

    seg_cancel = req["segment"].map({k: v[4] for k, v in config.SEGMENTS.items()}).to_numpy()
    ch_factor = req["channel"].map(CHANNEL_CANCEL_FACTOR).to_numpy()
    lead = req["lead_days"].to_numpy()
    p_cancel = np.clip(seg_cancel * ch_factor * (0.6 + lead / 90.0), 0, 0.75)
    will_cancel = rng.random(len(req)) < p_cancel
    cancel_t = book_t + rng.random(len(req)) * np.maximum(arr_day - book_t, 0.01)

    # Rate components fixed at request time; occupancy uplift applied during replay.
    rate_by_hotel = {h[0]: h[4] for h in config.HOTELS}
    dim_idx = dim.set_index("date")
    a = req["arrival_date"]
    years = ((a - pd.Timestamp(start)).dt.days / 365.25).to_numpy()
    base_rate = (req["hotel_id"].map(rate_by_hotel).to_numpy()
                 * a.dt.month.map(MONTH_RATE).to_numpy()
                 * a.dt.dayofweek.map(DOW_RATE).to_numpy()
                 * (1 + 0.6 * (dim_idx.loc[a, "event_uplift"].to_numpy() - 1))
                 * req["segment"].map({k: v[1] for k, v in config.SEGMENTS.items()}).to_numpy()
                 * (1 + ANNUAL_TREND) ** years
                 * rng.lognormal(0, 0.05, len(req)))

    cap = {h[0]: h[3] for h in config.HOTELS}
    n_days = int(arr_day.max() + 10)
    inv = {h: np.zeros(n_days, dtype=np.int32) for h in cap}
    hotel = req["hotel_id"].to_numpy()
    nights = req["nights"].to_numpy()
    rooms = req["rooms"].to_numpy()

    accepted = np.zeros(len(req), dtype=bool)
    rate = np.zeros(len(req))
    heap = [(book_t[i], 0, i) for i in range(len(req))]
    heapq.heapify(heap)
    while heap:
        t, kind, i = heapq.heappop(heap)
        h, d0, n, r = hotel[i], arr_day[i], nights[i], rooms[i]
        line = inv[h]
        if kind == 1:
            line[d0:d0 + n] -= r
            continue
        if line[d0:d0 + n].max() + r > cap[h]:
            continue
        line[d0:d0 + n] += r
        accepted[i] = True
        occ = line[d0] / cap[h]
        rate[i] = round(base_rate[i] * (1 + 0.55 * max(0.0, occ - 0.55)), 2)
        if will_cancel[i] and cancel_t[i] < as_of_t:
            heapq.heappush(heap, (cancel_t[i], 1, i))

    to_date = lambda t: (epoch + pd.to_timedelta(np.floor(t), unit="D"))
    req["booking_date"] = to_date(book_t)
    req["rate"] = rate
    cancelled = will_cancel & (cancel_t < as_of_t)

    bk = req[accepted].copy()
    bk_cancel = cancelled[accepted]
    bk["cancel_date"] = to_date(cancel_t[accepted]).where(bk_cancel)
    bk["room_nights"] = bk["nights"] * bk["rooms"]
    bk["room_revenue"] = (bk["rate"] * bk["room_nights"]).round(2)
    past = bk["arrival_date"] < pd.Timestamp(config.AS_OF)
    transient = bk["segment"].isin(["TRN", "TDS", "COR"])
    no_show = (~bk_cancel) & past.to_numpy() & transient.to_numpy() & (rng.random(len(bk)) < 0.02)
    bk["status"] = np.select([bk_cancel, no_show, past.to_numpy()],
                             ["Cancelled", "No-show", "Checked out"], "Confirmed")
    missing = rng.random(len(bk)) < MISSING_REVENUE_SHARE
    bk.loc[missing, "room_revenue"] = np.nan
    bk = bk.sort_values(["booking_date", "hotel_id"]).reset_index(drop=True)
    bk.insert(0, "booking_id", np.arange(1_000_001, 1_000_001 + len(bk)))
    bookings = bk[["booking_id", "hotel_id", "booking_date", "arrival_date", "nights", "rooms",
                   "room_nights", "segment", "channel", "rate", "room_revenue", "status",
                   "cancel_date"]]

    dn = req[~accepted].copy()
    dn.insert(0, "request_id", np.arange(5_000_001, 5_000_001 + len(dn)))
    dn["quoted_rate"] = np.round(base_rate[~accepted], 2)
    denials = dn[["request_id", "hotel_id", "booking_date", "arrival_date", "nights", "rooms",
                  "segment", "channel", "quoted_rate"]].rename(columns={"booking_date": "request_date"})

    hotels = pd.DataFrame(config.HOTELS, columns=["hotel_id", "hotel_name", "style", "rooms", "base_rate"])
    segments = pd.DataFrame([(k, v[0]) for k, v in config.SEGMENTS.items()], columns=["segment", "segment_name"])
    channels = pd.DataFrame([(k, v[0], v[1]) for k, v in config.CHANNELS.items()],
                            columns=["channel", "channel_name", "acquisition_cost"])
    dates = dim_core.copy()
    dates["date"] = dates["date"].dt.date
    return {"bookings": bookings, "denials": denials, "hotels": hotels,
            "segments": segments, "channels": channels, "dates": dates}


def write(tables: dict) -> None:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        df.to_csv(config.DATA_DIR / f"{name}.csv", index=False)
    tables["bookings"].sample(1000, random_state=1).sort_values("booking_id").to_csv(
        config.SAMPLE_DIR / "bookings_sample.csv", index=False)
    tables["denials"].sample(300, random_state=1).sort_values("request_id").to_csv(
        config.SAMPLE_DIR / "denials_sample.csv", index=False)
    for name in ("hotels", "segments", "channels"):
        tables[name].to_csv(config.SAMPLE_DIR / f"{name}.csv", index=False)
