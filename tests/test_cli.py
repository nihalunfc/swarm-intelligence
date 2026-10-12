import json

from swarm.cli import main

QUICK = ["train.total_steps=400", "train.num_envs=2", "train.learning_starts=100", "train.batch_size=32",
         "train.log_every=100000"]


def test_train_energy_and_wildfire_end_to_end(tmp_path):
    main(["train", "--config", "configs/energy.yaml", "--out", str(tmp_path), "--set", *QUICK,
          "env.n_agents=3"])
    main(["train", "--config", "configs/wildfire.yaml", "--out", str(tmp_path), "--set", *QUICK,
          "env.grid_size=8", "env.n_drones=2", "eval.episodes=2"])
    runs = sorted(tmp_path.glob("*/*/results.json"))
    assert len(runs) == 2
    for run in runs:
        rows = json.loads(run.read_text())
        assert rows[0]["policy"] == "swarm (trained)" and len(rows) >= 3


def test_replay_export(tmp_path):
    main(["train", "--config", "configs/wildfire.yaml", "--out", str(tmp_path), "--set", *QUICK,
          "env.grid_size=8", "env.n_drones=2", "eval.episodes=1"])
    run = next(tmp_path.glob("wildfire/*"))
    out = tmp_path / "replay.json"
    main(["replay", "--run", str(run), "--output", str(out), "--episodes", "1"])
    data = json.loads(out.read_text())
    assert "swarm (trained)" in data["policies"]
    frame = data["policies"]["swarm (trained)"][0]["frames"][0]
    assert len(frame["grid"]) == 64


def test_hotel_rows():
    from apps.hotel import benchmark_rows

    rows = benchmark_rows({})
    assert rows and all(r["total_cost"] > 0 for r in rows)
