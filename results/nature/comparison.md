# Cross-species comparison

All real recorded data. BL = body length (fish 2.5 cm from the paper; birds approximate field-guide lengths: jackdaw 0.34 m, pigeon 0.32 m, swift 0.13 m). Medians over groups.

| Species | Setting | Groups | Speed (BL/s) | Nearest neighbour (BL) | Repulsion-to-attraction switch (BL) | Polarisation | Topological wins | Median best k | Fluid fit R^2 (held out) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Black neon tetra (fish, 39) | lab tank, 2D | 2 | 4.7 | 1.8 | 3.4 | 0.84 | 2/2 | 10 | 0.13 |
| Black neon tetra (fish, 8) | lab tank, 2D | 1 | 6.3 | 1.3 | 1.6 | 0.95 | 1/1 | 5 | n/a |
| Jackdaw | wild, 3D stereo | 6 | 35.4 | 5.1 | 2.7 | 0.98 | 2/6 | 10 | n/a |
| Homing pigeon | GPS 5 Hz, 2D | 43 | 63.3 | 4.0 | 1.0 | 0.99 | 7/8 | 7 | n/a |
| Chimney swift | wild, 3D, at roost | 3 | 48.6 | 17.5 | n/a | 0.38 | not run | n/a | 0.66 |

Fluid fit uses the same method for fish and swifts (sparse Toner-Tu library, kernel width 2 nearest-neighbour distances for both). Jackdaw and pigeon groups are too short or too few for the field fit.
