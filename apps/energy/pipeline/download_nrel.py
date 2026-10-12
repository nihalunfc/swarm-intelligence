import pvlib
import pandas as pd
import time
import os
import sys

def download_nrel_multi_year(api_key, email, lat, lon, years, output_file):
    dfs = []
    for year in years:
        print(f"Downloading NREL data for {year}...")
        try:
            data, metadata = pvlib.iotools.get_nsrdb_psm4_conus(
                latitude=lat, longitude=lon, 
                api_key=api_key, email=email, 
                year=year, time_step=60, leap_day=True, utc=False
            )
            
            # pvlib already maps standard variables like 'ghi', 'dni', 'dhi', 'wind_speed', 'air_temperature'
            data['Year'] = data.index.year
            data['Month'] = data.index.month
            data['Day'] = data.index.day
            data['Hour'] = data.index.hour
            data['Minute'] = data.index.minute
            
            col_mapping = {
                'ghi': 'GHI',
                'dni': 'DNI',
                'dhi': 'DHI',
                'temp_air': 'Temperature',
                'wind_speed': 'Wind Speed'
            }
            # lower mapping just in case
            for c in list(data.columns):
                if c.lower() in col_mapping:
                    data.rename(columns={c: col_mapping[c.lower()]}, inplace=True)
            
            # Select necessary columns
            cols = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'GHI', 'DNI', 'DHI', 'Temperature', 'Wind Speed']
            dfs.append(data[cols].reset_index(drop=True))
            time.sleep(2)
        except Exception as e:
            print(f"Failed to download {year}: {e}")
            
    if dfs:
        final_df = pd.concat(dfs, ignore_index=True)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        final_df.to_csv(output_file, index=False)
        print(f"Saved multi-year NREL data to {output_file} ({len(final_df)} rows).")

if __name__ == "__main__":
    # The API key and email come from the environment so they are never committed.
    # Get a free key at https://developer.nrel.gov/signup/
    api_key = os.environ.get("NREL_API_KEY")
    email = os.environ.get("NREL_EMAIL")
    if not api_key or not email:
        sys.exit("Set NREL_API_KEY and NREL_EMAIL before running this script.")
    download_nrel_multi_year(
        api_key=api_key,
        email=email,
        lat=29.41,
        lon=-94.90,
        years=[2018, 2019, 2020, 2021, 2022],
        output_file="data/raw/nrel_2018_2022.csv"
    )
