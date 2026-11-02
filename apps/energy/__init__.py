"""Energy grid application: a battery swarm flattening ERCOT COAST load."""

from .baselines import BASELINES
from .env import EnergySwarmEnv, make_env

KEY_METRICS = ["par_after", "peak_reduction_mw", "std_reduction_pct", "return"]

__all__ = ["scaled_env_cfg", "BASELINES", "EnergySwarmEnv", "KEY_METRICS", "make_env"]


def scaled_env_cfg(env_cfg: dict, n: int) -> dict:
    """The same fleet (total MW and MWh) split into ``n`` batteries."""
    n0 = int(env_cfg.get("n_agents", 10))
    cap, rate = float(env_cfg.get("capacity_mwh", 400.0)), float(env_cfg.get("max_rate_mw", 100.0))
    return {**env_cfg, "n_agents": n, "capacity_mwh": cap * n0 / n, "max_rate_mw": rate * n0 / n}
