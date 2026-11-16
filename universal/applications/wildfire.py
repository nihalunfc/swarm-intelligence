"""Wildfire: forecast each fire's growth with the swarm growth law and allocate crews to the
fires that will grow most (decentralised: each fire 'agent' bids with its forecast growth).

Growth law: Richards curve A(t) = K / (1 + nu exp(-r (t - tm)))^(1/nu), the self-limiting growth
term of the general equation. Real data: daily progression of large fires (MTBS + Canada NBAC).
Test: fit on the first k days, predict the final size; compare with 'stop now' (final =
current), 'persistence' (the last daily growth continues for the typical remaining duration),
and an oracle persistence that knows the true remaining duration (not usable in practice). KPI: median absolute log error of the final size.
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


def _one(fires, k):
    err = {"richards": [], "persistence_typical_duration": [], "stop_now": [], "persistence_oracle_duration": []}
    typical = float(np.median([len(s.t) - k for s in fires if len(s.t) >= k + 3]))
    for s in fires:
        t, a = s.t, s.x
        if len(t) < k + 3:
            continue
        final = a[-1]
        err["richards"].append(abs(np.log(forecast_final(t, a, k) / final)))
        rate = a[k - 1] - a[k - 2]
        err["persistence_typical_duration"].append(abs(np.log((a[k - 1] + rate * typical) / final)))
        # oracle: knows how many days the fire will really burn (not available in practice)
        err["persistence_oracle_duration"].append(abs(np.log((a[k - 1] + rate * (len(t) - k)) / final)))
        err["stop_now"].append(abs(np.log(a[k - 1] / final)))
    return {"fires": len(err["richards"]),
            **{m: {"median_abs_log_error": float(np.median(v))} for m, v in err.items()}}


def demo(train_days=(5, 8, 12, 16), n_fires=300) -> dict:
    """Forecast skill as more days of each fire are seen (same fires: those that burn at least 19 days)."""
    from ..loaders import load

    fires = [s for s in load("fire", n_growth=n_fires).series if len(s.t) >= max(train_days) + 3]
    return {"data": "MTBS + NBAC daily fire progression (real)",
            "note": "same fires at every horizon; error = median |log(predicted final / actual final)|",
            **{f"{k}_days": _one(fires, k) for k in train_days}}


def allocate(forecast_growth: np.ndarray, crews: int) -> np.ndarray:
    """Each fire bids its forecast growth; crews go out in proportion (largest remainder)."""
    w = np.maximum(forecast_growth, 0)
    if w.sum() == 0:
        return np.zeros_like(w, dtype=int)
    raw = crews * w / w.sum()
    n = np.floor(raw).astype(int)
    n[np.argsort(-(raw - n))[: crews - n.sum()]] += 1
    return n
