# Multi-seed results

## energy-independent

5 training seeds (0, 1, 2, 3, 4) x 1 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | par_after | peak_reduction_mw | std_reduction_pct | return |
| :-- | --: | --: | --: | --: |
| swarm (trained) | 1.56 [1.55, 1.57] | 248.49 [126.15, 309.66] | 10.58 [10.12, 10.97] | 1,370.64 [1,329.44, 1,406.60] |
| no battery | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| threshold rule | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 5.03 [5.03, 5.03] | 732.82 [732.82, 732.82] |
| proportional rule | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 9.06 [9.06, 9.06] | 1,235.93 [1,235.93, 1,235.93] |
| MPC (24 h forecast) | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 6.84 [6.84, 6.84] | 957.12 [957.12, 957.12] |
| optimum: min peak (perfect foresight) | 1.50 [1.50, 1.50] | 948.68 [948.68, 948.68] | -0.06 [-0.06, -0.06] | -4.98 [-4.98, -4.98] |
| optimum: flattest (perfect foresight) | 1.49 [1.49, 1.49] | 948.68 [948.68, 948.68] | 14.67 [14.67, 14.67] | 1,880.44 [1,880.44, 1,880.44] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | par_after | peak_reduction_mw | std_reduction_pct | return |
| :-- | --: | --: | --: | --: |
| no battery | -0.02 [-0.03, -0.01], p=<0.001 | 248.49 [126.15, 309.66], p=<0.001 | 10.58 [10.12, 10.97], p=<0.001 | 1,370.64 [1,329.44, 1,406.60], p=<0.001 |
| threshold rule | -0.02 [-0.03, -0.01], p=<0.001 | 248.49 [126.15, 309.66], p=<0.001 | 5.55 [5.09, 5.95], p=<0.001 | 637.81 [596.61, 673.78], p=<0.001 |
| proportional rule | -0.02 [-0.03, -0.01], p=<0.001 | 248.49 [126.15, 309.66], p=<0.001 | 1.52 [1.06, 1.92], p=<0.001 | 134.71 [93.51, 170.67], p=<0.001 |
| MPC (24 h forecast) | -0.02 [-0.03, -0.01], p=<0.001 | 248.49 [126.15, 309.66], p=<0.001 | 3.75 [3.29, 4.14], p=<0.001 | 413.52 [372.32, 449.48], p=<0.001 |
| optimum: min peak (perfect foresight) | 0.06 [0.05, 0.07], p=<0.001 | -700.19 [-822.53, -639.03], p=<0.001 | 10.64 [10.18, 11.04], p=<0.001 | 1,375.61 [1,334.41, 1,411.58], p=<0.001 |
| optimum: flattest (perfect foresight) | 0.06 [0.06, 0.07], p=<0.001 | -700.19 [-822.53, -639.03], p=<0.001 | -4.09 [-4.55, -3.70], p=<0.001 | -509.80 [-551.00, -473.84], p=<0.001 |
