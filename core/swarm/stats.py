"""Statistics for multi-seed results: confidence intervals and paired tests.

RL results vary between training seeds, so every headline number is reported
over several independently trained swarms, evaluated on the same held-out
episodes as the rules. Two sources of variation are kept apart:

* **seeds**: which swarm came out of training (the main source for RL);
* **episodes**: which fires, days or weeks it was tested on.

``hierarchical_bootstrap`` resamples seeds, then episodes within each seed,
which is the usual way to get a confidence interval that covers both
(Agarwal et al., 2021, "Deep RL at the Edge of the Statistical Precipice").
A rule has no training seed, so its interval covers episodes only.

Comparisons with a rule are **paired**: the swarm and the rule play the same
episodes, so the per-episode difference removes episode difficulty from the
noise. ``paired_test`` gives the mean difference, its 95% interval and a
two-sided sign-flip permutation p-value (no distributional assumptions).
"""

from __future__ import annotations

import numpy as np

DEFAULT_RESAMPLES = 5_000


def hierarchical_bootstrap(x: np.ndarray, resamples: int = DEFAULT_RESAMPLES, ci: float = 0.95,
                           seed: int = 0) -> tuple[float, float, float]:
    """Mean and CI of ``x`` shaped (seeds, episodes); a 1-D array is one seed."""
    x = np.atleast_2d(np.asarray(x, dtype=float))
    S, E = x.shape
    rng = np.random.default_rng(seed)
    si = rng.integers(0, S, (resamples, S))
    ei = rng.integers(0, E, (resamples, S, E))
    boot = x[si[..., None], ei].mean(axis=(1, 2))
    lo, hi = np.quantile(boot, [(1 - ci) / 2, (1 + ci) / 2])
    return float(x.mean()), float(lo), float(hi)


def permutation_pvalue(d: np.ndarray, resamples: int = 20_000, seed: int = 0) -> float:
    """Two-sided sign-flip test that the mean of paired differences ``d`` is zero."""
    d = np.asarray(d, dtype=float).ravel()
    if len(d) == 0 or np.allclose(d, 0):
        return 1.0
    obs = abs(d.mean())
    if len(d) <= 16:  # exact: every sign pattern
        signs = ((np.arange(2 ** len(d))[:, None] >> np.arange(len(d))) & 1) * 2 - 1
    else:
        signs = np.random.default_rng(seed).choice([-1.0, 1.0], (resamples, len(d)))
    null = np.abs((signs * d).mean(axis=1))
    return float(((null >= obs - 1e-12).sum()) / len(null))


def paired_test(a: np.ndarray, b: np.ndarray, resamples: int = DEFAULT_RESAMPLES, seed: int = 0) -> dict:
    """Compare policy ``a`` (seeds, episodes) with ``b`` (episodes,) or (seeds, episodes).

    Returns the mean difference a - b, its hierarchical-bootstrap 95% CI, and a
    permutation p-value on the per-episode differences averaged over seeds.
    With a single episode (a whole held-out period) the test is over seeds.
    """
    a = np.atleast_2d(np.asarray(a, dtype=float))
    b = np.asarray(b, dtype=float)
    b = np.broadcast_to(b if b.ndim == 2 else b[None, :], a.shape)
    d = a - b
    mean, lo, hi = hierarchical_bootstrap(d, resamples, seed=seed)
    units = d[:, 0] if d.shape[1] == 1 else d.mean(axis=0)
    return {"diff": mean, "diff_lo": lo, "diff_hi": hi, "p_value": permutation_pvalue(units, seed=seed),
            "n_seeds": d.shape[0], "n_episodes": d.shape[1]}


def variant_test(a: np.ndarray, b: np.ndarray, resamples: int = DEFAULT_RESAMPLES, seed: int = 0) -> dict:
    """Compare two independently trained methods on the same episodes.

    ``a`` is (seeds_a, episodes), ``b`` is (seeds_b, episodes). The interval
    resamples each method's seeds independently and the episodes jointly (they
    are shared); the p-value is a sign-flip test on per-episode differences of
    the seed means, or a label-permutation test over seeds with one episode.
    """
    a, b = np.atleast_2d(np.asarray(a, float)), np.atleast_2d(np.asarray(b, float))
    rng = np.random.default_rng(seed)
    E = a.shape[1]
    ia = rng.integers(0, a.shape[0], (resamples, a.shape[0]))
    ib = rng.integers(0, b.shape[0], (resamples, b.shape[0]))
    ie = rng.integers(0, E, (resamples, E))
    ma = a[ia].mean(1)  # (R, E)
    mb = b[ib].mean(1)
    boot = (np.take_along_axis(ma, ie, 1) - np.take_along_axis(mb, ie, 1)).mean(1)
    lo, hi = np.quantile(boot, [0.025, 0.975])
    if E > 1:
        p = permutation_pvalue(a.mean(0) - b.mean(0), seed=seed)
    else:
        pooled = np.r_[a[:, 0], b[:, 0]]
        obs = abs(a.mean() - b.mean())
        perm = np.array([rng.permutation(pooled) for _ in range(5_000)])
        null = np.abs(perm[:, :a.shape[0]].mean(1) - perm[:, a.shape[0]:].mean(1))
        p = float((null >= obs - 1e-12).mean())
    return {"diff": float(a.mean() - b.mean()), "diff_lo": float(lo), "diff_hi": float(hi), "p_value": float(p)}


def fmt_ci(mean: float, lo: float, hi: float, digits: int = 1) -> str:
    return f"{mean:,.{digits}f} [{lo:,.{digits}f}, {hi:,.{digits}f}]"


def fmt_p(p: float) -> str:
    return "<0.001" if p < 0.001 else f"{p:.3f}"
