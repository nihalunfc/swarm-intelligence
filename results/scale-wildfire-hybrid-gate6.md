# Scale test: rule-led hybrid drone swarm

Trained with 6 drones only (configs/wildfire-hybrid.yaml); every larger swarm is a zero-shot test on a forest tiled with one launch pad per 16x16 tile. 10 test fires per size (seeds 10000+, never used in training or validation), the same fires for every policy. Mean [95% bootstrap interval over training seeds and fires]. Sensor noise is Gaussian noise on the drones' inputs; the rule reads the true state, so its row does not change with noise.

Gate: each drone follows the rule unless its best override beats "follow rule" by a margin chosen on 20 validation fires with 6 drones (an infinite margin is the rule itself). "gate off" is the same network acting greedily.

Chosen margins (seeds 0, 1, 2): hybrid, final weights: 0.02, 0.1, inf; hybrid, best-on-validation: inf, inf, inf; hybrid, old inputs: 0.05, inf, inf

## forest_saved_pct, sensor noise 0.0

| policy | 6 drones | 24 drones | 100 drones | 1,000 drones |
| :-- | --: | --: | --: | --: |
| nearest-fire rule | 92.2 [89.2, 95.1] | 88.8 [83.4, 93.8] | 90.6 [88.2, 93.0] | 86.4 [84.3, 88.8] |
| hybrid, final weights | 92.1 [90.3, 93.8] | 75.4 [60.4, 88.1] | 65.4 [44.6, 90.4] | 67.6 [52.1, 86.1] |
| &nbsp;&nbsp;minus rule | -0.1 [-0.4, +0.2] | -13.5 [-27.2, +0.0] | -25.2 [-47.0, +0.0] | -18.9 [-33.8, +0.0] |
| hybrid, final weights, gate off | 90.8 [88.3, 93.1] | 70.9 [59.4, 81.3] | 53.2 [37.9, 66.4] | 58.3 [48.5, 66.0] |
| &nbsp;&nbsp;minus rule | -1.4 [-3.3, +0.1] | -17.9 [-27.3, -9.3] | -37.5 [-51.7, -25.3] | -28.2 [-37.7, -21.0] |
| hybrid, best-on-validation | 92.2 [90.5, 94.0] | 88.8 [85.4, 91.8] | 90.6 [89.2, 92.0] | 86.4 [85.2, 87.7] |
| &nbsp;&nbsp;minus rule | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |
| hybrid, old inputs | 92.0 [89.9, 93.8] | 88.3 [85.2, 91.4] | 90.3 [88.7, 91.8] | 86.0 [84.5, 87.5] |
| &nbsp;&nbsp;minus rule | -0.2 [-1.4, +0.6] | -0.6 [-2.7, +0.6] | -0.3 [-1.1, +0.1] | -0.4 [-1.2, +0.0] |

## forest_saved_pct, sensor noise 0.1

| policy | 6 drones | 24 drones | 100 drones | 1,000 drones |
| :-- | --: | --: | --: | --: |
| nearest-fire rule | 92.2 [89.1, 95.2] | 88.8 [83.3, 93.8] | 90.6 [88.1, 93.0] | 86.4 [84.3, 88.8] |
| hybrid, final weights | 63.2 [41.3, 91.8] | 51.1 [25.8, 87.1] | 47.3 [18.8, 90.5] | 41.7 [13.4, 86.2] |
| &nbsp;&nbsp;minus rule | -29.0 [-50.0, +0.0] | -37.7 [-62.4, +0.0] | -43.4 [-71.5, +0.0] | -44.7 [-72.5, +0.0] |
| hybrid, final weights, gate off | 51.6 [40.3, 62.2] | 34.4 [24.9, 43.2] | 27.5 [14.5, 41.5] | 26.4 [13.1, 43.2] |
| &nbsp;&nbsp;minus rule | -40.5 [-50.6, -30.3] | -54.4 [-62.0, -47.5] | -63.1 [-76.6, -49.0] | -60.0 [-72.5, -43.5] |
| hybrid, best-on-validation | 92.2 [90.4, 93.9] | 88.8 [85.7, 91.7] | 90.6 [89.2, 92.1] | 86.4 [85.2, 87.7] |
| &nbsp;&nbsp;minus rule | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |
| hybrid, old inputs | 88.5 [79.8, 93.5] | 87.6 [83.7, 91.2] | 88.4 [83.5, 91.7] | 85.0 [82.1, 87.4] |
| &nbsp;&nbsp;minus rule | -3.7 [-11.9, +0.0] | -1.2 [-4.2, +0.0] | -2.2 [-6.2, +0.0] | -1.5 [-4.3, +0.0] |

## forest_saved_pct, sensor noise 0.3

| policy | 6 drones | 24 drones | 100 drones | 1,000 drones |
| :-- | --: | --: | --: | --: |
| nearest-fire rule | 92.2 [89.1, 95.1] | 88.8 [83.4, 93.8] | 90.6 [88.2, 93.0] | 86.4 [84.3, 88.7] |
| hybrid, final weights | 60.1 [37.5, 91.5] | 45.2 [17.2, 88.9] | 42.9 [15.2, 90.5] | 36.4 [8.0, 86.0] |
| &nbsp;&nbsp;minus rule | -32.1 [-53.2, +0.0] | -43.6 [-71.3, +0.0] | -47.8 [-75.0, +0.0] | -50.0 [-77.8, +0.0] |
| hybrid, final weights, gate off | 44.8 [36.2, 53.1] | 25.5 [16.2, 35.9] | 18.1 [12.0, 24.9] | 14.7 [8.9, 22.0] |
| &nbsp;&nbsp;minus rule | -47.4 [-55.1, -40.4] | -63.3 [-72.0, -54.0] | -72.5 [-78.0, -66.5] | -71.7 [-76.9, -65.0] |
| hybrid, best-on-validation | 92.2 [90.5, 93.9] | 88.8 [85.5, 91.9] | 90.6 [89.2, 92.0] | 86.4 [85.2, 87.8] |
| &nbsp;&nbsp;minus rule | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] | +0.0 [+0.0, +0.0] |
| hybrid, old inputs | 84.9 [70.1, 93.4] | 80.3 [63.5, 91.1] | 81.1 [62.8, 91.6] | 80.8 [70.0, 87.3] |
| &nbsp;&nbsp;minus rule | -7.3 [-21.3, +0.0] | -8.5 [-26.3, +0.0] | -9.5 [-27.5, +0.0] | -5.7 [-16.3, +0.0] |

## How often drones leave the rule (% of drone-steps)

| policy | noise | 6 | 24 | 100 | 1,000 |
| :-- | --: | --: | --: | --: | --: |
| hybrid, best-on-validation | 0.0 | 0.00 | 0.00 | 0.00 | 0.00 |
| hybrid, best-on-validation | 0.1 | 0.00 | 0.00 | 0.00 | 0.00 |
| hybrid, best-on-validation | 0.3 | 0.00 | 0.00 | 0.00 | 0.00 |
| hybrid, final weights, gate off | 0.0 | 23.58 | 43.76 | 64.53 | 68.06 |
| hybrid, final weights, gate off | 0.1 | 73.20 | 76.54 | 79.03 | 83.87 |
| hybrid, final weights, gate off | 0.3 | 79.92 | 82.98 | 85.01 | 85.95 |
| hybrid, final weights | 0.0 | 8.00 | 25.55 | 38.99 | 43.20 |
| hybrid, final weights | 0.1 | 48.13 | 50.30 | 50.65 | 55.06 |
| hybrid, final weights | 0.3 | 51.64 | 53.71 | 54.66 | 54.56 |
| hybrid, old inputs | 0.0 | 1.89 | 9.34 | 11.30 | 11.88 |
| hybrid, old inputs | 0.1 | 10.57 | 11.36 | 11.36 | 10.86 |
| hybrid, old inputs | 0.3 | 15.88 | 16.10 | 15.88 | 15.55 |
