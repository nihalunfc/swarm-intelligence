"""Wildfire application: a drone swarm containing fire on a forest grid."""

from .baselines import BASELINES
from .env import WildfireSwarmEnv, make_env
from .replay import export_replay

KEY_METRICS = ["forest_saved_pct", "burned_cells", "peak_fire_cells", "contained", "return"]

__all__ = ["scaled_env_cfg", "BASELINES", "KEY_METRICS", "WildfireSwarmEnv", "export_replay", "make_env"]


def scaled_env_cfg(env_cfg: dict, n: int) -> dict:
    """``n`` drones on a forest grown to keep the trained drones-per-cell density,
    with ignitions, launch pad and time limit growing with it."""
    n0, g0 = int(env_cfg.get("n_drones", 6)), int(env_cfg.get("grid_size", 16))
    k = (n / n0) ** 0.5
    return {**env_cfg, "n_drones": n, "grid_size": max(g0, round(g0 * k)),
            "n_ignitions": max(1, round(int(env_cfg.get("n_ignitions", 2)) * k * k)),
            "base_size": max(3, round(3 * k)), "max_steps": round(int(env_cfg.get("max_steps", 300)) * max(1.0, k))}
