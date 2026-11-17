"""Chimney swifts at the roost (Evangelista et al. 2017): the large-flock test of the fluid equation.

The files hold hundreds of birds per frame (29.97 fps) as they circle and drop into a
chimney at (x, y, z) = (0.6, 14.5, 2.6) m. Data are stored frame by frame, so instead of a
dense (T, N, D) array this module works on sampled frames and matches track ids between
frames to get accelerations.

The field fit is done on the horizontal plane (x, y): the birds circle around the
chimney, so the main flow is horizontal. Vertical motion is ignored in this first pass.
"""

from __future__ import annotations

from pathlib import Path

import h5py
import numpy as np

from .fields import TERMS_2D, coarse_grain, library, stlsq

FPS = 29.97
CHIMNEY = np.array([0.6, 14.5, 2.6])
BODY_LENGTH = 0.13   # approximate chimney swift length (field-guide value, not from the paper)


def _frame(f, key):
    g = f[key]
    return (g["tid"][:].astype(np.int64), np.stack([g["x"][:], g["y"][:], g["z"][:]], -1).astype(float),
            np.stack([g["vx"][:], g["vy"][:], g["vz"][:]], -1).astype(float))


def sampled_frames(path: Path, every: int = 15, gap: int = 2):
    """Yield (tid, x, v, a) for every `every`-th frame; a from velocity at +-gap frames."""
    with h5py.File(path, "r") as f:
        keys = sorted(f.keys(), key=int)
        for i in range(gap, len(keys) - gap, every):
            t0, x0, v0 = _frame(f, keys[i])
            tm, _, vm = _frame(f, keys[i - gap])
            tp, _, vp = _frame(f, keys[i + gap])
            im = {t: j for j, t in enumerate(tm)}
            ip = {t: j for j, t in enumerate(tp)}
            a = np.full_like(v0, np.nan)
            for j, t in enumerate(t0):
                if t in im and t in ip:
                    a[j] = (vp[ip[t]] - vm[im[t]]) / (2 * gap / FPS)
            yield int(keys[i]), t0, x0, v0, a


def plausible(x, v, vmin=2.0, vmax=25.0):
    """Drop likely ghost tracks (README: unrealistically slow or fast birds)."""
    s = np.linalg.norm(v, axis=-1)
    return np.isfinite(x).all(-1) & (s > vmin) & (s < vmax)


def summary_and_samples(paths: list[Path], every: int = 15):
    rows = []
    frames = []
    for p in paths:
        for key, _tid, x, v, a in sampled_frames(p, every=every):
            ok = plausible(x, v)
            x, v, a = x[ok], v[ok], a[ok]
            if len(x) < 10:
                continue
            u = v / np.linalg.norm(v, axis=-1, keepdims=True)
            d = np.linalg.norm(x[:, None] - x[None], axis=-1)
            np.fill_diagonal(d, np.inf)
            nn = d.min(1)
            # rotation about the vertical axis through the chimney (milling around the roost)
            r = x[:, :2] - CHIMNEY[:2]
            rh = r / np.linalg.norm(r, axis=-1, keepdims=True)
            uh = v[:, :2] / np.linalg.norm(v[:, :2], axis=-1, keepdims=True)
            mill = float(np.mean(rh[:, 0] * uh[:, 1] - rh[:, 1] * uh[:, 0]))
            rows.append({"file": p.name, "frame": key, "birds": int(len(x)),
                         "speed": float(np.median(np.linalg.norm(v, axis=-1))),
                         "nn": float(np.median(nn)), "polarisation": float(np.linalg.norm(u.mean(0))),
                         "milling_about_chimney": mill})
            frames.append((x, v, a))
    return rows, frames


ROOST_TERMS = [("toward roost", "new: pull toward the chimney (horizontal unit vector)"),
               ("around roost", "new: circling around the chimney (tangential unit vector)")]


def fit_equation_swifts(frames, sigma: float, cell: float, rho_min: float, threshold: float = 0.1,
                        roost_terms: bool = True) -> dict:
    """Sparse Toner-Tu fit on the horizontal plane, target = coarse-grained horizontal acceleration.

    With roost_terms, two candidate new terms are added: a pull toward the chimney and a
    circling term around it. They are kept only if they improve the held-out fit.
    """
    names = list(TERMS_2D) + (ROOST_TERMS if roost_terms else [])
    A_rows, b_rows, t_rows = [], [], []
    allx = np.concatenate([f[0][:, :2] for f in frames])
    lo, hi = np.percentile(allx, 1, axis=0) - 2 * sigma, np.percentile(allx, 99, axis=0) + 2 * sigma
    gx, gy = np.meshgrid(np.arange(lo[0], hi[0], cell), np.arange(lo[1], hi[1], cell), indexing="ij")
    rx, ry = CHIMNEY[0] - gx, CHIMNEY[1] - gy
    rn = np.hypot(rx, ry) + 1e-9
    toward = np.stack([rx / rn, ry / rn], -1)
    around = np.stack([-ry / rn, rx / rn], -1)
    extra = np.stack([toward, around], -1)
    for i, (x, v, a) in enumerate(frames):
        ok = np.isfinite(a).all(-1)
        x2, v2, a2 = x[ok, :2], v[ok, :2], a[ok, :2]
        if len(x2) < 20:
            continue
        rho, p = coarse_grain(x2, v2, (gx, gy), sigma)
        _, pa = coarse_grain(x2, a2, (gx, gy), sigma)
        with np.errstate(invalid="ignore", divide="ignore"):
            vel = p / rho[..., None]
            acc = pa / rho[..., None]
        lib = library(rho, np.nan_to_num(vel), cell)
        if roost_terms:
            lib = np.concatenate([lib, extra], axis=-1)
        dense = rho > rho_min
        m = dense.copy()
        m[:2, :] = m[-2:, :] = False
        m[:, :2] = m[:, -2:] = False
        for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)):
            m &= np.roll(dense, (sx, sy), axis=(0, 1))
        if not m.any():
            continue
        A_rows.append(lib[m].reshape(-1, lib.shape[-1]))
        b_rows.append(acc[m].reshape(-1))
        t_rows.append(np.full(m.sum() * 2, i))
    A, b, tt = np.concatenate(A_rows), np.concatenate(b_rows), np.concatenate(t_rows)
    ok = np.isfinite(A).all(1) & np.isfinite(b)
    A, b, tt = A[ok], b[ok], tt[ok]
    split = np.median(tt)
    tr_m, te_m = tt <= split, tt > split

    def r2(c, m):
        res = b[m] - A[m] @ c
        return float(1 - np.sum(res ** 2) / np.sum((b[m] - b[m].mean()) ** 2))

    full, *_ = np.linalg.lstsq(A[tr_m], b[tr_m], rcond=None)
    sparse = stlsq(A[tr_m], b[tr_m], threshold=threshold)
    single = {}
    for j, (name, _) in enumerate(names):
        cj, *_ = np.linalg.lstsq(A[tr_m][:, [j]], b[tr_m], rcond=None)
        c = np.zeros(A.shape[1])
        c[j] = cj[0]
        single[name] = r2(c, te_m)
    return {"samples": int(len(b)), "sigma_m": sigma, "cell_m": cell,
            "terms": [t for t, _ in names], "term_meaning": dict(names),
            "r2_test_full": r2(full, te_m), "r2_test_sparse": r2(sparse, te_m),
            "coef_sparse": {t: float(c) for (t, _), c in zip(names, sparse) if c != 0},
            "single_term_r2_test": single}


# ---------------------------------------------------------------- 3D fit

TERMS_3D = [
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
    ("z-hat", "new: constant vertical pull (gravity, descent to roost)"),
]


def coarse_grain_nd(x, v, grids, sigma):
    """Gaussian coarse-graining in any dimension. x, v: (N, D); grids: list of D arrays of the same shape."""
    D = x.shape[1]
    shape = grids[0].shape
    rho = np.zeros(shape)
    p = np.zeros(shape + (D,))
    norm = (2 * np.pi * sigma ** 2) ** (D / 2)
    for xi, vi in zip(x, v):
        r2 = sum((g - c) ** 2 for g, c in zip(grids, xi))
        k = np.exp(-r2 / (2 * sigma ** 2)) / norm
        rho += k
        p += k[..., None] * vi
    return rho, p


def library_nd(rho, vel, h):
    D = vel.shape[-1]
    ax = range(D)
    grad = lambda f: np.stack([np.gradient(f, h, axis=a) for a in ax], -1)  # noqa: E731
    J = np.stack([grad(vel[..., i]) for i in ax], -2)            # J[..., i, j] = d v_i / d x_j
    div = np.trace(J, axis1=-2, axis2=-1)
    sp2 = np.sum(vel ** 2, -1)
    adv = np.einsum("...ij,...j->...i", J, vel)
    lap = np.stack([sum(np.gradient(J[..., i, j], h, axis=j) for j in ax) for i in ax], -1)
    zhat = np.zeros_like(vel)
    zhat[..., -1] = 1.0
    terms = [vel, sp2[..., None] * vel, adv, div[..., None] * vel, grad(sp2), grad(rho),
             rho[..., None] * grad(rho), grad(div), lap, rho[..., None] * vel, zhat]
    return np.stack(terms, -1)                                     # (..., D, n_terms)


def fit_equation_swifts_3d(frames, sigma, cell, rho_min, threshold=0.1, max_frames=1200):
    allx = np.concatenate([f[0] for f in frames])
    lo = np.percentile(allx, 2, axis=0) - sigma
    hi = np.percentile(allx, 98, axis=0) + sigma
    axes = [np.arange(lo[d], hi[d], cell) for d in range(3)]
    grids = np.meshgrid(*axes, indexing="ij")
    idx = np.linspace(0, len(frames) - 1, min(max_frames, len(frames))).astype(int)
    A_rows, b_rows, t_rows = [], [], []
    for i in idx:
        x, v, a = frames[i]
        ok = np.isfinite(a).all(-1)
        inside = ((x >= lo) & (x <= hi)).all(-1)
        x3, v3, a3 = x[ok & inside], v[ok & inside], a[ok & inside]
        if len(x3) < 20:
            continue
        rho, p = coarse_grain_nd(x3, v3, grids, sigma)
        _, pa = coarse_grain_nd(x3, a3, grids, sigma)
        with np.errstate(invalid="ignore", divide="ignore"):
            vel = p / rho[..., None]
            acc = pa / rho[..., None]
        lib = library_nd(rho, np.nan_to_num(vel), cell)
        dense = rho > rho_min
        m = dense.copy()
        for d in range(3):
            sl = [slice(None)] * 3
            sl[d] = slice(0, 2)
            m[tuple(sl)] = False
            sl[d] = slice(-2, None)
            m[tuple(sl)] = False
            for s in (1, -1, 2, -2):
                m &= np.roll(dense, s, axis=d)
        if not m.any():
            continue
        A_rows.append(lib[m].reshape(-1, lib.shape[-1]))
        b_rows.append(acc[m].reshape(-1))
        t_rows.append(np.full(m.sum() * 3, i))
    A, b, tt = np.concatenate(A_rows), np.concatenate(b_rows), np.concatenate(t_rows)
    ok = np.isfinite(A).all(1) & np.isfinite(b)
    A, b, tt = A[ok], b[ok], tt[ok]
    split = np.median(tt)
    tr_m, te_m = tt <= split, tt > split

    def r2(c, m):
        res = b[m] - A[m] @ c
        return float(1 - np.sum(res ** 2) / np.sum((b[m] - b[m].mean()) ** 2))

    out = {"samples": int(len(b)), "sigma_m": sigma, "cell_m": cell, "grid": [len(a_) for a_ in axes],
           "terms": [t for t, _ in TERMS_3D], "term_meaning": dict(TERMS_3D)}
    for name, cols in (("without z-hat", list(range(len(TERMS_3D) - 1))), ("with z-hat", list(range(len(TERMS_3D))))):
        As = A[:, cols]
        full, *_ = np.linalg.lstsq(As[tr_m], b[tr_m], rcond=None)
        sp = stlsq(As[tr_m], b[tr_m], threshold=threshold)
        cf = np.zeros(A.shape[1])
        cs = np.zeros(A.shape[1])
        cf[cols], cs[cols] = full, sp
        out[name] = {"r2_test_full": r2(cf, te_m), "r2_test_sparse": r2(cs, te_m),
                     "coef_sparse": {TERMS_3D[j][0]: float(cs[j]) for j in cols if cs[j] != 0}}
    return out
