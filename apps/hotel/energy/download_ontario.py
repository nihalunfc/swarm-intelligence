"""Build an Ontario grid + weather file for the hotel peak-energy swarm.

Downloads IESO hourly Ontario demand and Environment and Climate Change Canada
hourly weather for Toronto Pearson, and writes one CSV in the layout
``apps.energy.data.load`` reads:

    python apps/hotel/energy/download_ontario.py --years 2023 2024 --out data/clean/ontario.csv
    swarm train --config configs/hotel-energy.yaml --set env.data_path=data/clean/ontario.csv

Sources (public):
* IESO, hourly Ontario demand: https://reports-public.ieso.ca/public/Demand/PUB_Demand_<year>.csv
* ECCC climate data, station 51459 (Toronto Pearson, hourly):
  https://climate.weather.gc.ca/climate_data/bulk_data_e.html
"""

import argparse
import io
from pathlib import Path

import pandas as pd
import requests

IESO = "https://reports-public.ieso.ca/public/Demand/PUB_Demand_{year}.csv"
ECCC = ("https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={station}"
        "&Year={year}&Month={month}&Day=1&timeframe=1&submit=Download+Data")


def ieso_demand(year: int) -> pd.DataFrame:
    text = requests.get(IESO.format(year=year), timeout=60).text
    lines = [ln for ln in text.splitlines() if not ln.startswith("\\")]  # header notes start with a backslash
    df = pd.read_csv(io.StringIO("\n".join(lines)))
    # Hour 1 is 00:00-01:00 Eastern Standard Time.
    ts = pd.to_datetime(df["Date"]) + pd.to_timedelta(df["Hour"] - 1, unit="h")
    return pd.DataFrame({"timestamp": ts, "demand_mw": df["Ontario Demand"].astype(float)})


def eccc_weather(year: int, station: int) -> pd.DataFrame:
    parts = []
    for month in range(1, 13):
        r = requests.get(ECCC.format(station=station, year=year, month=month), timeout=60)
        parts.append(pd.read_csv(io.StringIO(r.content.decode("utf-8-sig"))))
    w = pd.concat(parts)
    return pd.DataFrame({
        "timestamp": pd.to_datetime(w["Date/Time (LST)"]),
        "Temperature": w["Temp (°C)"].astype(float),
        "Wind Speed": w["Wind Spd (km/h)"].astype(float) / 3.6,
    })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", nargs="+", type=int, required=True)
    ap.add_argument("--station", type=int, default=51459)
    ap.add_argument("--out", default="data/clean/ontario.csv")
    args = ap.parse_args()
    demand = pd.concat(ieso_demand(y) for y in args.years)
    weather = pd.concat(eccc_weather(y, args.station) for y in args.years)
    df = demand.merge(weather, on="timestamp", how="left").sort_values("timestamp")
    df["GHI"] = 0.0  # not used by the hotel swarm; the loader expects the column
    df[["Temperature", "Wind Speed"]] = df[["Temperature", "Wind Speed"]].interpolate(limit_direction="both")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df[["timestamp", "GHI", "Temperature", "Wind Speed", "demand_mw"]].to_csv(out, index=False)
    print(f"Wrote {len(df):,} hours to {out}")


if __name__ == "__main__":
    main()
