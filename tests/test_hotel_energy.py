import numpy as np

import apps.hotel.energy as app
from apps.hotel.energy import BASELINES, make_env
from apps.hotel.energy.env import EARLY, NORMAL, SHED
from swarm.trainer import evaluate


def test_splits_are_whole_summer_days_without_overlap():
    train, test = make_env({}, "train", 0), make_env({}, "test", 0)
    assert len(train.grid) % 24 == 0 and len(test.grid) % 24 == 0
    assert not set(train.timestamps) & set(test.timestamps)
    months = {int(str(t)[5:7]) for t in np.concatenate([train.timestamps, test.timestamps])}
    assert months == {6, 7, 8, 9}


def test_buffers_respect_limits_and_deadlines():
    env = make_env({}, "train", 0)
    env.reset(seed=3)
    rng = np.random.default_rng(0)
    for _ in range(24):
        mask = env.action_mask()
        assert mask.any(1).all()
        actions = (rng.random(mask.shape) * mask).argmax(1)
        env.step(actions)
        f = env.fleet
        assert np.all(env.e >= f.e_min - 1e-6) and np.all(env.e <= f.e_max + 1e-6)
    # Laundry and EV backlogs are cleared (or counted as missed) at midnight.
    assert np.all(env.e[env.fleet.deadline] == 0)
    assert env.episode_metrics()["missed_kwh"] == 0  # the mask forces catch-up in time


def test_shedding_lowers_load_and_rules_cut_the_peak():
    env = make_env({}, "train", 0)
    env.reset(seed=0)
    env.t = env.start + 15  # 15:00, chillers are running
    _, _, _, _, info = env.step(np.where(env.action_mask()[:, SHED], SHED, NORMAL))
    assert info["delta_kw"] < 0
    none = evaluate(app, {}, BASELINES["no action"], 1, 0)
    rule = evaluate(app, {}, BASELINES["peak-alert rule"], 1, 0)
    assert none["peak_cut_kw"] == 0 and rule["peak_cut_kw"] > 0 and rule["missed_kwh"] == 0
