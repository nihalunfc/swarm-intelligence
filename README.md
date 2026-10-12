# Swarm Intelligence: Decentralized Resource Optimization Framework

One swarm engine, several real-world applications. Many independent agents each make their own small decision from what they can see locally, and together they solve a problem no single controller handles well: balancing a power grid, containing a wildfire, running hotel operations.

| App | Agents | Shared resource | Folder |
| :-- | :-- | :-- | :-- |
| Energy grid | Smart battery nodes on the ERCOT COAST grid | Grid capacity at peak hours | [`apps/energy`](apps/energy/README.md) |
| Wildfire | Retardant drones over a forest | Retardant and flight time | [`apps/wildfire`](apps/wildfire/README.md) |
| Hotel | Rooms, staff and properties (swarm environments planned) | Staff hours, rooms, energy | [`apps/hotel`](apps/hotel/README.md) |

## Repository layout

```
core/swarm/      the shared engine (environment interface, agent, trainer, benchmark, CLI)
apps/energy/     battery swarm, data pipeline, Phase 2 forecasts, notebooks
apps/wildfire/   drone swarm and the web dashboard (copy of GDGCHackathon2026, history kept)
apps/hotel/      hotel analytics, proposals and demo site (copy of hotel-business, history kept)
configs/         one YAML file per experiment
tests/           smoke and unit tests for the engine and apps
docs/            capstone proposals and reports
sandbox/         personal experiment folders for each team member
```

The public `hotel-business` and `GDGCHackathon2026` repositories and their GitHub Pages are unchanged; the copies here are where new work happens.

## Quick start

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu   # or a CUDA build
pip install -e ".[dev,hotel]"

swarm train --config configs/energy.yaml          # train, then compare with baselines on held-out data
swarm train --config configs/wildfire.yaml --set env.n_drones=12 train.total_steps=300000
swarm benchmark                                   # every app, one results table in runs/
swarm replay --run runs/wildfire/<id> --output apps/wildfire/docs/data/replay.json
pytest
```

Every run writes `runs/<app>/<timestamp>/` with the config, model, training history and a results table. `--set key.sub=value` overrides any config value. Seeds are fixed, so a run repeats exactly on the same machine.

## How the swarm works

Each agent runs the **same** small neural network on its **own** local observation and chooses its own action. Because the weights are shared, the network does not grow when you add agents: 10 batteries or 1,000 use the same model. The earlier version used one network that chose every agent's action at once, which needs one output per combination (3^10 = 59,049 outputs for 10 batteries, 6^12 ≈ 2.2 billion for 12 drones).

All agents are evaluated **in parallel**: every agent in every environment copy goes through the network in one batched pass (on a GPU when available), and `train.num_envs` environment copies collect experience side by side.

Agents learn together from one team reward with **Value Decomposition Networks** (VDN): the team's value is the sum of each agent's value, so each agent gets credit for its share of the result. `agent.mixer: independent` switches to independent Q-learning. Double-DQN targets, a soft-updated target network and action masks (no charging a full battery, no dropping with an empty tank) are used throughout.

A new application implements one interface, [`swarm.env.SwarmEnv`](core/swarm/env.py) (`reset`, `step`, `action_mask`, `episode_metrics`), plus a few baseline rules, and registers in [`swarm.registry`](core/swarm/registry.py).

## Results

RESULTS_PLACEHOLDER

## Research objectives

1. **Grid balancing:** can decentralized battery agents autonomously mitigate demand and renewable volatility?
2. **Scalability:** does the architecture stay stable as agents are added?
3. **Transfer:** does the same engine solve unrelated allocation problems (wildfire, hotel operations)?

## Energy data

| Source | Type | URL |
| :-- | :-- | :-- |
| NREL | Weather and solar irradiance | [NSRDB](https://nsrdb.nrel.gov/) |
| ERCOT | Hourly native load, COAST zone | [ERCOT](https://www.ercot.com/) |

| Variable | Unit | Source | Description |
| :-- | :-- | :-- | :-- |
| timestamp | YYYY-MM-DD HH | merged | Hourly index |
| GHI, DNI, DHI | W/m² | NREL | Global, direct and diffuse irradiance |
| Temperature | °C | NREL | Surface air temperature |
| Wind Speed | m/s | NREL | Local wind speed |
| load | MW | ERCOT | Native load, COAST zone |

The pipeline that downloads, cleans and merges 2018-2022 is in [`apps/energy/pipeline`](apps/energy/pipeline/README.md). A 2020 sample is committed so everything runs without downloads.
