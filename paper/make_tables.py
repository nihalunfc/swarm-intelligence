"""Generate the paper's LaTeX tables from the markdown tables in results/.

Every number in the paper comes from results/, so re-running an experiment and
then `make -C paper` updates the PDF. Each entry in TABLES names a results file,
the columns to keep (with their printed headers) and the output file in
paper/tables/. Missing results files produce a placeholder table instead of an
error, so the paper builds while experiments are still running.

Usage: python paper/make_tables.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
OUT = Path(__file__).resolve().parent / "tables"

# (output name, results file, [(column, header)], caption, label)
TABLES = [
    ("energy", "energy.md",
     [("policy", "Policy"), ("peak_reduction_mw", "Peak cut (MW)"),
      ("std_reduction_pct", "Load std cut (\\%)"), ("par_after", "PAR after")],
     "Energy: 10 batteries (1\\,GW / 4\\,GWh fleet) on ERCOT COAST load, held-out months.",
     "tab:energy"),
    ("wildfire", "wildfire.md",
     [("policy", "Policy"), ("forest_saved_pct", "Forest saved (\\%)"),
      ("burned_cells", "Burned cells"), ("peak_fire_cells", "Peak burning")],
     "Wildfire: 6 drones, $16\\times16$ forest, 50 unseen fires.",
     "tab:wildfire"),
    ("wildfire-imitate", "wildfire-imitate.md",
     [("policy", "Policy"), ("forest_saved_pct", "Forest saved (\\%)"),
      ("burned_cells", "Burned cells"), ("peak_fire_cells", "Peak burning")],
     "Wildfire with rule pre-training (imitation, then RL).",
     "tab:wildfire-imitate"),
    ("housekeeping", "hotel-housekeeping.md",
     [("policy", "Policy"), ("guest_wait_hours", "Guest wait (h/day)"),
      ("early_promises_kept_pct", "Early check-ins kept (\\%)"), ("workload_spread", "Workload spread")],
     "Hotel housekeeping: 8 attendants, 300 rooms, 50 generated days.",
     "tab:housekeeping"),
    ("shifts", "hotel-shifts.md",
     [("policy", "Policy"), ("total_cost", "Cost (\\$/week)"),
      ("fill_rate_pct", "Fill rate (\\%)"), ("agency_hours", "Agency hours")],
     "Hotel shift exchange across five properties (Ontario ESA rules).",
     "tab:shifts"),
    ("relocation", "hotel-relocation.md",
     [("policy", "Policy"), ("net_value", "Net value (\\$/night)"),
      ("kept_in_group_pct", "Kept in group (\\%)"), ("mean_transfer_km", "Transfer (km)")],
     "Hotel guest relocation on oversold nights.",
     "tab:relocation"),
]

# Scale tables are pivoted by swarm size; their first table is copied as is.
SCALE = [
    ("scale-energy", "scale-energy.md", "Energy peak cut (MW) by swarm size; model trained with 10 agents.", "tab:scale-energy"),
    ("scale-wildfire", "scale-wildfire.md", "Wildfire forest saved (\\%) by swarm size; model trained with 6 agents.", "tab:scale-wildfire"),
]


def parse_tables(text: str) -> list[list[list[str]]]:
    """Return every markdown pipe table in text as a list of rows of cells."""
    tables, cur = [], []
    for line in text.splitlines():
        if line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-+:?", c) for c in cells):
                continue
            cur.append(cells)
        elif cur:
            tables.append(cur)
            cur = []
    if cur:
        tables.append(cur)
    return tables


def tex_escape(s: str) -> str:
    return s.replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")


def fmt(cell: str) -> str:
    """Format a number, or a multi-seed "mean [lo, hi]" cell, for LaTeX."""
    m = re.fullmatch(r"\s*(-?[\d,.]+)\s*\[\s*(-?[\d,.]+)\s*,\s*(-?[\d,.]+)\s*\](.*)", cell)
    if m:
        mean, lo, hi, rest = m.groups()
        return f"{fmt(mean)} {{\\scriptsize [{fmt(lo)}, {fmt(hi)}]}}" + tex_escape(rest)
    try:
        v = float(cell.replace(",", ""))
    except ValueError:
        return tex_escape(cell)
    if abs(v) >= 1000:
        return f"{v:,.0f}".replace(",", "{,}")
    return f"{v:.1f}" if abs(v) >= 10 else f"{v:.2f}" if abs(v) >= 0.1 or v == 0 else f"{v:.3f}"


def render(header: list[str], rows: list[list[str]], caption: str, label: str) -> str:
    spec = "l" + "r" * (len(header) - 1)
    lines = [
        "\\begin{table}[t]", "\\centering", "\\small",
        f"\\caption{{{caption}}}", f"\\label{{{label}}}",
        f"\\begin{{tabular}}{{{spec}}}", "\\toprule",
        " & ".join(header) + " \\\\", "\\midrule",
    ]
    lines += [" & ".join(r) + " \\\\" for r in rows]
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    return "\n".join(lines)


def placeholder(caption: str, label: str, src: str) -> str:
    return render(["Status"], [[f"pending: results/{tex_escape(src)} not found"]], caption, label)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, src, cols, caption, label in TABLES:
        path = RESULTS / src
        if not path.exists():
            (OUT / f"{name}.tex").write_text(placeholder(caption, label, src))
            continue
        table = parse_tables(path.read_text())[0]
        head, body = table[0], table[1:]
        idx = [head.index(c) for c, _ in cols]
        rows = [[fmt(r[i]) if j else tex_escape(r[i]) for j, i in enumerate(idx)] for r in body]
        (OUT / f"{name}.tex").write_text(render([h for _, h in cols], rows, caption, label))
    for name, src, caption, label in SCALE:
        path = RESULTS / src
        if not path.exists():
            (OUT / f"{name}.tex").write_text(placeholder(caption, label, src))
            continue
        table = parse_tables(path.read_text())[0]
        header = [tex_escape(h) for h in table[0]]
        header[0] = "Policy"
        rows = [[tex_escape(r[0])] + [fmt(c) for c in r[1:]] for r in table[1:]]
        (OUT / f"{name}.tex").write_text(render(header, rows, caption, label))
    print(f"wrote {len(TABLES) + len(SCALE)} tables to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
