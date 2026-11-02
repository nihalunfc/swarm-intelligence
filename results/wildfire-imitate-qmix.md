# Multi-seed results

## wildfire-imitate-qmix

3 training seeds (0, 1, 2) x 50 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| swarm (trained) | 86.82 [82.80, 90.09] | 33.75 [25.37, 44.03] | 11.47 [9.64, 13.53] | 1.00 [1.00, 1.00] | -3.17 [-4.20, -2.34] |
| no drones | 33.22 [27.52, 39.37] | 170.96 [155.22, 185.56] | 37.90 [34.48, 41.36] | 1.00 [1.00, 1.00] | -16.90 [-18.36, -15.32] |
| random | 36.80 [30.75, 42.84] | 161.78 [146.32, 177.28] | 34.70 [31.42, 38.02] | 1.00 [1.00, 1.00] | -15.98 [-17.53, -14.43] |
| nearest-fire rule | 90.10 [87.39, 92.52] | 25.34 [19.16, 32.28] | 10.36 [8.84, 12.00] | 1.00 [1.00, 1.00] | -2.33 [-3.03, -1.72] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| no drones | 53.60 [47.62, 58.95], p=<0.001 | -137.21 [-150.91, -121.91], p=<0.001 | -26.43 [-29.33, -23.43], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | 13.72 [12.19, 15.09], p=<0.001 |
| random | 50.01 [43.72, 56.43], p=<0.001 | -128.03 [-144.46, -111.92], p=<0.001 | -23.23 [-26.29, -20.23], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | 12.80 [11.19, 14.45], p=<0.001 |
| nearest-fire rule | -3.28 [-6.98, -0.15], p=0.038 | 8.41 [0.37, 17.87], p=0.038 | 1.11 [-0.70, 2.97], p=0.223 | 0.00 [0.00, 0.00], p=1.000 | -0.84 [-1.79, -0.04], p=0.038 |
