"""MAPPO baseline: multi-agent PPO with a shared actor and a pooled centralised critic.

This is the standard on-policy baseline for cooperative multi-agent RL (Yu et
al., 2022, "The Surprising Effectiveness of PPO in Cooperative Multi-Agent
Games"). As in the DQN swarm, every agent runs the same actor on its own local
observation, so execution stays decentralised and the model does not grow with
the swarm. During training only, each agent's critic also sees a summary of the
whole swarm (the mean and max of all agents' encoded observations), which works
for any number of agents.

Per-agent advantages use GAE on the team reward plus that agent's shaping
reward, the same signal the DQN swarm learns from. Select it with
``algo: mappo`` in a config; ``ppo:`` holds its settings.
"""

from __future__ import annotations

import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from .config import seed_everything


def _mlp(i, hidden, o):
    layers, d = [], i
    for h in hidden:
        layers += [nn.Linear(d, h), nn.Tanh()]
        d = h
    layers.append(nn.Linear(d, o))
    return nn.Sequential(*layers)


class ActorCritic(nn.Module):
    def __init__(self, obs_dim, n_actions, hidden, agent_id, id_count):
        super().__init__()
        self.agent_id, self.id_count = agent_id, id_count
        d = obs_dim + (id_count if agent_id else 0)
        self.actor = _mlp(d, hidden, n_actions)
        self.encode = nn.Sequential(nn.Linear(d, hidden[0]), nn.Tanh())
        self.critic = _mlp(d + 2 * hidden[0], hidden, 1)

    def _x(self, obs):
        if not self.agent_id:
            return obs
        ids = torch.arange(obs.shape[-2], device=obs.device) % self.id_count
        eye = F.one_hot(ids, self.id_count).float().expand(*obs.shape[:-1], self.id_count)
        return torch.cat([obs, eye], -1)

    def logits(self, obs, mask):
        return self.actor(self._x(obs)).masked_fill(~mask, -1e9)

    def value(self, obs):
        x = self._x(obs)
        h = self.encode(x)
        pooled = torch.cat([h.mean(-2), h.max(-2).values], -1).unsqueeze(-2).expand(*x.shape[:-1], -1)
        return self.critic(torch.cat([x, pooled], -1)).squeeze(-1)


class PPOAgent:
    algo = "mappo"

    def __init__(self, env, cfg: dict):
        self.cfg = cfg
        hidden = list(cfg.get("hidden", [128, 128]))
        self.net = ActorCritic(env.obs_dim, env.n_actions, hidden, bool(cfg.get("agent_id", False)),
                               int(cfg.get("agent_id_count") or env.n_agents))
        self.opt = torch.optim.Adam(self.net.parameters(), lr=float(cfg.get("lr", 3e-4)), eps=1e-5)

    @torch.no_grad()
    def act(self, obs, mask, sample=False, rng=None):
        logits = self.net.logits(torch.as_tensor(obs, dtype=torch.float32), torch.as_tensor(mask))
        if not sample:
            return logits.argmax(-1).numpy()
        return torch.distributions.Categorical(logits=logits).sample().numpy()

    def policy(self):
        def _policy(env, obs, mask):
            return self.act(obs[None], mask[None])[0]
        return _policy

    def state_dict(self):
        return {"net": self.net.state_dict(), "cfg": self.cfg, "algo": self.algo}

    def load_state_dict(self, state):
        self.net.load_state_dict(state["net"])


def train_ppo(app, cfg: dict, log=print):
    from .trainer import Validator

    seed = int(cfg.get("seed", 0))
    seed_everything(seed)
    tcfg, pcfg = cfg.get("train", {}), cfg.get("ppo", {})
    n_envs = int(tcfg.get("num_envs", 8))
    total = int(tcfg.get("total_steps", 100_000))
    T = int(pcfg.get("rollout", 128))
    epochs, minibatches = int(pcfg.get("epochs", 4)), int(pcfg.get("minibatches", 4))
    gamma, lam = float(pcfg.get("gamma", cfg.get("agent", {}).get("gamma", 0.99))), float(pcfg.get("gae_lambda", 0.95))
    clip, ent_coef, vf_coef = float(pcfg.get("clip", 0.2)), float(pcfg.get("entropy", 0.01)), float(pcfg.get("value_coef", 0.5))
    log_every = int(tcfg.get("log_every", 10_000))

    envs = [app.make_env(cfg.get("env", {}), "train", seed + i) for i in range(n_envs)]
    e0 = envs[0]
    N, D, A = e0.n_agents, e0.obs_dim, e0.n_actions
    agent = PPOAgent(e0, {**cfg.get("agent", {}), "lr": pcfg.get("lr", 3e-4)})
    net, opt = agent.net, agent.opt
    validator = Validator(app, cfg, log)
    obs = np.stack([e.reset(seed=seed + i) for i, e in enumerate(envs)]).astype(np.float32)
    returns, history = np.zeros(n_envs), []
    steps, next_log, t0 = 0, log_every, time.time()

    while steps < total:
        B_obs = np.zeros((T, n_envs, N, D), np.float32)
        B_mask = np.zeros((T, n_envs, N, A), bool)
        B_act = np.zeros((T, n_envs, N), np.int64)
        B_logp = np.zeros((T, n_envs, N), np.float32)
        B_val = np.zeros((T, n_envs, N), np.float32)
        B_rew = np.zeros((T, n_envs, N), np.float32)
        B_done = np.zeros((T, n_envs), np.float32)       # episode really ended: no bootstrap
        B_boot = np.zeros((T, n_envs, N), np.float32)    # value of the cut-off state on truncation
        for t in range(T):
            mask = np.stack([e.action_mask() for e in envs])
            with torch.no_grad():
                o = torch.as_tensor(obs)
                dist = torch.distributions.Categorical(logits=net.logits(o, torch.as_tensor(mask)))
                act = dist.sample()
                B_logp[t], B_val[t] = dist.log_prob(act).numpy(), net.value(o).numpy()
            B_obs[t], B_mask[t], B_act[t] = obs, mask, act.numpy()
            for i, env in enumerate(envs):
                nxt, r, term, trunc, info = env.step(B_act[t, i])
                B_rew[t, i] = r + np.asarray(info.get("agent_rewards", np.zeros(N)), np.float32)
                returns[i] += r
                if term or trunc:
                    B_done[t, i] = 1.0
                    if trunc and not term:
                        with torch.no_grad():
                            B_boot[t, i] = net.value(torch.as_tensor(nxt[None], dtype=torch.float32))[0].numpy()
                    history.append({"step": steps, "return": float(returns[i]), **env.episode_metrics()})
                    returns[i] = 0.0
                    nxt = env.reset()
                obs[i] = nxt
            steps += n_envs
        with torch.no_grad():
            last_val = net.value(torch.as_tensor(obs)).numpy()
        adv = np.zeros_like(B_rew)
        gae = np.zeros((n_envs, N), np.float32)
        for t in reversed(range(T)):
            nv = last_val if t == T - 1 else B_val[t + 1]
            nonterminal = 1.0 - B_done[t][:, None]
            # On a time-limit cut, bootstrap from the cut-off state's value instead of the next episode.
            target_next = nonterminal * nv + B_boot[t]
            delta = B_rew[t] + gamma * target_next - B_val[t]
            gae = delta + gamma * lam * nonterminal * gae
            adv[t] = gae
        ret = adv + B_val

        flat = lambda x: x.reshape(T * n_envs, *x.shape[2:])
        f_obs, f_mask, f_act = map(torch.as_tensor, (flat(B_obs), flat(B_mask), flat(B_act)))
        f_logp, f_adv, f_ret = map(torch.as_tensor, (flat(B_logp), flat(adv), flat(ret)))
        idx = np.arange(T * n_envs)
        mb = max(1, len(idx) // minibatches)
        for _ in range(epochs):
            np.random.shuffle(idx)
            for s in range(0, len(idx), mb):
                j = torch.as_tensor(idx[s:s + mb])
                a_ = f_adv[j]
                a_ = (a_ - a_.mean()) / (a_.std() + 1e-8)
                dist = torch.distributions.Categorical(logits=net.logits(f_obs[j], f_mask[j]))
                ratio = (dist.log_prob(f_act[j]) - f_logp[j]).exp()
                pg = -torch.min(ratio * a_, ratio.clamp(1 - clip, 1 + clip) * a_).mean()
                vf = F.mse_loss(net.value(f_obs[j]), f_ret[j])
                loss = pg + vf_coef * vf - ent_coef * dist.entropy().mean()
                opt.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(net.parameters(), 0.5)
                opt.step()
        if steps >= next_log:
            recent = [h["return"] for h in history[-20:]]
            log(f"step {steps:>8,} | ppo loss {loss.item():.4f} | return(last 20) "
                f"{np.mean(recent) if recent else float('nan'):9.2f} | {time.time() - t0:5.0f}s")
            next_log += log_every
        validator.maybe(steps, agent)
    validator.finish(steps, agent)
    return agent, history
