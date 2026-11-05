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
swarm seeds --config configs/energy.yaml --seeds 0 1 2 3 4   # several seeds, CIs and paired tests
swarm robustness runs/seeds-energy-* --output results/robustness-energy
make reproduce                                    # every table in results/ (hours on a CPU)
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

Every number below is a mean over independently trained seeds and the same held-out test episodes, with a 95% hierarchical bootstrap interval. Rules and bounds play exactly the same episodes. The splits, statistics and reference points are described in [docs/evaluation-protocol.md](docs/evaluation-protocol.md). Full tables are in [`results/`](results/), per-seed raw episodes are in `results/runs/`, and the long runs are reproduced on GitHub Actions ([`experiments/queue.yaml`](experiments/queue.yaml)).

**Energy**: 10 batteries, 1 GW / 4 GWh fleet, ERCOT COAST 2020. The swarm validates on September and is tested on Oct–Dec. 10 seeds ([`results/energy.md`](results/energy.md)).

| Policy | Load spread (std) reduced | Peak reduction |
| :-- | --: | --: |
| Swarm (VDN DQN) | **10.8% [10.6, 11.0]** | 704 MW [547, 857] |
| Proportional rule | 9.1% | 0 MW |
| MPC on a 24 h forecast | 6.8% | 0 MW |
| Threshold rule | 5.0% | 0 MW |
| Perfect-foresight optimum (bound) | 14.7% | 949 MW |

- On load spread, the swarm beats every rule and the MPC baseline (p < 0.001 for each).
- It closes about 74% of the gap between doing nothing and the perfect-foresight optimum of its own objective.
- Its peak cut depends on the seed. QMIX gives a similar result. Independent learners, 3-step returns and MAPPO keep less of the peak.
- Choosing the checkpoint on validation does not change the spread result but helps keep the peak cut (705 vs 483 MW, not significant) ([`results/methods-energy.md`](results/methods-energy.md)).
- **Robustness:** with 30% of batteries failing mid-period it still reduces the spread by 10.0%, which beats every rule even with all their batteries working ([`results/robustness-energy.md`](results/robustness-energy.md)).

**Hotel housekeeping**: 8 room attendants, 50 generated test days, 5 seeds ([`results/methods-hotel-housekeeping.md`](results/methods-hotel-housekeeping.md)).

| Policy | Guest waiting (hours/day) |
| :-- | --: |
| Today's floor order | 111.3 |
| Swarm (VDN DQN) | 22.4 [19.4, 25.4] |
| MAPPO | 21.6 [18.8, 24.5] |
| Independent learners | 21.9 [18.9, 24.8] |
| Residual swarm (rule + learned overrides) | 21.5 [18.7, 24.4] |
| Soonest-needed rule | 21.5 [18.7, 24.3] |
| Lower bound (perfect foresight, no elevator time) | 18.1 |

- Every learned swarm cuts waiting about five-fold against floor order.
- None beats the soonest-needed rule. The residual swarm learns that the rule is already hard to improve on and leaves it unchanged.
- At most 3.5 hours/day of guest waiting remain to be won, and that gap is a bound, not a target.

**Wildfire**: 6 drones on a 16x16 forest, 50 unseen fires ([`results/methods-wildfire.md`](results/methods-wildfire.md)).

| Policy | Forest saved |
| :-- | --: |
| Spread rule (new hand-written coordination rule, target-choice actions) | **91.2% [88.9, 93.2]** |
| Nearest-fire rule | 90.1% [87.4, 92.5] |
| Residual swarm: rule + learned overrides (3 seeds) | 89.8% [86.6, 92.0] |
| Learning from the rule, then RL (5 seeds) | 87.2% [82.3, 90.9] |
| Same with QMIX (3 seeds) | 86.8% [82.8, 90.1] |
| Same with neighbour messages (3 seeds) | 82.1% [77.6, 86.0] |
| RL from scratch (3 seeds) | 79.2% [73.2, 84.8] |
| MAPPO (3 seeds) | 72.1% [62.2, 81.0] |
| No drones | 33.2% |

- **No learned swarm beats the nearest-fire rule.** The residual swarm matches it (−0.3 points, p = 0.81) with fewer burning cells at the peak (p = 0.02).
- Learning from the rule first is the best way to train from the rule's moves.
- Neighbour messages make things worse at this budget.
- The coordination idea that helps is hand-written. Letting drones choose *which* fire to fight, and taking the nearest one no other drone is closer to, beats nearest-fire by 2.4 points. A swarm trained in that action space reaches 88.0% ([`results/wildfire-targets.md`](results/wildfire-targets.md)).
- **Robustness:** with half the drones failing, every policy keeps at least 93% of its result. Sensor noise hurts the DQN swarms: the best one drops from 87% to 44% saved at noise 0.3. MAPPO is unaffected, and the rules read the true state, so noise cannot reach them ([`results/robustness-wildfire-imitate.md`](results/robustness-wildfire-imitate.md)).

**External benchmarks**: the same engine on two community benchmarks, 3 seeds each.

- **CityLearn Challenge 2022** (17 homes, Oct–Dec test). The swarm's district score is **0.96 [0.95, 0.97]**, against 1.03 for CityLearn's OptimizedRBC and 1.13 for its BasicRBC (lower is better; 1.0 = no battery control). It cuts cost by 8% and the average daily peak by 15% ([`results/citylearn.md`](results/citylearn.md)).
- **VMAS navigation** (4 robots). The swarm reaches 91% of goals with 0.07 collisions per episode. The go-to-goal rule reaches 98% but has 16 collisions ([`results/vmas-navigation.md`](results/vmas-navigation.md)).

**Hotel energy, relocation and shifts** (five sample hotels; dollar figures rest on the assumptions in each config). With 5 seeds, the peak-hour energy swarm is worse than the peak-alert rule by $40k/yr (p = 0.03). An earlier single-seed run had shown $279k; it was a lucky seed ([`results/hotel-energy.md`](results/hotel-energy.md)).

| Swarm | Swarm result | Best simple rule | Exact optimum |
| :-- | :-- | :-- | :-- |
| Peak-hour energy, HARLTON-01 (16 equipment agents, RL, 5 seeds) | $211k/yr net [166k, 250k], 486 kW off the top 5 grid hours | **Peak-alert rule $252k/yr, 561 kW** | n/a |
| Guest relocation, HARLTON-02 (auction) | +$4.6k net per oversold night | Nearest sister hotel +$3.6k; walking guests -$10.2k | +$4.9k |
| Shift exchange, H2-01 (contract net, Ontario ESA rules) | $4.8k per week of open shifts | First to accept $5.2k; agency only $8.0k | $4.7k |

**Scale** (`swarm scale`): one model runs unchanged at any swarm size with the same 18k / 110k parameters. Choosing actions for all 1,000 drones takes 2.8 ms.

- **Battery swarm:** keeps its peak cut at every size, because the fleet stays 1 GW.
- **Drone simulator fix:** launch pads that tile the forest keep refill trips short. The nearest-fire rule now saves 86% of the forest at 1,000 drones, against 40% with one pad.
- **Learned drone swarms do not scale on this task** ([`results/scale-wildfire-imitate-pads.md`](results/scale-wildfire-imitate-pads.md), [`results/scale-wildfire-scale.md`](results/scale-wildfire-scale.md)):

| Forest saved | 6 drones | 24 | 100 | 1,000 |
| :-- | --: | --: | --: | --: |
| Nearest-fire rule | 91.6% | 87.8% | 91.6% | 85.9% |
| Swarm trained with 6 drones (3 seeds) | 90.5% | 82.6% | 65.9% | 47.9% |
| Swarm with a 6→24 drone curriculum (3 seeds) | 70.8% | 67.6% | 43.7% | 33.2% |

- The swarm trained with 6 drones matches the rule at its training size, then falls behind as the swarm grows.
- Training on 24 drones (the curriculum) made it worse at every size. How to train swarms that grow is still an open question here.

**What is not claimed.** The learned swarms beat the rules on grid energy and CityLearn. They do not beat them on housekeeping, wildfire or hotel peak energy, and on wildfire they do not scale past their training size. Every simulator here is simplified. See the [model card](docs/model-card.md) and the [dataset card](docs/dataset-card.md).

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
