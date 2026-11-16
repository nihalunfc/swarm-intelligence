# Selective social interactions and speed-induced leadership in schooling fish

Species: black neon tetra (Hyphessobrycon herbertaxelrodi). Source: [Puy et al. 2024, PNAS, doi:10.1073/pnas.2309733121](https://zenodo.org/records/10890112), license CC-BY-4.0. Real recorded data, no simulation.

## 1. Motion summary

Speed and spacing use smoothed tracks (0.2 s Savitzky-Golay). BL = body length.

| Recording | Animals | Minutes | Median speed (cm/s) | Mean speed (BL/s) | Median nearest neighbour (cm) | Polarisation | Time polarised >0.8 | Time milling >0.5 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Experimental_school_N=39_recording_0 | 39 | 60 | 12.0 | 5.7 | 4.1 | 0.87 | 79% | 1.2% |
| Experimental_school_N=39_recording_1 | 39 | 60 | 11.3 | 5.3 | 4.9 | 0.81 | 67% | 2.6% |
| Experimental_school_N=8_recording_0 | 8 | 28 | 15.6 | 6.6 | 3.3 | 0.95 | 94% | 0.4% |

Published check: the paper's model uses a preferred speed of 11.0 cm/s (set from the data) and an equilibrium spacing of 5.8 cm.

## 2. Who each animal listens to (topological vs metric)

Held-out R^2 for predicting each animal's turn over the next 0.3 s from its neighbours' mean heading and the direction to their centre.

| Recording | Best k nearest | R^2 | Best radius (BL) | R^2 | Better rule |
| --- | --- | --- | --- | --- | --- |
| Experimental_school_N=39_recording_0 | 12 | 0.059 | 6 | 0.053 | topological |
| Experimental_school_N=39_recording_1 | 7 | 0.068 | 6 | 0.061 | topological |
| Experimental_school_N=8_recording_0 | 5 | 0.102 | 6 | 0.097 | topological |

## 3. Spacing rule (repulsion then attraction)

Mean acceleration of an animal toward each of its 6 nearest neighbours, by distance. The preferred spacing is where it changes from moving away (repulsion) to moving closer (attraction).

| Recording | Preferred spacing (BL) | Preferred spacing (cm) |
| --- | --- | --- |
| Experimental_school_N=39_recording_0 | 3.09 | 7.7 |
| Experimental_school_N=39_recording_1 | 3.75 | 9.4 |
| Experimental_school_N=8_recording_0 | 1.61 | 4.0 |

## 4. Fluid equation fit (Toner-Tu library, sparse regression)

Target: the flock's coarse-grained acceleration Dv/dt. Fit on the first half of each recording, scored on the second half.

**Experimental_school_N=39_recording_0**: continuity check residual 0.6% (should be near 0). Held-out R^2: all terms 0.068, sparse 0.063.

| Term | Meaning | Sparse coefficient | R^2 alone |
| --- | --- | --- | --- |
| `v` | alpha: drive to cruise | -0.109 | 0.000 |
| `¦v¦^2 v` | beta: speed saturation | 1.26 | -0.001 |
| `(v.grad)v` | lambda1: self-advection | 1.27 | 0.031 |
| `(div v) v` | lambda2 | -0.284 | 0.001 |
| `grad ¦v¦^2` | lambda3 | -0.301 | -0.001 |
| `grad rho` | pressure, P ~ rho |  | 0.004 |
| `rho grad rho` | pressure, P ~ rho^2 |  | 0.003 |
| `grad div v` | D_L: bulk viscosity | -0.00343 | 0.004 |
| `lap v` | D_1: shear viscosity |  | 0.000 |
| `rho v` | density-dependent alignment |  | -0.000 |

**Experimental_school_N=39_recording_1**: continuity check residual 0.7% (should be near 0). Held-out R^2: all terms 0.063, sparse 0.063.

| Term | Meaning | Sparse coefficient | R^2 alone |
| --- | --- | --- | --- |
| `v` | alpha: drive to cruise | -0.137 | -0.000 |
| `¦v¦^2 v` | beta: speed saturation |  | -0.000 |
| `(v.grad)v` | lambda1: self-advection | 0.958 | 0.004 |
| `(div v) v` | lambda2 | -0.395 | 0.006 |
| `grad ¦v¦^2` | lambda3 | -0.198 | 0.004 |
| `grad rho` | pressure, P ~ rho | -2.39e-05 | 0.011 |
| `rho grad rho` | pressure, P ~ rho^2 | 3.35e-08 | 0.009 |
| `grad div v` | D_L: bulk viscosity | -0.00267 | 0.004 |
| `lap v` | D_1: shear viscosity | 0.000652 | 0.002 |
| `rho v` | density-dependent alignment | 0.000599 | -0.000 |

