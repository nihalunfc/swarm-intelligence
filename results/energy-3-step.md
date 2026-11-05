# Multi-seed results

## energy-3-step

5 training seeds (0, 1, 2, 3, 4) x 1 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | par_after | peak_reduction_mw | std_reduction_pct | return |
| :-- | --: | --: | --: | --: |
| swarm (trained) | 1.55 [1.52, 1.57] | 313.60 [61.93, 631.14] | 10.80 [10.60, 11.00] | 1,391.91 [1,370.55, 1,418.37] |
| no battery | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| threshold rule | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 5.03 [5.03, 5.03] | 732.82 [732.82, 732.82] |
| proportional rule | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 9.06 [9.06, 9.06] | 1,235.93 [1,235.93, 1,235.93] |
| MPC (24 h forecast) | 1.58 [1.58, 1.58] | 0.00 [0.00, 0.00] | 6.84 [6.84, 6.84] | 957.12 [957.12, 957.12] |
| optimum: min peak (perfect foresight) | 1.50 [1.50, 1.50] | 948.68 [948.68, 948.68] | -0.06 [-0.06, -0.06] | -4.98 [-4.98, -4.98] |
| optimum: flattest (perfect foresight) | 1.49 [1.49, 1.49] | 948.68 [948.68, 948.68] | 14.67 [14.67, 14.67] | 1,880.44 [1,880.44, 1,880.44] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | par_after | peak_reduction_mw | std_reduction_pct | return |
| :-- | --: | --: | --: | --: |
| no battery | -0.03 [-0.06, -0.01], p=<0.001 | 313.60 [61.93, 631.14], p=0.017 | 10.80 [10.60, 11.00], p=<0.001 | 1,391.91 [1,370.55, 1,418.37], p=<0.001 |
| threshold rule | -0.03 [-0.05, -0.01], p=0.017 | 313.60 [61.93, 631.14], p=0.017 | 5.77 [5.58, 5.97], p=<0.001 | 659.09 [637.73, 685.55], p=<0.001 |
| proportional rule | -0.03 [-0.05, -0.01], p=0.011 | 313.60 [61.93, 631.14], p=0.017 | 1.74 [1.55, 1.94], p=<0.001 | 155.98 [134.62, 182.44], p=<0.001 |
| MPC (24 h forecast) | -0.03 [-0.05, -0.01], p=<0.001 | 313.60 [61.93, 631.14], p=0.017 | 3.97 [3.77, 4.16], p=<0.001 | 434.79 [413.43, 461.25], p=<0.001 |
| optimum: min peak (perfect foresight) | 0.05 [0.02, 0.07], p=<0.001 | -635.08 [-886.75, -317.54], p=<0.001 | 10.86 [10.67, 11.06], p=<0.001 | 1,396.89 [1,375.52, 1,423.35], p=<0.001 |
| optimum: flattest (perfect foresight) | 0.06 [0.03, 0.08], p=<0.001 | -635.08 [-886.75, -317.54], p=<0.001 | -3.87 [-4.07, -3.67], p=<0.001 | -488.53 [-509.89, -462.07], p=<0.001 |
