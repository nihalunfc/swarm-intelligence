# Methods and ablations: wildfire

Drone swarm (6 drones, 16x16 forest). Base: independent DQN that first learns from the nearest-fire rule.

Variants against **wildfire-imitate** (5 seeds): mean [95% CI] and difference from wildfire-imitate [95% CI], p-value.

| variant | seeds | forest_saved_pct | diff | peak_fire_cells | diff |
| :-- | --: | --: | --: | --: | --: |
| wildfire | 3 | 79.20 [73.18, 84.78] | -8.01 [-13.47, -3.27], p=0.002 | 14.43 [11.77, 17.39] | 2.91 [0.92, 5.19], p=0.004 |
| wildfire-imitate | 5 | 87.20 [82.26, 90.94] | – | 11.53 [9.43, 14.01] | – |
| wildfire-imitate-qmix | 3 | 86.82 [82.80, 90.09] | -0.39 [-3.71, 3.47], p=0.803 | 11.47 [9.64, 13.53] | -0.05 [-1.67, 1.30], p=0.974 |
| wildfire-mappo | 3 | 72.11 [62.22, 80.97] | -15.09 [-24.58, -6.45], p=<0.001 | 16.86 [13.34, 20.44] | 5.33 [2.36, 8.52], p=<0.001 |
| wildfire-imitate-messages | 3 | 82.06 [77.56, 86.03] | -5.14 [-9.20, -0.96], p=0.020 | 13.26 [11.07, 15.62] | 1.73 [0.01, 3.45], p=0.049 |
