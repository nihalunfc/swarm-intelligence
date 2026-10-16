"""H2-03 + HARLTON-03: room attendants as a swarm that gets rooms ready before guests arrive."""

from .baselines import BASELINES
from .env import HousekeepingSwarmEnv, make_env

KEY_METRICS = ["guest_wait_hours", "early_promises_kept_pct", "ready_by_noon_pct", "workload_spread", "floor_changes"]

__all__ = ["BASELINES", "HousekeepingSwarmEnv", "KEY_METRICS", "make_env"]
