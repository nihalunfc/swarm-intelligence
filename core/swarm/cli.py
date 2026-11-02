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

    from .benchmark import load_agent

    run = Path(args.run)
    cfg = load_config(run / "config.yaml", args.set)
    app = get_app(cfg["app"])
    if not hasattr(app, "export_replay"):
        raise SystemExit(f"App '{cfg['app']}' has no replay export")
    state = torch.load(run / "model.pt", map_location="cpu", weights_only=False)
    agent = load_agent(app.make_env(cfg["env"], "train", 0), state)
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


def cmd_seeds(args):
    """Train the same config with several seeds (in parallel processes), then aggregate."""
    import os
    import subprocess
    import sys

    from . import aggregate

    cfg = load_config(args.config, args.set)
    label = cfg.get("label") or Path(args.config).stem
    out = Path(args.out) / f"seeds-{label}-{time.strftime('%Y%m%d-%H%M%S')}"
    out.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "OMP_NUM_THREADS": str(args.threads), "MKL_NUM_THREADS": str(args.threads)}
    procs, done = [], []
    for seed in args.seeds:
        cmd = [sys.executable, "-m", "swarm.cli", "train", "--config", args.config, "--out", str(out / f"seed-{seed}"),
               "--set", *args.set, f"seed={seed}", f"label={label}"]
        while len([p for p in procs if p.poll() is None]) >= args.jobs:
            time.sleep(2)
        log = open(out / f"seed-{seed}.log", "w")
        procs.append(subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, env=env))
        print(f"started seed {seed} -> {out / f'seed-{seed}.log'}")
    for p in procs:
        done.append(p.wait())
    if any(done):
        raise SystemExit(f"{sum(c != 0 for c in done)} seed run(s) failed; see the logs in {out}")
    print(aggregate.write(aggregate.summarize(aggregate.load_runs([out])), out / "summary"))
    print(f"Saved to {out}")


def cmd_aggregate(args):
    from . import aggregate

    runs = aggregate.load_runs(args.runs)
    md = aggregate.write(aggregate.summarize(runs, args.metrics), Path(args.output))
    if args.compare_to:
        metrics = args.metrics or get_app(runs[0]["app"]).KEY_METRICS[:2]
        table = aggregate.compare_variants(runs, args.compare_to, metrics)
        Path(args.output).with_name(Path(args.output).name + "-variants.md").write_text(table)
        md += "\n" + table
    print(md)


def cmd_robustness(args):
    import yaml

    from . import robustness

    runs = sorted({p.parent for d in args.runs for p in Path(d).rglob("model.pt")})
    if not runs:
        raise SystemExit("no trained runs (model.pt) under: " + ", ".join(args.runs))
    app = yaml.safe_load((runs[0] / "config.yaml").read_text())["app"]
    scenarios = yaml.safe_load(Path(args.scenarios).read_text())[args.scenario_set or app]
    res = robustness.run(runs, scenarios, args.episodes)
    metric = args.metric or get_app(app).KEY_METRICS[0]
    print(robustness.write(res, metric, Path(args.output)))


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
    b.add_argument("--apps", nargs="+", default=[a for a in APPS if a not in ("citylearn", "vmas")], choices=list(APPS))
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

    sd = sub.add_parser("seeds", help="train one config with several seeds and report confidence intervals")
    sd.add_argument("--config", required=True)
    sd.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    sd.add_argument("--jobs", type=int, default=2, help="seeds trained at the same time")
    sd.add_argument("--threads", type=int, default=2, help="CPU threads per seed")
    sd.add_argument("--set", nargs="*", default=[], metavar="KEY=VALUE")
    sd.add_argument("--out", default=str(REPO / "runs"))
    sd.set_defaults(fn=cmd_seeds)

    ag = sub.add_parser("aggregate", help="combine seed runs into one table with CIs and paired tests")
    ag.add_argument("runs", nargs="+", help="run directories (searched recursively for episodes.json)")
    ag.add_argument("--output", required=True, help="output path without extension (.md and .json are written)")
    ag.add_argument("--metrics", nargs="*", default=None)
    ag.add_argument("--compare-to", default=None, help="label of the variant every other label is compared with")
    ag.set_defaults(fn=cmd_aggregate)

    rb = sub.add_parser("robustness", help="evaluate trained seeds and rules under failures, noise and new conditions")
    rb.add_argument("runs", nargs="+", help="directories searched for trained runs (model.pt)")
    rb.add_argument("--scenarios", default=str(REPO / "experiments" / "robustness.yaml"))
    rb.add_argument("--scenario-set", default=None, help="key in the scenarios file (default: the app name)")
    rb.add_argument("--episodes", type=int, default=None)
    rb.add_argument("--metric", default=None)
    rb.add_argument("--output", required=True)
    rb.set_defaults(fn=cmd_robustness)

    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
