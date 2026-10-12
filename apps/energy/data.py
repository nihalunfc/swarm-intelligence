"""Load the merged ERCOT + NREL dataset in either of its historical schemas.

Two column layouts exist in this project's history:

* the pipeline output (``Timestamp, NREL_GHI_W_m2, ..., ERCOT_COAST_Load_MW``)
* the 2020 cleaned sample (``timestamp, GHI, DNI, DHI, Temperature, Wind Speed, demand_mw``)

Both are mapped to one standard set of names here.
"""

from pathlib import Path

import numpy as np
import pandas as pd

COLUMN_MAP = {
    "timestamp": ["Timestamp", "timestamp"],
    "load_mw": ["ERCOT_COAST_Load_MW", "demand_mw", "COAST"],
    "ghi": ["NREL_GHI_W_m2", "GHI"],
    "dni": ["NREL_DNI_W_m2", "DNI"],
    "dhi": ["NREL_DHI_W_m2", "DHI"],
    "temp_c": ["NREL_Temperature_C", "Temperature"],
    "wind_ms": ["NREL_Wind_Speed_m_s", "Wind Speed"],
}
REQUIRED = ["timestamp", "load_mw", "ghi", "temp_c", "wind_ms"]

REPO = Path(__file__).resolve().parents[2]
SAMPLE = Path(__file__).resolve().parent / "data" / "sample" / "ercot_nrel_2020.csv"


def resolve_path(path: str | None) -> Path:
    if not path:
        return SAMPLE
    p = Path(path)
    return p if p.is_absolute() else REPO / p


def load(path: str | None = None) -> pd.DataFrame:
    """Read a merged CSV and return standard columns sorted by time, one row per hour."""
    src = resolve_path(path)
    raw = pd.read_csv(src)
    out = {}
    for std, candidates in COLUMN_MAP.items():
        col = next((c for c in candidates if c in raw.columns), None)
        if col is not None:
            out[std] = raw[col]
    missing = [c for c in REQUIRED if c not in out]
    if missing:
        raise ValueError(f"{src}: missing columns for {missing}. Found: {list(raw.columns)}")
    df = pd.DataFrame(out)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    if not pd.api.types.is_numeric_dtype(df["load_mw"]):
        df["load_mw"] = df["load_mw"].astype(str).str.replace(",", "").astype(float)
    df = df.sort_values("timestamp").drop_duplicates("timestamp").reset_index(drop=True)
    num = df.columns.drop("timestamp")
    df[num] = df[num].astype(float).interpolate(limit_direction="both")
    return df


def split(df: pd.DataFrame, test_start: str | None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Chronological split. Without ``test_start`` the last 20% is held out."""
    if test_start:
        cut = pd.Timestamp(test_start)
        train, test = df[df.timestamp < cut], df[df.timestamp >= cut]
    else:
        n = int(len(df) * 0.8)
        train, test = df.iloc[:n], df.iloc[n:]
    if len(train) < 48 or len(test) < 48:
        raise ValueError(f"Split at {test_start!r} leaves train={len(train)} test={len(test)} rows")
    return train.reset_index(drop=True), test.reset_index(drop=True)


def day_mean_target(df: pd.DataFrame) -> np.ndarray:
    """The flat level the swarm aims for each hour: that calendar day's mean load.

    This assumes a perfect day-ahead forecast of the daily mean. A next step is
    to replace it with the Phase 2 XGBoost forecast.
    """
    return df.groupby(df.timestamp.dt.date)["load_mw"].transform("mean").to_numpy()
