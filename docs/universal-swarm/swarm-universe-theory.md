# The swarm universe: a self-regulating, decentralised model of cosmic expansion

Author: Nihal. Status: **speculative theory with a first data test**. Nothing here is a proof.
The model is written so it can fail: every claim below says which observation would rule it out.
Numbers come from `results/universal/cosmology.md` and `results/universal/rar.json`, produced by code
in `universal/cosmos/` on real public data.

## 1. The idea in one paragraph

Natural swarms (fish, birds, crowds, fires, epidemics, grids) have no leader, yet they keep order,
limit their own growth, and pull themselves back after a shock. The universal swarm study
(`results/universal/REPORT.md`) measures the same three ingredients in 21 real datasets: agents
**align** with neighbours, **cohere** with a pull that switches on beyond a fixed distance, and the
collective level is **regulated** toward a set point, often with overshoot. The swarm-universe
hypothesis is that the universe can be described the same way: many causally connected regions
("cells") each follow local rules, and what we call the cosmological constant or dark energy is the
**collective set-point regulation** of that swarm, switched on when enough structure has formed. The
smooth Friedmann universe is then the mean-field limit of the swarm, just as a fluid equation is the
mean-field limit of a flock.

## 2. Postulates

| | Postulate | Swarm analogue | Status |
| :-- | :-- | :-- | :-- |
| P1 | Space is made of cells i (comoving domains), each with a local expansion rate θ_i = 3H_i, density ρ_i and a local vacuum term λ_i. | agents with velocity, local density, internal state | modelling choice |
| P2 | Gravity is the cohesion term: each cell obeys the Raychaudhuri equation. | cohesion β | standard GR |
| P3 | Cells in causal contact align their expansion rates. | alignment α | new, testable (homogenisation) |
| P4 | λ_i is regulated toward a set point Λ* by a damped second-order law, switched on by a quorum signal: the local collapsed (bound-structure) fraction F_i. | speed set point γ, quorum sensing | new, speculative |
| P5 | Fluctuations of λ_i scale with its level, σ ∝ λ^g (Taylor's law). | fluctuation scaling | new, speculative |
| P6 | The observed Friedmann universe is the average over cells (Buchert averaging). | continuum limit of a flock (Toner-Tu) | standard technique |

## 3. Micro equations (one cell)

With proper time τ, e-folds N = ln a, and units 8πG = c = 1 where convenient:

**Cohesion (gravity, P2).** Raychaudhuri for an irrotational dust cell plus the local vacuum term:

  dθ_i/dτ = −θ_i²/3 − 2σ_i² − (ρ_i + 3p_i)/2 + λ_i

**Alignment (P3).** Cells inside each other's horizon couple diffusively:

  dθ_i/dτ ⊃ α Σ_j K_ij (θ_j − θ_i),   K_ij = 0 if d_ij > d_horizon

**Continuity.** dρ_i/dτ = −θ_i (ρ_i + p_i)

**Regulation with quorum (P4).** The vacuum term is driven to its set point by a damped regulator
whose input is switched on by the collapsed fraction F_i(τ):

  d²λ_i/dN² + 2ζω dλ_i/dN + ω² (λ_i − Λ* Q(F_i)) = σ λ_i^g ξ_i(N),   Q(F) = F^s / (F^s + F_t^s)

ζ is the damping ratio, ω the regulation frequency in e-folds, F_t the quorum threshold, s its
sharpness. This is the same second-order set-point law the application frameworks use
(`universal/applications/core.py`), and the same structure as the general adaptive swarm equation
(GASE) of the universal study:

  dX/dt = r X [1 − (X/K)^θ] − κ (X − X*) + F(t) + σ X^γ ξ(t)

where the Richards growth term is the quorum switch, κ (X − X*) is the regulator, and γ is the
fluctuation-scaling exponent.

## 4. Mean field: from swarm to Friedmann

Averaging over a large domain D (Buchert 2000) gives, for the domain scale factor a_D,

  3 ä_D / a_D = −⟨ρ⟩/2 + Q_D + ⟨λ⟩
  3 (ȧ_D / a_D)² = ⟨ρ⟩ − ⟨R⟩/2 − Q_D/2 + ⟨λ⟩
  Q_D = (2/3)(⟨θ²⟩ − ⟨θ⟩²) − 2⟨σ²⟩

Two swarm quantities appear directly:

* **Disorder of the swarm** (variance of expansion rates, Q_D). In a flock this is 1 − polarization.
  Alignment (P3) drives it to zero, so the averaged universe becomes Friedmann-like. Standard
  perturbation theory finds Q_D is small today (of order 10^-5 of H²), so **backreaction alone cannot
  be dark energy**; we keep it only as the reason the mean-field limit is valid.
* **Mean vacuum** ⟨λ⟩(N). If cells reach quorum at about the same time (narrow F distribution),
  the step response of the regulator gives the closed forms fitted to data:

| Model | ρ_DE(a) / ρ_DE(1) = f(a) | Limit that gives ΛCDM |
| :-- | :-- | :-- |
| SU-A homeostatic vacuum (first-order regulator, dρ/dN = −k(ρ − ε ρ_m)) | a^(−k) plus a term ∝ a^−3 absorbed into matter, i.e. **exactly wCDM with w = k/3 − 1** | k → 0 |
| SU-B quorum emergence (regulator fast, switch is the Richards/Hill function) | (1 + a_t^s) / (1 + (a_t/a)^s) | s → 0 or a_t → 0 |
| SU-C regulated overshoot (switch sharp, regulator underdamped) | g(N)/g(0), g(n) = 1 − e^(−ζωn)[cos(ω_d n) + (ζω/ω_d) sin(ω_d n)], n = ln(a/a_on), ω_d = ω√(1−ζ²) | ζ → 1 with large ω |

The effective equation of state is w(a) = −1 − (1/3) d ln f / d ln a. SU-B is always phantom
(w < −1) while it switches on. SU-C is phantom while rising, crosses w = −1 at the overshoot peak,
then behaves like quintessence (w > −1) while relaxing. That crossing pattern is a prediction of the
underdamped regulator, not an input.

**Self-healing.** Linearising the regulator around the set point gives eigenvalues
−ζω ± iω√(1−ζ²): any perturbation of λ decays with e-folding time 1/(ζω). The de Sitter state is an
attractor. Note ΛCDM is already self-regulating in this sense: for matter + Λ,
dH/dt = −(3/2)(H² − H_Λ²), a first-order set-point law with set point H_Λ = √(Λ/3). The swarm model's
new content is not that the universe regulates, but **when** regulation switches on (tied to
structure) and **how** it approaches the set point (overshoot).

## 5. Origin and growth (more speculative)

* **Origin as an ordering transition.** Self-propelled swarms show a transition from disorder to
  collective motion when noise drops below a critical value (Vicsek). In the swarm picture the start
  of coherent expansion is such an ordering transition of the cells. This is an analogy only: it
  does not predict the primordial power spectrum, its tilt n_s ≈ 0.965, or the tensor bound, all of
  which inflation does.
* **Horizon problem.** Alignment needs causal contact (K_ij = 0 beyond the horizon), so the swarm
  cannot by itself explain why the CMB is uniform across regions that were never in contact. The
  model needs an early phase in which cells were in contact (inflation, a bounce, or a slow
  contracting phase). **This is a real gap; the swarm model is not an alternative to inflation.**
* **Growth and reproduction.** Smolin's cosmological natural selection treats universes as
  reproducing via black holes. A swarm of universes with heritable constants is a natural
  extension, but it is untestable with current data and is not part of the fitted model.

## 6. First data test (real data)

From `results/universal/cosmology.md` (Pantheon+ 1,580 SNe with full covariance, DESI DR2 BAO,
15 cosmic chronometers; with and without the Planck sound-horizon ruler r_d = 147.09 ± 0.26 Mpc):
see that file for the full table. Summary written after the fits:

| Model (late + CMB ruler) | χ² | extra params | ΔAIC vs ΛCDM | ΔBIC vs ΛCDM | H0 | w(z=0), w(z=1) |
| :-- | --: | --: | --: | --: | --: | :-- |
| ΛCDM | 1406.2 | 0 | 0 | 0 | 68.6 ± 0.5 | −1, −1 |
| SU-A = wCDM | 1401.5 | 1 | −2.7 | +2.7 | 67.8 ± 0.6 | −0.91, −0.91 |
| w0waCDM (CPL) | 1401.3 | 2 | −0.9 | +9.9 | 67.7 ± 0.6 | −0.89, −0.99 |
| SU-B quorum emergence | 1400.7 | 2 | −1.5 | +9.3 | 68.1 ± 0.5 | −1.00, −1.63 |
| SU-C regulated overshoot | 1399.3 | 3 | −0.9 | +15.2 | 67.8 ± 0.6 | −1.01, −1.27 |

What this says, plainly:

* **All three swarm models fit the real expansion data at least as well as ΛCDM** (χ² lower by 5 to 7,
  mostly from DESI BAO: 11.0 for ΛCDM vs 7.9 for SU-B and 6.2 for SU-C).
* **None is significantly preferred.** AIC differences are under 3 (no real preference) and BIC, which
  penalises extra parameters, prefers ΛCDM by 9 to 15. The data do not require a swarm mechanism.
* SU-B prefers a **sharp switch-on of the vacuum term at a_t ≈ 0.43 (z ≈ 1.3)**, around the era when
  galaxy clusters start to assemble. That timing is what a quorum picture predicts, but it is also
  where SN and BAO data are most constraining, so it may simply reflect where the data sit.
* SU-C prefers an underdamped regulator (ζ ≈ 0.16 to 0.25) that switches on early (z ≈ 6 to 14) and
  oscillates about once per e-fold. That is close to fitting noise; treat it as a hint to test with
  DESI DR3 and Euclid, not as a detection.
* **Hubble tension is not solved**: every model gives H0 ≈ 67 to 68 km/s/Mpc, 4.3 to 4.4σ below SH0ES
  when the CMB ruler is used. Late-time dark-energy changes cannot fix it here.
* The phantom-to-quintessence crossing that DESI reports is reproduced in direction by the CPL fit
  (w0 = −0.89, wa = −0.20) but is weak without full CMB likelihoods.

Galaxy scale (SPARC, 147 galaxies, 2,696 points): the observed acceleration follows the visible
matter with one crossover scale g† = 1.16 × 10⁻¹⁰ m/s² and 0.13 dex scatter; Newtonian gravity without
dark matter is off by 0.43 dex on average (0.72 dex at low accelerations). g† is
1.09 × cH0/2π. A swarm reading: the pull switches from local (Newtonian) to a collective floor at
one fixed scale, like the repulsion-to-attraction switch distance measured in animal swarms
(median 0.96 nearest-neighbour distances across 7 swarms). If the galaxy-scale floor is set by the
global regulator, g† should scale with H(z); ΛCDM with cold dark matter has no reason for that.

## 7. Comparison with major cosmological models

| Model | Core idea | Shares with swarm universe | Differs | What would separate them |
| :-- | :-- | :-- | :-- | :-- |
| ΛCDM | GR + cold dark matter + constant Λ | Same early universe, same gravity; de Sitter attractor | Λ is constant and unexplained; no link to structure | w(z) ≠ −1; DE evolution timed with structure growth |
| Inflation | Early accelerated expansion seeds perturbations and fixes horizon/flatness | Needs it (or a substitute) for the horizon problem | Swarm model says nothing about the primordial spectrum | None at early times; swarm model inherits inflation |
| Steady state (Hoyle, Bondi, Gold) | Constant density via continuous creation | Self-maintaining universe | No Big Bang; ruled out by CMB and source counts | Already falsified; swarm model keeps a hot Big Bang |
| Cyclic / ekpyrotic (Steinhardt, Turok) | Repeated bounces; slow contraction smooths space | Regulation and repetition | Swarm regulation is within one expansion | Primordial gravitational waves (ekpyrotic: none) |
| Conformal cyclic (Penrose) | Aeons joined at conformal boundaries | Self-renewal | Different mechanism, no regulator | Claimed CMB "Hawking points" (disputed) |
| Quintessence | A scalar field rolls, w > −1 | Dynamical dark energy | Swarm DE is regulated and structure-triggered; SU-C crosses w = −1, single-field quintessence cannot | Sign and timing of w(z) crossing |
| Holographic / running-vacuum DE | DE set by a horizon scale or by H² | DE tied to a global scale | Swarm ties DE to the collapsed fraction | DE vs growth history correlation |
| Unimodular gravity / vacuum sequestering | Λ is an integration constant or globally fixed | Global constraint on the vacuum | Swarm is local and dynamical | w(z) ≠ −1 favours swarm |
| Backreaction (Buchert) | Inhomogeneity averages to acceleration | Same averaging equations; Q_D = swarm disorder | Swarm does not rely on Q_D being large | Size of Q_D in simulations (small) |
| MOND (Milgrom) | Gravity changes below a0 | One acceleration scale, a0 ≈ cH0/2π | Swarm keeps GR and needs dark matter (bullet cluster) | a0(z) ∝ H(z) test; cluster lensing |
| Emergent gravity (Verlinde) | Gravity emerges from entanglement entropy; a0 = cH0/6 | Emergence from many micro degrees of freedom; local-global link | Verlinde derives a0; swarm only fits it | Lensing around isolated galaxies; dwarf galaxies |
| Cosmological natural selection (Smolin) | Universes reproduce via black holes | Population of self-reproducing systems | Swarm model is one universe | Neutron-star maximum mass (CNS prediction) |
| Loop quantum cosmology / bounce | Quantum gravity replaces the singularity | Avoids a hard start, self-limiting | Swarm model silent on the singularity | Pre-bounce imprints in the CMB |

## 8. Evidence table

"Supports" means the observation is consistent with and naturally explained by the swarm picture,
not that it proves it; most items are also explained by ΛCDM.

| Observation | Data | Verdict for the swarm universe | Why |
| :-- | :-- | :-- | :-- |
| Accelerating expansion (SNe Ia) | Pantheon+ | Consistent | All SU models fit as well as ΛCDM (see §6) |
| DESI DR2 hint of evolving DE (w0 > −1, wa < 0) | DESI DR2 + SNe | Mildly supports SU-C | An underdamped regulator crosses from phantom to w > −1, the same direction DESI prefers; significance is model-dependent (DESI: 2.8 to 4.2σ with CMB) |
| Cosmic coincidence (Ω_Λ ≈ Ω_m today) | All probes | Supports the idea | DE switches on with structure (quorum), so it naturally becomes important when structure has formed; ΛCDM treats it as chance |
| Size of Λ (120 orders below naive QFT) | Theory | Not solved | The set point Λ* is an input; the model does not explain its value |
| CMB acoustic peaks, damping tail | Planck | Consistent only by inheritance | Regulator is off at z > z_on; early physics is ΛCDM |
| CMB uniformity across causally disconnected regions | Planck | **Contradicts a swarm-only origin** | Alignment needs causal contact; requires inflation or a bounce |
| Flatness | Planck + BAO | Neutral | Inherited from inflation |
| Big Bang nucleosynthesis (D, He-4) | Abundances | Consistent by inheritance | Regulator off at BBN |
| BAO standard ruler | DESI DR2 | Consistent | Fits with r_d from Planck |
| Hubble tension (73 vs 67-68 km/s/Mpc) | SH0ES vs CMB+BAO | **Not solved** | Late-time DE changes cannot raise H0 while keeping the BAO+SN shape (see §6 tension column) |
| S8 / growth tension | Weak lensing | Open | Not yet tested; a structure-triggered DE predicts a specific growth suppression to test |
| Cosmic web (filaments, voids, clusters) | Galaxy surveys | Analogy supports | Aggregation into filaments and clusters is what attractive swarms do; no quantitative test yet |
| Galaxy rotation curves / RAR with one scale | SPARC | Supports a "local rule with one switch scale" | One-parameter law, 0.13 dex scatter; but the same is fitted by MOND and is a known ΛCDM challenge |
| a0 ≈ cH0/2π coincidence | SPARC + H0 | Suggestive | Numerically within ~10% here; a coincidence is not a mechanism |
| Bullet Cluster, cluster lensing offsets | Lensing + X-ray | **Contradicts any no-dark-matter version** | The swarm model must keep dark matter as a cohesive component |
| GW170817 (gravity waves travel at c) | LIGO/Virgo + GRB | Consistent | Swarm model leaves GR unchanged |
| Early massive galaxies (JWST) | JWST | Open | Faster early assembly would change the quorum timing; not modelled |
| Large-scale anomalies (dipole, low-ℓ) | Planck, quasars | Open | Local alignment could produce domains; no prediction yet |

## 9. Known faults (honest list)

1. **Degeneracy.** SU-A is mathematically wCDM. SU-B and SU-C are dark-energy parametrisations;
   good fits do not show that a swarm mechanism exists.
2. **Information criteria.** Extra parameters are penalised; see dAIC/dBIC in
   `results/universal/cosmology.md`. With BIC, ΛCDM is usually preferred.
3. **No microphysics.** The quorum signal F (collapsed fraction) and the regulator are postulated.
   A Lagrangian that produces them is missing, and the regulator could violate energy conditions
   (SU-B and the rising part of SU-C are phantom).
4. **Early universe is borrowed.** Horizon, flatness, primordial spectrum and nucleosynthesis come from
   the standard model, not from the swarm.
5. **Analogy is not identity.** The natural-swarm constants (alignment gains, switch distances,
   Taylor exponents) motivate the form of the equations; they do not set cosmological parameters.
6. **Data used here** omit full CMB likelihoods (only the r_d ruler), weak lensing, and redshift-space
   distortions, which are the strongest tests of a structure-triggered dark energy.

## 10. Falsifiable predictions

1. **w(z) shape.** If DE is a regulated swarm, w(z) crosses −1 from below to above at the overshoot
   peak, at a redshift close to when the collapsed fraction crosses the quorum threshold. A future
   DESI/Euclid/Rubin result with w = −1 at all z at high precision rules out SU-B and SU-C.
2. **Environment dependence.** Local cells with low collapsed fraction (deep voids) should show a
   weaker vacuum term. Supernova Hubble residuals split by void/cluster environment test this.
3. **a0 tracks H.** If the galaxy-scale switch is set by the global regulator, a0(z) ∝ H(z); high-z
   rotation curves (JWST, ALMA, SKA) test this.
4. **Growth suppression.** Structure-triggered DE predicts a specific link between fσ8(z) and the
   DE switch; redshift-space distortion data test it.

## 11. How to reproduce

```bash
python -m universal.fetch                 # public data only
python -m universal.run_study             # natural and engineered swarms
python -m universal.cosmos.fit            # SN + BAO + H(z) model comparison
python -m universal.cosmos.rar            # galaxy rotation curves
python -m universal.applications.run_demos
```
