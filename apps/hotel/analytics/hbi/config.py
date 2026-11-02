"""Shared configuration for the sample portfolio and all analytics."""

from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ANALYTICS_DIR = ROOT / "analytics"
DATA_DIR = ROOT / "data" / "generated"
SAMPLE_DIR = ROOT / "data" / "sample"
WAREHOUSE_PATH = DATA_DIR / "warehouse.sqlite"
SQL_DIR = ANALYTICS_DIR / "hbi" / "sql"
SITE_DATA_DIR = ROOT / "docs" / "data"
SITE_DOWNLOADS_DIR = ROOT / "docs" / "downloads"

SEED = 2026
AS_OF = date(2026, 10, 1)            # "today" for on-the-books and forecasts
HISTORY_START = date(2023, 10, 1)    # three full years of actuals
HORIZON_END = date(2027, 9, 30)      # twelve months forward

# Fictional portfolio. Names and figures are invented for demonstration.
HOTELS = [
    # id, name, style, rooms, base rate (CAD)
    (1, "Summit Tower Hotel", "Full-service tower", 620, 219.0),
    (2, "Grand Terrace Resort", "Resort with indoor waterpark", 520, 239.0),
    (3, "Riverside Suites", "Upscale all-suite", 380, 199.0),
    (4, "Harbour Lights Hotel", "Select-service", 300, 169.0),
    (5, "Parkview Inn", "Economy", 240, 129.0),
]

SEGMENTS = {
    # code: (label, rate multiplier, lead-time median days, mean nights, cancel base prob)
    "TRN": ("Transient retail", 1.00, 14, 2.0, 0.20),
    "TDS": ("Transient discount and packages", 0.85, 21, 2.2, 0.15),
    "COR": ("Corporate", 0.92, 10, 1.6, 0.12),
    "GRT": ("Group tour", 0.72, 120, 1.8, 0.06),
    "GRA": ("Group association and sports", 0.80, 90, 2.4, 0.05),
    "WHL": ("Wholesale", 0.75, 45, 2.3, 0.10),
}

CHANNELS = {
    # code: (label, acquisition cost as share of room revenue)
    "WEB": ("Direct web", 0.03),
    "VOI": ("Voice and reservations", 0.05),
    "OTA": ("Online travel agency", 0.18),
    "GDS": ("Global distribution system", 0.10),
    "WHS": ("Wholesaler", 0.20),
    "SAL": ("Direct sales (groups)", 0.02),
}

DEMAND_TIERS = [
    # label, minimum ratio of expected demand to capacity
    ("Compression", 1.00),
    ("High", 0.85),
    ("Shoulder", 0.60),
    ("Need", 0.0),
]
