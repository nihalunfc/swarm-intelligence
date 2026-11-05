# Multi-seed results

## wildfire-imitate-pads

3 training seeds (0, 1, 2) x 50 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| swarm (trained) | 87.18 [81.44, 91.26] | 32.83 [22.38, 47.50] | 11.59 [9.29, 14.48] | 1.00 [1.00, 1.00] | -3.08 [-4.55, -2.04] |
| no drones | 33.22 [27.52, 39.37] | 170.96 [155.22, 185.56] | 37.90 [34.48, 41.36] | 1.00 [1.00, 1.00] | -16.90 [-18.36, -15.32] |
| random | 36.80 [30.75, 42.84] | 161.78 [146.32, 177.28] | 34.70 [31.42, 38.02] | 1.00 [1.00, 1.00] | -15.98 [-17.53, -14.43] |
| nearest-fire rule | 90.10 [87.39, 92.52] | 25.34 [19.16, 32.28] | 10.36 [8.84, 12.00] | 1.00 [1.00, 1.00] | -2.33 [-3.03, -1.72] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | forest_saved_pct | burned_cells | peak_fire_cells | contained | return |
| :-- | --: | --: | --: | --: | --: |
| no drones | 53.96 [46.96, 60.23], p=<0.001 | -138.13 [-154.18, -120.21], p=<0.001 | -26.31 [-29.40, -23.15], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | 13.81 [12.02, 15.42], p=<0.001 |
| random | 50.37 [43.12, 57.13], p=<0.001 | -128.95 [-146.25, -110.40], p=<0.001 | -23.11 [-26.47, -19.68], p=<0.001 | 0.00 [0.00, 0.00], p=1.000 | 12.90 [11.04, 14.62], p=<0.001 |
| nearest-fire rule | -2.92 [-7.95, 1.55], p=0.190 | 7.49 [-3.96, 20.35], p=0.190 | 1.23 [-1.05, 3.72], p=0.302 | 0.00 [0.00, 0.00], p=1.000 | -0.75 [-2.03, 0.40], p=0.190 |
