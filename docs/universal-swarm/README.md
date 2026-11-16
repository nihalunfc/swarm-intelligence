# Universal swarm research: from real swarms to a model of the universe

Author: Nihal. License: MIT. Built with Claude, Claude Code, Antigravity and Gemini.
Built on 16 November 2026. Real recorded data only; simulations are labelled and never used as evidence.

This folder summarises three connected pieces of work:

1. **A general framework for decentralised adaptive swarms**, measured the same way on 21 real datasets
   from 7 domain groups (plus 4 cosmic datasets used in part 3).
2. **Application frameworks** that reuse the fitted law: grid, wildfire, epidemics, air traffic, drones, logistics.
3. **The swarm-universe model**: a speculative, explicitly mathematical model of a self-regulating
   universe, fitted to real supernova, BAO and H(z) data and compared with the major cosmological models.

| Read | What it is |
| :-- | :-- |
| [swarm-universe-paper.md](swarm-universe-paper.md) | Paper-style draft of the cosmology part (cautious, web-ready) |
| [swarm-universe-theory.md](swarm-universe-theory.md) | The universe model: postulates, equations, fits, comparison table, evidence table, faults, predictions |
| [../../results/universal/REPORT.md](../../results/universal/REPORT.md) | Full results of the universal swarm study |
| [../../results/universal/cosmology.md](../../results/universal/cosmology.md) | Cosmology fit tables |
| [../../results/universal/applications.md](../../results/universal/applications.md) | Application demo outputs |
| [TODO-manual.md](TODO-manual.md) | Downloads and emails only Nihal can do |

## 1. The 25 datasets

| Group | Datasets (key) | Source |
| :-- | :-- | :-- |
| Animal collective motion | tetra fish school (`fish`), zebrafish groups (`zebrafish`), wild jackdaw flocks 3D (`jackdaw`), homing pigeons under a robotic predator (`pigeon`), ant exploration (`ants`) | Zenodo 10890112, 1470446, 5007024, 6027115, 4931865 |
| Human and machine motion | Lyon pedestrian crowds (`crowd`), NGSIM I-80 road traffic (`traffic`), OpenSky air traffic (`air`), 30-drone outdoor flock (`drones`) | Zenodo 4527462, 7716863, 12751775, 4983910 |
| Spreading | COVID-19 first wave, 26 countries (`covid`), Twitter Higgs-boson cascade (`cascade_higgs`), Twitter 15M movement (`cascade_15m`) | JHU CSSE; Zenodo 2585375 |
| Hazards and criticality | daily wildfire growth, US + Canada (`fire`), Canadian wildfire evacuations (`evac`), earthquakes (`quake`), sunspots (`sunspots`) | Zenodo 11046212, 5703323, 4141086; SILSO |
| Ecology | Canadian lynx 1821-1934 (`lynx`), Christmas bird counts (`birdcounts`) | R datasets, bayesrules |
| Socio-technical | ERCOT grid load (`grid`), Capital Bikeshare (`bikes`), European stock indices (`markets`) | repo sample; R datasets |
| Cosmic | SPARC rotation curves (`sparc`), Pantheon+ supernovae (`pantheon`), DESI DR2 BAO (`bao`), cosmic chronometers (`chronometers`) | Zenodo 16284118; Pantheon+ release; DESI via Cobaya; Moresco |

All are downloaded by `python -m universal.fetch` (see [`universal/sources.yaml`](../../universal/sources.yaml) for
licences and citations). Ten more datasets are listed as placeholders (swifts, starlings, locusts,
honeybees, 39-fish school, IESO, AESO, CWFIS, USGS ComCat, Planck likelihoods) with the reason they
could not be fetched from the cloud runner.

## 2. The general adaptive swarm equation (GASE)

For a collective level X (cases, area burned, load, active users, flock speed):

    dX/dt = r X [1 - (X/K)^theta]  -  kappa (X - X*)  +  F(t)  +  sigma X^gamma xi(t)
            self-limiting growth      set-point regulation  forcing   fluctuation scaling

For agents that move, the same three ideas are a local rule (lengths in nearest-neighbour
distances d_nn, speeds in the typical speed v0):

    a_i = alpha (mean neighbour velocity - v_i) + beta (neighbour centre - x_i) + gamma (v0 - |v_i|) v_i/|v_i|
          alignment                              cohesion                       speed set point

### What the real data say (from results/universal/REPORT.md)

| Characteristic | Result across datasets | Reading |
| :-- | :-- | :-- |
| Alignment | positive in **8 of 8** moving swarms; median alpha 0.16 (fish 0.35, drones 0.37, crowds 1.0, pigeons 0.03) | agents turn toward neighbours' heading everywhere, with very different strengths |
| Repulsion-to-attraction switch | median **0.96 d_nn** (IQR 0.61 to 1.07, 7 swarms) | the switch from push to pull sits at about one neighbour distance in fish, birds, crowds, cars, aircraft, drones |
| Self-regulation of the collective level | **67%** of 12 series have a1 < 0 (pulled back) | most collective levels are regulated; growth phases (COVID, cascades) are not |
| Anti-persistent changes | **83%** of 12 have DFA exponent of changes < 0.5 (median 0.35) | rises tend to be followed by falls (regulation with overshoot). Caveat: differencing noisy data also lowers this exponent |
| Heavy-tailed events | **70%** of 10 event distributions have tail exponent between 1 and 3 (median 2.3) | fires, quakes, cascades, evacuations, bird counts show near-critical size distributions; most are as consistent with a lognormal as with a power law |
| Growth shape | Gompertz or Richards with theta < 1 wins for most fire and COVID curves (fires: Gompertz 137, Richards 90, logistic 47, exponential 16) | growth slows early and asymmetrically: the swarm limits itself before it hits its cap |
| Fluctuation scaling | median gamma 0.90 (7 series) | fluctuations scale almost proportionally with level: agents act collectively, not independently (0.5) |
| Local rule R² | 0.3% to 13% | single-step accelerations are mostly unexplained by the three terms; the rule describes average tendencies, not individual moves |

**Major characteristics (PCA)**: PC1 (30%) is memory and regulation (lag-1 correlation, spectral
slope, restoring coefficient); PC2 (18%) is speed regulation of moving agents; PC3 (14%) is
burstiness and heavy tails. Four clusters emerge that cut across domains: (1) ordered movers and
oscillators (fish, birds, ants, traffic, aircraft, drones, COVID, quakes, sunspots, lynx, bikes),
(2) loosely ordered groups (crowds, zebrafish), (3) bursty information and markets (cascades, grid,
stock indices), (4) hazard spreading (fires, evacuations, bird counts).

The leave-one-group-out check keeps the sign of every constant: no single domain drives the result.

## 3. Application frameworks (`universal/applications/`)

| Domain | What the framework does | Demo result |
| :-- | :-- | :-- |
| Energy / grid | batteries share discharge by state of charge (alignment) toward a 24 h set point; compared with the trained battery swarm from apps/energy on the same data and months | real ERCOT Oct-Dec 2020: the rule-based framework cuts spread 7.3% and no peak; the **trained swarm (10 seeds) cuts spread 10.8% and the peak by 704 MW**, ahead of the proportional rule (9.1%), MPC (6.8%) and threshold rule (5.0%); perfect foresight bound 949 MW. Use the trained swarm |
| Mixed-role energy | batteries, solar with curtailment, and demand response act on the net load each sees, no central coordinator; loaders ready for IESO (Ontario) and AESO (Alberta) | on real ERCOT + NREL data until the Canadian files are downloaded: spread 1,743 MW → 1,490 MW (−14.5%) and peak −453 MW with all three roles, vs −11.7% with solar + batteries |
| Wildfire | each fire forecasts its final size with the Richards law and bids for crews | real MTBS/NBAC fires (203 fires, same fires at each horizon), median abs log error after 5 / 8 / 12 / 16 days: Richards 1.81 / 1.52 / 0.94 / 0.68, persistence 0.83 / 0.84 / 0.56 / 0.40, "stops now" 2.42 / 1.68 / 1.06 / 0.64. **More days help the growth law a lot, but simple persistence still wins**; the law needs weather and fuel inputs |
| Epidemics | each region forecasts its wave and requests help by forecast growth | real COVID first wave, 21-day forecast from 20% of the wave: Gompertz 0.16, Richards 0.26, exponential 0.86 (median abs log error). Saturating laws beat exponential by 3 to 5 times |
| Air traffic | aircraft add the swarm separation and alignment terms only inside an alert radius | real OpenSky: 0.51 close (< 5 NM, 2D) pairs per snapshot; simulation: close-pair steps 28,635 to 3,920 (−86%) at 0.23 mean heading deviation |
| Drones | flocking controller with real-swarm gains plus goal seeking | simulation: all 30 arrive, 3 obstacle hits vs 18 without alignment, polarization 0.81 |
| Logistics | response-threshold task pickup (as in ants and bees) with adaptive thresholds | simulation: mean queue 5.6 vs 69 for round robin, 70% fewer moves |

## 4. The swarm-universe model (short version)

The universe is treated as a swarm of causally connected cells. Gravity is cohesion; cells in
contact align their expansion rates; the vacuum term is regulated toward a set point by a damped
second-order law that switches on when enough structure has formed (quorum). The averaged
(Buchert) equations give three closed forms for dark energy: SU-A (identical to wCDM), SU-B (quorum
emergence) and SU-C (regulated overshoot). Fitted to Pantheon+, DESI DR2 BAO and cosmic chronometers:

* every swarm model fits **as well as ΛCDM** (χ² lower by 5 to 7), but **none is preferred** once extra
  parameters are penalised (ΔAIC −0.9 to −2.7; ΔBIC +2.7 to +15 in favour of ΛCDM);
* SU-B places the switch at z ≈ 1.3; SU-C prefers an underdamped regulator (ζ ≈ 0.2);
* the Hubble tension remains (H0 ≈ 68, 4.3σ from SH0ES);
* galaxies follow one acceleration law with crossover g† = 1.16 × 10⁻¹⁰ m/s² (0.13 dex scatter on 2,696
  SPARC points), 1.09 × cH0/2π — consistent with a local rule tied to a global scale, but a coincidence
  is not a mechanism;
* the model cannot explain the CMB's uniformity without inflation or a bounce, does not explain the
  size of Λ, and needs dark matter (Bullet Cluster).

The full comparison with ΛCDM, inflation, steady state, cyclic, conformal cyclic, quintessence,
holographic DE, unimodular gravity, backreaction, MOND, emergent gravity, cosmological natural
selection and bounce cosmology, and the table of supporting and contradicting observations, are in
[swarm-universe-theory.md](swarm-universe-theory.md).

## 5. Reproduce

```bash
pip install -e ".[dev]" matplotlib openpyxl scikit-learn
python -m universal.fetch                    # about 300 MB of public data into data/universal/raw/
python -m universal.run_study                # about 1 minute
python -m universal.cosmos.fit               # about 15 minutes (multi-start fits)
python -m universal.cosmos.rar
python -m universal.applications.run_demos
pytest tests/test_universal.py
```

Nothing here runs on GitHub Actions automatically; CI only runs the fast unit tests.

## 6. Limits

* One pass per dataset; no bootstrap over recordings yet for the ensemble constants.
* Track datasets differ in frame rate and tracking noise; accelerations from positions are noisy,
  which keeps the local-rule R² low.
* Several "swarms" (sunspots, quakes, markets) are complex systems without identifiable agents; they
  are included to test how far the swarm law generalises, not because they are swarms.
* The cosmology is a phenomenological test of dark-energy shapes motivated by swarm regulation. It
  is not a derivation from first principles.
