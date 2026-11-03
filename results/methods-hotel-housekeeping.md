# Methods and ablations: hotel-housekeeping

Housekeeping swarm (8 attendants). Base: VDN DQN. Residual = soonest-needed rule plus learned overrides.

Variants against **hotel-housekeeping** (5 seeds): mean [95% CI] and difference from hotel-housekeeping [95% CI], p-value.

| variant | seeds | guest_wait_hours | diff | early_promises_kept_pct | diff |
| :-- | --: | --: | --: | --: | --: |
| hotel-housekeeping | 5 | 22.38 [19.40, 25.43] | – | 47.42 [43.57, 51.24] | – |
| hotel-housekeeping-residual | 5 | 21.54 [18.74, 24.37] | -0.84 [-1.41, -0.38], p=<0.001 | 48.22 [44.24, 52.09] | 0.80 [0.11, 1.57], p=0.028 |
| hotel-housekeeping-mappo | 5 | 21.61 [18.80, 24.51] | -0.76 [-1.33, -0.33], p=<0.001 | 47.59 [43.67, 51.46] | 0.16 [-0.85, 1.16], p=0.726 |
| hotel-housekeeping-independent | 5 | 21.85 [18.94, 24.81] | -0.53 [-1.07, -0.09], p=0.023 | 47.74 [43.74, 51.64] | 0.31 [-0.58, 1.19], p=0.468 |
| hotel-housekeeping-qmix | 5 | 22.32 [19.44, 25.30] | -0.05 [-0.67, 0.51], p=0.884 | 46.59 [42.76, 50.34] | -0.83 [-1.85, 0.16], p=0.093 |
