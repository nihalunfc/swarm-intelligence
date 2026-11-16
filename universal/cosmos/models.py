"""Background expansion for LCDM, two standard extensions and three swarm-universe (SU) models.

Every model is flat and has matter, radiation and a dark-energy (DE) term whose density,
relative to today, is f(a). E(z)^2 = H(z)^2/H0^2 = Om (1+z)^3 + Or (1+z)^4 + (1 - Om - Or) f(a).

SU models (speculative; see docs/universal-swarm/swarm-universe-theory.md):

* SU-A "homeostatic vacuum": first-order feedback dρ_DE/dN = -k (ρ_DE - eps ρ_m). Its solution is
  exactly wCDM with w = k/3 - 1 plus a rescaling of matter, so it is fitted as wCDM.
* SU-B "quorum emergence": the vacuum term switches on as structure forms, like a swarm reaching
  quorum: f(a) = (1 + a_t^s) / (1 + (a_t/a)^s). s -> 0 or a_t -> 0 gives LCDM.
* SU-C "regulated overshoot": a second-order regulator in N = ln a, switched on at a_on, drives the
  vacuum to its set point with damping zeta and frequency omega, so it overshoots and relaxes,
  like the damped oscillations seen in many natural swarms. zeta -> 1 and large omega gives LCDM.
"""
from __future__ import annotations

import numpy as np

C_KMS = 299792.458


def omega_r(h: float) -> float:
    # photons + 3.046 massless neutrinos, T_cmb = 2.7255 K
    return 2.469e-5 / h**2 * (1 + 0.2271 * 3.046)


def f_lcdm(a, p):
    return np.ones_like(a)


def f_wcdm(a, p):
    return a ** (-3 * (1 + p["w"]))


def f_cpl(a, p):
    w0, wa = p["w0"], p["wa"]
    return a ** (-3 * (1 + w0 + wa)) * np.exp(-3 * wa * (1 - a))


def f_su_quorum(a, p):
    at, s = p["a_t"], p["s"]
    return (1 + at**s) / (1 + (at / a) ** s)


def _regulator(n, omega, zeta):
    zeta = np.clip(zeta, 1e-3, 0.999)
    wd = omega * np.sqrt(1 - zeta**2)
    g = 1 - np.exp(-zeta * omega * n) * (np.cos(wd * n) + zeta * omega / wd * np.sin(wd * n))
    return np.where(n > 0, g, 0.0)


def f_su_overshoot(a, p):
    n = np.log(a) - np.log(p["a_on"])
    g = _regulator(n, p["omega"], p["zeta"])
    g0 = _regulator(np.array(-np.log(p["a_on"])), p["omega"], p["zeta"])
    return np.maximum(g / max(float(g0), 1e-6), 0.0)


MODELS = {
    "LCDM": {"f": f_lcdm, "params": {}, "bounds": {}},
    "wCDM (= SU-A homeostatic vacuum)": {"f": f_wcdm, "params": {"w": -1.0}, "bounds": {"w": (-2.0, -0.3)}},
    "w0waCDM (CPL)": {"f": f_cpl, "params": {"w0": -1.0, "wa": 0.0}, "bounds": {"w0": (-2.0, 0.0), "wa": (-3.0, 2.0)}},
    "SU-B quorum emergence": {"f": f_su_quorum, "params": {"a_t": 0.3, "s": 2.0},
                              "bounds": {"a_t": (0.01, 1.5), "s": (0.05, 12.0)}},
    "SU-C regulated overshoot": {"f": f_su_overshoot, "params": {"a_on": 0.2, "omega": 4.0, "zeta": 0.5},
                                 "bounds": {"a_on": (0.02, 0.8), "omega": (0.3, 15.0), "zeta": (0.05, 0.99)}},
}


def E(z, Om, h, model, p):
    a = 1.0 / (1.0 + np.asarray(z, float))
    Or = omega_r(h)
    return np.sqrt(Om * a**-3 + Or * a**-4 + (1 - Om - Or) * MODELS[model]["f"](a, p))


def comoving(z, Om, h, model, p, n=2048):
    """Comoving distance in Mpc, by trapezoid integration on a grid up to max(z)."""
    z = np.atleast_1d(np.asarray(z, float))
    zg = np.linspace(0, max(z.max(), 1e-6), n)
    inv = 1.0 / E(zg, Om, h, model, p)
    cum = np.concatenate([[0], np.cumsum(0.5 * (inv[1:] + inv[:-1]) * np.diff(zg))])
    return C_KMS / (100 * h) * np.interp(z, zg, cum)


def w_eff(z, model, p):
    """Equation of state of the DE term: w = -1 - (1/3) dln f / dln a."""
    a = 1.0 / (1.0 + np.asarray(z, float))
    f = MODELS[model]["f"]
    eps = 1e-4
    lf1 = np.log(np.maximum(f(a * np.exp(eps), p), 1e-300))
    lf0 = np.log(np.maximum(f(a * np.exp(-eps), p), 1e-300))
    return -1 - (lf1 - lf0) / (2 * eps) / 3
