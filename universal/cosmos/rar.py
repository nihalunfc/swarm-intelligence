"""Galaxies as swarms: the radial acceleration relation (RAR) in SPARC.

In a swarm, an agent's acceleration is set by local neighbours, but natural swarms also show a
fixed crossover scale where short-range push changes to long-range pull (see the switch distance
in universal.features). In disc galaxies the observed acceleration g_obs is a single function of
the acceleration expected from visible matter g_bar, with one crossover scale g_dagger
(McGaugh, Lelli & Schombert 2016). We fit three laws on real SPARC rotation curves:

    Newton:          g_obs = g_bar
    RAR (McGaugh):   g_obs = g_bar / (1 - exp(-sqrt(g_bar / g_dagger)))
    swarm cohesion:  g_obs = g_bar + sqrt(g_bar * g_dagger)  (local pull plus a collective floor)

and compare g_dagger with c H0 / (2 pi), the scale a self-regulating universe would tie to the
global expansion rate. A numerical coincidence is not evidence of a mechanism.

    python -m universal.cosmos.rar
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

from .data import sparc_rar

OUT = Path(__file__).resolve().parents[2] / "results" / "universal"
C = 2.99792458e8
MPC = 3.0857e22


def laws():
    return {
        "Newton (no dark matter)": lambda gb, gd: gb,
        "RAR (McGaugh 2016)": lambda gb, gd: gb / (1 - np.exp(-np.sqrt(gb / gd))),
        "swarm cohesion floor": lambda gb, gd: gb + np.sqrt(gb * gd),
    }


def run(H0=None) -> dict:
    d = sparc_rar()
    gb, go = d["gbar"].to_numpy(), d["gobs"].to_numpy()
    res = {"n_points": int(len(d)), "n_galaxies": int(d["galaxy"].nunique())}
    for name, f in laws().items():
        def loss(lg):
            return np.mean((np.log10(go) - np.log10(f(gb, 10**lg))) ** 2)

        if name.startswith("Newton"):
            lg, mse = np.nan, loss(-10)
        else:
            r = minimize_scalar(loss, bounds=(-12, -8), method="bounded")
            lg, mse = r.x, r.fun
        resid = np.log10(go) - np.log10(f(gb, 10**lg if np.isfinite(lg) else 1e-10))
        res[name] = {"g_dagger": float(10**lg) if np.isfinite(lg) else None, "rms_dex": float(np.sqrt(mse)),
                     "bias_dex": float(resid.mean()),
                     "low_acc_bias_dex": float(resid[gb < 1e-11].mean()) if (gb < 1e-11).any() else None}
    if H0 is None:
        try:
            cj = json.loads((OUT / "cosmology.json").read_text())
            H0 = cj["late + CMB ruler r_d"][0]["H0"]
        except Exception:
            H0 = 70.0
    cH0 = C * H0 * 1e3 / MPC
    gd = res["RAR (McGaugh 2016)"]["g_dagger"]
    res["H0_used"] = H0
    res["cH0_over_2pi"] = cH0 / (2 * np.pi)
    res["g_dagger_over_cH0_over_2pi"] = gd / (cH0 / (2 * np.pi))
    res["g_dagger_over_cH0_over_6"] = gd / (cH0 / 6)  # Verlinde (2017) emergent-gravity scale
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "rar.json").write_text(json.dumps(res, indent=1))
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(5.5, 4.5))
        ax.scatter(np.log10(gb), np.log10(go), s=2, alpha=0.3, color="grey", label="SPARC points")
        xs = np.logspace(np.log10(gb.min()), np.log10(gb.max()), 200)
        for name, f in laws().items():
            g = res[name]["g_dagger"] or 1e-10
            ax.plot(np.log10(xs), np.log10(f(xs, g)), label=f"{name} ({res[name]['rms_dex']:.3f} dex)")
        ax.set(xlabel="log10 g_bar (m/s^2)", ylabel="log10 g_obs (m/s^2)", title="Radial acceleration relation")
        ax.legend(fontsize=7, frameon=False)
        fig.tight_layout()
        fig.savefig(OUT / "rar.png", dpi=130)
    except Exception:
        pass
    return res


if __name__ == "__main__":
    print(json.dumps(run(), indent=1))
