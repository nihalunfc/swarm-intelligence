# Multi-seed results

## wildfire-scale

3 training seeds (0, 1, 2) x 30 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| swarm (trained) | 64.08 [53.43, 73.72] | 367.79 [269.12, 476.83] | 58.32 [46.07, 71.60] | 1.00 [1.00, 1.00] | -35.98 [-46.88, -26.11] |
| no drones | 21.31 [15.87, 27.06] | 805.77 [746.87, 861.50] | 117.40 [106.73, 128.30] | 1.00 [1.00, 1.00] | -79.78 [-85.35, -73.89] |
| random | 30.35 [23.73, 37.08] | 713.17 [644.30, 781.00] | 105.50 [93.93, 117.17] | 1.00 [1.00, 1.00] | -70.52 [-77.30, -63.63] |
| nearest-fire rule | 89.01 [85.65, 92.10] | 112.53 [80.93, 146.90] | 32.80 [26.97, 39.23] | 1.00 [1.00, 1.00] | -10.45 [-13.89, -7.29] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| no drones | 42.77 [33.86, 50.82], p=<0.001 | -437.98 [-520.40, -346.77], p=<0.001 | -59.08 [-65.92, -52.13], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | 43.80 [34.68, 52.04], p=<0.001 |
| random | 33.73 [26.36, 40.46], p=<0.001 | -345.38 [-414.27, -269.92], p=<0.001 | -47.18 [-54.43, -40.04], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | 34.54 [26.99, 41.43], p=<0.001 |
| nearest-fire rule | -24.93 [-33.64, -17.24], p=<0.001 | 255.26 [176.52, 344.43], p=<0.001 | 25.52 [16.51, 35.41], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | -25.53 [-34.44, -17.65], p=<0.001 |
