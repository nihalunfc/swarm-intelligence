"""Adapter: CityLearn's decentralized environment behind the ``SwarmEnv`` interface.

* Agents: one per building (17 homes), each controlling its battery.
* Actions: 7 discrete battery set-points (share of capacity charged, + , or
  discharged, -, this hour), ``LEVELS``.
* Observation (per home, scaled to [0, 1] with CityLearn's own bounds): hour,
  day type, temperature, solar irradiance, carbon intensity, the home's load,
  solar output, battery charge and net consumption, and the electricity price
  now and for the next three hours.
* Team reward (training only): minus the district's electricity cost, carbon
  emissions and ramping this hour, each divided by its average without
  batteries, so the three challenge goals weigh equally.
* Splits (the challenge year, hourly): January-August trains, September
  validates, October-December is the test.
* Metrics: CityLearn's own district KPIs from ``env.evaluate()`` and
  ``score``, the 2022 challenge average of cost, emissions and grid
  (mean of ramping and 1 - load factor). Lower is better for all of them.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from swarm.env import SwarmEnv

LEVELS = np.array([-0.2, -0.1, -0.05, 0.0, 0.05, 0.1, 0.2])
IDLE = 3
SPLITS = {"train": (0, 5831), "val": (5832, 6551), "test": (6552, 8759)}
FEATURES = ["hour", "day_type", "outdoor_dry_bulb_temperature", "direct_solar_irradiance", "diffuse_solar_irradiance",
            "carbon_intensity", "non_shiftable_load", "solar_generation", "electrical_storage_soc",
            "net_electricity_consumption", "electricity_pricing", "electricity_pricing_predicted_1",
            "electricity_pricing_predicted_2", "electricity_pricing_predicted_3"]
# Averages per hour without batteries on the training months (district totals), for reward scaling.
SCALE = {"cost": 3.61, "carbon": 1.84, "ramp": 4.17}
KPIS = {"cost_total": "cost_total", "carbon_emissions_total": "carbon_emissions_total",
        "ramping_average": "ramping_average", "daily_peak_average": "daily_peak_average",
        "one_minus_load_factor": "daily_one_minus_load_factor_average"}
KEY_METRICS = ["score", "cost_total", "carbon_emissions_total", "ramping_average", "daily_peak_average",
               "one_minus_load_factor"]
REPO = Path(__file__).resolve().parents[2]


def _schema(path):
    if path:
        return str(path)
    local = REPO / "data" / "citylearn" / "citylearn_challenge_2022_phase_all" / "schema.json"
    if not local.exists():
        from .download import download

        download()
    return str(local)


class CityLearnSwarmEnv(SwarmEnv):
    n_actions = len(LEVELS)
    null_action = IDLE

    def __init__(self, schema=None, split="train", seed=0):
        from citylearn.citylearn import CityLearnEnv

        start, end = SPLITS[split]
        self.env = CityLearnEnv(_schema(schema), central_agent=False, simulation_start_time_step=start,
                                simulation_end_time_step=end, random_seed=seed)
        names = self.env.observation_names[0]
        self.idx = [names.index(f) for f in FEATURES]
        space = self.env.observation_space
        self.lo = np.array([s.low[self.idx] for s in space], dtype=np.float32)
        self.hi = np.array([s.high[self.idx] for s in space], dtype=np.float32)
        self.n_agents = len(self.env.buildings)
        self.obs_dim = len(FEATURES)
        self.override = None  # continuous actions from a CityLearn controller (rules)
        self._raw = None

    def _obs(self, raw):
        self._raw = np.asarray(raw, dtype=np.float32)
        x = (self._raw[:, self.idx] - self.lo) / np.maximum(self.hi - self.lo, 1e-6)
        return np.clip(x, -1.0, 2.0).astype(np.float32)

    def reset(self, seed=None):
        out = self.env.reset()
        raw = out[0] if isinstance(out, tuple) else out
        self.prev_net = None
        return self._obs(raw)

    def raw(self, name: str) -> np.ndarray:
        """One raw observation for every home (e.g. 'hour')."""
        return self._raw[:, self.env.observation_names[0].index(name)]

    def step(self, actions):
        if self.override is not None:
            act, self.override = [[float(a)] for a in self.override], None
        else:
            act = [[float(LEVELS[a])] for a in np.asarray(actions)]
        raw, _, term, trunc, info = self.env.step(act)
        obs = self._obs(raw)
        net = self.raw("net_electricity_consumption")
        district = float(net.sum())
        price, ci = float(self.raw("electricity_pricing")[0]), float(self.raw("carbon_intensity")[0])
        pos = float(np.maximum(net, 0).sum())
        ramp = 0.0 if self.prev_net is None else abs(district - self.prev_net)
        self.prev_net = district
        reward = -(pos * price / SCALE["cost"] + pos * ci / SCALE["carbon"] + ramp / SCALE["ramp"]) / 3.0
        done = bool(term or self.env.terminated)
        return obs, reward, done, False, {}

    def episode_metrics(self):
        k = self.env.evaluate()
        d = k[k["level"] == "district"].set_index("cost_function")["value"]
        m = {name: float(d[src]) for name, src in KPIS.items()}
        m["score"] = float(np.mean([m["cost_total"], m["carbon_emissions_total"],
                                    np.mean([m["ramping_average"], m["one_minus_load_factor"]])]))
        return m


def make_env(env_cfg: dict, split: str, seed: int) -> CityLearnSwarmEnv:
    return CityLearnSwarmEnv(env_cfg.get("schema"), "val" if split == "val" else split, seed)


# --- reference controllers --------------------------------------------------
def no_battery(env, obs, mask):
    return np.full(env.n_agents, IDLE)


def optimized_rbc(env, obs, mask):
    """CityLearn's ``OptimizedRBC`` battery schedule (charge at night, discharge by day)."""
    out = []
    for hour in env.raw("hour"):
        h = int(hour)
        v = (-0.02 if 7 <= h <= 15 else -0.044 if 16 <= h <= 18 else -0.024 if 19 <= h <= 22
             else 0.034 if 23 <= h <= 24 else 0.05532 if 1 <= h <= 6 else 0.0)
        out.append(v)
    env.override = out
    return np.full(env.n_agents, IDLE)


def basic_rbc(env, obs, mask):
    """CityLearn's ``BasicRBC``: charge 9.1% of capacity 22:00-08:00, discharge 8% otherwise."""
    h = env.raw("hour").astype(int)
    env.override = list(np.where((h >= 22) | (h <= 8), 0.091, -0.08))
    return np.full(env.n_agents, IDLE)


BASELINES = {"no battery": no_battery, "CityLearn BasicRBC": basic_rbc, "CityLearn OptimizedRBC": optimized_rbc}
