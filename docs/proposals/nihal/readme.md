# Nihal's Capstone Proposal: Agent-Based Swarm Modeling

This directory contains the draft proposal, data dictionaries, and initial raw data extractions for **Phase 1: Energy Grid Optimization**. 

## Directory Index

| File Name | Description | Status |
| :--- | :--- | :--- |
| `02_phase_01_proposal_nihal.md` | [MAIN] The comprehensive, CRISP-DM compliant capstone project proposal. | Draft Complete |
| `02_phase_01_proposal_laymans.md` | The Layman's guide of proposal - a simpler version to understand the core of the proposal | Draft Complete |
| `02_proposal_data_dictionary_phase_01.md` | Data dictionary detailing the NREL environmental variables and the Pandas extraction code. | Complete |
| `phase_01_sample_rawdata.csv` | The raw historical solar/wind dataset extracted from the NREL database (Texas City, 2020). | Complete |
| `phase_01_sample_segmented.csv` | The lightweight, segmented dataset (August 2020) processed via Pandas for the MLOps pipeline. | Complete |
| `phase_01_sample_master_environment.csv` | The finalized, merged dataset containing continuous hourly NREL weather and ERCOT human demand for August 2020 (744 rows). | **Complete** |

## Project Scope
This proposal is strictly scoped for the roughly 11-week capstone timeline. It relies entirely on original, primary time-series data from the National Renewable Energy Laboratory (NREL) to build a multi-agent reinforcement learning simulation of decentralized energy routing.
