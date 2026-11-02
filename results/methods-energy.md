# Methods and ablations: energy

Battery swarm (10 batteries). Base: VDN, 1-step DQN, checkpoint chosen on validation.

Variants against **energy** (10 seeds): mean [95% CI] and difference from energy [95% CI], p-value.

| variant | seeds | std_reduction_pct | diff | peak_reduction_mw | diff |
| :-- | --: | --: | --: | --: | --: |
| energy | 10 | 10.79 [10.58, 11.03] | – | 704.26 [546.83, 857.30] | – |
| energy-qmix | 5 | 10.58 [10.42, 10.73] | -0.21 [-0.50, 0.05], p=0.132 | 829.66 [710.63, 948.68] | 125.40 [-73.33, 326.41], p=0.215 |
| energy-independent | 5 | 10.58 [10.12, 10.97] | -0.21 [-0.71, 0.22], p=0.389 | 248.49 [126.15, 309.66] | -455.77 [-655.70, -270.85], p=<0.001 |
| energy-3-step | 5 | 10.80 [10.60, 11.00] | 0.01 [-0.29, 0.31], p=0.928 | 313.60 [61.93, 631.14] | -390.66 [-697.06, -22.73], p=0.039 |
| energy-mappo | 5 | 8.87 [8.37, 9.48] | -1.92 [-2.46, -1.28], p=<0.001 | 351.55 [64.99, 674.53] | -352.71 [-674.27, 11.91], p=0.058 |
