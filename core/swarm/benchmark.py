"""Train (or load) the swarm for an app, evaluate it against the app's simple
baselines on held-out data, and write one results table."""

import csv
import json
import time
from pathlib import Path

import yaml

from .manifest import track, write_manifest
from .registry import get_app, is_trainable
from .trainer import evaluate_episodes, mean_metrics, train


def eval_env_cfg(cfg: dict) -> dict:
    return {**cfg.get("env", {}), **cfg.get("eval_env", {})}


def make_run_dir(root: str | Path, app: str) -> Path:
    run = Path(root) / app / time.strftime("%Y%m%d-%H%M%S")
    run.mkdir(parents=True, exist_ok=True)
    return run


def load_agent(env, state: dict):
    """Rebuild a trained swarm (DQN or MAPPO) for ``env`` from a saved state."""
    if state.get("algo") == "mappo":
        from .ppo import PPOAgent

        agent = PPOAgent(env, state["cfg"])
    else:
        from .agents import make_agent

        agent = make_agent(env, state["cfg"])
    agent.load_state_dict(state)
    return agent


def run_app(name: str, cfg: dict, run_dir: Path | None = None, model_path: str | None = None, log=print) -> list[dict]:
    started = time.time()
    app = get_app(name)
    if cfg.get("residual"):
        from .residual import wrap

        app = wrap(app, cfg["residual"])
    if not is_trainable(app):
        return app.benchmark_rows(cfg)

    import torch

    if model_path:
        state = torch.load(model_path, map_location="cpu", weights_only=False)
        agent = load_agent(app.make_env(cfg.get("env", {}), "train", 0), state)
        history = []
    else:
        log(f"[{name}] training swarm ...")
        agent, history = train(app, cfg, log=log)

    ecfg = eval_env_cfg(cfg)
    episodes = int(cfg.get("eval", {}).get("episodes", 1))
    seed = int(cfg.get("eval", {}).get("seed", 10_000))
    split = str(cfg.get("eval", {}).get("split", "test"))
    policies = {"swarm (trained)": agent.policy(), **{k: v for k, v in app.BASELINES.items() if k != "follow rule"}}
    per_episode = {p: evaluate_episodes(app, ecfg, pol, episodes, seed, split) for p, pol in policies.items()}
    for reference in getattr(app, "REFERENCES", []):
        per_episode.update(reference(app, ecfg, split, episodes, seed))
    rows = [{"app": name, "policy": p, **mean_metrics(eps)} for p, eps in per_episode.items()]

    if run_dir is not None:
        run_dir.mkdir(parents=True, exist_ok=True)
        torch.save(agent.state_dict(), run_dir / "model.pt")
        (run_dir / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
        if history:
            with open(run_dir / "train_history.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(history[0]))
                w.writeheader()
                w.writerows(history)
        if getattr(agent, "val_history", None):
            with open(run_dir / "val_history.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(agent.val_history[0]))
                w.writeheader()
                w.writerows(agent.val_history)
        (run_dir / "results.json").write_text(json.dumps(rows, indent=2))
        (run_dir / "episodes.json").write_text(json.dumps(
            {"app": name, "seed": cfg.get("seed", 0), "split": split, "eval_seed": seed, "policies": per_episode}))
        (run_dir / "results.md").write_text(format_table(rows, app.KEY_METRICS))
        write_manifest(run_dir, cfg, started)
        track(run_dir, cfg, rows)
    return rows


def format_table(rows: list[dict], metrics: list[str]) -> str:
    head = "| app | policy | " + " | ".join(metrics) + " |"
    sep = "| :-- | :-- | " + " | ".join("--:" for _ in metrics) + " |"
    lines = [head, sep]
    for r in rows:
        vals = []
        for m in metrics:
            v = r.get(m, "")
            vals.append(f"{v + 0.0:,.3f}" if isinstance(v, float) else str(v))
        lines.append(f"| {r['app']} | {r['policy']} | " + " | ".join(vals) + " |")
    return "\n".join(lines) + "\n"
