"""Simple rules the drone swarm must beat."""

import numpy as np

from .env import BURNING, DOWN, DROP, HOLD, LEFT, RIGHT, UP


def no_drones(env, obs, mask):
    return np.full(env.n_agents, HOLD)


def random_valid(env, obs, mask):
    noise = env.rng.random(mask.shape) * mask
    return noise.argmax(-1)


def _toward(y, x, ty, tx):
    if ty > y:
        return DOWN
    if ty < y:
        return UP
    if tx > x:
        return RIGHT
    if tx < x:
        return LEFT
    return HOLD


def nearest_fire(env, obs, mask):
    """The dashboard's original rule: fly to the nearest fire and drop; return to base when empty."""
    fy, fx = np.nonzero(env.grid == BURNING)
    actions = np.full(env.n_agents, HOLD)
    for i, (y, x) in enumerate(env.pos):
        if env.payload[i] == 0:
            actions[i] = _toward(y, x, *env.base)
        elif env.grid[y, x] == BURNING and mask[i, DROP]:
            actions[i] = DROP
        elif len(fy):
            # Small random tie-break so the swarm spreads out across the fire front.
            d = np.abs(fy - y) + np.abs(fx - x) + env.rng.random(len(fy)) * 2
            j = d.argmin()
            actions[i] = _toward(y, x, fy[j], fx[j])
    return actions


BASELINES = {"no drones": no_drones, "random": random_valid, "nearest-fire rule": nearest_fire}
