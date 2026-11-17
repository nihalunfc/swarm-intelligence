# Applied test: real human bottlenecks

Real data only. Pedestrians: Juelich HERMES 2009 bottleneck runs (Zenodo 1054017, CC BY 4.0). Vehicles: DRaT highway merge, four lanes to three, Fort Worth (Zenodo 20171110, CC BY 4.0).

## 1. A crowd leaving through an exit

| Exit width (m) | People | Flow (people/s) | Flow per metre (1/m/s) | Speed (m/s) | Nearest neighbour (m) | Polarisation | Push-to-pull switch (m) | Neighbour rule R^2 (k / radius) | Order before exit vs flow after (r) | Fluid fit R^2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.70 | 148 | 1.61 | 2.30 | 0.38 | 0.46 | 0.88 | 0.57 | 0.184 / 0.183 | 0.14 | 0.101 |
| 0.95 | 159 | 1.75 | 1.84 | 0.45 | 0.50 | 0.91 | 0.58 | 0.207 / 0.209 | -0.04 | 0.050 |
| 1.20 | 170 | 2.33 | 1.94 | 0.65 | 0.52 | 0.95 | 0.59 | 0.220 / 0.220 | 0.39 | 0.046 |
| 1.80 | 220 | 2.84 | 1.58 | 0.96 | 0.59 | 0.98 | 0.61 | 0.275 / 0.274 | -0.17 | 0.012 |

## 2. Drivers at a lane drop: car-following vs flock rules

Held-out R^2 for each driver's speed change over the next second. Car-following looks only at the car ahead (gap, own speed, speed difference). Flock terms add the two bird rules: match the mean speed of the 6 nearest vehicles in any lane (alignment) and move toward their centre (cohesion).

| Period | Minutes | Vehicles | Median speed (m/s) | Density (veh/km, all lanes) | Car-following | + alignment | + alignment + cohesion |
| --- | --- | --- | --- | --- | --- | --- | --- |
| congested | 39 | 2367 | 8.3 | 108 | 0.323 | 0.323 | 0.355 |
| free flow | 46 | 2892 | 27.6 | 37 | 0.072 | 0.085 | 0.101 |
