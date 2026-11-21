# Multi-seed results

## wildfire-crew-control

3 training seeds (0, 1, 2) x 50 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| swarm (trained) | 72.55 [65.13, 79.34] | 70.27 [52.88, 89.26] | 16.18 [13.08, 19.65] | 0.99 [0.96, 1.00] | -6.83 [-8.73, -5.09] |
| no drones | 33.22 [27.52, 39.37] | 170.96 [155.22, 185.56] | 37.90 [34.48, 41.36] | 1.00 [1.00, 1.00] | -16.90 [-18.36, -15.32] |
| random | 36.80 [30.75, 42.84] | 161.78 [146.32, 177.28] | 34.70 [31.42, 38.02] | 1.00 [1.00, 1.00] | -15.98 [-17.53, -14.43] |
| nearest-fire rule | 90.10 [87.39, 92.52] | 25.34 [19.16, 32.28] | 10.36 [8.84, 12.00] | 1.00 [1.00, 1.00] | -2.33 [-3.03, -1.72] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| no drones | 39.33 [32.53, 46.67], p=<0.001 | -100.69 [-119.47, -83.28], p=<0.001 | -21.72 [-24.98, -18.62], p=<0.001 | -0.01 [-0.04, 0.00], p=1.000 | 10.07 [8.33, 11.95], p=<0.001 |
| random | 35.74 [27.45, 44.19], p=<0.001 | -91.51 [-113.12, -70.28], p=<0.001 | -18.52 [-21.81, -15.33], p=<0.001 | -0.01 [-0.04, 0.00], p=1.000 | 9.15 [7.03, 11.31], p=<0.001 |
| nearest-fire rule | -17.55 [-24.23, -11.27], p=<0.001 | 44.93 [28.84, 62.02], p=<0.001 | 5.82 [3.14, 8.98], p=<0.001 | -0.01 [-0.04, 0.00], p=1.000 | -4.49 [-6.20, -2.88], p=<0.001 |
