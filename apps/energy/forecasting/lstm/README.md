# Phase 2: LSTM Deep Learning Baseline

This directory contains a PyTorch implementation of an LSTM (Long Short-Term Memory) neural network designed to forecast the ERCOT Coast load.

## Architecture
- **Lookback Window**: 24 hours. The model analyzes the previous 24 hours of weather, demand, and cyclical time features to predict the next hour's load.
- **Hidden Layers**: 2 stacked LSTM layers with 64 units each.
- **Output**: A fully connected linear layer predicting the continuous Megawatt load.

## Running on Kaggle (Recommended)
Because PyTorch is a massive deep learning framework, installing it locally on Windows can sometimes fail due to the `MAX_PATH` registry limit (`WinError 206`). Furthermore, training an LSTM on 43,800 rows of sequence data is highly computationally expensive on a local CPU.

**You requested to utilize Kaggle GPUs for this, which is the perfect solution!**

1. Upload the `baseline_lstm.ipynb` file as a new Kaggle Notebook.
2. Attach your dataset (`phase_01_master_environment_full_2018_2022.csv`) to the notebook.
3. In the Kaggle Notebook settings on the right sidebar, change the **Accelerator** to **GPU T4 x2**.
4. Run all cells. The script automatically detects the GPU (`device = cuda`) and will train exponentially faster than a local machine.

## Files
- `baseline_lstm.py`: The raw Python script containing the PyTorch Dataset, DataLoader, Model architecture, and training loops.
- `baseline_lstm.ipynb`: The Jupyter Notebook version of the script, pre-packaged for immediate upload and execution on Kaggle.
