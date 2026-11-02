"""Adapter: one VMAS scenario (default ``navigation``) behind ``SwarmEnv``."""

from __future__ import annotations

import numpy as np
from swarm.env import SwarmEnv

KEY_METRICS = ["success", "return", "collisions"]


class VmasSwarmEnv(SwarmEnv):
    null_action = 0

    def __init__(self, scenario="navigation", n_agents=4, max_steps=100, seed=0, **kwargs):
        import torch
        import vmas

        self.torch = torch
        self.env = vmas.make_env(scenario, num_envs=1, continuous_actions=False, n_agents=int(n_agents),
                                 max_steps=int(max_steps), seed=seed, device="cpu", **kwargs)
        self.n_agents = int(n_agents)
        self.n_actions = int(self.env.action_space[0].n)
        self.obs_dim = int(self.env.observation_space[0].shape[0])
        self.max_steps = int(max_steps)
        self._directions = None

    def _np(self, obs):
        return np.stack([o[0].numpy() for o in obs]).astype(np.float32)

    def reset(self, seed=None):
        if seed is not None:
            self.env.seed(int(seed))
        self.t, self.ret, self.success, self.collisions = 0, 0.0, 0.0, 0.0
        self.obs = self._np(self.env.reset())
        return self.obs

    def step(self, actions):
        acts = [self.torch.tensor([int(a)]) for a in np.asarray(actions)]
        obs, rews, dones, info = self.env.step(acts)
        r = float(sum(float(x[0]) for x in rews))
        self.ret += r
        self.t += 1
        # VMAS reports collisions as a (negative) penalty; count them instead.
        self.collisions += float(sum(float(i.get("agent_collisions", self.torch.zeros(1))[0]) < 0 for i in info))
        self.obs = self._np(obs)
        done = bool(dones[0])
        if done and self.t < self.max_steps:  # VMAS ends navigation early once every robot is on its goal
            self.success = 1.0
        return self.obs, r, False, done, {}

    def episode_metrics(self):
        return {"success": self.success, "collisions": self.collisions, "steps": float(self.t)}

    def directions(self) -> np.ndarray:
        """Unit direction of every discrete action, measured once by trying each in a 1-robot copy."""
        if self._directions is None:
            probe = VmasSwarmEnv(n_agents=1, max_steps=10)
            d = []
            for a in range(self.n_actions):
                p0 = probe.reset(seed=0)[0, :2].copy()
                for _ in range(3):
                    o, *_ = probe.step([a])
                d.append(o[0, :2] - p0)
            d = np.array(d, float)
            n = np.linalg.norm(d, axis=1, keepdims=True)
            self._directions = np.divide(d, n, out=np.zeros_like(d), where=n > 1e-9)
        return self._directions


def make_env(env_cfg: dict, split: str, seed: int) -> VmasSwarmEnv:
    # Episodes are generated; evaluation uses unseen seeds.
    return VmasSwarmEnv(seed=seed, **env_cfg)


def no_op(env, obs, mask):
    return np.zeros(env.n_agents, dtype=int)


def random_move(env, obs, mask):
    return np.random.default_rng(env.t).integers(0, env.n_actions, env.n_agents)


def go_to_goal(env, obs, mask):
    """Head straight for the goal, braking when close (observation columns 4:6 are position minus goal)."""
    goal = -obs[:, 4:6]
    vel = obs[:, 2:4]
    want = goal - 0.5 * vel
    d = env.directions()
    acts = (want @ d.T).argmax(1)
    acts[np.linalg.norm(goal, axis=1) < 0.05] = 0
    return acts


BASELINES = {"no-op": no_op, "random": random_move, "go to goal": go_to_goal}
