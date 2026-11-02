"""Simple rules the hotel equipment swarm must beat."""

import numpy as np

from . import loads as L
from .env import EARLY, NORMAL, SHED


def _plan(env, mask, active: bool):
    """Pre-cool and pre-heat for 3 hours before the grid's usual peak window,
    shed through it, then catch up deferred work.

    The window is the 4 hours that held most of the training period's top grid
    hours (``env.peak_window``; 14-18 h on the ERCOT sample, 16-20 h is typical
    for Ontario)."""
    PEAK = env.peak_window
    PRE = (PEAK[0] - 3, PEAK[0])
    h = env.hour[env.t]
    kind = env.fleet.kind
    store = (kind == L.TYPES.index("chiller")) | (kind == L.TYPES.index("pool"))
    actions = np.full(env.n_agents, NORMAL)
    if active and PRE[0] <= h < PRE[1]:
        actions[store] = EARLY
    elif active and PEAK[0] <= h < PEAK[1]:
        actions[:] = SHED
    elif h >= PEAK[1]:
        actions[env.fleet.deadline] = EARLY  # catch up deferred laundry and charging
    # Fall back to a valid action: the preferred one, else normal, else catch up.
    ok = mask[np.arange(env.n_agents), actions]
    actions = np.where(ok, actions, np.where(mask[:, NORMAL], NORMAL, EARLY))
    return actions


def no_action(env, obs, mask):
    return np.where(mask[:, NORMAL], NORMAL, EARLY)


def every_weekday(env, obs, mask):
    """Shed in the usual peak window on every weekday."""
    weekday = env.timestamps[env.t].astype("datetime64[D]").view("int64") % 7 not in (2, 3)  # 1970-01-01 was a Thursday
    return _plan(env, mask, weekday)


def peak_alert(env, obs, mask):
    """HARLTON-01 as written, without learning: act only on days whose forecast
    peak is in the top 20% of past days (the Peak Tracker alert)."""
    return _plan(env, mask, env.forecast_max[env.t] >= env.alert_level)


BASELINES = {"no action": no_action, "every weekday": every_weekday, "peak-alert rule": peak_alert}
