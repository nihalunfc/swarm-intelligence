# Energy: battery swarm on the ERCOT grid

Smart battery nodes learn to flatten ERCOT COAST load using NREL weather as context.

| Folder / file | What it is |
| :-- | :-- |
| `env.py` | The swarm environment: each battery sees the grid signal, its own state of charge and the swarm average, and chooses charge, idle or discharge. |
| `data.py` | Loads the merged ERCOT + NREL file in either historical column schema, splits train and held-out test by date. |
| `baselines.py` | Rules the swarm must beat: no battery, threshold rule, proportional rule. |
| `data/sample/ercot_nrel_2020.csv` | One year (2020) so everything runs without downloads. |
| `pipeline/` | Phase 1: download, clean and merge 2018-2022 data ([how](pipeline/README.md)). |
| `forecasting/` | Phase 2: XGBoost and LSTM load forecasts. |
| `notebooks/` | Phase 1 cleaning notebook and the original Phase 3 DQN notebook (kept for reference as `*_legacy`). |

## Run

```bash
swarm train --config configs/energy.yaml         # 2020 sample: Jan-Sep train, Oct-Dec test
swarm train --config configs/energy-full.yaml    # 2018-2021 train, 2022 test (build the data first)
```

## Model in one paragraph

Ten 400 MWh / 100 MW batteries (a 1 GW, 4-hour fleet) with 90% round-trip efficiency. The target each hour is that day's mean load, which assumes a perfect day-ahead forecast of the daily mean; replacing it with the Phase 2 forecast is planned. The team reward is the reduction in squared distance from that target, so the biggest peaks matter most. Invalid actions (charging a full battery, discharging an empty one) are masked instead of penalised. Training uses random one-week windows; evaluation plays the whole held-out period once.
