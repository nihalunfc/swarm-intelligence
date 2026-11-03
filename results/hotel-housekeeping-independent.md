# Multi-seed results

## hotel-housekeeping-independent

5 training seeds (0, 1, 2, 3, 4) x 50 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | guest_wait_hours | early_promises_kept_pct | ready_by_noon_pct | workload_spread | floor_changes |
| :-- | --: | --: | --: | --: | --: |
| swarm (trained) | 21.85 [18.94, 24.81] | 47.74 [43.74, 51.64] | 39.03 [37.98, 40.10] | 0.79 [0.73, 0.86] | 79.06 [77.09, 81.07] |
| floor order | 111.30 [98.61, 123.60] | 25.18 [21.78, 28.63] | 45.83 [44.75, 46.88] | 3.09 [2.90, 3.29] | 4.70 [4.36, 5.06] |
| soonest needed | 21.54 [18.72, 24.33] | 48.22 [44.23, 52.03] | 40.31 [39.29, 41.32] | 0.68 [0.62, 0.73] | 77.38 [75.80, 78.98] |
| random room | 29.76 [26.34, 33.15] | 42.07 [38.14, 45.87] | 39.21 [38.23, 40.18] | 0.64 [0.59, 0.69] | 87.34 [85.70, 89.02] |
| lower bound (perfect foresight, no elevator time) | 18.07 [15.59, 20.59] | – | – | – | – |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | guest_wait_hours | early_promises_kept_pct | ready_by_noon_pct | workload_spread | floor_changes |
| :-- | --: | --: | --: | --: | --: |
| floor order | -89.46 [-100.89, -78.09], p=<0.001 | 22.56 [19.18, 26.09], p=<0.001 | -6.80 [-7.55, -6.11], p=<0.001 | -2.31 [-2.51, -2.12], p=<0.001 | 74.36 [72.31, 76.40], p=<0.001 |
| soonest needed | 0.31 [0.07, 0.64], p=0.006 | -0.49 [-1.27, 0.18], p=0.175 | -1.28 [-1.84, -0.79], p=<0.001 | 0.11 [0.04, 0.19], p=0.002 | 1.68 [0.16, 3.28], p=0.033 |
| random room | -7.92 [-8.93, -6.94], p=<0.001 | 5.67 [3.90, 7.44], p=<0.001 | -0.18 [-0.76, 0.40], p=0.547 | 0.14 [0.08, 0.22], p=<0.001 | -8.28 [-9.95, -6.55], p=<0.001 |
| lower bound (perfect foresight, no elevator time) | 3.78 [3.23, 4.43], p=<0.001 | – | – | – | – |
