"""Scalability study (research objective 2): one trained model, many swarm sizes.

Because every agent shares one network, a model trained with a few agents can
be dropped into a swarm of any size. For each size this measures

* performance: the trained swarm, unchanged, against the app's rules, on
  held-out data (zero-shot transfer: the model never saw this many agents);
* compute: network parameters, time to choose every agent's action, one
  environment step, one training update, and replay memory per transition.

Each app says how a swarm of ``n`` agents is sized (``scaled_env_cfg``): the
energy fleet stays 1 GW but is split into more, smaller batteries; the forest
grows so each drone covers the same area.
"""

import copy
import json
import time
from pathlib import Path

import numpy as np

from .benchmark import eval_env_cfg
from .config import load_config
from .registry import get_app
from .trainer import evaluate, final_cfg


def _time(fn, repeats: int) -> float:
    fn()  # warm-up
    t = time.perf_counter()
    for _ in range(repeats):
        fn()
    return (time.perf_counter() - t) / repeats * 1000.0


def scale_study(run: str | Path, sizes: list[int], episodes: int = 5, batch_size: int = 32, log=print,
                overrides: list[str] | None = None) -> list[dict]:
    import torch

    from .agents import make_agent

    run = Path(run)
    cfg = load_config(run / "config.yaml", list(overrides or []))
    app = get_app(cfg["app"])
    if not hasattr(app, "scaled_env_cfg"):
        raise SystemExit(f"App '{cfg['app']}' does not define scaled_env_cfg")
    state = torch.load(run / "model.pt", map_location="cpu", weights_only=False)
    trained_n = app.make_env(final_cfg(cfg)["env"], "train", 0).n_agents  # a curriculum ends at its last stage
    seed = int(cfg.get("eval", {}).get("seed", 10_000))
    rows = []
    for n in sizes:
        ecfg = app.scaled_env_cfg(eval_env_cfg(cfg), n)
        env = app.make_env(ecfg, "test", seed)
        acfg = dict(state["cfg"])
        if acfg.get("agent_id") and not acfg.get("agent_id_count"):
            # Agent ids do not transfer to a new swarm size: reuse the trained ids cyclically.
            acfg["agent_id_count"] = trained_n
        agent = make_agent(env, acfg)
        agent.load_state_dict(state)
        params = sum(p.numel() for p in agent.q.parameters())

        obs, mask = env.reset(seed=seed), env.action_mask()
        act_ms = _time(lambda: agent.act(obs[None], mask[None]), 20)
        policy = agent.policy()

        def one_step():
            o = env.reset(seed=seed)
            env.step(policy(env, o, env.action_mask()))
        step_ms = _time(one_step, 5)
        rng = np.random.default_rng(0)
        B, N, D, A = batch_size, env.n_agents, env.obs_dim, env.n_actions
        batch = {
            "obs": rng.standard_normal((B, N, D)).astype(np.float32),
            "next_obs": rng.standard_normal((B, N, D)).astype(np.float32),
            "actions": rng.integers(0, A, (B, N)), "rewards": np.zeros(B, np.float32),
            "agent_rewards": np.zeros((B, N), np.float32), "discount": np.full(B, 0.9, np.float32),
            "next_mask": np.ones((B, N, A), bool),
        }
        learner = copy.deepcopy(agent)
        update_ms = _time(lambda: learner.update(batch), 5)
        bytes_per_transition = N * (2 * D * 4 + 8 + 4 + 2 * A) + 8

        log(f"[{cfg['app']}] {n} agents: evaluating swarm and rules on {episodes} episode(s) ...")
        perf = {"swarm (trained)": evaluate(app, ecfg, policy, episodes, seed)}
        for name, rule in app.BASELINES.items():
            perf[name] = evaluate(app, ecfg, rule, episodes, seed)
        for name, metrics in perf.items():
            rows.append({
                "app": cfg["app"], "agents": n, "policy": name, "trained_with": trained_n,
                **{k: metrics[k] for k in app.KEY_METRICS if k in metrics},
                "params": params, "act_ms": act_ms, "env_step_ms": step_ms,
                "update_ms": update_ms, "replay_kb_per_transition": bytes_per_transition / 1024,
            })
    return rows


def format_scale(rows: list[dict], metric: str) -> str:
    sizes = sorted({r["agents"] for r in rows})
    policies = list(dict.fromkeys(r["policy"] for r in rows))
    get = lambda n, p, k: next(r[k] for r in rows if r["agents"] == n and r["policy"] == p)
    lines = [f"**{metric}** by swarm size (model trained with {rows[0]['trained_with']} agents)", "",
             "| policy | " + " | ".join(f"{n} agents" for n in sizes) + " |",
             "| :-- | " + " | ".join("--:" for _ in sizes) + " |"]
    for p in policies:
        lines.append(f"| {p} | " + " | ".join(f"{get(n, p, metric):,.1f}" for n in sizes) + " |")
    lines += ["", "**Compute** (one CPU core)", "",
              "| agents | network params | choose all actions (ms) | env step (ms) | update, batch 32 (ms) | replay per transition (KB) |",
              "| --: | --: | --: | --: | --: | --: |"]
    for n in sizes:
        r = next(r for r in rows if r["agents"] == n)
        lines.append(f"| {n:,} | {r['params']:,} | {r['act_ms']:.2f} | {r['env_step_ms']:.1f} | "
                     f"{r['update_ms']:.1f} | {r['replay_kb_per_transition']:,.1f} |")
    return "\n".join(lines) + "\n"


def write(rows: list[dict], metric: str, out: Path) -> str:
    out.mkdir(parents=True, exist_ok=True)
    md = format_scale(rows, metric)
    (out / "scale.json").write_text(json.dumps(rows, indent=2))
    (out / "scale.md").write_text(md)
    return md
