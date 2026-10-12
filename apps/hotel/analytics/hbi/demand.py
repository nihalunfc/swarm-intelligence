"""Historical demand intelligence (HARLTON-10) and year-round tiering (HARLTON-11).

All analyses read from the warehouse. Booking pace is rebuilt from booking and
cancellation dates on fact_stay_night, which is equivalent to keeping a daily
snapshot of every reservation.
"""

import sqlite3

import numpy as np
import pandas as pd

from . import config

LEADS = [0, 1, 2, 3, 5, 7, 10, 14, 21, 30, 45, 60, 90, 120, 180, 270, 365]
SOLD_OUT = 0.99
NEAR_CAPACITY = 0.85


def _ts(d) -> pd.Timestamp:
    return pd.Timestamp(d)


AS_OF = _ts(config.AS_OF)
LTM_START = AS_OF - pd.DateOffset(years=1)
PRIOR_START = AS_OF - pd.DateOffset(years=2)


def load(con: sqlite3.Connection) -> dict:
    daily = pd.read_sql_query("SELECT * FROM mart_daily_hotel", con, parse_dates=["stay_date"])
    nights = pd.read_sql_query(
        "SELECT hotel_id, stay_date, rooms, revenue, status, booking_date, cancel_date FROM fact_stay_night",
        con, parse_dates=["stay_date", "booking_date", "cancel_date"])
    bookings = pd.read_sql_query(
        "SELECT booking_id, hotel_id, arrival_date, lead_days, nights, rooms, room_nights, segment, channel, "
        "rate, room_revenue, status FROM fact_booking", con, parse_dates=["arrival_date"])
    hotels = pd.read_sql_query("SELECT * FROM dim_hotel", con)
    dates = pd.read_sql_query("SELECT * FROM dim_date", con, parse_dates=["date"])
    channels = pd.read_sql_query("SELECT * FROM dim_channel", con)
    segments = pd.read_sql_query("SELECT * FROM dim_segment", con)
    return dict(daily=daily, nights=nights, bookings=bookings, hotels=hotels, dates=dates,
                channels=channels, segments=segments)


def otb_matrix(nights: pd.DataFrame, leads=LEADS) -> pd.DataFrame:
    """Rooms on the books for each hotel and stay date at each lead time (days before arrival)."""
    book_lead = (nights["stay_date"] - nights["booking_date"]).dt.days.to_numpy()
    cancel_lead = (nights["stay_date"] - nights["cancel_date"]).dt.days.to_numpy()
    cancelled = nights["cancel_date"].notna().to_numpy()
    out = {}
    for L in leads:
        on = (book_lead >= L) & (~cancelled | (cancel_lead < L))
        out[L] = nights.loc[on].groupby(["hotel_id", "stay_date"])["rooms"].sum()
    m = pd.DataFrame(out).fillna(0)
    m.columns = [f"otb_{L}" for L in leads]
    return m


def otb_as_of(nights: pd.DataFrame, as_of: pd.Timestamp) -> pd.Series:
    on = (nights["booking_date"] <= as_of) & (nights["cancel_date"].isna() | (nights["cancel_date"] > as_of))
    return nights.loc[on].groupby(["hotel_id", "stay_date"])["rooms"].sum()


def kpis(daily: pd.DataFrame, start, end) -> dict:
    d = daily[(daily["stay_date"] >= start) & (daily["stay_date"] < end)]
    sold, cap, rev = d["rooms_sold"].sum(), d["capacity"].sum(), d["room_revenue"].sum()
    return {"occupancy": sold / cap, "adr": rev / sold, "revpar": rev / cap, "revenue": rev,
            "room_nights": int(sold)}


def summary_kpis(daily: pd.DataFrame, hotels: pd.DataFrame) -> dict:
    ltm = kpis(daily, LTM_START, AS_OF)
    prior = kpis(daily, PRIOR_START, LTM_START)
    by_hotel = []
    for _, h in hotels.iterrows():
        dh = daily[daily["hotel_id"] == h["hotel_id"]]
        a, b = kpis(dh, LTM_START, AS_OF), kpis(dh, PRIOR_START, LTM_START)
        by_hotel.append({"hotel_id": int(h["hotel_id"]), "hotel": h["hotel_name"], "rooms": int(h["rooms"]),
                         "style": h["style"], **{k: round(v, 4) for k, v in a.items()},
                         "revpar_change": round(a["revpar"] / b["revpar"] - 1, 4)})
    return {"ltm": ltm, "prior": prior, "by_hotel": by_hotel}


def monthly_trend(daily: pd.DataFrame) -> pd.DataFrame:
    d = daily[daily["stay_date"] < AS_OF].copy()
    d["month"] = d["stay_date"].dt.to_period("M")
    m = d.groupby("month").agg(sold=("rooms_sold", "sum"), cap=("capacity", "sum"), rev=("room_revenue", "sum"))
    m["occupancy"] = m["sold"] / m["cap"]
    m["adr"] = m["rev"] / m["sold"]
    m["revpar"] = m["rev"] / m["cap"]
    m.index = m.index.astype(str)
    return m.reset_index()


def weekday_profile(daily: pd.DataFrame) -> pd.DataFrame:
    d = daily[(daily["stay_date"] >= LTM_START) & (daily["stay_date"] < AS_OF)]
    g = d.groupby(d["stay_date"].dt.dayofweek).agg(sold=("rooms_sold", "sum"), cap=("capacity", "sum"),
                                                   rev=("room_revenue", "sum"))
    g["occupancy"] = g["sold"] / g["cap"]
    g["adr"] = g["rev"] / g["sold"]
    g.index = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    return g.reset_index(names="day")


def booking_curves(otb: pd.DataFrame, daily: pd.DataFrame, dates: pd.DataFrame) -> dict:
    """Average share of final rooms on the books at each lead, for contrasting date types."""
    hist = daily[(daily["stay_date"] >= PRIOR_START) & (daily["stay_date"] < AS_OF)].set_index(["hotel_id", "stay_date"])
    j = otb.join(hist[["rooms_sold"]], how="inner")
    j = j[j["otb_0"] > 0]
    sd = j.index.get_level_values("stay_date")
    month, dow = sd.month, sd.dayofweek
    groups = {
        "Summer Saturdays": (np.isin(month, [6, 7, 8])) & (dow == 5),
        "Summer weekdays": (np.isin(month, [6, 7, 8])) & (dow <= 3),
        "Winter Saturdays": (np.isin(month, [12, 1, 2])) & (dow == 5),
        "Winter weekdays": (np.isin(month, [12, 1, 2])) & (dow <= 3),
    }
    out = {}
    for name, mask in groups.items():
        sub = j[mask]
        out[name] = [round(float((sub[f"otb_{L}"] / sub["otb_0"]).mean()), 4) for L in LEADS]
    return {"leads": LEADS, "curves": out}


def _features(index: pd.MultiIndex) -> pd.DataFrame:
    sd = index.get_level_values("stay_date")
    return pd.DataFrame({"hotel_id": index.get_level_values("hotel_id"), "dow": sd.dayofweek,
                         "month": sd.month}, index=index)


def unconstrain(otb: pd.DataFrame, daily: pd.DataFrame, open_threshold: float = 0.90) -> pd.DataFrame:
    """Estimate true demand on sold-out nights using pickup ratios from similar open nights.

    For each sold-out hotel-night, find the last lead time at which it was still clearly open
    (on the books below 90% of capacity). Similar nights that never sold out show how much
    demand usually arrives after that lead time; the ratio is applied to the sold-out night.
    """
    d = daily[daily["stay_date"] < AS_OF].set_index(["hotel_id", "stay_date"])
    j = otb.join(d[["capacity", "rooms_sold", "rooms_denied", "adr"]], how="inner")
    j["final"] = j["otb_0"]
    j["sold_out"] = j["otb_0"] >= SOLD_OUT * j["capacity"]
    f = _features(j.index)
    j = j.join(f)
    # Peers: nights that stayed open but came close to selling out, so their late demand is comparable.
    open_nights = j[~j["sold_out"] & (j["final"] >= NEAR_CAPACITY * j["capacity"])]

    est = []
    for idx, row in j[j["sold_out"]].iterrows():
        close_lead = next((L for L in LEADS if row[f"otb_{L}"] < open_threshold * row["capacity"]), LEADS[-1])
        peers = open_nights[(open_nights["hotel_id"] == row["hotel_id"]) & (open_nights["dow"] == row["dow"])
                            & (abs(open_nights["month"] - row["month"]) <= 1)]
        base = peers[f"otb_{close_lead}"]
        ok = base > 0
        ratio = float((peers.loc[ok, "final"] / base[ok]).median()) if ok.sum() >= 5 else 1.0
        estimate = max(row["final"], row[f"otb_{close_lead}"] * ratio)
        est.append((idx[0], idx[1], row["capacity"], row["final"], estimate,
                    row["final"] + row["rooms_denied"], row["adr"], close_lead))
    return pd.DataFrame(est, columns=["hotel_id", "stay_date", "capacity", "rooms_sold", "estimated_demand",
                                      "true_demand", "adr", "close_lead"])


def pickup_forecast(otb: pd.DataFrame, daily: pd.DataFrame, unc: pd.DataFrame) -> dict:
    """Additive pickup forecast with a back-test against same-day-last-year."""
    d = daily.set_index(["hotel_id", "stay_date"])
    hist = otb.join(d[["capacity", "rooms_sold"]], how="inner")
    hist = hist[hist.index.get_level_values("stay_date") < AS_OF]
    u = unc.set_index(["hotel_id", "stay_date"])["estimated_demand"]
    hist["final_u"] = hist["rooms_sold"].astype(float)
    common = hist.index.intersection(u.index)
    hist.loc[common, "final_u"] = u.loc[common]
    hist = hist.join(_features(hist.index))
    sd = hist.index.get_level_values("stay_date")

    test_leads = [7, 14, 30, 60]
    rows = []
    test = hist[sd >= LTM_START]
    train = hist[sd < LTM_START]
    for L in test_leads:
        pk = (train["final_u"] - train[f"otb_{L}"]).groupby([train["hotel_id"], train["dow"], train["month"]]).mean()
        key = pd.MultiIndex.from_arrays([test["hotel_id"], test["dow"], test["month"]])
        pred = np.minimum(test[f"otb_{L}"].to_numpy() + pk.reindex(key).fillna(0).to_numpy(),
                          test["capacity"].to_numpy())
        actual = test["rooms_sold"].to_numpy()
        stly_idx = pd.MultiIndex.from_arrays([test["hotel_id"],
                                              test.index.get_level_values("stay_date") - pd.Timedelta(days=364)])
        naive = d["rooms_sold"].reindex(stly_idx).to_numpy()
        ok = (actual > 0) & ~np.isnan(naive)
        mape_p = float(np.mean(np.abs(pred[ok] - actual[ok]) / actual[ok]))
        mape_n = float(np.mean(np.abs(naive[ok] - actual[ok]) / actual[ok]))
        rows.append({"lead_days": L, "pickup_mape": round(mape_p, 4), "last_year_mape": round(mape_n, 4)})

    recent = hist[sd >= PRIOR_START]
    pickup_u = {L: (recent["final_u"] - recent[f"otb_{L}"]).groupby(
        [recent["hotel_id"], recent["dow"], recent["month"]]).mean() for L in LEADS}
    return {"backtest": rows, "pickup_u": pickup_u}


def event_uplift(daily: pd.DataFrame, dates: pd.DataFrame) -> pd.DataFrame:
    d = daily[daily["stay_date"] < AS_OF].merge(dates[["date", "event", "month", "day_of_week"]],
                                                left_on="stay_date", right_on="date")
    p = d.groupby(["stay_date", "event", "month", "day_of_week"], dropna=False).agg(
        sold=("rooms_sold", "sum"), cap=("capacity", "sum"), rev=("room_revenue", "sum")).reset_index()
    p["occ"] = p["sold"] / p["cap"]
    p["adr"] = p["rev"] / p["sold"]
    base = p[p["event"].isna()].groupby(["month", "day_of_week"])[["occ", "adr"]].mean()
    ev = p[p["event"].notna()].join(base, on=["month", "day_of_week"], rsuffix="_base")
    out = ev.groupby("event").agg(nights=("stay_date", "count"), occ=("occ", "mean"), occ_base=("occ_base", "mean"),
                                  adr=("adr", "mean"), adr_base=("adr_base", "mean")).reset_index()
    out["adr_uplift"] = out["adr"] / out["adr_base"] - 1
    out["occ_points"] = out["occ"] - out["occ_base"]
    return out.sort_values("adr_uplift", ascending=False)


def channel_mix(bookings: pd.DataFrame, channels: pd.DataFrame) -> pd.DataFrame:
    b = bookings[(bookings["arrival_date"] >= LTM_START) & (bookings["arrival_date"] < AS_OF)
                 & (bookings["status"] == "Checked out")]
    g = b.groupby("channel").agg(room_nights=("room_nights", "sum"), revenue=("room_revenue", "sum")).reset_index()
    g = g.merge(channels, on="channel")
    g["adr"] = g["revenue"] / g["room_nights"]
    g["net_adr"] = g["adr"] * (1 - g["acquisition_cost"])
    g["share"] = g["room_nights"] / g["room_nights"].sum()
    g["acquisition_spend"] = g["revenue"] * g["acquisition_cost"]
    return g.sort_values("room_nights", ascending=False)


def cancellations(bookings: pd.DataFrame) -> dict:
    b = bookings[(bookings["arrival_date"] >= LTM_START) & (bookings["arrival_date"] < AS_OF)].copy()
    b["cancelled"] = b["status"] == "Cancelled"
    bins = [-1, 7, 30, 60, 120, 400]
    labels = ["0-7 days", "8-30 days", "31-60 days", "61-120 days", "Over 120 days"]
    b["lead_bucket"] = pd.cut(b["lead_days"], bins=bins, labels=labels)
    by_lead = b.groupby("lead_bucket", observed=True)["cancelled"].mean()
    by_channel = b.groupby("channel")["cancelled"].mean().sort_values(ascending=False)
    return {"overall": float(b["cancelled"].mean()),
            "no_show": float((b["status"] == "No-show").mean()),
            "by_lead": [{"bucket": k, "rate": round(float(v), 4)} for k, v in by_lead.items()],
            "by_channel": [{"channel": k, "rate": round(float(v), 4)} for k, v in by_channel.items()]}


def length_of_stay(bookings: pd.DataFrame) -> list:
    b = bookings[(bookings["arrival_date"] >= LTM_START) & (bookings["arrival_date"] < AS_OF)
                 & (bookings["status"] == "Checked out")]
    s = b["nights"].clip(upper=5).value_counts(normalize=True).sort_index()
    return [{"nights": ("5+" if k == 5 else str(k)), "share": round(float(v), 4)} for k, v in s.items()]


def tier_label(ratio: float) -> str:
    for label, threshold in config.DEMAND_TIERS:
        if ratio >= threshold:
            return label
    return config.DEMAND_TIERS[-1][0]


def forward_calendar(nights, daily, dates, hotels, pickup_u, events) -> pd.DataFrame:
    """Expected unconstrained demand, pace against last year, and a demand tier for each future date."""
    otb_now = otb_as_of(nights, AS_OF)
    stly = otb_as_of(nights, AS_OF - pd.Timedelta(days=364))
    future = pd.date_range(AS_OF, config.HORIZON_END, freq="D")
    cap = hotels.set_index("hotel_id")["rooms"]
    ev_factor = {r["event"]: 1 + max(0.0, r["occ_points"]) for _, r in events.iterrows()}
    dd = dates.set_index("date")
    rows = []
    for hid in cap.index:
        for d in future:
            lead = (d - AS_OF).days
            L = max([x for x in LEADS if x <= lead], default=0)
            L = min(L, LEADS[-1])
            on = float(otb_now.get((hid, d), 0.0))
            pk = pickup_u[L].get((hid, d.dayofweek, d.month), 0.0)
            if lead > LEADS[-1]:
                pk = pickup_u[LEADS[-1]].get((hid, d.dayofweek, d.month), 0.0)
            ev = dd.at[d, "event"] if d in dd.index else None
            pk *= ev_factor.get(ev, 1.0) if isinstance(ev, str) else 1.0
            demand = on + max(pk, 0.0)
            ly = d - pd.Timedelta(days=364)
            rows.append((hid, d, cap[hid], on, float(stly.get((hid, ly), 0.0)), demand))
    f = pd.DataFrame(rows, columns=["hotel_id", "date", "capacity", "otb", "otb_stly", "expected_demand"])
    return f


def portfolio_calendar(f: pd.DataFrame, dates: pd.DataFrame) -> pd.DataFrame:
    p = f.groupby("date").agg(capacity=("capacity", "sum"), otb=("otb", "sum"), otb_stly=("otb_stly", "sum"),
                              expected_demand=("expected_demand", "sum")).reset_index()
    p["ratio"] = p["expected_demand"] / p["capacity"]
    p["tier"] = p["ratio"].apply(tier_label)
    p["otb_occ"] = p["otb"] / p["capacity"]
    p["stly_occ"] = p["otb_stly"] / p["capacity"]
    p["forecast_occ"] = np.minimum(p["expected_demand"], p["capacity"]) / p["capacity"]
    p = p.merge(dates[["date", "day_name", "holiday_ca", "holiday_us", "event", "long_weekend"]], on="date", how="left")
    return p


PLAYBOOK = {
    "Compression": "Hold or raise rates. Two-night minimum on this night. Keep online travel agency allocation tight; accept groups only if they beat displaced revenue.",
    "High": "Hold rates and watch pace daily. Minimum stay only on the peak night. Upsell early check-in and parking.",
    "Shoulder": "Open targeted offers to past guests and packages with dining. Keep all channels open.",
    "Need": "Pursue groups, tournaments and tours. Use packages rather than visible rate cuts. Regional drive-market campaign.",
}


def selling_brief(p: pd.DataFrame, weeks: int = 6) -> list:
    end = AS_OF + pd.Timedelta(weeks=weeks)
    w = p[(p["date"] >= AS_OF) & (p["date"] < end)].copy()
    w["pace_points"] = w["otb_occ"] - w["stly_occ"]
    reasons = []
    for _, r in w.iterrows():
        tags = [x for x in (r["holiday_ca"], r["holiday_us"], r["event"]) if isinstance(x, str) and x]
        notable = r["tier"] in ("Compression", "High") or abs(r["pace_points"]) >= 0.08 or tags
        if not notable:
            continue
        pace = ("ahead of" if r["pace_points"] >= 0.02 else "behind" if r["pace_points"] <= -0.02 else "in line with")
        action = PLAYBOOK[r["tier"]]
        if r["tier"] in ("High", "Shoulder") and r["pace_points"] <= -0.05:
            action = "Pace is behind last year. Check competitor rates, then open a targeted offer to past guests. " + action
        elif r["tier"] in ("Shoulder", "Need") and r["pace_points"] >= 0.08:
            action = "Booking faster than last year: hold rates rather than discount, and review again in a week."
        reasons.append({
            "date": r["date"].strftime("%a %b %d"),
            "iso": r["date"].strftime("%Y-%m-%d"),
            "tier": r["tier"],
            "why": ", ".join(tags) if tags else ("Saturday peak" if r["day_name"] == "Saturday"
                                                 else "Friday peak" if r["day_name"] == "Friday"
                                                 else "Booking faster than last year" if r["pace_points"] > 0
                                                 else "Booking slower than last year"),
            "on_books": round(float(r["otb_occ"]), 3),
            "last_year": round(float(r["stly_occ"]), 3),
            "pace_text": f"{abs(r['pace_points']) * 100:.0f} points {pace} last year" if pace != "in line with" else "In line with last year",
            "forecast": round(float(r["forecast_occ"]), 3),
            "action": action,
        })
    return reasons[:16]
