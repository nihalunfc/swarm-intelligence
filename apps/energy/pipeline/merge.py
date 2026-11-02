import argparse
import sys

import pandas as pd


def merge_datasets(ercot_path, nrel_path, output_path):
    print("Initializing Synthesis Engine...")
    
    try:
        # Load the cleaned intermediate artifacts
        print(f"Loading ERCOT data from '{ercot_path}'...")
        df_ercot = pd.read_csv(ercot_path)
        
        print(f"Loading NREL data from '{nrel_path}'...")
        df_nrel = pd.read_csv(nrel_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Ensure both data ingestion scripts have been run successfully.")
        sys.exit(1)

    # 1. Re-cast Timestamps to datetime objects
    df_ercot['Timestamp'] = pd.to_datetime(df_ercot['Timestamp'])
    df_nrel['Timestamp'] = pd.to_datetime(df_nrel['Timestamp'])

    # 2. Fix Temporal Misalignment
    print("Executing temporal alignment: Flooring NREL 30-minute offsets to the top of the hour...")
    df_nrel['Timestamp'] = df_nrel['Timestamp'].dt.floor('h')

    print("Executing strict inner merge on 'Timestamp'...")
    
    # 3. Perform the inner merge
    df_merged = pd.merge(df_nrel, df_ercot, on='Timestamp', how='inner')

    # 4. Sort chronologically 
    df_merged = df_merged.sort_values('Timestamp').reset_index(drop=True)

    # 5. Pipeline Integrity Diagnostics
    print("\n--- Pipeline Integrity Diagnostics ---")
    print(f"ERCOT input rows: {len(df_ercot)}")
    print(f"NREL input rows:  {len(df_nrel)}")
    print(f"Merged output:    {len(df_merged)} rows")
    
    if len(df_merged) == 0:
        print("Error: Merged output is still 0. Alignment failed.")
        sys.exit(1)
        
    missing_vals = df_merged.isnull().sum().sum()
    if missing_vals > 0:
        print(f"Warning: {missing_vals} missing values detected in the master matrix.")
    else:
        print("Status: VALIDATED. Zero missing values detected in the state-space matrix.")
    print("--------------------------------------\n")

    # 6. Export the master artifact
    print(f"Exporting master environment matrix to '{output_path}'...")
    df_merged.to_csv(output_path, index=False)
    print("Success! Dataset is securely fused and ready for Phase 2.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge Cleaned ERCOT and NREL Datasets")
    parser.add_argument("--ercot_input", required=True, help="Path to cleaned ERCOT CSV")
    parser.add_argument("--nrel_input", required=True, help="Path to cleaned NREL CSV")
    parser.add_argument("--output", required=True, help="Path to output master merged CSV")
    
    args = parser.parse_args()
    merge_datasets(args.ercot_input, args.nrel_input, args.output)
