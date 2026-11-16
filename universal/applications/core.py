"""Shared pieces for the application frameworks: the nature-fitted local rule and the regulator.

Every application uses the same two ideas measured on real swarms (results/universal/):

1. ``NatureRule``: each agent steers by alignment (match neighbours' heading), cohesion (move
   toward neighbours), short-range separation, and a speed set-point. Gains default to the
   ensemble medians of the real moving swarms and can be tuned per application.
2. ``Regulator``: the collective level (load, fire area, cases, queue length) is pulled to a set
   point by a second-order law dx'' = -2 zeta w x' - w^2 (x - x*), the damped regulation seen in
   natural swarms (self-regulating share and anti-persistent changes in the ensemble).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

RESULTS = Path(__file__).resolve().parents[2] / "results" / "universal"


@dataclass
class NatureRule:
    alpha: float = 0.16  # alignment gain (ensemble median)
    beta: float = 0.01  # cohesion gain
    gamma: float = 0.05  # speed set-point gain
    switch_r: float = 0.95  # separation acts inside this many nearest-neighbour distances
    k: int = 3
    v0: float = 1.0
    d0: float = 1.0
    sep_gain: float = 0.5

    @classmethod
    def from_results(cls, **kw) -> "NatureRule":
        try:
            c = json.loads((RESULTS / "ensemble.json").read_text())["constants"]
            base = dict(alpha=c["tr_alpha_align"]["median"], beta=max(c["tr_beta_cohesion"]["median"], 0.0),
                        gamma=c["tr_gamma_speed"]["median"], switch_r=c["tr_switch_r_over_dnn"]["median"])
        except Exception:
            base = {}
        base.update(kw)
        return cls(**base)

    def accel(self, pos: np.ndarray, vel: np.ndarray, extra: np.ndarray | None = None) -> np.ndarray:
        """Acceleration of every agent from its k nearest neighbours (dimensionless units)."""
        n = len(pos)
        if n < 2:
            return np.zeros_like(vel)
        k = min(self.k, n - 1)
        d, j = cKDTree(pos).query(pos, k + 1)
        d, j = d[:, 1:], j[:, 1:]
        align = vel[j].mean(1) - vel
        coh = pos[j].mean(1) - pos
        diff = pos[:, None, :] - pos[j]
        close = (d < self.switch_r * self.d0)[..., None]
        sep = (close * diff / np.maximum(d[..., None], 1e-9) ** 2).sum(1)
        s = np.linalg.norm(vel, axis=1, keepdims=True)
        vhat = vel / np.maximum(s, 1e-9)
        scale = self.v0**2 / self.d0  # acceleration unit: typical speed / (neighbour distance / speed)
        a = scale * (self.alpha * align / self.v0 + self.beta * coh / self.d0
                     + self.gamma * (1 - s / self.v0) * vhat + self.sep_gain * sep * self.d0)
        if extra is not None:
            a = a + extra
        return a


@dataclass
class Regulator:
    """Second-order set-point regulator (damped, like natural swarms). Units of x per step."""

    omega: float = 0.3
    zeta: float = 0.7
    limit: float = np.inf

    def __post_init__(self):
        self.v = 0.0

    def step(self, x: float, target: float) -> float:
        acc = -2 * self.zeta * self.omega * self.v - self.omega**2 * (x - target)
        self.v = float(np.clip(self.v + acc, -self.limit, self.limit))
        return self.v


def polarization(vel: np.ndarray) -> float:
    s = np.linalg.norm(vel, axis=1, keepdims=True)
    return float(np.linalg.norm((vel / np.maximum(s, 1e-9)).sum(0)) / len(vel))


def min_separation(pos: np.ndarray) -> float:
    d, _ = cKDTree(pos).query(pos, 2)
    return float(d[:, 1].min())
