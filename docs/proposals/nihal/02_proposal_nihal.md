# Capstone Project Proposal: Agent-Based Swarm Modeling for Dynamic Network Optimization
## Proposal Number : 2

**Course:** DAMO-699-1: Summer 2026 Capstone Project  \
**Supervisor:** Professor Mehdi Mostofi  \
**Methodology:** CRISP-DM Framework with MLOps Data Streaming  \
**Timeline Constraint:** 11 Weeks (July 6 - September)  

---

## 1. Problem Statement
Traditional macro-systems frequently rely on top-down, centralized predictive models that struggle to adapt to the dynamic, high-frequency volatility and shifting parameters of complex environments. As global infrastructures and analytical domains transition toward a decentralized era, there is a critical need for localized, autonomous resource routing and decision-making. 

This project proposes an Agent-Based Swarm Modeling approach. Instead of relying purely on a central predictive algorithm, independent nodes will operate under localized reinforcement learning rules to collectively balance, optimize, and map the broader system. This localized "swarm intelligence" presents a highly scalable alternative to traditional macro-level predictive modeling. 

For this capstone, the swarm architecture will be applied to one of the following primary domains:
1. **Astrophysics & Cosmological Modeling:** Coordinating satellite cluster telemetry or meteorite predictions utilizing primary NASA/NOAA datasets.
2. **Energy Grid Optimization:** Simulating smart battery nodes to route power dynamically based on high-frequency renewable energy generation (NREL data).
3. **Autonomous Logistics & Military Applications:** Decentralized routing algorithms for drone fleets or supply chains in unpredictable physical environments.
4. **Biological & Natural Emergent Phenomena:** Modeling localized rules generating macro-level biological structures to predict massive ecosystem shifts.
5. **Quantitative Finance:** Modeling liquidity flows and independent algorithmic trading bots executing decentralized arbitrage across volatile market data.

## 2. Project Objectives
The primary objectives of this capstone project are to:
1. **Establish a Predictive Baseline:** Develop traditional, centralized machine learning models (e.g., Time-Series Forecasting, Random Forest) to serve as a benchmark for system optimization.
2. **Develop an Agent-Based Model (ABM):** Engineer an Object-Oriented ABM environment where independent nodes utilize localized Q-Learning policies.
3. **Evaluate Swarm Efficacy:** Mathematically compare the performance, latency, and stability of the decentralized swarm against the traditional predictive baseline.
4. **Deploy a Real-Time Pipeline:** Construct an MLOps data pipeline using Python generator functions to sequentially stream historical data to the agents, mimicking a live environment.
5. **Develop an Interactive Dashboard:** Build a comprehensive visual interface to monitor the swarm's real-time decision-making and aggregate system health.

## 3. Research Questions
* **Primary Question:** Can a decentralized, multi-agent reinforcement learning (MARL) swarm architecture successfully optimize resource allocation and balance systemic loads within a simulated dynamic network better than traditional, centralized static baseline models?
* **Secondary Question 1 (Emergent Stability):** To what extent do localized reinforcement learning rules applied to independent nodes result in macro-level system stability when subjected to sudden environmental or market constraints?
* **Secondary Question 2 (Adaptability & MLOps):** How effectively can Python-based generator functions simulate a live MLOps data streaming environment to test the swarm's real-time adaptability to sudden data anomalies?

## 4. Hypotheses 
Depending on the final dataset secured, the project will validate the overarching theory against one of the following specific domain constraints: 

* **Astrophysics & Cosmological Modeling:** * **$H_A$:** A decentralized swarm utilizing localized kinetic constraints will maintain orbital stability with a lower Mean Squared Error (MSE) than centralized deterministic trajectories.
* **Quantitative Finance:**
  * **$H_A$:** Independent trading agents will result in a faster stabilization of liquidity variance ($\sigma^2$) during market shocks compared to top-down macroeconomic baseline models.
* **Autonomous Logistics:**
  * **$H_A$:** Swarm agents will autonomously reroute logistics subject to random structural shocks, minimizing total system latency ($\sum \Delta t$) more effectively than centralized routing algorithms.
* **Biological & Natural Emergent Phenomena:**
  * **$H_A$:** Agent-Based Models will predict environmental tipping points with higher classification accuracy (F1-Score) than top-down statistical ecosystem models.
* **Energy Grid Optimization:**
  * **$H_A$:** Decentralized "Smart Battery Nodes" will route energy loads and reduce simulated grid failure rates significantly better than centralized, static load-balancing baselines.

*(Note: The Null Hypothesis ($H_0$) for all domains dictates that the decentralized swarm architecture will yield no statistically significant improvement over traditional centralized predictive baselines).*

## 5. Methodology
This project strictly adheres to the CRISP-DM lifecycle.

### 5.1 Data Collection 
To maintain strict academic integrity, this project will rely exclusively on primary, original datasets. No synthetic data (e.g., Faker) or third-party aggregators (e.g., Kaggle) will be utilized. Data will be sourced directly from verifiable institutions (e.g., NREL, NASA, SEC, FRED) and must include rigorous data dictionaries.

### 5.2 Data Preparation
The raw time-series data will undergo robust preprocessing using Pandas:
* **Missing Value Imputation:** Handling NaNs inherently found in physical sensor or market data using forward-fill or rolling averages.
* **Temporal Alignment:** Precise timestamp formatting to allow for sequential streaming during the MLOps deployment phase.
* **Normalization:** Scaling continuous variables to ensure stable convergence during reinforcement learning training.

### 5.3 Potential Features
While dependent on the final dataset, the core features extracted for model training will generally include:
* **Temporal Data:** `Timestamp`, `Interval_ID`, `Seasonality_Index`
* **Node Status Variables:** `Current_Capacity`, `Local_Demand`, `Node_Health`
* **Environmental/External Constraints:** `Weather_Variability`, `Market_Volatility_Index`, `Spatial_Coordinates (X, Y)`
* **Target/Reward Variable:** `System_Failure_Flag`, `Latency_Score`, `Resource_Deficit`

### 5.4 Predictive Modeling & Baseline Establishment
Before deploying the swarm, traditional predictive modeling will be utilized to establish a benchmark:
* **Time-Series Forecasting:** ARIMA or Prophet models will be trained on historical data to predict macro-level system loads.
* **Classification Models:** Random Forest and Logistic Regression algorithms will be used to predict the likelihood of system failures (e.g., grid overloads, market crashes) based on centralized data. 
* **The Goal:** These traditional models represent the "status quo." The swarm must demonstrably beat their performance metrics to prove the thesis.

### 5.5 Agent Architecture & Mathematical Framework (ABM)
The core simulation will transition from top-down machine learning to bottom-up decentralized node logic:
* **Agent Architecture (OOP):** Agents will be programmed using Python Object-Oriented Programming to represent localized nodes.
* **Environment Simulation:** The Python library `Mesa` will manage the 2D spatial/temporal environment and schedule agent actions (ticks).
* **Markov Decision Process (MDP):** The environment is evaluated using the Bellman equation:
  $$V(s)=\max_a\left(R(s,a)+\gamma\sum_{s'}P(s'|s,a)V(s')\right)$$
* **Reinforcement Learning:** Agents will dynamically update their local knowledge bases via the model-free Q-Learning state-action update equation:
  $$Q(s,a)\leftarrow Q(s,a)+\alpha\left(R(s,a)+\gamma\max_{a'}Q(s',a')-Q(s,a)\right)$$

## 6. Model Evaluation
The performance of the agent-based swarm will be rigorously quantified against the traditional predictive baseline models using the following metrics:
* **Mean Squared Error (MSE) / Root Mean Squared Error (RMSE):** Used to measure the deviation of the swarm's resource allocation against the optimal theoretical allocation.
* **Classification Metrics:** Precision, Recall, and F1-Score will be used to evaluate how successfully the swarm prevented discrete system failures (e.g., preventing a grid blackout) compared to the Random Forest baseline.
* **Cumulative Reward Convergence:** Tracking the reinforcement learning training curve to prove mathematical convergence and ensure agents are not acting randomly.
* **System Survival Rate / Latency:** Measuring the macro-level stability of the system (e.g., total uptime, flow efficiency) across the duration of the simulation.

## 7. Dashboard Development 
The analytical output will culminate in an interactive dashboard (e.g., utilizing Power BI, Streamlit, or Plotly Dash). The dashboard will feature:
* **Simulation Visualizer:** A 2D spatial mapping of the Mesa grid, showing agents changing states, routing resources, or moving in real-time.
* **Live KPI Trackers:** Dynamic readouts of System Health, Active Nodes, and Resource Deficits.
* **Comparative Analytics:** Side-by-side visual graphs comparing the Swarm's real-time optimization curve against the Centralized Baseline predictions.

## 8. Expected Deliverables
By the conclusion of the 11-week timeline, the team will deliver:
1. **Cleaned Primary Dataset:** The processed, temporally aligned dataset complete with a formal data dictionary.
2. **Python Codebase:** Fully commented Object-Oriented code containing the predictive baselines, the Mesa environment, and the Q-Learning agent logic.
3. **Interactive Dashboard:** A deployable visual interface showcasing the results.
4. **APA Formatted Final Report (60%):** A comprehensive academic paper detailing the methodology, data analysis, mathematical proofs, and actionable business insights.
5. **Poster Presentation (10%):** A summarized visual defense of the capstone project.

## 9. Project Timeline & Agile Constraints
This execution is ruthlessly scoped to validate the architecture within a strictly defined 11-week academic timeline.

* **Sprint 1 (Weeks 1-2):** Group Formation, TCPS 2 Certification, Proposal Submission (10%).
* **Sprint 2 (Weeks 3-4):** Primary Data Ingestion and Pandas Pipeline Construction.
* **Sprint 3 (Weeks 5-7):** Baseline Predictive Modeling & Object-Oriented Agent Programming.
* **Sprint 4 (Week 8):** Swarm Evaluation against Historical Baselines.
* **Sprint 5 (Week 9):** MLOps Sequential Data Streaming and Dashboard Finalization.
* **Sprint 6 (Week 10):** Final APA Report (60%) and Poster Presentation (10%) Delivery.
* **Sprint 7 (Week 11):** Individual Reflection Paper (20%).

---

## Appendix: Post-Capstone Abstract Generalization (Future Scope)
*Note: The following outlines post-graduate research scalability and is explicitly outside the boundaries and scope of the 11-week capstone project.*

The core objective of the initial capstone is to prove the efficacy of localized, decentralized routing on a single, specific dataset. However, the mathematical equations governing the Markov Decision Process (MDP) and Q-Learning policies are domain-agnostic. 

In future research phases (Phase 2 and Phase 3), this foundational architecture is intended to be abstracted into a **Generalized Theory of Dynamic Networks**. Once the ABM proves it can efficiently route physical resources (like energy or logistics) across a grid, those exact same differential equations can be abstracted to route non-physical resources—such as capital across a decentralized financial network, or telemetry data across a satellite cluster. The ultimate goal of this extended research is the formulation of a universal "swarm intelligence" algorithm capable of automatically stabilizing any decentralized macro-system, culminating in peer-reviewed academic publication.
