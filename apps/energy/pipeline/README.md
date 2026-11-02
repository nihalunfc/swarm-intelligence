# Energy data pipeline

Builds `data/clean/ercot_nrel_2018_2022.csv`, the dataset used by `configs/energy-full.yaml` and the Phase 2 forecasts. Run from the repository root.

```bash
pip install gridstatus pvlib openpyxl

# 1. Download (NREL needs a free key from https://developer.nrel.gov/signup/)
export NREL_API_KEY=...  NREL_EMAIL=...
python apps/energy/pipeline/download_ercot.py      # -> data/raw/ercot_2018_2022.xlsx
python apps/energy/pipeline/download_nrel.py       # -> data/raw/nrel_2018_2022.csv

# 2. Clean
python apps/energy/pipeline/ingest_ercot.py --input data/raw/ercot_2018_2022.xlsx \
    --output data/clean/ercot_2018_2022.csv --start_date 2018-01-01 --end_date "2022-12-31 23:00:00"
python apps/energy/pipeline/ingest_nrel.py --input data/raw/nrel_2018_2022.csv \
    --output data/clean/nrel_2018_2022.csv --start_date 2018-01-01 --end_date "2022-12-31 23:00:00"

# 3. Merge on the hourly timestamp
python apps/energy/pipeline/merge.py --ercot_input data/clean/ercot_2018_2022.csv \
    --nrel_input data/clean/nrel_2018_2022.csv --output data/clean/ercot_nrel_2018_2022.csv
```

`data/` is not committed. The swarm loader (`apps/energy/data.py`) reads this file and the older 2020 sample schema.
