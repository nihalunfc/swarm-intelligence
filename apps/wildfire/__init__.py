"""Wildfire application: a drone swarm containing fire on a forest grid."""

from .baselines import BASELINES
from .env import WildfireSwarmEnv, make_env
from .replay import export_replay

KEY_METRICS = ["forest_saved_pct", "burned_cells", "peak_fire_cells", "contained", "return"]

__all__ = ["BASELINES", "KEY_METRICS", "WildfireSwarmEnv", "export_replay", "make_env"]
