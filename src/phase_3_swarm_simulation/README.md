# Phase 3: Agent-Based Swarm Simulation

This directory contains the entire Reinforcement Learning simulation where autonomous "Smart Battery Nodes" learn to flatten the ERCOT grid curve.

## Swarm Configuration
- **Number of Agents:** 5
- **Individual Battery Capacity:** 200 MW (1,000 MW Total)
- **Charge/Discharge Rate:** 50 MW/hour per agent
- **Why this scale?** ERCOT Coast peak load occasionally breaches 25,000 MW. A 1,000 MW Swarm cluster provides enough capacity to tangibly offset peak demand and bridge extreme troughs without unrealistically assuming infinite battery capacity.

## Running on Kaggle
Because of the heavy multi-agent reinforcement learning (DQN) architecture, you must run this on Kaggle using a GPU to train it in a reasonable timeframe.

1. Upload `train_swarm.ipynb` to Kaggle.
2. Attach the `phase_01_master_environment_full_2018_2022.csv` dataset you generated.
3. Turn on the **GPU T4 x2** accelerator in the Kaggle sidebar.
4. Run all cells.

The notebook contains:
1. **The Custom Gymnasium Environment (`GridSwarmEnv`)**: Handles the physics, maximum capacities, charging penalties, and the Peak-to-Average Ratio (PAR) reward function.
2. **The Deep Q-Network (`QNetwork`)**: A PyTorch neural network built from scratch that maps the 5-agent multi-discrete action space.
3. **The Plotting Engine**: Produces a comparative chart showing the ERCOT load *without* batteries vs. the flattened ERCOT load *with* the AI Swarm.
