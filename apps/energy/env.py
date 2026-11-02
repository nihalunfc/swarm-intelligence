"""Battery swarm on the ERCOT COAST grid.

Each agent is one battery. It sees the grid signal (load, weather, time of day,
how far load is from today's flat level), its own state of charge and the
swarm's average state of charge, and chooses charge, idle or discharge. The
team reward is how much closer the net load gets to the day's flat level,
so peaks are shaved and troughs are filled.
"""

import numpy as np
from swarm.env import SwarmEnv

from . import data as D

CHARGE, IDLE, DISCHARGE = 0, 1, 2

_CACHE: dict = {}


def _prepared(path, test_start, val_start=None):
    """Chronological train / validation / test frames and the training-set scaling.

    With ``val_start`` the months between it and ``test_start`` are a validation
    period used to choose settings and checkpoints; test is only for the final report.
    """
    key = (str(path), test_start, val_start)
    if key not in _CACHE:
        df = D.load(path)
        df["target_mw"] = D.day_mean_target(df)
        train, test = D.split(df, test_start)
        val = None
        if val_start:
            train, val = D.split(train, val_start)
        cols = ["load_mw", "ghi", "temp_c", "wind_ms"]
        stats = {c: (train[c].mean(), train[c].std() + 1e-6) for c in cols}
        _CACHE[key] = (train, val, test, stats)
    return _CACHE[key]


class EnergySwarmEnv(SwarmEnv):
    n_actions = 3
    null_action = IDLE  # a failed battery sits idle (robustness tests)

    def __init__(self, frame, stats, n_agents=10, capacity_mwh=400.0, max_rate_mw=100.0,
                 round_trip_efficiency=0.90, initial_soc=0.5, episode_hours=168, seed=0):
        self.n_agents = int(n_agents)
        self.capacity = float(capacity_mwh)
        self.rate = float(max_rate_mw)
        self.eta = float(np.sqrt(round_trip_efficiency))  # one-way efficiency
        self.initial_soc = float(initial_soc)
        self.episode_hours = int(episode_hours) if episode_hours else None
        self.rng = np.random.default_rng(seed)

        # Arrays instead of DataFrame lookups: one row read per step is a slice, not iloc.
        self.load = frame["load_mw"].to_numpy(np.float64)
        self.target = frame["target_mw"].to_numpy(np.float64)
        self.timestamps = frame["timestamp"].to_numpy()
        hour = frame["timestamp"].dt.hour.to_numpy()
        dow = frame["timestamp"].dt.dayofweek.to_numpy()
        z = lambda c: (frame[c].to_numpy() - stats[c][0]) / stats[c][1]
        self.fleet_mw = self.n_agents * self.rate
        self.grid_features = np.stack([
            z("load_mw"),
            (self.load - self.target) / self.fleet_mw / 5.0,
            z("ghi"), z("temp_c"), z("wind_ms"),
            np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24),
            np.sin(2 * np.pi * dow / 7), np.cos(2 * np.pi * dow / 7),
        ], axis=1).astype(np.float32)
        self.obs_dim = self.grid_features.shape[1] + 2
        self.t = self.start = self.end = 0
        self.energy = np.zeros(self.n_agents)

    # --- SwarmEnv API -------------------------------------------------
    def reset(self, seed=None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        n = len(self.load)
        if self.episode_hours and self.episode_hours < n:
            self.start = int(self.rng.integers(0, n - self.episode_hours))
            self.end = self.start + self.episode_hours
        else:
            self.start, self.end = 0, n
        self.t = self.start
        self.energy = np.full(self.n_agents, self.initial_soc * self.capacity)
        self._orig, self._net = [], []
        return self._obs()

    def action_mask(self):
        m = np.ones((self.n_agents, 3), dtype=bool)
        m[:, CHARGE] = self.energy < self.capacity - 1e-6
        m[:, DISCHARGE] = self.energy > 1e-6
        return m

    def step(self, actions):
        a = np.asarray(actions)
        charge = a == CHARGE
        discharge = a == DISCHARGE
        draw = np.where(charge, np.minimum(self.rate, (self.capacity - self.energy) / self.eta), 0.0)
        removed = np.where(discharge, np.minimum(self.rate, self.energy), 0.0)
        self.energy = np.clip(self.energy + draw * self.eta - removed, 0.0, self.capacity)
        net_battery_mw = draw.sum() - removed.sum() * self.eta

        load, target = self.load[self.t], self.target[self.t]
        net = load + net_battery_mw
        reward = ((load - target) ** 2 - (net - target) ** 2) / self.fleet_mw ** 2
        self._orig.append(load)
        self._net.append(net)

        self.t += 1
        terminated = self.t >= self.end and self.end == len(self.load)
        truncated = self.t >= self.end and not terminated
        info = {"original_load": load, "net_load": net, "net_battery_mw": net_battery_mw,
                "avg_soc": float(self.energy.mean() / self.capacity)}
        obs = self._obs(min(self.t, len(self.load) - 1))
        return obs, float(reward), terminated, truncated, info

    def episode_metrics(self):
        o, n = np.asarray(self._orig), np.asarray(self._net)
        if len(o) == 0:
            return {}
        return {
            "par_before": float(o.max() / o.mean()),
            "par_after": float(n.max() / n.mean()),
            "peak_reduction_mw": float(o.max() - n.max()),
            "std_reduction_pct": float(100 * (1 - n.std() / o.std())),
            "hours": len(o),
        }

    # --- helpers ------------------------------------------------------
    def _obs(self, t=None):
        t = self.t if t is None else t
        soc = self.energy / self.capacity
        shared = np.broadcast_to(self.grid_features[t], (self.n_agents, self.grid_features.shape[1]))
        return np.concatenate([shared, soc[:, None], np.full((self.n_agents, 1), soc.mean())], axis=1).astype(np.float32)


def make_env(env_cfg: dict, split: str, seed: int) -> EnergySwarmEnv:
    cfg = dict(env_cfg)
    train, val, test, stats = _prepared(cfg.pop("data_path", None), cfg.pop("test_start", None),
                                        cfg.pop("val_start", None))
    if split == "val" and val is None:
        raise ValueError("energy: set env.val_start to evaluate on a validation period")
    frame = {"train": train, "val": val}.get(split, test)
    if split != "train":
        cfg["episode_hours"] = cfg.get("eval_episode_hours")  # None = the whole held-out period
    cfg.pop("eval_episode_hours", None)
    return EnergySwarmEnv(frame, stats, seed=seed, **cfg)
