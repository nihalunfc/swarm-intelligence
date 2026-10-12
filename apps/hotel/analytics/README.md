# Analytics Package

The code behind the demo site. One command rebuilds the sample dataset, the SQL warehouse, every analysis and the site data:

```bash
pip install -r analytics/requirements.txt
python analytics/build.py        # about 40 seconds on a laptop CPU
pytest analytics/tests
```

## Pipeline

| Step | Module | What it does |
| :-- | :-- | :-- |
| 1. Sample data | [hbi/generate.py](hbi/generate.py) | Draws booking requests for five fictional hotels from a demand model (season, weekday, Canadian and US holidays, local events, trend). Replays them in booking order against room inventory, so sell-outs, denials and cancellations behave as in a real reservation system. 1.5% of rows have missing revenue on purpose. |
| 2. Warehouse | [hbi/warehouse.py](hbi/warehouse.py), [hbi/sql/](hbi/sql) | Loads staging tables into SQLite and builds a star schema: `dim_hotel`, `dim_date`, `dim_segment`, `dim_channel`, `fact_booking`, `fact_stay_night` (via recursive CTE), `fact_denied_night`, and `mart_daily_hotel`. |
| 3. Quality checks | [hbi/sql/04_quality_checks.sql](hbi/sql/04_quality_checks.sql) | Ten checks, including duplicate keys, room-night arithmetic, revenue tie-out between booking and stay-night grain, and sold above capacity. Any failure stops the build. |
| 4. Revenue analytics | [hbi/demand.py](hbi/demand.py) | Booking pace rebuilt from booking and cancellation dates; additive pickup forecast with a back-test against same-day-last-year; unconstrained demand on sold-out nights, validated against the known denials; event uplift; channel net rate; cancellations by lead time; 365-day demand tiers and the weekly selling brief. |
| 5. Scheduling | [hbi/schedule.py](hbi/schedule.py), [hbi/excel.py](hbi/excel.py) | Converts departures and stayovers into labour hours, solves a mixed-integer shift assignment with PuLP and CBC, checks the result with an independent Ontario ESA rule checker, compares it with a fixed weekly pattern, and writes a colour-coded Excel workbook with live formulas. |
| 6. Site export | [hbi/site_export.py](hbi/site_export.py) | Writes the JSON and Excel files the pages in [docs/](../docs) read. |

## Key definitions

- **Occupancy:** rooms sold divided by rooms available. Cancelled bookings and no-shows are excluded.
- **ADR:** room revenue divided by rooms sold.
- **RevPAR:** room revenue divided by rooms available.
- **On the books at lead L:** rooms booked at least L days before the night and not cancelled by then.
- **Same time last year:** on the books for the night 364 days earlier, measured 364 days earlier, so weekdays line up.
- **Demand tier:** expected unconstrained demand divided by capacity. 100% and above is Compression, 85% High, 60% Shoulder, below 60% Need.

## Notes on honesty of results

- The sample data is generated. It is realistic in shape, but the absolute figures describe fictional hotels.
- The unconstraining estimate is deliberately conservative. Because this sample records every denied request, the method's accuracy can be measured. The demo reports that measurement rather than hiding it.
- Schedule savings depend on the comparison chosen. The fixed weekly pattern is a common manual approach, and uncovered work is costed at overtime rates. Both assumptions are stated on the page.
- The multi-agent coordination engine referenced in the proposals is not part of this package. The scheduler here is a standard, transparent optimization model.
