"""Simple rules the housekeeping swarm must beat."""

import numpy as np


def floor_order(env, obs, mask):
    """Today's common practice: each attendant owns a block of floors and cleans
    its vacated rooms in room-number order, whatever the next guest needs."""
    env.override = {}
    free = env._dirty_free()
    claimed = set()
    for i in np.nonzero(env.busy == 0)[0]:
        lo = i * env.F // env.n_agents
        hi = max(lo + 1, (i + 1) * env.F // env.n_agents)
        mine = np.nonzero(free & (env.floor >= lo) & (env.floor < hi))[0]
        mine = [r for r in mine[np.argsort(env.room_no[mine])] if r not in claimed]
        if mine:
            env.override[i] = mine[0]
            claimed.add(mine[0])
    return np.full(env.n_agents, env.WAIT)


def soonest_needed(env, obs, mask):
    """Greedy: always clean the free room whose guest needs it soonest (counting the elevator trip)."""
    return np.where(mask[:, 0], 0, env.WAIT)


def random_room(env, obs, mask):
    noise = env.rng.random(mask.shape) * mask
    noise[:, env.WAIT] = np.where(mask[:, :env.K].any(1), 0, 1)  # never idle when there is work
    return noise.argmax(-1)


BASELINES = {"floor order": floor_order, "soonest needed": soonest_needed, "random room": random_room}
