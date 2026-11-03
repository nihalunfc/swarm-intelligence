"""Generate the paper's LaTeX tables from the markdown tables in results/.

Every number in the paper comes from results/, so re-running an experiment and
then `make -C paper` updates the PDF. Tables are described by specs below:

- select:  some columns of one results table, one row per policy.
- compose: rows picked from several results files (one policy row each), with an
           optional "difference from a rule" column read from that file's
           "Swarm minus rule" table, so each difference is paired within its run.
- grid:    one metric's scenario or swarm-size table (robustness, scale), mean
           only, rows picked from several files.

A missing file or row prints "--" and a warning instead of failing, so the paper
still builds while an experiment is re-running.

Usage: python paper/make_tables.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
OUT = Path(__file__).resolve().parent / "tables"
SWARM = "swarm (trained)"
VS = "Swarm minus rule"
MISSING = "--"


# --------------------------------------------------------------------------- parsing

def _rows(lines: list[str]) -> list[list[str]]:
    out = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not all(re.fullmatch(r":?-+:?", c) for c in cells):
            out.append(cells)
    return out


def tables(path: Path) -> list[tuple[str, list[list[str]]]]:
    """Every pipe table in a markdown file, with the last non-table line before it."""
    found, cur, title, last = [], [], "", ""
    for line in path.read_text().splitlines() + [""]:
        if line.strip().startswith("|"):
            if not cur:
                title = last
            cur.append(line)
        else:
            if cur:
                found.append((title, _rows(cur)))
                cur = []
            if line.strip():
                last = line.strip()
    return found


def table(src: str, after: str | None = None, nth: int = 0) -> list[list[str]] | None:
    """The nth table in results/src, or the first one whose title contains `after`."""
    path = RESULTS / src
    if not path.exists():
        warn(f"missing results/{src}")
        return None
    ts = tables(path)
    if after is not None:
        ts = [t for t in ts if after in t[0]]
    if len(ts) <= nth:
        warn(f"no table {after or nth!r} in results/{src}")
        return None
    return ts[nth][1]


def cell(tab: list[list[str]] | None, row: str, col: str) -> str:
    if tab is None:
        return MISSING
    head = tab[0]
    key = "policy" if "policy" in head else head[0]
    if col not in head:
        warn(f"no column {col!r}")
        return MISSING
    for r in tab[1:]:
        if r[head.index(key)] == row:
            return r[head.index(col)]
    warn(f"no row {row!r}")
    return MISSING


def warn(msg: str) -> None:
    print(f"make_tables: warning: {msg}", file=sys.stderr)


# --------------------------------------------------------------------------- formatting

def tex_escape(s: str) -> str:
    for a, b in (("\\", "\\textbackslash{}"), ("&", "\\&"), ("%", "\\%"), ("_", "\\_"), ("#", "\\#"), ("$", "\\$")):
        s = s.replace(a, b)
    return s.replace("->", "$\\to$")


def places(x: str) -> int:
    v = abs(float(x.replace(",", "")))
    return 0 if v >= 1000 else 1 if v >= 10 else 2


def num(x: str, p: int | None = None) -> str:
    """Format a number; p = decimal places (default: from its own size)."""
    v = float(x.replace(",", ""))
    p = places(x) if p is None else p
    return f"{v:,.{p}f}".replace(",", "{,}")


NUM = r"-?[\d,]*\.?\d+"


def lead(c: str) -> float | None:
    m = re.match(rf"\s*({NUM})", c)
    return float(m.group(1).replace(",", "")) if m else None


def fmt(c: str, ci: bool = True, p: int | None = None) -> str:
    """Format a number, "mean [lo, hi]", or "diff [lo, hi], p=..." cell for LaTeX (p = decimal places)."""
    c = c.strip()
    m = re.fullmatch(rf"({NUM})\s*\[\s*({NUM})\s*,\s*({NUM})\s*\](.*)", c)
    if m:
        mean, lo, hi, rest = m.groups()
        p = places(mean) if p is None else p
        out = num(mean, p)
        if ci and lo != hi:
            out += f" {{\\scriptsize [{num(lo, p)}, {num(hi, p)}]}}"
        pv = re.search(r"p=(<?)\s*([\d.]+)", rest)
        if pv:
            out += f" {{\\scriptsize $p{'<' if pv.group(1) else '='}{pv.group(2)}$}}"
        return out
    if re.fullmatch(NUM, c):
        return num(c, p)
    return tex_escape(c)


def format_rows(rows: list[list[str]], ci: bool = True, uniform: bool = False) -> list[list[str]]:
    """rows: [LaTeX label, raw cells...] or ["---"]. Each column gets one precision from its largest
    value; uniform=True uses one precision for the whole table (columns of the same metric)."""
    width = max(len(r) for r in rows if r != ["---"]) if rows else 0
    prec = {}
    for j in range(1, width):
        vals = [abs(v) for r in rows if r != ["---"] and j < len(r) for v in [lead(r[j])] if v is not None]
        prec[j] = places(str(max(vals))) if vals else None
    if uniform and any(v is not None for v in prec.values()):
        prec = dict.fromkeys(prec, min(v for v in prec.values() if v is not None))
    return [r if r == ["---"] else [r[0]] + [fmt(c, ci, prec[j]) if c else "" for j, c in enumerate(r[1:], 1)]
            for r in rows]


def render(header: list[str], rows: list[list[str]], caption: str, label: str, wide: bool = False) -> str:
    env = "table*" if wide else "table"
    spec = "l" + "r" * (len(header) - 1)
    lines = [f"\\begin{{{env}}}[!htbp]", "\\centering", "\\small", "\\setlength{\\tabcolsep}{4pt}",
             f"\\caption{{{caption}}}", f"\\label{{{label}}}",
             f"\\begin{{tabular}}{{{spec}}}", "\\toprule", " & ".join(header) + " \\\\", "\\midrule"]
    for r in rows:
        lines.append("\\midrule" if r == ["---"] else " & ".join(r) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", f"\\end{{{env}}}", ""]
    return "\n".join(lines)


# --------------------------------------------------------------------------- table kinds

def label_of(name: str, rename: dict) -> str:
    """A policy name from a results file as a LaTeX row label (renames are written in LaTeX already)."""
    return rename[name] if name in rename else tex_escape(name[:1].upper() + name[1:])


def select(spec: dict) -> str:
    tab = table(spec["src"], spec.get("after"))
    head = [h for _, h in spec["cols"]]
    rows = []
    if tab is not None:
        cols = [c for c, _ in spec["cols"]]
        for r in tab[1:]:
            name = r[tab[0].index("policy")] if "policy" in tab[0] else r[0]
            if name not in spec.get("drop", ()):
                rows.append([label_of(name, spec.get("rename", {}))] + [cell(tab, name, c) for c in cols[1:]])
    return render(head, format_rows(rows, spec.get("ci", True)), spec["caption"], spec["label"])


def compose(spec: dict) -> str:
    """spec["rows"]: (LaTeX label, src, policy) or "---"; spec["cols"]: (metric, header);
    spec["vs"]: optional (rule, metric, header) read from each src's swarm-minus-rule table."""
    head = ["Policy"] + [h for _, h in spec["cols"]]
    if "vs" in spec:
        head.append(spec["vs"][2])
    rows = []
    for item in spec["rows"]:
        if item == "---":
            rows.append(["---"])
            continue
        label, src, policy = item
        main = table(src, nth=0)
        r = [label] + [cell(main, policy, m) for m, _ in spec["cols"]]
        if "vs" in spec:
            rule, metric, _ = spec["vs"]
            r.append(cell(table(src, after=VS), rule, metric) if policy == SWARM else "")
        rows.append(r)
    return render(head, format_rows(rows), spec["caption"], spec["label"], spec.get("wide", False))


def grid(spec: dict) -> str:
    """spec["rows"]: (LaTeX label, src, policy); spec["metric"]: bold title of the block;
    spec["cols"]: (header in file, printed header). Means only."""
    head = ["Policy"] + [h for _, h in spec["cols"]]
    rows = []
    for label, src, policy in spec["rows"]:
        tab = table(src, after=f"**{spec['metric']}**")
        rows.append([label] + [re.sub(r"\s*\(\d+%\)$", "", cell(tab, policy, c)) for c, _ in spec["cols"]])
    return render(head, format_rows(rows, ci=False, uniform=True), spec["caption"], spec["label"], spec.get("wide", False))


# --------------------------------------------------------------------------- the paper's tables

WF_ROB_COLS = [("normal", "Normal"), ("50% drones fail", "50\\% fail"), ("sensor noise 0.1", "Noise 0.1"),
               ("sensor noise 0.3", "Noise 0.3"), ("stronger wind", "Strong wind"), ("4 ignitions", "4 fires")]
SIZES = [("6 agents", "6"), ("24 agents", "24"), ("100 agents", "100"), ("1,000 agents", "1{,}000")]

SPECS = {
    "energy": (compose, dict(
        caption="Energy: 10 batteries (1\\,GW / 4\\,GWh fleet) on ERCOT COAST load, test months Oct--Dec 2020. "
                "Mean [95\\% CI] over training seeds (10 for VDN, 5 otherwise); rules and bounds are deterministic. "
                "Last column: paired difference in load-spread reduction against the proportional rule.",
        label="tab:energy", wide=True,
        cols=[("std_reduction_pct", "Spread cut (\\%)"), ("peak_reduction_mw", "Peak cut (MW)")],
        vs=("proportional rule", "std_reduction_pct", "vs proportional (pts)"),
        rows=[("Swarm, VDN (ours)", "energy.md", SWARM),
              ("Swarm, QMIX", "energy-qmix.md", SWARM),
              ("Swarm, independent learners", "energy-independent.md", SWARM),
              ("Swarm, 3-step returns", "energy-3-step.md", SWARM),
              ("Swarm, no validation selection", "energy-no-val-selection.md", SWARM),
              ("MAPPO", "energy-mappo.md", SWARM),
              "---",
              ("Proportional rule", "energy.md", "proportional rule"),
              ("MPC, 24\\,h forecast", "energy.md", "MPC (24 h forecast)"),
              ("Threshold rule", "energy.md", "threshold rule"),
              "---",
              ("Bound: flattest load (perfect foresight)", "energy.md", "optimum: flattest (perfect foresight)"),
              ("Bound: minimum peak (perfect foresight)", "energy.md", "optimum: min peak (perfect foresight)")])),
    "housekeeping": (compose, dict(
        caption="Hotel housekeeping: 8 attendants, 300 rooms, 50 generated test days, 5 seeds per method. "
                "Guest waiting in hours per day (lower is better); last column is the paired difference from the soonest-needed rule.",
        label="tab:housekeeping",
        cols=[("guest_wait_hours", "Guest wait (h/day)")],
        vs=("soonest needed", "guest_wait_hours", "vs soonest-needed"),
        rows=[("Residual swarm (ours)", "hotel-housekeeping-residual.md", SWARM),
              ("MAPPO", "hotel-housekeeping-mappo.md", SWARM),
              ("Swarm, independent learners", "hotel-housekeeping-independent.md", SWARM),
              ("Swarm, QMIX", "hotel-housekeeping-qmix.md", SWARM),
              ("Swarm, VDN", "hotel-housekeeping.md", SWARM),
              "---",
              ("Soonest-needed rule", "hotel-housekeeping.md", "soonest needed"),
              ("Random room", "hotel-housekeeping.md", "random room"),
              ("Floor order (today's practice)", "hotel-housekeeping.md", "floor order"),
              "---",
              ("Lower bound (perfect foresight)", "hotel-housekeeping.md",
               "lower bound (perfect foresight, no elevator time)")])),
    "wildfire": (compose, dict(
        caption="Wildfire: 6 drones, $16\\times16$ forest, 50 unseen fires. Seeds: 5 for imitation then RL, 3 otherwise. "
                "Last column: paired difference in forest saved from the nearest-fire rule in the same run. "
                "The target-choice rows use a different action space (drones pick which fire to fight), "
                "whose nearest-fire rule saves 88.9\\%.",
        label="tab:wildfire", wide=True,
        cols=[("forest_saved_pct", "Forest saved (\\%)"), ("peak_fire_cells", "Peak burning cells")],
        vs=("nearest-fire rule", "forest_saved_pct", "vs nearest-fire (pts)"),
        rows=[("Residual swarm (ours)", "wildfire-residual.md", SWARM),
              ("Imitation, then RL", "wildfire-imitate.md", SWARM),
              ("Imitation, then RL, QMIX", "wildfire-imitate-qmix.md", SWARM),
              ("Imitation, then RL, multi-pad", "wildfire-imitate-pads.md", SWARM),
              ("Imitation, then RL, neighbour messages", "wildfire-imitate-messages.md", SWARM),
              ("RL from scratch", "wildfire.md", SWARM),
              ("MAPPO", "wildfire-mappo.md", SWARM),
              ("Target choice: swarm", "wildfire-targets.md", SWARM),
              "---",
              ("Target choice: spread rule", "wildfire-targets.md", "spread rule"),
              ("Nearest-fire rule", "wildfire-imitate.md", "nearest-fire rule"),
              ("Random", "wildfire-imitate.md", "random"),
              ("No drones", "wildfire-imitate.md", "no drones")])),
    "hotel-energy": (select, dict(
        src="hotel-energy.md",
        caption="Hotel peak-hour energy (HARLTON-01): 16 equipment agents, summer test weeks, 5 seeds. "
                "Net saving per year under the global-adjustment tariff assumptions in the config.",
        label="tab:hotel-energy",
        cols=[("policy", "Policy"), ("net_saving_usd", "Net saving (\\$/yr)"), ("peak_cut_kw", "Peak cut (kW)")],
        rename={SWARM: "Swarm (VDN)"})),
    "shifts": (select, dict(
        src="hotel-shifts.md",
        caption="Hotel shift exchange across five properties under Ontario ESA limits (contract-net market, "
                "deterministic). Cost per week of open shifts.",
        label="tab:shifts",
        cols=[("policy", "Policy"), ("total_cost", "Cost (\\$/wk)"), ("fill_rate_pct", "Filled (\\%)"),
              ("agency_hours", "Agency (h)")],
        rename={"swarm market": "Contract-net market", "optimal plan (reference)": "Optimum (MILP)"})),
    "relocation": (select, dict(
        src="hotel-relocation.md",
        caption="Hotel guest relocation on oversold nights (auction, deterministic). Net value per night.",
        label="tab:relocation",
        cols=[("policy", "Policy"), ("net_value", "Net (\\$/night)"), ("kept_in_group_pct", "Kept in group (\\%)")],
        rename={"swarm auction": "Relocation auction", "optimal plan (reference)": "Optimum (MILP)"})),
    "citylearn": (select, dict(
        src="citylearn.md",
        caption="CityLearn Challenge 2022 (17 homes, Oct--Dec test), 3 seeds. Scores are normalised so that "
                "no battery control is 1.0; lower is better.",
        label="tab:citylearn",
        cols=[("policy", "Policy"), ("score", "Score"), ("cost_total", "Cost"), ("daily_peak_average", "Daily peak")],
        rename={SWARM: "Swarm (VDN)"})),
    "vmas": (compose, dict(
        caption="VMAS navigation, 4 robots, 50 test episodes, 3 seeds.",
        label="tab:vmas",
        cols=[("success", "Goals reached"), ("collisions", "Collisions")],
        rows=[("Swarm (VDN DQN)", "vmas-navigation.md", SWARM),
              ("MAPPO", "vmas-navigation-mappo.md", SWARM),
              ("Go-to-goal rule", "vmas-navigation.md", "go to goal"),
              ("Random", "vmas-navigation.md", "random")])),
    "robust-energy": (grid, dict(
        caption="Energy robustness: load-spread reduction (\\%) when batteries fail mid-period or observations are noisy. "
                "No policy is retrained.",
        label="tab:robust-energy", metric="std_reduction_pct",
        cols=[("normal", "Normal"), ("10% batteries fail", "10\\% fail"), ("30% batteries fail", "30\\% fail"),
              ("50% batteries fail", "50\\% fail"), ("sensor noise 0.3", "Noise 0.3")],
        rows=[("Swarm (VDN)", "robustness-energy.md", SWARM),
              ("Proportional rule", "robustness-energy.md", "proportional rule"),
              ("MPC, 24\\,h forecast", "robustness-energy.md", "MPC (24 h forecast)"),
              ("Threshold rule", "robustness-energy.md", "threshold rule")])),
    "robust-housekeeping": (grid, dict(
        caption="Housekeeping robustness: guest waiting (h/day) when attendants leave at 11:00 and on unseen busier days.",
        label="tab:robust-housekeeping", metric="guest_wait_hours",
        cols=[("normal", "Normal"), ("2 of 8 leave", "2 leave"), ("4 of 8 leave", "4 leave"),
              ("busier day (45% check-outs)", "Busier day"), ("more early check-ins (30%)", "More early")],
        rows=[("Swarm (VDN)", "robustness-hotel-housekeeping.md", SWARM),
              ("Soonest-needed rule", "robustness-hotel-housekeeping.md", "soonest needed"),
              ("Floor order", "robustness-hotel-housekeeping.md", "floor order")])),
    "robust-wildfire": (grid, dict(
        caption="Wildfire robustness: forest saved (\\%) when drones fail, under Gaussian observation noise, and on "
                "unseen conditions. Noise is added to the agents' observations; the nearest-fire rule reads the true state.",
        label="tab:robust-wildfire", metric="forest_saved_pct", wide=True,
        cols=WF_ROB_COLS,
        rows=[("Residual swarm", "robustness-wildfire-residual.md", SWARM),
              ("Imitation, then RL", "robustness-wildfire-imitate.md", SWARM),
              ("RL from scratch", "robustness-wildfire.md", SWARM),
              ("MAPPO", "robustness-wildfire-mappo.md", SWARM),
              ("Nearest-fire rule", "robustness-wildfire-imitate.md", "nearest-fire rule"),
              ("Target choice: spread rule", "robustness-wildfire-targets.md", "spread rule")])),
    "scale-wildfire": (grid, dict(
        caption="Wildfire scale: forest saved (\\%) with launch pads tiling the forest. Each model runs unchanged at "
                "every size; mean over 3 training seeds.",
        label="tab:scale-wildfire", metric="forest_saved_pct",
        cols=SIZES,
        rows=[("Nearest-fire rule", "scale-wildfire-imitate-pads.md", "nearest-fire rule"),
              ("Swarm trained with 6 drones", "scale-wildfire-imitate-pads.md", SWARM),
              ("Swarm, 6$\\to$24 curriculum", "scale-wildfire-scale.md", SWARM),
              ("Random", "scale-wildfire-imitate-pads.md", "random"),
              ("No drones", "scale-wildfire-imitate-pads.md", "no drones")])),
    "compute": (select, dict(
        src="scale-wildfire-scale.md", after="**Compute**",
        caption="Compute per swarm size on one CPU core (wildfire). The network has 109{,}574 parameters at every size.",
        label="tab:compute",
        cols=[("agents", "Drones"), ("choose all actions (ms)", "Act (ms)"), ("env step (ms)", "Env step (ms)"),
              ("update, batch 32 (ms)", "Update (ms)")])),
}


def scale_data() -> str:
    """Forest saved by swarm size, as a pgfplots table (figures/scale.dat). NaN marks a missing value."""
    series = [("rule", "scale-wildfire-imitate-pads.md", "nearest-fire rule"),
              ("swarm", "scale-wildfire-imitate-pads.md", SWARM),
              ("curriculum", "scale-wildfire-scale.md", SWARM)]
    lines = ["n " + " ".join(f"{k} {k}_lo {k}_hi" for k, _, _ in series)]
    tabs = {src: table(src, after="**forest_saved_pct**") for _, src, _ in series}
    for col, _ in SIZES:
        vals = []
        for _, src, policy in series:
            m = re.fullmatch(rf"({NUM})\s*\[\s*({NUM})\s*,\s*({NUM})\s*\]", cell(tabs[src], policy, col))
            vals += [g.replace(",", "") for g in m.groups()] if m else ["nan"] * 3
        lines.append(col.split()[0].replace(",", "") + " " + " ".join(vals))
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (kind, spec) in SPECS.items():
        (OUT / f"{name}.tex").write_text(kind(spec))
    (OUT.parent / "figures").mkdir(exist_ok=True)
    (OUT.parent / "figures" / "scale.dat").write_text(scale_data())
    print(f"wrote {len(SPECS)} tables to {OUT.relative_to(ROOT)} and figures/scale.dat")


if __name__ == "__main__":
    main()
