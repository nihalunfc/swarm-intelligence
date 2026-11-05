"""Simple rules the battery swarm must beat."""

import numpy as np

from .env import CHARGE, DISCHARGE, IDLE
from .references import mpc_policy


def no_battery(env, obs, mask):
    return np.full(env.n_agents, IDLE)


def threshold(env, obs, mask):
    """Every battery discharges when load is above today's level and charges when below."""
    gap = env.load[env.t] - env.target[env.t]
    band = 0.5 * env.rate
    act = DISCHARGE if gap > band else CHARGE if gap < -band else IDLE
    return np.where(mask[:, act], act, IDLE)


def proportional(env, obs, mask):
    """Dispatch just enough batteries to close the gap, fullest (or emptiest) first."""
    gap = env.load[env.t] - env.target[env.t]
    k = int(min(env.n_agents, round(abs(gap) / env.rate)))
    actions = np.full(env.n_agents, IDLE)
    if k == 0:
        return actions
    act = DISCHARGE if gap > 0 else CHARGE
    order = np.argsort(-env.energy if act == DISCHARGE else env.energy)
    chosen = [i for i in order if mask[i, act]][:k]
    actions[chosen] = act
    return actions


BASELINES = {"no battery": no_battery, "threshold rule": threshold, "proportional rule": proportional,
             "MPC (24 h forecast)": mpc_policy()}
