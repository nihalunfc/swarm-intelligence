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


GATE_MARGINS = (0.0, 0.02, 0.05, 0.1, 0.2, 0.5, float("inf"))


def tune_gate(run, margins=GATE_MARGINS, episodes: int | None = None, log=print, sizes=None) -> dict:
    """Pick how sure a residual swarm must be before it leaves the rule, on validation fires.

    For each margin the gated swarm (see ``SwarmAgent.act``) plays the validation
    episodes (never the test ones). The best margin by ``eval.select_metric`` is
    kept; ties go to the larger margin, i.e. closer to the rule. An infinite
    margin is the rule itself, so the chosen swarm is never worse than the rule
    on validation. The margin is written into the run's ``model.pt``, so every
    later tool (evaluate, scale, robustness) uses the gated swarm.

    ``sizes`` (optional, apps with ``scaled_env_cfg``): also play the validation
    fires with these swarm sizes and score each margin by its worst size. A
    correction that only helps the trained size is then refused.
    """
    from pathlib import Path

    import torch
    import yaml

    from .agents import make_agent
    from .registry import get_app
    from .trainer import evaluate, final_cfg

    run = Path(run)
    cfg = final_cfg(yaml.safe_load((run / "config.yaml").read_text()))
    if not cfg.get("residual"):
        raise SystemExit("tune_gate: this run is not a residual swarm (no `residual:` in its config)")
    app = wrap(get_app(cfg["app"]), cfg["residual"])
    vcfg = cfg.get("eval", {})
    env_cfg = {**cfg.get("env", {}), **cfg.get("eval_env", {})}
    n_eps = int(episodes or vcfg.get("val_episodes", 10))
    val_seed, metric = int(vcfg.get("val_seed", 5_000)), str(vcfg.get("select_metric", "return"))
    sign = -1.0 if str(vcfg.get("select_mode", "max")) == "min" else 1.0
    state = torch.load(run / "model.pt", map_location="cpu", weights_only=False)
    inner = get_app(cfg["app"])
    cfgs = {"trained": env_cfg}
    for n in sizes or []:
        cfgs[f"{n} agents"] = inner.scaled_env_cfg(env_cfg, int(n))
    follow = int(app.make_env(env_cfg, "val", val_seed).FOLLOW)
    rows = []
    for m in margins:
        acfg = {**state["cfg"], "gate_margin": float(m), "gate_follow": follow}
        scores, over = {}, []
        for label, ecfg in cfgs.items():
            agent = make_agent(app.make_env(ecfg, "val", val_seed), acfg)
            agent.load_state_dict(state)
            agent.cfg = acfg
            res = evaluate(app, ecfg, agent.policy(), n_eps, val_seed, "val")
            scores[label] = res[metric]
            over.append(res.get("override_rate_pct", 0.0))
        worst = min(scores.values(), key=lambda v: sign * v)
        rows.append({"margin": float(m), metric: worst, "by_size": scores, "override_rate_pct": float(np.mean(over))})
        log(f"gate margin {m}: validation {metric} " + ", ".join(f"{k} {v:.3f}" for k, v in scores.items())
            + f", overrides {rows[-1]['override_rate_pct']:.2f}%")
    best = max(rows, key=lambda r: (sign * r[metric], r["margin"]))
    state["cfg"] = {**state["cfg"], "gate_margin": best["margin"], "gate_follow": follow}
    torch.save(state, run / "model.pt")
    (run / "gate.json").write_text(__import__("json").dumps({"chosen": best, "tried": rows}, indent=2))
    log(f"chosen gate margin: {best['margin']} ({metric} {best[metric]:.3f} on {n_eps} validation fires)")
    return {"chosen": best, "tried": rows}
