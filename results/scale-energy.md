**peak_reduction_mw** by swarm size (model trained with 10 agents)

| policy | 10 agents | 100 agents | 1000 agents |
| :-- | --: | --: | --: |
| swarm (trained) | 948.7 | 948.7 | 948.7 |
| no battery | 0.0 | 0.0 | 0.0 |
| threshold rule | 0.0 | 0.0 | 0.0 |
| proportional rule | 0.0 | 0.0 | 0.0 |

**Compute** (one CPU core)

| agents | network params | choose all actions (ms) | env step (ms) | update, batch 32 (ms) | replay per transition (KB) |
| --: | --: | --: | --: | --: | --: |
| 10 | 18,435 | 0.33 | 0.8 | 6.3 | 1.0 |
| 100 | 18,435 | 0.24 | 0.6 | 19.3 | 10.4 |
| 1,000 | 18,435 | 0.81 | 1.3 | 254.7 | 103.5 |
