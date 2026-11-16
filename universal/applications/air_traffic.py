"""Air traffic: aircraft as a swarm that keeps separation with local rules.

Real data part: OpenSky ADS-B positions (Europe, July 2019). We count close pairs (horizontal
distance under a threshold at the same timestamp). The OpenSky subset has no altitude, so these
are 2D proximity events, not real losses of separation.
Simulated part: random crossing flows; each aircraft follows its route plus the nature rule's
separation and alignment terms only when another aircraft is within the alert radius. KPI:
close pairs and route deviation, with and without the swarm rule. Simulation only.
"""
from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree

from .core import NatureRule


def real_proximity(threshold_km=9.26) -> dict:
    from ..loaders import load

    df = load("air").tracks.df
    pairs, frames = 0, 0
    for _, g in df.groupby("t"):
        if len(g) < 2:
            continue
        frames += 1
        pairs += len(cKDTree(g[["x", "y"]].to_numpy()).query_pairs(threshold_km * 1000))
    return {"data": "OpenSky ADS-B Europe July 2019 (real, 2D only)", "timestamps": frames,
            "pairs_within_5NM": int(pairs), "pairs_per_timestamp": pairs / max(frames, 1)}


def simulate(n=60, steps=400, swarm=True, seed=0, alert=3.0) -> dict:
    rng = np.random.default_rng(seed)
    ang = rng.uniform(0, 2 * np.pi, n)
    pos = np.c_[np.cos(ang), np.sin(ang)] * 30
    goal = -pos + rng.normal(0, 3, (n, 2))
    vel = (goal - pos) / np.linalg.norm(goal - pos, axis=1, keepdims=True)
    rule = NatureRule(alpha=0.2, beta=0.0, gamma=0.3, switch_r=alert, d0=1.0, v0=1.0, sep_gain=0.8)
    close, dev = 0, 0.0
    for _ in range(steps):
        to_goal = goal - pos
        dist = np.linalg.norm(to_goal, axis=1, keepdims=True)
        desired = to_goal / np.maximum(dist, 1e-9)
        a = 0.5 * (desired - vel)
        if swarm:
            d, j = cKDTree(pos).query(pos, 2)
            near = d[:, 1] < alert
            if near.any():
                a[near] += rule.accel(pos, vel)[near]
        vel = vel + 0.1 * a
        vel = vel / np.maximum(np.linalg.norm(vel, axis=1, keepdims=True), 1e-9)
        pos = pos + 0.1 * vel
        close += len(cKDTree(pos).query_pairs(1.0))
        dev += float(np.abs(1 - (vel * desired).sum(1)).mean())
    return {"close_pair_steps": close, "mean_heading_deviation": dev / steps}


def demo() -> dict:
    return {"real": real_proximity(), "simulated (not evidence)": {
        "no swarm rule": simulate(swarm=False), "swarm rule": simulate(swarm=True)}}
