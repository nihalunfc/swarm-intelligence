"""Preallocated replay buffer storing whole-swarm transitions."""

import numpy as np


class ReplayBuffer:
    def __init__(self, capacity: int, n_agents: int, obs_dim: int, n_actions: int, seed: int = 0):
        self.capacity = capacity
        self.obs = np.zeros((capacity, n_agents, obs_dim), dtype=np.float32)
        self.next_obs = np.zeros((capacity, n_agents, obs_dim), dtype=np.float32)
        self.actions = np.zeros((capacity, n_agents), dtype=np.int64)
        self.rewards = np.zeros(capacity, dtype=np.float32)
        self.terminated = np.zeros(capacity, dtype=np.float32)
        self.next_mask = np.ones((capacity, n_agents, n_actions), dtype=bool)
        self.pos = 0
        self.size = 0
        self.rng = np.random.default_rng(seed)

    def push(self, obs, actions, reward, next_obs, terminated, next_mask):
        i = self.pos
        self.obs[i] = obs
        self.actions[i] = actions
        self.rewards[i] = reward
        self.next_obs[i] = next_obs
        self.terminated[i] = float(terminated)
        self.next_mask[i] = next_mask
        self.pos = (self.pos + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def sample(self, batch_size: int) -> dict:
        idx = self.rng.integers(0, self.size, size=batch_size)
        return {
            "obs": self.obs[idx],
            "actions": self.actions[idx],
            "rewards": self.rewards[idx],
            "next_obs": self.next_obs[idx],
            "terminated": self.terminated[idx],
            "next_mask": self.next_mask[idx],
        }

    def __len__(self) -> int:
        return self.size
