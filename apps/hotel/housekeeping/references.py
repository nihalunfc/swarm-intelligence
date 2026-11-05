"""A lower bound on guest waiting for the housekeeping swarm.

Every day is solved as a mixed-integer program with **perfect foresight** (all
check-out and arrival times known at 08:00) and **no elevator time** (a room
always takes 30 minutes). Both relaxations can only help, so no policy that
learns check-outs as they happen and walks between floors can wait less: the
result is a lower bound on ``guest_wait_hours``. HiGHS proves it within a time
limit; when it stops early, its proven dual bound is reported, which is still
a valid lower bound.

Variables: x[j, s] = 1 if room j is started at step s (s >= its check-out step,
s + 3 <= the end of the day). At every step at most ``attendants`` rooms are in
progress. The cost of each start time is exactly the waiting the environment
would charge for that room; a room left uncleaned costs the waiting until 17:00
plus the environment's one-hour end-of-day charge.
"""

from __future__ import annotations

import numpy as np

from .env import CLEAN_STEPS, DAY_START, NO_ARRIVAL, STEP_MIN

NAME = "lower bound (perfect foresight, no elevator time)"


def day_bound(env, time_limit: float = 60.0) -> float:
    from scipy.optimize import Bounds, LinearConstraint, milp  # loaded only when the bound is computed
    from scipy.sparse import lil_matrix

    S, N = env.n_steps, env.n_agents
    now = DAY_START + np.arange(1, S + 1) * STEP_MIN               # clock after each step
    n = len(env.needed)
    waits_from = env.needed[:, None] <= now[None, :]               # (rooms, steps) guest is due
    never = env.weight * STEP_MIN * waits_from.sum(1) + env.weight * 60.0 * (env.needed < NO_ARRIVAL)
    cols, cost = [], []
    for j in range(n):
        for s in range(S - CLEAN_STEPS + 1):
            if env.checkout[j] > DAY_START + s * STEP_MIN:
                continue
            ready = DAY_START + (s + CLEAN_STEPS) * STEP_MIN
            cols.append((j, s))
            cost.append(env.weight[j] * STEP_MIN * (waits_from[j] & (now < ready)).sum() - never[j])
    m = len(cols)
    if m == 0:
        return float(never.sum() / 60.0)
    A = lil_matrix((n + S, m))
    for k, (j, s) in enumerate(cols):
        A[j, k] = 1                                                  # each room at most once
        for t in range(s, min(S, s + CLEAN_STEPS)):
            A[n + t, k] = 1                                          # attendants busy at step t
    res = milp(np.asarray(cost), constraints=LinearConstraint(A.tocsr(), -np.inf, np.r_[np.ones(n), np.full(S, N)]),
               integrality=np.ones(m), bounds=Bounds(0, 1), options={"time_limit": time_limit})
    bound = res.fun if res.status == 0 else getattr(res, "mip_dual_bound", None)
    if bound is None:
        raise RuntimeError(f"housekeeping bound failed: {res.message}")
    return float((never.sum() + bound) / 60.0)


def lower_bound_rows(app, env_cfg: dict, split: str, episodes: int, seed: int) -> dict[str, list[dict]]:
    env = app.make_env(env_cfg, split, seed)
    rows = []
    for ep in range(episodes):
        env.reset(seed=seed + ep)
        hours = day_bound(env)
        rows.append({"guest_wait_hours": hours, "return": -hours / max(1.0, env.n_agents)})
    return {NAME: rows}
