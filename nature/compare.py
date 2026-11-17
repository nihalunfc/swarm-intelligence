"""Cross-species table (stage 6) from the per-dataset results in results/nature/*.json.

    python nature/compare.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parents[1] / "results" / "nature"


def med(xs):
    xs = [x for x in xs if x is not None and np.isfinite(x)]
    return float(np.median(xs)) if xs else None


def f(x, nd=2):
    return "n/a" if x is None else f"{x:.{nd}f}"


def rows():
    out = []
    fish = json.loads((OUT / "fish-tetra-2024.json").read_text())["runs"]
    for label, sel in (("fish, 39", [r for r in fish if "N=39" in r["recording"]]),
                       ("fish, 8", [r for r in fish if "N=8" in r["recording"]])):
        bl = 0.025
        out.append({
            "species": f"Black neon tetra ({label})", "setting": "lab tank, 2D", "groups": len(sel),
            "speed_bl_s": med([r["summary"]["median_speed_m_s"] / bl for r in sel]),
            "nn_bl": med([r["summary"]["median_nn_distance_m"] / bl for r in sel]),
            "switch_bl": med([r["spacing"]["preferred_spacing_bl"] for r in sel]),
            "polarisation": med([r["summary"]["polarisation_mean"] for r in sel]),
            "topo_wins": f"{sum(r['neighbours']['winner'] == 'topological' for r in sel)}/{len(sel)}",
            "best_k": med([r["neighbours"]["best_k"] for r in sel]),
            "fluid_r2": med([r["equation_2nn"]["r2_test_sparse"] for r in sel if "equation_2nn" in r]),
        })
    for ds, name, setting, bl in (("jackdaw-2019", "Jackdaw", "wild, 3D stereo", 0.34),
                                  ("pigeon-predation-2022", "Homing pigeon", "GPS 5 Hz, 2D", 0.32)):
        res = json.loads((OUT / f"{ds}.json").read_text())
        runs = res["runs"]
        ruled = [r for r in runs if "neighbours" in r]
        signal = [r for r in ruled if r["neighbours"]["winner"] != "no signal"]
        out.append({
            "species": name, "setting": setting, "groups": len(runs),
            "speed_bl_s": med([r["summary"]["median_speed_m_s"] / bl for r in runs]),
            "nn_bl": med([r["summary"]["median_nn_distance_m"] / bl for r in runs]),
            "switch_bl": med([r["spacing"]["preferred_spacing_bl"] for r in ruled]),
            "polarisation": med([r["summary"]["polarisation_mean"] for r in runs]),
            "topo_wins": f"{sum(r['neighbours']['winner'] == 'topological' for r in signal)}/{len(signal)}",
            "best_k": med([r["neighbours"]["best_k"] for r in signal if r["neighbours"]["winner"] == "topological"]),
            "fluid_r2": None,
        })
    sw = json.loads((OUT / "swift-2017.json").read_text())
    bl = sw["body_length_m"]
    pf = sw["per_file"].values()
    out.append({
        "species": "Chimney swift", "setting": "wild, 3D, at roost", "groups": len(sw["per_file"]),
        "speed_bl_s": med([v["speed"] / bl for v in pf]), "nn_bl": med([v["nn"] / bl for v in pf]),
        "switch_bl": None, "polarisation": med([v["polarisation"] for v in pf]),
        "topo_wins": "not run", "best_k": None,
        "fluid_r2": sw["fits"]["sigma=2nn"]["r2_test_sparse"],
    })
    return out


def main():
    R = rows()
    L = ["# Cross-species comparison", "",
         "All real recorded data. BL = body length (fish 2.5 cm from the paper; birds approximate field-guide "
         "lengths: jackdaw 0.34 m, pigeon 0.32 m, swift 0.13 m). Medians over groups.", "",
         "| Species | Setting | Groups | Speed (BL/s) | Nearest neighbour (BL) | Repulsion-to-attraction switch (BL) "
         "| Polarisation | Topological wins | Median best k | Fluid fit R^2 (held out) |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in R:
        L.append(f"| {r['species']} | {r['setting']} | {r['groups']} | {f(r['speed_bl_s'], 1)} | {f(r['nn_bl'], 1)} "
                 f"| {f(r['switch_bl'], 1)} | {f(r['polarisation'])} | {r['topo_wins']} | {f(r['best_k'], 0)} "
                 f"| {f(r['fluid_r2'])} |")
    L += ["", "Fluid fit uses the same method for fish and swifts (sparse Toner-Tu library, kernel width 2 nearest-"
          "neighbour distances for both). Jackdaw and pigeon groups are too short or too few "
          "for the field fit."]
    (OUT / "comparison.md").write_text("\n".join(L) + "\n")
    (OUT / "comparison.json").write_text(json.dumps(R, indent=1))
    print("\n".join(L))


if __name__ == "__main__":
    main()
