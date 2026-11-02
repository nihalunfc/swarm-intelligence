# Multi-seed results

## energy-mappo

5 training seeds (0, 1, 2, 3, 4) x 1 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | par_after | peak_reduction_mw | std_reduction_pct | return |
| :-- | --: | --: | --: | --: |
| swarm (trained) | 1.55 [1.52, 1.57] | 351.55 [64.99, 674.53] | 8.87 [8.37, 9.48] | 1,156.21 [1,092.69, 1,224.29] |
| no battery | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| threshold rule | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 5.03 [5.03, 5.03] | 732.82 [732.82, 732.82] |
| proportional rule | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 9.06 [9.06, 9.06] | 1,235.93 [1,235.93, 1,235.93] |
| MPC (24 h forecast) | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 6.84 [6.84, 6.84] | 957.12 [957.12, 957.12] |
| optimum: min peak (perfect foresight) | 1.50 [1.50, 1.50] | 948.68 [948.68, 948.68] | -0.06 [-0.06, -0.06] | -4.98 [-4.98, -4.98] |
| optimum: flattest (perfect foresight) | 1.49 [1.49, 1.49] | 948.68 [948.68, 948.68] | 14.67 [14.67, 14.67] | 1,880.44 [1,880.44, 1,880.44] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | par_after | peak_reduction_mw | std_reduction_pct | return |
| :-- | --: | --: | --: | --: |
| no battery | -0.03 [-0.06, -0.01], p=<0.001 | 351.55 [64.99, 674.53], p=<0.001 | 8.87 [8.37, 9.48], p=<0.001 | 1,156.21 [1,092.69, 1,224.29], p=<0.001 |
| threshold rule | -0.03 [-0.06, -0.01], p=<0.001 | 351.55 [64.99, 674.53], p=<0.001 | 3.84 [3.35, 4.45], p=<0.001 | 423.39 [359.87, 491.46], p=<0.001 |
| proportional rule | -0.03 [-0.06, -0.01], p=<0.001 | 351.55 [64.99, 674.53], p=<0.001 | -0.19 [-0.68, 0.42], p=0.478 | -79.72 [-143.24, -11.64], p=0.023 |
| MPC (24 h forecast) | -0.03 [-0.06, -0.01], p=<0.001 | 351.55 [64.99, 674.53], p=<0.001 | 2.03 [1.54, 2.64], p=<0.001 | 199.09 [135.57, 267.17], p=<0.001 |
| optimum: min peak (perfect foresight) | 0.05 [0.02, 0.07], p=<0.001 | -597.14 [-883.70, -274.15], p=<0.001 | 8.93 [8.44, 9.54], p=<0.001 | 1,161.19 [1,097.66, 1,229.26], p=<0.001 |
| optimum: flattest (perfect foresight) | 0.05 [0.03, 0.08], p=<0.001 | -597.14 [-883.70, -274.15], p=<0.001 | -5.80 [-6.30, -5.19], p=<0.001 | -724.23 [-787.75, -656.15], p=<0.001 |
