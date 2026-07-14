import pandas as pd
from datetime import timedelta

def clean_ercot_data(input_filepath, output_filepath):
    print(f"Loading raw ERCOT data from '{input_filepath}'...")
    
    try:
        df = pd.read_excel(input_filepath)
    except FileNotFoundError:
        print(f"Error: Could not find '{input_filepath}'.")
        return

    # 1. Clean column headers
    df.columns = df.columns.str.strip()
    print(f"Detected columns in file: {list(df.columns)}")

    # 2. Map the combined Date/Time column
    hour_col = next((col for col in ['HourEnding', 'Hour_Ending', 'Hour Ending'] if col in df.columns), None)

    if not hour_col:
        print("\nError: Could not identify the 'HourEnding' column.")
        return

    print(f"Parsing combined Date/Time from '{hour_col}'...")
    
    # 3. Scrub string anomalies
    df[hour_col] = df[hour_col].astype(str).str.strip()
    df[hour_col] = df[hour_col].str.replace(' DST', '', regex=False)
    df[hour_col] = df[hour_col].str.replace('*', '', regex=False)
    
    # 4. Handle the "24:00" DateTime Anomaly within the string
    # Identify which strings contain "24:00"
    is_midnight = df[hour_col].str.contains('24:00')
    
    # Replace "24:00" with "00:00" so pandas can parse it
    df.loc[is_midnight, hour_col] = df.loc[is_midnight, hour_col].str.replace('24:00', '00:00')
    
    # Convert the now-valid strings directly to datetime objects
    df['Timestamp'] = pd.to_datetime(df[hour_col])
    
    # Roll the Timestamp forward by 1 day for the rows that originally had '24:00'
    df.loc[is_midnight, 'Timestamp'] = df.loc[is_midnight, 'Timestamp'] + timedelta(days=1)
    
    # Sort chronologically to maintain strict temporal sequence
    df = df.sort_values('Timestamp').reset_index(drop=True)
    
    print("Isolating the COAST zone and slicing the Phase 1 timeframe...")
    
    # 5. Find the COAST column dynamically
    coast_col = next((c for c in df.columns if c.upper() == 'COAST'), None)
    
    if not coast_col:
        print("Error: 'COAST' column missing from data. Check the raw Excel sheet.")
        return
        
    df_filtered = df[['Timestamp', coast_col]].copy()
    
    # Slice exactly for August 2020
    start_date = '2020-08-01'
    end_date = '2020-08-31 23:59:59'
    mask = (df_filtered['Timestamp'] >= start_date) & (df_filtered['Timestamp'] <= end_date)
    df_final = df_filtered.loc[mask].copy()
    
    # Standardize column naming for the inner merge
    df_final.rename(columns={coast_col: 'ERCOT_COAST_Load_MW'}, inplace=True)
    
    # 6. Export the clean artifact
    print(f"Exporting validated training artifact to '{output_filepath}'...")
    df_final.to_csv(output_filepath, index=False)
    
    print(f"Success! Pipeline generated '{output_filepath}' with {len(df_final)} rows.")

if __name__ == "__main__":
    INPUT_FILE = "/kaggle/input/datasets/vsnihal/load-file/Native_Load_2020.xlsx"
    OUTPUT_FILE = "/kaggle/working/ercot_sample.csv"
    
    clean_ercot_data(INPUT_FILE, OUTPUT_FILE)
