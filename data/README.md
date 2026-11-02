# data/

Generated data lives here and is not committed. Rebuild the energy dataset with the pipeline in [`apps/energy/pipeline`](../apps/energy/pipeline/README.md):

```
data/raw/      downloaded ERCOT and NREL files
data/clean/    cleaned and merged master files (e.g. ercot_nrel_2018_2022.csv)
runs/          trained models, metrics and replays (one folder per run)
```

A one-year sample (2020) that runs out of the box is kept at `apps/energy/data/sample/ercot_nrel_2020.csv`.
