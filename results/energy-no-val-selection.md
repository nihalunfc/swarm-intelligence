# Multi-seed results

## energy-no-val-selection

5 training seeds (0, 1, 2, 3, 4) x 1 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | par_after | peak_reduction_mw | std_reduction_pct | return |
| :-- | --: | --: | --: | --: |
| swarm (trained) | 1.54 [1.51, 1.55] | 482.92 [318.70, 729.49] | 11.02 [10.65, 11.38] | 1,406.16 [1,362.69, 1,452.20] |
| no battery | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| threshold rule | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 5.03 [5.03, 5.03] | 732.82 [732.82, 732.82] |
| proportional rule | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 9.06 [9.06, 9.06] | 1,235.93 [1,235.93, 1,235.93] |
| MPC (24 h forecast) | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 6.84 [6.84, 6.84] | 957.12 [957.12, 957.12] |
| optimum: min peak (perfect foresight) | 1.50 [1.50, 1.50] | 948.68 [948.68, 948.68] | -0.06 [-0.06, -0.06] | -4.98 [-4.98, -4.98] |
| optimum: flattest (perfect foresight) | 1.49 [1.49, 1.49] | 948.68 [948.68, 948.68] | 14.67 [14.67, 14.67] | 1,880.44 [1,880.44, 1,880.44] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | par_after | peak_reduction_mw | std_reduction_pct | return |
| :-- | --: | --: | --: | --: |
| no battery | -0.04 [-0.06, -0.03], p=<0.001 | 482.92 [318.70, 729.49], p=<0.001 | 11.02 [10.65, 11.38], p=<0.001 | 1,406.16 [1,362.69, 1,452.20], p=<0.001 |
| threshold rule | -0.04 [-0.06, -0.03], p=<0.001 | 482.92 [318.70, 729.49], p=<0.001 | 5.99 [5.62, 6.35], p=<0.001 | 673.34 [629.87, 719.37], p=<0.001 |
| proportional rule | -0.04 [-0.06, -0.03], p=<0.001 | 482.92 [318.70, 729.49], p=<0.001 | 1.96 [1.59, 2.32], p=<0.001 | 170.23 [126.77, 216.27], p=<0.001 |
| MPC (24 h forecast) | -0.04 [-0.06, -0.03], p=<0.001 | 482.92 [318.70, 729.49], p=<0.001 | 4.18 [3.81, 4.54], p=<0.001 | 449.04 [405.58, 495.08], p=<0.001 |
| optimum: min peak (perfect foresight) | 0.04 [0.02, 0.05], p=<0.001 | -465.76 [-629.99, -219.19], p=<0.001 | 11.08 [10.71, 11.44], p=<0.001 | 1,411.13 [1,367.67, 1,457.17], p=<0.001 |
| optimum: flattest (perfect foresight) | 0.04 [0.02, 0.06], p=<0.001 | -465.76 [-629.99, -219.19], p=<0.001 | -3.65 [-4.02, -3.30], p=<0.001 | -474.28 [-517.75, -428.24], p=<0.001 |
