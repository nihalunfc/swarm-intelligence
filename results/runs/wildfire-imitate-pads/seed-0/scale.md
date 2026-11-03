**forest_saved_pct** by swarm size (model trained with 6 agents)

| policy | 6 agents | 24 agents | 100 agents | 1000 agents |
| :-- | --: | --: | --: | --: |
| swarm (trained) | 89.5 | 86.5 | 72.3 | 49.8 |
| no drones | 47.8 | 33.4 | 9.3 | 6.6 |
| random | 41.9 | 30.2 | 17.1 | 15.5 |
| nearest-fire rule | 91.6 | 87.8 | 91.6 | 85.9 |

**Compute** (one CPU core)

| agents | network params | choose all actions (ms) | env step (ms) | update, batch 32 (ms) | replay per transition (KB) |
| --: | --: | --: | --: | --: | --: |
| 6 | 109,574 | 0.19 | 1.3 | 4.2 | 7.6 |
| 24 | 109,574 | 0.26 | 1.8 | 14.3 | 30.2 |
| 100 | 109,574 | 0.49 | 3.9 | 63.2 | 125.8 |
| 1,000 | 109,574 | 2.77 | 75.1 | 631.9 | 1,257.8 |
