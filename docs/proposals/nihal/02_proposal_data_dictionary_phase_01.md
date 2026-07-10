# Data Dictionary: Phase 1 Environment State

## Primary Dataset: NREL Solar & Meteorological Supply
This dataset serves as the base thermodynamic environment for the Agent-Based Swarm simulation. It provides the highly volatile, stochastic renewable energy generation metrics required to train the agents' Markov Decision Process.

* **Source Authority:** National Solar Radiation Database (NSRDB) via the National Renewable Energy Laboratory (NREL).
* **Reference URL:** [https://nsrdb.nrel.gov/data-viewer](https://nsrdb.nrel.gov/data-viewer)
* **Geographic Node:** Texas City, Texas (Latitude: 29.41, Longitude: -94.90) - ERCOT Grid
* **Temporal Scope:** Raw data extracted for Year 2020; dynamically filtered via MLOps pipeline to **August 2020** (High-volatility summer month).
* **Resolution:** Hourly

### Active Variables (Environment State Space)
The raw dataset contains 30+ meteorological columns. To optimize the Reinforcement Learning pipeline, the state space has been mathematically reduced to the following core features:

| Feature Name | Unit | Description | Mathematical Purpose in Simulation |
| :--- | :--- | :--- | :--- |
| **GHI** | $W/m^2$ | Global Horizontal Irradiance | The primary driver of solar generation. Represents the total thermodynamic energy available for the "Smart Battery Nodes" to absorb. |
| **DNI** | $W/m^2$ | Direct Normal Irradiance | Secondary solar metric (direct beam radiation). |
| **DHI** | $W/m^2$ | Diffuse Horizontal Irradiance | Tertiary solar metric (scattered light). |
| **Temperature** | Celsius | Ambient Surface Temperature | Used as an environmental penalty variable. High temperatures increase battery degradation during charge/discharge cycles. |
| **Wind Speed** | $m/s$ | Surface Wind Velocity | Acts as a proxy variable for decentralized wind turbine generation across the node. |

---

## Data Preprocessing & MLOps Pipeline
**Data Governance Note:** Initial NREL metadata rows must be programmatically stripped, and temporal features (`Year`, `Month`, `Day`, `Hour`, `Minute`) must be merged into a single `timestamp` index. This ensures strict chronological alignment with the secondary ERCOT Human Demand dataset.

The following Python/Pandas script serves as the Phase 1 ingestion pipeline. It ingests the raw NREL 2020 data, isolates the August testing sandbox, ruthlessly drops redundant meteorological features, and outputs the clean Environment State. I used kaggle notebook for the purpsoe of easeness to clean the data I downloaded

```python
import pandas as pd

def process_nrel_environment(file_path):
    """
    Ingests and cleans raw NREL NSRDB data for the Swarm Environment.
    """
    # 1. Load the raw 2020 dataset 
    # (skiprows=2 bypasses the NREL metadata rows to grab actual column headers)
    df = pd.read_csv(file_path, skiprows=2)

    # 2. Filter strictly for August (Month == 8) to create our Phase 1 Sandbox
    august_df = df[df['Month'] == 8].copy()

    # 3. Ruthlessly cut unwanted columns. Keep only thermodynamic and temporal data.
    columns_to_keep = ['Year', 'Month', 'Day', 'Hour', 'Minute', 
                       'GHI', 'DNI', 'DHI', 'Temperature', 'Wind Speed']
    clean_env_df = august_df[columns_to_keep]

    # 4. Create a unified DateTime index for MLOps alignment
    clean_env_df['timestamp'] = pd.to_datetime(clean_env_df[['Year', 'Month', 'Day', 'Hour', 'Minute']])
    clean_env_df.set_index('timestamp', inplace=True)

    # Drop the raw time columns as they are now mathematically redundant
    clean_env_df.drop(columns=['Year', 'Month', 'Day', 'Hour', 'Minute'], inplace=True)

    return clean_env_df

# Execute the pipeline
if __name__ == "__main__":
    raw_file = '744683_29.41_-94.90_2020.csv'
    environment_df = process_nrel_environment(raw_file)
    
    # Export the clean, localized Environment State
    output_filename = 'TexasCity_August2020_Environment.csv'
    environment_df.to_csv(output_filename)
    
    print(f"MLOps Pipeline Success. Environment file saved as {output_filename}")
***
