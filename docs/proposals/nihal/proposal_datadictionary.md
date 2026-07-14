# Phase 1: Energy Grid Optimization - Data Dictionary

## 1. Project Overview & Data Architecture
This document outlines the data governance and mapping for the "Energy Grid Optimization" capstone project. By utilizing Multi-Agent Reinforcement Learning (MARL), independent nodes (Smart Battery Agents) learn to autonomously route energy to mitigate volatility in renewable generation. 

The data architecture is strictly reproducible, relying entirely on the provided scripts (`data_ingestion_nrel.py`, `data_ingestion_ercot.py`, `data_merge.py`) within the repository to transform the raw files into the final state-space matrix.

## 2. Primary Data Sources & Authenticity
To ensure academic rigor and pristine data governance, we use 100% original, primary-source datasets:

* **Weather & Solar Irradiance:** National Renewable Energy Laboratory (NREL) National Solar Radiation Database.
    * **Source Link:** [NSRDB Viewer](https://nsrdb.nrel.gov/](https://nsrdb.nlr.gov/data-viewer)
    * **Raw File:** `nrel_rawdata.csv`
    * **Processing Script:** `data_ingestion_nrel.py`
    * **Cleaned Output:** `nrel_cleaned.csv`
* **Human Energy Demand:** Electric Reliability Council of Texas (ERCOT) Hourly Native Load.
    * **Source Link:** [ERCOT Hourly Load Archives](https://www.ercot.com/gridinfo/load/load_hist)
    * **Raw File:** `ercot_rawdata.xlsx`
    * **Processing Script:** `data_ingestion_ercot.py`
    * **Cleaned Output:** `ercot_cleaned.csv`

---

## 3. Dataset Mapping & Taxonomy

The synthesis engine (`data_merge.py`) fuses the cleaned datasets using a strict inner merge on a synthesized **Connecting Label**. The three tables below illustrate the lineage of each data point from its raw state to the final merged matrix.

### Table A: ERCOT Extraction Map
*Extracted via `data_ingestion_ercot.py`*

| Raw Label (`ercot_rawdata.xlsx`) | Intermediate Label (`ercot_cleaned.csv`) | Purpose / Transformation |
| :--- | :--- | :--- |
| `HourEnding` | **`Timestamp`** (Connecting Label) | Scrubbed "24:00" & DST anomalies; converted to unified standard datetime. |
| `COAST` | `ERCOT_COAST_Load_MW` | Isolated target region; standardized naming. |
| *(All other zones)* | *Dropped* | Filtered out to maintain strict COAST scope. |

### Table B: NREL Extraction Map
*Extracted via `data_ingestion_nrel.py`*

| Raw Label (`nrel_rawdata.csv`) | Intermediate Label (`nrel_cleaned.csv`) | Purpose / Transformation |
| :--- | :--- | :--- |
| `Year`, `Month`, `Day`, `Hour`, `Minute` | **`Timestamp`** (Connecting Label) | Reconstructed into unified datetime; 30-min offset floored to top-of-hour. |
| `GHI` | `NREL_GHI_W_m2` | Standardized Global Horizontal Irradiance metric. |
| `DNI` | `NREL_DNI_W_m2` | Standardized Direct Normal Irradiance metric. |
| `DHI` | `NREL_DHI_W_m2` | Standardized Diffuse Horizontal Irradiance metric. |
| `Temperature` | `NREL_Temperature_C` | Standardized ambient surface temperature. |
| `Wind Speed` | `NREL_Wind_Speed_m_s` | Standardized surface wind velocity. |

### Table C: Master Merged Data Dictionary
*Fused via `data_merge.py` into `sample_merged_dataset.csv`*

| Final Matrix Label | Unit | Source Origin | Description |
| :--- | :--- | :--- | :--- |
| **`Timestamp`** | YYYY-MM-DD HH:MM | **Connecting Label** | Perfect hourly temporal alignment matching both subsets. |
| `NREL_GHI_W_m2` | $W/m^2$ | NREL | Global Horizontal Irradiance |
| `NREL_DNI_W_m2` | $W/m^2$ | NREL | Direct Normal Irradiance |
| `NREL_DHI_W_m2` | $W/m^2$ | NREL | Diffuse Horizontal Irradiance |
| `NREL_Temperature_C` | **°C** | NREL | Ambient surface temperature |
| `NREL_Wind_Speed_m_s` | **m/s** | NREL | Surface wind velocity |
| `ERCOT_COAST_Load_MW` | **MW** | ERCOT | Human load requirement (COAST zone) |
