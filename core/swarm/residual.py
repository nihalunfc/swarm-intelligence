"""Residual swarm: the best hand-written rule plus a learned correction.

Each agent sees its usual observation **and the rule's suggested action**, and
chooses either one of its normal actions (an override) or an extra action,
"follow the rule". Training starts from imitation of "follow the rule"
(``pretrain.rule: follow rule``), so the untrained swarm already behaves
exactly like the rule; reinforcement learning then only has to learn *when*
deviating pays. An optional ``override_cost`` (team reward per override)
keeps the swarm on the rule unless an override clearly helps, which also makes
the learned policy easy to explain: every deviation from the rule is a
deliberate, logged decision.

Use it from any config with::

    residual:
      rule: nearest-fire rule      # one of the app's BASELINES (no side effects)
      override_cost: 0.0

It wraps the app, so DQN, MAPPO, validation, multi-seed runs and all the
app's rules and reference bounds work unchanged.
"""

from __future__ import annotations

import types

import numpy as np

from .env import SwarmEnv

FOLLOW = "follow rule"


class ResidualEnv(SwarmEnv):
    def __init__(self, inner: SwarmEnv, rule, override_cost: float = 0.0, seed: int = 0):
        self.inner, self.rule, self.cost = inner, rule, float(override_cost)
        self.n_agents = inner.n_agents
        self.n_actions = inner.n_actions + 1
        self.FOLLOW = inner.n_actions
        self.obs_dim = inner.obs_dim + inner.n_actions
        self.rule_rng = np.random.default_rng(seed + 7_919)  # the rule's tie-breaks must not disturb the episode
        self.overrides = self.steps = 0

    def _suggest(self, obs):
        saved = getattr(self.inner, "rng", None)
        if saved is not None:
            self.inner.rng = self.rule_rng
        try:
            self.suggested = np.asarray(self.rule(self.inner, obs, self.inner.action_mask()))
        finally:
            if saved is not None:
                self.inner.rng = saved
        if getattr(self.inner, "override", None):
            raise ValueError("residual: the rule plans by side effect (env.override); pick a rule that returns actions")
        onehot = np.eye(self.inner.n_actions, dtype=np.float32)[self.suggested]
        return np.concatenate([obs, onehot], axis=1).astype(np.float32)

    def reset(self, seed=None):
        if seed is not None:
            self.rule_rng = np.random.default_rng(seed + 7_919)
        self.overrides = self.steps = 0
        return self._suggest(self.inner.reset(seed=seed))

    def action_mask(self):
        m = self.inner.action_mask()
        return np.concatenate([m, np.ones((self.n_agents, 1), dtype=bool)], axis=1)

    def step(self, actions):
        a = np.asarray(actions)
        follow = a == self.FOLLOW
        real = np.where(follow, self.suggested, a)
        n_over = int((~follow & (a != self.suggested)).sum())
        self.overrides += n_over
        self.steps += 1
        obs, r, term, trunc, info = self.inner.step(real)
        return self._suggest(obs), r - self.cost * n_over, term, trunc, info

    def episode_metrics(self):
        return {**self.inner.episode_metrics(),
                "override_rate_pct": 100.0 * self.overrides / max(1, self.n_agents * self.steps)}

    def __getattr__(self, name):  # rules and exporters read the inner env's state
        if name == "inner":
            raise AttributeError(name)
        return getattr(self.inner, name)


def _lift(policy):
    """Run an original rule on the wrapped env (actions keep their indices)."""
    def lifted(env, obs, mask):
        return policy(env.inner, obs[:, :env.inner.obs_dim], mask[:, :env.inner.n_actions])
    return lifted


def wrap(app, rcfg: dict):
    """An app module look-alike whose environments are residual over ``rcfg['rule']``."""
    rule_name = rcfg["rule"]
    if rule_name not in app.BASELINES:
        raise KeyError(f"residual.rule '{rule_name}' is not one of: {', '.join(app.BASELINES)}")
    rule, cost = app.BASELINES[rule_name], float(rcfg.get("override_cost", 0.0))

    def make_env(env_cfg, split, seed):
        return ResidualEnv(app.make_env(env_cfg, split, seed), rule, cost, seed)

    def follow(env, obs, mask):
        return np.full(env.n_agents, env.FOLLOW)

    baselines = {name: _lift(p) for name, p in app.BASELINES.items()}
    baselines[FOLLOW] = follow  # identical to the rule; used for imitation pre-training
    refs = [(lambda f: lambda _app, *a: f(app, *a))(f) for f in getattr(app, "REFERENCES", [])]
    w = types.SimpleNamespace(make_env=make_env, BASELINES=baselines, REFERENCES=refs,
                              KEY_METRICS=list(app.KEY_METRICS) + ["override_rate_pct"], inner=app)
    return w
