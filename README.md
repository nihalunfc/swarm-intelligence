# Swarm Intelligence: Decentralized Resource Optimization Framework

One swarm engine, several real-world applications. Many independent agents each make their own small decision from what they can see locally, and together they solve a problem no single controller handles well: balancing a power grid, containing a wildfire, running hotel operations.

| App | Agents | Shared resource | Folder |
| :-- | :-- | :-- | :-- |
| Energy grid | Smart battery nodes on the ERCOT COAST grid | Grid capacity at peak hours | [`apps/energy`](apps/energy/README.md) |
| Wildfire | Retardant drones over a forest | Retardant and flight time | [`apps/wildfire`](apps/wildfire/README.md) |
| Hotel | Equipment, room attendants, staff and properties | Peak-hour grid capacity, attendant time, rooms, shifts | [`apps/hotel`](apps/hotel/README.md) |

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

Trained with the configs in `configs/` on one 4-core CPU (energy about 2 minutes, wildfire about 40 minutes) and evaluated on data the swarm never trained on. Full tables are in [`results/`](results/).

**Energy** (10 batteries, 1 GW / 4 GWh fleet; trained Jan-Sep 2020, tested Oct-Dec 2020):

| Policy | Peak reduction | Load spread (std) reduced | Peak-to-average after (1.579 before) |
| :-- | --: | --: | --: |
| Swarm (trained) | **949 MW** | **9.9%** | **1.496** |
| Proportional rule | 0 MW | 9.1% | 1.577 |
| Threshold rule | 0 MW | 5.0% | 1.577 |

The rules empty the batteries in the hours before the evening peak; the swarm learns to keep charge for the peak hour itself. Peak reduction varies between training settings (one 3-step run reached 0 MW peak but the best std reduction, 11.0%); the config uses the 1-step setting, chosen by looking at these held-out months, so treat this as a validation result until it is confirmed on 2022 with `configs/energy-full.yaml`.

**Wildfire** (6 drones, 16x16 forest, 50 unseen fires with random ignition and wind):

| Policy | Forest saved | Peak burning cells |
| :-- | --: | --: |
| Nearest-fire rule | **90.1%** | **10.4** |
| Swarm (trained) | 77.3% | 15.5 |
| Random | 36.8% | 34.7 |
| No drones | 33.2% | 37.9 |

The learned swarm is far better than no action, but the hand-written nearest-fire rule still wins. **Learning from the rule first** (`configs/wildfire-imitate.yaml`: pre-train on the rule's moves, then reinforcement learning) raises the swarm to **87.2%** forest saved (copying the rule alone gives 83.2%), closing most of the gap to the rule's 90.1% ([`results/wildfire-imitate.md`](results/wildfire-imitate.md)).

**Hotel swarms** (five sample hotels; held-out days or generated scenarios; dollar figures rest on the assumptions in each config):

| Swarm | Swarm result | Best simple rule | Exact optimum |
| :-- | :-- | :-- | :-- |
| Peak-hour energy, HARLTON-01 (16 equipment agents, RL) | $279k/yr net, 666 kW off the top 5 grid hours | Peak-alert rule $251k/yr, 561 kW | n/a |
| Housekeeping, H2-03 (8 attendants, RL) | 23.3 guest wait hours/day | Soonest-needed 21.5 h; today's floor order 111 h | n/a |
| Guest relocation, HARLTON-02 (auction) | +$4.6k net per oversold night | Nearest sister hotel +$3.6k; walking guests -$10.2k | +$4.9k |
| Shift exchange, H2-01 (contract net, Ontario ESA rules) | $4.8k per week of open shifts | First to accept $5.2k; agency only $8.0k | $4.7k |

The learned housekeeping swarm does not beat the soonest-needed rule yet; both cut guest waiting about five-fold against cleaning in floor order. The PuLP schedule from the existing analytics costs $39.4k vs $50.0k for the fixed weekly pattern in the coming-week forecast.

**Scale** (research objective 2, `swarm scale`): one model trained with 10 batteries or 6 drones runs unchanged at 10, 100 and 1,000 agents with the same 18k / 110k parameters ([`results/scale-energy.md`](results/scale-energy.md), [`results/scale-wildfire.md`](results/scale-wildfire.md)). The battery swarm gives the same 949 MW peak cut at every size (the fleet stays 1 GW). The drones beat the rule at 10 (82.9% vs 79.4%) but fall behind at 100 and 1,000 (41% vs 47%, 26% vs 40%) on forests grown to match, where one corner launch pad means long refill trips: more pads are the next step. Choosing all 1,000 agents' actions takes 3.5 ms; a training update grows with agents (835 ms at 1,000 drones, batch 32).

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
