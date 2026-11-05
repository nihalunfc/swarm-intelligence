import json

import numpy as np

from swarm.cli import main
from swarm.stats import hierarchical_bootstrap, paired_test, permutation_pvalue

QUICK = ["train.total_steps=300", "train.num_envs=2", "train.learning_starts=100", "train.batch_size=32",
         "train.log_every=100000"]


def test_bootstrap_interval_contains_the_mean_and_shrinks_with_data():
    rng = np.random.default_rng(0)
    small = rng.normal(5, 1, (3, 10))
    large = rng.normal(5, 1, (10, 100))
    m, lo, hi = hierarchical_bootstrap(small)
    assert lo < m < hi
    _, lo2, hi2 = hierarchical_bootstrap(large)
    assert hi2 - lo2 < hi - lo
    assert lo2 < 5 < hi2


def test_permutation_test_detects_a_real_difference_and_not_noise():
    rng = np.random.default_rng(1)
    assert permutation_pvalue(rng.normal(1.0, 1.0, 50)) < 0.01
    assert permutation_pvalue(rng.normal(0.0, 1.0, 50)) > 0.05
    assert permutation_pvalue(np.zeros(5)) == 1.0
    # exact test on few units: 5 positive differences give p = 2/32
    assert abs(permutation_pvalue(np.ones(5)) - 2 / 32) < 1e-9


def test_paired_test_shapes():
    a = np.full((4, 20), 3.0) + np.random.default_rng(2).normal(0, 0.1, (4, 20))
    b = np.full(20, 2.0)
    r = paired_test(a, b)
    assert r["diff_lo"] < r["diff"] < r["diff_hi"] and r["diff_lo"] > 0.9
    assert r["n_seeds"] == 4 and r["n_episodes"] == 20


def test_seeds_are_aggregated_into_cis_and_paired_comparisons(tmp_path):
    for seed in (0, 1):
        main(["train", "--config", "configs/hotel-housekeeping.yaml", "--out", str(tmp_path / f"s{seed}"),
              "--set", *QUICK, f"seed={seed}", "eval.episodes=3", "env.rooms=60", "env.attendants=3"])
    eps = json.loads(next(tmp_path.rglob("episodes.json")).read_text())
    assert len(eps["policies"]["swarm (trained)"]) == 3
    assert (next(tmp_path.rglob("manifest.json"))).exists()
    out = tmp_path / "summary"
    main(["aggregate", str(tmp_path), "--output", str(out)])
    summary = json.loads(out.with_suffix(".json").read_text())
    s = summary["hotel-housekeeping"]
    assert s["seeds"] == [0, 1] and s["episodes"] == 3
    assert "soonest needed" in s["comparisons"]
    assert "p=" in out.with_suffix(".md").read_text()


def test_validation_split_and_checkpoint_selection(tmp_path):
    main(["train", "--config", "configs/energy.yaml", "--out", str(tmp_path), "--set", *QUICK, "env.n_agents=3",
          "env.val_start=2020-09-01", "train.eval_every=150", "eval.val_episodes=1"])
    run = next(tmp_path.glob("energy/*"))
    hist = (run / "val_history.csv").read_text().splitlines()
    assert len(hist) >= 3  # header + at least two validations


def test_mappo_baseline_trains_and_reloads(tmp_path):
    main(["train", "--config", "configs/wildfire.yaml", "--out", str(tmp_path), "--set", "algo=mappo",
          "train.total_steps=256", "train.num_envs=2", "ppo.rollout=32", "env.grid_size=8", "env.n_drones=2",
          "eval.episodes=1", "train.eval_every=128", "eval.val_episodes=1"])
    run = next(tmp_path.glob("wildfire/*"))
    main(["evaluate", "--run", str(run)])
    assert (run / "val_history.csv").exists()


def test_reference_bounds_are_reported():
    import apps.energy as E
    import apps.hotel.housekeeping as H
    from apps.hotel.housekeeping.references import NAME, lower_bound_rows
    from swarm.trainer import evaluate

    rows = lower_bound_rows(H, {"rooms": 60, "attendants": 3}, "test", 2, 10000)[NAME]
    rule = evaluate(H, {"rooms": 60, "attendants": 3}, H.BASELINES["soonest needed"], 2)
    assert np.mean([r["guest_wait_hours"] for r in rows]) <= rule["guest_wait_hours"] + 1e-6
    opt = E.optimum_rows(E, {"test_start": "2020-12-01", "n_agents": 3}, "test", 1, 10000)
    flat = opt["optimum: flattest (perfect foresight)"][0]
    prop = evaluate(E, {"test_start": "2020-12-01", "n_agents": 3}, E.BASELINES["proportional rule"], 1)
    assert flat["return"] >= prop["return"] - 1e-6


def test_residual_swarm_starts_as_the_rule(tmp_path):
    from swarm.registry import get_app
    from swarm.residual import wrap
    from swarm.trainer import evaluate

    app = wrap(get_app("hotel-housekeeping"), {"rule": "soonest needed"})
    cfg = {"rooms": 60, "attendants": 3}
    follow = evaluate(app, cfg, app.BASELINES["follow rule"], 3)
    rule = evaluate(app, cfg, app.BASELINES["soonest needed"], 3)
    assert follow["guest_wait_hours"] == rule["guest_wait_hours"] and follow["override_rate_pct"] == 0
    main(["train", "--config", "configs/hotel-housekeeping-residual.yaml", "--out", str(tmp_path), "--set", *QUICK,
          "env.rooms=60", "env.attendants=3", "eval.episodes=2", "pretrain.demo_steps=200", "pretrain.updates=20"])
    rows = json.loads(next(tmp_path.rglob("results.json")).read_text())
    assert "override_rate_pct" in rows[0] and "follow rule" not in {r["policy"] for r in rows}


def test_robustness_scenarios(tmp_path):
    main(["train", "--config", "configs/wildfire.yaml", "--out", str(tmp_path), "--set", *QUICK,
          "env.grid_size=8", "env.n_drones=4", "eval.episodes=2"])
    sc = tmp_path / "sc.yaml"
    sc.write_text("wildfire:\n  - {name: normal}\n  - {name: half fail, fail: 0.5}\n  - {name: noisy, noise: 0.3}\n"
                  "  - {name: windy, set: [p_wind=0.5]}\n")
    out = tmp_path / "rob"
    main(["robustness", str(tmp_path), "--scenarios", str(sc), "--output", str(out), "--metric", "forest_saved_pct"])
    md = out.with_suffix(".md").read_text()
    assert "half fail" in md and "nearest-fire rule" in md


def test_failed_agents_take_the_null_action():
    from apps.wildfire.env import HOLD, WildfireSwarmEnv
    from swarm.robustness import PerturbedEnv

    env = PerturbedEnv(WildfireSwarmEnv(grid_size=8, n_drones=4), fail=0.5, fail_at=0.0, horizon=10)
    env.reset(seed=3)
    m = env.action_mask()
    assert env.failed.sum() == 2 and (m[env.failed].sum(1) == 1).all() and m[env.failed, HOLD].all()


def test_failed_agents_get_no_work_from_rules_that_assign_rooms():
    from apps.hotel.housekeeping.baselines import floor_order
    from apps.hotel.housekeeping.env import make_env
    from swarm.robustness import PerturbedEnv

    inner = make_env({}, "test", 10_000)
    env = PerturbedEnv(inner, fail=0.5, fail_at=0.0, horizon=10)
    obs = env.reset(seed=10_000)
    for _ in range(20):
        a = floor_order(inner, obs, inner.action_mask())
        before = inner.busy.copy()
        obs, *_ = env.step(a)
        assert not ((inner.busy > 0) & (before == 0) & env.failed).any()
