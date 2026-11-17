# Three-dimensional trajectories and network analyses of group behaviour within chimney swift flocks

Species: chimney swift (Chaetura pelagica), wild. Source: [Evangelista et al. 2017, Proc. R. Soc. B, doi:10.5061/dryad.p68f8](https://datadryad.org/dataset/doi:10.5061/dryad.p68f8) (Zenodo mirror 5082229), license CC0-1.0. Real recorded data, no simulation. Likely ghost tracks (speed under 2 or over 25 m/s) are dropped, as the data README advises.

## 1. Motion summary (one frame in 15 sampled)

| File | Frames | Birds per frame | Speed (m/s) | Nearest neighbour (m) | Polarisation | Circling about chimney (-1 to 1) |
| --- | --- | --- | --- | --- | --- | --- |
| A_nodes.hdf5 | 1020 | 320 | 6.0 | 3.88 | 0.59 | 0.20 |
| B_nodes.hdf5 | 1131 | 940 | 6.5 | 2.28 | 0.36 | -0.10 |
| C_nodes.hdf5 | 908 | 236 | 6.3 | 1.40 | 0.38 | 0.20 |

## 2. Fluid equation fit (horizontal plane)

Target: coarse-grained horizontal acceleration. Grid cell = median nearest-neighbour distance (2.4 m). Fit on the first half of the frames, scored on the second half. '+roost' adds two candidate new terms: a pull toward the chimney and circling around it.

| Fit | Samples | Held-out R^2 (all terms) | Held-out R^2 (sparse) | Kept terms |
| --- | --- | --- | --- | --- |
| sigma=2nn | 4050276 | 0.652 | 0.658 | `v` 0.0261, `¦v¦^2 v` -0.000388, `(v.grad)v` 0.625, `(div v) v` -0.121, `grad ¦v¦^2` -0.143, `grad rho` 12.7 |
| sigma=2nn +roost | 4050276 | 0.645 | 0.656 | `v` 0.0451, `¦v¦^2 v` -0.000861, `(v.grad)v` 0.616, `(div v) v` -0.0973, `grad ¦v¦^2` -0.141, `toward roost` 0.182, `around roost` 0.0871 |
| sigma=4nn | 5530798 | 0.698 | 0.710 | `(v.grad)v` 1.2, `(div v) v` -0.338, `grad ¦v¦^2` -0.202, `grad rho` 21.9, `grad div v` -11.2 |
| sigma=4nn +roost | 5530798 | 0.704 | 0.708 | `v` 0.045, `¦v¦^2 v` -0.000903, `(v.grad)v` 1.21, `(div v) v` -0.264, `grad ¦v¦^2` -0.205, `grad div v` -9.74, `toward roost` 0.14, `around roost` 0.0918 |
