# Swarm Intelligence: Decentralized Resource Optimization Framework

## Project Overview
This repository contains the architecture and simulation pipeline for a Decentralized Resource Optimization Framework, currently applied to energy grid balancing using Multi-Agent Reinforcement Learning (MARL)[cite: 2244, 2186]. [cite_start]The system models autonomous agents (e.g., smart buildings, microgrids) that independently negotiate and adjust their load based on dynamic pricing and supply signals. 

While tested on electrical grid data, the underlying swarm logic is scalable and designed to resolve complex, unpredictable supply-and-demand logistics across various sectors, including hospitality, telecommunications, and autonomous staffing.

## Research Objectives
1. **Grid Balancing:** Can decentralized battery agents autonomously mitigate renewable volatility?
2. **Scalability:** Does this MARL architecture maintain stability as nodes are added? 
3. **Virtual Determinism:** Can we transform stochastic renewable supply into a predictable, load-balanced output? 

## Phase 1: Environment Synthesis Pipeline

Phase 1 focuses exclusively on establishing a mathematically locked environment. [cite_start]By integrating high-resolution meteorological data (NREL) with regional human electricity demand (ERCOT), we create the state-space matrix necessary to train the autonomous agents.

### Data Governance & Sources

| Source | Type | URL |
| :--- | :--- | :--- |
| NREL | Weather/Generation | [NSRDB Database](https://nsrdb.nrel.gov/) |
| ERCOT | Human Demand | [ERCOT Hourly Load Data](https://www.ercot.com/) |

### Data Dictionary

| Variable | Unit | Source | Description |
| :--- | :--- | :--- | :--- |
| timestamp | YYYY-MM-DD HH | Sync | [cite_start]Hourly temporal index  |
| GHI | W/m² | NREL | [cite_start]Global Horizontal Irradiance  |
| DNI | W/m² | NREL | [cite_start]Direct Normal Irradiance |
| DHI | W/m² | NREL | [cite_start]Diffuse Horizontal Irradiance  |
| Temperature | °C | NREL | [cite_start]Ambient surface temperature  |
| Wind Speed | m/s | NREL | Local wind velocity |
| demand_mw | MW | ERCOT | [cite_start]Native load (COAST zone)  |

### Technical Architecture

[cite_start]The data pipeline utilizes a Separation of Concerns approach, isolating raw data extraction from environment synthesis[cite: 2314, 2315].

**1. `data_ingestion.py` (ETL Layer)**
Handles raw file cleaning and temporal standardization.It features custom logic to sanitize ERCOT's specific formatting anomalies (e.g., stripping daylight saving "DST" tags and remapping "24:00" midnight markers to "00:00"). It also utilizes aggressive `.dt.floor('h')` rounding to bypass Pandas' native Banker's Rounding bugs during hourly weather aggregation.

**2. `pipeline_engine.py` (Synthesis Layer)**
The execution engine that merges the cleaned NREL and ERCOT data into the state-space matrix. It strips hidden timezone markers and executes an inner join strictly on the timestamp.

**System Verification**
The pipeline includes a fail-safe sequence. [cite_start]If the merged output does not hit exactly 744 synchronized rows (representing every hour of August), the pipeline aborts, preventing corrupted state-space matrices from reaching the reinforcement learning agents.
