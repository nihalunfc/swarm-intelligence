"""Turn experiments/queue.yaml into a GitHub Actions job matrix (one entry per seed)."""

import json
import sys
from pathlib import Path

import yaml


def plan(path: str = "experiments/queue.yaml") -> list[dict]:
    spec = yaml.safe_load(Path(path).read_text()) or {}
    jobs = []
    for exp in spec.get("experiments") or []:
        label = exp.get("label") or Path(exp["config"]).stem
        for seed in exp.get("seeds", [0, 1, 2, 3, 4]):
            jobs.append({"config": exp["config"], "label": label, "seed": int(seed),
                         "set": " ".join(exp.get("set", [])), "extras": ",".join(["hotel", *exp.get("extras", [])]),
                         "scale": " ".join(str(n) for n in exp.get("scale", [])),
                         "scale_set": " ".join(exp.get("scale_set", []))})
    if len(jobs) > 256:
        sys.exit(f"{len(jobs)} jobs: GitHub allows at most 256 per matrix; split the queue")
    return jobs


if __name__ == "__main__":
    print(json.dumps({"include": plan(*sys.argv[1:])}))
