"""Shared board and LLM crew. No network, no API key: the LLM is always a fake."""

import json
import subprocess
from types import SimpleNamespace

import pytest
import yaml

from swarm import crew
from swarm.board import Board, BoardError


def _results(swarm, rule, metric="std_reduction_pct", split="test"):
    return {"energy": {"app": "energy", "split": split, "metrics": [metric, "return"], "policies": {
        "swarm (trained)": {metric: swarm, "return": [1, 1, 1]},
        "no battery": {metric: [0, 0, 0], "return": [0, 0, 0]},
        "proportional rule": {metric: rule, "return": [9, 9, 9]},
        "optimum: flattest (perfect foresight)": {metric: [99, 99, 99], "return": [99, 99, 99]},
    }}}


def test_post_claim_evidence_close_and_ledger(tmp_path):
    b = Board(tmp_path)
    t = b.post("alice", "check peak", data={"x": 1})
    b.claim(t["id"], "bob")
    with pytest.raises(BoardError):
        b.claim(t["id"], "carol")
    b.add_evidence(t["id"], "bob", "ran it", {"peak": 3})
    b.close(t["id"], "bob", "done")
    with pytest.raises(BoardError):
        b.add_evidence(t["id"], "bob", "late")
    actions = [e["action"] for e in b.ledger()]
    assert actions == ["post", "claim", "evidence", "close"]
    assert b.get(t["id"])["state"] == "closed" and b.verify() == []
    assert len(b.history(t["id"])) == 4


def test_originals_recoverable_and_restore(tmp_path):
    b = Board(tmp_path)
    t = b.post("a", "task")
    b.update(t["id"], "a", data={"v": 1})
    b.update(t["id"], "a", data={"v": 2})
    first_update = b.ledger()[1]["seq"]
    restored = b.restore(t["id"], first_update, "a")
    assert restored["data"]["v"] == 1
    assert [h["data"].get("v") for h in b.history(t["id"])] == [None, 1, 2, 1]
    assert b.verify() == []


def test_verify_catches_tampering(tmp_path):
    b = Board(tmp_path)
    t = b.post("a", "task")
    b.close(t["id"], "a")
    lines = b.ledger_path.read_text().splitlines()
    edited = json.loads(lines[0])
    edited["actor"] = "mallory"
    b.ledger_path.write_text("\n".join([json.dumps(edited)] + lines[1:]) + "\n")
    assert any("hash mismatch" in p for p in b.verify())


def test_post_with_key_does_not_duplicate(tmp_path):
    b = Board(tmp_path)
    t1 = b.post("a", "x", key="k")
    assert b.post("a", "x again", key="k")["id"] == t1["id"]


def test_git_commit_per_step(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    for k, v in (("user.email", "t@example.com"), ("user.name", "t")):
        subprocess.run(["git", "-C", str(tmp_path), "config", k, v], check=True)
    b = Board(tmp_path / "board", commit=True)
    t = b.post("a", "x")
    b.close(t["id"], "a")
    log = subprocess.run(["git", "-C", str(tmp_path), "log", "--oneline"], capture_output=True, text=True).stdout
    assert log.count("board:") == 2


def test_find_gaps_flags_only_clear_losses():
    behind = crew.find_gaps(_results([8.0, 7.5, 8.5], [9.0, 9.0, 9.0]), "energy")
    assert len(behind) == 1 and behind[0].rule == "proportional rule" and behind[0].gap_pct > 0
    tie = crew.find_gaps(_results([8.8, 8.2, 9.4], [9.0, 9.0, 9.0]), "energy")
    ahead = crew.find_gaps(_results([10.0, 9.8, 10.2], [9.0, 9.0, 9.0]), "energy")
    assert tie == [] and ahead == []  # optimum and no-battery are never treated as rules


def test_lower_is_better_metric():
    gaps = crew.find_gaps(_results([60.0, 55.0, 65.0], [50.0, 50.0, 50.0], metric="burned_cells"), "w")
    assert len(gaps) == 1 and gaps[0].lower_is_better


def test_check_proposal_dev_only():
    clean = crew.check_proposal({"train.total_steps": 1000, "agent.lr": 0.001, "env.test_start": "2020-01-01",
                                 "eval.episodes": 1, "train.cmd": {"rm": 1}})
    assert clean == {"train.total_steps": 1000, "agent.lr": 0.001}
    with pytest.raises(ValueError):
        crew.check_proposal({"env.data_path": "x"})


class FakeLLM:
    name = "fake"

    def __init__(self):
        self.calls = []

    def complete(self, role, system, prompt):
        self.calls.append(role)
        if role == "triage":
            return 'Sure: {"decision": "fix", "reason": "big gap"}'
        if role == "fix":
            return json.dumps({"overrides": {"train.total_steps": 99, "env.test_start": "2020-01-01"},
                               "reason": "train longer"})
        return "summary"


def _setup(tmp_path, swarm=(8.0, 7.5, 8.5)):
    repo = tmp_path / "repo"
    (repo / "configs").mkdir(parents=True)
    (repo / "configs" / "energy.yaml").write_text(yaml.safe_dump({"app": "energy", "train": {"total_steps": 10}}))
    res = tmp_path / "results"
    res.mkdir()
    (res / "energy.json").write_text(json.dumps(_results(list(swarm), [9.0, 9.0, 9.0])))
    return repo, res, Board(tmp_path / "board")


def test_crew_end_to_end_with_fake_llm(tmp_path):
    repo, res, board = _setup(tmp_path)
    assert len(crew.watch(board, res)) == 1
    assert crew.watch(board, res) == []  # same gap is not posted twice
    llm = FakeLLM()
    counts = crew.Router(board, client=llm, repo=repo).run()
    assert counts == {"triage": 1, "fix": 1, "review": 1, "errors": 0}
    assert llm.calls == ["triage", "fix", "review"]  # Opus-tier review once per run
    fix = board.tasks(kind="fix")[0]
    assert fix["state"] == "open" and fix["data"]["overrides"] == {"train.total_steps": 99}
    proposal = yaml.safe_load((board.root / fix["data"]["proposal"]).read_text())
    assert proposal["base_config"] == "configs/energy.yaml" and "env.test_start" not in proposal["overrides"]
    assert yaml.safe_load((repo / "configs" / "energy.yaml").read_text())["train"]["total_steps"] == 10
    assert board.verify() == []

    # Rule first: a retrain that only ties the rule is rejected, one that clears it is kept.
    tie = tmp_path / "tie.json"
    tie.write_text(json.dumps(_results([9.1, 8.6, 9.6], [9.0, 9.0, 9.0])))
    assert crew.gate(board, fix["id"], tie) is False
    assert board.get(fix["id"])["resolution"] == "rejected"


def test_gate_keeps_a_clear_win_and_needs_test_split(tmp_path):
    _, res, board = _setup(tmp_path)
    t = board.post("x", "fix", kind="fix", data={"metric": "std_reduction_pct", "rule": "proportional rule"})
    val = tmp_path / "val.json"
    val.write_text(json.dumps(_results([12, 11, 13], [9, 9, 9], split="val")))
    with pytest.raises(ValueError):
        crew.gate(board, t["id"], val)
    win = tmp_path / "win.json"
    win.write_text(json.dumps(_results([12, 11, 13], [9, 9, 9])))
    assert crew.gate(board, t["id"], win) is True


def test_bad_llm_reply_releases_task(tmp_path):
    _, res, board = _setup(tmp_path)
    crew.watch(board, res)

    class Broken(FakeLLM):
        def complete(self, role, system, prompt):
            return "no json here" if role == "triage" else "ok"

    counts = crew.Router(board, client=Broken(), repo=tmp_path).run()
    assert counts["errors"] == 1 and board.tasks(kind="gap")[0]["state"] == "open"


def test_offline_client_runs_whole_loop(tmp_path, monkeypatch):
    monkeypatch.delenv("SWARM_LLM", raising=False)
    assert isinstance(crew.default_client(), crew.OfflineClient)
    repo, res, board = _setup(tmp_path)
    crew.watch(board, res)
    counts = crew.Router(board, repo=repo).run()
    assert counts["errors"] == 0 and board.tasks(kind="fix")[0]["data"]["overrides"] == {"train.total_steps": 20}


def test_anthropic_client_uses_role_models_with_mocked_sdk():
    seen = []

    def create(**kw):
        seen.append(kw)
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text="hi")])

    sdk = SimpleNamespace(messages=SimpleNamespace(create=create),
                          beta=SimpleNamespace(messages=SimpleNamespace(create=create)))
    c = crew.AnthropicClient(client=sdk)
    assert [c.complete(r, "s", "{}") for r in ("triage", "fix", "review")] == ["hi"] * 3
    assert [k["model"] for k in seen] == ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"]


def test_real_results_files_parse(tmp_path):
    from pathlib import Path

    board = Board(tmp_path)
    crew.watch(board, Path(__file__).resolve().parents[1] / "results")
    assert board.verify() == []
