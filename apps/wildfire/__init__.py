"""Wildfire application: a drone swarm containing fire on a forest grid."""

from .baselines import BASELINES
from .env import WildfireSwarmEnv, make_env
from .replay import export_replay

KEY_METRICS = ["forest_saved_pct", "burned_cells", "peak_fire_cells", "contained", "return"]

__all__ = ["scaled_env_cfg", "BASELINES", "KEY_METRICS", "WildfireSwarmEnv", "export_replay", "make_env"]


def scaled_env_cfg(env_cfg: dict, n: int) -> dict:
    """``n`` drones on a forest grown to keep the trained drones-per-cell density,
    with ignitions and time limit growing with it.

    Launch pads: by default the single pad grows (the original study, where
    refill trips get long). With ``scale_pads: true`` the forest is tiled with
    more pads of the trained size instead, so every drone keeps the same
    distance to a pad as in training.
    """
    n0, g0 = int(env_cfg.get("n_drones", 6)), int(env_cfg.get("grid_size", 16))
    k = (n / n0) ** 0.5
    out = {**env_cfg, "n_drones": n, "grid_size": max(g0, round(g0 * k)),
           "n_ignitions": max(1, round(int(env_cfg.get("n_ignitions", 2)) * k * k)),
           "max_steps": round(int(env_cfg.get("max_steps", 300)) * max(1.0, k))}
    if env_cfg.get("scale_pads"):
        p0 = int(env_cfg.get("pads_per_side", 1))
        out["pads_per_side"] = max(p0, round(p0 * k))
        out["grid_size"] = max(g0, out["pads_per_side"] * (g0 // p0))  # whole tiles of the trained size
    else:
        out["base_size"] = max(3, round(3 * k))
    return out
