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

**Data Governance Note:** Initial NREL metadata rows have been programmatically stripped, and temporal features (`Year`, `Month`, `Day`, `Hour`, `Minute`) have been merged into a single `timestamp` index to ensure strict chronological alignment with the secondary ERCOT Human Demand dataset.
