# Phase 1: Energy Grid Optimization (Nihal)

## Project Overview
This repository contains the architectural foundation, data engineering pipeline, and simulation framework for the "Energy Grid Optimization" capstone project. 

This project utilizes an **Agent-Based Swarm Modeling** approach to solve the problem of decentralized grid balancing. By utilizing Multi-Agent Reinforcement Learning (MARL), independent nodes (Smart Battery Agents) learn to autonomously route energy to mitigate volatility in renewable generation.

## Data Governance & Architecture
The foundation of this project is a synchronized, multivariate time-series environment.

### 1. Primary Data Source: NREL (Weather/Generation)
* **Description:** High-resolution meteorological and irradiance data.
* **Source:** [National Solar Radiation Database (NSRDB)](https://nsrdb.nrel.gov/)

### 2. Secondary Data Source: ERCOT (Human Demand)
* **Description:** Historical electricity load (demand) data for the Texas Coast (COAST) weather zone.
* **Source:** [ERCOT Hourly Load Data Archives](https://www.ercot.com/gridinfo/load/load_hist)

---

## Data Dictionary
| Variable | Unit | Source | Description |
| :--- | :--- | :--- | :--- |
| `timestamp` | YYYY-MM-DD HH:MM | Sync | Standardized hourly index |
| `GHI` | $W/m^2$ | NREL | Global Horizontal Irradiance |
| `DNI` | $W/m^2$ | NREL | Direct Normal Irradiance |
| `DHI` | $W/m^2$ | NREL | Diffuse Horizontal Irradiance |
| `Temperature` | °C | NREL | Ambient surface temperature |
| `Wind Speed` | m/s | NREL | Surface wind velocity |
| `demand_mw` | MW | ERCOT | Human load requirement (COAST zone) |

---

## Data Management Pipeline (`data_ingestion.py`)
Use this script to transform raw CSV/XLSX exports into the `phase_01_master_environment.csv` file required for model training.

```python
import pandas as pd
import os

def ingest_data():
    # 1. Load Raw NREL Data
    # Assumes file is in raw_data/ directory
    weather_df = pd.read_csv('raw_data/nrel_2020.csv', skiprows=2)
    weather_df['timestamp'] = pd.to_datetime(weather_df['Time'])
    
    # 2. Load Raw ERCOT Data
    # Assumes file is in raw_data/ directory
    ercot_df = pd.read_excel('raw_data/native_load_2020.xlsx')
    
    # Clean ERCOT data: Remove 'DST' tags and convert to datetime
    ercot_df['HourEnding'] = ercot_df['HourEnding'].astype(str).str.replace(' DST', '')
    ercot_df['HourEnding'] = pd.to_datetime(ercot_df['HourEnding'])
    
    # 3. Synchronize Datasets
    # Aggregate NREL to hourly, then merge on timestamp
    weather_agg = weather_df.groupby('timestamp').mean()
    
    master_df = weather_agg.merge(
        ercot_df[['HourEnding', 'COAST']], 
        left_on='timestamp', 
        right_on='HourEnding'
    ).rename(columns={'COAST': 'demand_mw'})
    
    # 4. Save Master Environment
    if not os.path.exists('processed'):
        os.makedirs('processed')
    master_df.to_csv('processed/phase_01_master_environment.csv', index=False)
    print("ETL Process Complete: master_environment.csv generated.")

if __name__ == "__main__":
    ingest_data()
