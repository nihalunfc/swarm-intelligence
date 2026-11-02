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
        "train_history.csv", "val_history.csv"]


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
        written.append(label)
    return written


if __name__ == "__main__":
    labels = collect(Path(sys.argv[1]), Path(sys.argv[2] if len(sys.argv) > 2 else "results"))
    print("aggregated:", ", ".join(labels) or "nothing")
