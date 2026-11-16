"""Epidemics: regions as agents. Each region forecasts its own wave with the swarm growth law and
asks neighbours for help (tests, beds) in proportion to forecast growth.

Real data: JHU CSSE COVID-19 confirmed cases, first wave (Jan-Jun 2020), 25 countries + Canada.
Test: fit days up to the point where cases reach 20% of the wave total, forecast 21 days ahead;
compare Richards (swarm law), Gompertz, and pure exponential. KPI: median absolute log error.
"""
from __future__ import annotations

import warnings

import numpy as np
from scipy.optimize import curve_fit

from ..equation import exponential, gompertz, richards


def _fit_predict(f, p0, bounds, t, y, t_new):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            p, _ = curve_fit(f, t, y, p0=p0, bounds=bounds, maxfev=20000)
            return f(t_new, *p)
        except Exception:
            return np.full_like(t_new, y[-1])


def demo(horizon=21, frac=0.2) -> dict:
    from ..loaders import load

    err = {"richards": [], "gompertz": [], "exponential": []}
    for s in load("covid").series:
        y = s.x
        start = np.argmax(y > 100)
        y = y[start:]
        if len(y) < 40:
            continue
        cut = np.argmax(y >= frac * y[-1])
        if cut < 10 or cut + horizon >= len(y):
            continue
        t = np.arange(cut, dtype=float)
        sc = y[cut - 1]
        tn = np.array([cut - 1 + horizon], float)
        truth = y[cut - 1 + horizon]
        pr = _fit_predict(richards, [3, 0.1, cut, 1], ([1, 1e-3, 0, 0.02], [1e3, 2, 400, 10]), t, y[:cut] / sc, tn)
        pg = _fit_predict(gompertz, [3, 0.05, cut], ([1, 1e-3, -100], [1e3, 2, 400]), t, y[:cut] / sc, tn)
        pe = _fit_predict(exponential, [0.1, 0.05], ([1e-9, 0], [10, 2]), t, y[:cut] / sc, tn)
        for k, p in zip(err, [pr, pg, pe]):
            err[k].append(abs(np.log(max(p[0] * sc, 1) / truth)))
    return {"data": "JHU CSSE COVID-19 first wave (real)", "countries": len(err["richards"]), "horizon_days": horizon,
            **{m: {"median_abs_log_error": float(np.median(v))} for m, v in err.items()}}
