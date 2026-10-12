import numpy as np
import pandas as pd

from apps.energy import BASELINES, data, make_env
from apps.energy.env import CHARGE, DISCHARGE, IDLE

ENV = {"test_start": "2020-10-01", "n_agents": 4, "capacity_mwh": 100, "max_rate_mw": 50, "episode_hours": 48}


def test_both_schemas_load(tmp_path):
    old = pd.DataFrame({
        "Timestamp": pd.date_range("2022-01-01", periods=5, freq="h").astype(str),
        "NREL_GHI_W_m2": 0, "NREL_Temperature_C": 20.0, "NREL_Wind_Speed_m_s": 3.0,
        "ERCOT_COAST_Load_MW": ["10,000", "10,100", "10,200", "10,300", "10,400"],
    })
    p = tmp_path / "old.csv"
    old.to_csv(p, index=False)
    df = data.load(str(p))
    assert list(df.load_mw) == [10000, 10100, 10200, 10300, 10400]
    sample = data.load(None)
    assert {"load_mw", "ghi", "temp_c", "wind_ms"} <= set(sample.columns)
    assert len(sample) > 8000


def test_held_out_split_does_not_overlap():
    train = make_env(ENV, "train", 0)
    test = make_env(ENV, "test", 0)
    assert train.timestamps.max() < test.timestamps.min()


def test_energy_is_conserved_and_bounded():
    env = make_env(ENV, "train", 0)
    obs = env.reset(seed=1)
    assert obs.shape == (4, env.obs_dim)
    for _ in range(10):
        _, _, _, _, info = env.step(np.full(4, CHARGE))
    assert np.all(env.energy <= env.capacity + 1e-9)
    assert not env.action_mask()[:, CHARGE].any()  # full batteries cannot charge
    _, _, _, _, info = env.step(np.full(4, DISCHARGE))
    assert info["net_battery_mw"] < 0


def test_idle_swarm_changes_nothing_and_episode_truncates():
    env = make_env(ENV, "train", 0)
    env.reset(seed=0)
    done, steps = False, 0
    while not done:
        _, r, term, trunc, info = env.step(np.full(4, IDLE))
        assert r == 0 and info["net_load"] == info["original_load"]
        done, steps = term or trunc, steps + 1
    assert steps == 48 and trunc and not term
    assert env.episode_metrics()["peak_reduction_mw"] == 0


def test_baselines_return_valid_actions():
    env = make_env(ENV, "test", 0)
    obs = env.reset()
    for name, policy in BASELINES.items():
        acts = policy(env, obs, env.action_mask())
        assert acts.shape == (4,) and set(np.unique(acts)) <= {0, 1, 2}, name
