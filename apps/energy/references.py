"""Strong references for the battery swarm: what is possible, and what a classic
controller achieves.

* ``optimum`` (perfect foresight, continuous): two linear programs over the whole
  evaluation period with the true future load, solved for the fleet as one
  1 GW / 4 GWh battery whose power can take any value. One minimises the peak
  (a linear program); the other minimises the squared distance from the
  daily-mean target, which is exactly the swarm's training objective (a
  quadratic program, solved with OSQP). No controller that has to act hour by hour
  on discrete battery moves can beat these, so they are upper bounds: each
  table reports what share of the gap from "no battery" to the bound a policy
  closes.
* ``mpc_policy`` (model predictive control): every hour, plan the next 24 hours
  with a linear program on a seasonal-naive forecast (the load at the same hour
  yesterday; the current hour is known, as for the rules), then dispatch the
  first hour's plan as whole batteries. This is the standard engineering
  baseline for battery scheduling.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import diags, eye, hstack, lil_matrix, vstack

from .env import CHARGE, DISCHARGE, IDLE


def _fleet(env):
    return env.n_agents * env.capacity, env.n_agents * env.rate, env.eta


def _lp(load: np.ndarray, target: np.ndarray, cap: float, rate: float, eta: float, e0: float, objective: str):
    """Variables x = [c (T), d (T), E (T), extra]; c = grid draw for charging, d = energy taken out.

    net_t = load_t + c_t - eta * d_t;  E_t = E_{t-1} + eta * c_t - d_t,  0 <= E_t <= cap.
    objective "peak": minimise P with net_t <= P (extra = [P]).
    objective "l1": minimise sum u_t with |net_t - target_t| <= u_t (extra = u, T values).
    Returns the net load.
    """
    T = len(load)
    I = eye(T, format="csr")
    # Energy balance: E_t - E_{t-1} - eta c_t + d_t = 0 (E_{-1} = e0).
    D = (eye(T) - diags([1.0], [-1], shape=(T, T))).tocsr()
    b_eq = np.zeros(T)
    b_eq[0] = e0
    if objective == "peak":
        n_extra = 1
        A_eq = hstack([-eta * I, I, D, lil_matrix((T, 1))]).tocsr()
        # load + c - eta d - P <= 0
        A_ub = hstack([I, -eta * I, lil_matrix((T, T)), -np.ones((T, 1))]).tocsr()
        b_ub = -load
        cost = np.r_[np.zeros(3 * T), 1.0]
    else:
        n_extra = T
        A_eq = hstack([-eta * I, I, D, lil_matrix((T, T))]).tocsr()
        # +(net - target) <= u and -(net - target) <= u
        A_ub = vstack([hstack([I, -eta * I, lil_matrix((T, T)), -I]),
                       hstack([-I, eta * I, lil_matrix((T, T)), -I])]).tocsr()
        b_ub = np.r_[target - load, load - target]
        cost = np.r_[np.zeros(3 * T), np.ones(T)]
    bounds = [(0, rate)] * T + [(0, rate)] * T + [(0, cap)] * T + [(None, None)] * n_extra
    res = linprog(cost, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")
    if not res.success:
        raise RuntimeError(f"LP failed: {res.message}")
    c, d = res.x[:T], res.x[T:2 * T]
    return load + c - eta * d, c, d


def _qp(load: np.ndarray, target: np.ndarray, cap: float, rate: float, eta: float, e0: float):
    """Minimise sum (net_t - target_t)^2 exactly (the swarm's own objective), with OSQP.

    Variables are scaled by the fleet power so the problem is well conditioned.
    """
    import osqp
    from scipy.sparse import csc_matrix, triu

    T, s = len(load), rate
    I = eye(T, format="csc")
    M = hstack([I, -eta * I, lil_matrix((T, T))]).tocsc()          # net - load, in units of s
    r = (load - target) / s
    P = triu(2 * (M.T @ M)).tocsc()
    q = 2 * (M.T @ r)
    D = (eye(T) - diags([1.0], [-1], shape=(T, T))).tocsc()
    A = vstack([hstack([-eta * I, I, D]), eye(3 * T)]).tocsc()        # balance, then bounds
    b = np.zeros(T)
    b[0] = e0 / s
    lo = np.r_[b, np.zeros(3 * T)]
    hi = np.r_[b, np.ones(T), np.ones(T), np.full(T, cap / s)]
    solver = osqp.OSQP()
    solver.setup(csc_matrix(P), q, A, lo, hi, verbose=False, eps_abs=1e-7, eps_rel=1e-7, max_iter=200_000,
                 polishing=True)
    res = solver.solve()
    x = np.clip(res.x, 0, None) * s
    c, d = np.minimum(x[:T], rate), np.minimum(x[T:2 * T], rate)
    return load + c - eta * d, c, d


def _metrics(orig: np.ndarray, net: np.ndarray, target: np.ndarray, fleet_mw: float) -> dict:
    reward = (((orig - target) ** 2 - (net - target) ** 2) / fleet_mw ** 2).sum()
    return {"return": float(reward), "par_before": float(orig.max() / orig.mean()),
            "par_after": float(net.max() / net.mean()), "peak_reduction_mw": float(orig.max() - net.max()),
            "std_reduction_pct": float(100 * (1 - net.std() / orig.std())), "hours": float(len(orig))}


def optimum_rows(app, env_cfg: dict, split: str, episodes: int, seed: int) -> dict[str, list[dict]]:
    """Per-episode metrics of the two perfect-foresight bounds (same episodes as evaluation)."""
    env = app.make_env(env_cfg, split, seed)
    cap, rate, eta = _fleet(env)
    peak, flat = "optimum: min peak (perfect foresight)", "optimum: flattest (perfect foresight)"
    out = {peak: [], flat: []}
    for ep in range(episodes):
        env.reset(seed=seed + ep)
        load, target = env.load[env.start:env.end], env.target[env.start:env.end]
        e0 = float(env.energy.sum())
        out[peak].append(_metrics(load, _lp(load, target, cap, rate, eta, e0, "peak")[0], target, env.fleet_mw))
        out[flat].append(_metrics(load, _qp(load, target, cap, rate, eta, e0)[0], target, env.fleet_mw))
    return out


def mpc_policy(horizon: int = 24):
    """Receding-horizon LP on a seasonal-naive forecast, dispatched as whole batteries."""

    def policy(env, obs, mask):
        t = env.t
        hs = np.arange(t, min(t + horizon, env.end))
        # Hour 0 is known (as for the rules); later hours use the load 24 hours earlier.
        lag = np.where(hs - 24 >= 0, hs - 24, np.maximum(t - 1, 0))
        forecast = env.load[lag].copy()
        forecast[0] = env.load[t]
        cap, rate, eta = _fleet(env)
        _, c, d = _lp(forecast, env.target[hs], cap, rate, eta, float(env.energy.sum()), "l1")
        p = c[0] - eta * d[0]
        actions = np.full(env.n_agents, IDLE)
        k = int(min(env.n_agents, round(abs(p) / env.rate)))
        if k == 0:
            return actions
        act = CHARGE if p > 0 else DISCHARGE
        order = np.argsort(env.energy if act == CHARGE else -env.energy)
        chosen = [i for i in order if mask[i, act]][:k]
        actions[chosen] = act
        return actions

    return policy


def gap_closed(value: float, none: float, best: float) -> float:
    """Share (%) of the distance from doing nothing to the bound that ``value`` covers."""
    return float(100 * (value - none) / (best - none)) if best != none else float("nan")

