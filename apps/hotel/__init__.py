"""Hotel application. The swarm environments for hotel operations come in a
later batch; for now the benchmark reports the existing schedule optimizer
(PuLP) against the fixed weekly pattern, from analytics/ outputs."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
KEY_METRICS = ["total_cost", "shortfall_hours", "requests_honoured", "rule_violations"]


def benchmark_rows(cfg: dict) -> list[dict]:
    path = HERE / cfg.get("schedule_json", "docs/data/schedule.json")
    data = json.loads(path.read_text())
    rows = []
    for s in data["scenarios"]:
        for key, label in (("optimized", "PuLP schedule"), ("manual", "fixed weekly pattern")):
            ev = s[key]["evaluation"]
            rules = s[key].get("rules", [])
            rows.append({
                "app": "hotel",
                "policy": f"{label} ({s['title']})",
                "total_cost": float(ev["total_cost"]),
                "shortfall_hours": float(ev["shortfall_hours"]),
                "requests_honoured": f"{ev['requests_honoured']}/{ev['requests_total']}",
                "rule_violations": sum(r["violations"] for r in rules),
            })
    return rows
