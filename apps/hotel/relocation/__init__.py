"""HARLTON-02: walked guests placed inside the group instead of at competitors.

On an oversold night, every reservation that has to move is an agent. Each
works out what each sister hotel is worth to it (the group keeps the room
revenue, minus transfer, compensation and any room-type change) and bids in
an auction for their open rooms (``swarm.market.auction``). A group bids as one
agent for all its rooms in one hotel, a guest who needs an accessible room
bids only for accessible rooms, and a multi-night stay only for hotels that
can hold every night. Guests that no sister hotel suits are walked to a
competitor, the status quo.

Scenarios are generated from the five sample hotels; the costs and rates are
assumptions in ``DEFAULTS`` meant to be replaced with the group's own.
"""

import numpy as np
import pandas as pd
from swarm.market import auction

from ..energy.loads import HOTELS_CSV

KEY_METRICS = ["net_value", "revenue_kept", "total_cost", "kept_in_group_pct", "rule_violations", "mean_transfer_km"]

DEFAULTS = {
    "scenarios": 50,
    "seed": 0,
    "oversell_share": 0.08,      # of the oversold hotel's rooms
    "open_share": 0.02,          # sister hotels' open rooms tonight, as a share of their rooms
    "accessible_share": 0.1,     # of open rooms
    "group_share": 0.3,          # of walked reservations that belong to a group
    "transfer_base": 15.0,       # $ per transfer
    "transfer_per_km": 2.0,
    "gesture": 50.0,             # $ credit for a guest moved inside the group
    "walk_compensation": 1.1,    # competitor room cost as a multiple of the guest's rate
    "walk_transfer": 40.0,
    "future_value_share": 0.2,   # of a loyal guest's yearly value put at risk by a walk
}

# Rough positions (km) of the five sample properties around one city.
POSITIONS = np.array([[0.0, 0.0], [12.0, 6.0], [3.0, -2.0], [-4.0, 3.0], [8.0, -9.0]])


def scenario(rng, hotels: pd.DataFrame, p: dict) -> dict:
    H = len(hotels)
    over = int(rng.integers(H))
    rooms = hotels.rooms.to_numpy()
    n_walk = max(2, rng.binomial(int(rooms[over]), p["oversell_share"]))
    guests, g = [], 0
    while sum(x["size"] for x in guests) < n_walk:
        size = int(rng.integers(2, 6)) if rng.random() < p["group_share"] else 1
        guests.append({
            "id": g, "size": size,
            "suite": bool(rng.random() < 0.15),
            "accessible": bool(size == 1 and rng.random() < 0.05),
            "nights": int(rng.choice([1, 2, 3], p=[0.6, 0.3, 0.1])),
            "rate": float(hotels.base_rate[over] * rng.uniform(0.8, 1.3)),
            "loyal_value": float(rng.choice([0, 600, 2500], p=[0.6, 0.3, 0.1])),
        })
        g += 1
    open_rooms = np.array([0 if h == over else rng.binomial(int(rooms[h]), p["open_share"]) for h in range(H)])
    accessible = rng.binomial(open_rooms, p["accessible_share"])
    suites = rng.binomial(open_rooms, 0.1)
    # Some open rooms are only free tonight; multi-night guests need the ones free for 3 nights.
    long_stay = rng.binomial(open_rooms, 0.6)
    dist = np.linalg.norm(POSITIONS[:H] - POSITIONS[over], axis=1)
    return {"over": over, "guests": guests, "open": open_rooms, "accessible": accessible, "suites": suites,
            "long_stay": long_stay, "dist": dist, "rates": hotels.base_rate.to_numpy(float)}


def walk_cost(guest, p):
    """Cost of sending a reservation to a competitor (on top of losing its revenue): the
    competitor's first night, the transfer, and the loyal guest's future value at risk."""
    return guest["size"] * (guest["rate"] * p["walk_compensation"] + p["walk_transfer"]) \
        + p["future_value_share"] * guest["loyal_value"]


def stay_value(guest, h, s, p):
    """Value of moving a reservation to sister hotel h instead of walking it (None if not allowed)."""
    if h == s["over"]:
        return None
    k = guest["size"]
    if k > s["open"][h] or (guest["accessible"] and s["accessible"][h] < 1):
        return None
    if guest["nights"] > 1 and k > s["long_stay"][h]:
        return None
    downgrade = guest["suite"] and s["suites"][h] < 1
    revenue = k * guest["nights"] * guest["rate"] * (0.85 if downgrade else 1.0)
    cost = k * (p["transfer_base"] + p["transfer_per_km"] * s["dist"][h] + p["gesture"])
    return revenue - cost + walk_cost(guest, p)  # gain over walking the reservation


def evaluate(s, assign, p) -> dict:
    """assign[g] = sister hotel index or -1 (walked). Checks the hard rules from scratch."""
    used = np.zeros(len(s["open"]), dtype=int)
    used_acc = np.zeros(len(s["open"]), dtype=int)
    used_long = np.zeros(len(s["open"]), dtype=int)
    kept_rev = cost = violations = km = moved = 0.0
    people = sum(g["size"] for g in s["guests"])
    for g, h in zip(s["guests"], assign):
        k = g["size"]
        if h < 0:
            cost += walk_cost(g, p)
            continue
        used[h] += k
        used_acc[h] += int(g["accessible"])
        used_long[h] += k if g["nights"] > 1 else 0
        if h == s["over"]:
            violations += 1
        downgrade = g["suite"] and s["suites"][h] < 1
        kept_rev += k * g["nights"] * g["rate"] * (0.85 if downgrade else 1.0)
        cost += k * (p["transfer_base"] + p["transfer_per_km"] * s["dist"][h] + p["gesture"])
        km += k * s["dist"][h]
        moved += k
    violations += int((used > s["open"]).sum() + (used_acc > s["accessible"]).sum() + (used_long > s["long_stay"]).sum())
    return {"net_value": kept_rev - cost, "revenue_kept": kept_rev, "total_cost": cost, "kept_in_group_pct": 100 * moved / people,
            "rule_violations": violations, "mean_transfer_km": km / moved if moved else 0.0}


def walk_all(s, p):
    return np.full(len(s["guests"]), -1)


def nearest_first(s, p):
    """First come, first served: each reservation in booking order takes the nearest sister hotel that fits."""
    left, acc, long_ = s["open"].copy(), s["accessible"].copy(), s["long_stay"].copy()
    out = []
    for g in s["guests"]:
        choice = -1
        for h in np.argsort(s["dist"]):
            if h == s["over"] or left[h] < g["size"] or (g["accessible"] and acc[h] < 1):
                continue
            if g["nights"] > 1 and long_[h] < g["size"]:
                continue
            choice = int(h)
            break
        if choice >= 0:
            left[choice] -= g["size"]
            acc[choice] -= int(g["accessible"])
            long_[choice] -= g["size"] if g["nights"] > 1 else 0
        out.append(choice)
    return np.array(out)


def swarm_auction(s, p):
    """Each reservation bids for sister hotels by its own value; prices settle contested rooms.

    Accessible and multi-night rooms are scarcer than open rooms in general, so
    those reservations bid in a first round for their own pools, then everyone
    bids for what is left.
    """
    G, H = len(s["guests"]), len(s["open"])
    assign = np.full(G, -1)
    left, acc, long_ = s["open"].copy(), s["accessible"].copy(), s["long_stay"].copy()
    rounds = [
        [i for i, g in enumerate(s["guests"]) if g["accessible"]],
        [i for i, g in enumerate(s["guests"]) if g["nights"] > 1 and not g["accessible"]],
        [i for i, g in enumerate(s["guests"]) if g["nights"] == 1 and not g["accessible"]],
    ]
    for pool, members in zip(["acc", "long", "open"], rounds):
        if not members:
            continue
        vals = np.full((len(members), H), -np.inf)
        for r, i in enumerate(members):
            g = s["guests"][i]
            for h in range(H):
                state = {**s, "open": left, "accessible": acc, "long_stay": long_}
                v = stay_value(g, h, state, p)
                if v is not None:
                    vals[r, h] = v
        cap = {"acc": np.minimum(acc, left), "long": np.minimum(long_, left), "open": left}[pool]
        sizes = np.array([s["guests"][i]["size"] for i in members])
        got = auction(vals, cap.copy(), sizes, eps=1.0)
        for r, i in enumerate(members):
            h = got[r]
            if h < 0:
                continue
            g = s["guests"][i]
            assign[i] = h
            left[h] -= g["size"]
            acc[h] -= int(g["accessible"])
            long_[h] -= g["size"] if g["nights"] > 1 else 0
    return assign


def optimal(s, p):
    """Exact best plan (integer program), for reference: what a central planner could reach."""
    import pulp

    G, H = len(s["guests"]), len(s["open"])
    prob = pulp.LpProblem("relocation", pulp.LpMaximize)
    x = {}
    for i, g in enumerate(s["guests"]):
        for h in range(H):
            v = stay_value(g, h, s, p)
            if v is not None:
                x[i, h] = (pulp.LpVariable(f"x_{i}_{h}", cat="Binary"), v)
    prob += pulp.lpSum(var * v for var, v in x.values())
    for i in range(G):
        prob += pulp.lpSum(x[i, h][0] for h in range(H) if (i, h) in x) <= 1
    for h in range(H):
        prob += pulp.lpSum(x[i, h][0] * s["guests"][i]["size"] for i in range(G) if (i, h) in x) <= s["open"][h]
        prob += pulp.lpSum(x[i, h][0] for i in range(G) if (i, h) in x and s["guests"][i]["accessible"]) <= s["accessible"][h]
        prob += pulp.lpSum(x[i, h][0] * s["guests"][i]["size"] for i in range(G)
                           if (i, h) in x and s["guests"][i]["nights"] > 1) <= s["long_stay"][h]
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    out = np.full(G, -1)
    for (i, h), (var, _) in x.items():
        if var.value() and var.value() > 0.5:
            out[i] = h
    return out


METHODS = {"walk to competitor": walk_all, "nearest sister hotel": nearest_first,
           "swarm auction": swarm_auction, "optimal plan (reference)": optimal}


def benchmark_rows(cfg: dict) -> list[dict]:
    p = {**DEFAULTS, **(cfg.get("env") or {})}
    hotels = pd.read_csv(cfg.get("hotels_csv") or HOTELS_CSV)
    rng = np.random.default_rng(int(p["seed"]))
    scenarios = [scenario(rng, hotels, p) for _ in range(int(p["scenarios"]))]
    rows = []
    for name, method in METHODS.items():
        res = [evaluate(s, method(s, p), p) for s in scenarios]
        rows.append({"app": "hotel-relocation", "policy": name,
                     **{k: float(np.mean([r[k] for r in res])) for k in res[0]},
                     "scenarios": len(scenarios)})
    return rows
