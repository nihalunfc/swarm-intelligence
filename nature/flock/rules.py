"""Measure the local interaction rules from real tracks (stage 3 of the study).

Two measurements:

1. Topological versus metric neighbours. For each animal we predict how its heading
   turns over the next 0.3 s from (a) the mean heading of its neighbours and (b) the
   direction to their centre. Neighbours are either the k nearest (topological) or all within
   radius r (metric). The fit is made on the first half of the recording and scored on the
   second half, so the better neighbour rule is the one that predicts unseen data better.

2. Distance response. The acceleration of an animal along the line to each neighbour,
   averaged by distance. Negative = moves away (repulsion), positive = moves closer
   (attraction). The zero crossing is the preferred spacing.
"""

from __future__ import annotations

import numpy as np

from .io import Tracks
from .kinematics import derivatives, nearest_neighbour_distance, unit


def _chunk(N: int, D: int, budget: float = 2e7) -> int:
    """Frames per batch so the (frames, N, N, D) pair arrays stay around 160 MB."""
    return max(1, int(budget / (N * N * D)))


def _perp(vec: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Component of vec perpendicular to unit vector u."""
    return vec - np.sum(vec * u, axis=-1, keepdims=True) * u


def _features(x, u, lag, mask_fn):
    """Features (neighbour heading, direction to neighbour centre) and target (heading change after `lag` steps).

    All three are taken perpendicular to the focal animal's own heading, so they describe turning only.
    """
    T, N, D = x.shape
    T = T - lag
    chunk = _chunk(N, D)
    feats, targets = [], []
    for t0 in range(0, T, chunk):
        t1 = min(T, t0 + chunk)
        xs, us, uf = x[t0:t1], u[t0:t1], u[t0 + lag:t1 + lag]
        off = xs[:, None, :, :] - xs[:, :, None, :]          # off[t,i,j] = x_j - x_i
        dist = np.linalg.norm(off, axis=-1)
        idx = np.arange(N)
        dist[:, idx, idx] = np.inf
        dist = np.where(np.isnan(dist), np.inf, dist)
        m = mask_fn(dist) & np.isfinite(dist)               # (t, i, j) neighbour set
        cnt = m.sum(axis=2, keepdims=True)
        w = m / np.where(cnt > 0, cnt, 1)
        mean_u = np.einsum("tij,tjd->tid", w, np.nan_to_num(us))
        mean_off = np.einsum("tij,tijd->tid", w, np.nan_to_num(off))
        f_align = _perp(mean_u, us)
        f_centre = _perp(unit(mean_off), us)
        y = _perp(uf, us)
        ok = (cnt[..., 0] > 0) & np.isfinite(y).all(-1) & np.isfinite(f_align).all(-1) & np.isfinite(f_centre).all(-1)
        feats.append(np.stack([f_align[ok], f_centre[ok]], axis=-1))   # (n, D, 2)
        targets.append(y[ok])                                          # (n, D)
    return np.concatenate(feats).reshape(-1, 2), np.concatenate(targets).reshape(-1)


def _fit_score(x, u, lag, mask_fn):
    """Fit on the first half of the recording, score R^2 on the second half."""
    h = x.shape[0] // 2
    Ftr, Ytr = _features(x[:h], u[:h], lag, mask_fn)
    Fte, Yte = _features(x[h:], u[h:], lag, mask_fn)
    if len(Ytr) < 200 or len(Yte) < 200:      # too few animals with neighbours in range
        return float("nan"), [float("nan"), float("nan")]
    coef, *_ = np.linalg.lstsq(Ftr, Ytr, rcond=None)
    res = Yte - Fte @ coef
    r2 = 1.0 - np.sum(res ** 2) / np.sum((Yte - Yte.mean()) ** 2)
    return float(r2), [float(c) for c in coef]


def auto_stride(tr: Tracks, target_dt: float = 0.1) -> int:
    """Subsample to about 10 frames per second (no subsampling for slower data)."""
    return max(1, int(round(target_dt / tr.dt)))


def topological_vs_metric(tr: Tracks, stride: int | None = None, lag_s: float = 0.3,
                          ks=(1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20),
                          radii_bl=(1, 1.5, 2, 3, 4, 5, 6, 8, 10, 15, 20)) -> dict:
    stride = stride or auto_stride(tr)
    x, v, _ = derivatives(tr)
    x, u = x[::stride], unit(v[::stride])
    lag = max(1, int(round(lag_s / (tr.dt * stride))))
    N = tr.N
    bl = tr.body_length or 1.0
    topo = {}
    for k in ks:
        if k >= N:
            continue

        def mask(dist, k=k):
            return dist <= np.sort(dist, axis=2)[:, :, k - 1:k]
        topo[k] = _fit_score(x, u, lag, mask)
    metric = {}
    for r in radii_bl:
        metric[r] = _fit_score(x, u, lag, lambda dist, rr=r * bl: dist <= rr)
    def score(d, key):
        return d[key][0] if np.isfinite(d[key][0]) else -np.inf
    best_k = max(topo, key=lambda k: score(topo, k))
    best_r = max(metric, key=lambda r: score(metric, r))
    return {
        "lag_s": lag * tr.dt * stride,
        "topological": {str(k): {"r2_test": s, "coef_align_centre": c} for k, (s, c) in topo.items()},
        "metric_bl": {str(r): {"r2_test": s, "coef_align_centre": c} for r, (s, c) in metric.items()},
        "best_k": int(best_k), "best_k_r2": topo[best_k][0],
        "best_radius_bl": float(best_r), "best_radius_r2": metric[best_r][0],
        "winner": ("no signal" if max(topo[best_k][0], metric[best_r][0]) < 0.01
                   else "topological" if topo[best_k][0] > metric[best_r][0] else "metric"),
    }


def distance_response(tr: Tracks, stride: int | None = None, max_bl: float | None = None, bins: int = 32,
                      k: int = 6) -> dict:
    """Mean acceleration toward each of the k nearest neighbours, binned by distance."""
    stride = stride or auto_stride(tr)
    x, v, a = derivatives(tr)
    x, a = x[::stride], a[::stride]
    bl = tr.body_length or 1.0
    if max_bl is None:   # cover about 4 typical nearest-neighbour distances
        max_bl = max(8.0, 4 * float(np.nanmedian(nearest_neighbour_distance(x))) / bl)
    edges = np.linspace(0, max_bl, bins + 1)
    s = np.zeros(bins)
    n = np.zeros(bins)
    N = tr.N
    chunk = _chunk(N, tr.D)
    for t0 in range(0, x.shape[0], chunk):
        xs, as_ = x[t0:t0 + chunk], a[t0:t0 + chunk]
        off = xs[:, None, :, :] - xs[:, :, None, :]
        dist = np.linalg.norm(off, axis=-1)
        idx = np.arange(N)
        dist[:, idx, idx] = np.inf
        dist = np.where(np.isnan(dist), np.inf, dist)
        kk = min(k, N - 1)
        kth = np.sort(dist, axis=2)[:, :, kk - 1:kk]
        m = (dist <= kth) & np.isfinite(dist)
        rhat = off / np.where(dist > 0, dist, np.nan)[..., None]
        proj = np.sum(as_[:, :, None, :] * rhat, axis=-1)    # accel of i along line to j
        ok = m & np.isfinite(proj)
        d_bl = dist[ok] / bl
        b = np.digitize(d_bl, edges) - 1
        good = (b >= 0) & (b < bins)
        np.add.at(s, b[good], proj[ok][good])
        np.add.at(n, b[good], 1)
    mean = np.where(n > 50, s / np.maximum(n, 1), np.nan)
    centres = 0.5 * (edges[1:] + edges[:-1])
    # preferred spacing = first sign change from negative (repulsion) to positive (attraction)
    zero = None
    for i in range(bins - 1):
        if np.isfinite(mean[i]) and np.isfinite(mean[i + 1]) and mean[i] < 0 <= mean[i + 1]:
            zero = float(centres[i] - mean[i] * (centres[i + 1] - centres[i]) / (mean[i + 1] - mean[i]))
            break
    return {"distance_bl": centres.tolist(), "accel_toward_m_s2": [None if not np.isfinite(m) else float(m)
                                                                    for m in mean],
            "counts": n.astype(int).tolist(), "preferred_spacing_bl": zero}
