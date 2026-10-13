"""Decentralized swarm agent with shared parameters.

Every agent runs the same small Q-network on its own local observation, so
each agent decides for itself. All agents (and all parallel environment
copies) are evaluated together in one batched forward pass. The network's
size does not depend on the number of agents, unlike a joint-action network
whose output layer needs one unit per combination (n_actions ** n_agents).

Training uses n-step returns and one of two value schemes for the shared team reward:

* ``vdn`` (default): Value Decomposition Networks. The team value is the sum
  of each agent's chosen Q-value, so agents learn credit for the team result.
* ``independent``: each agent treats the team reward as its own (IQL).

Double-DQN targets, a soft-updated target network and action masks are used
in both cases.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def _mlp(in_dim: int, hidden: list[int], out_dim: int) -> nn.Sequential:
    layers, d = [], in_dim
    for h in hidden:
        layers += [nn.Linear(d, h), nn.ReLU()]
        d = h
    layers.append(nn.Linear(d, out_dim))
    return nn.Sequential(*layers)


class SharedQNetwork(nn.Module):
    def __init__(self, obs_dim: int, n_actions: int, n_agents: int, hidden: list[int], agent_id: bool):
        super().__init__()
        self.n_agents = n_agents
        self.agent_id = agent_id
        in_dim = obs_dim + (n_agents if agent_id else 0)
        self.net = _mlp(in_dim, hidden, n_actions)

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        """obs: (..., n_agents, obs_dim) -> Q: (..., n_agents, n_actions)."""
        if self.agent_id:
            eye = torch.eye(self.n_agents, device=obs.device).expand(*obs.shape[:-1], self.n_agents)
            obs = torch.cat([obs, eye], dim=-1)
        return self.net(obs)


class SwarmAgent:
    def __init__(self, obs_dim: int, n_actions: int, n_agents: int, cfg: dict, device: str = "cpu"):
        self.n_actions = n_actions
        self.n_agents = n_agents
        self.cfg = cfg
        self.device = torch.device(device)
        hidden = list(cfg.get("hidden", [128, 128]))
        agent_id = bool(cfg.get("agent_id", False))
        self.q = SharedQNetwork(obs_dim, n_actions, n_agents, hidden, agent_id).to(self.device)
        self.q_target = SharedQNetwork(obs_dim, n_actions, n_agents, hidden, agent_id).to(self.device)
        self.q_target.load_state_dict(self.q.state_dict())
        self.opt = torch.optim.Adam(self.q.parameters(), lr=float(cfg.get("lr", 5e-4)))
        self.gamma = float(cfg.get("gamma", 0.99))
        self.tau = float(cfg.get("tau", 0.01))
        self.mixer = cfg.get("mixer", "vdn")
        if self.mixer not in ("vdn", "independent"):
            raise ValueError(f"Unknown mixer '{self.mixer}' (use 'vdn' or 'independent')")
        self.grad_clip = float(cfg.get("grad_clip", 10.0))

    @torch.no_grad()
    def act(self, obs: np.ndarray, mask: np.ndarray, epsilon: float = 0.0, rng: np.random.Generator | None = None) -> np.ndarray:
        """Pick actions for every agent of every env copy at once.

        obs: (E, N, obs_dim), mask: (E, N, A) -> actions (E, N).
        """
        q = self.q(torch.as_tensor(obs, dtype=torch.float32, device=self.device))
        q = q.masked_fill(~torch.as_tensor(mask, device=self.device), -1e9)
        actions = q.argmax(-1).cpu().numpy()
        if epsilon > 0:
            rng = rng or np.random.default_rng()
            explore = rng.random(actions.shape) < epsilon
            if explore.any():
                # Uniform choice among the valid actions of each exploring agent.
                noise = rng.random(mask.shape) * mask
                actions = np.where(explore, noise.argmax(-1), actions)
        return actions

    def update(self, batch: dict) -> float:
        dev = self.device
        obs = torch.as_tensor(batch["obs"], device=dev)
        actions = torch.as_tensor(batch["actions"], device=dev)
        rewards = torch.as_tensor(batch["rewards"], device=dev)
        agent_rewards = torch.as_tensor(batch["agent_rewards"], device=dev)
        next_obs = torch.as_tensor(batch["next_obs"], device=dev)
        discount = torch.as_tensor(batch["discount"], device=dev)
        next_mask = torch.as_tensor(batch["next_mask"], device=dev)

        q_taken = self.q(obs).gather(-1, actions.unsqueeze(-1)).squeeze(-1)  # (B, N)
        with torch.no_grad():
            next_online = self.q(next_obs).masked_fill(~next_mask, -1e9)
            next_a = next_online.argmax(-1, keepdim=True)
            next_q = self.q_target(next_obs).gather(-1, next_a).squeeze(-1)  # (B, N)

        if self.mixer == "vdn":
            pred = q_taken.sum(-1)
            target = rewards + agent_rewards.sum(-1) + discount * next_q.sum(-1)
        else:
            pred = q_taken
            target = rewards.unsqueeze(-1) + agent_rewards + discount.unsqueeze(-1) * next_q

        loss = F.smooth_l1_loss(pred, target)
        self.opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.q.parameters(), self.grad_clip)
        self.opt.step()
        with torch.no_grad():
            for p, tp in zip(self.q.parameters(), self.q_target.parameters()):
                tp.mul_(1 - self.tau).add_(self.tau * p)
        return float(loss.item())

    def policy(self):
        """Greedy policy usable by ``swarm.trainer.evaluate``."""
        def _policy(env, obs, mask):
            return self.act(obs[None], mask[None])[0]
        return _policy

    def state_dict(self) -> dict:
        return {"q": self.q.state_dict(), "cfg": self.cfg}

    def load_state_dict(self, state: dict) -> None:
        self.q.load_state_dict(state["q"])
        self.q_target.load_state_dict(state["q"])
