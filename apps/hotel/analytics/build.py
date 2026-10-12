"""Rebuild the sample dataset, warehouse, analyses and site data from scratch.

Usage:  python analytics/build.py
Runs on CPU in about a minute. No GPU needed.
"""

import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hbi import config, demand, generate, site_export, warehouse  # noqa: E402


def main() -> None:
    t0 = time.time()
    tables = generate.generate()
    generate.write(tables)
    print(f"Generated {len(tables['bookings']):,} bookings and {len(tables['denials']):,} denied requests")

    con = warehouse.build(tables)
    checks = warehouse.quality_checks(con)
    print(checks.to_string(index=False))
    if not checks["passed"].all():
        raise SystemExit("Data quality checks failed; site data not refreshed.")
    profile = warehouse.source_profile(con)
    con.close()

    con = sqlite3.connect(config.WAREHOUSE_PATH)
    X = demand.load(con)
    otb = demand.otb_matrix(X["nights"])
    out = site_export.export_all(X, otb, checks, profile)
    rev, sch = out["revenue"], out["schedule"]
    print(f"Last 12 months: occupancy {rev['ltm']['occupancy']:.1%}, ADR ${rev['ltm']['adr']:.2f}, "
          f"RevPAR ${rev['ltm']['revpar']:.2f}")
    for s in sch["scenarios"]:
        o, m = s["optimized"]["evaluation"], s["manual"]["evaluation"]
        print(f"{s['title']}: optimized total ${o['total_cost']:,.0f} vs manual ${m['total_cost']:,.0f}; "
              f"rule violations {sum(r['violations'] for r in s['optimized']['rules'])}")
    print(f"Done in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
