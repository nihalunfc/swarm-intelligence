# Bird Flock study (natural swarms)

This study measures how real animal groups move and fits fluid-like equations to them. The aim is one general equation whose terms can be reused as control rules for agent swarms (drones, vehicles, logistics, air traffic).

**Rule: real recorded data only.** No simulated data is used as study data. Small hand-built inputs appear only in `tests/test_nature.py`, to check the maths.

Plan, data sources and research map: <https://claude.ai/artifact/DzcxGNrZzboUt66g52XnaQ>

## Stages

| Stage | Code | Output |
| --- | --- | --- |
| 1. Real tracks | `fetch.py`, `sources.yaml`, `flock/io.py` | `nature/data/raw/<id>/` (git-ignored) |
| 2. Clean and describe | `flock/kinematics.py` | speed, spacing, polarisation, milling |
| 3. Local rules | `flock/rules.py` | k nearest vs radius, preferred spacing |
| 4. Fields | `flock/fields.py` (`coarse_grain`) | density and velocity fields, continuity check |
| 5. Fluid equation | `flock/fields.py` (`fit_equation`) | sparse Toner-Tu fit, held-out R^2 |
| 6-8. Species, general form, agent cross-check | next | |

## Run

```bash
python nature/fetch.py fish-tetra-2024      # about 600 MB from Zenodo
python nature/run_study.py fish-tetra-2024  # a few minutes on a laptop CPU
```

Results go to `results/nature/<id>.md` and `.json`. Nothing here uses GitHub Actions.

## Datasets

See `sources.yaml` for licence, citation and file list.

| id | Animals | Fetch |
| --- | --- | --- |
| `fish-tetra-2024` | black neon tetra schools, 2D, 8 and 39 fish | automatic (Zenodo, CC BY 4.0) |
| `jackdaw-2019` | wild jackdaw flocks, 3D | manual (Dryad, CC0) |
| `swift-2017` | chimney swifts at the roost, 3D, about 1,800 birds | manual (Dryad, CC0) |
| `pigeon-predation-2022` | pigeon flocks with a robotic falcon, GPS | manual (Dryad, CC0) |

**Manual (Dryad) downloads:** Dryad's file API needs a login token, so automatic download is not possible. Download the files from the dataset page in a browser, then put them in `nature/data/raw/<id>/`.
