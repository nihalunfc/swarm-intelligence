"""Combine several training seeds of one experiment into one table with
confidence intervals and paired comparisons against every rule.

Input: run directories written by ``swarm train`` (each has ``episodes.json``
and ``config.yaml``). Runs are grouped by their ``label`` (config key, else
the app name), so variants of a method (plain, residual, ...) can be compared
in the same report.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import yaml

from .registry import get_app
from .stats import fmt_ci, fmt_p, hierarchical_bootstrap, paired_test, variant_test

SWARM = "swarm (trained)"


def load_runs(paths: list[str | Path]) -> list[dict]:
    runs = []
    for p in paths:
        p = Path(p)
        for ep in sorted(p.rglob("episodes.json")) if p.is_dir() else []:
            cfg = yaml.safe_load((ep.parent / "config.yaml").read_text())
            data = json.loads(ep.read_text())
            runs.append({"dir": ep.parent, "cfg": cfg, **data})
    if not runs:
        raise SystemExit("No episodes.json found under: " + ", ".join(map(str, paths)))
    return runs


def _matrix(runs: list[dict], policy: str, metric: str) -> np.ndarray:
    """(seeds, episodes); NaN where a reference row does not report the metric."""
    return np.array([[e.get(metric, np.nan) for e in r["policies"][policy]] for r in runs], dtype=float)


def _ci(x: np.ndarray):
    return hierarchical_bootstrap(x) if not np.isnan(x).any() else (np.nan, np.nan, np.nan)


def _paired(a: np.ndarray, b: np.ndarray):
    if np.isnan(b).any():
        return {"diff": np.nan, "diff_lo": np.nan, "diff_hi": np.nan, "p_value": np.nan}
    return paired_test(a, b)


def summarize(runs: list[dict], metrics: list[str] | None = None) -> dict:
    """Stats per (label, policy, metric) and swarm-vs-rule comparisons."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in runs:
        groups[r["cfg"].get("label") or r["app"]].append(r)
    out = {}
    for label, rs in groups.items():
        app_name = rs[0]["app"]
        n_eps = {len(r["policies"][SWARM]) for r in rs}
        if len(n_eps) != 1 or len({r["eval_seed"] for r in rs}) != 1 or len({r["split"] for r in rs}) != 1:
            raise SystemExit(f"{label}: runs were evaluated on different episodes; re-evaluate them identically")
        keys = metrics or [m for m in get_app(app_name).KEY_METRICS if m in rs[0]["policies"][SWARM][0]]
        rules = [p for p in rs[0]["policies"] if p != SWARM]
        policies = {}
        for pol in [SWARM, *rules]:
            # A rule does not depend on the training seed: use one copy of its episodes.
            sub = rs if pol == SWARM else rs[:1]
            policies[pol] = {m: _ci(_matrix(sub, pol, m)) for m in keys}
        comparisons = {rule: {m: _paired(_matrix(rs, SWARM, m), _matrix(rs[:1], rule, m)[0]) for m in keys}
                       for rule in rules}
        out[label] = {"app": app_name, "split": rs[0]["split"], "seeds": sorted(r["seed"] for r in rs),
                      "episodes": n_eps.pop(), "metrics": keys, "policies": policies, "comparisons": comparisons}
    return out


def to_markdown(summary: dict, digits: int = 2) -> str:
    lines = []
    for label, s in summary.items():
        lines += [f"## {label}", "",
                  f"{len(s['seeds'])} training seeds ({', '.join(map(str, s['seeds']))}) x {s['episodes']} "
                  f"{s['split']} episode(s). Mean with 95% bootstrap interval (seeds and episodes resampled; "
                  f"rules have no training seed, so their interval covers episodes only).", "",
                  "| policy | " + " | ".join(s["metrics"]) + " |",
                  "| :-- | " + " | ".join("--:" for _ in s["metrics"]) + " |"]
        for pol, ms in s["policies"].items():
            lines.append(f"| {pol} | " + " | ".join("–" if np.isnan(ms[m][0]) else fmt_ci(*ms[m], digits)
                                                   for m in s["metrics"]) + " |")
        lines += ["", "**Swarm minus rule** on the same episodes (difference [95% CI], bootstrap p-value over seeds "
                  "and episodes):", "",
                  "| vs rule | " + " | ".join(s["metrics"]) + " |",
                  "| :-- | " + " | ".join("--:" for _ in s["metrics"]) + " |"]
        for rule, ms in s["comparisons"].items():
            cells = ["–" if np.isnan(ms[m]["diff"]) else
                     f"{fmt_ci(ms[m]['diff'], ms[m]['diff_lo'], ms[m]['diff_hi'], digits)}, p={fmt_p(ms[m]['p_value'])}"
                     for m in s["metrics"]]
            lines.append(f"| {rule} | " + " | ".join(cells) + " |")
        lines.append("")
    return "\n".join(lines)


def write(summary: dict, out: Path) -> str:
    out.parent.mkdir(parents=True, exist_ok=True)
    md = to_markdown(summary)
    out.with_suffix(".md").write_text("# Multi-seed results\n\n" + md)
    out.with_suffix(".json").write_text(json.dumps(summary, indent=2, default=float))
    return md


def compare_variants(runs: list[dict], base: str, metrics: list[str], digits: int = 2) -> str:
    """One table: every label (variant) against ``base`` on the same test episodes.

    Used for ablations and method comparisons (plain vs residual vs MAPPO ...).
    """
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in runs:
        groups[r["cfg"].get("label") or r["app"]].append(r)
    if base not in groups:
        raise SystemExit(f"base variant '{base}' not found among: {', '.join(groups)}")
    lines = [f"Variants against **{base}** ({len(groups[base])} seeds): mean [95% CI] and difference from "
             f"{base} [95% CI], p-value.", "",
             "| variant | seeds | " + " | ".join(f"{m} | diff" for m in metrics) + " |",
             "| :-- | --: | " + " | ".join("--: | --:" for _ in metrics) + " |"]
    for label, rs in groups.items():
        cells = []
        for m in metrics:
            a, b = _matrix(rs, SWARM, m), _matrix(groups[base], SWARM, m)
            cells.append(fmt_ci(*hierarchical_bootstrap(a), digits))
            if label == base:
                cells.append("–")
            else:
                t = variant_test(a, b)
                cells.append(f"{fmt_ci(t['diff'], t['diff_lo'], t['diff_hi'], digits)}, p={fmt_p(t['p_value'])}")
        lines.append(f"| {label} | {len(rs)} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"
