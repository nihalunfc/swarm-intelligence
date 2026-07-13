import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

def clean_nrel_data(filepath='02_phase_01_sample_rawdata_nrel.csv', target_month=8):
    print("Loading NREL Weather Data...")
    
    # 1. Ingestion
    nrel_raw = pd.read_csv(filepath, skiprows=2)
    
    # 2. Timestamp Synthesis
    nrel_raw['timestamp'] = pd.to_datetime(nrel_raw[['Year', 'Month', 'Day', 'Hour', 'Minute']])
    
    # 3. Temporal Isolation
    nrel_target = nrel_raw[nrel_raw['Month'] == target_month].copy()
    
    # 4. Feature Selection
    nrel_clean = nrel_target[['timestamp', 'GHI', 'DNI', 'DHI', 'Temperature', 'Wind Speed']]

    print("Aggregating Temporal Data...")
    
    # 5. Temporal Aggregation
    nrel_clean['timestamp'] = nrel_clean['timestamp'].dt.round('H')
    
    # 6. Deduplication
    nrel_final = nrel_clean.groupby('timestamp').mean().reset_index()
    
    print("NREL Data Cleaning Complete.")
    
    # ---File Export ---

    if not os.path.exists('processed'):
        os.makedirs('processed')
        
    # 7. Output Extraction
    output_path = '02_phase_01_sample_segmented.csv'
    nrel_final.to_csv(output_path, index=False)
    
    print(f"Export Complete! Data saved successfully as '{output_path}'")
    
    return nrel_final

if __name__ == "__main__":
    nrel_printable_df = clean_nrel_data()
