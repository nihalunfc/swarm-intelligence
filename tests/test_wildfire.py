import numpy as np

from apps.wildfire import BASELINES, make_env
from apps.wildfire.env import BURNED, BURNING, DROP, HOLD, WET

ENV = {"grid_size": 10, "n_drones": 3, "max_payload": 2, "max_steps": 60}


def test_fire_burns_out_without_drones():
    env = make_env({**ENV, "max_steps": 500}, "train", 0)
    env.reset(seed=3)
    done = False
    while not done:
        _, _, term, trunc, _ = env.step(np.full(3, HOLD))
        done = term or trunc
    assert term, "a fire with no drones should still end once it runs out of fuel"
    assert (env.grid == BURNING).sum() == 0
    assert (env.grid == BURNED).sum() == env.ignited.sum()


def test_drop_extinguishes_and_uses_payload():
    env = make_env(ENV, "train", 0)
    env.reset(seed=0)
    y, x = np.argwhere(env.grid == BURNING)[0]
    env.pos[0] = (y, x)
    assert env.action_mask()[0, DROP]
    env.step(np.array([DROP, HOLD, HOLD]))
    assert env.grid[y, x] == WET and env.payload[0] == 1


def test_refill_only_at_base():
    env = make_env(ENV, "train", 0)
    env.reset(seed=0)
    env.payload[:] = 0
    env.pos[1] = (5, 5)
    env.step(np.full(3, HOLD))
    assert env.payload[0] == 2 and env.payload[1] == 0


def test_observation_shape_and_baselines():
    env = make_env(ENV, "train", 0)
    obs = env.reset(seed=1)
    assert obs.shape == (3, env.obs_dim) and np.isfinite(obs).all()
    for name, policy in BASELINES.items():
        acts = policy(env, obs, env.action_mask())
        assert acts.shape == (3,), name
        assert env.action_mask()[np.arange(3), acts].all(), name
