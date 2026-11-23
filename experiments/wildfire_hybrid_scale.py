"""Scale test for the rule-led hybrid drone swarm (configs/wildfire-hybrid.yaml).

For every trained seed: tune the confidence gate on validation fires (6 drones,
never the test fires), then run the swarm unchanged at every swarm size, with
and without sensor noise, next to the nearest-fire rule. Also runs the same
swarm with the gate off (margin 0), and any extra run families given with
--family (e.g. the old-inputs ablation), so each change can be judged alone.

    python experiments/wildfire_hybrid_scale.py \
        --family "hybrid (local inputs)=runs/hybrid" --family "hybrid (old inputs)=runs/global" \
        --out results/scale-wildfire-hybrid

Writes <out>.md (tables with 95% bootstrap intervals over seeds and episodes,
and swarm-minus-rule paired differences) and <out>.json (every episode).
"""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

METRIC = "forest_saved_pct"


def _runs(root: str) -> list[Path]:
    return sorted({p.parent for p in Path(root).rglob("model.pt")})


def _episodes(task: dict) -> dict:
    """One (policy, seed, size, noise) cell: per-episode metrics."""
    import torch
    import yaml

    torch.set_num_threads(1)
    from apps import wildfire
    from swarm.agents import make_agent
    from swarm.benchmark import eval_env_cfg
    from swarm.residual import wrap
    from swarm.robustness import scenario_app
    from swarm.trainer import evaluate_episodes, final_cfg

    cfg = final_cfg(yaml.safe_load((Path(task["run"]) / "config.yaml").read_text()))
    app = wrap(wildfire, cfg["residual"])
    ecfg = wildfire.scaled_env_cfg(eval_env_cfg(cfg), task["n"])
    sapp = scenario_app(app, {"noise": task["noise"]}) if task["noise"] > 0 else app
    if task["policy"] == "rule":
        # The rule through the residual env, so it uses the same tie-break random stream as a swarm
        # that follows it: a swarm that never overrides then scores exactly the rule's numbers.
        # It reads the true state, so sensor noise does not reach it.
        policy = app.BASELINES["follow rule"]
        sapp = app
    else:
        state = torch.load(Path(task["run"]) / "model.pt", map_location="cpu", weights_only=False)
        env = app.make_env(ecfg, "test", task["seed"])
        acfg = dict(state["cfg"])
        if task["gate"] == "off":
            acfg["gate_margin"] = None
        agent = make_agent(env, acfg)
        agent.load_state_dict(state)
        policy = agent.policy()
        if task["noise"] > 0:
            inner = policy
            policy = lambda e, o, m: inner(e.inner, o, m)  # noqa: E731  (scenario env wraps the residual env)
    rows = evaluate_episodes(sapp, ecfg, policy, task["episodes"], task["seed"])
    return {**{k: v for k, v in task.items() if k != "run"}, "run": str(task["run"]),
            "values": [r[METRIC] for r in rows], "overrides": [r.get("override_rate_pct", 0.0) for r in rows]}


def _boot(cells: list[list[float]], reps: int = 2000, rng=None) -> tuple[float, float, float]:
    """Mean and 95% interval, resampling seeds then episodes (cells = one list per seed)."""
    rng = rng or np.random.default_rng(0)
    arr = [np.asarray(c, float) for c in cells]
    means = []
    for _ in range(reps):
        pick = rng.integers(len(arr), size=len(arr))
        means.append(np.mean([arr[i][rng.integers(len(arr[i]), size=len(arr[i]))].mean() for i in pick]))
    return float(np.mean([a.mean() for a in arr])), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", action="append", required=True, help="label=directory of trained seed runs")
    ap.add_argument("--sizes", type=int, nargs="+", default=[6, 24, 100, 1000])
    ap.add_argument("--noise", type=float, nargs="+", default=[0.0, 0.1, 0.3])
    ap.add_argument("--episodes", type=int, default=10)
    ap.add_argument("--seed", type=int, default=10_000, help="first test fire (training never sees 10,000+)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--skip-tune", action="store_true")
    ap.add_argument("--val-sizes", type=int, nargs="*", default=[],
                    help="also tune the gate on validation fires at these swarm sizes (worst size counts)")
    ap.add_argument("--out", default="results/scale-wildfire-hybrid")
    args = ap.parse_args()

    from swarm.residual import tune_gate

    families = [f.split("=", 1) for f in args.family]
    gates = {}
    for _label, root in families:
        for run in _runs(root):
            if not args.skip_tune or not (run / "gate.json").exists():
                tune_gate(run, sizes=args.val_sizes)
            gates[str(run)] = json.loads((run / "gate.json").read_text())["chosen"]

    tasks = []
    first = _runs(families[0][1])[0]
    for n in args.sizes:
        tasks.append(dict(policy="rule", gate="-", family="nearest-fire rule", run=first, n=n, noise=0.0,
                          episodes=args.episodes, seed=args.seed))
        for noise in args.noise:
            for k, (label, root) in enumerate(families):
                for run in _runs(root):
                    for gate in (["on", "off"] if k == 0 else ["on"]):
                        tasks.append(dict(policy="swarm", gate=gate, family=label, run=run, n=n, noise=noise,
                                          episodes=args.episodes, seed=args.seed))
    with ProcessPoolExecutor(args.workers) as pool:
        done = list(pool.map(_episodes, tasks))

    rule = {d["n"]: d["values"] for d in done if d["policy"] == "rule"}
    lines = [
        "# Scale test: rule-led hybrid drone swarm",
        "",
        f"Trained with 6 drones only (configs/wildfire-hybrid.yaml); every larger swarm is a zero-shot test on "
        f"a forest tiled with one launch pad per 16x16 tile. {args.episodes} test fires per size (seeds "
        f"{args.seed}+, never used in training or validation), the same fires for every policy. "
        "Mean [95% bootstrap interval over training seeds and fires]. Sensor noise is Gaussian noise on the "
        "drones' inputs; the rule reads the true state, so its row does not change with noise.",
        "",
        "Gate: each drone follows the rule unless its best override beats \"follow rule\" by a margin chosen "
        "on 20 validation fires with 6 drones" + (f" and with {', '.join(map(str, args.val_sizes))} drones (the worst size counts)" if args.val_sizes else "") + " (an infinite margin is the rule itself). "
        "\"gate off\" is the same network acting greedily.",
        "",
        "Chosen margins: " + "; ".join(f"{lab}: " + ", ".join(str(gates[str(r)]["margin"]) for r in _runs(root))
                                       for lab, root in families),
        "",
    ]
    rng = np.random.default_rng(0)
    out_rows = []
    for noise in args.noise:
        lines += [f"## {METRIC}, sensor noise {noise}", "",
                  "| policy | " + " | ".join(f"{n:,} drones" for n in args.sizes) + " |",
                  "| :-- | " + " | ".join("--:" for _ in args.sizes) + " |"]
        labels = [("nearest-fire rule", "-")] + [(families[0][0], "on"), (families[0][0], "off")] + \
            [(lab, "on") for lab, _ in families[1:]]
        for fam, gate in labels:
            cells, diffs = [], []
            for n in args.sizes:
                if fam == "nearest-fire rule":
                    seeds = [rule[n]]
                else:
                    seeds = [d["values"] for d in done if d["family"] == fam and d["gate"] == gate
                             and d["n"] == n and d["noise"] == noise]
                m, lo, hi = _boot(seeds, rng=rng)
                cell = f"{m:.1f} [{lo:.1f}, {hi:.1f}]"
                if fam != "nearest-fire rule":
                    dm, dlo, dhi = _boot([list(np.subtract(s, rule[n])) for s in seeds], rng=rng)
                    diffs.append(f"{dm:+.1f} [{dlo:+.1f}, {dhi:+.1f}]")
                    out_rows.append(dict(family=fam, gate=gate, n=n, noise=noise, mean=m, lo=lo, hi=hi,
                                         diff=dm, diff_lo=dlo, diff_hi=dhi))
                cells.append(cell)
            name = fam if gate in ("-", "on") else f"{fam}, gate off"
            lines.append(f"| {name} | " + " | ".join(cells) + " |")
            if diffs:
                lines.append("| &nbsp;&nbsp;minus rule | " + " | ".join(diffs) + " |")
        lines.append("")
    ov = {}
    for d in done:
        if d["policy"] == "swarm":
            ov.setdefault((d["family"], d["gate"], d["n"], d["noise"]), []).extend(d["overrides"])
    lines += ["## How often drones leave the rule (% of drone-steps)", "",
              "| policy | noise | " + " | ".join(f"{n:,}" for n in args.sizes) + " |",
              "| :-- | --: | " + " | ".join("--:" for _ in args.sizes) + " |"]
    for (fam, gate) in sorted({(k[0], k[1]) for k in ov}):
        for noise in args.noise:
            name = fam if gate == "on" else f"{fam}, gate off"
            lines.append(f"| {name} | {noise} | " + " | ".join(
                f"{np.mean(ov[(fam, gate, n, noise)]):.2f}" for n in args.sizes) + " |")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".md").write_text("\n".join(lines) + "\n")
    out.with_suffix(".json").write_text(json.dumps({"gates": gates, "summary": out_rows, "episodes": done}, indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
