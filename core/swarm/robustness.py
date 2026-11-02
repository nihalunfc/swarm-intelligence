"""Robustness tests: how gracefully the swarm and the rules degrade.

A swarm's main promise over a central controller is that losing some agents,
or some information, should cost a little performance, not everything. Each
scenario changes the evaluation only (models are not retrained):

* ``fail``: a share of agents fails at ``fail_at`` (a fraction of the episode;
  0 = from the start). A failed agent takes the app's ``null_action`` (a drone
  holds, a battery idles, an attendant takes no new rooms), and the others are
  not told. The same agents fail for every policy in an episode.
* ``noise``: Gaussian noise of this standard deviation on every observation.
* ``set``: other environment overrides for conditions never seen in training
  (stronger wind, a busier hotel day ...), as for ``--set eval_env.*``.

Rules see the true state (they read the environment directly), so ``noise``
only affects learned policies; ``fail`` affects everyone.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import numpy as np
import yaml

from .config import apply_overrides
from .env import SwarmEnv
from .stats import fmt_ci, hierarchical_bootstrap


class PerturbedEnv(SwarmEnv):
    def __init__(self, inner: SwarmEnv, fail: float = 0.0, fail_at: float = 0.0, noise: float = 0.0,
                 horizon: int | None = None, seed: int = 0):
        self.inner, self.fail, self.fail_at, self.noise = inner, float(fail), float(fail_at), float(noise)
        self.n_agents, self.n_actions, self.obs_dim = inner.n_agents, inner.n_actions, inner.obs_dim
        self.horizon = horizon
        self.seed = seed

    def reset(self, seed=None):
        s = self.seed if seed is None else seed
        self.prng = np.random.default_rng(s + 104_729)
        k = int(round(self.fail * self.n_agents))
        self.failed = np.zeros(self.n_agents, bool)
        self.failed[self.prng.choice(self.n_agents, k, replace=False)] = True
        self.t = 0
        return self._noisy(self.inner.reset(seed=seed))

    def _noisy(self, obs):
        if self.noise > 0:
            obs = obs + self.prng.normal(0, self.noise, obs.shape).astype(np.float32)
        return obs

    def _down(self):
        return self.failed & (self.t >= self.fail_at * (self.horizon or 0))

    def action_mask(self):
        m = self.inner.action_mask().copy()
        down = self._down()
        if down.any():
            m[down] = False
            m[down, self.inner.null_action] = True
        return m

    def step(self, actions):
        a = np.array(actions, copy=True)
        down = self._down()
        a[down] = self.inner.null_action
        override = getattr(self.inner, "override", None)  # rules that assign work by side effect
        if isinstance(override, dict):
            for i in np.nonzero(down)[0]:
                override.pop(int(i), None)
        obs, r, term, trunc, info = self.inner.step(a)
        self.t += 1
        return self._noisy(obs), r, term, trunc, info

    def episode_metrics(self):
        return self.inner.episode_metrics()

    def __getattr__(self, name):
        if name == "inner":
            raise AttributeError(name)
        return getattr(self.inner, name)


def _horizon(env) -> int:
    for attr in ("max_steps", "n_steps"):
        if hasattr(env, attr):
            return int(getattr(env, attr))
    if hasattr(env, "end"):
        return int(env.end - env.start) if env.end else len(env.load)
    return 0


def scenario_app(app, sc: dict):
    """An app look-alike whose environments carry the scenario's perturbations."""
    import types

    def make_env(env_cfg, split, seed):
        inner = app.make_env(env_cfg, split, seed)
        inner.reset(seed=seed)
        return PerturbedEnv(inner, sc.get("fail", 0.0), sc.get("fail_at", 0.0), sc.get("noise", 0.0),
                            _horizon(inner), seed)

    def lift(policy):
        return lambda env, obs, mask: policy(env.inner, obs, mask)

    return types.SimpleNamespace(make_env=make_env, KEY_METRICS=app.KEY_METRICS,
                                 BASELINES={k: lift(v) for k, v in app.BASELINES.items()})


def run(run_dirs: list[Path], scenarios: list[dict], episodes: int | None = None, log=print) -> dict:
    """Evaluate every seed's swarm and every rule under every scenario."""
    import torch

    from .benchmark import eval_env_cfg, load_agent
    from .registry import get_app
    from .trainer import evaluate_episodes

    out: dict = {"scenarios": [], "app": None}
    for sc in scenarios:
        per_policy: dict[str, list[list[float]]] = {}
        for k, rd in enumerate(run_dirs):
            cfg = yaml.safe_load((rd / "config.yaml").read_text())
            app = get_app(cfg["app"])
            if cfg.get("residual"):
                from .residual import wrap

                app = wrap(app, cfg["residual"])
            out["app"] = cfg["app"]
            ecfg = apply_overrides(eval_env_cfg(cfg), list(sc.get("set", [])))
            n_eps = episodes or int(cfg.get("eval", {}).get("episodes", 1))
            seed = int(cfg.get("eval", {}).get("seed", 10_000))
            sapp = scenario_app(app, sc)
            state = torch.load(rd / "model.pt", map_location="cpu", weights_only=False)
            agent = load_agent(app.make_env(cfg.get("env", {}), "train", 0), state)
            pols = {"swarm (trained)": agent.policy()}
            if k == 0:  # rules do not depend on the training seed
                pols.update({n: p for n, p in sapp.BASELINES.items() if n != "follow rule"})
            for name, pol in pols.items():
                rows = evaluate_episodes(sapp, ecfg, pol, n_eps, seed)
                per_policy.setdefault(name, []).append(rows)
        log(f"scenario {sc['name']}: done")
        out["scenarios"].append({**sc, "policies": per_policy})
    return out


def to_markdown(res: dict, metric: str, digits: int = 2) -> str:
    names = [s["name"] for s in res["scenarios"]]
    policies = list(res["scenarios"][0]["policies"])
    base = res["scenarios"][0]
    lines = [f"**{metric}** under each scenario: mean [95% CI] and, in brackets after it, the share of the "
             f"policy's own '{base['name']}' result that is kept.", "",
             "| policy | " + " | ".join(names) + " |", "| :-- | " + " | ".join("--:" for _ in names) + " |"]
    for p in policies:
        cells = []
        ref = np.mean([[e[metric] for e in rows] for rows in base["policies"][p]])
        for s in res["scenarios"]:
            x = np.array([[e[metric] for e in rows] for rows in s["policies"][p]])
            m, lo, hi = hierarchical_bootstrap(x)
            kept = f" ({100 * m / ref:.0f}%)" if ref else ""
            cells.append(fmt_ci(m, lo, hi, digits) + kept)
        lines.append(f"| {p} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def write(res: dict, metrics: str | list[str], out: Path) -> str:
    out.parent.mkdir(parents=True, exist_ok=True)
    metrics = [metrics] if isinstance(metrics, str) else metrics
    present = res["scenarios"][0]["policies"]
    first = next(iter(present.values()))[0][0]
    md = "\n".join(to_markdown(res, m) for m in metrics if m in first)
    note = ("Failed agents take the app's null action from the failure time on, and the others are not told. "
            "Sensor noise is added to the agents' observations only; rules and references that read the true "
            "state are not affected by it.\n\n")
    out.with_suffix(".md").write_text(f"# Robustness: {res['app']}\n\n" + note + md)
    slim = copy.deepcopy(res)
    out.with_suffix(".json").write_text(json.dumps(slim))
    return md
