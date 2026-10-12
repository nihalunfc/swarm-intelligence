import gridstatus
import pandas as pd
import os
import time

def download_ercot_multi_year(years, output_file):
    ercot = gridstatus.Ercot()
    dfs = []
    for year in years:
        print(f"Downloading ERCOT COAST load data for {year}...")
        start = f"{year}-01-01"
        end = f"{year}-12-31"
        
        try:
            # get_load_by_weather_zone returns hourly load per zone for ERCOT
            # Warning: Fetching a whole year day-by-day might take a few minutes
            df = ercot.get_load_by_weather_zone(start=start, end=end)
            
            # The ingestion script expects 'HourEnding' as a string and 'COAST' column
            # gridstatus provides 'Interval End' which we can use
            if 'Interval End' in df.columns:
                df['HourEnding'] = df['Interval End'].dt.strftime('%m/%d/%Y %H:%M')
                
                # Replace ' 00:00' with ' 24:00' of the PREVIOUS day to match ERCOT's native format
                # But actually, the ingestion script converts 24:00 to 00:00. So we can just leave it as 00:00!
                # If we leave it as 00:00, the ingestion script's string replace won't find '24:00' and it will just parse it normally.
                pass
                
            dfs.append(df)
        except Exception as e:
            print(f"Failed to download {year}: {e}")
            
    if dfs:
        final_df = pd.concat(dfs, ignore_index=True)
        # We only need HourEnding and COAST to mimic the raw file for the ingestion script
        out_cols = ['HourEnding', 'COAST']
        if all(c in final_df.columns for c in out_cols):
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            # Save to Excel as the ingestion script uses pd.read_excel
            final_df[out_cols].to_excel(output_file, index=False)
            print(f"Saved multi-year ERCOT data to {output_file} ({len(final_df)} rows).")
        else:
            print(f"Error: Columns {out_cols} not found in fetched data. Found: {final_df.columns}")

if __name__ == "__main__":
    download_ercot_multi_year(
        years=[2018, 2019, 2020, 2021, 2022],
        output_file="data/raw/ercot_2018_2022.xlsx"
    )
