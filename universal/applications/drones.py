"""Drones: a flocking controller whose gains come from real swarms (fish, birds, crowds, drones).

The controller is NatureRule (alignment, cohesion, separation, speed set point) plus a
goal-seeking term. Simulation only: N drones fly to a target through a field of round
obstacles. KPIs: polarization, minimum separation, collisions, arrival. Compare gains from
the real-swarm ensemble with alignment switched off. Real flight logs of a 30-drone flock
(Vasarhelyi et al. 2018) are in the universal study, which is where the gains are checked.
"""
from __future__ import annotations

import numpy as np

from .core import NatureRule, min_separation, polarization


def simulate(n=30, steps=600, rule: NatureRule | None = None, seed=0) -> dict:
    rng = np.random.default_rng(seed)
    pos = rng.normal(0, 3, (n, 2))
    vel = np.tile([1.0, 0.0], (n, 1)) + rng.normal(0, 0.3, (n, 2))
    obstacles = np.array([[20, 2], [35, -3], [50, 1]])
    goal = np.array([70.0, 0.0])
    rule = rule or NatureRule.from_results(d0=2.0, v0=1.0, sep_gain=0.6)
    collisions, pol, sep = 0, [], []
    for _ in range(steps):
        a = rule.accel(pos, vel)
        to_goal = goal - pos
        a += 0.4 * to_goal / np.maximum(np.linalg.norm(to_goal, axis=1, keepdims=True), 1e-9)
        for o in obstacles:
            r = pos - o
            d = np.linalg.norm(r, axis=1, keepdims=True)
            a += np.where(d < 6, 2.0 * r / np.maximum(d, 1e-9) ** 2, 0)
            collisions += int((d < 1.0).sum())
        vel = vel + 0.1 * a
        sp = np.linalg.norm(vel, axis=1, keepdims=True)
        vel = vel / np.maximum(sp, 1e-9) * np.clip(sp, 0.2, 2.0)
        pos = pos + 0.1 * vel
        pol.append(polarization(vel))
        sep.append(min_separation(pos))
    arrived = float((np.linalg.norm(pos - goal, axis=1) < 10).mean())
    return {"polarization": float(np.mean(pol)), "min_separation": float(np.min(sep)),
            "obstacle_hits": collisions, "arrived_share": arrived}


def demo() -> dict:
    base = NatureRule.from_results(d0=2.0, v0=1.0, sep_gain=0.6)
    no_align = NatureRule.from_results(d0=2.0, v0=1.0, sep_gain=0.6, alpha=0.0)
    return {"simulated (not evidence)": {"ensemble gains": simulate(rule=base), "no alignment": simulate(rule=no_align)}}
