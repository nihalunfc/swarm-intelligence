import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
import warnings
warnings.filterwarnings('ignore')

# --- 1. PyTorch Dataset Definition ---
class TimeSeriesDataset(Dataset):
    def __init__(self, X, y, sequence_length=24):
        self.X = X
        self.y = y
        self.sequence_length = sequence_length

    def __len__(self):
        return len(self.X) - self.sequence_length

    def __getitem__(self, idx):
        # Return a sequence of X and the target y at the *end* of the sequence
        x_seq = self.X[idx : idx + self.sequence_length]
        y_target = self.y[idx + self.sequence_length]
        return torch.tensor(x_seq, dtype=torch.float32), torch.tensor(y_target, dtype=torch.float32)


# --- 2. PyTorch LSTM Model ---
class ERCOT_LSTM(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2):
        super(ERCOT_LSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Batch_first=True implies input shape is (batch, seq, feature)
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        # h0 and c0 are automatically initialized to zeros if not provided
        out, _ = self.lstm(x)
        
        # Take the output from the last time step in the sequence
        out = out[:, -1, :]
        out = self.fc(out)
        return out


# --- 3. Data Loading and Preprocessing ---
def load_and_preprocess_data(filepath):
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    
    # 1. Clean ERCOT Load Column
    if df['ERCOT_COAST_Load_MW'].dtype == 'O':
        df['ERCOT_COAST_Load_MW'] = df['ERCOT_COAST_Load_MW'].astype(str).str.replace(',', '').astype(float)
        
    # 2. Parse Timestamp
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.sort_values('Timestamp').reset_index(drop=True)
    
    # 3. Cyclical Feature Engineering
    df['Hour'] = df['Timestamp'].dt.hour
    df['DayOfWeek'] = df['Timestamp'].dt.dayofweek
    df['Month'] = df['Timestamp'].dt.month
    df['DayOfYear'] = df['Timestamp'].dt.dayofyear
    
    df['Hour_sin'] = np.sin(2 * np.pi * df['Hour'] / 23.0)
    df['Hour_cos'] = np.cos(2 * np.pi * df['Hour'] / 23.0)
    df['Month_sin'] = np.sin(2 * np.pi * df['Month'] / 12.0)
    df['Month_cos'] = np.cos(2 * np.pi * df['Month'] / 12.0)
    
    return df

def prepare_data(df, sequence_length=24):
    features = [
        'NREL_GHI_W_m2', 'NREL_DNI_W_m2', 'NREL_DHI_W_m2', 
        'NREL_Temperature_C', 'NREL_Wind_Speed_m_s',
        'Hour', 'DayOfWeek', 'Month', 'DayOfYear',
        'Hour_sin', 'Hour_cos', 'Month_sin', 'Month_cos'
    ]
    target = 'ERCOT_COAST_Load_MW'
    
    print("Splitting data chronologically at 2022-01-01...")
    train_df = df[df['Timestamp'] < '2022-01-01'].copy()
    test_df = df[df['Timestamp'] >= '2022-01-01'].copy()
    
    # Extract arrays
    X_train_raw = train_df[features].values
    y_train_raw = train_df[target].values.reshape(-1, 1)
    
    X_test_raw = test_df[features].values
    y_test_raw = test_df[target].values.reshape(-1, 1)
    
    # Scaling Features
    feature_scaler = StandardScaler()
    X_train_scaled = feature_scaler.fit_transform(X_train_raw)
    X_test_scaled = feature_scaler.transform(X_test_raw)
    
    # Scaling Target (Crucial for Neural Network convergence)
    target_scaler = StandardScaler()
    y_train_scaled = target_scaler.fit_transform(y_train_raw)
    y_test_scaled = target_scaler.transform(y_test_raw)
    
    # Create PyTorch Datasets
    train_dataset = TimeSeriesDataset(X_train_scaled, y_train_scaled, sequence_length)
    test_dataset = TimeSeriesDataset(X_test_scaled, y_test_scaled, sequence_length)
    
    # Dataloaders
    batch_size = 256
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    print(f"Train batches: {len(train_loader)} | Test batches: {len(test_loader)}")
    return train_loader, test_loader, target_scaler, test_df, len(features)


# --- 4. Training Loop ---
def train_model(model, train_loader, epochs=5, lr=0.001, device='cpu'):
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    model.train()
    print(f"Training on {device} for {epochs} epochs...")
    
    for epoch in range(epochs):
        epoch_loss = 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            
            optimizer.zero_grad()
            y_pred = model(X_batch)
            
            loss = criterion(y_pred, y_batch)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            
        print(f"Epoch {epoch+1}/{epochs} - Loss: {epoch_loss/len(train_loader):.4f}")

# --- 5. Evaluation and Plotting ---
def evaluate_model(model, test_loader, target_scaler, device='cpu'):
    model.eval()
    predictions = []
    actuals = []
    
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            X_batch = X_batch.to(device)
            y_pred = model(X_batch).cpu().numpy()
            
            predictions.extend(y_pred)
            actuals.extend(y_batch.numpy())
            
    # Inverse transform to get back to Megawatts (MW)
    predictions = target_scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
    actuals = target_scaler.inverse_transform(np.array(actuals).reshape(-1, 1)).flatten()
    
    mae = mean_absolute_error(actuals, predictions)
    rmse = np.sqrt(mean_squared_error(actuals, predictions))
    mape = mean_absolute_percentage_error(actuals, predictions) * 100
    
    print(f"\n--- LSTM Baseline Results ---")
    print(f"MAE:  {mae:.2f} MW")
    print(f"RMSE: {rmse:.2f} MW")
    print(f"MAPE: {mape:.2f} %\n")
    
    return predictions, actuals

def plot_predictions(test_df, predictions, sequence_length, output_path="predictions_vs_actuals_lstm.png"):
    # The first 'sequence_length' rows in test_df don't have a prediction because they act as the initial lookback
    plot_df = test_df.iloc[sequence_length:].copy()
    plot_df['LSTM_Pred'] = predictions
    
    sample_df = plot_df[(plot_df['Timestamp'] >= '2022-07-01') & (plot_df['Timestamp'] < '2022-07-08')]
    
    plt.figure(figsize=(15, 6))
    plt.plot(sample_df['Timestamp'], sample_df['ERCOT_COAST_Load_MW'], label='Actual ERCOT Load', color='black', linewidth=2)
    plt.plot(sample_df['Timestamp'], sample_df['LSTM_Pred'], label='LSTM Baseline (24h Lookback)', color='green', linestyle='-.')
    
    plt.title('LSTM Deep Learning Baseline: Actual vs Predicted Load (July 2022 Sample)', fontsize=14)
    plt.xlabel('Date')
    plt.ylabel('Load (MW)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    data_path = "../../../data/clean_data/phase_01_master_environment_full_2018_2022.csv"
    if not os.path.exists(data_path):
        data_path = "data/clean_data/phase_01_master_environment_full_2018_2022.csv"
        
    df = load_and_preprocess_data(data_path)
    
    SEQUENCE_LENGTH = 24
    train_loader, test_loader, target_scaler, test_df, num_features = prepare_data(df, sequence_length=SEQUENCE_LENGTH)
    
    # Auto-detect GPU (CUDA or Apple MPS)
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    
    model = ERCOT_LSTM(input_size=num_features, hidden_size=64, num_layers=2).to(device)
    
    # Train for 5 epochs (takes slightly longer on CPU, but manageable for baseline verification)
    train_model(model, train_loader, epochs=5, lr=0.001, device=device)
    
    predictions, actuals = evaluate_model(model, test_loader, target_scaler, device=device)
    
    # Save Model Weights
    os.makedirs("src/phase_2_baseline_modeling/lstm", exist_ok=True)
    torch.save(model.state_dict(), "src/phase_2_baseline_modeling/lstm/lstm_baseline.pth")
    print("Model saved to src/phase_2_baseline_modeling/lstm/lstm_baseline.pth")
    
    plot_predictions(test_df, predictions, SEQUENCE_LENGTH, output_path="src/phase_2_baseline_modeling/lstm/predictions_vs_actuals_lstm.png")
