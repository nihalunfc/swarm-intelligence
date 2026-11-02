# Multi-seed results

## hotel-housekeeping-mappo

5 training seeds (0, 1, 2, 3, 4) x 50 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | guest_wait_hours | early_promises_kept_pct | ready_by_noon_pct | workload_spread | floor_changes |
| :-- | --: | --: | --: | --: | --: |
| swarm (trained) | 21.61 [18.80, 24.51] | 47.59 [43.67, 51.46] | 38.79 [37.32, 40.26] | 0.64 [0.57, 0.72] | 77.25 [75.38, 79.02] |
| floor order | 111.30 [98.61, 123.60] | 25.18 [21.78, 28.63] | 45.83 [44.75, 46.88] | 3.09 [2.90, 3.29] | 4.70 [4.36, 5.06] |
| soonest needed | 21.54 [18.72, 24.33] | 48.22 [44.23, 52.03] | 40.31 [39.29, 41.32] | 0.68 [0.62, 0.73] | 77.38 [75.80, 78.98] |
| random room | 29.76 [26.34, 33.15] | 42.07 [38.14, 45.87] | 39.21 [38.23, 40.18] | 0.64 [0.59, 0.69] | 87.34 [85.70, 89.02] |
| lower bound (perfect foresight, no elevator time) | 18.07 [15.59, 20.59] | – | – | – | – |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | guest_wait_hours | early_promises_kept_pct | ready_by_noon_pct | workload_spread | floor_changes |
| :-- | --: | --: | --: | --: | --: |
| floor order | -89.69 [-101.09, -78.31], p=<0.001 | 22.41 [18.91, 25.93], p=<0.001 | -7.04 [-8.36, -5.79], p=<0.001 | -2.45 [-2.65, -2.25], p=<0.001 | 72.55 [70.67, 74.33], p=<0.001 |
| soonest needed | 0.07 [-0.10, 0.28], p=0.434 | -0.64 [-1.51, 0.02], p=0.066 | -1.52 [-2.78, -0.34], p=0.003 | -0.03 [-0.11, 0.04], p=0.395 | -0.13 [-1.40, 1.02], p=0.858 |
| random room | -8.15 [-9.19, -7.15], p=<0.001 | 5.52 [3.63, 7.40], p=<0.001 | -0.42 [-1.68, 0.80], p=0.522 | 0.00 [-0.09, 0.09], p=0.919 | -10.09 [-11.77, -8.53], p=<0.001 |
| lower bound (perfect foresight, no elevator time) | 3.54 [3.09, 4.07], p=<0.001 | – | – | – | – |
