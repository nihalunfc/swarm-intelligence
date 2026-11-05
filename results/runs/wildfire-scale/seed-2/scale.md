**forest_saved_pct** by swarm size (model trained with 24 agents)

| policy | 6 agents | 24 agents | 100 agents | 1000 agents |
| :-- | --: | --: | --: | --: |
| swarm (trained) | 67.7 | 61.5 | 36.3 | 34.6 |
| no drones | 47.8 | 33.4 | 9.3 | 6.6 |
| random | 41.9 | 30.2 | 17.1 | 15.5 |
| nearest-fire rule | 91.6 | 87.8 | 91.6 | 85.9 |

**Compute** (one CPU core)

| agents | network params | choose all actions (ms) | env step (ms) | update, batch 32 (ms) | replay per transition (KB) |
| --: | --: | --: | --: | --: | --: |
| 6 | 109,574 | 0.06 | 0.6 | 2.6 | 7.6 |
| 24 | 109,574 | 0.09 | 0.8 | 9.6 | 30.2 |
| 100 | 109,574 | 0.25 | 1.9 | 46.7 | 125.8 |
| 1,000 | 109,574 | 2.07 | 38.2 | 487.8 | 1,257.8 |
