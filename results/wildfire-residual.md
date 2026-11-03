# Multi-seed results

## wildfire-residual

3 training seeds (0, 1, 2) x 50 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| swarm (trained) | 89.77 [86.58, 92.03] | 26.19 [20.40, 34.35] | 9.90 [8.56, 11.35] | 1.00 [1.00, 1.00] | -2.48 [-3.32, -1.88] |
| no drones | 33.22 [27.52, 39.37] | 170.96 [155.22, 185.56] | 37.90 [34.48, 41.36] | 1.00 [1.00, 1.00] | -18.69 [-20.21, -17.05] |
| random | 36.80 [30.75, 42.84] | 161.78 [146.32, 177.28] | 34.70 [31.42, 38.02] | 1.00 [1.00, 1.00] | -17.41 [-19.02, -15.79] |
| nearest-fire rule | 90.10 [87.39, 92.52] | 25.34 [19.16, 32.28] | 10.36 [8.84, 12.00] | 1.00 [1.00, 1.00] | -2.37 [-3.07, -1.75] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| no drones | 56.55 [50.94, 61.68], p=<0.001 | -144.77 [-157.91, -130.42], p=<0.001 | -28.00 [-31.01, -24.93], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | 16.21 [14.71, 17.59], p=<0.001 |
| random | 52.96 [46.87, 59.01], p=<0.001 | -135.59 [-151.06, -120.00], p=<0.001 | -24.80 [-27.83, -21.73], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | 14.92 [13.29, 16.56], p=<0.001 |
| nearest-fire rule | -0.33 [-3.28, 2.48], p=0.808 | 0.85 [-6.36, 8.40], p=0.808 | -0.46 [-2.04, 1.14], p=0.567 | 0.00 [0.00, 0.00], p=1.000 | -0.11 [-0.89, 0.61], p=0.745 |
