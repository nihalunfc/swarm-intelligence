---
title: "Can a self-regulating swarm describe cosmic acceleration? A cautious test against supernova, BAO and H(z) data"
author: Nihal
date: 2026-11-16
status: draft, not peer reviewed
license: MIT (code), CC BY 4.0 (text)
description: A speculative dark-energy model inspired by decentralised natural swarms, fitted to Pantheon+, DESI DR2 and cosmic chronometers. It fits as well as ΛCDM but is not preferred.
---

# Can a self-regulating swarm describe cosmic acceleration?

**A cautious test against supernova, BAO and H(z) data**

Nihal · Draft of 16 November 2026 · Not peer reviewed

> **Read this first.** This is an exploratory, speculative study. The model is a phenomenological
> description of dark energy motivated by an analogy with natural swarms. It is not derived from a
> fundamental theory, it does not outperform the standard model (ΛCDM) once its extra parameters are
> penalised, and it leaves the main open problems of cosmology (the size of Λ, the Hubble tension, the
> initial conditions) unsolved. The value of the exercise is that it makes the analogy precise enough to
> be tested and to fail.

## Abstract

Decentralised swarms in nature keep order without a leader: agents align with neighbours, attract
beyond a fixed distance, and the collective level is regulated toward a set point. We measure these
three ingredients with one method on 21 real datasets (fish, birds, ants, crowds, traffic, aircraft,
drones, epidemics, information cascades, wildfires, earthquakes, populations, grids and markets) and
find positive alignment in all 8 moving swarms, a push-to-pull switch at about one neighbour distance,
and set-point regulation in 67% of collective time series. Motivated by this, we model the universe as
a swarm of causally connected cells in which gravity acts as cohesion, expansion rates align, and the
vacuum energy is regulated by a damped second-order law that switches on when enough bound structure
has formed. Averaging over cells gives three closed-form dark-energy histories: a first-order
"homeostatic vacuum" (mathematically identical to wCDM), a "quorum emergence" switch, and a "regulated
overshoot". Fitted to 1,580 Pantheon+ supernovae with full covariance, DESI DR2 baryon acoustic
oscillations and 15 cosmic-chronometer H(z) points, all three fit the data at least as well as ΛCDM
(χ² lower by 4.7 to 6.9), but none is preferred: ΔAIC ranges from −0.9 to −2.7 and ΔBIC from +2.7 to
+15.2 in favour of ΛCDM. The Hubble tension persists (H0 ≈ 68 km/s/Mpc, 4.3σ below the distance-ladder
value). On galaxy scales, 2,696 SPARC rotation-curve points follow a single acceleration relation with
crossover g† = 1.16 × 10⁻¹⁰ m/s², about 1.09 cH0/2π; we note this as a coincidence that a
self-regulating picture would need to explain, not as evidence for it. We list the observations that
contradict the model and four tests that could rule it out.

## 1. Introduction

ΛCDM describes the expansion history, the cosmic microwave background (CMB) and large-scale structure
with six parameters, but the cosmological constant Λ is put in by hand, its observed value is many
orders of magnitude below naive vacuum estimates, and it becomes dynamically important only recently
(the coincidence problem). Recent DESI results combined with supernovae have reported a preference,
of model-dependent significance, for dark energy that evolves with time (DESI Collaboration 2025).

Swarms in nature solve a related problem every day: they keep a collective quantity (spacing,
speed, population, activity) near a set point without any agent knowing the global state. Many
self-organising systems show the same small set of rules (Vicsek et al. 1995; Couzin et al. 2002;
Ballerini et al. 2008). This paper asks a narrow question: **if dark energy behaved like the set-point
regulation of a decentralised swarm, what would the expansion history look like, and do current data
allow or prefer it?**

We do not claim that the universe is a swarm. We use the analogy to write down specific, testable
dark-energy histories and check them against public data with transparent code.

## 2. What real swarms share

Using one loader per dataset and the same dimensionless measurements (lengths in nearest-neighbour
distances, speeds in the typical speed), we fit for moving agents the local rule

  a_i = α (⟨v⟩_neighbours − v_i) + β (⟨x⟩_neighbours − x_i) + γ (v₀ − |v_i|) v̂_i

and for collective time series X(t) the general adaptive swarm equation (GASE)

  dX/dt = r X [1 − (X/K)^θ] − κ (X − X*) + F(t) + σ X^g ξ(t).

Key results (full tables in `results/universal/REPORT.md`):

| Characteristic | Result |
| :-- | :-- |
| Alignment α > 0 | 8 of 8 moving swarms (median α = 0.16) |
| Push-to-pull switch distance | median 0.96 neighbour distances (7 swarms) |
| Set-point regulation (κ > 0) | 8 of 12 collective series |
| Changes that reverse more than chance (DFA < 0.5) | 10 of 12 (caveat: differencing noisy data lowers this exponent) |
| Heavy-tailed event sizes (exponent 1 to 3) | 7 of 10 |
| Self-limiting growth beats exponential | most wildfire and COVID-19 growth curves (Gompertz or Richards with θ < 1) |

Two of these motivate the cosmological model directly: collective levels are **regulated**, and the
regulation is often **underdamped** (it overshoots and comes back). Growth is **self-limiting** and
switches on asymmetrically. These are motivations, not derivations.

## 3. The swarm-universe model

### 3.1 Cells and local rules

Space is divided into comoving cells i with local expansion rate θ_i = 3H_i, matter density ρ_i and a
local vacuum term λ_i. In units 8πG = c = 1:

* **Cohesion (gravity).** dθ_i/dτ = −θ_i²/3 − 2σ_i² − ρ_i/2 + λ_i (Raychaudhuri, irrotational dust).
* **Alignment.** dθ_i/dτ ⊃ α Σ_j K_ij (θ_j − θ_i), with K_ij = 0 for cells outside each other's horizon.
* **Regulation with quorum.** With N = ln a,

  d²λ_i/dN² + 2ζω dλ_i/dN + ω² [λ_i − Λ* Q(F_i)] = 0,  Q(F) = F^s / (F^s + F_t^s),

  where F_i is the local fraction of matter in bound structures, F_t a threshold, ζ the damping ratio
  and ω the regulation rate per e-fold.

### 3.2 Mean field

Averaging over a large domain (Buchert 2000) gives

  3 ä/a = −⟨ρ⟩/2 + Q_D + ⟨λ⟩,  Q_D = (2/3)(⟨θ²⟩ − ⟨θ⟩²) − 2⟨σ²⟩.

Q_D measures the disorder of the swarm (the analogue of 1 − polarisation). Alignment drives it to zero;
perturbative estimates put it far below what dark energy requires, so we do not use it as dark energy.
If cells reach quorum at about the same time, ⟨λ⟩ follows the regulator's step response. With
f(a) = ρ_DE(a)/ρ_DE(1) and E²(z) = Ω_m(1+z)³ + Ω_r(1+z)⁴ + (1 − Ω_m − Ω_r) f(a):

| Model | f(a) | Free parameters | ΛCDM limit |
| :-- | :-- | :-- | :-- |
| SU-A homeostatic vacuum (first-order) | a^(−k): identical to wCDM with w = k/3 − 1 | 1 | k → 0 |
| SU-B quorum emergence | (1 + a_t^s) / (1 + (a_t/a)^s) | 2 | s → 0 |
| SU-C regulated overshoot | g(N)/g(0), g(n) = 1 − e^(−ζωn)[cos ω_d n + (ζω/ω_d) sin ω_d n], n = ln(a/a_on) | 3 | ζ → 1, ω large |

The effective equation of state is w(a) = −1 − (1/3) d ln f/d ln a. SU-B is phantom (w < −1) while it
switches on; SU-C is phantom while rising and crosses to w > −1 after its overshoot.

Note that ΛCDM is already self-regulating in one sense: for matter plus Λ, dH/dt = −(3/2)(H² − H_Λ²),
a first-order law relaxing to H_Λ. What the swarm model adds is a specific **trigger** (structure) and
**approach** (overshoot).

## 4. Data and method

| Data | Use | Reference |
| :-- | :-- | :-- |
| Pantheon+ (1,580 SNe Ia at z > 0.01, Cepheid hosts removed) | shape of D_L(z), full STAT+SYS covariance, absolute magnitude marginalised analytically | Scolnic et al. 2022; Brout et al. 2022 |
| DESI DR2 BAO (13 measurements with covariance) | D_M/r_d, D_H/r_d, D_V/r_d | DESI Collaboration 2025 |
| Cosmic chronometers (15 points, BC03 set) | H(z) directly, sets H0 | Moresco et al. 2012, 2015, 2016 |
| Optional sound-horizon prior r_d = 147.09 ± 0.26 Mpc | early-universe ruler | Planck Collaboration 2020 |
| SPARC (147 galaxies, 2,696 points after quality cuts) | radial acceleration relation | Lelli, McGaugh & Schombert 2016 |

Models are flat with radiation included. Parameters are fitted by multi-start L-BFGS-B followed by
Nelder-Mead (12 starts, 30 for SU-C); uncertainties are from the numerical Hessian of χ² and are only
approximate. We compare models with AIC = χ² + 2k and BIC = χ² + k ln n (n = 1,609 with the r_d prior).
No full CMB likelihood, weak lensing or redshift-space-distortion data are used. Code:
`universal/cosmos/` in the swarm-intelligence repository; one command reproduces every number.

## 5. Results

### 5.1 Expansion history (SN + BAO + H(z) + r_d prior)

| Model | χ² | k | ΔAIC | ΔBIC | Ω_m | H0 (km/s/Mpc) | Extra parameters | w(0), w(1) |
| :-- | --: | --: | --: | --: | --: | --: | :-- | :-- |
| ΛCDM | 1406.2 | 3 | 0 | 0 | 0.305 ± 0.008 | 68.6 ± 0.5 | none | −1, −1 |
| SU-A = wCDM | 1401.5 | 4 | −2.7 | +2.7 | 0.298 ± 0.009 | 67.8 ± 0.6 | w = −0.91 ± 0.04 | −0.91, −0.91 |
| w0waCDM (CPL) | 1401.3 | 5 | −0.9 | +9.9 | 0.305 ± 0.016 | 67.7 ± 0.6 | w0 = −0.89 ± 0.06, wa = −0.20 ± 0.43 | −0.89, −0.99 |
| SU-B quorum emergence | 1400.7 | 5 | −1.5 | +9.3 | 0.328 ± 0.009 | 68.1 ± 0.5 | a_t = 0.43 ± 0.04, s = 10.7 ± 3.7 | −1.00, −1.63 |
| SU-C regulated overshoot | 1399.3 | 6 | −0.9 | +15.2 | 0.307 ± 0.009 | 67.8 ± 0.6 | a_on = 0.15 ± 0.04, ω = 6.8 ± 1.3, ζ = 0.25 ± 0.04 | −1.01, −1.27 |

Without the r_d prior the χ² values and parameters are almost the same (see `results/universal/cosmology.md`).

1. **Fit quality.** Every swarm model lowers χ² by 4.7 to 6.9 relative to ΛCDM. Most of the gain comes
   from the BAO data (χ²_BAO 11.0 for ΛCDM, 7.9 for SU-B, 6.2 for SU-C); the supernova χ² barely changes.
2. **Model selection.** AIC differences are below 3, which is not a meaningful preference. BIC prefers
   ΛCDM by 2.7 to 15.2. **The data do not require the swarm mechanism.**
3. **Timing.** SU-B prefers a sharp switch at a ≈ 0.43 (z ≈ 1.3), roughly when massive clusters begin to
   assemble. This is the kind of timing a quorum picture predicts, but it coincides with the redshift
   range where SN and BAO data are densest, so it may reflect the data rather than physics.
4. **Overshoot.** SU-C prefers an underdamped regulator (ζ ≈ 0.25) oscillating about once per e-fold.
   With three extra parameters and a gain of 6.9 in χ², this is consistent with fitting noise.
5. **Hubble tension.** All models give H0 between 67.7 and 68.6 km/s/Mpc, 4.3 to 4.4σ below the
   distance-ladder value of 73.04 ± 1.04 (Riess et al. 2022). Late-time regulation does not resolve it.

### 5.2 Galaxy scale

| Law | g† (m/s²) | rms scatter (dex) | Mean bias at g_bar < 10⁻¹¹ (dex) |
| :-- | --: | --: | --: |
| Newtonian, visible matter only | none | 0.51 | +0.72 |
| Radial acceleration relation (McGaugh et al. 2016) | 1.16 × 10⁻¹⁰ | 0.133 | −0.01 |
| Local pull plus collective floor, g = g_bar + √(g_bar g†) | 7.6 × 10⁻¹¹ | 0.138 | +0.03 |

g† is 1.09 times cH0/2π (with H0 = 68.6) and 1.04 times cH0/6, the scale in Verlinde (2017). A swarm
reading is that galaxies follow a local rule with one global switch scale. The same data are fitted
equally well by MOND and are reproduced, with feedback, by ΛCDM galaxy-formation simulations; this
result does not discriminate between them.

## 6. Comparison with other models

| Model | Relation to the swarm universe |
| :-- | :-- |
| ΛCDM | Same early universe and gravity; differs only in the late-time vacuum term. Preferred by BIC. |
| Inflation | Required: alignment needs causal contact, so the model cannot explain CMB uniformity on its own. |
| Steady state | Shares "self-maintenance"; already ruled out by the CMB and evolution of sources. |
| Cyclic, ekpyrotic, conformal cyclic, bounce | Share self-renewal; the swarm model works within one expansion and says nothing about the beginning. |
| Quintessence | Also dynamical; a single minimally coupled field cannot cross w = −1, which SU-C does. |
| Holographic and running-vacuum DE | Tie DE to a global scale (horizon, H²); the swarm model ties it to the bound fraction. |
| Unimodular gravity, vacuum sequestering | Fix Λ globally; the swarm model makes it local and dynamical. |
| Backreaction (Buchert) | Same averaging equations; the swarm model does not rely on Q_D being large. |
| MOND, emergent gravity | Share a single acceleration scale; the swarm model keeps GR and dark matter. |
| Cosmological natural selection | Shares a population view; not used in the fitted model. |

## 7. Observations that contradict or limit the model

* **CMB uniformity across causally disconnected regions.** Alignment cannot act outside the horizon; an
  early phase of inflation or a bounce is still needed.
* **Bullet Cluster and cluster lensing.** Any version without dark matter fails; the model keeps it.
* **Value of Λ.** The set point Λ* is an input, so the fine-tuning problem is unchanged.
* **Hubble tension.** Not reduced.
* **Energy conditions.** SU-B and the rising part of SU-C are phantom; a microphysical realisation must
  avoid ghost instabilities, and none is given here.
* **Degeneracy.** SU-A is exactly wCDM; SU-B and SU-C are dark-energy parametrisations, so a good fit does
  not demonstrate a swarm mechanism.

## 8. Tests that could rule it out

1. **w(z) at percent precision.** If DESI DR3, Euclid and Rubin find w = −1 at all redshifts, SU-B and
   SU-C are excluded.
2. **Environment dependence.** If the vacuum term is triggered by local structure, supernova Hubble
   residuals should differ between deep voids and dense regions beyond peculiar-velocity effects.
3. **Growth.** A structure-triggered vacuum predicts a specific relation between fσ8(z) and the switch
   redshift; redshift-space-distortion data can test it.
4. **Evolving acceleration scale.** If the galaxy-scale floor is set globally, g† should scale with H(z);
   rotation curves at z ≈ 1 to 2 can test this.

## 9. Conclusion

A self-regulating, decentralised-swarm description of dark energy can be written in closed form,
reduces to ΛCDM in a limit, and fits current supernova, BAO and H(z) data as well as ΛCDM. It is not
preferred once its extra parameters are counted, and it does not address the Hubble tension, the value
of Λ or the initial conditions. Its usefulness is as a source of specific, falsifiable dark-energy
histories (a structure-timed switch and an overshoot) that upcoming surveys can confirm or exclude.

## Acknowledgements

Built with Claude, Claude Code, Antigravity and Gemini. All errors are the author's.

## Data and code availability

All data are public (licences in `universal/sources.yaml`). Code: `universal/` in
github.com/nihalunfc/swarm-intelligence (MIT). Reproduce with `python -m universal.fetch`,
`python -m universal.cosmos.fit` and `python -m universal.cosmos.rar`.

## References

* Ballerini, M. et al. 2008, PNAS 105, 1232. Interaction ruling animal collective behavior depends on topological rather than metric distance.
* Brout, D. et al. 2022, ApJ 938, 110. The Pantheon+ analysis: cosmological constraints.
* Buchert, T. 2000, Gen. Rel. Grav. 32, 105. On average properties of inhomogeneous fluids in general relativity: dust cosmologies.
* Couzin, I. D. et al. 2002, J. Theor. Biol. 218, 1. Collective memory and spatial sorting in animal groups.
* DESI Collaboration 2025, arXiv:2503.14738. DESI DR2 results II: measurements of baryon acoustic oscillations and cosmological constraints.
* Lelli, F., McGaugh, S. S. & Schombert, J. M. 2016, AJ 152, 157. SPARC: mass models for 175 disk galaxies.
* McGaugh, S. S., Lelli, F. & Schombert, J. M. 2016, PRL 117, 201101. Radial acceleration relation in rotationally supported galaxies.
* Moresco, M. et al. 2012, JCAP 08, 006; Moresco, M. 2015, MNRAS 450, L16; Moresco, M. et al. 2016, JCAP 05, 014. Cosmic chronometers.
* Planck Collaboration 2020, A&A 641, A6. Planck 2018 results VI: cosmological parameters.
* Riess, A. G. et al. 2022, ApJL 934, L7. A comprehensive measurement of the local value of the Hubble constant.
* Scolnic, D. et al. 2022, ApJ 938, 113. The Pantheon+ analysis: the full data set and light-curve release.
* Smolin, L. 1992, Class. Quantum Grav. 9, 173. Did the universe evolve?
* Verlinde, E. 2017, SciPost Phys. 2, 016. Emergent gravity and the dark universe.
* Vicsek, T. et al. 1995, PRL 75, 1226. Novel type of phase transition in a system of self-driven particles.
