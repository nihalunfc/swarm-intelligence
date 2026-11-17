# Shared board and LLM crew

`core/swarm/board.py` is a task board that swarm watchers, LLM helpers and people share.
`core/swarm/crew.py` puts a small LLM crew on it. Rule first: a learned or LLM-proposed change
stays only if it beats the simple rule on held-out test data.

## The board

A board is a folder (default `runs/board/`, which git ignores):

| path | what it holds |
| :-- | :-- |
| `tasks/<id>.json` | current state of each task (`open`, `claimed`, `closed`) |
| `ledger.jsonl` | one line per step (post, claim, release, evidence, update, close, restore), hash-chained |
| `originals/<sha256>.json` | every version of every task, never deleted |
| `proposals/` | config overrides written by the fixer, never applied automatically |

Each ledger line records the task hash before and after the step, so `Board.restore(task, seq)`
puts any earlier version back (as a new, logged step) and `Board.verify()` catches a hand-edited
or truncated ledger. With `--commit` (or `Board(root, commit=True)`) and the board inside a git
work tree, every step is also a git commit of the board folder only.

## The crew

| step | who | model | what it does |
| :-- | :-- | :-- | :-- |
| watch | Python | none | reads `results/*.json`, posts a `gap` task when the swarm's 95% interval is entirely worse than the best rule (ties are not flagged; "no battery", "random" and perfect-foresight bounds are not rules) |
| triage | Router -> triage | Haiku | fix, watch or won't fix, with one sentence why |
| fix | Router -> fixer | Sonnet | proposes `train.*` / `agent.*` overrides only; data, splits and evaluation keys are dropped; writes `proposals/<task>-overrides.yaml` and the exact `swarm train` command |
| review | Router -> reviewer | Opus, once per run | short plain-English summary of the board |
| gate | Python | none | after someone retrains with the proposal, keeps it only if the new swarm clearly beats the rule on the held-out test split; otherwise closes it as `rejected` |

The routing is plain Python (`crew.Router`). Nothing edits `configs/` or merges anything: nihal
reads the proposal, runs it, gates it, and merges by hand.

## LLM calls are opt-in

Without `SWARM_LLM=1` the crew uses `OfflineClient`, a rule-based stand-in, so the loop runs with
no API key and no cost. CI never calls an API; the tests use a fake client and a mocked SDK.
To use Claude: `pip install anthropic`, sign in (`ANTHROPIC_API_KEY` or `ant auth login`), then
`SWARM_LLM=1 swarm board crew`.

## Commands

```bash
swarm board watch                    # post gaps from results/*.json
swarm board crew                     # triage, fix, one review (offline unless SWARM_LLM=1)
swarm board list --state open
swarm board verify                   # check the hash chain and originals
swarm board gate --task <fix-id> --results-file runs/.../results.json
```

On the current `results/` the watcher flags the known gaps: the wildfire swarms behind the
nearest-fire rule, the paused hotel swarms on some metrics, and one CityLearn ramping metric.
The energy battery swarm is ahead of every rule and is not flagged.
