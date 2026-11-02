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
* ``qmix``: a monotonic mixing network weighs each agent's value by the
  situation (``QMixer``).

With ``comm.enabled`` agents also exchange messages with their neighbours
through attention (``CommQNetwork``).

Double-DQN targets, a soft-updated target network and action masks are used
in both cases.

Learning from demonstrations (DQfD-style): ``update`` can also take a batch of
transitions recorded from a hand-written rule. A large-margin loss then pushes
the rule's action to have the highest Q-value by at least ``margin``, so the
swarm starts from the rule's behaviour and reinforcement learning improves on it.
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
    def __init__(self, obs_dim: int, n_actions: int, n_agents: int, hidden: list[int], agent_id: bool,
                 id_count: int | None = None):
        super().__init__()
        self.n_agents = n_agents
        self.agent_id = agent_id
        # One-hot ids of width ``id_count``; a larger swarm reuses the ids cyclically,
        # which lets a model trained with k agents run any number of them.
        self.id_count = int(id_count or n_agents)
        in_dim = obs_dim + (self.id_count if agent_id else 0)
        self.net = _mlp(in_dim, hidden, n_actions)

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        """obs: (..., n_agents, obs_dim) -> Q: (..., n_agents, n_actions)."""
        if self.agent_id:
            ids = torch.arange(obs.shape[-2], device=obs.device) % self.id_count
            eye = F.one_hot(ids, self.id_count).float().expand(*obs.shape[:-1], self.id_count)
            obs = torch.cat([obs, eye], dim=-1)
        return self.net(obs)


class CommQNetwork(nn.Module):
    """Shared Q-network whose agents also read messages from their neighbours.

    Each agent encodes its observation, sends a key and a message, and attends
    over the messages of the agents it can reach (``neighbours``: an
    (..., N, N) boolean mask, all agents when None; an agent always hears
    itself). Its Q-values come from its own encoding plus what it heard. The
    weights are shared, so this works for any swarm size, like an ant reacting
    to the ants around it.
    """

    def __init__(self, obs_dim: int, n_actions: int, n_agents: int, hidden: list[int], agent_id: bool,
                 id_count: int | None = None, dim: int = 64, rounds: int = 1):
        super().__init__()
        self.n_agents, self.agent_id = n_agents, agent_id
        self.id_count = int(id_count or n_agents)
        in_dim = obs_dim + (self.id_count if agent_id else 0)
        self.encode = nn.Sequential(nn.Linear(in_dim, dim), nn.ReLU(), nn.Linear(dim, dim), nn.ReLU())
        self.rounds = nn.ModuleList(nn.ModuleDict({
            "q": nn.Linear(dim, dim), "k": nn.Linear(dim, dim), "v": nn.Linear(dim, dim),
            "out": nn.Sequential(nn.Linear(2 * dim, dim), nn.ReLU()),
        }) for _ in range(rounds))
        self.head = _mlp(dim, hidden, n_actions)
        self.neighbours = None  # set by the agent from the env's comm spec

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        if self.agent_id:
            ids = torch.arange(obs.shape[-2], device=obs.device) % self.id_count
            eye = F.one_hot(ids, self.id_count).float().expand(*obs.shape[:-1], self.id_count)
            x = torch.cat([obs, eye], dim=-1)
        else:
            x = obs
        h = self.encode(x)
        adj = self.neighbours(obs) if self.neighbours is not None else None
        for r in self.rounds:
            att = r["q"](h) @ r["k"](h).transpose(-1, -2) / h.shape[-1] ** 0.5  # (..., N, N)
            if adj is not None:
                eye = torch.eye(h.shape[-2], dtype=torch.bool, device=h.device)
                att = att.masked_fill(~(adj | eye), -1e9)
            heard = att.softmax(-1) @ r["v"](h)
            h = r["out"](torch.cat([h, heard], dim=-1))
        return self.head(h)


def radius_neighbours(pos_cols: tuple[int, int], radius: float):
    """Agents within ``radius`` (in the same units as the position columns) hear each other."""
    i, j = pos_cols

    def fn(obs: torch.Tensor) -> torch.Tensor:
        p = obs[..., [i, j]]
        d = (p.unsqueeze(-2) - p.unsqueeze(-3)).abs().amax(-1)  # Chebyshev distance
        return d <= radius
    return fn


class QMixer(nn.Module):
    """Monotonic team value (QMIX-style) that works for any number of agents.

    Q_team = w2(s) . elu(sum_i |w1(s, o_i)| * Q_i + b1(s)) + b2(s), with s the
    mean of all agents' observations. Non-negative weights keep each agent's
    best action the team's best action, as in QMIX, while letting the team value
    weigh agents by situation (a drone at the fire front counts more).
    """

    def __init__(self, obs_dim: int, embed: int = 32):
        super().__init__()
        self.w1 = nn.Sequential(nn.Linear(2 * obs_dim, embed), nn.ReLU(), nn.Linear(embed, embed))
        self.b1 = nn.Linear(obs_dim, embed)
        self.w2 = nn.Sequential(nn.Linear(obs_dim, embed), nn.ReLU(), nn.Linear(embed, embed))
        self.b2 = nn.Sequential(nn.Linear(obs_dim, embed), nn.ReLU(), nn.Linear(embed, 1))

    def forward(self, q: torch.Tensor, obs: torch.Tensor) -> torch.Tensor:
        """q: (B, N) chosen Q-values, obs: (B, N, D) -> (B,) team value."""
        s = obs.mean(-2)
        w1 = self.w1(torch.cat([obs, s.unsqueeze(-2).expand_as(obs)], -1)).abs()  # (B, N, E)
        hidden = F.elu((w1 * q.unsqueeze(-1)).sum(-2) + self.b1(s))           # (B, E)
        return (self.w2(s).abs() * hidden).sum(-1) + self.b2(s).squeeze(-1)


class SwarmAgent:
    def __init__(self, obs_dim: int, n_actions: int, n_agents: int, cfg: dict, device: str = "cpu"):
        self.n_actions = n_actions
        self.n_agents = n_agents
        self.cfg = cfg
        self.device = torch.device(device)
        hidden = list(cfg.get("hidden", [128, 128]))
        agent_id = bool(cfg.get("agent_id", False))
        ids = cfg.get("agent_id_count")
        comm = cfg.get("comm") or {}

        def make():
            if comm.get("enabled"):
                return CommQNetwork(obs_dim, n_actions, n_agents, hidden, agent_id, ids,
                                    int(comm.get("dim", 64)), int(comm.get("rounds", 1)))
            return SharedQNetwork(obs_dim, n_actions, n_agents, hidden, agent_id, ids)
        self.q, self.q_target = make().to(self.device), make().to(self.device)
        self.q_target.load_state_dict(self.q.state_dict())
        self.mixer = cfg.get("mixer", "vdn")
        if self.mixer not in ("vdn", "independent", "qmix"):
            raise ValueError(f"Unknown mixer '{self.mixer}' (use 'vdn', 'independent' or 'qmix')")
        params = list(self.q.parameters())
        if self.mixer == "qmix":
            self.mix, self.mix_target = QMixer(obs_dim).to(self.device), QMixer(obs_dim).to(self.device)
            self.mix_target.load_state_dict(self.mix.state_dict())
            params += list(self.mix.parameters())
        self.opt = torch.optim.Adam(params, lr=float(cfg.get("lr", 5e-4)))
        self.gamma = float(cfg.get("gamma", 0.99))
        self.tau = float(cfg.get("tau", 0.01))
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

    def _td_loss(self, batch: dict) -> torch.Tensor:
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
        elif self.mixer == "qmix":
            pred = self.mix(q_taken, obs)
            with torch.no_grad():
                target = rewards + agent_rewards.sum(-1) + discount * self.mix_target(next_q, next_obs)
        else:
            pred = q_taken
            target = rewards.unsqueeze(-1) + agent_rewards + discount.unsqueeze(-1) * next_q

        return F.smooth_l1_loss(pred, target)

    def _margin_loss(self, batch: dict, margin: float) -> torch.Tensor:
        """max_a [Q(s,a) + margin * (a != a_demo)] - Q(s, a_demo), over valid actions."""
        dev = self.device
        obs = torch.as_tensor(batch["obs"], device=dev)
        actions = torch.as_tensor(batch["actions"], device=dev)
        mask = torch.as_tensor(batch["mask"], device=dev)
        q = self.q(obs)  # (B, N, A)
        bonus = torch.full_like(q, margin).scatter_(-1, actions.unsqueeze(-1), 0.0)
        best = (q + bonus).masked_fill(~mask, -1e9).max(-1).values
        q_demo = q.gather(-1, actions.unsqueeze(-1)).squeeze(-1)
        return (best - q_demo).mean()

    def update(self, batch: dict | None, demo: dict | None = None, demo_weight: float = 0.0, margin: float = 0.8) -> float:
        """One gradient step on the TD loss of ``batch`` (replay) and, when given,
        the TD plus large-margin loss of ``demo`` (rule demonstrations)."""
        loss = torch.zeros((), device=self.device)
        if batch is not None:
            loss = loss + self._td_loss(batch)
        if demo is not None and demo_weight > 0:
            loss = loss + demo_weight * (self._td_loss(demo) + self._margin_loss(demo, margin))
        self.opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_([p for g in self.opt.param_groups for p in g["params"]], self.grad_clip)
        self.opt.step()
        with torch.no_grad():
            pairs = list(zip(self.q.parameters(), self.q_target.parameters()))
            if self.mixer == "qmix":
                pairs += list(zip(self.mix.parameters(), self.mix_target.parameters()))
            for p, tp in pairs:
                tp.mul_(1 - self.tau).add_(self.tau * p)
        return float(loss.item())

    def policy(self):
        """Greedy policy usable by ``swarm.trainer.evaluate``."""
        def _policy(env, obs, mask):
            return self.act(obs[None], mask[None])[0]
        return _policy

    def set_neighbours(self, fn) -> None:
        """Who can hear whom (see ``CommQNetwork``); ignored without ``comm``."""
        for net in (self.q, self.q_target):
            if isinstance(net, CommQNetwork):
                net.neighbours = fn

    def state_dict(self) -> dict:
        state = {"q": self.q.state_dict(), "cfg": self.cfg}
        if self.mixer == "qmix":
            state["mix"] = self.mix.state_dict()
        return state

    def load_state_dict(self, state: dict) -> None:
        self.q.load_state_dict(state["q"])
        self.q_target.load_state_dict(state["q"])
        if self.mixer == "qmix" and "mix" in state:
            self.mix.load_state_dict(state["mix"])
            self.mix_target.load_state_dict(state["mix"])


def make_agent(env, cfg: dict, device: str = "cpu") -> SwarmAgent:
    """A SwarmAgent sized for ``env``, wired to the env's neighbour rule when it has one.

    An env can define ``comm_spec() -> (pos_cols, radius)``: agents whose
    position columns are within ``radius`` hear each other. Without it every
    agent hears every other (fine for batteries on one grid).
    """
    agent = SwarmAgent(env.obs_dim, env.n_actions, env.n_agents, cfg, device=device)
    if hasattr(env, "comm_spec"):
        agent.set_neighbours(radius_neighbours(*env.comm_spec()))
    return agent
