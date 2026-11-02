"""VMAS navigation: a standard multi-agent RL testbed for checking the engine.

VMAS (Bettini et al., 2022) is a vectorized multi-robot simulator used by the
BenchMARL benchmark. In ``navigation`` each robot must reach its own goal
without collisions, seeing its position, velocity, goal offset and a short
range lidar. Discrete actions (9 moves) are used, which our engine supports.

Needs ``pip install vmas``.
"""

from .env import BASELINES, KEY_METRICS, VmasSwarmEnv, make_env

__all__ = ["BASELINES", "KEY_METRICS", "VmasSwarmEnv", "make_env"]
