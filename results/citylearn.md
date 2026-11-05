# Multi-seed results

## citylearn

3 training seeds (0, 1, 2) x 1 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | score | cost_total | carbon_emissions_total | ramping_average | daily_peak_average | one_minus_load_factor |
| :-- | --: | --: | --: | --: | --: | --: |
| swarm (trained) | 0.96 [0.95, 0.97] | 0.92 [0.91, 0.93] | 0.96 [0.95, 0.97] | 1.06 [1.04, 1.09] | 0.85 [0.83, 0.86] | 0.93 [0.93, 0.94] |
| no battery | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| CityLearn BasicRBC | 1.13 [1.13, 1.13] | 1.11 [1.11, 1.11] | 1.17 [1.17, 1.17] | 1.22 [1.22, 1.22] | 1.12 [1.12, 1.12] | 0.98 [0.98, 0.98] |
| CityLearn OptimizedRBC | 1.03 [1.03, 1.03] | 1.03 [1.03, 1.03] | 1.06 [1.06, 1.06] | 1.04 [1.04, 1.04] | 0.95 [0.95, 0.95] | 0.97 [0.97, 0.97] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | score | cost_total | carbon_emissions_total | ramping_average | daily_peak_average | one_minus_load_factor |
| :-- | --: | --: | --: | --: | --: | --: |
| no battery | -0.04 [-0.05, -0.03], p=<0.001 | -0.08 [-0.09, -0.07], p=<0.001 | -0.04 [-0.05, -0.03], p=<0.001 | 0.06 [0.04, 0.09], p=<0.001 | -0.15 [-0.17, -0.14], p=<0.001 | -0.07 [-0.07, -0.06], p=<0.001 |
| CityLearn BasicRBC | -0.17 [-0.18, -0.16], p=<0.001 | -0.19 [-0.20, -0.18], p=<0.001 | -0.21 [-0.22, -0.20], p=<0.001 | -0.16 [-0.18, -0.13], p=<0.001 | -0.27 [-0.29, -0.26], p=<0.001 | -0.05 [-0.05, -0.04], p=<0.001 |
| CityLearn OptimizedRBC | -0.08 [-0.09, -0.06], p=<0.001 | -0.12 [-0.12, -0.10], p=<0.001 | -0.10 [-0.12, -0.10], p=<0.001 | 0.02 [0.00, 0.05], p=<0.001 | -0.10 [-0.12, -0.09], p=<0.001 | -0.03 [-0.04, -0.03], p=<0.001 |
