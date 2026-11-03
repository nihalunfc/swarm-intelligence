# Multi-seed results

## wildfire-targets

3 training seeds (0, 1, 2) x 50 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| swarm (trained) | 87.95 [83.63, 91.33] | 30.84 [22.20, 41.91] | 11.21 [9.17, 13.77] | 1.00 [1.00, 1.00] | -2.88 [-3.99, -2.02] |
| no drones | 33.58 [27.60, 39.65] | 170.04 [154.50, 185.34] | 38.42 [34.40, 42.92] | 1.00 [1.00, 1.00] | -16.80 [-18.33, -15.25] |
| nearest-fire rule | 88.85 [85.65, 91.57] | 28.54 [21.58, 36.74] | 10.12 [8.72, 11.58] | 1.00 [1.00, 1.00] | -2.65 [-3.47, -1.96] |
| spread rule | 91.22 [88.86, 93.23] | 22.48 [17.34, 28.52] | 9.50 [8.22, 10.88] | 1.00 [1.00, 1.00] | -2.05 [-2.65, -1.53] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| no drones | 54.38 [48.20, 60.24], p=<0.001 | -139.20 [-154.21, -123.40], p=<0.001 | -27.21 [-31.31, -23.49], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | 13.92 [12.34, 15.42], p=<0.001 |
| nearest-fire rule | -0.90 [-4.16, 1.97], p=0.582 | 2.30 [-5.04, 10.64], p=0.582 | 1.09 [-0.23, 2.95], p=0.130 | 0.00 [0.00, 0.00], p=1.000 | -0.23 [-1.06, 0.50], p=0.581 |
| spread rule | -3.27 [-6.36, -1.00], p=0.004 | 8.36 [2.57, 16.29], p=0.004 | 1.71 [0.59, 3.42], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | -0.84 [-1.63, -0.26], p=0.004 |
