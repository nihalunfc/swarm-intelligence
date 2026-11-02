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


def test_several_pads_refill_and_scale():
    import numpy as np

    from apps.wildfire import scaled_env_cfg
    from apps.wildfire.env import HOLD, WildfireSwarmEnv

    env = WildfireSwarmEnv(grid_size=16, n_drones=8, pads_per_side=2, seed=0)
    env.reset(seed=1)
    assert len(env.pads) == 4 and env._at_base(8, 8) and not env._at_base(5, 5)
    assert (env._pad_distance()[0] == 0).all()  # every drone starts on a pad
    env.pos[0] = (9, 9)
    env.payload[0] = 0
    env.step(np.full(8, HOLD))
    assert env.payload[0] == env.max_payload
    cfg = scaled_env_cfg({"n_drones": 6, "grid_size": 16, "scale_pads": True}, 600)
    assert cfg["pads_per_side"] == 10 and cfg["grid_size"] == 160 and "base_size" not in cfg


def test_target_actions_follow_the_rule_logic():
    import numpy as np

    from apps.wildfire.targets import BASELINES, WildfireTargetsEnv

    env = WildfireTargetsEnv(grid_size=12, n_drones=4, targets=3, seed=0)
    obs = env.reset(seed=2)
    assert obs.shape == (4, env.obs_dim) and env.n_actions == 5
    for _ in range(20):
        m = env.action_mask()
        a = BASELINES["spread rule"](env, obs, m)
        assert m[np.arange(4), a].all()
        obs, r, term, trunc, _ = env.step(a)
        if term or trunc:
            break
    assert 0 <= env.episode_metrics()["forest_saved_pct"] <= 100
