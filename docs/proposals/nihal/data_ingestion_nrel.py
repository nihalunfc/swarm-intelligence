import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def clean_nrel_data(filepath='02_phase_01_sample_rawdata.csv', target_month=8):
    print("Loading NREL Weather Data...")
    
    # 1. Ingestion: Skip the first two rows to bypass standard NREL text metadata
    nrel_raw = pd.read_csv(filepath, skiprows=2)
    
    # 2. Timestamp Synthesis: Construct a clean datetime object from separate columns
    nrel_raw['timestamp'] = pd.to_datetime(nrel_raw[['Year', 'Month', 'Day', 'Hour', 'Minute']])
    
    # 3. Temporal Isolation: Filter strictly for our target month (August 2020)
    nrel_target = nrel_raw[nrel_raw['Month'] == target_month].copy()
    
    # 4. Feature Selection: Retain ONLY our final "printable" columns
    nrel_clean = nrel_target[['timestamp', 'GHI', 'DNI', 'DHI', 'Temperature', 'Wind Speed']]

    print("Aggregating Temporal Data...")
    
    # 5. Temporal Aggregation: Force NREL timestamps to round to the nearest hour
    nrel_clean['timestamp'] = nrel_clean['timestamp'].dt.round('H')
    
    # 6. Deduplication: Group by the new hourly timestamp and calculate the mean 
    # This eliminates the 30-min duplicates from the raw NREL pull
    nrel_final = nrel_clean.groupby('timestamp').mean().reset_index()
    
    print("NREL Data Cleaning Complete.")
    return nrel_final

# Execute the isolated function
if __name__ == "__main__":
    nrel_printable_df = clean_nrel_data()
    print(nrel_printable_df.head())
