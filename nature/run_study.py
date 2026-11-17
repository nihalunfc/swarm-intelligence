"""Run the study stages on one dataset and write results/nature/<id>.json and .md.

    python nature/fetch.py fish-tetra-2024
    python nature/run_study.py fish-tetra-2024

Runs on a laptop CPU in a few minutes per recording. No GitHub Actions needed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from nature.flock.fields import fit_equation  # noqa: E402
from nature.flock.io import (  # noqa: E402,E501
    RAW_DIR,
    load_dataset,
    load_jackdaw_flocks,
    load_pigeon_flights,
    load_sources,
)
from nature.flock.kinematics import summary  # noqa: E402
from nature.flock.predator import compare as predator_compare  # noqa: E402
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
        # same kernel in neighbour units as the swift fit (width 2 nearest-neighbour distances)
        nn_bl = res["summary"]["median_nn_distance_m"] / tr.body_length
        res["equation_2nn"] = fit_equation(tr, sigma_bl=2 * nn_bl, cell_bl=nn_bl)
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


def bird_tracks(dataset_id: str, src: dict):
    raw = RAW_DIR / dataset_id
    if dataset_id == "jackdaw-2019":
        return load_jackdaw_flocks(raw / "DataS1.txt", src["body_length_m"])
    if dataset_id == "pigeon-predation-2022":
        return load_pigeon_flights(raw / "all_emp_data.csv", src["body_length_m"])
    raise NotImplementedError(dataset_id)


def run_birds(dataset_id: str, src: dict) -> dict:
    tracks = bird_tracks(dataset_id, src)
    runs = []
    for tr in tracks:
        print(f"{tr.name}: {tr.T} frames, {tr.N} track ids")
        r = {"recording": tr.name, "summary": summary(tr),
             "meta": {k: v for k, v in tr.meta.items() if not hasattr(v, "shape")}}
        # rules need enough birds to compare neighbour counts
        if tr.N >= 20:
            r["neighbours"] = topological_vs_metric(tr)
            r["spacing"] = distance_response(tr)
        runs.append(r)
    out = {"dataset": dataset_id, "runs": runs}
    if dataset_id == "pigeon-predation-2022":
        pc = predator_compare(tracks)
        out["predator"] = {k: v for k, v in pc.items() if k != "flights"}
    return out


def write_bird_markdown(src: dict, res: dict, path: Path) -> None:
    runs = res["runs"]
    L = [f"# {src['title']}", "", f"Species: {src['species']}. Source: [{src['citation']}]({src['url']}), "
         f"license {src['license']}. Real recorded data, no simulation. "
         f"BL = body length, taken as {src['body_length_m']} m (approximate).", "",
         "## 1. Motion summary", "",
         "| Recording | Track ids | Seconds | Median speed (m/s) | Median nearest neighbour (m) | Polarisation "
         "| Milling |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in runs:
        s = r["summary"]
        L.append(f"| {r['recording']} | {s['animals']} | {s['duration_s']:.0f} | {s['median_speed_m_s']:.1f} "
                 f"| {s['median_nn_distance_m']:.2f} | {s['polarisation_mean']:.2f} | {s['milling_mean']:.2f} |")
    with_rules = [r for r in runs if "neighbours" in r]
    if with_rules:
        L += ["", "## 2. Who each bird listens to, and preferred spacing", "",
              f"Held-out R^2 for predicting each bird's turn over the next {with_rules[0]['neighbours']['lag_s']:.1f} s. "
              "'no signal' means neither rule explains even 1% of turns.", "",
              "| Recording | Best k | R^2 | Best radius (BL) | R^2 | Better rule | Repulsion-to-attraction switch (BL) |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
        for r in with_rules:
            n, z = r["neighbours"], r["spacing"]["preferred_spacing_bl"]
            L.append(f"| {r['recording']} | {n['best_k']} | {n['best_k_r2']:.3f} | {n['best_radius_bl']:g} "
                     f"| {n['best_radius_r2']:.3f} | {n['winner']} | {fmt(z, 2)} |")
    if "predator" in res:
        p = res["predator"]
        L += ["", "## 3. Effect of the robotic falcon (extrinsic parameter)", "",
              "Median per flight, then median over flights.", "",
              "| Condition | Flights | Speed (m/s) | Turning (deg/s) | Nearest neighbour (m) | Polarisation "
              "| Spread from centre (m) |", "| --- | --- | --- | --- | --- | --- | --- |"]
        for k, v in p["by_condition"].items():
            L.append(f"| {k} | {v['flights']} | {v['speed']:.1f} | {v['turn_deg_s']:.1f} | {v['nn']:.2f} "
                     f"| {v['polarisation']:.3f} | {v['spread']:.1f} |")
        L += ["", "Inside falcon flights, by the falcon's distance to the nearest bird:", "",
              "| Falcon distance | Frames | Speed (m/s) | Turning (deg/s) | Nearest neighbour (m) | Polarisation "
              "| Spread (m) |", "| --- | --- | --- | --- | --- | --- | --- |"]
        for k, v in p["by_falcon_distance"].items():
            L.append(f"| {k} | {v['frames']} | {fmt(v['speed'], 1)} | {fmt(v['turn_deg_s'], 1)} | {fmt(v['nn'], 2)} "
                     f"| {fmt(v['polarisation'], 3)} | {fmt(v['spread'], 1)} |")
    path.write_text("\n".join(L) + "\n")


def run_swifts(src: dict) -> dict:
    from nature.flock.swift import BODY_LENGTH, fit_equation_swifts, summary_and_samples
    raw = RAW_DIR / "swift-2017"
    files = [raw / f for f in src["files"] if f.endswith(".hdf5") and (raw / f).exists()]
    rows, frames = summary_and_samples(files, every=15)
    keys = ("birds", "speed", "nn", "polarisation", "milling_about_chimney")
    per_file = {}
    for f in files:
        sel = [r for r in rows if r["file"] == f.name]
        per_file[f.name] = {"frames": len(sel), **{k: float(np.median([r[k] for r in sel])) for k in keys}}
    nn = float(np.median([r["nn"] for r in rows]))
    fits = {}
    for mult in (2, 4):
        for roost in (False, True):
            fits[f"sigma={mult}nn" + (" +roost" if roost else "")] = fit_equation_swifts(
                frames, sigma=mult * nn, cell=nn, rho_min=0.05 / nn ** 2, roost_terms=roost)
    return {"dataset": "swift-2017", "body_length_m": BODY_LENGTH, "median_nn_m": nn, "per_file": per_file,
            "fits": fits}


def write_swift_markdown(src: dict, res: dict, path: Path) -> None:
    L = [f"# {src['title']}", "", f"Species: {src['species']}. Source: [{src['citation']}]({src['url']}) "
         f"(Zenodo mirror 5082229), license {src['license']}. Real recorded data, no simulation. "
         "Likely ghost tracks (speed under 2 or over 25 m/s) are dropped, as the data README advises.", "",
         "## 1. Motion summary (one frame in 15 sampled)", "",
         "| File | Frames | Birds per frame | Speed (m/s) | Nearest neighbour (m) | Polarisation "
         "| Circling about chimney (-1 to 1) |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for f, v in res["per_file"].items():
        L.append(f"| {f} | {v['frames']} | {v['birds']:.0f} | {v['speed']:.1f} | {v['nn']:.2f} "
                 f"| {v['polarisation']:.2f} | {v['milling_about_chimney']:.2f} |")
    L += ["", "## 2. Fluid equation fit (horizontal plane)", "",
          f"Target: coarse-grained horizontal acceleration. Grid cell = median nearest-neighbour distance "
          f"({res['median_nn_m']:.1f} m). Fit on the first half of the frames, scored on the second half. "
          "'+roost' adds two candidate new terms: a pull toward the chimney and circling around it.", "",
          "| Fit | Samples | Held-out R^2 (all terms) | Held-out R^2 (sparse) | Kept terms |",
          "| --- | --- | --- | --- | --- |"]
    for name, r in res["fits"].items():
        kept = ", ".join(f"`{t.replace('|', '¦')}` {c:.3g}" for t, c in r["coef_sparse"].items())
        L.append(f"| {name} | {r['samples']} | {r['r2_test_full']:.3f} | {r['r2_test_sparse']:.3f} | {kept} |")
    path.write_text("\n".join(L) + "\n")


def main(argv):
    ids = [a for a in argv if not a.startswith("--")]
    dataset_id = ids[0] if ids else "fish-tetra-2024"
    src = load_sources()[dataset_id]
    if dataset_id == "swift-2017":
        OUT.mkdir(parents=True, exist_ok=True)
        js = OUT / "swift-2017.json"
        res = json.loads(js.read_text()) if "--md-only" in argv else run_swifts(src)
        js.write_text(json.dumps(res, indent=1))
        write_swift_markdown(src, res, OUT / "swift-2017.md")
        print(f"wrote {OUT / 'swift-2017'}.md")
        return
    if dataset_id in ("jackdaw-2019", "pigeon-predation-2022"):
        OUT.mkdir(parents=True, exist_ok=True)
        js = OUT / f"{dataset_id}.json"
        res = json.loads(js.read_text()) if "--md-only" in argv else run_birds(dataset_id, src)
        js.write_text(json.dumps(res, indent=1))
        write_bird_markdown(src, res, OUT / f"{dataset_id}.md")
        print(f"wrote {OUT / dataset_id}.md")
        return
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
