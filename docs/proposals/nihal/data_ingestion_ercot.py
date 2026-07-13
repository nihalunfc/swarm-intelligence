import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

def clean_ercot_data(filepath='Native_Load_2020.xlsx', target_month=8):
    print("Loading ERCOT Native Load Data from Excel...")
    
    # 1. Ingestion: Requires 'openpyxl' engine to parse the raw Excel workbook
    ercot_raw = pd.read_excel(filepath)
    
    # 2. Sanitize DST: Scrub the Daylight Saving Time (' DST') string artifacts
    ercot_raw['HourEnding'] = ercot_raw['HourEnding'].astype(str).str.replace(' DST', '')
    
    print("Resolving Temporal Anomalies...")
    
    # 3. Midnight Anomaly Fix: Replace '24:00' with '00:00' and shift date forward by 1 day
    # This is mathematically required to prevent pandas from throwing a ValueError
    ercot_raw['HourEnding'] = ercot_raw['HourEnding'].apply(
        lambda x: pd.to_datetime(x.replace(' 24:00', ' 00:00')) + pd.Timedelta(days=1) 
        if ' 24:00' in str(x) else pd.to_datetime(x)
    )
    
    # 4. Temporal Isolation: Filter strictly for our target month (August 2020)
    ercot_target = ercot_raw[ercot_raw['HourEnding'].dt.month == target_month].copy()
    
    # 5. Feature Selection & Standardization: Isolate COAST zone and align column names
    ercot_clean = ercot_target[['HourEnding', 'COAST']].rename(
        columns={'HourEnding': 'timestamp', 'COAST': 'demand_mw'}
    )
    
    print("ERCOT Data Cleaning Complete.")
    
    # Ensure the target directory exists before saving
    if not os.path.exists('processed'):
        os.makedirs('processed')
        
    # 6. Output Extraction: Save the segmented data
    output_path = '02_phase_01_ercot_sample_segmented.csv'
    ercot_clean.to_csv(output_path, index=False)
    
    print(f"Export Complete! Data saved successfully as '{output_path}'")
    
    return ercot_clean

# Execute the isolated function
if __name__ == "__main__":
    ercot_printable_df = clean_ercot_data()
    print(ercot_printable_df.head())
