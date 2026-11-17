"""Shared task board for swarm agents and LLM helpers.

Any agent (a swarm watcher, an LLM triage agent, a person) can **post** a task,
**claim** it, attach **evidence** and **close** it. The board is a plain folder,
so it can live in a run directory or in its own git repository:

    board/
      tasks/<task-id>.json      current state of each task
      originals/<sha256>.json   every earlier version of every task (never deleted)
      ledger.jsonl              one line per step, hash-chained
      proposals/                dev-only config overrides written by agents

Every step appends one ledger line ``{seq, ts, actor, action, task, data,
before, after, prev, hash}``. ``before``/``after`` are content hashes of the
task file, and the old version is copied to ``originals/`` first, so any
earlier state can be restored with :meth:`Board.restore`. ``prev`` links each
line to the one before it, and :meth:`Board.verify` re-checks the whole chain,
so a hand-edited or truncated ledger is caught.

With ``commit=True`` and the board inside a git work tree, each step is also
committed (``git add`` of the board folder only, then ``git commit``), giving
a second, independent history. Nothing here pushes or touches other files.
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
import time
import uuid
from pathlib import Path

log = logging.getLogger("swarm.board")

STATES = ("open", "claimed", "closed")
RESOLUTIONS = ("done", "rejected", "duplicate", "wontfix")


class BoardError(RuntimeError):
    """An invalid step, for example claiming a task someone else holds."""


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _sha(obj) -> str:
    return hashlib.sha256(_canon(obj)).hexdigest()


class Board:
    def __init__(self, root: str | Path, commit: bool = False, clock=time.time):
        self.root = Path(root)
        self.commit = commit
        self.clock = clock
        for d in ("tasks", "originals", "proposals"):
            (self.root / d).mkdir(parents=True, exist_ok=True)
        self.ledger_path = self.root / "ledger.jsonl"
        self.ledger_path.touch(exist_ok=True)

    # ------------------------------------------------------------------ reads
    def get(self, task_id: str) -> dict:
        path = self._task_path(task_id)
        if not path.exists():
            raise BoardError(f"no task {task_id}")
        return json.loads(path.read_text())

    def tasks(self, state: str | None = None, kind: str | None = None) -> list[dict]:
        out = [json.loads(p.read_text()) for p in sorted((self.root / "tasks").glob("*.json"))]
        out = [t for t in out if (state is None or t["state"] == state) and (kind is None or t["kind"] == kind)]
        return sorted(out, key=lambda t: t["created"])

    def ledger(self) -> list[dict]:
        return [json.loads(line) for line in self.ledger_path.read_text().splitlines() if line.strip()]

    def find(self, key: str) -> dict | None:
        """The task posted with this de-duplication key, if any (any state)."""
        for t in self.tasks():
            if t.get("key") == key:
                return t
        return None

    # ----------------------------------------------------------------- steps
    def post(self, actor: str, title: str, kind: str = "task", body: str = "", data: dict | None = None,
             key: str | None = None, priority: int = 0) -> dict:
        """Create an open task. With ``key``, an existing open or claimed task with the
        same key is returned instead of posting a duplicate."""
        if key:
            old = self.find(key)
            if old and old["state"] != "closed":
                return old
        now = self.clock()
        task = {
            "id": f"{time.strftime('%Y%m%d', time.gmtime(now))}-{uuid.uuid4().hex[:8]}",
            "kind": kind, "title": title, "body": body, "data": data or {}, "key": key,
            "priority": int(priority), "state": "open", "owner": None, "resolution": None,
            "evidence": [], "created": now, "updated": now, "posted_by": actor,
        }
        self._write(actor, "post", None, task, {"title": title, "kind": kind})
        return task

    def claim(self, task_id: str, actor: str) -> dict:
        task = self.get(task_id)
        if task["state"] == "closed":
            raise BoardError(f"{task_id} is closed")
        if task["state"] == "claimed" and task["owner"] != actor:
            raise BoardError(f"{task_id} is held by {task['owner']}")
        new = {**task, "state": "claimed", "owner": actor, "updated": self.clock()}
        self._write(actor, "claim", task, new, {})
        return new

    def release(self, task_id: str, actor: str, reason: str = "") -> dict:
        task = self.get(task_id)
        if task["owner"] != actor or task["state"] != "claimed":
            raise BoardError(f"{actor} does not hold {task_id}")
        new = {**task, "state": "open", "owner": None, "updated": self.clock()}
        self._write(actor, "release", task, new, {"reason": reason})
        return new

    def add_evidence(self, task_id: str, actor: str, summary: str, data: dict | None = None,
                     files: list[str] | None = None) -> dict:
        task = self.get(task_id)
        if task["state"] == "closed":
            raise BoardError(f"{task_id} is closed")
        item = {"by": actor, "at": self.clock(), "summary": summary, "data": data or {}, "files": files or []}
        new = {**task, "evidence": task["evidence"] + [item], "updated": item["at"]}
        self._write(actor, "evidence", task, new, {"summary": summary})
        return new

    def update(self, task_id: str, actor: str, **fields) -> dict:
        """Change ``data``, ``priority``, ``body`` or ``kind`` (merge for ``data``)."""
        task = self.get(task_id)
        bad = set(fields) - {"data", "priority", "body", "kind"}
        if bad:
            raise BoardError(f"cannot update {sorted(bad)}")
        new = {**task, **fields, "updated": self.clock()}
        if "data" in fields:
            new["data"] = {**task["data"], **fields["data"]}
        self._write(actor, "update", task, new, {"fields": sorted(fields)})
        return new

    def close(self, task_id: str, actor: str, resolution: str = "done", note: str = "") -> dict:
        if resolution not in RESOLUTIONS:
            raise BoardError(f"resolution must be one of {RESOLUTIONS}")
        task = self.get(task_id)
        if task["state"] == "closed":
            raise BoardError(f"{task_id} is already closed")
        new = {**task, "state": "closed", "resolution": resolution, "note": note, "updated": self.clock()}
        self._write(actor, "close", task, new, {"resolution": resolution, "note": note})
        return new

    def write_proposal(self, task_id: str, actor: str, name: str, content: str) -> Path:
        """Save a proposal file under ``proposals/`` (never over an existing one) and log it."""
        safe = "".join(c if c.isalnum() or c in "-_." else "-" for c in name)
        path = self.root / "proposals" / f"{task_id}-{safe}"
        if path.exists():
            raise BoardError(f"{path.name} already exists")
        path.write_text(content)
        rel = str(path.relative_to(self.root))
        self.add_evidence(task_id, actor, f"proposal written: {rel}", {"sha256": hashlib.sha256(content.encode())
                                                                       .hexdigest()}, [rel])
        return path

    # -------------------------------------------------------------- history
    def original(self, sha: str) -> dict:
        return json.loads((self.root / "originals" / f"{sha}.json").read_text())

    def history(self, task_id: str) -> list[dict]:
        """Every version of a task, oldest first, rebuilt from the ledger and originals/."""
        return [self.original(e["after"]) for e in self.ledger() if e["task"] == task_id and e["after"]]

    def restore(self, task_id: str, seq: int, actor: str) -> dict:
        """Put a task back to the state it had right after ledger step ``seq``.
        The restore is itself a logged step, so nothing is lost."""
        entry = next((e for e in self.ledger() if e["seq"] == seq), None)
        if entry is None or entry["task"] != task_id:
            raise BoardError(f"step {seq} is not a step of {task_id}")
        old = self.original(entry["after"])
        current = self.get(task_id)
        self._write(actor, "restore", current, {**old, "updated": self.clock()}, {"to_seq": seq})
        return self.get(task_id)

    def verify(self) -> list[str]:
        """Re-check the ledger: sequence, hash chain, and that every version exists.
        Returns a list of problems (empty when the board is intact)."""
        problems, prev = [], ""
        for i, e in enumerate(self.ledger()):
            body = {k: v for k, v in e.items() if k != "hash"}
            if e["seq"] != i:
                problems.append(f"line {i}: seq {e['seq']}")
            if e["prev"] != prev:
                problems.append(f"line {i}: broken chain")
            if _sha(body) != e["hash"]:
                problems.append(f"line {i}: hash mismatch")
            for h in (e["before"], e["after"]):
                if h and not (self.root / "originals" / f"{h}.json").exists():
                    problems.append(f"line {i}: missing original {h[:12]}")
            prev = e["hash"]
        for t in self.tasks():
            last = [e for e in self.ledger() if e["task"] == t["id"]]
            if not last or last[-1]["after"] != _sha(t):
                problems.append(f"task {t['id']}: file differs from ledger")
        return problems

    # ------------------------------------------------------------- internals
    def _task_path(self, task_id: str) -> Path:
        if not task_id or "/" in task_id or task_id.startswith("."):
            raise BoardError(f"bad task id {task_id!r}")
        return self.root / "tasks" / f"{task_id}.json"

    def _keep(self, task: dict | None) -> str | None:
        if task is None:
            return None
        sha = _sha(task)
        path = self.root / "originals" / f"{sha}.json"
        if not path.exists():
            path.write_text(json.dumps(task, indent=2, sort_keys=True))
        return sha

    def _write(self, actor: str, action: str, before: dict | None, after: dict, data: dict):
        before_sha = self._keep(before)
        after_sha = self._keep(after)
        lines = self.ledger()
        entry = {"seq": len(lines), "ts": self.clock(), "actor": actor, "action": action, "task": after["id"],
                 "data": data, "before": before_sha, "after": after_sha, "prev": lines[-1]["hash"] if lines else ""}
        entry["hash"] = _sha(entry)
        tmp = self._task_path(after["id"]).with_suffix(".tmp")
        tmp.write_text(json.dumps(after, indent=2, sort_keys=True))
        tmp.replace(self._task_path(after["id"]))
        with self.ledger_path.open("a") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")
        log.info("%s %s %s %s", entry["seq"], actor, action, after["id"])
        if self.commit:
            self._git_commit(f"board: {actor} {action} {after['id']}")

    def _git_commit(self, message: str):
        def git(*args):
            return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True)

        if git("rev-parse", "--is-inside-work-tree").returncode != 0:
            log.warning("board commit skipped: %s is not in a git work tree", self.root)
            return
        git("add", "--", ".")
        res = git("commit", "-q", "-m", message, "--", ".")
        if res.returncode != 0 and "nothing to commit" not in res.stdout + res.stderr:
            log.warning("board commit failed: %s", res.stderr.strip())
