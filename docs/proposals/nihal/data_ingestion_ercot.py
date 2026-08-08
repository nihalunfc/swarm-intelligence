import argparse
import pandas as pd
from datetime import timedelta
import sys

def clean_ercot_data(input_filepath, output_filepath, start_date, end_date):
    print(f"Loading raw ERCOT data from '{input_filepath}'...")
    
    try:
        df = pd.read_excel(input_filepath)
    except FileNotFoundError:
        print(f"Error: Could not find '{input_filepath}'.")
        sys.exit(1)

    # 1. Clean column headers
    df.columns = df.columns.str.strip()
    print(f"Detected columns in file: {list(df.columns)}")

    # 2. Map the combined Date/Time column
    hour_col = next((col for col in ['HourEnding', 'Hour_Ending', 'Hour Ending'] if col in df.columns), None)

    if not hour_col:
        print("\nError: Could not identify the 'HourEnding' column.")
        sys.exit(1)

    print(f"Parsing combined Date/Time from '{hour_col}'...")
    
    # 3. Scrub string anomalies
    df[hour_col] = df[hour_col].astype(str).str.strip()
    df[hour_col] = df[hour_col].str.replace(' DST', '', regex=False)
    df[hour_col] = df[hour_col].str.replace('*', '', regex=False)
    
    # 4. Handle the "24:00" DateTime Anomaly within the string
    is_midnight = df[hour_col].str.contains('24:00')
    df.loc[is_midnight, hour_col] = df.loc[is_midnight, hour_col].str.replace('24:00', '00:00')
    
    df['Timestamp'] = pd.to_datetime(df[hour_col])
    df.loc[is_midnight, 'Timestamp'] = df.loc[is_midnight, 'Timestamp'] + timedelta(days=1)
    
    df = df.sort_values('Timestamp').reset_index(drop=True)
    
    print(f"Isolating the COAST zone and slicing for {start_date} to {end_date}...")
    
    # 5. Find the COAST column dynamically
    coast_col = next((c for c in df.columns if c.upper() == 'COAST'), None)
    
    if not coast_col:
        print("Error: 'COAST' column missing from data. Check the raw Excel sheet.")
        sys.exit(1)
        
    df_filtered = df[['Timestamp', coast_col]].copy()
    
    # Slice exactly for the target date range
    mask = (df_filtered['Timestamp'] >= start_date) & (df_filtered['Timestamp'] <= end_date)
    df_final = df_filtered.loc[mask].copy()
    
    # Standardize column naming for the inner merge
    df_final.rename(columns={coast_col: 'ERCOT_COAST_Load_MW'}, inplace=True)
    
    # 6. Export the clean artifact
    print(f"Exporting validated training artifact to '{output_filepath}'...")
    df_final.to_csv(output_filepath, index=False)
    
    print(f"Success! Pipeline generated '{output_filepath}' with {len(df_final)} rows.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ERCOT Data Ingestion & Cleaning")
    parser.add_argument("--input", required=True, help="Path to raw ERCOT Excel file")
    parser.add_argument("--output", required=True, help="Path to output cleaned CSV file")
    parser.add_argument("--start_date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end_date", required=True, help="End date (YYYY-MM-DD HH:MM:SS)")
    
    args = parser.parse_args()
    clean_ercot_data(args.input, args.output, args.start_date, args.end_date)
