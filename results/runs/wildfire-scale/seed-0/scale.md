**forest_saved_pct** by swarm size (model trained with 24 agents)

| policy | 6 agents | 24 agents | 100 agents | 1000 agents |
| :-- | --: | --: | --: | --: |
| swarm (trained) | 71.1 | 72.9 | 53.8 | 32.0 |
| no drones | 47.8 | 33.4 | 9.3 | 6.6 |
| random | 41.9 | 30.2 | 17.1 | 15.5 |
| nearest-fire rule | 91.6 | 87.8 | 91.6 | 85.9 |

**Compute** (one CPU core)

| agents | network params | choose all actions (ms) | env step (ms) | update, batch 32 (ms) | replay per transition (KB) |
| --: | --: | --: | --: | --: | --: |
| 6 | 109,574 | 0.20 | 1.3 | 4.1 | 7.6 |
| 24 | 109,574 | 0.22 | 1.7 | 13.5 | 30.2 |
| 100 | 109,574 | 0.42 | 3.7 | 60.0 | 125.8 |
| 1,000 | 109,574 | 2.74 | 63.4 | 594.8 | 1,257.8 |
