**forest_saved_pct** by swarm size (model trained with 6 agents)

| policy | 10 agents | 100 agents | 1000 agents |
| :-- | --: | --: | --: |
| swarm (trained) | 82.9 | 41.1 | 26.2 |
| no drones | 22.2 | 9.8 | 7.5 |
| random | 33.0 | 19.2 | 10.9 |
| nearest-fire rule | 79.4 | 47.4 | 39.5 |

**Compute** (one CPU core)

| agents | network params | choose all actions (ms) | env step (ms) | update, batch 32 (ms) | replay per transition (KB) |
| --: | --: | --: | --: | --: | --: |
| 10 | 109,574 | 0.32 | 2.2 | 8.7 | 12.6 |
| 100 | 109,574 | 0.89 | 9.9 | 69.3 | 125.8 |
| 1,000 | 109,574 | 3.47 | 45.8 | 835.1 | 1,257.8 |
