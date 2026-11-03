# Multi-seed results

## wildfire-mappo

3 training seeds (0, 1, 2) x 50 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| swarm (trained) | 72.11 [62.22, 80.97] | 71.39 [48.72, 96.71] | 16.86 [13.34, 20.44] | 0.99 [0.96, 1.00] | -6.94 [-9.47, -4.67] |
| no drones | 33.22 [27.52, 39.37] | 170.96 [155.22, 185.56] | 37.90 [34.48, 41.36] | 1.00 [1.00, 1.00] | -16.90 [-18.36, -15.32] |
| random | 36.80 [30.75, 42.84] | 161.78 [146.32, 177.28] | 34.70 [31.42, 38.02] | 1.00 [1.00, 1.00] | -15.98 [-17.53, -14.43] |
| nearest-fire rule | 90.10 [87.39, 92.52] | 25.34 [19.16, 32.28] | 10.36 [8.84, 12.00] | 1.00 [1.00, 1.00] | -2.33 [-3.03, -1.72] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| no drones | 38.89 [28.90, 48.05], p=<0.001 | -99.57 [-123.01, -73.98], p=<0.001 | -21.04 [-24.68, -17.25], p=<0.001 | -0.01 [-0.04, 0.00], p=0.576 | 9.96 [7.40, 12.30], p=<0.001 |
| random | 35.31 [25.62, 44.98], p=<0.001 | -90.39 [-115.16, -65.58], p=<0.001 | -17.84 [-21.50, -14.13], p=<0.001 | -0.01 [-0.04, 0.00], p=0.576 | 9.04 [6.56, 11.52], p=<0.001 |
| nearest-fire rule | -17.99 [-27.59, -9.20], p=<0.001 | 46.05 [23.54, 70.63], p=<0.001 | 6.50 [3.20, 9.90], p=<0.001 | -0.01 [-0.04, 0.00], p=0.576 | -4.61 [-7.06, -2.35], p=<0.001 |
