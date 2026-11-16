# Manual steps for Nihal

Everything that could be scripted from the cloud runner is built and pushed. These steps need a
person (a browser login, an email, or a network the cloud runner cannot reach). After each
download, put the files in `data/universal/raw/<key>/` and run `python -m universal.run_study`.

## Downloads (browser)

| # | Data | Where | Put files in | Why it matters |
| --: | :-- | :-- | :-- | :-- |
| 1 | Chimney swift flocks, 1,800 birds, 3D | Dryad doi:10.5061/dryad.p68f8 (14 GB; the trajectory files alone are enough) | `data/universal/raw/swift/` | Only flock large enough to test the continuum (Toner-Tu) limit |
| 2 | Jackdaw raw data from Dryad | doi:10.5061/dryad.kb8js06 | already mirrored on Zenodo 5007024 and loaded; nothing to do unless the Dryad version has more flocks | - |
| 3 | Tetra school with 39 fish | Zenodo 10890112, files `Experimental_school_N=39_*` (261 MB each) | `data/universal/raw/fish/` | Larger school for the fish fit; scriptable but large: `python -m universal.fetch --only fish` after adding the files to `sources.yaml` |
| 4 | Locust hopper bands | Zenodo 10463065 (940 MB) | `data/universal/raw/locust/` | Insect marching swarm; needs a loader once the format is known |
| 5 | Honeybee swarm 3D assembly | Zenodo 18992443 (132 MB) | `data/universal/raw/honeybee/` | Self-assembly and disassembly (growth and decay of a swarm) |
| 6 | Ontario grid (IESO hourly demand and output by fuel) | reports-public.ieso.ca/public/Demand/ | `data/universal/raw/ieso/` | Canadian grid for the energy framework |
| 7 | Alberta grid (AESO pool price and load) | aeso.ca market data | `data/universal/raw/aeso/` | Second Canadian grid |
| 8 | Canadian National Fire Database (points and perimeters) | cwfis.cfs.nrcan.gc.ca/datamart | `data/universal/raw/cwfis/` | Full Canadian wildfire record for the wildfire framework |
| 9 | USGS global earthquake catalog | earthquake.usgs.gov/earthquakes/search (CSV, M ≥ 2.5) | `data/universal/raw/comcat/` | Global Gutenberg-Richter and Omori tests |
| 10 | Real ERCOT 2018-22 and NREL weather | needs a new NREL API key (old one is in git history; revoke it) | `apps/energy/data/` | Confirms the grid battery result on another year (old TODO) |

The cloud runner could not reach ieso.ca, aeso.ca, cwfis, usgs.gov, opensky-network.org, sdss.org or
the Planck archive; adding them to the environment's allowed hosts would let the fetch script do
items 6 to 9 next time.

## Emails

| # | To | Ask |
| --: | :-- | :-- |
| 1 | COBBS group, Rome (starling murmurations) | Access to 3D starling trajectories for research use. Note: the 2026 starling data on Zenodo 19628928 is simulated and must not be used as evidence. |
| 2 | ELTE collective motion group, Budapest | Pigeon flock GPS data (password protected) |
| 3 | Bird-flock data requests already drafted | `/mnt/project-files/swarm/bird-flock/data-request-emails.md` |

## Decisions

1. Read `docs/universal-swarm/swarm-universe-theory.md` and decide whether the cosmology part goes in
   the arXiv paper, a separate essay, or stays as an internal research note (recommended: separate
   note; the swarm paper is cs.MA and this would be astro-ph.CO / gr-qc with a much higher bar).
2. The Experiments workflow is now manual only (Actions tab, "Run workflow"). Check the job-minute
   estimate before starting it.
3. Optional: allow more hosts in the cloud environment (see above) so the remaining data can be fetched by script.
