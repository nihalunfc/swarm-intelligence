"""Per-animal and per-group motion measures (stages 2 of the study)."""

from __future__ import annotations

import numpy as np
from scipy.signal import savgol_filter

from .io import Tracks


def fill_short_gaps(pos: np.ndarray, max_gap: int) -> np.ndarray:
    """Linearly fill NaN runs of at most `max_gap` frames per animal; longer gaps stay NaN."""
    out = pos.copy()
    T, N, D = pos.shape
    t = np.arange(T)
    for i in range(N):
        bad = np.isnan(pos[:, i, 0])
        if not bad.any() or bad.all():
            continue
        good = ~bad
        filled = np.stack([np.interp(t, t[good], pos[good, i, d]) for d in range(D)], axis=-1)
        # find run lengths of NaN
        edges = np.diff(np.concatenate([[0], bad.astype(int), [0]]))
        starts, stops = np.where(edges == 1)[0], np.where(edges == -1)[0]
        for a, b in zip(starts, stops):
            if b - a <= max_gap and a > 0 and b < T:
                out[a:b, i] = filled[a:b]
    return out


def derivatives(tr: Tracks, window_s: float = 0.2, poly: int = 3, max_gap_s: float = 0.2):
    """Smoothed position, velocity and acceleration (Savitzky-Golay), NaN where data are missing."""
    pos = fill_short_gaps(tr.pos, int(round(max_gap_s / tr.dt)))
    w = max(poly + 2, int(round(window_s / tr.dt)) | 1)
    nan = np.isnan(pos)
    # Savitzky-Golay cannot see NaN: fill with linear interpolation, then re-mask (and widen the mask)
    filled = fill_short_gaps(pos, pos.shape[0])
    filled = np.where(np.isnan(filled), 0.0, filled)
    x = savgol_filter(filled, w, poly, axis=0)
    v = savgol_filter(filled, w, poly, deriv=1, delta=tr.dt, axis=0)
    a = savgol_filter(filled, w, poly, deriv=2, delta=tr.dt, axis=0)
    bad = nan.any(axis=-1)
    k = w // 2   # a smoothed value is unreliable within half a window of a gap
    bad_w = bad.copy()
    for s in range(1, k + 1):
        bad_w[s:] |= bad[:-s]
        bad_w[:-s] |= bad[s:]
    for arr in (x, v, a):
        arr[bad_w] = np.nan
    return x, v, a


def unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n > 0, n, np.nan)


def group_order(x: np.ndarray, v: np.ndarray) -> dict:
    """Polarisation P (1 = all aligned) and milling M (1 = all circling) per frame."""
    u = unit(v)
    P = np.linalg.norm(np.nanmean(u, axis=1), axis=-1)
    c = np.nanmean(x, axis=1, keepdims=True)
    r = unit(x - c)
    if x.shape[-1] == 2:
        cross = r[..., 0] * u[..., 1] - r[..., 1] * u[..., 0]
        M = np.abs(np.nanmean(cross, axis=1))
    else:
        M = np.linalg.norm(np.nanmean(np.cross(r, u), axis=1), axis=-1)
    return {"polarisation": P, "milling": M}


def pairwise(x: np.ndarray):
    """Pairwise offsets (T, N, N, D) and distances (T, N, N) with self-distance = inf."""
    d = x[:, None, :, :] - x[:, :, None, :]     # d[t, i, j] = x_j - x_i
    dist = np.linalg.norm(d, axis=-1)
    idx = np.arange(x.shape[1])
    dist[:, idx, idx] = np.inf
    dist = np.where(np.isnan(dist), np.inf, dist)
    return d, dist


def nearest_neighbour_distance(x: np.ndarray) -> np.ndarray:
    _, dist = pairwise(x)
    nn = dist.min(axis=2)
    return np.where(np.isfinite(nn), nn, np.nan)


def summary(tr: Tracks, stride: int = 5) -> dict:
    x, v, _ = derivatives(tr)
    x, v = x[::stride], v[::stride]
    speed = np.linalg.norm(v, axis=-1)
    order = group_order(x, v)
    nn = nearest_neighbour_distance(x)
    bl = tr.body_length or np.nan
    return {
        "frames": int(tr.T), "animals": int(tr.N), "dims": int(tr.D), "duration_s": float(tr.T * tr.dt),
        "missing_fraction": float(np.isnan(tr.pos[..., 0]).mean()),
        "mean_speed_m_s": float(np.nanmean(speed)),
        "median_speed_m_s": float(np.nanmedian(speed)),
        "mean_nn_distance_m": float(np.nanmean(nn)),
        "median_nn_distance_m": float(np.nanmedian(nn)),
        "mean_speed_bl_s": float(np.nanmean(speed) / bl),
        "mean_nn_distance_bl": float(np.nanmean(nn) / bl),
        "polarisation_mean": float(np.nanmean(order["polarisation"])),
        "milling_mean": float(np.nanmean(order["milling"])),
        "fraction_polarised_gt_0.8": float(np.nanmean(order["polarisation"] > 0.8)),
        "fraction_milling_gt_0.5": float(np.nanmean(order["milling"] > 0.5)),
    }
