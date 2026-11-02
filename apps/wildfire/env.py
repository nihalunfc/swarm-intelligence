"""Drone swarm containing a wildfire on a 2D forest grid.

Cell states: 0 fuel, 1 burning, 2 burned out, 3 wet (retardant or
extinguished, will not burn). Burning cells burn out after a few steps, so a
fire also ends on its own once it runs out of fuel; the drones' job is to keep
the burned area small.

Each drone sees only a local window around itself plus a few navigation cues,
and chooses to move, drop retardant on its cell, or hold (holding on the
launch pad refills). Fire spread is vectorized with NumPy shifts.
"""

import numpy as np
from swarm.env import SwarmEnv

FUEL, BURNING, BURNED, WET = 0, 1, 2, 3
UP, DOWN, LEFT, RIGHT, DROP, HOLD = range(6)
MOVES = {UP: (-1, 0), DOWN: (1, 0), LEFT: (0, -1), RIGHT: (0, 1)}
WINDS = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]


class WildfireSwarmEnv(SwarmEnv):
    n_actions = 6
    null_action = HOLD  # what a failed drone does (robustness tests)

    def __init__(self, grid_size=16, n_drones=6, max_payload=6, view_radius=3, max_steps=150,
                 p_spread=0.12, p_wind=0.30, burn_time=(3, 6), n_ignitions=2, wind=None,
                 reward_extinguish=1.0, drop_near_fire_only=True, shaping=0.1, shaping_gamma=0.97, fire_every=1,
                 base_size=3, comm_radius=4, pads_per_side=1, seed=0):
        self.G = int(grid_size)
        self.n_agents = int(n_drones)
        self.max_payload = int(max_payload)
        self.r = int(view_radius)
        self.max_steps = int(max_steps)
        self.p_spread, self.p_wind = float(p_spread), float(p_wind)
        self.burn_time = tuple(burn_time)
        self.n_ignitions = int(n_ignitions)
        self.fixed_wind = tuple(wind) if wind else None
        self.reward_extinguish = float(reward_extinguish)
        self.drop_near_fire_only = bool(drop_near_fire_only)
        self.shaping, self.shaping_gamma = float(shaping), float(shaping_gamma)
        self.fire_every = int(fire_every)  # drones move this many cells per fire-spread tick
        self.rng = np.random.default_rng(seed)
        w = 2 * self.r + 1
        self.obs_dim = 3 * w * w + 3 + 3 + 2 + 2 + 1
        self.base = (0, 0)
        self.comm_radius = int(comm_radius)  # drones within this many cells hear each other
        self.base_size = int(base_size)  # drones launch from and refill anywhere on a pad
        # Launch pads: one (top-left) by default, or a p x p grid of pads, one per tile of the
        # forest, so refill trips stay short when the forest and swarm grow.
        p = int(pads_per_side)
        tile = self.G // p
        self.pads = np.array([(i * tile, j * tile) for i in range(p) for j in range(p)], dtype=int)

    # --- SwarmEnv API -------------------------------------------------
    def reset(self, seed=None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        G = self.G
        self.grid = np.zeros((G, G), dtype=np.int8)
        self.timer = np.zeros((G, G), dtype=np.int16)
        self.ignited = np.zeros((G, G), dtype=bool)
        lo, hi = G // 4, G - G // 4
        for _ in range(self.n_ignitions):
            y, x = self.rng.integers(lo, hi, size=2)
            self._ignite(np.array([[y]]), np.array([[x]]))
        self.wind = self.fixed_wind or WINDS[self.rng.integers(len(WINDS))]
        # Random launch cells on the pad, so identical drones do not start (and stay) stacked.
        self.pos = self.rng.integers(0, self.base_size, size=(self.n_agents, 2))
        self.pos += self.pads[np.arange(self.n_agents) % len(self.pads)]  # drones spread over the pads
        self.payload = np.full(self.n_agents, self.max_payload)
        self.steps = 0
        self.drops = 0
        self.extinguished = 0
        self.fire_trace = [int((self.grid == BURNING).sum())]
        return self._obs()

    def action_mask(self):
        m = np.ones((self.n_agents, 6), dtype=bool)
        y, x = self.pos[:, 0], self.pos[:, 1]
        m[:, UP] = y > 0
        m[:, DOWN] = y < self.G - 1
        m[:, LEFT] = x > 0
        m[:, RIGHT] = x < self.G - 1
        cell = self.grid[y, x]
        droppable = (cell == BURNING) | (cell == FUEL)
        if self.drop_near_fire_only:
            # Firebreaks only make sense next to the fire; this stops payload being wasted far away.
            near = np.pad(self.grid == BURNING, 1)
            near = near[:-2, 1:-1] | near[2:, 1:-1] | near[1:-1, :-2] | near[1:-1, 2:]
            droppable = (cell == BURNING) | ((cell == FUEL) & near[y, x])
        m[:, DROP] = (self.payload > 0) & droppable
        return m

    def step(self, actions):
        a = np.asarray(actions)
        reward = 0.0
        agent_rewards = np.zeros(self.n_agents)
        phi_before = self._potential()
        # 1. Drones act (in order; two drones on one cell share it).
        for i, act in enumerate(a):
            y, x = self.pos[i]
            if act in MOVES:
                dy, dx = MOVES[act]
                self.pos[i] = (np.clip(y + dy, 0, self.G - 1), np.clip(x + dx, 0, self.G - 1))
            elif act == DROP and self.payload[i] > 0 and self.grid[y, x] in (FUEL, BURNING):
                if self.grid[y, x] == BURNING:
                    self.extinguished += 1
                    agent_rewards[i] += self.reward_extinguish
                self.grid[y, x] = WET
                self.payload[i] -= 1
                self.drops += 1
            elif act == HOLD and self._at_base(y, x):
                self.payload[i] = self.max_payload
        # 2. Fire spreads and burns out (every ``fire_every`` drone steps).
        self.steps += 1
        new = self._spread() if self.steps % self.fire_every == 0 else 0
        reward -= float(new)
        burning = int((self.grid == BURNING).sum())
        self.fire_trace.append(burning)
        terminated = burning == 0
        truncated = not terminated and self.steps >= self.max_steps
        # Training-only credit for each drone: its own extinguishes, plus potential-based
        # shaping for closing in on the fire (or on base when empty).
        agent_rewards += self.shaping * (self.shaping_gamma * self._potential() - phi_before) * 10
        info = {"burning": burning, "new_ignitions": new, "agent_rewards": agent_rewards * 0.1}
        return self._obs(), reward * 0.1, terminated, truncated, info

    def episode_metrics(self):
        lost = int(self.ignited.sum())
        return {
            "burned_cells": lost,
            "forest_saved_pct": float(100 * (1 - lost / self.G ** 2)),
            "peak_fire_cells": int(max(self.fire_trace)),
            "steps": self.steps,
            "drops": self.drops,
            "contained": float(self.fire_trace[-1] == 0),
        }

    def comm_spec(self):
        """Position columns of the observation (y/G, x/G) and the radio range in those units."""
        w = 2 * self.r + 1
        return (3 * w * w, 3 * w * w + 1), self.comm_radius / self.G

    # --- physics ------------------------------------------------------
    def _ignite(self, ys, xs):
        self.grid[ys, xs] = BURNING
        self.ignited[ys, xs] = True
        self.timer[ys, xs] = self.rng.integers(self.burn_time[0], self.burn_time[1] + 1, size=np.shape(ys))

    def _spread(self) -> int:
        burning = self.grid == BURNING
        no_ignite = np.ones(self.grid.shape)
        wy, wx = self.wind
        for dy, dx in MOVES.values():
            src = np.zeros_like(burning)
            # src[y, x] is True when the neighbour at (y - dy, x - dx) is burning, i.e. fire moves by (dy, dx).
            ys = slice(max(dy, 0), self.G + min(dy, 0))
            yd = slice(max(-dy, 0), self.G + min(-dy, 0))
            xs = slice(max(dx, 0), self.G + min(dx, 0))
            xd = slice(max(-dx, 0), self.G + min(-dx, 0))
            src[ys, xs] = burning[yd, xd]
            p = self.p_spread + (self.p_wind if (dy and dy == wy) or (dx and dx == wx) else 0.0)
            no_ignite *= 1 - p * src
        catch = (self.grid == FUEL) & (self.rng.random(self.grid.shape) > no_ignite)
        self.timer[burning] -= 1
        self.grid[burning & (self.timer <= 0)] = BURNED
        ys, xs = np.nonzero(catch)
        if len(ys):
            self._ignite(ys, xs)
        return len(ys)

    def _at_base(self, y, x) -> bool:
        d = np.array([y, x]) - self.pads
        return bool(((d >= 0) & (d < self.base_size)).all(1).any())

    def _pad_distance(self) -> tuple[np.ndarray, np.ndarray]:
        """Steps from each drone to its nearest pad, and that pad's corner (y, x)."""
        b = self.base_size - 1
        lo = self.pads[None] - self.pos[:, None]          # (drones, pads, 2): pad corner minus position
        gap = np.maximum(np.maximum(lo, 0), -(lo + b))     # 0 inside the pad along that axis
        dist = gap.sum(-1)
        k = dist.argmin(1)
        return dist[np.arange(self.n_agents), k].astype(float), self.pads[k]

    def nearest_pad(self, i: int) -> tuple[int, int]:
        return tuple(self._pad_distance()[1][i])

    def _potential(self) -> np.ndarray:
        """Minus each drone's distance (in grids) to where it should head next."""
        fy, fx = np.nonzero(self.grid == BURNING)
        y, x = self.pos[:, 0:1], self.pos[:, 1:2]
        to_base = self._pad_distance()[0]
        if len(fy):
            to_fire = (np.abs(fy[None] - y) + np.abs(fx[None] - x)).min(1).astype(float)
        else:
            to_fire = np.zeros(self.n_agents)
        dist = np.where(self.payload > 0, to_fire, to_base)
        return -dist / self.G

    # --- observations -------------------------------------------------
    def _obs(self):
        """Local windows for every drone at once (one strided view, no per-drone loop)."""
        G, r = self.G, self.r
        w = 2 * r + 1
        win = np.lib.stride_tricks.sliding_window_view
        pad = lambda arr: np.pad(arr, r, constant_values=0)
        y, x = self.pos[:, 0], self.pos[:, 1]
        fire = win(pad((self.grid == BURNING).astype(np.float32)), (w, w))[y, x]
        fuel = win(pad((self.grid == FUEL).astype(np.float32)), (w, w))[y, x]
        drones = np.zeros((G, G), dtype=np.float32)
        np.add.at(drones, (y, x), 1.0)
        others = win(pad(drones), (w, w))[y, x].copy()
        others[:, r, r] -= 1
        fy, fx = np.nonzero(self.grid == BURNING)
        if len(fy):
            d = np.abs(fy[None] - y[:, None]) + np.abs(fx[None] - x[:, None])
            j = d.argmin(1)
            near = np.stack([(fy[j] - y) / G, (fx[j] - x) / G, d[np.arange(len(y)), j] / (2 * G)], 1)
        else:
            near = np.zeros((self.n_agents, 3))
        n = self.n_agents
        return np.concatenate([
            fire.reshape(n, -1), fuel.reshape(n, -1), others.reshape(n, -1),
            np.stack([y / G, x / G, self.payload / self.max_payload], 1),
            near,
            (self._pad_distance()[1] - self.pos) / G,      # toward the nearest launch pad
            np.broadcast_to(np.asarray(self.wind, dtype=np.float32), (n, 2)),
            np.full((n, 1), len(fy) / G ** 2),
        ], axis=1).astype(np.float32)


def make_env(env_cfg: dict, split: str, seed: int) -> WildfireSwarmEnv:
    # Fires are generated, so "test" uses unseen random seeds rather than held-out data.
    cfg = {k: v for k, v in env_cfg.items() if k != "scale_pads"}
    return WildfireSwarmEnv(seed=seed, **cfg)
