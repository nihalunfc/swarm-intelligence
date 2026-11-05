# Multi-seed results

## wildfire

3 training seeds (0, 1, 2) x 50 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| swarm (trained) | 79.20 [73.18, 84.78] | 53.26 [38.97, 68.66] | 14.43 [11.77, 17.39] | 1.00 [1.00, 1.00] | -5.13 [-6.67, -3.70] |
| no drones | 33.22 [27.52, 39.37] | 170.96 [155.22, 185.56] | 37.90 [34.48, 41.36] | 1.00 [1.00, 1.00] | -16.90 [-18.36, -15.32] |
| random | 36.80 [30.75, 42.84] | 161.78 [146.32, 177.28] | 34.70 [31.42, 38.02] | 1.00 [1.00, 1.00] | -15.98 [-17.53, -14.43] |
| nearest-fire rule | 90.10 [87.39, 92.52] | 25.34 [19.16, 32.28] | 10.36 [8.84, 12.00] | 1.00 [1.00, 1.00] | -2.33 [-3.03, -1.72] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| no drones | 45.98 [39.74, 52.00], p=<0.001 | -117.70 [-133.12, -101.74], p=<0.001 | -23.47 [-26.32, -20.65], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | 11.77 [10.17, 13.31], p=<0.001 |
| random | 42.39 [35.14, 49.51], p=<0.001 | -108.52 [-126.74, -89.96], p=<0.001 | -20.27 [-23.53, -17.05], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | 10.85 [9.00, 12.67], p=<0.001 |
| nearest-fire rule | -10.91 [-16.64, -5.73], p=<0.001 | 27.92 [14.66, 42.61], p=<0.001 | 4.07 [1.65, 6.90], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | -2.79 [-4.26, -1.47], p=<0.001 |
