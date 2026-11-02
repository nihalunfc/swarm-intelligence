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

    def add(self, obs, act, r, ar, next_obs, next_mask, terminated: bool, ended: bool, mask=None) -> list[tuple]:
        self.q.append((obs, act, r, ar, mask))
        out = []
        if len(self.q) == self.n:
            out.append(self._pop(next_obs, next_mask, terminated))
        if ended:
            while self.q:
                out.append(self._pop(next_obs, next_mask, terminated))
        return out

    def _pop(self, next_obs, next_mask, terminated):
        R, AR = 0.0, 0.0
        for k, (_, _, r, ar, _) in enumerate(self.q):
            R += self.gamma ** k * r
            AR = AR + self.gamma ** k * ar
        obs, act, _, _, mask = self.q.popleft()
        discount = 0.0 if terminated else self.gamma ** (len(self.q) + 1)
        return obs, act, R, next_obs, discount, next_mask, AR, mask


def collect_demos(app, cfg: dict, n: int, gamma: float, n_step: int, seed: int) -> ReplayBuffer:
    """Record ``n`` n-step transitions from one of the app's rules (``pretrain.rule``)."""
    pcfg = cfg.get("pretrain", {})
    rule = pcfg.get("rule")
    if rule not in app.BASELINES:
        raise KeyError(f"pretrain.rule '{rule}' is not one of: {', '.join(app.BASELINES)}")
    policy = app.BASELINES[rule]
    env = app.make_env(cfg.get("env", {}), "train", seed)
    buf = ReplayBuffer(n, env.n_agents, env.obs_dim, env.n_actions, seed)
    ns = NStep(n_step, gamma)
    obs = env.reset(seed=seed)
    while len(buf) < n:
        mask = env.action_mask()
        actions = policy(env, obs, mask)
        nxt, r, term, trunc, info = env.step(actions)
        ar = info.get("agent_rewards", np.zeros(env.n_agents))
        for tr in ns.add(obs.copy(), actions, r, ar, nxt, env.action_mask(), term, term or trunc, mask):
            if len(buf) < n:
                buf.push(*tr)
        obs = env.reset() if term or trunc else nxt
    return buf


def train(app, cfg: dict, log=print):
    """Train one parameter-shared agent on ``num_envs`` environment copies in parallel."""
    from .agents import make_agent  # torch is only needed for training

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
    agent = make_agent(e0, cfg.get("agent", {}), device=cfg.get("device", "cpu"))
    buf = ReplayBuffer(int(tcfg.get("buffer_size", 100_000)), e0.n_agents, e0.obs_dim, e0.n_actions, seed)
    rng = np.random.default_rng(seed)
    nsteps = [NStep(n_step, agent.gamma) for _ in envs]

    # Optional learning from a rule first: pre-train on its demonstrations, keep
    # them in replay, and fade their large-margin loss out during fine-tuning.
    pcfg = cfg.get("pretrain") or {}
    demo_buf = None
    if pcfg.get("rule"):
        n_demo = int(pcfg.get("demo_steps", 50_000))
        t_demo = time.time()
        demo_buf = collect_demos(app, cfg, n_demo, agent.gamma, n_step, seed + 1_000)
        log(f"recorded {n_demo:,} transitions from the {pcfg['rule']} in {time.time() - t_demo:.0f}s")
        for i in range(len(demo_buf)):
            buf.push(demo_buf.obs[i], demo_buf.actions[i], demo_buf.rewards[i], demo_buf.next_obs[i],
                     demo_buf.discount[i], demo_buf.next_mask[i], demo_buf.agent_rewards[i], demo_buf.mask[i])
        margin = float(pcfg.get("margin", 0.8))
        updates = int(pcfg.get("updates", 5_000))
        for k in range(updates):
            loss = agent.update(None, demo_buf.sample(batch_size), 1.0, margin)
            if (k + 1) % max(1, updates // 5) == 0:
                log(f"pretrain {k + 1:>6,}/{updates:,} | demo loss {loss:.4f}")
        demo_weight = float(pcfg.get("demo_weight", 1.0))
        demo_decay = float(pcfg.get("demo_decay_fraction", 0.5)) * total

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
            for tr in nsteps[i].add(obs[i].copy(), actions[i], r, ar, nxt, env.action_mask(), term, term or trunc, mask[i]):
                buf.push(*tr)
            returns[i] += r
            if term or trunc:
                history.append({"step": steps, "return": float(returns[i]), **env.episode_metrics()})
                returns[i] = 0.0
                nxt = env.reset()
            obs[i] = nxt
        steps += n_envs
        if steps >= learning_starts and len(buf) >= batch_size:
            w = demo_weight * max(0.0, 1.0 - steps / max(1.0, demo_decay)) if demo_buf is not None else 0.0
            for _ in range(gradient_steps):
                loss = agent.update(buf.sample(batch_size), demo_buf.sample(batch_size) if w > 0 else None, w,
                                    margin if demo_buf is not None else 0.8)
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
