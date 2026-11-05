# Multi-seed results

## hotel-housekeeping-qmix

5 training seeds (0, 1, 2, 3, 4) x 50 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | guest_wait_hours | early_promises_kept_pct | ready_by_noon_pct | workload_spread | floor_changes |
| :-- | --: | --: | --: | --: | --: |
| swarm (trained) | 22.32 [19.44, 25.30] | 46.59 [42.76, 50.34] | 39.00 [38.07, 39.92] | 0.77 [0.70, 0.85] | 79.80 [76.08, 83.09] |
| floor order | 111.30 [98.61, 123.60] | 25.18 [21.78, 28.63] | 45.83 [44.75, 46.88] | 3.09 [2.90, 3.29] | 4.70 [4.36, 5.06] |
| soonest needed | 21.54 [18.72, 24.33] | 48.22 [44.23, 52.03] | 40.31 [39.29, 41.32] | 0.68 [0.62, 0.73] | 77.38 [75.80, 78.98] |
| random room | 29.76 [26.34, 33.15] | 42.07 [38.14, 45.87] | 39.21 [38.23, 40.18] | 0.64 [0.59, 0.69] | 87.34 [85.70, 89.02] |
| lower bound (perfect foresight, no elevator time) | 18.07 [15.59, 20.59] | – | – | – | – |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | guest_wait_hours | early_promises_kept_pct | ready_by_noon_pct | workload_spread | floor_changes |
| :-- | --: | --: | --: | --: | --: |
| floor order | -88.98 [-100.34, -77.60], p=<0.001 | 21.42 [18.11, 24.82], p=<0.001 | -6.83 [-7.45, -6.22], p=<0.001 | -2.32 [-2.51, -2.13], p=<0.001 | 75.10 [71.35, 78.38], p=<0.001 |
| soonest needed | 0.78 [0.38, 1.29], p=<0.001 | -1.63 [-2.60, -0.79], p=<0.001 | -1.31 [-1.75, -0.92], p=<0.001 | 0.10 [0.02, 0.19], p=0.014 | 2.42 [-1.24, 5.58], p=0.191 |
| random room | -7.44 [-8.50, -6.41], p=<0.001 | 4.52 [2.81, 6.23], p=<0.001 | -0.21 [-0.69, 0.18], p=0.331 | 0.13 [0.05, 0.22], p=<0.001 | -7.54 [-11.15, -4.37], p=<0.001 |
| lower bound (perfect foresight, no elevator time) | 4.25 [3.64, 5.04], p=<0.001 | – | – | – | – |
