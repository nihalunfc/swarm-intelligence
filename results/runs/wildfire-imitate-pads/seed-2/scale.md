**forest_saved_pct** by swarm size (model trained with 6 agents)

| policy | 6 agents | 24 agents | 100 agents | 1000 agents |
| :-- | --: | --: | --: | --: |
| swarm (trained) | 91.7 | 74.8 | 62.4 | 53.7 |
| no drones | 47.8 | 33.4 | 9.3 | 6.6 |
| random | 41.9 | 30.2 | 17.1 | 15.5 |
| nearest-fire rule | 91.6 | 87.8 | 91.6 | 85.9 |

**Compute** (one CPU core)

| agents | network params | choose all actions (ms) | env step (ms) | update, batch 32 (ms) | replay per transition (KB) |
| --: | --: | --: | --: | --: | --: |
| 6 | 109,574 | 0.11 | 0.9 | 3.3 | 7.6 |
| 24 | 109,574 | 0.15 | 1.2 | 12.1 | 30.2 |
| 100 | 109,574 | 0.33 | 2.7 | 52.8 | 125.8 |
| 1,000 | 109,574 | 2.42 | 53.5 | 532.8 | 1,257.8 |
