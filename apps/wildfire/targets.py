"""Wildfire with high-level actions: each drone chooses *which fire to fight*.

The nearest-fire rule sends every drone to its own nearest burning cell, so
drones bunch up on one part of the front while another part spreads. Here a
drone chooses among its ``K`` nearest *distinct* fire targets (target 0 is the
rule's choice), or returning to a pad, or holding. Movement, dropping and
refilling are then done by the same logic as the rule, so learning only has to
answer the coordination question: who covers which part of the fire.

Each drone's observation is the usual local view plus, for every candidate
target, its offset, distance and how many other drones are already closer to
it, so a drone can see when a target is "taken".

Registered as the app ``wildfire-targets``; the rule is "always target 0",
which reproduces the nearest-fire rule.
"""

from __future__ import annotations

import numpy as np

from .baselines import _toward
from .env import BURNING, DROP, HOLD, WildfireSwarmEnv

KEY_METRICS = ["forest_saved_pct", "burned_cells", "peak_fire_cells", "contained", "return"]


class WildfireTargetsEnv(WildfireSwarmEnv):
    def __init__(self, targets: int = 4, **kw):
        super().__init__(**kw)
        self.K = int(targets)
        self.BASE, self.STAY = self.K, self.K + 1
        self.n_actions = self.K + 2
        self.null_action = self.STAY
        self.base_obs_dim = self.obs_dim
        self.obs_dim = self.base_obs_dim + 4 * self.K

    def _targets(self):
        """(drones, K) indices into the burning cells, nearest first; -1 pads."""
        fy, fx = np.nonzero(self.grid == BURNING)
        self.fy, self.fx = fy, fx
        out = np.full((self.n_agents, self.K), -1)
        if len(fy) == 0:
            self.tdist = np.zeros((self.n_agents, 0))
            return out
        y, x = self.pos[:, :1], self.pos[:, 1:]
        d = np.abs(fy[None] - y) + np.abs(fx[None] - x)        # (drones, fires)
        self.tdist = d
        # Same small random tie-break as the nearest-fire rule, so drones at equal distance spread out.
        order = np.argsort(d + self.rng.random(d.shape) * 2, axis=1)[:, :self.K]
        out[:, :order.shape[1]] = order
        return out

    def _obs(self):
        base = super()._obs()
        self.cand = self._targets()
        G = self.G
        extra = np.zeros((self.n_agents, 4 * self.K), np.float32)
        if len(self.fy):
            for k in range(self.K):
                j = self.cand[:, k]
                ok = j >= 0
                jj = np.where(ok, j, 0)
                dy, dx = (self.fy[jj] - self.pos[:, 0]) / G, (self.fx[jj] - self.pos[:, 1]) / G
                dist = self.tdist[np.arange(self.n_agents), jj]
                # How many other drones are closer to this target than I am.
                closer = (self.tdist[:, jj] < dist[None]).sum(0) - 0
                extra[:, 4 * k:4 * k + 4] = np.stack([dy, dx, dist / (2 * G), closer / self.n_agents], 1) * ok[:, None]
        return np.concatenate([base, extra], 1).astype(np.float32)

    def action_mask(self):
        m = np.zeros((self.n_agents, self.n_actions), bool)
        m[:, :self.K] = getattr(self, "cand", np.full((self.n_agents, self.K), -1)) >= 0
        m[:, self.BASE] = True
        m[:, self.STAY] = True
        return m

    def step(self, actions):
        a = np.asarray(actions)
        prim = np.full(self.n_agents, HOLD)
        pm = super().action_mask()
        pad = self._pad_distance()
        for i, (y, x) in enumerate(self.pos):
            if a[i] == self.STAY:
                continue
            if a[i] == self.BASE or self.payload[i] == 0:
                prim[i] = HOLD if pad[0][i] == 0 else _toward(y, x, *pad[1][i])
            elif self.grid[y, x] == BURNING and pm[i, DROP]:
                prim[i] = DROP
            else:
                j = self.cand[i, a[i]]
                if j >= 0:
                    prim[i] = _toward(y, x, self.fy[j], self.fx[j])
        return super().step(prim)


def make_env(env_cfg: dict, split: str, seed: int) -> WildfireTargetsEnv:
    cfg = {k: v for k, v in env_cfg.items() if k != "scale_pads"}
    return WildfireTargetsEnv(seed=seed, **cfg)


def nearest_target(env, obs, mask):
    """The nearest-fire rule in this action space: always the nearest target."""
    return np.where(mask[:, 0], 0, env.BASE)


def no_drones(env, obs, mask):
    return np.full(env.n_agents, env.STAY)


def spread_rule(env, obs, mask):
    """A hand-made coordination rule: take the nearest target that no other drone is closer to."""
    acts = np.where(mask[:, 0], 0, env.BASE)
    for i in range(env.n_agents):
        for k in range(env.K):
            if not mask[i, k]:
                break
            if obs[i, env.base_obs_dim + 4 * k + 3] == 0:
                acts[i] = k
                break
    return acts


BASELINES = {"no drones": no_drones, "nearest-fire rule": nearest_target, "spread rule": spread_rule}


def scaled_env_cfg(env_cfg: dict, n: int) -> dict:
    from . import scaled_env_cfg as base

    return base(env_cfg, n)
