"""Dimensionless features measured the same way on every dataset.

Tracks (agent level)
    polarization, speed regulation, spacing regularity, persistence, and a fitted local rule
    a = alpha*(neighbour velocity - own) + beta*(neighbour centre - own) + gamma*(v0 - |v|) v_hat
    in units where the median nearest-neighbour distance and the median speed are 1.
Series (collective level)
    DFA exponent of increments, spectral slope, lag-1 restoring rate, burstiness, kurtosis.
Events
    power-law tail exponent (Clauset-Shalizi-Newman MLE with KS-chosen xmin) and a
    likelihood-ratio test against a lognormal.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from scipy.spatial import cKDTree

from .types import Events, Series, Tracks

RNG = np.random.default_rng(0)


# ---------------------------------------------------------------- tracks
def _episode_arrays(g: pd.DataFrame, dims: int):
    cols = ["x", "y", "z"][:dims]
    g = g.sort_values(["id", "t"])
    pos = g[cols].to_numpy(float)
    t = g["t"].to_numpy(float)
    ids = g["id"].to_numpy()
    same = np.r_[ids[1:] == ids[:-1], False]
    dt = np.r_[np.diff(t), np.nan]
    step = np.nanmedian(dt[same]) if same.any() else np.nan
    ok = same & np.isclose(dt, step, rtol=0.05)
    vel = np.full_like(pos, np.nan)
    nxt = np.r_[pos[1:], pos[-1:]]
    vel[ok] = (nxt[ok] - pos[ok]) / step
    out = g[["t", "id"]].copy()
    out[[f"p{i}" for i in range(dims)]] = pos
    out[[f"v{i}" for i in range(dims)]] = vel
    # acceleration from consecutive velocities of the same agent
    vn = np.r_[vel[1:], vel[-1:]]
    acc = np.full_like(pos, np.nan)
    ok2 = ok & np.r_[ok[1:], False]
    acc[ok2] = (vn[ok2] - vel[ok2]) / step
    out[[f"a{i}" for i in range(dims)]] = acc
    return out.dropna(subset=[f"v{i}" for i in range(dims)]), step


def _stride(tr: Tracks) -> int:
    """Sample step so each agent moves about 0.3 neighbour distances per step (less tracking noise)."""
    eps = list(tr.episodes())[:5]
    v, dn, st = [], [], []
    for _, g in eps:
        e, step = _episode_arrays(g, tr.dims)
        if len(e) == 0:
            continue
        st.append(step)
        v.append(np.linalg.norm(e[[f"v{i}" for i in range(tr.dims)]].to_numpy(), axis=1))
        for t in e["t"].unique()[:: max(1, e["t"].nunique() // 100)]:
            p = e.loc[e["t"] == t, [f"p{i}" for i in range(tr.dims)]].to_numpy()
            if len(p) > 1:
                dn.append(np.median(cKDTree(p).query(p, 2)[0][:, 1]))
    if not v or not dn:
        return 1
    move = np.median(np.concatenate(v)) * np.nanmedian(st)
    return int(max(1, round(0.3 * np.median(dn) / max(move, 1e-12))))


def track_features(tr: Tracks, max_frames: int = 4000, k: int = 3) -> dict:
    dims = tr.dims
    stride = _stride(tr)
    if stride > 1:
        df = tr.df
        keep = []
        for _, g in df.groupby("ep", sort=False):
            ts = np.sort(g["t"].unique())[::stride]
            keep.append(g[g["t"].isin(ts)])
        tr = Tracks(pd.concat(keep), tr.unit, dims)
    P = [f"p{i}" for i in range(dims)]
    V = [f"v{i}" for i in range(dims)]
    A = [f"a{i}" for i in range(dims)]
    frames, speeds, steps = [], [], []
    for _, g in tr.episodes():
        e, step = _episode_arrays(g, dims)
        if len(e) == 0:
            continue
        steps.append(step)
        speeds.append(np.linalg.norm(e[V].to_numpy(), axis=1))
        frames.append(e)
    if not frames:
        return {}
    v0 = float(np.median(np.concatenate(speeds)))
    allf = pd.concat([f.assign(ep=i) for i, f in enumerate(frames)])
    keys = allf[["ep", "t"]].drop_duplicates()
    if len(keys) > max_frames:
        keys = keys.sample(max_frames, random_state=0)
    sel = allf.merge(keys, on=["ep", "t"])
    pol, nn_all, X, Y, radial = [], [], [], [], []
    for (_, _), f in sel.groupby(["ep", "t"]):
        n = len(f)
        if n < 2:
            continue
        p = f[P].to_numpy()
        v = f[V].to_numpy()
        s = np.linalg.norm(v, axis=1)
        moving = s > 1e-9
        if moving.sum() >= 2:
            pol.append(np.linalg.norm((v[moving] / s[moving, None]).sum(0)) / moving.sum())
        kk = min(k, n - 1)
        d, j = cKDTree(p).query(p, kk + 1)
        d, j = d[:, 1:], j[:, 1:]
        nn_all.append(d[:, 0])
        a = f[A].to_numpy()
        good = ~np.isnan(a).any(1) & moving
        if good.any():
            align = v[j].mean(1) - v
            coh = p[j].mean(1) - p
            vhat = np.where(moving[:, None], v / np.maximum(s, 1e-12)[:, None], 0)
            spd = (1.0 - s / v0)[:, None] * vhat  # filled in units below
            X.append(np.stack([align[good], coh[good], spd[good] * v0], 1))
            Y.append(a[good])
            rhat = (p[j[:, 0]] - p) / np.maximum(d[:, :1], 1e-12)
            radial.append(np.c_[d[good, 0], (a[good] * rhat[good]).sum(1)])
    out = {"v0": v0, "dt": float(np.nanmedian(steps)), "dims": dims, "stride": stride}
    if nn_all:
        nn = np.concatenate(nn_all)
        nn = nn[nn > 0]
        d0 = float(np.median(nn))
        out.update(d_nn=d0, spacing_cv=float(nn.std() / nn.mean()))
    if pol:
        out.update(polarization=float(np.mean(pol)), polarization_sd=float(np.std(pol)))
    sp = np.concatenate(speeds)
    out["speed_cv"] = float(sp.std() / sp.mean())
    out["persistence"] = _persistence(frames, V, out.get("d_nn"), v0)
    if X and "d_nn" in out:
        out.update(_local_rule(np.concatenate(X), np.concatenate(Y), out["d_nn"], v0))
        out.update(_switch_distance(np.concatenate(radial), out["d_nn"], v0))
    else:
        out.update(_speed_only_rule(frames, V, A, v0))
    return out


def _persistence(frames, V, d0, v0):
    """Velocity autocorrelation time, in units of d_nn / v0 (or of the sample step if alone)."""
    taus = []
    for f in frames[:50]:
        for _, g in list(f.groupby("id"))[:40]:
            v = g[V].to_numpy()
            if len(v) < 20:
                continue
            u = v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-12)
            c = [np.mean((u[:-lag] * u[lag:]).sum(1)) for lag in range(1, min(len(u) // 2, 200))]
            c = np.array(c)
            below = np.where(c < np.exp(-1))[0]
            taus.append((below[0] + 1) if len(below) else len(c))
            t = g["t"].to_numpy()
    if not taus:
        return np.nan
    step = np.nanmedian(np.diff(t)) if len(t) > 1 else 1.0
    scale = (d0 / v0) if d0 else step
    return float(np.median(taus) * step / scale)


def _local_rule(X, Y, d0, v0):
    """Least squares for a = alpha*align + beta*cohesion + gamma*speed_term, dimensionless."""
    T = d0 / v0
    Xs = X.copy()
    Xs[:, 0] /= v0
    Xs[:, 1] /= d0
    Xs[:, 2] /= v0
    Ys = Y * T / v0
    Xf = Xs.transpose(0, 2, 1).reshape(-1, 3)
    yf = Ys.reshape(-1)
    ok = np.isfinite(Xf).all(1) & np.isfinite(yf)
    Xf, yf = Xf[ok], yf[ok]
    lo, hi = np.percentile(yf, [1, 99])
    m = (yf > lo) & (yf < hi)
    Xf, yf = Xf[m], yf[m]
    coef, *_ = np.linalg.lstsq(Xf, yf, rcond=None)
    r2 = 1 - np.sum((yf - Xf @ coef) ** 2) / np.sum((yf - yf.mean()) ** 2)
    # bootstrap SE
    se = []
    for _ in range(30):
        i = RNG.integers(0, len(yf), len(yf))
        se.append(np.linalg.lstsq(Xf[i], yf[i], rcond=None)[0])
    se = np.std(se, 0)
    return {"alpha_align": float(coef[0]), "beta_cohesion": float(coef[1]), "gamma_speed": float(coef[2]),
            "alpha_se": float(se[0]), "beta_se": float(se[1]), "gamma_se": float(se[2]),
            "rule_r2": float(r2), "rule_n": int(len(yf))}


def _speed_only_rule(frames, V, A, v0):
    xs, ys = [], []
    for f in frames:
        v = f[V].to_numpy()
        a = f[A].to_numpy()
        s = np.linalg.norm(v, axis=1)
        ok = (s > 0) & ~np.isnan(a).any(1)
        vhat = v[ok] / s[ok, None]
        xs.append(1 - s[ok] / v0)
        ys.append((a[ok] * vhat).sum(1))
    x, y = np.concatenate(xs), np.concatenate(ys)
    if len(x) < 10:
        return {}
    step = np.nanmedian([np.nanmedian(np.diff(f["t"].unique())) for f in frames])
    y = y * step / v0  # per-step units (no neighbour scale for a lone agent)
    lo, hi = np.percentile(y, [1, 99])
    m = (y > lo) & (y < hi)
    g = float(np.sum(x[m] * y[m]) / np.sum(x[m] ** 2))
    r2 = 1 - np.sum((y[m] - g * x[m]) ** 2) / np.sum((y[m] - y[m].mean()) ** 2)
    return {"gamma_speed": g, "rule_r2": float(r2), "rule_n": int(m.sum()), "rule_note": "speed term only (lone agents)"}


def _switch_distance(rad, d0, v0):
    """Distance (in d_nn) where the push from the nearest neighbour turns from repulsion to attraction."""
    r = rad[:, 0] / d0
    f = rad[:, 1] * (d0 / v0) / v0
    bins = np.quantile(r, np.linspace(0, 1, 21))
    mids, means = [], []
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (r >= lo) & (r < hi)
        if m.sum() > 20:
            mids.append(np.median(r[m]))
            means.append(np.median(f[m]))
    mids, means = np.array(mids), np.array(means)
    cross = np.where((means[:-1] < 0) & (means[1:] >= 0))[0]
    r0 = float(np.interp(0, [means[cross[0]], means[cross[0] + 1]], [mids[cross[0]], mids[cross[0] + 1]])) \
        if len(cross) else np.nan
    return {"switch_r_over_dnn": r0, "radial_profile": [[float(a), float(b)] for a, b in zip(mids, means)]}


# ---------------------------------------------------------------- series
def dfa_alpha(x: np.ndarray, min_box=4) -> float:
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) < 32:
        return np.nan
    y = np.cumsum(x - x.mean())
    sizes = np.unique(np.logspace(np.log10(min_box), np.log10(len(x) // 4), 15).astype(int))
    F = []
    for s in sizes:
        n = len(y) // s
        seg = y[: n * s].reshape(n, s)
        t = np.arange(s)
        res = []
        for row in seg:
            c = np.polyfit(t, row, 1)
            res.append(np.mean((row - np.polyval(c, t)) ** 2))
        F.append(np.sqrt(np.mean(res)))
    F = np.array(F)
    ok = F > 0
    return float(np.polyfit(np.log(sizes[ok]), np.log(F[ok]), 1)[0])


def spectral_slope(x: np.ndarray) -> float:
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    if len(x) < 32:
        return np.nan
    x = x - np.polyval(np.polyfit(np.arange(len(x)), x, 1), np.arange(len(x)))
    p = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    f = np.fft.rfftfreq(len(x))
    m = (f > 0) & (p > 0)
    return float(-np.polyfit(np.log(f[m]), np.log(p[m]), 1)[0])


def series_features(s: Series) -> dict:
    x = np.asarray(s.x, float)
    x = x[np.isfinite(x)]
    inc = np.diff(x)
    if s.cumulative:
        level = inc  # the flow (new cases, area per day) is the swarm's activity
        inc = np.diff(level)
    else:
        level = x
    out = {"n": int(len(x))}
    if len(level) < 16:
        return out
    z = (level - level.mean()) / (level.std() + 1e-12)
    det = z - np.polyval(np.polyfit(np.arange(len(z)), z, 1), np.arange(len(z)))
    phi1 = float(np.corrcoef(det[:-1], det[1:])[0, 1])
    absinc = np.abs(inc)
    out.update({
        "dfa_increments": dfa_alpha(inc),
        "dfa_level": dfa_alpha(level),
        "spectral_slope": spectral_slope(level),
        "ar1": phi1,
        "restoring_rate": float(-np.log(max(min(phi1, 0.9999), 1e-4))),
        "burstiness": float((absinc.std() - absinc.mean()) / (absinc.std() + absinc.mean() + 1e-12)),
        "kurtosis_increments": float(stats.kurtosis(inc / (inc.std() + 1e-12))),
    })
    return out


# ---------------------------------------------------------------- events
def powerlaw_fit(x: np.ndarray, n_xmin=40) -> dict:
    x = np.sort(np.asarray(x, float))
    x = x[np.isfinite(x) & (x > 0)]
    if len(x) < 50:
        return {}
    cands = np.unique(np.quantile(x, np.linspace(0.0, 0.9, n_xmin)))
    best = None
    for xm in cands:
        tail = x[x >= xm]
        if len(tail) < 30:
            continue
        a = 1 + len(tail) / np.sum(np.log(tail / xm))
        cdf_emp = np.arange(1, len(tail) + 1) / len(tail)
        cdf_fit = 1 - (tail / xm) ** (1 - a)
        ks = np.max(np.abs(cdf_emp - cdf_fit))
        if best is None or ks < best[2]:
            best = (xm, a, ks, len(tail))
    if best is None:
        return {}
    xm, a, ks, nt = best
    tail = x[x >= xm]
    # lognormal on the same tail (truncated at xmin), log-likelihood ratio (positive favours power law)
    ll_pl = np.log(a - 1) - np.log(xm) - a * np.log(tail / xm)
    mu, sg = np.mean(np.log(tail)), np.std(np.log(tail)) + 1e-12
    from scipy.optimize import minimize

    def nll(p):
        m, s = p[0], abs(p[1]) + 1e-6
        surv = stats.norm.sf((np.log(xm) - m) / s)
        return -np.sum(stats.lognorm.logpdf(tail, s, scale=np.exp(m)) - np.log(max(surv, 1e-300)))

    r = minimize(nll, [mu, sg], method="Nelder-Mead")
    ll_ln = -r.fun
    diff = ll_pl - (stats.lognorm.logpdf(tail, abs(r.x[1]) + 1e-6, scale=np.exp(r.x[0]))
                    - np.log(max(stats.norm.sf((np.log(xm) - r.x[0]) / (abs(r.x[1]) + 1e-6)), 1e-300)))
    R = float(np.sum(diff))
    p = float(2 * stats.norm.sf(abs(R) / (np.sqrt(len(tail)) * diff.std() + 1e-12)))
    return {"tail_alpha": float(a), "tail_xmin_quantile": float(np.mean(x < xm)), "tail_n": int(nt),
            "tail_ks": float(ks), "pl_vs_lognormal_LR": R, "pl_vs_lognormal_p": p, "ll_lognormal": float(ll_ln)}


def event_features(e: Events) -> dict:
    out = powerlaw_fit(e.sizes)
    if e.times is not None and len(e.times) > 50:
        gaps = np.diff(np.sort(e.times))
        gaps = gaps[gaps > 0]
        out["interevent_burstiness"] = float((gaps.std() - gaps.mean()) / (gaps.std() + gaps.mean()))
        out["interevent_memory"] = float(np.corrcoef(gaps[:-1], gaps[1:])[0, 1])
    return out
