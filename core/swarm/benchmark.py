"""Train (or load) the swarm for an app, evaluate it against the app's simple
baselines on held-out data, and write one results table."""

import csv
import json
import time
from pathlib import Path

import yaml

from .registry import get_app, is_trainable
from .trainer import evaluate, train


def eval_env_cfg(cfg: dict) -> dict:
    return {**cfg.get("env", {}), **cfg.get("eval_env", {})}


def make_run_dir(root: str | Path, app: str) -> Path:
    run = Path(root) / app / time.strftime("%Y%m%d-%H%M%S")
    run.mkdir(parents=True, exist_ok=True)
    return run


def run_app(name: str, cfg: dict, run_dir: Path | None = None, model_path: str | None = None, log=print) -> list[dict]:
    app = get_app(name)
    if not is_trainable(app):
        return app.benchmark_rows(cfg)

    import torch

    from .agents import SwarmAgent

    if model_path:
        state = torch.load(model_path, map_location="cpu", weights_only=False)
        probe = app.make_env(cfg.get("env", {}), "train", 0)
        agent = SwarmAgent(probe.obs_dim, probe.n_actions, probe.n_agents, state["cfg"])
        agent.load_state_dict(state)
        history = []
    else:
        log(f"[{name}] training swarm ...")
        agent, history = train(app, cfg, log=log)

    ecfg = eval_env_cfg(cfg)
    episodes = int(cfg.get("eval", {}).get("episodes", 1))
    seed = int(cfg.get("eval", {}).get("seed", 10_000))
    rows = [{"app": name, "policy": "swarm (trained)", **evaluate(app, ecfg, agent.policy(), episodes, seed)}]
    for bname, policy in app.BASELINES.items():
        rows.append({"app": name, "policy": bname, **evaluate(app, ecfg, policy, episodes, seed)})

    if run_dir is not None:
        run_dir.mkdir(parents=True, exist_ok=True)
        torch.save(agent.state_dict(), run_dir / "model.pt")
        (run_dir / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
        if history:
            with open(run_dir / "train_history.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(history[0]))
                w.writeheader()
                w.writerows(history)
        (run_dir / "results.json").write_text(json.dumps(rows, indent=2))
        (run_dir / "results.md").write_text(format_table(rows, app.KEY_METRICS))
    return rows


def format_table(rows: list[dict], metrics: list[str]) -> str:
    head = "| app | policy | " + " | ".join(metrics) + " |"
    sep = "| :-- | :-- | " + " | ".join("--:" for _ in metrics) + " |"
    lines = [head, sep]
    for r in rows:
        vals = []
        for m in metrics:
            v = r.get(m, "")
            vals.append(f"{v:,.3f}" if isinstance(v, float) else str(v))
        lines.append(f"| {r['app']} | {r['policy']} | " + " | ".join(vals) + " |")
    return "\n".join(lines) + "\n"
