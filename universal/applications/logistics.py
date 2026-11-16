"""Logistics: robots or vehicles that pick up work by a response-threshold rule (as ants and
bees divide labour) with set-point regulation of each queue.

Each zone has a queue q_z that grows by random arrivals. Each agent responds to stimulus s = q_z
in its current zone with probability s^2 / (s^2 + theta_i^2) (response threshold); thresholds
adapt (agents that work get lower thresholds, idle ones higher), so the swarm regulates every
queue toward a set point without a dispatcher. Simulation only; compare with a fixed
round-robin assignment. KPIs: mean and 95th percentile queue, travel moves.
"""
from __future__ import annotations

import numpy as np


def simulate(n_agents=20, zones=8, steps=2000, rule="swarm", seed=0) -> dict:
    rng = np.random.default_rng(seed)
    rates = rng.uniform(0.5, 3.0, zones)
    q = np.zeros(zones)
    where = rng.integers(0, zones, n_agents)
    theta = np.full(n_agents, 5.0)
    moves, hist = 0, []
    for t in range(steps):
        q += rng.poisson(rates)
        if rule == "round_robin":
            where = (np.arange(n_agents) + t) % zones
            moves += n_agents
        for i in range(n_agents):
            s = q[where[i]]
            if rule == "swarm":
                p = s**2 / (s**2 + theta[i] ** 2 + 1e-9)
                if rng.random() < p:
                    theta[i] = max(1.0, theta[i] - 0.1)
                else:
                    theta[i] = min(20.0, theta[i] + 0.1)
                    # move toward the neighbouring zone with the longer queue (local information only)
                    nb = [(where[i] - 1) % zones, (where[i] + 1) % zones]
                    where[i] = nb[int(q[nb[1]] > q[nb[0]])]
                    moves += 1
                    continue
            q[where[i]] = max(0.0, q[where[i]] - 1.0)
        hist.append(q.copy())
    h = np.array(hist[steps // 2:])
    return {"mean_queue": float(h.mean()), "p95_queue": float(np.percentile(h, 95)), "moves": int(moves)}


def demo() -> dict:
    return {"simulated (not evidence)": {"swarm (response threshold)": simulate(rule="swarm"),
                                         "round robin": simulate(rule="round_robin")}}
