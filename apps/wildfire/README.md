# The Wildfire Suppressor: Multi-Agent Drone Swarm

**Build with AI: Innovation Challenge 2026**
*GDG on Campus – University of Niagara Falls Canada*

## Overview
The Wildfire Suppressor is a decentralized, **WARL (Wildfire Autonomous Reinforcement Learning)** drone swarm designed to autonomously contain and manage extreme wildfires. By treating the spread of a wildfire as a dynamic mathematical curve, our AI swarm learns to route autonomous drones to drop fire retardant at highly optimized "choke points," effectively flattening the curve of the fire's growth.

This project tackles a critical Canadian and global crisis—underfunded and inefficient wildfire management—by replacing reactive human coordination with proactive, autonomous swarm intelligence.

## Documentation & Explanation Guides
Please refer to our interactive notebooks for a complete breakdown of the project architecture and simulation logic:
1. [01_Problem_Statement_and_Methodology.ipynb](./notebooks/01_Problem_Statement_and_Methodology.ipynb) - Project theory, MDP architecture, and technology stack.
2. [02_DQN_Wildfire_Training.ipynb](./notebooks/02_DQN_Wildfire_Training.ipynb) - The live generative environment (physics engine) and AI training logic.

## Repository Structure
```
GDGCHackathon2026/
├── src/                # Core Python source code for the Swarm RL Environment
├── notebooks/          # Jupyter notebooks for training the Deep Q-Network and visualizing convergence
├── docs/               # GitHub Pages front-end UI (HTML/JS) and Live Dashboard
└── README.md           # Project overview and setup instructions
```

## Technologies Used
- **Google Cloud Platform:** For robust backend hosting and simulation scaling.
- **Leaflet.js & Esri:** For high-performance, real-time Satellite Imagery mapping over Canadian forests.
- **Google Gemini API:** An interactive "Swarm Commander" chatbot that allows users to query the AI (e.g., "Why did the swarm route North?") and receive plain-English explanations of the Swarm's mathematical logic.
- **PyTorch (Gymnasium):** Custom Deep Q-Network for the Wildfire Autonomous Reinforcement Learning (WARL) engine.

## The GDG Innovation Challenge Roadmap
- [x] **Phase 1:** Project Pitch, Repository Setup, and Architecture Mapping.
- [x] **Phase 2:** Developing the Core WARL Swarm Engine in Python.
- [x] **Phase 3:** Building the Live Web Dashboard (GitHub Pages).
- [x] **Phase 4:** Integrating the Gemini Chatbot Commander.
- [x] **Phase 5:** Final Polish and Demo Video recording.

## Development Timeline & Milestones
- **2026-09-01 07:00 AM EDT** - Completed Phase 3: Built the Live Web Dashboard (GitHub Pages) with cellular automata physics engine.
- **2026-09-01 07:25 AM EDT** - Optimized Swarm Logic: Scaled to 12 drones and implemented decentralized targeting heuristics.
- **2026-09-01 09:30 AM EDT** - Completed Phase 4: Integrated Gemini Chatbot Commander and Esri Satellite Imagery.
- **2026-09-01 10:00 AM EDT** - 🏆 **Hackathon Project Officially Submitted!**
- **2026-09-01 10:05 AM EDT** - *Post-Submission Roadmap:* Planned integration of True PyTorch RL JSON export, Drone Payload Logistics (Base refills), and advanced Chatbot debugging to achieve absolute perfection.

---
*Developed for the GDG Innovation Challenge 2026.*
