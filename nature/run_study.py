"""Run the study stages on one dataset and write results/nature/<id>.json and .md.

    python nature/fetch.py fish-tetra-2024
    python nature/run_study.py fish-tetra-2024

Runs on a laptop CPU in a few minutes per recording. No GitHub Actions needed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from nature.flock.fields import fit_equation  # noqa: E402
from nature.flock.io import RAW_DIR, load_dataset, load_sources  # noqa: E402
from nature.flock.kinematics import summary  # noqa: E402
from nature.flock.rules import distance_response, topological_vs_metric  # noqa: E402

OUT = ROOT / "results" / "nature"


def run_file(dataset_id: str, fname: str, fields_min_animals: int = 20) -> dict:
    tr = load_dataset(dataset_id, fname)
    print(f"{tr.name}: {tr.T} frames, {tr.N} animals")
    res = {"recording": tr.name, "summary": summary(tr)}
    res["neighbours"] = topological_vs_metric(tr)
    res["spacing"] = distance_response(tr)
    if tr.N >= fields_min_animals and tr.D == 2:
        res["equation"] = fit_equation(tr)
    return res


def fmt(x, nd=3):
    return "n/a" if x is None else f"{x:.{nd}f}"


def write_markdown(src: dict, runs: list[dict], path: Path) -> None:
    L = [f"# {src['title']}", "", f"Species: {src['species']}. Source: [{src['citation']}]({src['url']}), "
         f"license {src['license']}. Real recorded data, no simulation.", ""]
    checks = src.get("published_checks", {})
    L += ["## 1. Motion summary", "",
          "Speed and spacing use smoothed tracks (0.2 s Savitzky-Golay). BL = body length.", "",
          "| Recording | Animals | Minutes | Median speed (cm/s) | Mean speed (BL/s) | Median nearest neighbour (cm) "
          "| Polarisation | Time polarised >0.8 | Time milling >0.5 |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in runs:
        s = r["summary"]
        L.append(f"| {r['recording']} | {s['animals']} | {s['duration_s'] / 60:.0f} | {100 * s['median_speed_m_s']:.1f} "
                 f"| {s['mean_speed_bl_s']:.1f} | {100 * s['median_nn_distance_m']:.1f} | {s['polarisation_mean']:.2f} "
                 f"| {100 * s['fraction_polarised_gt_0.8']:.0f}% | {100 * s['fraction_milling_gt_0.5']:.1f}% |")
    if checks:
        L += ["", f"Published check: the paper's model uses a preferred speed of {checks.get('mean_speed_cm_s')} cm/s "
              f"(set from the data) and an equilibrium spacing of {checks.get('nn_distance_cm')} cm."]
    L += ["", "## 2. Who each animal listens to (topological vs metric)", "",
          "Held-out R^2 for predicting each animal's turn over the next "
          f"{runs[0]['neighbours']['lag_s']:.1f} s from its neighbours' mean heading and the direction to their centre.",
          "", "| Recording | Best k nearest | R^2 | Best radius (BL) | R^2 | Better rule |", "| --- | --- | --- | --- | --- | --- |"]
    for r in runs:
        n = r["neighbours"]
        L.append(f"| {r['recording']} | {n['best_k']} | {n['best_k_r2']:.3f} | {n['best_radius_bl']:g} "
                 f"| {n['best_radius_r2']:.3f} | {n['winner']} |")
    L += ["", "## 3. Spacing rule (repulsion then attraction)", "",
          "Mean acceleration of an animal toward each of its 6 nearest neighbours, by distance. The preferred "
          "spacing is where it changes from moving away (repulsion) to moving closer (attraction).", "",
          "| Recording | Preferred spacing (BL) | Preferred spacing (cm) |", "| --- | --- | --- |"]
    for r in runs:
        z = r["spacing"]["preferred_spacing_bl"]
        L.append(f"| {r['recording']} | {fmt(z, 2)} | {fmt(None if z is None else z * src.get('body_length_cm', 1), 1)} |")
    eq = [r for r in runs if "equation" in r]
    if eq:
        L += ["", "## 4. Fluid equation fit (Toner-Tu library, sparse regression)", "",
              "Target: the flock's coarse-grained acceleration Dv/dt. Fit on the first half of each "
              "recording, scored on the second half.", ""]
        for r in eq:
            e = r["equation"]
            L += [f"**{r['recording']}**: continuity check residual {100 * e['continuity_residual_fraction']:.1f}% "
                  f"(should be near 0). Held-out R^2: all terms {e['r2_test_full']:.3f}, sparse "
                  f"{e['r2_test_sparse']:.3f}.", "",
                  "| Term | Meaning | Sparse coefficient | R^2 alone |", "| --- | --- | --- | --- |"]
            for t in e["terms"]:
                c = e["coef_sparse"].get(t)
                L.append(f"| `{t.replace('|', '¦')}` | {e['term_meaning'][t]} | {'' if c is None else f'{c:.3g}'} "
                         f"| {e['single_term_r2_test'][t]:.3f} |")
            L.append("")
    path.write_text("\n".join(L) + "\n")


def main(argv):
    ids = [a for a in argv if not a.startswith("--")]
    dataset_id = ids[0] if ids else "fish-tetra-2024"
    src = load_sources()[dataset_id]
    files = [f for f in src["files"] if (RAW_DIR / dataset_id / f).exists()]
    if not files:
        raise SystemExit(f"No files for {dataset_id}. Run: python nature/fetch.py {dataset_id}")
    OUT.mkdir(parents=True, exist_ok=True)
    js = OUT / f"{dataset_id}.json"
    if "--md-only" in argv:
        runs = json.loads(js.read_text())["runs"]
    else:
        runs = [run_file(dataset_id, f) for f in files]
        js.write_text(json.dumps({"dataset": dataset_id, "runs": runs}, indent=1))
    write_markdown(src, runs, OUT / f"{dataset_id}.md")
    print(f"wrote {OUT / dataset_id}.md")


if __name__ == "__main__":
    main(sys.argv[1:])
