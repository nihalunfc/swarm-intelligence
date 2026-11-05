# Multi-seed results

## hotel-housekeeping-residual

5 training seeds (0, 1, 2, 3, 4) x 50 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | guest_wait_hours | early_promises_kept_pct | ready_by_noon_pct | workload_spread | floor_changes |
| :-- | --: | --: | --: | --: | --: |
| swarm (trained) | 21.54 [18.74, 24.37] | 48.22 [44.24, 52.09] | 40.31 [39.29, 41.32] | 0.68 [0.62, 0.73] | 77.38 [75.78, 78.98] |
| floor order | 111.30 [98.61, 123.60] | 25.18 [21.78, 28.63] | 45.83 [44.75, 46.88] | 3.09 [2.90, 3.29] | 4.70 [4.36, 5.06] |
| soonest needed | 21.54 [18.72, 24.33] | 48.22 [44.23, 52.03] | 40.31 [39.29, 41.32] | 0.68 [0.62, 0.73] | 77.38 [75.80, 78.98] |
| random room | 29.76 [26.34, 33.15] | 42.07 [38.14, 45.87] | 39.21 [38.23, 40.18] | 0.64 [0.59, 0.69] | 87.34 [85.70, 89.02] |
| lower bound (perfect foresight, no elevator time) | 18.07 [15.59, 20.59] | – | – | – | – |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | guest_wait_hours | early_promises_kept_pct | ready_by_noon_pct | workload_spread | floor_changes |
| :-- | --: | --: | --: | --: | --: |
| floor order | -89.76 [-101.24, -78.33], p=<0.001 | 23.05 [19.66, 26.54], p=<0.001 | -5.52 [-6.03, -5.02], p=<0.001 | -2.42 [-2.62, -2.22], p=<0.001 | 72.68 [71.04, 74.28], p=<0.001 |
| soonest needed | 0.00 [0.00, 0.00], p=1.000 | 0.00 [0.00, 0.00], p=1.000 | 0.00 [0.00, 0.00], p=1.000 | 0.00 [0.00, 0.00], p=1.000 | 0.00 [0.00, 0.00], p=1.000 |
| random room | -8.22 [-9.23, -7.24], p=<0.001 | 6.15 [4.38, 7.99], p=<0.001 | 1.10 [0.72, 1.47], p=<0.001 | 0.03 [-0.02, 0.10], p=0.236 | -9.96 [-11.26, -8.72], p=<0.001 |
| lower bound (perfect foresight, no elevator time) | 3.47 [3.01, 3.97], p=<0.001 | – | – | – | – |
