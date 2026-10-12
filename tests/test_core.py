import numpy as np
import pytest

from swarm.agents import SwarmAgent
from swarm.buffer import ReplayBuffer
from swarm.config import apply_overrides


def test_overrides_are_typed_and_nested():
    cfg = apply_overrides({"train": {"total_steps": 10}}, ["train.total_steps=500", "agent.mixer=independent"])
    assert cfg["train"]["total_steps"] == 500
    assert cfg["agent"]["mixer"] == "independent"


@pytest.mark.parametrize("n_agents", [3, 50])
def test_network_size_does_not_depend_on_swarm_size(n_agents):
    agent = SwarmAgent(obs_dim=8, n_actions=3, n_agents=n_agents, cfg={"hidden": [16]})
    n_params = sum(p.numel() for p in agent.q.parameters())
    assert n_params == 8 * 16 + 16 + 16 * 3 + 3


def test_act_respects_masks_and_batches_envs():
    agent = SwarmAgent(obs_dim=4, n_actions=3, n_agents=5, cfg={"hidden": [8]})
    obs = np.random.rand(2, 5, 4).astype(np.float32)
    mask = np.zeros((2, 5, 3), dtype=bool)
    mask[..., 1] = True
    for eps in (0.0, 1.0):
        acts = agent.act(obs, mask, eps, np.random.default_rng(0))
        assert acts.shape == (2, 5)
        assert (acts == 1).all()


@pytest.mark.parametrize("mixer", ["vdn", "independent"])
def test_update_runs(mixer):
    agent = SwarmAgent(obs_dim=4, n_actions=3, n_agents=5, cfg={"hidden": [8], "mixer": mixer})
    buf = ReplayBuffer(100, 5, 4, 3)
    for _ in range(40):
        buf.push(np.random.rand(5, 4), np.random.randint(0, 3, 5), 1.0, np.random.rand(5, 4), False, np.ones((5, 3), bool))
    loss = agent.update(buf.sample(16))
    assert np.isfinite(loss)
