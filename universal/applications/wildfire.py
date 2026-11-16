"""Wildfire: forecast each fire's growth with the swarm growth law and allocate crews to the
fires that will grow most (decentralised: each fire 'agent' bids with its forecast growth).

Growth law: Richards curve A(t) = K / (1 + nu exp(-r (t - tm)))^(1/nu), the self-limiting growth
term of the general equation. Real data: daily progression of large fires (MTBS + Canada NBAC).
Test: fit on the first k days, predict the final size; compare with 'persistence' (assume the
fire keeps growing at its last daily rate for the same number of remaining days) and with
'stop now' (final = current). KPI: median absolute log error of the final size.
"""
from __future__ import annotations

import warnings

import numpy as np
from scipy.optimize import curve_fit

from ..equation import richards


def forecast_final(days: np.ndarray, area: np.ndarray, k: int) -> float:
    t, y = days[:k], area[:k]
    scale = y.max()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            p, _ = curve_fit(richards, t, y / scale, p0=[2, 0.5, t.mean(), 0.5],
                             bounds=([1, 0.01, -50, 0.02], [200, 5, 200, 10]), maxfev=20000)
            return float(p[0] * scale)
        except Exception:
            return float(y[-1])


def demo(k=5, n_fires=150) -> dict:
    from ..loaders import load

    fires = load("fire", n_growth=n_fires).series
    err = {"richards": [], "persistence": [], "stop_now": []}
    for s in fires:
        t, a = s.t, s.x
        if len(t) < k + 3:
            continue
        final = a[-1]
        err["richards"].append(abs(np.log(forecast_final(t, a, k) / final)))
        rate = a[k - 1] - a[k - 2]
        err["persistence"].append(abs(np.log((a[k - 1] + rate * (len(t) - k)) / final)))
        err["stop_now"].append(abs(np.log(a[k - 1] / final)))
    return {"data": "MTBS + NBAC daily fire progression (real)", "fires": len(err["richards"]), "train_days": k,
            **{m: {"median_abs_log_error": float(np.median(v))} for m, v in err.items()}}


def allocate(forecast_growth: np.ndarray, crews: int) -> np.ndarray:
    """Each fire bids its forecast growth; crews go out in proportion (largest remainder)."""
    w = np.maximum(forecast_growth, 0)
    if w.sum() == 0:
        return np.zeros_like(w, dtype=int)
    raw = crews * w / w.sum()
    n = np.floor(raw).astype(int)
    n[np.argsort(-(raw - n))[: crews - n.sum()]] += 1
    return n
