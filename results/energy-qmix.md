# Multi-seed results

## energy-qmix

5 training seeds (0, 1, 2, 3, 4) x 1 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | par_after | peak_reduction_mw | std_reduction_pct | return |
| :-- | --: | --: | --: | --: |
| swarm (trained) | 1.51 [1.50, 1.52] | 829.66 [710.63, 948.68] | 10.58 [10.42, 10.73] | 1,369.15 [1,339.19, 1,396.15] |
| no battery | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| threshold rule | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 5.03 [5.03, 5.03] | 732.82 [732.82, 732.82] |
| proportional rule | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 9.06 [9.06, 9.06] | 1,235.93 [1,235.93, 1,235.93] |
| MPC (24 h forecast) | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 6.84 [6.84, 6.84] | 957.12 [957.12, 957.12] |
| optimum: min peak (perfect foresight) | 1.50 [1.50, 1.50] | 948.68 [948.68, 948.68] | -0.06 [-0.06, -0.06] | -4.98 [-4.98, -4.98] |
| optimum: flattest (perfect foresight) | 1.49 [1.49, 1.49] | 948.68 [948.68, 948.68] | 14.67 [14.67, 14.67] | 1,880.44 [1,880.44, 1,880.44] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | par_after | peak_reduction_mw | std_reduction_pct | return |
| :-- | --: | --: | --: | --: |
| no battery | -0.07 [-0.08, -0.06], p=<0.001 | 829.66 [710.63, 948.68], p=<0.001 | 10.58 [10.42, 10.73], p=<0.001 | 1,369.15 [1,339.19, 1,396.15], p=<0.001 |
| threshold rule | -0.07 [-0.08, -0.06], p=<0.001 | 829.66 [710.63, 948.68], p=<0.001 | 5.55 [5.40, 5.70], p=<0.001 | 636.32 [606.37, 663.33], p=<0.001 |
| proportional rule | -0.07 [-0.08, -0.06], p=<0.001 | 829.66 [710.63, 948.68], p=<0.001 | 1.53 [1.37, 1.67], p=<0.001 | 133.22 [103.27, 160.22], p=<0.001 |
| MPC (24 h forecast) | -0.07 [-0.08, -0.06], p=<0.001 | 829.66 [710.63, 948.68], p=<0.001 | 3.75 [3.59, 3.89], p=<0.001 | 412.03 [382.07, 439.03], p=<0.001 |
| optimum: min peak (perfect foresight) | 0.01 [-0.00, 0.02], p=0.159 | -119.03 [-238.05, 0.00], p=0.159 | 10.65 [10.49, 10.79], p=<0.001 | 1,374.12 [1,344.17, 1,401.13], p=<0.001 |
| optimum: flattest (perfect foresight) | 0.01 [0.00, 0.02], p=<0.001 | -119.03 [-238.05, 0.00], p=0.159 | -4.09 [-4.25, -3.94], p=<0.001 | -511.29 [-541.25, -484.29], p=<0.001 |
