"""Energy grid application: a battery swarm flattening ERCOT COAST load."""

from .baselines import BASELINES
from .env import EnergySwarmEnv, make_env

KEY_METRICS = ["par_after", "peak_reduction_mw", "std_reduction_pct", "return"]

__all__ = ["BASELINES", "EnergySwarmEnv", "KEY_METRICS", "make_env"]
