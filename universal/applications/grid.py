"""Energy / grid: batteries as a swarm that regulates feeder load to a moving set point.

Agents: N batteries (default 10 x 100 MW / 400 MWh, the fleet in apps/energy). Each battery sees
only (a) the current load, (b) its own state of charge, (c) the mean state of charge of its
neighbours (alignment: batteries that are fuller than neighbours discharge more). The fleet's
collective action follows the damped Regulator toward a set point = rolling 24 h mean load.
Data: real ERCOT COAST 2020 hourly load from the repo sample. KPI: peak and spread reduction,
compared with no batteries and with a simple threshold rule. This is a framework demo, not the
trained swarm in apps/energy (see results/energy.md for that).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

REPO_SAMPLE = "apps/energy/data/sample/ercot_nrel_2020.csv"


def simulate(load: np.ndarray, n=10, p_max=100.0, e_max=400.0, rule="swarm", seed=0) -> dict:
    rng = np.random.default_rng(seed)
    soc = np.full(n, 0.5 * e_max) + rng.normal(0, 5, n)
    net = np.empty_like(load)
    target_window = 24
    for t, x in enumerate(load):
        target = load[max(0, t - target_window):t + 1].mean()
        if rule == "none":
            power = np.zeros(n)
        elif rule == "threshold":  # discharge above 1.05 x target, charge below 0.95 x target
            sign = 1.0 if x > 1.05 * target else (-1.0 if x < 0.95 * target else 0.0)
            power = np.full(n, sign * p_max)
        else:
            want = x - target  # positive = fleet should discharge
            fleet = np.clip(want, -n * p_max, n * p_max)
            # alignment: share by relative state of charge (fuller batteries give more)
            room = soc if fleet > 0 else (e_max - soc)
            share = room / room.sum() if room.sum() > 1e-9 else np.full(n, 1.0 / n)
            power = fleet * share
        power = np.clip(power, -p_max, p_max)
        power = np.where(power > 0, np.minimum(power, soc), -np.minimum(-power, e_max - soc))
        soc = soc - power
        net[t] = x - power.sum()
    return {"peak_MW": float(net.max()), "std_MW": float(net.std()), "net": net}


def trained_swarm_results(root="results/runs/energy") -> dict:
    """Held-out test results of the trained battery swarm (apps/energy, VDN, 10 seeds), same months and data."""
    import json
    from pathlib import Path

    rows = {}
    for f in sorted(Path(root).glob("seed-*/episodes.json")):
        pol = json.loads(f.read_text())["policies"]
        for name, eps in pol.items():
            rows.setdefault(name, []).append((eps[0]["peak_reduction_mw"], eps[0]["std_reduction_pct"]))
    return {name: {"seeds": len(v), "peak_cut_MW": float(np.mean([a for a, _ in v])),
                   "spread_cut_pct": float(np.mean([b for _, b in v]))} for name, v in rows.items()}


def demo(path=REPO_SAMPLE) -> dict:
    load = pd.read_csv(path)["demand_mw"].to_numpy(float)
    load = load[-24 * 92:]  # Oct-Dec, the held-out test months used in apps/energy
    base = simulate(load, rule="none")
    out = {"data": "ERCOT COAST 2020 Oct-Dec (real)"}
    for r in ["threshold", "swarm"]:
        s = simulate(load, rule=r)
        out[f"framework {r} rule"] = {"peak_cut_MW": base["peak_MW"] - s["peak_MW"],
                                      "spread_cut_pct": 100 * (1 - s["std_MW"] / base["std_MW"])}
    # The trained swarm cannot be re-run without PyTorch, so its recorded held-out results are used:
    # same data, same months, same 10 x 100 MW / 400 MWh fleet (results/runs/energy, seeds 0-9).
    out["trained swarm and baselines (apps/energy, recorded test runs)"] = trained_swarm_results()
    return out
