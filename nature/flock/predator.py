"""Extrinsic parameter: how a predator changes a flock (pigeons with a robotic falcon).

Compares flights with the falcon to control flights, and, inside falcon flights,
frames when the falcon is close to frames when it is far.
"""

from __future__ import annotations

import numpy as np

from .io import Tracks
from .kinematics import derivatives, group_order, nearest_neighbour_distance, unit

DIST_BINS = ((0, 30), (30, 100), (100, 1e9))


def per_frame(tr: Tracks) -> dict:
    x, v, _ = derivatives(tr)
    u = unit(v)
    speed = np.linalg.norm(v, axis=-1)
    # turning rate: angle between successive headings, per second
    cosang = np.clip(np.nansum(u[1:] * u[:-1], axis=-1), -1, 1)
    turn = np.degrees(np.arccos(cosang)) / tr.dt
    turn = np.where(np.isfinite(u[1:]).all(-1) & np.isfinite(u[:-1]).all(-1), turn, np.nan)
    turn = np.vstack([np.full((1, tr.N), np.nan), turn])
    order = group_order(x, v)
    nn = nearest_neighbour_distance(x)
    c = np.nanmean(x, axis=1, keepdims=True)
    spread = np.nanmean(np.linalg.norm(x - c, axis=-1), axis=1)   # mean distance to flock centre
    return {"speed": np.nanmedian(speed, axis=1), "turn_deg_s": np.nanmedian(turn, axis=1),
            "nn": np.nanmedian(nn, axis=1), "polarisation": order["polarisation"], "spread": spread}


def compare(flights: list[Tracks]) -> dict:
    rows = []
    for tr in flights:
        f = per_frame(tr)
        rows.append({"flight": tr.name, "condition": tr.meta["condition"], "size": tr.meta["flock_size"],
                     "birds": tr.N, **{k: float(np.nanmedian(v)) for k, v in f.items()}})
    by_group = {}
    for cond in ("predator", "control"):
        for size in ("small", "big"):
            sel = [r for r in rows if r["condition"] == cond and r["size"] == size]
            if sel:
                by_group[f"{cond}/{size}"] = {"flights": len(sel), **{
                    k: float(np.median([r[k] for r in sel])) for k in ("speed", "turn_deg_s", "nn", "polarisation",
                                                                         "spread")}}
    # inside falcon flights: close vs far frames (pooled over flights, median per bin)
    near = {f"{a}-{b if b < 1e8 else 'inf'} m": {k: [] for k in ("speed", "turn_deg_s", "nn", "polarisation",
                                                                    "spread")} for a, b in DIST_BINS}
    for tr in flights:
        if tr.meta["condition"] != "predator":
            continue
        f = per_frame(tr)
        dp = tr.meta["dist_to_predator_m"]
        for (a, b), key in zip(DIST_BINS, near):
            m = (dp >= a) & (dp < b)
            for k in near[key]:
                near[key][k].extend(f[k][m][np.isfinite(f[k][m])].tolist())
    near_summary = {key: {"frames": len(vals["nn"]), **{k: float(np.median(v)) if v else None
                                                        for k, v in vals.items()}} for key, vals in near.items()}
    return {"flights": rows, "by_condition": by_group, "by_falcon_distance": near_summary}
