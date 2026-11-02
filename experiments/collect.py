"""Gather the per-seed runs downloaded from GitHub Actions into results/.

For each label: copy each seed's small files to results/runs/<label>/seed-<k>/
(the model weights stay in the workflow artifacts) and write the multi-seed
summary to results/<label>.md and .json.
"""

import shutil
import sys
from collections import defaultdict
from pathlib import Path

import yaml

from swarm import aggregate

KEEP = ["config.yaml", "episodes.json", "manifest.json", "results.json", "results.md",
        "train_history.csv", "val_history.csv", "scale.json", "scale.md"]


def scale_summary(label: str, seed_dirs: list[Path]) -> str | None:
    """Mean [95% CI over training seeds] of every scale-study metric, by swarm size."""
    import json

    import numpy as np

    from swarm.stats import fmt_ci, hierarchical_bootstrap

    rows = [r for d in seed_dirs if (d / "scale.json").exists() for r in json.loads((d / "scale.json").read_text())]
    if not rows:
        return None
    skip = {"app", "agents", "policy", "trained_with", "params", "act_ms", "env_step_ms", "update_ms",
            "replay_kb_per_transition"}
    metrics = [k for k in rows[0] if k not in skip]
    sizes = sorted({r["agents"] for r in rows})
    policies = list(dict.fromkeys(r["policy"] for r in rows))
    n_seeds = len([d for d in seed_dirs if (d / "scale.json").exists()])
    out = [f"# Scale study: {label}", "",
           f"{n_seeds} training seed(s), each trained with {rows[0]['trained_with']} agents and run unchanged at every size. "
           "Mean [95% bootstrap interval over training seeds]; the rules do not depend on the seed.", ""]
    for m in metrics:
        out += [f"**{m}**", "", "| policy | " + " | ".join(f"{n:,} agents" for n in sizes) + " |",
                "| :-- | " + " | ".join("--:" for _ in sizes) + " |"]
        for p in policies:
            cells = []
            for n in sizes:
                v = np.array([r[m] for r in rows if r["agents"] == n and r["policy"] == p and m in r], float)
                cells.append(fmt_ci(*hierarchical_bootstrap(v[:, None])) if len(v) else "–")
            out.append(f"| {p} | " + " | ".join(cells) + " |")
        out.append("")
    out += ["**Compute** (seed 0's run; one CPU core)", "",
            "| agents | network params | choose all actions (ms) | env step (ms) | update, batch 32 (ms) |",
            "| --: | --: | --: | --: | --: |"]
    for n in sizes:
        r = next(r for r in rows if r["agents"] == n)
        out.append(f"| {n:,} | {r['params']:,} | {r['act_ms']:.2f} | {r['env_step_ms']:.1f} | {r['update_ms']:.1f} |")
    return "\n".join(out) + "\n"


def collect(downloads: Path, results: Path) -> list[str]:
    by_label = defaultdict(list)
    for ep in downloads.rglob("episodes.json"):
        cfg = yaml.safe_load((ep.parent / "config.yaml").read_text())
        by_label[cfg.get("label") or cfg["app"]].append((cfg.get("seed", 0), ep.parent))
    written = []
    for label, runs in by_label.items():
        dest = results / "runs" / label
        if dest.exists():
            shutil.rmtree(dest)
        for seed, src in runs:
            d = dest / f"seed-{seed}"
            d.mkdir(parents=True, exist_ok=True)
            for name in KEEP:
                if (src / name).exists():
                    shutil.copy2(src / name, d / name)
        aggregate.write(aggregate.summarize(aggregate.load_runs([dest])), results / label)
        md = scale_summary(label, sorted(dest.iterdir()))
        if md:
            (results / f"scale-{label}.md").write_text(md)
        written.append(label)
    return written


if __name__ == "__main__":
    labels = collect(Path(sys.argv[1]), Path(sys.argv[2] if len(sys.argv) > 2 else "results"))
    print("aggregated:", ", ".join(labels) or "nothing")
