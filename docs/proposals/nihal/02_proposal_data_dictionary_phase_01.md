# Phase 1: Energy Grid Optimization (Nihal)

## Project Overview
This repository contains the architectural foundation, data engineering pipeline, and simulation framework for the "Energy Grid Optimization" capstone project. 

This project utilizes an **Agent-Based Swarm Modeling** approach to solve the problem of decentralized grid balancing. By utilizing Multi-Agent Reinforcement Learning (MARL), independent nodes (Smart Battery Agents) learn to autonomously route energy to mitigate volatility in renewable generation.

## Data Governance & Architecture
The foundation of this project is a synchronized, multivariate time-series environment. We have integrated two primary sources to create a "Virtual Power Plant" sandbox.

### 1. Primary Data Source: NREL (Solar & Wind)
* **Description:** High-resolution meteorological and irradiance data.
* **Metrics:** GHI (Global Horizontal Irradiance), DNI, DHI, Temperature, and Surface Wind Speed.
* **Source:** [National Solar Radiation Database (NSRDB)](https://nsrdb.nrel.gov/)

### 2. Secondary Data Source: ERCOT (Human Demand)
* **Description:** Historical electricity load (demand) data for the Texas Coast (COAST) weather zone.
* **Metrics:** Native Load (MW) at hourly intervals.
* **Source:** [ERCOT Hourly Load Data Archives](https://www.ercot.com/gridinfo/load/load_hist)

---

## Data Dictionary
| Variable | Unit | Description |
| :--- | :--- | :--- |
| `timestamp` | YYYY-MM-DD HH:MM | Standardized hourly index |
| `GHI` | $W/m^2$ | Global Horizontal Irradiance |
| `DNI` | $W/m^2$ | Direct Normal Irradiance |
| `DHI` | $W/m^2$ | Diffuse Horizontal Irradiance |
| `Temperature` | °C | Ambient surface temperature |
| `Wind Speed` | m/s | Surface wind velocity |
| `demand_mw` | MW | Human load requirement in COAST zone |

---

## Pipeline Execution Status
| Milestone | Status | Artifact |
| :--- | :--- | :--- |
| NREL Ingestion | Complete | `phase_01_rawdata.csv` |
| ERCOT Ingestion | Complete | `Native_Load_2020.csv` |
| Temporal Alignment | Complete | `phase_01_master_environment.csv` |
| Swarm Environment | Pending | `Agent_Simulation_v1` |

## MLOps Data Pipeline (ETL Logic)
The following Python logic is used to synchronize the disparate datasets into a mathematically aligned environment:

```python
# MLOps Pipeline: Syncing NREL (Weather) and ERCOT (Demand)
import pandas as pd

# 1. Load Datasets
weather_df = pd.read_csv('nrel_data.csv', skiprows=2)
load_df = pd.read_csv('Native_Load_2020.csv')

# 2. Sanitize and Align
# Convert timestamps, strip 'DST' anomalies, and round to nearest hour
weather_df['timestamp'] = pd.to_datetime(weather_df['Time'])
load_df['HourEnding'] = pd.to_datetime(load_df['HourEnding'].str.replace(' DST', ''))

# 3. Temporal Aggregation & Merge
# Mean-aggregation to ensure 1-to-1 relationship per hour
master_df = weather_df.groupby('timestamp').mean().merge(
    load_df, left_on='timestamp', right_on='HourEnding'
)

# 4. Export
master_df.to_csv('phase_01_master_environment.csv', index=False)
