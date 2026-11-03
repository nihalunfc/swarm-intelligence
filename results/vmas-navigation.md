# Multi-seed results

## vmas-navigation

3 training seeds (0, 1, 2) x 50 test episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; rules have no training seed, so their interval covers episodes only).

| policy | success | return | collisions |
| :-- | --: | --: | --: |
| swarm (trained) | 0.91 [0.83, 0.98] | 15.27 [14.30, 16.22] | 0.07 [0.00, 0.24] |
| no-op | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| random | 0.00 [0.00, 0.00] | -4.48 [-6.52, -2.68] | 3.52 [1.92, 5.40] |
| go to goal | 0.98 [0.94, 1.00] | -0.83 [-10.53, 7.20] | 16.04 [8.00, 25.64] |

**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds and episodes):

| vs rule | success | return | collisions |
| :-- | --: | --: | --: |
| no-op | 0.91 [0.83, 0.98], p=<0.001 | 15.27 [14.30, 16.22], p=<0.001 | 0.07 [0.00, 0.24], p=0.480 |
| random | 0.91 [0.83, 0.98], p=<0.001 | 19.75 [17.55, 22.13], p=<0.001 | -3.45 [-5.33, -1.84], p=<0.001 |
| go to goal | -0.07 [-0.16, 0.02], p=0.145 | 16.10 [7.97, 26.01], p=<0.001 | -15.97 [-25.69, -8.01], p=<0.001 |
