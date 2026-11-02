import numpy as np
from swarm.market import auction, contract_net
from swarm.trainer import evaluate

import apps.hotel.housekeeping as hk
import apps.hotel.relocation as rel
import apps.hotel.shifts as sh


def test_auction_matches_best_assignment_on_unit_sizes():
    rng = np.random.default_rng(0)
    for _ in range(20):
        v = rng.uniform(1, 10, (5, 5))
        got = auction(v, np.ones(5, dtype=int), eps=0.01)
        best = max(sum(v[i, p[i]] for i in range(5)) for p in __import__("itertools").permutations(range(5)))
        assert sorted(got) == list(range(5))
        assert sum(v[i, got[i]] for i in range(5)) >= best - 5 * 0.01


def test_auction_respects_capacity_and_group_sizes():
    v = np.array([[10.0, 9.0], [10.0, 9.0], [30.0, 5.0]])
    got = auction(v, np.array([3, 2]), sizes=np.array([1, 1, 3]))
    used = np.bincount(got[got >= 0], weights=np.array([1, 1, 3])[got >= 0], minlength=2)
    assert np.all(used <= [3, 2]) and got[2] == 0  # the group of 3 keeps the hotel it values most


def test_contract_net_awards_lowest_bid():
    agents = [{"cost": 5, "n": 0}, {"cost": 3, "n": 0}]
    res = contract_net([1, 2], agents, lambda a, t: a["cost"] + 10 * a["n"], lambda a, t: a.update(n=a["n"] + 1))
    assert res == {0: 1, 1: 0}


def test_relocation_methods_keep_the_rules():
    rows = {r["policy"]: r for r in rel.benchmark_rows({"env": {"scenarios": 8}})}
    assert all(r["rule_violations"] == 0 for r in rows.values())
    assert rows["swarm auction"]["net_value"] > rows["walk to competitor"]["net_value"]
    assert rows["optimal plan (reference)"]["net_value"] >= rows["swarm auction"]["net_value"] - 1e-6


def test_shift_market_only_awards_legal_shifts():
    p = sh.DEFAULTS
    s = sh.scenario(np.random.default_rng(1), __import__("pandas").read_csv(sh.HOTELS_CSV), p)
    staff = [{**e, "shifts": list(e["shifts"]), "extra": 0} for e in s["staff"]]
    picks = sh.swarm_market(staff, s["open"], p)
    for e in staff:
        shifts = sorted(e["shifts"])
        assert sh._hours(e) <= p["max_week_hours"]
        assert all(b2[0] >= b1[1] + p["min_rest"] - 1e-9 for b1, b2 in zip(shifts, shifts[1:]))
    assert sum(a is not None for a in picks) > 0


def test_housekeeping_rooms_are_cleaned_once_and_rules_rank_sensibly():
    env = hk.make_env({}, "test", 0)
    env.reset(seed=0)
    done = False
    while not done:
        _, _, done, _, _ = env.step(hk.BASELINES["soonest needed"](env, None, env.action_mask()))
    assert env.done_count.sum() == np.isfinite(env.ready_at).sum()
    floor = evaluate(hk, {}, hk.BASELINES["floor order"], 5, 0)
    soon = evaluate(hk, {}, hk.BASELINES["soonest needed"], 5, 0)
    assert soon["guest_wait_hours"] < floor["guest_wait_hours"]
