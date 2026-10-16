"""HARLTON-01: hotel equipment swarm that keeps load out of the grid's peak hours.

In Ontario, a Class A customer pays the Global Adjustment by its share of the
grid's top five demand hours of the year. Every flexible load in the five
sample hotels (chillers, laundry, EV chargers, pool heating) is an agent. Each
sees the grid signal that an operator has in real time (current grid load,
the day-ahead forecast of today's peak, weather, time) and its own state, and
chooses to run early (pre-cool, pre-heat, catch up), run normally, or shed
(coast on stored cooling or heat, defer a cycle).

The team reward is the load the hotels take off the grid's peak hours, minus a
small charge for the extra energy that shifting uses and a penalty for
laundry or EV charging left unfinished at the end of a day.
"""

import numpy as np
import pandas as pd

from swarm.env import SwarmEnv

from . import loads as L

EARLY, NORMAL, SHED = 0, 1, 2

_CACHE: dict = {}


def _season(path, months, test_weeks):
    from apps.energy import data as D  # the grid signal and weather come from the energy pipeline

    key = (str(path), tuple(months), test_weeks)
    if key not in _CACHE:
        df = D.load(path)
        df = df[df.timestamp.dt.month.isin(months)].copy()
        days = df.timestamp.dt.normalize()
        full = days.map(days.value_counts()) == 24  # whole days only
        df = df[full.to_numpy()].reset_index(drop=True)
        week = df.timestamp.dt.isocalendar().week.to_numpy()
        is_test = (week % 2 == 1) if test_weeks == "odd" else (week % 2 == 0)
        train, test = df[~is_test].reset_index(drop=True), df[is_test].reset_index(drop=True)
        daily_max = train.groupby(train.timestamp.dt.date)["load_mw"].max()
        stats = {c: (train[c].mean(), train[c].std() + 1e-6) for c in ["load_mw", "temp_c"]}
        stats["day_max"] = (float(daily_max.quantile(0.8)), float(daily_max.std() + 1e-6))
        # The 4-hour window holding most of the training days' top-40 grid hours (for the rules).
        top_hours = train.timestamp.dt.hour.to_numpy()[np.argsort(-train.load_mw.to_numpy())[:40]]
        counts = np.bincount(top_hours, minlength=24)
        start = int(np.argmax([counts[h:h + 4].sum() for h in range(21)]))
        stats["peak_window"] = (start, start + 4)
        _CACHE[key] = (train, test, stats)
    return _CACHE[key]


class HotelEnergySwarmEnv(SwarmEnv):
    n_actions = 3

    def __init__(self, frame: pd.DataFrame, stats: dict, hotels_csv=None, episode_days=1, peak_hours=40,
                 ga_cost_per_kw_year=450.0, energy_price_kwh=0.11, energy_weight=0.02, miss_penalty=2.0, forecast_noise=0.02, seed=0):
        self.fleet = L.build_fleet(hotels_csv)
        self.n_agents = self.fleet.n
        self.episode_days = int(episode_days) if episode_days else None
        self.ga_cost = float(ga_cost_per_kw_year)
        self.energy_price = float(energy_price_kwh)
        self.energy_weight = float(energy_weight)
        self.miss_penalty = float(miss_penalty)
        self.rng = np.random.default_rng(seed)

        ts = frame["timestamp"]
        self.timestamps = ts.to_numpy()
        self.grid = frame["load_mw"].to_numpy(np.float64)
        self.hour = ts.dt.hour.to_numpy()
        dow = ts.dt.dayofweek.to_numpy()
        self.n_days = len(frame) // 24
        self.base = L.baseline_kw(self.fleet, ts, frame["temp_c"].to_numpy())       # (T, n)
        self.hotel_base = L.hotel_base_kw(self.fleet, ts)                            # (T, H)

        # Day-ahead forecast of today's grid peak (what the IESO Peak Tracker gives an operator).
        day_max = self.grid.reshape(self.n_days, 24).max(1)
        noise = np.random.default_rng(12_345).normal(0.0, forecast_noise, self.n_days)
        self.forecast_max = np.repeat(day_max * (1 + noise), 24)
        self.alert_level = stats["day_max"][0]  # 80th percentile of training days' peaks
        self.peak_window = stats["peak_window"]

        # Training credit goes to the split's top ``peak_hours`` grid hours.
        self.peak_w = np.zeros(len(self.grid))
        self.peak_w[np.argsort(-self.grid)[:peak_hours]] = 1.0

        z = lambda c: (frame[c].to_numpy() - stats[c][0]) / stats[c][1]
        self.grid_features = np.stack([
            z("load_mw"),
            self.grid / self.forecast_max,
            (self.forecast_max - stats["day_max"][0]) / stats["day_max"][1],
            z("temp_c"),
            np.sin(2 * np.pi * self.hour / 24), np.cos(2 * np.pi * self.hour / 24),
            np.sin(2 * np.pi * dow / 7), np.cos(2 * np.pi * dow / 7),
            (dow >= 5).astype(float),
        ], axis=1).astype(np.float32)
        f = self.fleet
        self.static = np.concatenate([
            np.eye(len(L.TYPES))[f.kind],
            (f.power / f.power.max())[:, None],
            (f.rooms / f.rooms.max())[:, None],
        ], axis=1).astype(np.float32)
        self.obs_dim = self.grid_features.shape[1] + self.static.shape[1] + 3
        self.scale = f.power.sum()
        self.t = self.start = self.end = 0
        self.e = np.zeros(self.n_agents)

    # --- SwarmEnv API -------------------------------------------------
    def reset(self, seed=None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        if self.episode_days and self.episode_days < self.n_days:
            d = int(self.rng.integers(0, self.n_days - self.episode_days + 1))
            self.start, self.end = 24 * d, 24 * (d + self.episode_days)
        else:
            self.start, self.end = 0, 24 * self.n_days
        self.t = self.start
        self.e = np.zeros(self.n_agents)
        self._delta, self._missed = [], 0.0
        return self._obs()

    def _rooms(self):
        """kWh each agent could move up (run early) and down (shed) this hour."""
        t = min(self.t, len(self.grid) - 1)  # the mask is also read once after the last step
        f, b = self.fleet, self.base[t]
        up = np.where(f.deadline, np.maximum(0.0, -self.e), np.maximum(0.0, (f.e_max - self.e) / f.eta))
        up = np.minimum(f.power, up)
        down = np.minimum.reduce([f.power, b, np.maximum(0.0, self.e - f.e_min)])
        return up, down

    def action_mask(self):
        f = self.fleet
        up, down = self._rooms()
        hours_after = 23 - self.hour[min(self.t, len(self.grid) - 1)]  # hours left in the day after this one
        m = np.ones((self.n_agents, 3), dtype=bool)
        m[:, EARLY] = up > 1e-6
        # A deadline load may only defer what it can still catch up today.
        can_catch_up = -(self.e - down) <= f.power * hours_after + 1e-6
        m[:, SHED] = (down > 1e-6) & (~f.deadline | can_catch_up)
        must_catch_up = f.deadline & (-self.e > f.power * hours_after + 1e-6)
        m[must_catch_up, NORMAL] = False
        m[must_catch_up, SHED] = False
        m[must_catch_up, EARLY] = True
        return m

    def step(self, actions):
        a = np.asarray(actions)
        f = self.fleet
        up, down = self._rooms()
        p_up = np.where(a == EARLY, up, 0.0)
        p_dn = np.where(a == SHED, down, 0.0)
        self.e = self.e + p_up * f.eta - p_dn
        self.e = np.where(self.e > 0, self.e * (1 - f.leak), self.e)  # stored cooling or heat drifts away
        delta = float((p_up - p_dn).sum())  # kW added to (+) or taken off (-) the hotels' load

        reward = -(delta * self.peak_w[self.t] + self.energy_weight * delta) / self.scale
        self._delta.append(delta)
        if self.hour[self.t] == 23:
            backlog = -self.e[f.deadline]
            missed = float(backlog[backlog > 1e-6].sum())
            self._missed += missed
            reward -= self.miss_penalty * missed / self.scale
            self.e[f.deadline] = 0.0

        self.t += 1
        terminated = self.t >= self.end and self.end == 24 * self.n_days
        truncated = self.t >= self.end and not terminated
        info = {"delta_kw": delta}
        return self._obs(min(self.t, len(self.grid) - 1)), float(reward), terminated, truncated, info

    def episode_metrics(self):
        d = np.asarray(self._delta)
        if len(d) == 0:
            return {}
        sl = slice(self.start, self.start + len(d))
        grid = self.grid[sl]
        total = self.base[sl].sum(1) + self.hotel_base[sl].sum(1)
        top5 = np.argsort(-grid)[:5]
        top20 = np.argsort(-grid)[:20]
        cut5 = float(-d[top5].mean())
        # energy used by shifting (losses), counting pool heat still owed at the end
        extra = float(d.sum() + np.maximum(0.0, -self.e[~self.fleet.deadline]).sum())
        return {
            "peak_cut_kw": cut5,                                  # mean cut over the grid's top 5 hours
            "peak_cut_pct": float(100 * cut5 / total[top5].mean()),
            "top20_cut_kw": float(-d[top20].mean()),
            "peaks_hit": int((d[top5] < -1e-6).sum()),            # of the 5
            "ga_saving_usd": self.ga_cost * cut5,                 # per year at the configured $/kW-year
            "extra_kwh": extra,
            "extra_energy_usd": self.energy_price * extra,
            "net_saving_usd": self.ga_cost * cut5 - self.energy_price * extra,
            "missed_kwh": self._missed,                           # laundry/EV work left undone
            "days": len(d) // 24,
        }

    # --- helpers ------------------------------------------------------
    def _obs(self, t=None):
        t = self.t if t is None else t
        f = self.fleet
        span = np.maximum(f.e_max - f.e_min, 1e-6)
        hours_after = 23 - self.hour[t]
        own = np.stack([
            self.e / span,
            self.base[t] / f.power,
            np.where(f.deadline, hours_after / 23.0, 0.0),
        ], axis=1)
        shared = np.broadcast_to(self.grid_features[t], (self.n_agents, self.grid_features.shape[1]))
        return np.concatenate([shared, self.static, own], axis=1).astype(np.float32)


def make_env(env_cfg: dict, split: str, seed: int) -> HotelEnergySwarmEnv:
    cfg = dict(env_cfg)
    train, test, stats = _season(cfg.pop("data_path", None), cfg.pop("months", [6, 7, 8, 9]),
                                 cfg.pop("test_weeks", "odd"))
    frame = train if split == "train" else test
    if split != "train":
        cfg["episode_days"] = cfg.get("eval_episode_days")  # None = every held-out day in one run
    cfg.pop("eval_episode_days", None)
    return HotelEnergySwarmEnv(frame, stats, seed=seed, **cfg)
