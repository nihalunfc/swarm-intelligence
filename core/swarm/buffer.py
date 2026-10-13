"""Preallocated replay buffer storing whole-swarm (n-step) transitions."""

import numpy as np


class ReplayBuffer:
    def __init__(self, capacity: int, n_agents: int, obs_dim: int, n_actions: int, seed: int = 0):
        self.capacity = capacity
        self.obs = np.zeros((capacity, n_agents, obs_dim), dtype=np.float32)
        self.next_obs = np.zeros((capacity, n_agents, obs_dim), dtype=np.float32)
        self.actions = np.zeros((capacity, n_agents), dtype=np.int64)
        self.rewards = np.zeros(capacity, dtype=np.float32)
        self.agent_rewards = np.zeros((capacity, n_agents), dtype=np.float32)
        self.discount = np.zeros(capacity, dtype=np.float32)  # gamma**n, or 0 at a true episode end
        self.next_mask = np.ones((capacity, n_agents, n_actions), dtype=bool)
        self.pos = 0
        self.size = 0
        self.rng = np.random.default_rng(seed)

    def push(self, obs, actions, reward, next_obs, discount, next_mask, agent_rewards=None):
        i = self.pos
        self.obs[i] = obs
        self.actions[i] = actions
        self.rewards[i] = reward
        self.agent_rewards[i] = 0.0 if agent_rewards is None else agent_rewards
        self.next_obs[i] = next_obs
        self.discount[i] = discount
        self.next_mask[i] = next_mask
        self.pos = (self.pos + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def sample(self, batch_size: int) -> dict:
        idx = self.rng.integers(0, self.size, size=batch_size)
        return {
            "obs": self.obs[idx],
            "actions": self.actions[idx],
            "rewards": self.rewards[idx],
            "agent_rewards": self.agent_rewards[idx],
            "next_obs": self.next_obs[idx],
            "discount": self.discount[idx],
            "next_mask": self.next_mask[idx],
        }

    def __len__(self) -> int:
        return self.size
