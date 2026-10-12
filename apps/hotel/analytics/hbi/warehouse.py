"""Build the SQLite warehouse from generated CSVs and run data quality checks."""

import sqlite3

import pandas as pd

from . import config

SQL_FILES = ["01_schema.sql", "02_transform.sql", "03_marts.sql"]


def build(tables: dict) -> sqlite3.Connection:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    if config.WAREHOUSE_PATH.exists():
        config.WAREHOUSE_PATH.unlink()
    con = sqlite3.connect(config.WAREHOUSE_PATH)
    staging = {
        "stg_bookings": tables["bookings"].assign(
            booking_date=lambda d: pd.to_datetime(d["booking_date"]).dt.strftime("%Y-%m-%d"),
            arrival_date=lambda d: pd.to_datetime(d["arrival_date"]).dt.strftime("%Y-%m-%d"),
            cancel_date=lambda d: pd.to_datetime(d["cancel_date"]).dt.strftime("%Y-%m-%d")),
        "stg_denials": tables["denials"].assign(
            request_date=lambda d: pd.to_datetime(d["request_date"]).dt.strftime("%Y-%m-%d"),
            arrival_date=lambda d: pd.to_datetime(d["arrival_date"]).dt.strftime("%Y-%m-%d")),
        "stg_hotels": tables["hotels"],
        "stg_segments": tables["segments"],
        "stg_channels": tables["channels"],
        "stg_dates": tables["dates"].assign(date=lambda d: pd.to_datetime(d["date"]).dt.strftime("%Y-%m-%d")),
    }
    for name, df in staging.items():
        df.to_sql(name, con, index=False, if_exists="replace")
    for f in SQL_FILES:
        con.executescript((config.SQL_DIR / f).read_text())
    con.commit()
    return con


def quality_checks(con: sqlite3.Connection) -> pd.DataFrame:
    sql = (config.SQL_DIR / "04_quality_checks.sql").read_text()
    checks = pd.read_sql_query(sql, con)
    checks["passed"] = checks["failures"] == 0
    return checks


def source_profile(con: sqlite3.Connection) -> dict:
    q = lambda s: con.execute(s).fetchone()[0]
    return {
        "bookings": q("SELECT COUNT(*) FROM fact_booking"),
        "stay_nights": q("SELECT COUNT(*) FROM fact_stay_night"),
        "denied_requests": q("SELECT COUNT(*) FROM stg_denials"),
        "revenue_imputed_rows": q("SELECT SUM(revenue_imputed) FROM fact_booking"),
        "first_arrival": q("SELECT MIN(arrival_date) FROM fact_booking"),
        "last_arrival": q("SELECT MAX(arrival_date) FROM fact_booking"),
    }
