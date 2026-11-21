"""LLM agent crew on the shared board (groundwork, phase 4 of the swarm + LLM plan).

The crew watches swarm results, flags where the learned swarm is behind the
simple rule, and proposes **dev-only** config changes. A person merges. The
pieces, in the order a task moves through them:

1. :func:`watch` (plain Python, no LLM) reads ``results/*.json`` and posts one
   ``gap`` task per app and metric where the swarm's 95% interval is entirely
   on the wrong side of the best rule. Ties are not flagged.
2. :class:`Router` (plain Python) picks who works on each task:
   * ``gap`` tasks go to **triage** (Haiku): is this worth a fix, and why?
   * ``fix`` tasks go to the **fixer** (Sonnet): propose config overrides.
   * Once per crew run, the **reviewer** (Opus) writes one summary of the board.
3. :func:`check_proposal` validates fixer output: only training and agent
   hyperparameters (``train.*``, ``agent.*``) may change. Data paths, splits
   and evaluation settings are off limits, so nobody can "win" by moving the
   test set. Proposals are written to the board's ``proposals/`` folder, never
   to ``configs/``.
4. :func:`gate` is the rule-first test: after someone trains the proposal, the
   override is kept only if the new swarm beats the best rule on the held-out
   test split (interval clear of the rule). Otherwise the task is closed as
   ``rejected`` and the rule stays.

LLM calls are optional. Without the ``anthropic`` package or credentials the
crew uses :class:`OfflineClient`, which writes rule-based notes, so the whole
loop runs (and is tested) with no API key and no cost.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from .board import Board

log = logging.getLogger("swarm.crew")

SWARM = "swarm (trained)"
# Policies that are not rules a deployment could use instead of the swarm.
NOT_RULES = re.compile(r"^(no[ -]|random|optimum|lower bound|upper bound)|perfect foresight", re.I)
# Metrics where smaller is better. Anything else is treated as higher-is-better.
LOWER_IS_BETTER = {
    "par_after", "burned_cells", "peak_fire_cells", "score", "cost_total", "carbon_emissions_total",
    "ramping_average", "daily_peak_average", "one_minus_load_factor", "guest_wait_hours", "total_cost",
    "shortfall_hours", "rule_violations", "workload_spread", "floor_changes", "agency_hours", "overtime_hours",
    "missed_kwh", "extra_energy_usd", "collisions", "mean_transfer_km", "max_extra_shifts", "peaks_hit",
}
SKIP_METRICS = {"return"}  # training reward: scale differs per app, not a deployment metric
ALLOWED_PREFIXES = ("train.", "agent.")

MODELS = {"triage": "claude-haiku-5-5", "fix": "claude-sonnet-5-5", "review": "claude-opus-5-5"}
# USD per million tokens (input, output), first-party API list prices, Nov 2026. Used only to print an estimate.
PRICES = {"claude-haiku-5-5": (0.10, 0.50), "claude-sonnet-5-5": (2.00, 10.00), "claude-opus-5-5": (4.00, 20.00)}
# Apps that are paused (hotel work is on hold): the watcher leaves them alone unless asked.
PAUSED = ("hotel",)


# --------------------------------------------------------------------- watcher
@dataclass
class Gap:
    run: str
    app: str
    metric: str
    rule: str
    swarm: tuple[float, float, float]
    rule_score: tuple[float, float, float]
    lower_is_better: bool

    @property
    def gap_pct(self) -> float:
        """How far the swarm's mean is behind the rule, in % of the rule (positive = behind)."""
        base = abs(self.rule_score[0]) or 1.0
        diff = self.swarm[0] - self.rule_score[0]
        return round(100 * (diff if self.lower_is_better else -diff) / base, 2)

    def key(self) -> str:
        return f"gap:{self.run}:{self.metric}"


def _triple(v) -> tuple[float, float, float]:
    if isinstance(v, (int, float)):
        return float(v), float(v), float(v)
    return float(v[0]), float(v[1]), float(v[2])


def find_gaps(results: dict, run: str) -> list[Gap]:
    """Metrics where the swarm is clearly behind the best rule in one results file."""
    gaps = []
    for app, block in results.items():
        if not isinstance(block, dict) or SWARM not in block.get("policies", {}):
            continue
        pol = block["policies"]
        rules = [p for p in pol if p != SWARM and not NOT_RULES.search(p)]
        for metric in block.get("metrics", []):
            if metric in SKIP_METRICS or metric not in pol[SWARM]:
                continue
            low = metric in LOWER_IS_BETTER
            scored = [(p, _triple(pol[p][metric])) for p in rules if metric in pol[p]]
            if not scored:
                continue
            best, best_s = (min if low else max)(scored, key=lambda x: x[1][0])
            sw = _triple(pol[SWARM][metric])
            behind = sw[1] > best_s[0] if low else sw[2] < best_s[0]
            if behind:
                gaps.append(Gap(run, block.get("app", app), metric, best, sw, best_s, low))
    return gaps


def _gap_data(g: Gap) -> dict:
    return {"metric": g.metric, "rule": g.rule, "swarm": list(g.swarm), "rule_score": list(g.rule_score),
            "lower_is_better": g.lower_is_better, "gap_pct": g.gap_pct}


def watch(board: Board, results_dir: str | Path, actor: str = "watcher", skip: tuple[str, ...] = PAUSED) -> list[dict]:
    """Post one ``gap`` task per results file where the swarm is behind a rule.

    All metrics behind in one run go into one task (``data["metrics"]``), so the fixer
    proposes one change per config instead of one per metric. The headline metric (the
    first one the results file lists) is the task's ``metric``. Runs whose file name or
    app starts with a ``skip`` prefix (paused work) are left alone."""
    posted = []
    for path in sorted(Path(results_dir).glob("*.json")):
        if path.stem.startswith(skip):
            continue
        try:
            results = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        gaps = [g for g in find_gaps(results, path.stem) if not g.app.startswith(skip)]
        if not gaps:
            continue
        head = gaps[0]
        key = f"gap:{head.run}"
        if board.find(key):
            continue
        direction = "lower" if head.lower_is_better else "higher"
        more = f" (+{len(gaps) - 1} more metric{'s' if len(gaps) > 2 else ''})" if len(gaps) > 1 else ""
        task = board.post(
            actor, f"{head.run}: swarm behind {head.rule} on {head.metric} ({head.gap_pct:.1f}% behind){more}",
            kind="gap",
            body="; ".join(f"{g.metric}: swarm {g.swarm[0]:.4g} [{g.swarm[1]:.4g}, {g.swarm[2]:.4g}] vs {g.rule} "
                           f"{g.rule_score[0]:.4g} ({'lower' if g.lower_is_better else 'higher'} is better)"
                           for g in gaps) if len(gaps) > 1 else
                 f"swarm {head.swarm[0]:.4g} [{head.swarm[1]:.4g}, {head.swarm[2]:.4g}] vs {head.rule} "
                 f"{head.rule_score[0]:.4g} ({direction} is better)",
            data={"run": head.run, "app": head.app, **_gap_data(head), "results": str(path),
                  "metrics": [_gap_data(g) for g in gaps]},
            key=key, priority=int(min(max(abs(g.gap_pct) for g in gaps), 100)))
        posted.append(task)
    return posted


# ------------------------------------------------------------------ LLM clients
class OfflineClient:
    """No-LLM stand-in: deterministic, rule-based answers. Used when there is no API access."""

    name = "offline"

    def complete(self, role: str, system: str, prompt: str) -> str:
        data = json.loads(prompt)
        if role == "triage":
            gap = data["task"]["data"].get("gap_pct", 0)
            return json.dumps({"decision": "fix" if abs(gap) >= 2 else "watch",
                               "reason": f"offline rule: gap {gap:+.1f}% {'>=' if abs(gap) >= 2 else '<'} 2%"})
        if role == "fix":
            return json.dumps({"overrides": {"train.total_steps": 2 * int(data.get("config", {}).get("train", {})
                                                                         .get("total_steps", 50000))},
                               "reason": "offline rule: train twice as long before changing anything else"})
        return f"Offline summary: {len(data.get('tasks', []))} task(s) on the board."


class AnthropicClient:
    """Calls Claude through the official SDK. Imported lazily so the package stays optional."""

    name = "anthropic"

    def __init__(self, models: dict | None = None, client=None):
        if client is None:
            import anthropic

            client = anthropic.Anthropic()
        self.client = client
        self.models = {**MODELS, **(models or {})}
        self.usage: dict[str, dict] = {}  # model -> {"calls", "input_tokens", "output_tokens"}

    def complete(self, role: str, system: str, prompt: str) -> str:
        model = self.models[role]
        kwargs = dict(model=model, max_tokens=4000 if role != "review" else 16000, system=system,
                      messages=[{"role": "user", "content": prompt}],
                      output_config={"effort": "low" if role == "triage" else "medium"})
        if role == "triage":
            resp = self.client.messages.create(**kwargs)
        else:  # Sonnet and Opus: let the API retry on a declined request with a fallback model
            resp = self.client.beta.messages.create(betas=["server-side-fallback-2026-07-01"], fallbacks="default",
                                                    **kwargs)
        self._count(getattr(resp, "model", None) or model, getattr(resp, "usage", None))
        if resp.stop_reason == "refusal":
            raise RuntimeError(f"{model} declined the request")
        return "".join(b.text for b in resp.content if b.type == "text")


    def _count(self, model: str, usage):
        u = self.usage.setdefault(model, {"calls": 0, "input_tokens": 0, "output_tokens": 0})
        u["calls"] += 1
        if usage is not None:
            u["input_tokens"] += int(getattr(usage, "input_tokens", 0) or 0)
            u["output_tokens"] += int(getattr(usage, "output_tokens", 0) or 0)

    def cost(self) -> float:
        """Estimated USD for the calls so far (list prices; unknown models count as Opus)."""
        total = 0.0
        for model, u in self.usage.items():
            pin, pout = PRICES.get(model, PRICES["claude-opus-5-5"])
            total += (u["input_tokens"] * pin + u["output_tokens"] * pout) / 1e6
        return round(total, 4)


def default_client():
    """Claude only when ``SWARM_LLM=1`` is set (opt-in, so nothing is billed by accident)
    and the SDK can start; otherwise the offline stand-in."""
    if os.environ.get("SWARM_LLM") != "1":
        return OfflineClient()
    try:
        return AnthropicClient()
    except Exception as e:  # missing package or credentials
        log.warning("LLM calls off (%s); using offline client", e)
        return OfflineClient()


# ------------------------------------------------------------------- proposals
def check_proposal(overrides: dict) -> dict:
    """Keep only dev-only keys with plain scalar values; raise if nothing is left."""
    if not isinstance(overrides, dict):
        raise ValueError("overrides must be a mapping")
    clean, dropped = {}, []
    for k, v in overrides.items():
        ok_key = isinstance(k, str) and k.startswith(ALLOWED_PREFIXES) and re.fullmatch(r"[a-z0-9_.]+", k)
        ok_val = isinstance(v, (int, float, str, bool)) or (isinstance(v, list) and all(
            isinstance(x, (int, float)) for x in v))
        if ok_key and ok_val:
            clean[k] = v
        else:
            dropped.append(k)
    if dropped:
        log.warning("dropped non dev-only overrides: %s", dropped)
    if not clean:
        raise ValueError(f"no allowed overrides (only {', '.join(ALLOWED_PREFIXES)} keys)")
    return clean


def _parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON object in reply")
    return json.loads(m.group(0))


# ---------------------------------------------------------------------- router
SYSTEM = {
    "triage": "You triage swarm-vs-rule gaps for a multi-agent RL project. Reply with JSON only: "
              '{"decision": "fix" | "watch" | "wontfix", "reason": "<one sentence>"}. Choose fix only when the gap '
              "is large enough that tuning training could plausibly close it.",
    "fix": "You propose config overrides to help a learned swarm catch up with a simple rule. Only keys under "
           "train.* or agent.* may change; data, splits and evaluation are fixed. Reply with JSON only: "
           '{"overrides": {"train.total_steps": 120000, ...}, "reason": "<one or two sentences>"}.',
    "review": "You review a task board for a swarm research project and write a short plain-English summary for "
              "the owner: what is behind the rule, what was proposed, and what to try next. Under 200 words.",
}


class Router:
    """Python routing: triage gaps, fix approved gaps, review once per run."""

    def __init__(self, board: Board, client=None, repo: str | Path | None = None, max_tasks: int = 20):
        self.board = board
        self.client = client or default_client()
        self.repo = Path(repo) if repo else Path(__file__).resolve().parents[2]
        self.max_tasks = max_tasks
        self.reviewed = False

    def route(self, task: dict) -> str | None:
        if task["state"] == "closed":
            return None
        if task["kind"] == "gap":
            return "triage"
        if task["kind"] == "fix" and not task["data"].get("proposal"):
            return "fix"
        return None

    def run(self) -> dict:
        """One pass over the open tasks, then one review. Returns counts per role."""
        counts = {"triage": 0, "fix": 0, "review": 0, "errors": 0}
        for wanted in ("triage", "fix"):  # fixes posted by triage are picked up in the same run
            todo = [t for t in self.board.tasks(state="open") if self.route(t) == wanted]
            for task in sorted(todo, key=lambda t: -t["priority"])[: self.max_tasks]:
                self._do(wanted, task, counts)
        if not self.reviewed:
            self._review()
            counts["review"] = 1
        return counts

    def _do(self, role: str, task: dict, counts: dict):
        try:
            getattr(self, f"_{role}")(task)
            counts[role] += 1
        except Exception as e:  # one bad reply must not stop the run; the task goes back to open
            counts["errors"] += 1
            log.warning("%s failed on %s: %s", role, task["id"], e)
            now = self.board.get(task["id"])
            if now["state"] == "claimed":
                self.board.release(task["id"], now["owner"], reason=str(e))

    def _ask(self, role: str, payload: dict) -> str:
        return self.client.complete(role, SYSTEM[role], json.dumps(payload, default=str))

    def _triage(self, task: dict):
        self.board.claim(task["id"], "triage")
        reply = _parse_json(self._ask("triage", {"task": task}))
        decision = reply.get("decision", "watch")
        self.board.add_evidence(task["id"], "triage", reply.get("reason", ""),
                                {"decision": decision, "client": self.client.name})
        if decision == "fix":
            self.board.post("triage", f"Fix: {task['title']}", kind="fix", data={**task["data"], "gap_task": task["id"]},
                            key=f"fix:{task['data'].get('run', task['key'])}", priority=task["priority"])
            self.board.close(task["id"], "triage", "done", "sent to fixer")
        elif decision == "wontfix":
            self.board.close(task["id"], "triage", "wontfix", reply.get("reason", ""))
        else:
            self.board.release(task["id"], "triage", reason="watch")
            self.board.update(task["id"], "triage", kind="watch")

    def _config_for(self, task: dict) -> tuple[dict, str | None]:
        path = self.repo / "configs" / f"{task['data'].get('run', '')}.yaml"
        if not path.exists():
            path = self.repo / "configs" / f"{task['data'].get('app', '')}.yaml"
        return (yaml.safe_load(path.read_text()) or {}, str(path.relative_to(self.repo))) if path.exists() else ({}, None)

    def _fix(self, task: dict):
        self.board.claim(task["id"], "fixer")
        cfg, cfg_path = self._config_for(task)
        reply = _parse_json(self._ask("fix", {"task": task, "config": cfg, "config_path": cfg_path}))
        overrides = check_proposal(reply.get("overrides", {}))
        content = yaml.safe_dump({"base_config": cfg_path, "overrides": overrides, "reason": reply.get("reason", ""),
                                  "status": "dev-only, needs held-out test and owner merge"}, sort_keys=False)
        path = self.board.write_proposal(task["id"], "fixer", "overrides.yaml", content)
        cmd = f"swarm train --config {cfg_path} --set " + " ".join(f"{k}={v}" for k, v in overrides.items())
        self.board.update(task["id"], "fixer", data={"proposal": str(path.relative_to(self.board.root)),
                                                    "overrides": overrides, "try": cmd})
        self.board.release(task["id"], "fixer", reason="proposal ready; waiting for a held-out run")

    def _review(self):
        tasks = [{k: t[k] for k in ("id", "kind", "title", "state", "resolution", "data")} for t in self.board.tasks()]
        text = self._ask("review", {"tasks": tasks[-50:]})
        task = self.board.post("reviewer", "Crew review", kind="review", body=text)
        self.board.close(task["id"], "reviewer", "done")
        self.reviewed = True


# ------------------------------------------------------------------------ gate
def gate(board: Board, task_id: str, results_path: str | Path, actor: str = "gate") -> bool:
    """Rule first: keep a proposal only if the retrained swarm clearly beats the best rule
    on the held-out split in ``results_path``. Closes the task either way."""
    task = board.get(task_id)
    checks = task["data"].get("metrics") or [{"metric": task["data"]["metric"], "rule": task["data"]["rule"]}]
    results = json.loads(Path(results_path).read_text())
    block = next(b for b in results.values() if isinstance(b, dict) and SWARM in b.get("policies", {}))
    if block.get("split", "test") != "test":
        raise ValueError("gate needs results on the held-out test split")
    lines, wins = [], True
    for c in checks:  # every flagged metric must clear its rule; one loss and the rule stays
        metric, rule = c["metric"], c["rule"]
        sw = _triple(block["policies"][SWARM][metric])
        rs = _triple(block["policies"][rule][metric])
        low = metric in LOWER_IS_BETTER
        ok = sw[2] < rs[0] if low else sw[1] > rs[0]
        wins = wins and ok
        lines.append(f"{metric}: swarm {sw[0]:.4g} [{sw[1]:.4g}, {sw[2]:.4g}] vs {rule} {rs[0]:.4g} "
                     f"({'clears' if ok else 'does not clear'} the rule)")
    board.add_evidence(task_id, actor, "held-out " + "; ".join(lines), {"wins": wins, "results": str(results_path)})
    board.close(task_id, actor, "done" if wins else "rejected",
                "beats the rule on held-out test; ready for owner review" if wins else "does not beat the rule; rule stays")
    return wins
