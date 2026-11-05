# Multi-seed results

## vmas-navigation-mappo

3 training seeds (0, 1, 2) x 50 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | success | return | collisions |
| :-- | --: | --: | --: |
| swarm (trained) | 0.93 [0.83, 1.00] | 12.54 [11.40, 13.64] | 2.69 [1.59, 3.95] |
| no-op | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| random | 0.00 [0.00, 0.00] | -4.48 [-6.52, -2.68] | 3.52 [1.92, 5.40] |
| go to goal | 0.98 [0.94, 1.00] | -0.83 [-10.53, 7.20] | 16.04 [8.00, 25.64] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | success | return | collisions |
| :-- | --: | --: | --: |
| no-op | 0.93 [0.83, 1.00], p=<0.001 | 12.54 [11.40, 13.64], p=<0.001 | 2.69 [1.59, 3.95], p=<0.001 |
| random | 0.93 [0.83, 1.00], p=<0.001 | 17.02 [15.06, 19.12], p=<0.001 | -0.83 [-2.76, 0.89], p=0.378 |
| go to goal | -0.05 [-0.16, 0.04], p=0.407 | 13.37 [5.30, 23.13], p=<0.001 | -13.35 [-22.85, -5.53], p=<0.001 |
