# Multi-seed results

## hotel-housekeeping

5 training seeds (0, 1, 2, 3, 4) x 50 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | guest_wait_hours | early_promises_kept_pct | ready_by_noon_pct | workload_spread | floor_changes |
| :-- | --: | --: | --: | --: | --: |
| swarm (trained) | 22.38 [19.40, 25.43] | 47.42 [43.57, 51.24] | 38.47 [36.86, 40.02] | 0.81 [0.74, 0.88] | 79.70 [77.98, 81.45] |
| floor order | 111.30 [98.61, 123.60] | 25.18 [21.78, 28.63] | 45.83 [44.75, 46.88] | 3.09 [2.90, 3.29] | 4.70 [4.36, 5.06] |
| soonest needed | 21.54 [18.72, 24.33] | 48.22 [44.23, 52.03] | 40.31 [39.29, 41.32] | 0.68 [0.62, 0.73] | 77.38 [75.80, 78.98] |
| random room | 29.76 [26.34, 33.15] | 42.07 [38.14, 45.87] | 39.21 [38.23, 40.18] | 0.64 [0.59, 0.69] | 87.34 [85.70, 89.02] |
| lower bound (perfect foresight, no elevator time) | 18.07 [15.59, 20.59] | – | – | – | – |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | guest_wait_hours | early_promises_kept_pct | ready_by_noon_pct | workload_spread | floor_changes |
| :-- | --: | --: | --: | --: | --: |
| floor order | -88.92 [-100.25, -77.72], p=<0.001 | 22.25 [18.96, 25.67], p=<0.001 | -7.36 [-8.84, -6.00], p=<0.001 | -2.29 [-2.49, -2.09], p=<0.001 | 75.00 [73.24, 76.80], p=<0.001 |
| soonest needed | 0.84 [0.39, 1.40], p=<0.001 | -0.80 [-1.57, -0.10], p=0.027 | -1.84 [-3.24, -0.57], p=<0.001 | 0.13 [0.06, 0.21], p=<0.001 | 2.32 [0.90, 3.87], p=0.003 |
| random room | -7.38 [-8.44, -6.32], p=<0.001 | 5.35 [3.59, 7.27], p=<0.001 | -0.74 [-2.15, 0.54], p=0.251 | 0.17 [0.09, 0.25], p=<0.001 | -7.64 [-9.03, -6.12], p=<0.001 |
| lower bound (perfect foresight, no elevator time) | 4.31 [3.63, 5.13], p=<0.001 | – | – | – | – |
