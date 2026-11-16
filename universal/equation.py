"""The general adaptive swarm equation (GASE) and its fits.

For a collective observable X of a decentralised swarm (cases, area burned, load, flock
speed, number of active users) we write

    dX/dt = r X [1 - (X/K)^theta]  -  kappa (X - X*)  +  F(t)  +  sigma X^gamma xi(t)
            \\___ self-limiting ___/   \\_ set-point _/   forcing   \\_ fluctuation scaling _/
                  growth                 regulation

* growth phase (cumulative curves): the Richards term dominates; theta = 1 is logistic,
  theta -> 0 is Gompertz, theta -> infinity is unlimited exponential growth then a hard cap.
* steady phase (levels): linearise around the set point, dz = (a0 + a1 z + a2 z^2) dt + noise;
  a1 < 0 means the swarm pulls itself back (self-regulation) with rate kappa = -a1.
* gamma is the fluctuation-scaling (Taylor's law) exponent: 0.5 = independent agents,
  1 = fully collective (all agents move together).

At agent level (tracks) the same three ideas are the local rule in ``features``:
alignment (alpha), cohesion (beta) and speed set-point regulation (gamma_speed).
"""
from __future__ import annotations

import warnings

import numpy as np
from scipy.optimize import curve_fit

from .types import Series


def richards(t, K, r, tm, nu):
    return K / np.power(1 + nu * np.exp(-r * (t - tm)), 1 / nu)


def gompertz(t, K, r, tm):
    return K * np.exp(-np.exp(-r * (t - tm)))


def exponential(t, A, r):
    return A * np.exp(r * t)


def _aic(rss, n, k):
    return n * np.log(max(rss, 1e-300) / n) + 2 * k


def fit_growth(s: Series) -> dict:
    """Fit Richards, logistic, Gompertz and exponential to a cumulative curve (scaled to [0, 1])."""
    t = np.asarray(s.t, float)
    x = np.asarray(s.x, float)
    m = np.isfinite(x)
    t, x = t[m], x[m]
    if len(t) < 8 or x.max() <= 0:
        return {}
    first = np.argmax(x > 0.001 * x.max())
    t, x = t[first:], x[first:]
    tt = (t - t[0]) / max(t[-1] - t[0], 1e-12)
    y = x / x.max()
    n = len(y)
    res = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fits = {
            "richards": (richards, [1, 10, 0.5, 1], ([0.1, 0.01, -1, 0.01], [10, 500, 2, 20])),
            "logistic": (lambda t, K, r, tm: richards(t, K, r, tm, 1.0), [1, 10, 0.5], ([0.1, 0.01, -1], [10, 500, 2])),
            "gompertz": (gompertz, [1, 5, 0.3], ([0.1, 0.01, -1], [10, 500, 2])),
            "exponential": (exponential, [0.01, 3], ([1e-9, 0], [10, 200])),
        }
        for name, (f, p0, b) in fits.items():
            try:
                p, _ = curve_fit(f, tt, y, p0=p0, bounds=b, maxfev=20000)
                rss = float(np.sum((y - f(tt, *p)) ** 2))
                res[name] = {"params": [float(v) for v in p], "aic": float(_aic(rss, n, len(p))),
                             "r2": float(1 - rss / np.sum((y - y.mean()) ** 2))}
            except Exception:
                continue
    if not res:
        return {}
    best = min(res, key=lambda k: res[k]["aic"])
    out = {"best": best, "models": res}
    if "richards" in res:
        K, r, tm, nu = res["richards"]["params"]
        out.update(theta=nu, r_scaled=r, saturation=float(y[-1] / K), r2=res["richards"]["r2"])
    return out


def fit_drift(s: Series) -> dict:
    """Langevin drift and fluctuation scaling for a level series."""
    x = np.asarray(s.x, float)
    if s.cumulative:
        x = np.diff(x)
    x = x[np.isfinite(x)]
    if len(x) < 30:
        return {}
    mu, sd = x.mean(), x.std() + 1e-12
    z = (x - mu) / sd
    dz = np.diff(z)
    Z = np.c_[np.ones(len(z) - 1), z[:-1], z[:-1] ** 2]
    coef, *_ = np.linalg.lstsq(Z, dz, rcond=None)
    resid = dz - Z @ coef
    r2 = 1 - np.sum(resid**2) / np.sum((dz - dz.mean()) ** 2)
    a0, a1, a2 = (float(c) for c in coef)
    out = {"a0": a0, "a1": a1, "a2": a2, "drift_r2": float(r2), "kappa": float(-a1)}
    # fixed points of a0 + a1 z + a2 z^2 and their stability
    roots = np.roots([a2, a1, a0]) if abs(a2) > 1e-9 else np.array([-a0 / a1])
    real = [float(r.real) for r in np.atleast_1d(roots) if abs(r.imag) < 1e-9]
    out["fixed_points"] = real
    out["stable_fixed_points"] = [r for r in real if a1 + 2 * a2 * r < 0]
    # fluctuation scaling: |noise| ~ level^gamma on positive levels (Taylor's law)
    lvl = x[:-1]
    pos = lvl > 0
    if pos.sum() > 20 and (x > 0).all():
        e = np.abs(np.diff(x))[pos]
        ok = e > 0
        if ok.sum() > 20:
            g = np.polyfit(np.log(lvl[pos][ok]), np.log(e[ok]), 1)[0]
            out["taylor_gamma"] = float(g)
    return out
