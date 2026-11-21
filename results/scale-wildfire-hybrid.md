# Scale test: rule-led hybrid drone swarm

Trained with 6 drones only (configs/wildfire-hybrid.yaml); every larger swarm is a zero-shot test on a forest tiled with one launch pad per 16x16 tile. 10 test fires per size (seeds 10000+, never used in training or validation), the same fires for every policy. Mean [95% bootstrap interval over training seeds and fires]. Sensor noise is Gaussian noise on the drones' inputs; the rule reads the true state, so its row does not change with noise.

Gate: each drone follows the rule unless its best override beats "follow rule" by a margin chosen on 20 validation fires with 6 drones and with 100 drones (the worst size counts) (an infinite margin is the rule itself). "gate off" is the same network acting greedily.

Chosen margins (seeds 0, 1, 2): hybrid, final weights: inf, inf, inf; hybrid, best-on-validation: inf, inf, inf; hybrid, old inputs: inf, inf, inf

## forest_saved_pct, sensor noise 0.0

| policy | 6 drones | 24 drones | 100 drones | 1,000 drones |
| :-- | --: | --: | --: | --: |
| nearest-fire rule | 92.2 [89.2, 95.1] | 88.8 [83.4, 93.8] | 90.6 [88.2, 93.0] | 86.4 [84.3, 88.8] |
| hybrid, final weights | 92.2 [90.4, 93.8] | 88.8 [85.6, 91.9] | 90.6 [89.2, 92.0] | 86.4 [85.1, 87.8] |
| &nbsp;&nbsp;minus rule | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |
| hybrid, final weights, gate off | 90.8 [88.3, 93.1] | 70.9 [59.4, 81.3] | 53.2 [37.9, 66.4] | 58.3 [48.5, 66.0] |
| &nbsp;&nbsp;minus rule | -1.4 [-3.3, +0.1] | -17.9 [-27.3, -9.3] | -37.5 [-51.7, -25.3] | -28.2 [-37.7, -21.0] |
| hybrid, best-on-validation | 92.2 [90.5, 94.0] | 88.8 [85.4, 91.8] | 90.6 [89.2, 92.0] | 86.4 [85.2, 87.7] |
| &nbsp;&nbsp;minus rule | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |
| hybrid, old inputs | 92.2 [90.3, 93.8] | 88.8 [85.5, 91.9] | 90.6 [89.2, 92.0] | 86.4 [85.2, 87.7] |
| &nbsp;&nbsp;minus rule | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |

## forest_saved_pct, sensor noise 0.1

| policy | 6 drones | 24 drones | 100 drones | 1,000 drones |
| :-- | --: | --: | --: | --: |
| nearest-fire rule | 92.2 [89.1, 95.2] | 88.8 [83.3, 93.8] | 90.6 [88.1, 93.0] | 86.4 [84.3, 88.8] |
| hybrid, final weights | 92.2 [90.5, 94.0] | 88.8 [85.5, 91.8] | 90.6 [89.3, 92.0] | 86.4 [85.1, 87.8] |
| &nbsp;&nbsp;minus rule | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |
| hybrid, final weights, gate off | 51.6 [40.3, 62.2] | 34.4 [24.9, 43.2] | 27.5 [14.5, 41.5] | 26.4 [13.1, 43.2] |
| &nbsp;&nbsp;minus rule | -40.5 [-50.6, -30.3] | -54.4 [-62.0, -47.5] | -63.1 [-76.6, -49.0] | -60.0 [-72.5, -43.5] |
| hybrid, best-on-validation | 92.2 [90.4, 93.9] | 88.8 [85.7, 91.7] | 90.6 [89.2, 92.1] | 86.4 [85.2, 87.7] |
| &nbsp;&nbsp;minus rule | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |
| hybrid, old inputs | 92.2 [90.4, 93.8] | 88.8 [85.3, 91.9] | 90.6 [89.1, 92.1] | 86.4 [85.2, 87.7] |
| &nbsp;&nbsp;minus rule | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |

## forest_saved_pct, sensor noise 0.3

| policy | 6 drones | 24 drones | 100 drones | 1,000 drones |
| :-- | --: | --: | --: | --: |
| nearest-fire rule | 92.2 [89.1, 95.1] | 88.8 [83.4, 93.8] | 90.6 [88.2, 93.0] | 86.4 [84.3, 88.7] |
| hybrid, final weights | 92.2 [90.4, 93.9] | 88.8 [85.5, 91.8] | 90.6 [89.2, 92.0] | 86.4 [85.2, 87.7] |
| &nbsp;&nbsp;minus rule | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |
| hybrid, final weights, gate off | 44.8 [36.2, 53.1] | 25.5 [16.2, 35.9] | 18.1 [12.0, 24.9] | 14.7 [8.9, 22.0] |
| &nbsp;&nbsp;minus rule | -47.4 [-55.1, -40.4] | -63.3 [-72.0, -54.0] | -72.5 [-78.0, -66.5] | -71.7 [-76.9, -65.0] |
| hybrid, best-on-validation | 92.2 [90.5, 93.9] | 88.8 [85.5, 91.9] | 90.6 [89.2, 92.0] | 86.4 [85.2, 87.8] |
| &nbsp;&nbsp;minus rule | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |
| hybrid, old inputs | 92.2 [90.4, 93.9] | 88.8 [85.5, 91.8] | 90.6 [89.2, 92.0] | 86.4 [85.2, 87.7] |
| &nbsp;&nbsp;minus rule | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |

## How often drones leave the rule (% of drone-steps)

| policy | noise | 6 | 24 | 100 | 1,000 |
| :-- | --: | --: | --: | --: | --: |
| hybrid, best-on-validation | 0.0 | 0.00 | 0.00 | 0.00 | 0.00 |
| hybrid, best-on-validation | 0.1 | 0.00 | 0.00 | 0.00 | 0.00 |
| hybrid, best-on-validation | 0.3 | 0.00 | 0.00 | 0.00 | 0.00 |
| hybrid, final weights, gate off | 0.0 | 23.58 | 43.76 | 64.53 | 68.06 |
| hybrid, final weights, gate off | 0.1 | 73.20 | 76.54 | 79.03 | 83.87 |
| hybrid, final weights, gate off | 0.3 | 79.92 | 82.98 | 85.01 | 85.95 |
| hybrid, final weights | 0.0 | 0.00 | 0.00 | 0.00 | 0.00 |
| hybrid, final weights | 0.1 | 0.00 | 0.00 | 0.00 | 0.00 |
| hybrid, final weights | 0.3 | 0.00 | 0.00 | 0.00 | 0.00 |
| hybrid, old inputs | 0.0 | 0.00 | 0.00 | 0.00 | 0.00 |
| hybrid, old inputs | 0.1 | 0.00 | 0.00 | 0.00 | 0.00 |
| hybrid, old inputs | 0.3 | 0.00 | 0.00 | 0.00 | 0.00 |
