import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

class GridSwarmEnv(gym.Env):
    """
    Custom Environment for Agent-Based Swarm Simulation on the ERCOT Grid.
    
    Agents: Multiple localized smart battery nodes.
    Goal: Flatten the human demand curve (minimize Peak-to-Average Ratio).
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, data_path, num_agents=5, battery_capacity_mw=200.0, max_charge_rate_mw=50.0):
        super(GridSwarmEnv, self).__init__()
        
        # Grid/Swarm Physics Configuration
        self.num_agents = num_agents
        self.battery_capacity_mw = battery_capacity_mw
        self.max_charge_rate_mw = max_charge_rate_mw
        self.efficiency = 0.95 # 95% round-trip efficiency
        
        # Load Dataset
        self.df = pd.read_csv(data_path)
        if self.df['ERCOT_COAST_Load_MW'].dtype == 'O':
            self.df['ERCOT_COAST_Load_MW'] = self.df['ERCOT_COAST_Load_MW'].astype(str).str.replace(',', '').astype(float)
        
        # Feature columns for state space
        self.features = [
            'ERCOT_COAST_Load_MW', 'NREL_GHI_W_m2', 'NREL_Temperature_C', 
            'NREL_Wind_Speed_m_s'
        ]
        
        # Normalization properties (for neural network stability)
        self.max_load = self.df['ERCOT_COAST_Load_MW'].max()
        self.avg_load = self.df['ERCOT_COAST_Load_MW'].mean()
        
        # Action Space: 0 = Charge, 1 = Standby, 2 = Discharge (for EACH agent)
        # We use MultiDiscrete to allow each agent to take an independent action simultaneously
        self.action_space = spaces.MultiDiscrete([3] * self.num_agents)
        
        # State Space: Grid Features + State of Charge (SoC) for each agent
        # SoC is tracked as a percentage [0.0 to 1.0]
        obs_dim = len(self.features) + self.num_agents
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32)
        
        self.current_step = 0
        self.agent_socs = np.zeros(self.num_agents)
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        # Start batteries at 50% charge
        self.agent_socs = np.full(self.num_agents, 0.5)
        return self._get_obs(), {}

    def _get_obs(self):
        # Current grid state
        grid_state = self.df.iloc[self.current_step][self.features].values.astype(np.float32)
        # Normalize grid state (simple max scaling for neural net)
        grid_state[0] /= self.max_load
        
        # Combine grid state with agent SoCs
        return np.concatenate((grid_state, self.agent_socs), dtype=np.float32)

    def step(self, actions):
        """
        actions: list or array of size num_agents. (0: Charge, 1: Standby, 2: Discharge)
        """
        current_load = self.df.iloc[self.current_step]['ERCOT_COAST_Load_MW']
        
        net_battery_action_mw = 0.0
        penalties = 0.0
        
        # Process each agent's action
        for i, action in enumerate(actions):
            current_energy_mwh = self.agent_socs[i] * self.battery_capacity_mw
            
            if action == 0:  # CHARGE (Draw from grid)
                space_available = self.battery_capacity_mw - current_energy_mwh
                if space_available > 0:
                    charge_amount = min(self.max_charge_rate_mw, space_available)
                    current_energy_mwh += (charge_amount * self.efficiency)
                    net_battery_action_mw += charge_amount # Increases grid load
                else:
                    penalties -= 5.0 # Penalty for trying to overcharge
                    
            elif action == 2:  # DISCHARGE (Push to grid)
                energy_available = current_energy_mwh
                if energy_available > 0:
                    discharge_amount = min(self.max_charge_rate_mw, energy_available)
                    current_energy_mwh -= discharge_amount
                    net_battery_action_mw -= (discharge_amount * self.efficiency) # Decreases grid load
                else:
                    penalties -= 5.0 # Penalty for trying to discharge when empty
            
            # Update SoC
            self.agent_socs[i] = current_energy_mwh / self.battery_capacity_mw
            
        # Calculate new net grid load
        net_grid_load = current_load + net_battery_action_mw
        
        # --- Reward Function: Flatten the Curve ---
        # We want net_grid_load to be as close to the historical avg_load as possible.
        # Variance reduction.
        original_variance = abs(current_load - self.avg_load)
        new_variance = abs(net_grid_load - self.avg_load)
        
        # Reward is the reduction in variance (positive if we flattened the curve, negative if we made it worse)
        reward = (original_variance - new_variance) + penalties
        
        # Scale reward for neural network stability
        reward /= 100.0
        
        self.current_step += 1
        terminated = self.current_step >= len(self.df) - 1
        truncated = False
        
        info = {
            'original_load': current_load,
            'net_load': net_grid_load,
            'net_battery_action': net_battery_action_mw
        }
        
        return self._get_obs(), reward, terminated, truncated, info
