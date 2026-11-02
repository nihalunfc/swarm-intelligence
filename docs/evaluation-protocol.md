# Evaluation protocol

This page explains how every number in `results/` is produced, so that a reader can check or repeat it.

## Data splits

Each app has three disjoint splits. Settings and checkpoints are chosen on **validation**. **Test** is used only for the numbers that get reported.

| App | Train | Validation | Test |
| :-- | :-- | :-- | :-- |
| Energy (ERCOT COAST + NREL, 2020) | Jan–Aug | Sep | Oct–Dec |
| Hotel peak energy (summer 2020) | even ISO weeks | every other odd week | the remaining odd weeks |
| Wildfire, housekeeping, VMAS (generated) | episode seeds 0+ | seeds 5000+ | seeds 10000+ |
| CityLearn Challenge 2022 | Jan–Aug | Sep | Oct–Dec |

Checkpoint selection (`train.eval_every`): the greedy swarm plays the validation episodes at regular intervals, and the weights with the best `eval.select_metric` are kept. That metric is the return by default, and forest saved for wildfire.

## Seeds and statistics

- Every method is trained with several independent **training seeds**: 10 for energy, 5 for the main methods and 3 for the extra variants. All seeds play the same test episodes as the rules, because episode `k` always starts from seed `10000 + k`.
- **Confidence intervals** are 95% hierarchical bootstrap intervals (5,000 resamples). They resample seeds, then episodes within each seed (Agarwal et al., 2021). A rule has no training seed, so its interval covers episodes only.
- **Swarm vs rule** is a paired comparison on the same episodes. We report the mean difference, its 95% bootstrap interval, and a two-sided sign-flip permutation p-value on the per-episode differences, averaged over seeds. When there is only one test episode (a whole test period), the test runs over seeds instead. With 10 seeds the smallest possible p-value is then 2/1024.
- **Method vs method** (ablations, residual vs plain, MAPPO vs DQN) resamples each method's seeds independently and the shared episodes jointly (`swarm aggregate --compare-to`).

Code: [`core/swarm/stats.py`](../core/swarm/stats.py) and [`core/swarm/aggregate.py`](../core/swarm/aggregate.py).

## Reference points

| App | Simple rules | Strong baseline | Best possible |
| :-- | :-- | :-- | :-- |
| Energy | threshold, proportional | MPC on a 24 h seasonal-naive forecast | perfect-foresight LP (peak) and QP (the swarm's own squared objective) |
| Housekeeping | floor order, soonest needed | MAPPO | MILP lower bound on guest waiting (perfect foresight, no elevator time) |
| Wildfire | nearest-fire, random | QMIX, MAPPO | none known |
| CityLearn | CityLearn BasicRBC and OptimizedRBC | | |
| VMAS navigation | go-to-goal | MAPPO | |

The perfect-foresight bounds know the future and act continuously, so no real controller can reach them. They show how much room is left.

## Methods compared

- **Swarm (DQN)**: a shared Q-network per agent with VDN, QMIX or independent learners, Double DQN and n-step returns ([`agents.py`](../core/swarm/agents.py)).
- **Learning from the rule**: DQfD-style pre-training on the rule's moves with a large-margin loss, then RL ([`trainer.py`](../core/swarm/trainer.py)).
- **Residual swarm**: each agent sees the rule's suggestion and either follows it or overrides it, and starts as an exact copy of the rule ([`residual.py`](../core/swarm/residual.py)).
- **MAPPO**: a shared actor with a pooled centralised critic ([`ppo.py`](../core/swarm/ppo.py)).

## Robustness

`swarm robustness` re-evaluates every trained seed and every rule, without retraining, under these conditions: a share of agents failing mid-episode (they take the app's null action, and the others are not told), Gaussian observation noise, and conditions never seen in training. Scenarios are listed in [`experiments/robustness.yaml`](../experiments/robustness.yaml).

## Reproducing

- Locally: `make reproduce` (hours on a laptop CPU), or one app at a time with `swarm seeds --config ... --seeds 0 1 2 3 4`.
- On GitHub Actions: list experiments in [`experiments/queue.yaml`](../experiments/queue.yaml) and push. Each seed runs as its own job, and the aggregated tables are committed back to `results/`.
- Every run directory has a `manifest.json` (git commit, library versions, machine, command) and `episodes.json` (per-episode metrics for every policy).
