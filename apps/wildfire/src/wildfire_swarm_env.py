import gymnasium as gym
from gymnasium import spaces
import numpy as np

class WildfireSwarmEnv(gym.Env):
    """
    Multi-Agent Reinforcement Learning Environment for Wildfire Suppression.
    Models a 2D cellular automata forest grid where autonomous UAVs must navigate,
    deploy retardant, and manage payloads to minimize contiguous fire spread.
    """
    
    def __init__(self, grid_size=10, num_drones=3, max_payload=5, wind_vector=(1, 0)):
        super(WildfireSwarmEnv, self).__init__()
        
        self.grid_size = grid_size
        self.num_drones = num_drones
        self.max_payload = max_payload
        self.wind_vector = wind_vector # (dy, dx) bias for fire spread
        
        # Grid states: 0=Unburned, 1=Burning, 2=Extinguished/Burned
        self.grid = np.zeros((self.grid_size, self.grid_size), dtype=np.int8)
        
        # Agent states: [y, x, payload]
        self.drone_states = np.zeros((self.num_drones, 3), dtype=np.int32)
        
        # Action space per drone: 0=Up, 1=Down, 2=Left, 3=Right, 4=Drop Retardant, 5=Wait/Refill
        self.action_space = spaces.MultiDiscrete([6] * self.num_drones)
        
        # Observation space: 1D array containing flattened grid + drone states
        obs_dim = (self.grid_size * self.grid_size) + (self.num_drones * 3)
        self.observation_space = spaces.Box(low=0, high=max(self.grid_size, self.max_payload), shape=(obs_dim,), dtype=np.float32)
        
        self.max_steps = 100
        self.current_step = 0
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        
        # Initialize forest as unburned
        self.grid.fill(0)
        
        # Ignite center of the forest
        center = self.grid_size // 2
        self.grid[center, center] = 1
        
        # Initialize drones at base (0, 0) with full payloads
        for i in range(self.num_drones):
            self.drone_states[i] = [0, 0, self.max_payload]
            
        return self._get_obs(), {}
        
    def _get_obs(self):
        grid_flat = self.grid.flatten().astype(np.float32)
        drones_flat = self.drone_states.flatten().astype(np.float32)
        return np.concatenate((grid_flat, drones_flat))
        
    def step(self, actions):
        self.current_step += 1
        reward = 0.0
        
        # 1. Process Drone Actions
        for i, action in enumerate(actions):
            y, x, payload = self.drone_states[i]
            
            if action == 0 and y > 0: y -= 1                 # Up
            elif action == 1 and y < self.grid_size - 1: y += 1 # Down
            elif action == 2 and x > 0: x -= 1               # Left
            elif action == 3 and x < self.grid_size - 1: x += 1 # Right
            elif action == 4:                                # Drop Retardant
                if payload > 0 and self.grid[y, x] == 1:
                    self.grid[y, x] = 2 # Extinguish
                    payload -= 1
                    reward += 10.0 # Reward for extinguishing fire
                else:
                    reward -= 1.0 # Penalty for wasted drop or empty payload
            elif action == 5:                                # Refill
                if y == 0 and x == 0: # Must be at base
                    payload = self.max_payload
                else:
                    reward -= 0.5 # Penalty for idle action outside base
                    
            self.drone_states[i] = [y, x, payload]
            
        # 2. Process Fire Spread (Cellular Automata)
        new_grid = self.grid.copy()
        fire_count = 0
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                if self.grid[y, x] == 1:
                    fire_count += 1
                    # Spread to neighbors with probability influenced by wind
                    neighbors = [(y-1, x), (y+1, x), (y, x-1), (y, x+1)]
                    for ny, nx in neighbors:
                        if 0 <= ny < self.grid_size and 0 <= nx < self.grid_size:
                            if self.grid[ny, nx] == 0:
                                # Base 10% spread chance, adjust if wind aligns
                                spread_prob = 0.1
                                if (ny - y) == self.wind_vector[0] and (nx - x) == self.wind_vector[1]:
                                    spread_prob = 0.4 # Wind blows fire this way
                                if np.random.rand() < spread_prob:
                                    new_grid[ny, nx] = 1
                                    
        self.grid = new_grid
        
        # Global penalty for active fires (encourages speed)
        reward -= (fire_count * 0.5)
        
        terminated = False
        if fire_count == 0:
            terminated = True
            reward += 100.0 # Massive reward for total containment
        elif self.current_step >= self.max_steps:
            terminated = True
            
        info = {'fire_count': fire_count}
        return self._get_obs(), reward, terminated, False, info
