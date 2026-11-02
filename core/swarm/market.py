"""Market-based swarm coordination: agents bid, prices settle who gets what.

Some swarm problems are one-shot allocations (which guest goes to which
hotel, who covers which open shift) rather than step-by-step control. There
the swarm coordinates through a market instead of a learned policy: each
agent works out its own value for each option from what it knows, bids, and
simple local rules (raise the price of a contested option, award a task to the
lowest bid) settle the allocation with no central planner. This is the same
idea as ants or bees allocating foragers through local signals.

* ``auction``: Bertsekas' auction for assigning bidders, each needing ``size``
  units, to options with limited capacity. Bidders raise an option's price
  until each holds its best option at the going prices; with a small ``eps``
  the result is within ``n * eps`` of the best total value for unit sizes.
* ``contract_net``: tasks are announced one at a time; every agent that can
  take the task bids its own cost, and the lowest bid wins.
"""

import numpy as np


def auction(values: np.ndarray, capacity: np.ndarray, sizes: np.ndarray | None = None,
            eps: float = 1.0, max_rounds: int = 100_000) -> np.ndarray:
    """values: (n_bidders, n_options), -inf where not allowed; capacity: (n_options,) units.

    Returns the option index for each bidder, or -1 when the bidder is better
    off with its outside option (value 0) at the final prices.
    """
    n, m = values.shape
    sizes = np.ones(n, dtype=int) if sizes is None else np.asarray(sizes, dtype=int)
    price = np.zeros(m)                       # price per unit of capacity
    holder_bid = np.zeros(n)                  # each bidder's standing bid per unit
    assign = np.full(n, -1)
    out = np.zeros(n, dtype=bool)             # dropped out: nothing beats the outside option
    # A bidder turned away from an option that is not full (its group does not fit beside
    # higher bids) stays away from it until that option's price changes.
    blocked_at = np.full((n, m), np.nan)
    for _ in range(max_rounds):
        free = np.nonzero((assign < 0) & ~out)[0]
        if len(free) == 0:
            break
        i = free[0]
        net = values[i] - price * sizes[i]
        net[capacity < sizes[i]] = -np.inf
        net[blocked_at[i] == price] = -np.inf
        order = np.argsort(-net)
        best = order[0]
        if not np.isfinite(net[best]) or net[best] < 0:
            out[i] = True
            continue
        second = net[order[1]] if m > 1 and np.isfinite(net[order[1]]) else 0.0
        second = max(second, 0.0)
        bid = price[best] + (net[best] - second + eps) / sizes[i]
        assign[i] = best
        holder_bid[i] = bid
        old_price = price[best]
        # The option keeps its highest bids per unit within capacity and turns the rest away.
        holders = np.nonzero(assign == best)[0]
        holders = holders[np.argsort(-holder_bid[holders])]
        used = 0
        for h in holders:
            if used + sizes[h] <= capacity[best]:
                used += sizes[h]
            else:
                assign[h] = -1
                out[h] = False
        if used >= capacity[best] or used + sizes.min() > capacity[best]:
            kept = holders[assign[holders] == best]
            price[best] = holder_bid[kept].min() if len(kept) else price[best]
        if price[best] == old_price:  # turned away without the price rising: a size misfit
            for h in holders:
                if assign[h] < 0:
                    blocked_at[h, best] = price[best]
    return assign


def contract_net(tasks: list, agents: list, bid, award) -> dict:
    """Announce each task in turn; ``bid(agent, task)`` returns a cost or None
    (cannot take it); the lowest bidder wins and ``award(agent, task)`` updates
    that agent's own state. Returns {task index: agent index or None}."""
    result = {}
    for t, task in enumerate(tasks):
        bids = [(c, a) for a, agent in enumerate(agents) if (c := bid(agent, task)) is not None]
        if bids:
            cost, a = min(bids, key=lambda x: x[0])
            award(agents[a], task)
            result[t] = a
        else:
            result[t] = None
    return result
