"""Command line entry point: ``swarm train | evaluate | benchmark | replay``."""

import argparse
import json
import time
from pathlib import Path

from .benchmark import eval_env_cfg, format_table, make_run_dir, run_app
from .config import load_config
from .registry import APPS, get_app

REPO = Path(__file__).resolve().parents[2]


def _config_for(app: str, path: str | None, overrides: list[str]) -> dict:
    cfg = load_config(path or REPO / "configs" / f"{app}.yaml", overrides)
    cfg.setdefault("app", app)
    return cfg


def cmd_train(args):
    cfg = load_config(args.config, args.set)
    app = cfg["app"]
    run = make_run_dir(args.out, app)
    rows = run_app(app, cfg, run_dir=run)
    print(format_table(rows, get_app(app).KEY_METRICS))
    print(f"Saved run to {run}")


def cmd_evaluate(args):
    run = Path(args.run)
    cfg = load_config(run / "config.yaml", args.set)
    rows = run_app(cfg["app"], cfg, model_path=str(run / "model.pt"))
    print(format_table(rows, get_app(cfg["app"]).KEY_METRICS))


def cmd_benchmark(args):
    out = Path(args.out) / f"benchmark-{time.strftime('%Y%m%d-%H%M%S')}"
    out.mkdir(parents=True, exist_ok=True)
    sections, all_rows = [], []
    for name in args.apps:
        cfg = _config_for(name, None, args.set)
        rows = run_app(name, cfg, run_dir=out / name)
        all_rows += rows
        sections.append(f"## {name}\n\n" + format_table(rows, get_app(name).KEY_METRICS))
    report = "# Swarm benchmark\n\n" + "\n".join(sections)
    (out / "results.md").write_text(report)
    (out / "results.json").write_text(json.dumps(all_rows, indent=2))
    print(report)
    print(f"Saved to {out}")


def cmd_replay(args):
    import torch

    from .agents import make_agent

    run = Path(args.run)
    cfg = load_config(run / "config.yaml", args.set)
    app = get_app(cfg["app"])
    if not hasattr(app, "export_replay"):
        raise SystemExit(f"App '{cfg['app']}' has no replay export")
    state = torch.load(run / "model.pt", map_location="cpu", weights_only=False)
    probe = app.make_env(cfg["env"], "train", 0)
    agent = make_agent(probe, state["cfg"])
    agent.load_state_dict(state)
    policies = {"swarm (trained)": agent.policy(), **app.BASELINES}
    app.export_replay(eval_env_cfg(cfg), policies, args.output, episodes=args.episodes)
    print(f"Wrote {args.output}")


def cmd_scale(args):
    from .scale import scale_study, write

    rows = scale_study(args.run, args.sizes, args.episodes)
    cfg = load_config(Path(args.run) / "config.yaml", [])
    metric = args.metric or get_app(cfg["app"]).KEY_METRICS[0]
    out = Path(args.out) / f"scale-{cfg['app']}-{time.strftime('%Y%m%d-%H%M%S')}"
    print(write(rows, metric, out))
    print(f"Saved to {out}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="swarm", description="Swarm intelligence engine")
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("train", help="train the swarm for one app and compare with baselines")
    t.add_argument("--config", required=True)
    t.add_argument("--set", nargs="*", default=[], metavar="KEY=VALUE")
    t.add_argument("--out", default=str(REPO / "runs"))
    t.set_defaults(fn=cmd_train)

    e = sub.add_parser("evaluate", help="re-evaluate a saved run")
    e.add_argument("--run", required=True)
    e.add_argument("--set", nargs="*", default=[], metavar="KEY=VALUE")
    e.set_defaults(fn=cmd_evaluate)

    b = sub.add_parser("benchmark", help="train and compare every app, one results table")
    b.add_argument("--apps", nargs="+", default=list(APPS), choices=list(APPS))
    b.add_argument("--set", nargs="*", default=[], metavar="KEY=VALUE")
    b.add_argument("--out", default=str(REPO / "runs"))
    b.set_defaults(fn=cmd_benchmark)

    r = sub.add_parser("replay", help="export recorded episodes for a web dashboard")
    r.add_argument("--run", required=True)
    r.add_argument("--output", required=True)
    r.add_argument("--episodes", type=int, default=3)
    r.add_argument("--set", nargs="*", default=[], metavar="KEY=VALUE")
    r.set_defaults(fn=cmd_replay)

    s = sub.add_parser("scale", help="run a trained model at other swarm sizes and time it")
    s.add_argument("--run", required=True)
    s.add_argument("--sizes", nargs="+", type=int, default=[10, 100, 1000])
    s.add_argument("--episodes", type=int, default=5)
    s.add_argument("--metric", default=None, help="results column to tabulate (default: the app's first)")
    s.add_argument("--out", default=str(REPO / "runs"))
    s.set_defaults(fn=cmd_scale)

    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
