# Capstone Project Proposal: Agent-Based Swarm Modeling for Decentralized Energy Grid Optimization

**Team Members:** Nihal, Kanishka, Swati, Priya 
**Course:** DAMO-699-1: Summer 2026 Capstone Project 
**Supervisor:** Professor Mehdi Mostofi 
**Methodology:** CRISP-DM Framework with MLOps Data Streaming 
**Timeline Constraint:** 11 Weeks (July 6 - September) 

---

## 1. Problem Statement (Business Understanding)
Traditional energy grids rely on top-down, centralized optimization models that struggle to adapt to the dynamic, high-frequency volatility of renewable energy sources and shifting consumer demands. As the global infrastructure transitions toward a decentralized energy era, there is a critical need for localized resource routing. This project proposes an Agent-Based Swarm Modeling approach, where independent nodes operate under localized reinforcement learning rules to collectively balance grid loads. This localized "swarm intelligence" presents a highly scalable alternative to traditional macro-level predictive modeling and sets a foundational architectural framework applicable to broader dynamic networks.

## 2. Research Questions
* **Primary:** Can a decentralized, multi-agent reinforcement learning (MARL) swarm architecture successfully optimize resource allocation and balance supply/demand loads within a simulated energy grid using historical meteorological and generation data better than traditional, centralized static baseline models? 
* **Secondary:** How effectively can Python-based generator functions simulate a live MLOps data streaming environment to test the swarm's real-time adaptability to sudden weather or demand anomalies? 

## 3. Hypothesis
By modeling an energy network as a Markov Decision Process (MDP) and applying localized Q-Learning algorithms to independent agents , the emergent swarm behavior will autonomously route energy efficiently, mitigating simulated grid overloads and shortages.

## 4. Data Collection Strategy
To maintain strict academic integrity and comply with syllabus requirements, this project will rely exclusively on primary, original datasets. No synthetic data or third-party aggregators will be utilized.

* **Primary Source:** National Renewable Energy Laboratory (NREL).
* **Data Type:** Historical, highly granular time-series data detailing 5-minute interval solar/wind generation and regional power demand.
* **Validation & Schema:** The selected NREL datasets include world-class, government-mandated metadata and rigorous data dictionaries to explicitly map all features.

## 5. Data Preparation & Exploratory Data Analysis (EDA)
Following the CRISP-DM lifecycle, the raw NREL time-series data will undergo robust preprocessing:
* **Data Cleaning:** The NREL time-series data will be cleaned, formatted, and loaded into Pandas DataFrames to remove anomalies and handle missing values.
* **Temporal Alignment:** Ensuring precise timestamp formatting to allow for sequential streaming during the deployment phase.
* **EDA Visualizations:** Initial statistical analysis to map historical baseline load failures, providing the benchmark against which the swarm's performance will be evaluated.

## 6. Modeling Methodology (Architecture & Mathematics)
The core of this capstone relies on transitioning from top-down machine learning to bottom-up decentralized node logic.

* **Agent Architecture (OOP):** Agents will be programmed using Python Object-Oriented Programming (OOP) to represent localized "Smart Battery Nodes".
* **Environment Simulation:** The Python library Mesa will be utilized to construct the spatial and temporal environment (the grid) and manage the scheduling of agent actions (ticks).
* **Mathematical Framework (MDP):** The decision-making environment will be governed by a Markov Decision Process (MDP). The fundamental variables include State Space ($S$), Action Space ($A$), Transition Probability ($P$), and a localized Reward Function ($R$) . The environment is evaluated using the Bellman equation:
  $$V(s) = \max_a \left( R(s, a) + \gamma \sum_{s'} P(s' | s, a) V(s') \right)$$
* **Reinforcement Learning:** The agents will learn optimal routing policies using a model-free Q-Learning algorithm. They will dynamically update their local knowledge bases via the state-action update equation:
  $$Q(s, a) \leftarrow Q(s, a) + \alpha \left( R(s, a) + \gamma \max_{a'} Q(s', a') - Q(s, a) \right)$$

## 7. Model Evaluation
The swarm's intelligence will be validated by comparing the agents' collective grid efficiency and stability (reward output) against the historical baseline averages of the unoptimized NREL data. 

## 8. Deployment, MLOps, & Dashboarding
To fulfill the secondary syllabus requirement of incorporating MLOps elements , the architecture will simulate a live, dynamic production environment.
* **Data Streaming:** Instead of training the model statically, Python generator functions (`yield`) will stream the highly granular historical NREL data sequentially to the agents. This pipeline mimics a real-time weather and energy market.
The project will culminate in a final dataset, actionable recommendations, and a formal dashboard/poster summarizing the derived insights and swarm performance metrics.

## 9. Project Timeline & Constraints
This execution acts as a highly scoped Phase 1 to validate the architecture within a strictly defined 11-week academic timeline.

* **Weeks 1-2:** Group Formation, Proposal Submission (10%), TCPS 2 Certification.
* **Weeks 3-4:** NREL Data Ingestion and Pandas Pipeline Construction.
* **Weeks 5-7:** Object-Oriented Agent Programming and Q-Learning Model Training.
* **Week 8:** Swarm Evaluation against Historical Baselines.
* **Week 9:** MLOps Sequential Data Streaming and Dashboard Finalization.
* **Week 10:** Final APA Report (60%) and Poster Presentation (10%) Delivery.
* **Week 11:** Individual Reflection Paper (20%).

