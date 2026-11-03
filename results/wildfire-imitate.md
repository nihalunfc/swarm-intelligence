# Multi-seed results

## wildfire-imitate

5 training seeds (0, 1, 2, 3, 4) x 50 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| swarm (trained) | 87.20 [82.26, 90.94] | 32.76 [23.19, 45.42] | 11.53 [9.43, 14.01] | 1.00 [1.00, 1.00] | -3.08 [-4.34, -2.12] |
| no drones | 33.22 [27.52, 39.37] | 170.96 [155.22, 185.56] | 37.90 [34.48, 41.36] | 1.00 [1.00, 1.00] | -16.90 [-18.36, -15.32] |
| random | 36.80 [30.75, 42.84] | 161.78 [146.32, 177.28] | 34.70 [31.42, 38.02] | 1.00 [1.00, 1.00] | -15.98 [-17.53, -14.43] |
| nearest-fire rule | 90.10 [87.39, 92.52] | 25.34 [19.16, 32.28] | 10.36 [8.84, 12.00] | 1.00 [1.00, 1.00] | -2.33 [-3.03, -1.72] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| no drones | 53.99 [47.57, 59.72], p=<0.001 | -138.20 [-152.88, -121.77], p=<0.001 | -26.37 [-29.30, -23.34], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | 13.82 [12.18, 15.29], p=<0.001 |
| random | 50.40 [43.69, 57.13], p=<0.001 | -129.02 [-146.24, -111.85], p=<0.001 | -23.17 [-26.34, -20.01], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | 12.90 [11.19, 14.62], p=<0.001 |
| nearest-fire rule | -2.90 [-7.13, 0.78], p=0.132 | 7.42 [-2.00, 18.25], p=0.132 | 1.17 [-0.79, 3.23], p=0.255 | 0.00 [0.00, 0.00], p=1.000 | -0.74 [-1.83, 0.20], p=0.132 |
