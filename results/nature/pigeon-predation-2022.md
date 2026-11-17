# Emergence of splits and collective turns in pigeon flocks under predation

Species: homing pigeon (Columba livia), GPS, robotic falcon. Source: [Papadopoulou et al. 2022, doi:10.5061/dryad.905qfttkc](https://datadryad.org/stash/dataset/doi:10.5061/dryad.905qfttkc), license CC0-1.0. Real recorded data, no simulation. BL = body length, taken as 0.32 m (approximate).

## 1. Motion summary

| Recording | Track ids | Seconds | Median speed (m/s) | Median nearest neighbour (m) | Polarisation | Milling |
| --- | --- | --- | --- | --- | --- | --- |
| pigeon_flight_9 | 10 | 32 | 19.4 | 1.54 | 0.99 | 0.12 |
| pigeon_flight_10 | 8 | 37 | 16.5 | 1.40 | 0.99 | 0.14 |
| pigeon_flight_11 | 8 | 45 | 18.0 | 1.21 | 0.99 | 0.12 |
| pigeon_flight_12 | 8 | 77 | 17.5 | 1.30 | 0.99 | 0.11 |
| pigeon_flight_13 | 10 | 42 | 17.8 | 1.73 | 0.99 | 0.10 |
| pigeon_flight_14 | 8 | 40 | 16.8 | 1.25 | 1.00 | 0.13 |
| pigeon_flight_15 | 8 | 47 | 20.2 | 1.30 | 0.99 | 0.13 |
| pigeon_flight_16 | 8 | 43 | 21.0 | 1.24 | 0.99 | 0.12 |
| pigeon_flight_17 | 10 | 46 | 20.3 | 1.48 | 1.00 | 0.06 |
| pigeon_flight_18 | 8 | 42 | 20.4 | 1.61 | 0.99 | 0.12 |
| pigeon_flight_19 | 8 | 27 | 21.1 | 1.36 | 0.99 | 0.14 |
| pigeon_flight_20 | 8 | 32 | 20.1 | 1.09 | 0.99 | 0.13 |
| pigeon_flight_21 | 34 | 45 | 18.7 | 0.84 | 0.99 | 0.05 |
| pigeon_flight_22 | 10 | 28 | 19.5 | 1.21 | 1.00 | 0.09 |
| pigeon_flight_23 | 8 | 34 | 18.1 | 1.87 | 0.99 | 0.09 |
| pigeon_flight_24 | 8 | 45 | 17.1 | 1.60 | 0.99 | 0.05 |
| pigeon_flight_25 | 8 | 43 | 16.7 | 1.23 | 0.99 | 0.10 |
| pigeon_flight_26 | 34 | 30 | 20.6 | 0.92 | 0.99 | 0.09 |
| pigeon_flight_27 | 31 | 35 | 18.8 | 1.19 | 0.99 | 0.12 |
| pigeon_flight_28 | 10 | 34 | 20.3 | 1.29 | 0.99 | 0.08 |
| pigeon_flight_29 | 8 | 32 | 22.3 | 1.27 | 0.99 | 0.10 |
| pigeon_flight_30 | 8 | 33 | 21.5 | 1.31 | 0.99 | 0.10 |
| pigeon_flight_31 | 7 | 31 | 22.3 | 1.49 | 0.98 | 0.19 |
| pigeon_flight_32 | 34 | 35 | 18.0 | 0.82 | 0.99 | 0.07 |
| pigeon_flight_33 | 28 | 24 | 22.2 | 1.90 | 1.00 | 0.12 |
| pigeon_flight_34 | 10 | 41 | 22.2 | 1.34 | 0.98 | 0.15 |
| pigeon_flight_35 | 8 | 38 | 18.1 | 1.08 | 0.99 | 0.14 |
| pigeon_flight_36 | 8 | 24 | 24.8 | 1.48 | 0.99 | 0.07 |
| pigeon_flight_37 | 8 | 25 | 23.5 | 1.72 | 0.99 | 0.08 |
| pigeon_flight_38 | 34 | 28 | 24.6 | 1.29 | 0.99 | 0.06 |
| pigeon_flight_39 | 34 | 27 | 23.6 | 0.84 | 1.00 | 0.06 |
| pigeon_flight_40 | 30 | 24 | 24.6 | 1.51 | 0.99 | 0.11 |
| pigeon_flight_41 | 34 | 26 | 23.0 | 0.73 | 0.99 | 0.06 |
| pigeon_flight_42 | 10 | 29 | 22.8 | 1.46 | 0.99 | 0.14 |
| pigeon_flight_43 | 8 | 43 | 22.6 | 0.85 | 0.99 | 0.11 |
| pigeon_flight_44 | 8 | 25 | 23.4 | 1.62 | 0.99 | 0.14 |
| pigeon_flight_45 | 7 | 30 | 21.0 | 1.54 | 0.99 | 0.10 |
| pigeon_flight_46 | 33 | 47 | 18.4 | 0.97 | 0.99 | 0.07 |
| pigeon_flight_47 | 10 | 35 | 19.2 | 0.79 | 0.99 | 0.14 |
| pigeon_flight_48 | 8 | 31 | 20.6 | 1.58 | 0.99 | 0.16 |
| pigeon_flight_49 | 8 | 35 | 19.8 | 1.23 | 0.99 | 0.10 |
| pigeon_flight_50 | 8 | 40 | 17.7 | 1.07 | 0.99 | 0.09 |
| pigeon_flight_51 | 32 | 54 | 19.4 | 0.80 | 1.00 | 0.08 |

## 2. Who each bird listens to, and preferred spacing

Held-out R^2 for predicting each bird's turn over the next 0.2 s. 'no signal' means neither rule explains even 1% of turns.

| Recording | Best k | R^2 | Best radius (BL) | R^2 | Better rule | Repulsion-to-attraction switch (BL) |
| --- | --- | --- | --- | --- | --- | --- |
| pigeon_flight_21 | 15 | -0.025 | 1 | 0.007 | no signal | 1.04 |
| pigeon_flight_26 | 1 | 0.003 | 4 | -0.008 | no signal | 1.03 |
| pigeon_flight_27 | 7 | 0.041 | 15 | 0.018 | topological | 2.69 |
| pigeon_flight_32 | 20 | 0.001 | 20 | -0.004 | no signal | 0.49 |
| pigeon_flight_33 | 7 | 0.076 | 20 | 0.040 | topological | 3.23 |
| pigeon_flight_38 | 2 | 0.011 | 4 | 0.020 | metric | 2.34 |
| pigeon_flight_39 | 12 | 0.037 | 10 | 0.026 | topological | 0.85 |
| pigeon_flight_40 | 7 | 0.081 | 20 | 0.026 | topological | 2.95 |
| pigeon_flight_41 | 3 | 0.024 | 2 | 0.014 | topological | 0.79 |
| pigeon_flight_46 | 20 | 0.015 | 20 | 0.005 | topological | 1.27 |
| pigeon_flight_51 | 8 | 0.027 | 1 | 0.010 | topological | 0.46 |

## 3. Effect of the robotic falcon (extrinsic parameter)

Median per flight, then median over flights.

| Condition | Flights | Speed (m/s) | Turning (deg/s) | Nearest neighbour (m) | Polarisation | Spread from centre (m) |
| --- | --- | --- | --- | --- | --- | --- |
| predator/small | 20 | 19.4 | 12.7 | 1.34 | 0.999 | 2.5 |
| predator/big | 7 | 21.0 | 12.5 | 0.86 | 0.998 | 3.6 |
| control/small | 12 | 20.9 | 9.2 | 1.28 | 0.999 | 2.3 |
| control/big | 4 | 22.0 | 11.0 | 1.13 | 0.998 | 4.0 |

Inside falcon flights, by the falcon's distance to the nearest bird:

| Falcon distance | Frames | Speed (m/s) | Turning (deg/s) | Nearest neighbour (m) | Polarisation | Spread (m) |
| --- | --- | --- | --- | --- | --- | --- |
| 0-30 m | 1122 | 17.3 | 27.1 | 1.35 | 0.996 | 2.9 |
| 30-100 m | 1969 | 19.1 | 13.2 | 1.17 | 0.999 | 2.6 |
| 100-inf m | 2018 | 20.8 | 9.6 | 1.31 | 0.999 | 2.9 |
