# Model card: swarm policies

This card follows the structure of Mitchell et al. (2019), "Model Cards for Model Reporting". It covers every policy trained by `swarm train` in this repository.

## Model details

- **Author:** Nihal. MIT license. Cite with [`CITATION.cff`](../CITATION.cff).
- **Type:** cooperative multi-agent reinforcement learning. Every agent runs the same small network on its own local observation, so the model does not grow with the number of agents.
- **Algorithms:**
  - Parameter-shared DQN with VDN, QMIX or independent learners, Double DQN and n-step returns ([`agents.py`](../core/swarm/agents.py)).
  - DQfD-style pre-training on a hand-written rule ([`trainer.py`](../core/swarm/trainer.py)).
  - Residual swarm: the rule plus a learned override ([`residual.py`](../core/swarm/residual.py)).
  - MAPPO with a pooled centralised critic ([`ppo.py`](../core/swarm/ppo.py)).
- **Size:** about 18k parameters (energy) to 110k (wildfire). Choosing actions for 1,000 agents takes a few milliseconds on a CPU.
- **Versions:** each run folder has a `manifest.json` with the git commit, library versions, machine and command.

## Intended use

- **Intended:** research and teaching on decentralised control, as a benchmark for comparing learned swarms with rules and optimisation bounds, and as a prototype to show what a swarm controller could do before a real pilot.
- **Not intended:** controlling real batteries, aircraft, buildings or staff. None of these policies has been tested on hardware or with people. Every decision would need a human operator, a safety layer and a proper field trial first.

## Training and evaluation data

See the [dataset card](dataset-card.md). Every app has separate train, validation and test splits ([evaluation protocol](evaluation-protocol.md)). Checkpoints are chosen on validation, and reported numbers come from the test split only.

## Metrics

Each app reports its own operational metric next to the training return:

| App | Main metric |
| :-- | :-- |
| Energy | peak reduction (MW), load spread (std) reduction, peak-to-average ratio |
| Hotel peak energy | kW taken off the grid's top hours, net $ per year |
| Housekeeping | guest waiting hours per day |
| Wildfire | forest saved (%), peak burning cells |
| CityLearn | the challenge's district cost, emissions, ramping and load-factor KPIs |
| VMAS navigation | success rate, collisions |

All numbers are means over training seeds and test episodes, with 95% hierarchical bootstrap intervals. Comparisons with rules are paired on the same episodes.

## Results summary

Full tables are in [`results/`](../results/). In short:

- **Energy:** the swarm beats every rule and the 24 h MPC on load-spread reduction, and closes most of the gap to the perfect-foresight optimum. Its peak cut varies between training seeds.
- **Wildfire and housekeeping:** the best hand-written rule is still at least as good as the learned swarm. Learning from the rule and the residual formulation close most of the gap, but they have not yet clearly beaten the rule.
- **Scale:** the same weights run at 10, 100 and 1,000 agents.

## Limitations and risks

- **Simulators:** wildfire, housekeeping and VMAS are simplified simulators. Results do not carry over to real fires, hotels or robots without new validation.
- **Data:**
  - Energy uses one ERCOT zone and one year (2020) in the committed sample.
  - Hotel data is synthetic (five fictional hotels).
  - Dollar figures rest on the assumptions written in each config.
- **Seed variance:** RL results vary between training seeds. Single-seed numbers in older result files are labelled as such and should not be quoted on their own.
- **Distribution shift:** the policies have not been tested under real distribution shift. The robustness study (`swarm robustness`) covers agent failures, observation noise and a few unseen conditions only.
- **No safety guarantees:** action masks block physically impossible moves, such as charging a full battery, but nothing more.

## Ethical considerations

- The housekeeping and shift apps model people's work. A real system must leave final assignment to supervisors, follow labour law (the shift app encodes Ontario ESA rules) and must not be used to monitor or rank individual staff.
- No personal data is used.
