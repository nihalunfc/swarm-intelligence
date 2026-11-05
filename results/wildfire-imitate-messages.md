# Multi-seed results

## wildfire-imitate-messages

3 training seeds (0, 1, 2) x 50 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| swarm (trained) | 82.06 [77.56, 86.03] | 45.93 [35.77, 57.45] | 13.26 [11.07, 15.62] | 1.00 [1.00, 1.00] | -4.39 [-5.54, -3.38] |
| no drones | 33.22 [27.52, 39.37] | 170.96 [155.22, 185.56] | 37.90 [34.48, 41.36] | 1.00 [1.00, 1.00] | -16.90 [-18.36, -15.32] |
| random | 36.80 [30.75, 42.84] | 161.78 [146.32, 177.28] | 34.70 [31.42, 38.02] | 1.00 [1.00, 1.00] | -15.98 [-17.53, -14.43] |
| nearest-fire rule | 90.10 [87.39, 92.52] | 25.34 [19.16, 32.28] | 10.36 [8.84, 12.00] | 1.00 [1.00, 1.00] | -2.33 [-3.03, -1.72] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| no drones | 48.84 [43.18, 54.40], p=<0.001 | -125.03 [-139.25, -110.54], p=<0.001 | -24.64 [-27.31, -21.93], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | 12.50 [11.05, 13.93], p=<0.001 |
| random | 45.26 [38.89, 51.73], p=<0.001 | -115.85 [-132.42, -99.57], p=<0.001 | -21.44 [-24.42, -18.53], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | 11.59 [9.96, 13.24], p=<0.001 |
| nearest-fire rule | -8.04 [-12.26, -4.21], p=<0.001 | 20.59 [10.77, 31.37], p=<0.001 | 2.90 [0.79, 5.05], p=0.008 | 0.00 [0.00, 0.00], p=1.000 | -2.06 [-3.14, -1.08], p=<0.001 |
