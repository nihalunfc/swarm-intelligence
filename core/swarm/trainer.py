"""Training and evaluation loops shared by every swarm application."""

import time
from collections import deque

import numpy as np

from .buffer import ReplayBuffer
from .config import seed_everything


def _epsilon(step: int, total: int, cfg: dict) -> float:
    start, end = float(cfg.get("eps_start", 1.0)), float(cfg.get("eps_end", 0.05))
    frac = min(1.0, step / max(1.0, float(cfg.get("eps_fraction", 0.5)) * total))
    return start + frac * (end - start)


class NStep:
    """Turns one environment's 1-step transitions into n-step ones.

    Rewards are summed over up to ``n`` steps before bootstrapping, which
    carries credit back much faster when the effect of an action shows up
    several steps later (a drone flying toward a fire, a battery saving
    charge for the evening peak).
    """

    def __init__(self, n: int, gamma: float):
        self.n, self.gamma = n, gamma
        self.q: deque = deque()

    def add(self, obs, act, r, ar, next_obs, next_mask, terminated: bool, ended: bool) -> list[tuple]:
        self.q.append((obs, act, r, ar))
        out = []
        if len(self.q) == self.n:
            out.append(self._pop(next_obs, next_mask, terminated))
        if ended:
            while self.q:
                out.append(self._pop(next_obs, next_mask, terminated))
        return out

    def _pop(self, next_obs, next_mask, terminated):
        R, AR = 0.0, 0.0
        for k, (_, _, r, ar) in enumerate(self.q):
            R += self.gamma ** k * r
            AR = AR + self.gamma ** k * ar
        obs, act, _, _ = self.q.popleft()
        discount = 0.0 if terminated else self.gamma ** (len(self.q) + 1)
        return obs, act, R, next_obs, discount, next_mask, AR


def train(app, cfg: dict, log=print):
    """Train one parameter-shared agent on ``num_envs`` environment copies in parallel."""
    from .agents import SwarmAgent  # torch is only needed for training

    seed = int(cfg.get("seed", 0))
    seed_everything(seed)
    tcfg = cfg.get("train", {})
    n_envs = int(tcfg.get("num_envs", 4))
    total = int(tcfg.get("total_steps", 50_000))
    batch_size = int(tcfg.get("batch_size", 128))
    learning_starts = int(tcfg.get("learning_starts", 1_000))
    gradient_steps = int(tcfg.get("gradient_steps", 1))
    log_every = int(tcfg.get("log_every", 10_000))
    n_step = int(tcfg.get("n_step", 3))

    envs = [app.make_env(cfg.get("env", {}), "train", seed + i) for i in range(n_envs)]
    e0 = envs[0]
    agent = SwarmAgent(e0.obs_dim, e0.n_actions, e0.n_agents, cfg.get("agent", {}), device=cfg.get("device", "cpu"))
    buf = ReplayBuffer(int(tcfg.get("buffer_size", 100_000)), e0.n_agents, e0.obs_dim, e0.n_actions, seed)
    rng = np.random.default_rng(seed)
    nsteps = [NStep(n_step, agent.gamma) for _ in envs]

    obs = np.stack([e.reset(seed=seed + i) for i, e in enumerate(envs)])
    returns = np.zeros(n_envs)
    history: list[dict] = []
    steps, next_log, t0, loss = 0, log_every, time.time(), float("nan")

    while steps < total:
        eps = _epsilon(steps, total, tcfg)
        mask = np.stack([e.action_mask() for e in envs])
        actions = agent.act(obs, mask, eps, rng)
        for i, env in enumerate(envs):
            nxt, r, term, trunc, info = env.step(actions[i])
            ar = info.get("agent_rewards", np.zeros(env.n_agents))
            for tr in nsteps[i].add(obs[i].copy(), actions[i], r, ar, nxt, env.action_mask(), term, term or trunc):
                buf.push(*tr)
            returns[i] += r
            if term or trunc:
                history.append({"step": steps, "return": float(returns[i]), **env.episode_metrics()})
                returns[i] = 0.0
                nxt = env.reset()
            obs[i] = nxt
        steps += n_envs
        if steps >= learning_starts and len(buf) >= batch_size:
            for _ in range(gradient_steps):
                loss = agent.update(buf.sample(batch_size))
        if steps >= next_log:
            recent = [h["return"] for h in history[-20:]]
            mean_ret = np.mean(recent) if recent else float("nan")
            log(f"step {steps:>8,} | eps {eps:.2f} | loss {loss:.4f} | return(last 20) {mean_ret:9.2f} | {time.time() - t0:5.0f}s")
            next_log += log_every
    return agent, history


def evaluate(app, env_cfg: dict, policy, episodes: int = 1, seed: int = 10_000, split: str = "test") -> dict:
    """Run ``policy(env, obs, mask)`` greedily and average the episode metrics."""
    env = app.make_env(env_cfg, split, seed)
    rows = []
    for ep in range(episodes):
        obs = env.reset(seed=seed + ep)
        total, done = 0.0, False
        while not done:
            actions = policy(env, obs, env.action_mask())
            obs, r, term, trunc, _ = env.step(actions)
            total += r
            done = term or trunc
        rows.append({"return": total, **env.episode_metrics()})
    keys = [k for k in rows[0] if isinstance(rows[0][k], (int, float))]
    return {k: float(np.mean([row[k] for row in rows])) for k in keys} | {"episodes": episodes}
