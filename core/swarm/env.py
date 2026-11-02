"""The interface every swarm application implements.

A swarm environment holds ``n_agents`` identical agents. Each agent sees only its
own local observation and picks one of ``n_actions`` discrete actions. The swarm
shares one team reward, which is what the agents learn to maximise together.
"""

from abc import ABC, abstractmethod

import numpy as np


class SwarmEnv(ABC):
    n_agents: int
    n_actions: int
    obs_dim: int

    @abstractmethod
    def reset(self, seed: int | None = None) -> np.ndarray:
        """Start an episode. Returns local observations, shape (n_agents, obs_dim)."""

    @abstractmethod
    def step(self, actions: np.ndarray) -> tuple[np.ndarray, float, bool, bool, dict]:
        """Apply one action per agent. Returns (obs, team_reward, terminated, truncated, info).

        ``terminated`` means the episode really ended (no future value);
        ``truncated`` means it was cut off by a time limit.

        ``info["agent_rewards"]`` (optional, shape (n_agents,)) carries
        per-agent shaping used only during training, e.g. credit to the drone
        that extinguished a cell. Reported returns use the team reward only.
        """

    def action_mask(self) -> np.ndarray:
        """Boolean (n_agents, n_actions): which actions are valid right now."""
        return np.ones((self.n_agents, self.n_actions), dtype=bool)

    def episode_metrics(self) -> dict:
        """Application KPIs for the episode just played (e.g. peak reduction)."""
        return {}
