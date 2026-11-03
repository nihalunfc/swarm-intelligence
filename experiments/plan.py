"""Turn experiments/queue.yaml into a GitHub Actions job matrix (one entry per seed)."""

import json
import os
import sys
from pathlib import Path

import yaml


def _spec(path: str) -> dict | None:
    spec = yaml.safe_load(Path(path).read_text()) or {}
    # A queue runs only on the branch it was written for, so merging it into another
    # branch (e.g. the paper's) does not start the same experiments again there.
    ref = os.environ.get("GITHUB_REF_NAME")
    if spec.get("branch") and ref and ref != spec["branch"]:
        print(f"queue is for branch {spec['branch']}, not {ref}: nothing to run", file=sys.stderr)
        return None
    return spec


def plan(path: str = "experiments/queue.yaml") -> list[dict]:
    spec = _spec(path)
    if spec is None:
        return []
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


def plan_robustness(path: str = "experiments/queue.yaml") -> list[dict]:
    """One job per ``robustness`` entry: re-test a label's trained seeds (from this run, or
    from an earlier run given by ``run_id``) under the scenarios in experiments/robustness.yaml."""
    spec = _spec(path)
    if spec is None:
        return []
    return [{"label": r["label"], "run_id": str(r.get("run_id", "")), "scenario_set": r.get("scenario_set", ""),
             "episodes": str(r.get("episodes", "")), "extras": ",".join(["hotel", *r.get("extras", [])])}
            for r in spec.get("robustness") or []]


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--robustness"]:
        print(json.dumps({"include": plan_robustness(*args[1:])}))
    else:
        print(json.dumps({"include": plan(*args)}))
