"""Coarse-grain animals into density and velocity fields, then fit a Toner-Tu-like equation.

Stages 4 and 5 of the study.

Coarse-graining: each animal is spread over a Gaussian of width `sigma`. This gives
density rho(x, t) and momentum density p = rho v. With this choice the continuity equation
d rho/dt + div(p) = 0 holds by construction, which we use as a check of the pipeline.

Equation fit: the flock's acceleration field Dv/dt is regressed on a library of candidate terms (the Toner-Tu terms
plus a few extra ones) with sequentially thresholded least squares (the SINDy method),
which keeps only the terms that matter. Fit on the first half of the recording, score on
the second half.
"""

from __future__ import annotations

import numpy as np

from .io import Tracks
from .kinematics import derivatives

TERMS_2D = [
    ("v", "alpha: drive to cruise"),
    ("|v|^2 v", "beta: speed saturation"),
    ("(v.grad)v", "lambda1: self-advection"),
    ("(div v) v", "lambda2"),
    ("grad |v|^2", "lambda3"),
    ("grad rho", "pressure, P ~ rho"),
    ("rho grad rho", "pressure, P ~ rho^2"),
    ("grad div v", "D_L: bulk viscosity"),
    ("lap v", "D_1: shear viscosity"),
    ("rho v", "density-dependent alignment"),
]


def coarse_grain(x: np.ndarray, v: np.ndarray, grid: tuple[np.ndarray, np.ndarray], sigma: float):
    """Density (per m^2) and velocity on a 2D grid for one frame. x, v: (N, 2)."""
    gx, gy = grid
    ok = np.isfinite(x).all(-1) & np.isfinite(v).all(-1)
    x, v = x[ok], v[ok]
    dx = gx[None, :, :] - x[:, 0, None, None]
    dy = gy[None, :, :] - x[:, 1, None, None]
    k = np.exp(-(dx ** 2 + dy ** 2) / (2 * sigma ** 2)) / (2 * np.pi * sigma ** 2)
    rho = k.sum(0)
    p = np.stack([(k * v[:, 0, None, None]).sum(0), (k * v[:, 1, None, None]).sum(0)], axis=-1)
    return rho, p


def _grad(f, h):
    gx = np.gradient(f, h, axis=0)
    gy = np.gradient(f, h, axis=1)
    return gx, gy


def library(rho, vel, h):
    """Candidate terms (each (X, Y, 2)) at one time, for 2D fields."""
    vx, vy = vel[..., 0], vel[..., 1]
    vxx, vxy = _grad(vx, h)
    vyx, vyy = _grad(vy, h)
    div = vxx + vyy
    sp2 = vx ** 2 + vy ** 2
    s2x, s2y = _grad(sp2, h)
    rx, ry = _grad(rho, h)
    dvx, dvy = _grad(div, h)
    lap_x = np.gradient(vxx, h, axis=0) + np.gradient(vxy, h, axis=1)
    lap_y = np.gradient(vyx, h, axis=0) + np.gradient(vyy, h, axis=1)
    adv_x = vx * vxx + vy * vxy
    adv_y = vx * vyx + vy * vyy
    terms = [
        (vx, vy), (sp2 * vx, sp2 * vy), (adv_x, adv_y), (div * vx, div * vy), (s2x, s2y),
        (rx, ry), (rho * rx, rho * ry), (dvx, dvy), (lap_x, lap_y), (rho * vx, rho * vy),
    ]
    return np.stack([np.stack(t, axis=-1) for t in terms], axis=-1)   # (X, Y, 2, n_terms)


def stlsq(A, b, threshold=0.05, iters=10):
    """Sequentially thresholded least squares on standardised columns."""
    scale = np.sqrt((A ** 2).mean(0))
    scale[scale == 0] = 1
    As = A / scale
    c, *_ = np.linalg.lstsq(As, b, rcond=None)
    for _ in range(iters):
        small = np.abs(c) < threshold * np.abs(c).max()
        c[small] = 0
        big = ~small
        if big.sum() == 0:
            break
        c[big], *_ = np.linalg.lstsq(As[:, big], b, rcond=None)
    return c / scale


def build_samples(tr: Tracks, sigma_bl=2.0, cell_bl=1.0, smooth_s=0.5, rho_min_per_bl2=0.05,
                  max_frames=3000, pad_bl=2.0, check_dt_s=0.1):
    """Library matrix A and target b = coarse-grained acceleration (stacked x, y components).

    The target is the kernel-weighted mean acceleration of the animals near each grid cell,
    i.e. the material derivative Dv/dt = dv/dt + (v.grad)v of the flock. Using the animals'
    own accelerations avoids the edge effects of differentiating a sparse field in time.
    If the flock behaved like an ordinary fluid, the (v.grad)v coefficient would come out
    near 1; Toner-Tu theory allows it to differ from 1 (lambda1 != 1).
    """
    if tr.D != 2:
        raise NotImplementedError("3D fields come with the bird data")
    bl = tr.body_length or 1.0
    sigma, h = sigma_bl * bl, cell_bl * bl
    x, v, acc = derivatives(tr, window_s=smooth_s)
    lo = np.nanmin(x.reshape(-1, 2), axis=0) - pad_bl * bl
    hi = np.nanmax(x.reshape(-1, 2), axis=0) + pad_bl * bl
    gx, gy = np.meshgrid(np.arange(lo[0], hi[0], h), np.arange(lo[1], hi[1], h), indexing="ij")
    step = max(1, int(round(check_dt_s / tr.dt)))
    ts = np.arange(step, tr.T - step, step)
    if len(ts) > max_frames:
        ts = ts[np.linspace(0, len(ts) - 1, max_frames).astype(int)]
    rho_min = rho_min_per_bl2 / bl ** 2
    A_rows, b_rows, t_rows = [], [], []
    cont_num = cont_den = 0.0
    for t in ts:
        r1, p1 = coarse_grain(x[t], v[t], (gx, gy), sigma)
        _, pa = coarse_grain(x[t], acc[t], (gx, gy), sigma)
        # continuity check: d rho/dt + div(rho v) should be ~0
        r0, _ = coarse_grain(x[t - step], v[t - step], (gx, gy), sigma)
        r2_, _ = coarse_grain(x[t + step], v[t + step], (gx, gy), sigma)
        drho = (r2_ - r0) / (2 * step * tr.dt)
        divp = np.gradient(p1[..., 0], h, axis=0) + np.gradient(p1[..., 1], h, axis=1)
        inner = r1 > rho_min
        cont_num += np.sum((drho + divp)[inner] ** 2)
        cont_den += np.sum(drho[inner] ** 2)
        with np.errstate(invalid="ignore", divide="ignore"):
            vel = p1 / r1[..., None]
            target = pa / r1[..., None]
        lib = library(r1, np.nan_to_num(vel), h)
        dense = r1 > rho_min
        m = dense.copy()
        m[:2, :] = m[-2:, :] = False
        m[:, :2] = m[:, -2:] = False
        for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)):
            m &= np.roll(dense, (sx, sy), axis=(0, 1))      # derivative stencil stays inside the flock
        if not m.any():
            continue
        A_rows.append(lib[m].reshape(-1, lib.shape[-1]))
        b_rows.append(target[m].reshape(-1))
        t_rows.append(np.full(m.sum() * 2, t))
    A = np.concatenate(A_rows)
    b = np.concatenate(b_rows)
    tt = np.concatenate(t_rows)
    ok = np.isfinite(A).all(1) & np.isfinite(b)
    return A[ok], b[ok], tt[ok], {"continuity_residual_fraction": float(cont_num / max(cont_den, 1e-30)),
                                  "grid_cells": int(gx.size), "frames_used": int(len(ts)),
                                  "sigma_m": sigma, "cell_m": h, "smooth_s": smooth_s}


def fit_equation(tr: Tracks, threshold=0.1, **kw) -> dict:
    A, b, tt, info = build_samples(tr, **kw)
    split = np.median(tt)
    tr_m, te_m = tt <= split, tt > split

    def r2(c, m):
        res = b[m] - A[m] @ c
        return float(1 - np.sum(res ** 2) / np.sum((b[m] - b[m].mean()) ** 2))

    full, *_ = np.linalg.lstsq(A[tr_m], b[tr_m], rcond=None)
    sparse = stlsq(A[tr_m], b[tr_m], threshold=threshold)
    # term importance: drop each kept term and see how much held-out R^2 falls
    importance = {}
    base = r2(sparse, te_m)
    for j in np.nonzero(sparse)[0]:
        keep = np.nonzero(sparse)[0]
        keep = keep[keep != j]
        c = np.zeros_like(sparse)
        if len(keep):
            c[keep], *_ = np.linalg.lstsq(A[tr_m][:, keep], b[tr_m], rcond=None)
        importance[TERMS_2D[j][0]] = base - r2(c, te_m)
    single = {}
    for j, (name, _) in enumerate(TERMS_2D):
        cj, *_ = np.linalg.lstsq(A[tr_m][:, [j]], b[tr_m], rcond=None)
        c = np.zeros(A.shape[1])
        c[j] = cj[0]
        single[name] = r2(c, te_m)
    return {
        **info,
        "samples": int(len(b)),
        "single_term_r2_test": single,
        "terms": [t for t, _ in TERMS_2D],
        "term_meaning": {t: m for t, m in TERMS_2D},
        "coef_full": dict(zip([t for t, _ in TERMS_2D], map(float, full))),
        "r2_test_full": r2(full, te_m),
        "coef_sparse": {t: float(c) for (t, _), c in zip(TERMS_2D, sparse) if c != 0},
        "r2_test_sparse": base,
        "drop_one_r2_loss": importance,
    }
