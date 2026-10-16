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


@pytest.mark.parametrize("mixer", ["vdn", "independent", "qmix"])
@pytest.mark.parametrize("comm", [False, True])
def test_update_runs(mixer, comm):
    agent = SwarmAgent(obs_dim=4, n_actions=3, n_agents=5,
                       cfg={"hidden": [8], "mixer": mixer, "comm": {"enabled": comm, "dim": 8}})
    buf = ReplayBuffer(100, 5, 4, 3)
    for _ in range(40):
        buf.push(np.random.rand(5, 4), np.random.randint(0, 3, 5), 1.0, np.random.rand(5, 4), 0.99, np.ones((5, 3), bool))
    loss = agent.update(buf.sample(16))
    assert np.isfinite(loss)


def test_nstep_sums_rewards_and_stops_at_episode_end():
    from swarm.trainer import NStep

    ns = NStep(3, 0.5)
    z = np.zeros(2)
    assert ns.add("o0", 0, 1.0, z, "o1", None, False, False) == []
    assert ns.add("o1", 0, 1.0, z, "o2", None, False, False) == []
    (obs, _, R, nxt, disc, _, _, _), = ns.add("o2", 0, 1.0, z, "o3", None, False, False)
    assert obs == "o0" and R == 1.75 and nxt == "o3" and disc == 0.125
    out = ns.add("o3", 0, 4.0, z, "o4", None, True, True)
    assert [o[0] for o in out] == ["o1", "o2", "o3"]
    assert out[-1][2] == 4.0 and all(o[4] == 0.0 for o in out)


def test_pretrain_from_rule_runs_and_agent_copies_rule():
    """A short demo pre-training makes the swarm mostly pick the rule's action."""
    from swarm.registry import get_app
    from swarm.trainer import collect_demos, train

    app = get_app("wildfire")
    cfg = {
        "seed": 0,
        "env": {"grid_size": 8, "n_drones": 2, "max_steps": 30, "fire_every": 3},
        "agent": {"hidden": [64], "mixer": "independent", "agent_id": True},
        "train": {"total_steps": 200, "num_envs": 2, "batch_size": 64, "learning_starts": 50, "n_step": 3,
                  "log_every": 10_000},
        "pretrain": {"rule": "nearest-fire rule", "demo_steps": 600, "updates": 400},
    }
    agent, _ = train(app, cfg, log=lambda *_: None)
    demos = collect_demos(app, cfg, 300, agent.gamma, 3, seed=99)
    q_actions = agent.act(demos.obs[:300], demos.mask[:300])
    assert (q_actions == demos.actions[:300]).mean() > 0.6


def test_messages_only_reach_neighbours():
    """With a radius rule, changing a far-away agent does not change another agent's Q-values."""
    import torch

    from swarm.agents import radius_neighbours

    agent = SwarmAgent(obs_dim=4, n_actions=3, n_agents=3, cfg={"hidden": [8], "comm": {"enabled": True, "dim": 8}})
    agent.set_neighbours(radius_neighbours((0, 1), 0.2))
    obs = torch.tensor([[[0.0, 0.0, 1, 1], [0.1, 0.1, 1, 1], [0.9, 0.9, 1, 1]]])
    q = agent.q(obs)
    far = obs.clone()
    far[0, 2, 2:] = -5.0  # agent 2 is out of range of agents 0 and 1
    q2 = agent.q(far)
    assert torch.allclose(q[0, :2], q2[0, :2]) and not torch.allclose(q[0, 2], q2[0, 2])
    near = obs.clone()
    near[0, 1, 2:] = -5.0  # agent 1 is in range of agent 0
    assert not torch.allclose(q[0, 0], agent.q(near)[0, 0])
