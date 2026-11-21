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
| watch | Python | none | reads `results/*.json`, posts one `gap` task per run listing every metric where the swarm's 95% interval is entirely worse than the best rule (ties are not flagged; "no battery", "random" and perfect-foresight bounds are not rules). Paused apps (hotel) are skipped unless you pass `--skip` with other prefixes |
| triage | Router -> triage | Haiku | fix, watch or won't fix, with one sentence why |
| fix | Router -> fixer | Sonnet | proposes `train.*` / `agent.*` overrides only; data, splits and evaluation keys are dropped; writes `proposals/<task>-overrides.yaml` and the exact `swarm train` command |
| review | Router -> reviewer | Opus, once per run | short plain-English summary of the board |
| gate | Python | none | after someone retrains with the proposal, keeps it only if the new swarm clearly beats the rule on the held-out test split on **every** flagged metric; otherwise closes it as `rejected` |

The routing is plain Python (`crew.Router`). Nothing edits `configs/` or merges anything: nihal
reads the proposal, runs it, gates it, and merges by hand.

## LLM calls are opt-in

Without `SWARM_LLM=1` the crew uses `OfflineClient`, a rule-based stand-in, so the loop runs with
no API key and no cost. CI never calls an API; the tests use a fake client and a mocked SDK.
To use Claude: `pip install anthropic`, sign in (`ANTHROPIC_API_KEY` or `ant auth login`), then
`SWARM_LLM=1 swarm board crew`.

After a live run the CLI prints the calls and tokens per model and an estimated cost at list
prices (Haiku 5.5 $0.10/$0.50, Sonnet 5.5 $2/$10, Opus 5.5 $4/$20 per million tokens in/out).
On the current results a full run is about 6 triage calls, up to 5 fixer calls and one review,
which comes to cents, not dollars.

## Gating a proposal (step by step)

1. Read the proposal: `cat runs/board/proposals/<fix-id>-overrides.yaml`. The `try` command is on the task too.
2. Retrain with it on 3 seeds (wildfire: about 20 minutes per seed per 600k steps on 4 CPU cores):
   `swarm seeds --config configs/wildfire.yaml --seeds 0 1 2 --set <overrides> label=wildfire-crew-<fix-id>`
3. Gate on the held-out test fires: `swarm board gate --task <fix-id> --results-file runs/seeds-wildfire-crew-<fix-id>-*/summary.json`
4. Kept proposals still need you to copy the overrides into `configs/` and merge. Rejected ones stay on the board as a record.

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

## Gate log

| date | task | proposal | held-out result (3 seeds x 50 fires) | verdict |
| :-- | :-- | :-- | :-- | :-- |
| 2026-11-21 | wildfire gap (offline crew, control) | `train.total_steps` 600k -> 1.2M | forest saved 72.6% [65.1, 79.3] vs rule 90.1% (600k swarm: 79.2%) | rejected: training longer made it worse |
