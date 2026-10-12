import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
from sklearn.linear_model import LinearRegression
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

def load_and_preprocess_data(filepath):
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    
    # 1. Clean ERCOT Load Column
    if df['ERCOT_COAST_Load_MW'].dtype == 'O':
        df['ERCOT_COAST_Load_MW'] = df['ERCOT_COAST_Load_MW'].astype(str).str.replace(',', '').astype(float)
        
    # 2. Parse Timestamp
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.sort_values('Timestamp').reset_index(drop=True)
    
    # 3. Cyclical Feature Engineering (Time Series Best Practices)
    print("Engineering cyclical time features...")
    df['Hour'] = df['Timestamp'].dt.hour
    df['DayOfWeek'] = df['Timestamp'].dt.dayofweek
    df['Month'] = df['Timestamp'].dt.month
    df['DayOfYear'] = df['Timestamp'].dt.dayofyear
    
    # Sine/Cosine transformations to represent cyclicality
    df['Hour_sin'] = np.sin(2 * np.pi * df['Hour'] / 23.0)
    df['Hour_cos'] = np.cos(2 * np.pi * df['Hour'] / 23.0)
    df['Month_sin'] = np.sin(2 * np.pi * df['Month'] / 12.0)
    df['Month_cos'] = np.cos(2 * np.pi * df['Month'] / 12.0)
    
    # We can drop the raw Hour/Month if we want, but keeping them is fine for tree models
    
    return df

def chronological_train_test_split(df, split_date='2022-01-01'):
    print(f"Splitting data chronologically at {split_date}...")
    train = df[df['Timestamp'] < split_date].copy()
    test = df[df['Timestamp'] >= split_date].copy()
    
    print(f"Train size (2018-2021): {len(train)} rows")
    print(f"Test size (2022): {len(test)} rows")
    return train, test

def prepare_features_and_target(train, test):
    # Features to use for modeling
    features = [
        'NREL_GHI_W_m2', 'NREL_DNI_W_m2', 'NREL_DHI_W_m2', 
        'NREL_Temperature_C', 'NREL_Wind_Speed_m_s',
        'Hour', 'DayOfWeek', 'Month', 'DayOfYear',
        'Hour_sin', 'Hour_cos', 'Month_sin', 'Month_cos'
    ]
    target = 'ERCOT_COAST_Load_MW'
    
    X_train = train[features]
    y_train = train[target]
    
    X_test = test[features]
    y_test = test[target]
    
    # Scale continuous features
    scaler = StandardScaler()
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()
    
    # We only scale the environmental variables, not the cyclical ones technically, 
    # but scaling everything is safe for most models. Let's scale all for simplicity.
    X_train_scaled[features] = scaler.fit_transform(X_train[features])
    X_test_scaled[features] = scaler.transform(X_test[features])
    
    return X_train_scaled, y_train, X_test_scaled, y_test, features

def evaluate_model(name, y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100
    
    print(f"--- {name} Results ---")
    print(f"MAE:  {mae:.2f} MW")
    print(f"RMSE: {rmse:.2f} MW")
    print(f"MAPE: {mape:.2f} %\n")
    return {'MAE': mae, 'RMSE': rmse, 'MAPE': mape}

def plot_predictions(test_df, y_test, y_pred_linear, y_pred_xgb, output_path="predictions_vs_actuals.png"):
    # Plot a 1-week sample (168 hours) in Summer 2022 (e.g., July 1st week)
    print(f"Generating sample prediction plot to {output_path}...")
    
    plot_df = test_df.copy()
    plot_df['Actual'] = y_test
    plot_df['Linear_Pred'] = y_pred_linear
    plot_df['XGB_Pred'] = y_pred_xgb
    
    # Select first week of July 2022
    sample_df = plot_df[(plot_df['Timestamp'] >= '2022-07-01') & (plot_df['Timestamp'] < '2022-07-08')]
    
    plt.figure(figsize=(15, 6))
    plt.plot(sample_df['Timestamp'], sample_df['Actual'], label='Actual ERCOT Load', color='black', linewidth=2)
    plt.plot(sample_df['Timestamp'], sample_df['Linear_Pred'], label='Linear Regression Baseline', color='red', linestyle='--')
    plt.plot(sample_df['Timestamp'], sample_df['XGB_Pred'], label='XGBoost Baseline', color='blue', linestyle='-.')
    
    plt.title('Predictive Modeling Baselines: Actual vs Predicted Load (July 2022 Sample)', fontsize=14)
    plt.xlabel('Date')
    plt.ylabel('Load (MW)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path)
    print("Plot saved successfully.")

if __name__ == "__main__":
    # Define paths
    data_path = "../../../data/clean_data/phase_01_master_environment_full_2018_2022.csv"
    
    if not os.path.exists(data_path):
        # Handle execution from repo root
        data_path = "data/clean_data/phase_01_master_environment_full_2018_2022.csv"
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Could not find dataset at {data_path}")
            
    # 1. Load and Preprocess
    df = load_and_preprocess_data(data_path)
    
    # 2. Split Data
    train, test = chronological_train_test_split(df, split_date='2022-01-01')
    
    # 3. Feature Engineering
    X_train, y_train, X_test, y_test, feature_names = prepare_features_and_target(train, test)
    
    # 4. Naive / Linear Baseline
    print("Training Linear Regression Baseline...")
    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train)
    y_pred_linear = linear_model.predict(X_test)
    evaluate_model("Linear Regression Baseline", y_test, y_pred_linear)
    
    # 5. XGBoost Baseline
    print("Training XGBoost Regressor Baseline...")
    xgb_model = xgb.XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        early_stopping_rounds=50
    )
    xgb_model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
    y_pred_xgb = xgb_model.predict(X_test)
    evaluate_model("XGBoost Baseline", y_test, y_pred_xgb)
    
    # 6. Feature Importance (XGBoost)
    print("Top 5 Important Features (XGBoost):")
    importance = xgb_model.feature_importances_
    for i, v in sorted(enumerate(importance), key=lambda x: x[1], reverse=True)[:5]:
        print(f" - {feature_names[i]}: {v:.4f}")
        
    # 7. Visual Evaluation
    plot_predictions(test, y_test, y_pred_linear, y_pred_xgb, output_path="src/phase_2_baseline_modeling/xgboost/predictions_vs_actuals.png")
    
    print("\nPhase 2 Baseline Modeling Complete.")
