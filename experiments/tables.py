"""Method and ablation tables: every variant against one base method, on shared test episodes.

Reads results/runs/<label>/seed-*/ (written by collect.py) and writes
results/methods-<app>.md. Variants that have not run yet are skipped.

    PYTHONPATH=core:. python experiments/tables.py
"""

import sys
from pathlib import Path

from swarm import aggregate

TABLES = {
    "energy": {
        "base": "energy",
        "variants": ["energy", "energy-qmix", "energy-independent", "energy-3-step", "energy-mappo",
                     "energy-no-val-selection"],
        "metrics": ["std_reduction_pct", "peak_reduction_mw"],
        "about": "Battery swarm (10 batteries). Base: VDN, 1-step DQN, checkpoint chosen on validation.",
    },
    "hotel-housekeeping": {
        "base": "hotel-housekeeping",
        "variants": ["hotel-housekeeping", "hotel-housekeeping-residual", "hotel-housekeeping-mappo",
                     "hotel-housekeeping-independent", "hotel-housekeeping-qmix"],
        "metrics": ["guest_wait_hours", "early_promises_kept_pct"],
        "about": "Housekeeping swarm (8 attendants). Base: VDN DQN. Residual = soonest-needed rule plus learned overrides.",
    },
    "wildfire": {
        "base": "wildfire-imitate",
        "variants": ["wildfire", "wildfire-imitate", "wildfire-imitate-qmix", "wildfire-mappo",
                     "wildfire-imitate-messages", "wildfire-residual"],
        "metrics": ["forest_saved_pct", "peak_fire_cells"],
        "about": "Drone swarm (6 drones, 16x16 forest). Base: independent DQN that first learns from the nearest-fire rule.",
    },
}


def build(results: Path) -> list[str]:
    written = []
    for app, spec in TABLES.items():
        dirs = [results / "runs" / v for v in spec["variants"] if (results / "runs" / v).exists()]
        if len(dirs) < 2 or not (results / "runs" / spec["base"]).exists():
            continue
        runs = aggregate.load_runs(dirs)
        table = aggregate.compare_variants(runs, spec["base"], spec["metrics"])
        (results / f"methods-{app}.md").write_text(f"# Methods and ablations: {app}\n\n{spec['about']}\n\n{table}")
        written.append(app)
    return written


if __name__ == "__main__":
    print("tables:", ", ".join(build(Path(sys.argv[1] if len(sys.argv) > 1 else "results"))) or "none")
