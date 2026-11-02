"""Run manifests and optional experiment tracking.

Every run directory gets ``manifest.json``: the exact code version (git
commit and whether the tree had uncommitted changes), library versions,
machine, command line and timings, so any number in ``results/`` can be
traced back to what produced it.

If MLflow is installed and ``SWARM_MLFLOW`` is set (to a tracking URI, or
``1`` for the local ``mlruns/`` folder), the run's config, metrics and files
are also logged there. Nothing is required to run without it.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _git(*args: str) -> str | None:
    try:
        return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _version(mod: str) -> str | None:
    try:
        return __import__(mod).__version__
    except Exception:
        return None


def build_manifest(cfg: dict, started: float) -> dict:
    status = _git("status", "--porcelain", "--untracked-files=no")
    return {
        "app": cfg.get("app"),
        "seed": cfg.get("seed"),
        "git_commit": _git("rev-parse", "HEAD"),
        "git_dirty": bool(status) if status is not None else None,
        "command": " ".join([Path(sys.argv[0]).name, *sys.argv[1:]]),
        "started": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(started)),
        "seconds": round(time.time() - started, 1),
        "python": platform.python_version(),
        "packages": {m: _version(m) for m in ("numpy", "pandas", "torch", "yaml")},
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "ci": {k: os.environ[k] for k in ("GITHUB_RUN_ID", "GITHUB_SHA", "GITHUB_REF_NAME") if k in os.environ},
    }


def write_manifest(run_dir: Path, cfg: dict, started: float) -> dict:
    m = build_manifest(cfg, started)
    (run_dir / "manifest.json").write_text(json.dumps(m, indent=2))
    return m


def _flat(d: dict, prefix: str = "") -> dict:
    out = {}
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(_flat(v, key + "."))
        else:
            out[key] = v
    return out


def track(run_dir: Path, cfg: dict, rows: list[dict]) -> None:
    """Log to MLflow when ``SWARM_MLFLOW`` is set and mlflow is importable."""
    uri = os.environ.get("SWARM_MLFLOW")
    if not uri:
        return
    try:
        import mlflow
    except ImportError:
        print("SWARM_MLFLOW is set but mlflow is not installed (pip install mlflow); skipping tracking")
        return
    if uri != "1":
        mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(str(cfg.get("app")))
    with mlflow.start_run(run_name=run_dir.name):
        mlflow.log_params({k: str(v)[:250] for k, v in _flat(cfg).items()})
        for r in rows:
            tag = r["policy"].replace(" ", "_").replace("(", "").replace(")", "")
            mlflow.log_metrics({f"{tag}.{k}": v for k, v in r.items() if isinstance(v, (int, float))})
        mlflow.log_artifacts(str(run_dir))
