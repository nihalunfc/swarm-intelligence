# Local interactions and their group-level consequences in flocking jackdaws

Species: jackdaw (Corvus monedula), wild. Source: [Ling et al. 2019, Proc. R. Soc. B, doi:10.5061/dryad.kb8js06](https://datadryad.org/stash/dataset/doi:10.5061/dryad.kb8js06), license CC0-1.0. Real recorded data, no simulation. BL = body length, taken as 0.34 m (approximate).

## 1. Motion summary

| Recording | Track ids | Seconds | Median speed (m/s) | Median nearest neighbour (m) | Polarisation | Milling |
| --- | --- | --- | --- | --- | --- | --- |
| jackdaw_flock_01 | 494 | 13 | 13.4 | 1.42 | 0.98 | 0.14 |
| jackdaw_flock_02 | 361 | 16 | 13.0 | 1.71 | 0.99 | 0.10 |
| jackdaw_flock_03 | 383 | 16 | 13.0 | 1.72 | 0.99 | 0.10 |
| jackdaw_flock_04 | 148 | 27 | 10.1 | 2.28 | 0.94 | 0.13 |
| jackdaw_flock_05 | 218 | 20 | 8.5 | 1.96 | 0.93 | 0.18 |
| jackdaw_flock_06 | 56 | 10 | 11.1 | 1.73 | 0.99 | 0.12 |

## 2. Who each bird listens to, and preferred spacing

Held-out R^2 for predicting each bird's turn over the next 0.3 s. 'no signal' means neither rule explains even 1% of turns.

| Recording | Best k | R^2 | Best radius (BL) | R^2 | Better rule | Repulsion-to-attraction switch (BL) |
| --- | --- | --- | --- | --- | --- | --- |
| jackdaw_flock_01 | 12 | -0.002 | 4 | 0.011 | metric | 2.96 |
| jackdaw_flock_02 | 12 | 0.028 | 3 | 0.025 | topological | 2.71 |
| jackdaw_flock_03 | 8 | 0.037 | 3 | 0.026 | topological | 2.69 |
| jackdaw_flock_04 | 3 | 0.008 | 4 | 0.043 | metric | 2.59 |
| jackdaw_flock_05 | 4 | 0.027 | 8 | 0.050 | metric | 3.01 |
| jackdaw_flock_06 | 10 | 0.073 | 6 | 0.080 | metric | 2.67 |
