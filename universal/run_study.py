"""Run the universal swarm study on every downloaded dataset.

    python -m universal.fetch
    python -m universal.run_study            # writes results/universal/
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from . import ensemble
from .equation import fit_drift, fit_growth
from .features import event_features, series_features, track_features
from .loaders import available, load

OUT = Path(__file__).resolve().parents[1] / "results" / "universal"
COSMIC = {"sparc", "pantheon", "bao", "chronometers"}


def _median_dicts(ds: list[dict]) -> dict:
    keys = {k for d in ds for k, v in d.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
    return {k: float(np.nanmedian([d[k] for d in ds if k in d and d[k] is not None])) for k in keys}


def study_one(key: str) -> dict:
    d = load(key)
    row = {"key": key, "category": d.category, "group": d.group, "notes": d.notes}
    if d.tracks is not None:
        tf = track_features(d.tracks)
        row["tracks"] = tf
    if d.series:
        sf = [series_features(s) for s in d.series]
        dr = [fit_drift(s) for s in d.series]
        row["series"] = _median_dicts(sf)
        row["drift"] = _median_dicts([x for x in dr if x])
        row["n_series"] = len(d.series)
        cum = [s for s in d.series if s.cumulative]
        if cum:
            gf = [fit_growth(s) for s in cum]
            gf = [g for g in gf if g]
            best = pd.Series([g["best"] for g in gf]).value_counts().to_dict()
            row["growth"] = {**_median_dicts([{k: v for k, v in g.items() if k != "models"} for g in gf]),
                             "best_model_counts": best, "n_curves": len(gf)}
    if d.events:
        row["events"] = [{"label": e.label, "n": int(len(e.sizes)), **event_features(e)} for e in d.events]
    return row


def flat(row: dict) -> dict:
    """One numeric feature vector per dataset for the ensemble."""
    f = {"key": row["key"], "group": row["group"]}
    t = row.get("tracks", {})
    for k in ["polarization", "speed_cv", "spacing_cv", "persistence", "alpha_align", "beta_cohesion",
              "gamma_speed", "rule_r2", "switch_r_over_dnn"]:
        f[f"tr_{k}"] = t.get(k, np.nan)
    s = row.get("series", {})
    for k in ["dfa_increments", "dfa_level", "spectral_slope", "ar1", "burstiness", "kurtosis_increments"]:
        f[f"se_{k}"] = s.get(k, np.nan)
    dr = row.get("drift", {})
    for k in ["a1", "a2", "taylor_gamma"]:
        f[f"dr_{k}"] = dr.get(k, np.nan)
    g = row.get("growth", {})
    f["gr_theta"] = g.get("theta", np.nan)
    ev = row.get("events", [])
    if ev:
        e = ev[0]
        f["ev_tail_alpha"] = e.get("tail_alpha", np.nan)
        f["ev_pl_vs_ln"] = e.get("pl_vs_lognormal_LR", np.nan)
    return f


def main(keys: list[str] | None = None) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for k in keys or available():
        if k in COSMIC:
            continue
        t0 = time.time()
        try:
            r = study_one(k)
        except Exception as e:  # keep going; the report lists the failure
            r = {"key": k, "error": repr(e)}
        r["seconds"] = round(time.time() - t0, 1)
        print(k, r.get("error", "ok"), r["seconds"], flush=True)
        rows.append(r)
    (OUT / "datasets.json").write_text(json.dumps(rows, indent=1, default=float))
    table = pd.DataFrame([flat(r) for r in rows if "error" not in r])
    table.to_csv(OUT / "features.csv", index=False)
    ens = ensemble.analyse(table)
    (OUT / "ensemble.json").write_text(json.dumps(ens, indent=1, default=float))
    ensemble.report(rows, table, ens, OUT)


if __name__ == "__main__":
    import sys

    main(sys.argv[1:] or None)
