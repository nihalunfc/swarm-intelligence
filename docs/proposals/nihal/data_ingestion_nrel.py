import pandas as pd

def clean_nrel_data(input_filepath, output_filepath):
    print(f"Loading raw NREL data from '{input_filepath}'...")
    
    try:
        # NREL NSRDB files typically have 2 rows of metadata before the actual headers.
        # We try reading normally first. If it fails to find standard columns, we skip the metadata.
        df = pd.read_csv(input_filepath)
        if 'Year' not in df.columns and 'GHI' not in df.columns:
            print("Detected NREL metadata headers. Skipping first 2 rows to access column names...")
            df = pd.read_csv(input_filepath, skiprows=2)
    except FileNotFoundError:
        print(f"Error: Could not find '{input_filepath}'.")
        return

    # 1. Clean column headers
    df.columns = df.columns.str.strip()
    
    print("Constructing unified Timestamp from NREL date components...")
    
    # 2. Synthesize the Timestamp column
    # We combine the split date/time columns into a single string, then parse it.
    try:
        datetime_str = (
            df['Year'].astype(str) + '-' +
            df['Month'].astype(str).str.zfill(2) + '-' +
            df['Day'].astype(str).str.zfill(2) + ' ' +
            df['Hour'].astype(str).str.zfill(2) + ':' +
            df['Minute'].astype(str).str.zfill(2)
        )
        df['Timestamp'] = pd.to_datetime(datetime_str)
    except KeyError as e:
        print(f"\nError: Missing expected NREL time column: {e}")
        print(f"Detected columns: {list(df.columns)}")
        return

    # Sort chronologically to maintain structural integrity
    df = df.sort_values('Timestamp').reset_index(drop=True)

    print("Slicing timeframe for Phase 1 (August 2020)...")
    
    # 3. Slice exactly for August 2020 to match the ERCOT sample
    start_date = '2020-08-01'
    end_date = '2020-08-31 23:59:59'
    mask = (df['Timestamp'] >= start_date) & (df['Timestamp'] <= end_date)
    df_filtered = df.loc[mask].copy()

    print("Isolating essential environmental features...")
    
    # 4. Dynamically locate the targeted weather columns
    # We use upper() to ignore case sensitivity in case NREL changes their capitalization
    ghi_col = next((c for c in df.columns if 'GHI' in c.upper()), None)
    dni_col = next((c for c in df.columns if 'DNI' in c.upper()), None)
    dhi_col = next((c for c in df.columns if 'DHI' in c.upper()), None)
    temp_col = next((c for c in df.columns if 'TEMPERATURE' in c.upper()), None)
    wind_col = next((c for c in df.columns if 'WIND SPEED' in c.upper() or 'WIND_SPEED' in c.upper()), None)

    # 5. Define mapping dictionary for standardized column alignment
    features_to_keep = {'Timestamp': 'Timestamp'}
    
    if ghi_col: features_to_keep[ghi_col] = 'NREL_GHI_W_m2'
    if dni_col: features_to_keep[dni_col] = 'NREL_DNI_W_m2'
    if dhi_col: features_to_keep[dhi_col] = 'NREL_DHI_W_m2'
    if temp_col: features_to_keep[temp_col] = 'NREL_Temperature_C'
    if wind_col: features_to_keep[wind_col] = 'NREL_Wind_Speed_m_s'

    # Check if we captured the necessary features
    if len(features_to_keep) < 6:
        print("Warning: Could not find all 5 target environmental features (GHI, DNI, DHI, Temp, Wind).")
        print(f"Found: {list(features_to_keep.keys())}")

    # Extract the isolated features and rename them
    df_final = df_filtered[list(features_to_keep.keys())].rename(columns=features_to_keep)

    # 6. Export the clean artifact
    print(f"Exporting validated training artifact to '{output_filepath}'...")
    df_final.to_csv(output_filepath, index=False)
    
    print(f"Success! Pipeline generated '{output_filepath}' with {len(df_final)} rows.")

if __name__ == "__main__":

    INPUT_FILE = "/kaggle/input/datasets/vsnihal/test-sample/744683_29.41_-94.90_2020.csv" 
    OUTPUT_FILE = "/kaggle/working/nrel_sample.csv"
    
    clean_nrel_data(INPUT_FILE, OUTPUT_FILE)
