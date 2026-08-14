import nbformat as nbf
import os

nb = nbf.v4.new_notebook()

# Cell 1: Setup and Imports
cell_1 = """!pip install gymnasium
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
import warnings
warnings.filterwarnings('ignore')

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")"""

# Cell 2: The Environment
cell_2 = """class GridSwarmEnv(gym.Env):
    \"\"\"
    Custom Environment for Agent-Based Swarm Simulation on the ERCOT Grid.
    \"\"\"
    def __init__(self, data_path, num_agents=5, battery_capacity_mw=1000.0, max_charge_rate_mw=400.0):
        super(GridSwarmEnv, self).__init__()
        
        self.num_agents = num_agents
        self.battery_capacity_mw = battery_capacity_mw
        self.max_charge_rate_mw = max_charge_rate_mw
        self.efficiency = 0.95
        
        self.df = pd.read_csv(data_path)
        if self.df['ERCOT_COAST_Load_MW'].dtype == 'O':
            self.df['ERCOT_COAST_Load_MW'] = self.df['ERCOT_COAST_Load_MW'].astype(str).str.replace(',', '').astype(float)
            
        # Target only a subset for faster RL episodic training (e.g. 1 year)
        self.df = self.df[self.df['Timestamp'] >= '2022-01-01'].reset_index(drop=True)
        
        self.features = ['ERCOT_COAST_Load_MW', 'NREL_GHI_W_m2', 'NREL_Temperature_C', 'NREL_Wind_Speed_m_s']
        self.max_load = self.df['ERCOT_COAST_Load_MW'].max()
        self.avg_load = self.df['ERCOT_COAST_Load_MW'].mean()
        
        # Action Space: MultiDiscrete for all agents [Charge, Standby, Discharge]
        self.action_space = spaces.MultiDiscrete([3] * self.num_agents)
        
        obs_dim = len(self.features) + self.num_agents
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32)
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.agent_socs = np.full(self.num_agents, 0.5)
        return self._get_obs(), {}

    def _get_obs(self):
        grid_state = self.df.iloc[self.current_step][self.features].values.astype(np.float32)
        grid_state[0] /= self.max_load # Normalize
        return np.concatenate((grid_state, self.agent_socs), dtype=np.float32)

    def step(self, actions):
        current_load = self.df.iloc[self.current_step]['ERCOT_COAST_Load_MW']
        net_battery_action_mw = 0.0
        penalties = 0.0
        
        for i, action in enumerate(actions):
            current_energy_mwh = self.agent_socs[i] * self.battery_capacity_mw
            
            if action == 0:  # CHARGE
                space_available = self.battery_capacity_mw - current_energy_mwh
                if space_available > 0:
                    charge_amount = min(self.max_charge_rate_mw, space_available)
                    current_energy_mwh += (charge_amount * self.efficiency)
                    net_battery_action_mw += charge_amount
                else:
                    penalties -= 10.0
                    
            elif action == 2:  # DISCHARGE
                energy_available = current_energy_mwh
                if energy_available > 0:
                    discharge_amount = min(self.max_charge_rate_mw, energy_available)
                    current_energy_mwh -= discharge_amount
                    net_battery_action_mw -= (discharge_amount * self.efficiency)
                else:
                    penalties -= 10.0
            
            self.agent_socs[i] = current_energy_mwh / self.battery_capacity_mw
            
        net_grid_load = current_load + net_battery_action_mw
        
        original_variance = abs(current_load - self.avg_load)
        new_variance = abs(net_grid_load - self.avg_load)
        
        reward = (original_variance - new_variance) + penalties
        reward /= 100.0 # Scale
        
        self.current_step += 1
        terminated = self.current_step >= len(self.df) - 1
        
        info = {'original_load': current_load, 'net_load': net_grid_load}
        return self._get_obs(), reward, terminated, False, info"""

# Cell 3: Neural Network & Replay Buffer
cell_3 = """class QNetwork(nn.Module):
    def __init__(self, obs_dim, num_agents):
        super(QNetwork, self).__init__()
        # Flatten the MultiDiscrete action space into a single massive discrete space
        # 3 actions ^ num_agents (e.g., 3^5 = 243 possible swarm combinations)
        self.num_actions = 3 ** num_agents
        
        self.fc = nn.Sequential(
            nn.Linear(obs_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, self.num_actions)
        )
        
    def forward(self, x):
        return self.fc(x)

class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)
        
    def push(self, state, action_idx, reward, next_state, done):
        self.buffer.append((state, action_idx, reward, next_state, done))
        
    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = map(np.stack, zip(*batch))
        return state, action, reward, next_state, done
        
    def __len__(self):
        return len(self.buffer)"""

# Cell 4: Utility Functions for MultiDiscrete mapping
cell_4 = """def index_to_actions(index, num_agents):
    # Converts a flattened index (0 to 242) into a tuple of 5 actions (e.g., [0,1,2,0,1])
    actions = []
    for _ in range(num_agents):
        actions.append(index % 3)
        index //= 3
    return actions"""

# Cell 5: Training Loop
cell_5 = """def train_dqn(env, episodes=50, batch_size=128, gamma=0.99, lr=1e-3):
    obs_dim = env.observation_space.shape[0]
    num_agents = env.num_agents
    num_actions = 3 ** num_agents
    
    q_network = QNetwork(obs_dim, num_agents).to(device)
    target_network = QNetwork(obs_dim, num_agents).to(device)
    target_network.load_state_dict(q_network.state_dict())
    
    optimizer = optim.Adam(q_network.parameters(), lr=lr)
    buffer = ReplayBuffer(50000)
    
    epsilon = 1.0
    epsilon_decay = 0.90
    epsilon_min = 0.05
    
    rewards_history = []
    
    for episode in range(episodes):
        state, _ = env.reset()
        total_reward = 0
        done = False
        
        # Let episode steps run longer for better learning
        step_count = 0
        max_steps = 8760 # Train on a full year of hours per episode
        
        while not done and step_count < max_steps:
            # Epsilon-Greedy Action Selection
            if random.random() < epsilon:
                action_idx = random.randint(0, num_actions - 1)
            else:
                with torch.no_grad():
                    state_tensor = torch.FloatTensor(state).unsqueeze(0).to(device)
                    q_values = q_network(state_tensor)
                    action_idx = q_values.argmax().item()
                    
            actions = index_to_actions(action_idx, num_agents)
            
            next_state, reward, done, _, info = env.step(actions)
            buffer.push(state, action_idx, reward, next_state, done)
            state = next_state
            total_reward += reward
            step_count += 1
            
            # Train model
            if len(buffer) > batch_size:
                s, a, r, s_next, d = buffer.sample(batch_size)
                
                s = torch.FloatTensor(s).to(device)
                a = torch.LongTensor(a).to(device)
                r = torch.FloatTensor(r).to(device)
                s_next = torch.FloatTensor(s_next).to(device)
                d = torch.FloatTensor(d).to(device)
                
                q_values = q_network(s)
                q_value = q_values.gather(1, a.unsqueeze(1)).squeeze(1)
                
                with torch.no_grad():
                    next_q_values = target_network(s_next)
                    max_next_q_values = next_q_values.max(1)[0]
                    target = r + gamma * max_next_q_values * (1 - d)
                    
                loss = nn.MSELoss()(q_value, target)
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
        # Update Target Network
        if episode % 2 == 0:
            target_network.load_state_dict(q_network.state_dict())
            
        epsilon = max(epsilon_min, epsilon * epsilon_decay)
        rewards_history.append(total_reward)
        print(f"Episode {episode+1}/{episodes} | Reward: {total_reward:.2f} | Epsilon: {epsilon:.2f}")
        
    return q_network"""

# Cell 6: Run Execution & Plotting
cell_6 = """DATA_PATH = "/kaggle/input/ercot-nrel-merged/phase_01_master_environment_full_2018_2022.csv"
# Fallback for local testing if path doesn't exist
import os
if not os.path.exists(DATA_PATH):
    DATA_PATH = "data/clean_data/phase_01_master_environment_full_2018_2022.csv"

print("Initializing 5-Agent Swarm Environment (1000MWh Battery Each, 400MW/h Rate)...")
env = GridSwarmEnv(data_path=DATA_PATH, num_agents=5, battery_capacity_mw=1000.0, max_charge_rate_mw=400.0)

print("Training Deep Q-Network for 50 Episodes...")
trained_model = train_dqn(env, episodes=50)

# --- Evaluate and Plot ---
print("Evaluating Flattened Curve (Summer Peak Season)...")
state, _ = env.reset()
env.current_step = 4500 # Fast forward to mid-July
state = env._get_obs()
done = False

original_loads = []
net_loads = []

with torch.no_grad():
    for _ in range(500): # Sample 500 hours
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(device)
        q_values = trained_model(state_tensor)
        action_idx = q_values.argmax().item()
        
        actions = index_to_actions(action_idx, env.num_agents)
        next_state, reward, done, _, info = env.step(actions)
        
        original_loads.append(info['original_load'])
        net_loads.append(info['net_load'])
        state = next_state

plt.figure(figsize=(15, 6))
plt.plot(original_loads, label='Original ERCOT Load (No Battery)', color='black', alpha=0.5)
plt.plot(net_loads, label='Flattened Net Load (Swarm AI)', color='green', linewidth=2)
plt.title('Agent-Based Swarm Simulation: Peak-to-Average Ratio Flattening')
plt.xlabel('Hours')
plt.ylabel('Load (MW)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()"""

nb['cells'] = [
    nbf.v4.new_markdown_cell("# Phase 3: Agent-Based Swarm Intelligence (DQN)"),
    nbf.v4.new_code_cell(cell_1),
    nbf.v4.new_markdown_cell("## 1. Grid Swarm Environment (Gymnasium)"),
    nbf.v4.new_code_cell(cell_2),
    nbf.v4.new_markdown_cell("## 2. Deep Q-Network Architecture"),
    nbf.v4.new_code_cell(cell_3),
    nbf.v4.new_code_cell(cell_4),
    nbf.v4.new_markdown_cell("## 3. Training Loop"),
    nbf.v4.new_code_cell(cell_5),
    nbf.v4.new_markdown_cell("## 4. Execution & Visualization"),
    nbf.v4.new_code_cell(cell_6)
]

with open('src/phase_3_swarm_simulation/train_swarm.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Generated train_swarm.ipynb successfully.")
