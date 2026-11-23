# Rule-led hybrid drone swarm at 1,000 drones

**Question.** Learned drone swarms trained with 6 drones fall from about 90% to 48% forest saved at 1,000
drones, while the nearest-fire rule holds 86% ([scale-wildfire-imitate-pads.md](scale-wildfire-imitate-pads.md)).
Can a hybrid, where the rule leads and learning only adds small corrections, close that gap and still add something?

**Short answer.** The gap closes, but the learning adds nothing. The hybrid matches the rule exactly at every size
(86.4% at 1,000 drones, same fires). It does that because every learned correction we trained either failed to beat
the rule on validation fires, or beat it only at 6 drones and then hurt at larger sizes and under sensor noise. A
validation check at 100 drones catches that and switches the corrections off. The rule stays.

## What was built

1. **Size-invariant drone inputs** (`env.obs_mode: local`, `apps/wildfire/env.py`). The original inputs divide
   positions and directions by the forest size. On the 1,000-drone forest (208 cells) the direction to the launch pad
   comes out about 30 times smaller than in training, and the direction to the nearest fire about 4 times smaller.
   In local mode everything is measured in cells and clipped at 16; absolute position becomes "is an edge in view",
   and the global fire share becomes the share burning within 16 cells. Off by default, so old results reproduce.
2. **A confidence gate on the residual swarm** (`SwarmAgent.act`, `swarm residual-gate`, `core/swarm/residual.py`).
   A drone leaves the rule only when its best override beats "follow rule" by a margin. The margin is picked on
   validation fires only (never test); an infinite margin is the rule itself, so the chosen swarm is never worse than
   the rule on validation. `--sizes 100` also validates at a larger swarm, and the worst size counts.
3. **An imitation anchor** (`pretrain.demo_floor`, `core/swarm/trainer.py`): keeps part of the imitation loss for
   the whole run, so RL can only learn small corrections.
4. `swarm scale --noise` and residual runs in `swarm scale`; the full test is
   [experiments/wildfire_hybrid_scale.py](../experiments/wildfire_hybrid_scale.py).

All runs: config [configs/wildfire-hybrid.yaml](../configs/wildfire-hybrid.yaml), 6 drones, 400k steps, 3 seeds per
variant, trained locally (no GitHub Actions minutes). Tests: 10 unseen fires per size, the same fires for every
policy, 95% bootstrap intervals over seeds and fires.

## Results

| Variant (3 seeds each) | What happened in training | Forest saved, 6 / 24 / 100 / 1,000 drones |
| :-- | :-- | --: |
| Nearest-fire rule | – | 92.2 / 88.8 / 90.6 / 86.4 |
| Hybrid, best checkpoint on validation (local inputs) | RL never beat the rule on validation after the imitation phase; all 3 seeds kept the rule copy | 92.2 / 88.8 / 90.6 / 86.4 |
| Hybrid, old inputs (ablation) | same; 1 seed kept a small change | 92.0 / 88.3 / 90.3 / 86.0 |
| Hybrid with imitation anchor (floor 0.3) | never left the rule (identical to the rule on test) | = rule |
| Hybrid, final weights, no gate | RL moved away from the rule | 90.8 / 70.9 / 53.2 / 58.3 |
| same, gate tuned at 6 drones | picked margins 0.02, 0.1, inf | 92.1 / 75.4 / 65.4 / 67.6 |
| same, gate tuned at 6 and 100 drones | refused every correction (margin inf) | 92.2 / 88.8 / 90.6 / 86.4 |

Full tables, paired differences against the rule and override rates:
[scale-wildfire-hybrid.md](scale-wildfire-hybrid.md) (gate validated at 6 and 100 drones) and
[scale-wildfire-hybrid-gate6.md](scale-wildfire-hybrid-gate6.md) (gate validated at 6 drones only).

## Findings

- **The scale collapse is a property of the learned part, not of decentralisation.** Any variant that keeps the rule
  in charge holds 86% at 1,000 drones. Learned overrides grow with swarm size: the ungated final network overrides
  24% of drone-steps at 6 drones and 68% at 1,000.
- **Size-invariant inputs did not stop that.** With local inputs the learned network still overrides more as the swarm
  grows. The likely remaining causes are things a 16x16 forest never shows: crowds of other drones in view, fires
  further than 16 cells away, and many fronts at once. So the input fix is necessary but not enough.
- **Validating at the training size alone is not a safe check.** Gates tuned on 6-drone validation fires looked
  slightly better than the rule there (+0.5 to +0.7 points) and then lost 19 points at 1,000 drones and up to 50 points under
  sensor noise. Adding one validation size (100 drones) was enough to refuse them.
- **Sensor noise:** the hybrid that stays on the rule is untouched by noise (the rule reads the true state). Ungated
  learned corrections fall to 15-27% at 1,000 drones with noise 0.1-0.3.

## What this means

For a Canadian deployment the recommendation is the rule (or the spread rule, 91.2% at 6 drones) with a learned layer
only behind a gate that is validated at the deployment size. The gate and the larger-size validation are now in the
engine, so any future learned correction is checked the same way. Training on larger forests with many fronts is the
open next step; the 6→24 curriculum tried before made things worse, so it needs a different approach.
