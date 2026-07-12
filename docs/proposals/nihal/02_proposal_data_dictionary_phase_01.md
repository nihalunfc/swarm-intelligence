# Phase 1: Energy Grid Optimization (Nihal)

## Project Overview
This repository contains the architectural foundation, data engineering pipeline, and simulation framework for the "Energy Grid Optimization" capstone project. 

This project utilizes an **Agent-Based Swarm Modeling** approach to solve the problem of decentralized grid balancing. By utilizing Multi-Agent Reinforcement Learning (MARL), independent nodes (Smart Battery Agents) learn to autonomously route energy to mitigate volatility in renewable generation.

## Data Governance & Architecture
The foundation of this project is a synchronized, multivariate time-series environment. We have integrated two primary sources to create a "Virtual Power Plant" sandbox.

### 1. Primary Data Source: NREL (Weather/Generation)
* **Description:** High-resolution meteorological and irradiance data.
* **Metrics:** GHI, DNI, DHI, Temperature, and Wind Speed.
* **Source:** [National Solar Radiation Database (NSRDB)](https://nsrdb.nrel.gov/)

### 2. Secondary Data Source: ERCOT (Human Demand)
* **Description:** Historical electricity load (demand) data for the Texas Coast (COAST) weather zone.
* **Metrics:** Native Load (MW) at hourly intervals.
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

## MLOps Data Pipeline (ETL Logic)
This pipeline synchronizes the disparate NREL and ERCOT datasets into a mathematically aligned environment.

```python
import pandas as pd

# 1. Load Datasets
weather_df = pd.read_csv('phase_01_rawdata.csv')
ercot_raw = pd.read_excel('Native_Load_2020.xlsx')

# 2. Scrub & Normalize
# Handle ERCOT quirks (DST tags and 24:00 time formats)
ercot_raw['HourEnding'] = ercot_raw['HourEnding'].astype(str).str.replace(' DST', '')
ercot_raw['HourEnding'] = pd.to_datetime(ercot_raw['HourEnding'])

# 3. Aggregate & Merge
# Grouping NREL data by hour to ensure 1-to-1 temporal alignment
weather_agg = weather_df.groupby('timestamp').mean()
master_df = weather_agg.merge(
    ercot_raw[['HourEnding', 'COAST']], 
    left_on='timestamp', right_on='HourEnding'
).rename(columns={'COAST': 'demand_mw'})

# 4. Final Output
master_df.to_csv('phase_01_master_environment.csv', index=False)
