"""Code checks for the universal swarm study. Synthetic arrays only test the code; they are
never used as evidence (the study itself runs on real data, see universal/sources.yaml)."""
import numpy as np
import pandas as pd

from universal.applications import logistics
from universal.applications.core import NatureRule, Regulator
from universal.cosmos.models import MODELS, E, w_eff
from universal.equation import fit_drift, fit_growth, richards
from universal.features import dfa_alpha, powerlaw_fit, track_features
from universal.types import Series, Tracks

rng = np.random.default_rng(1)


def test_powerlaw_recovers_exponent():
    x = (1 - rng.random(20000)) ** (-1 / 1.5)  # Pareto with alpha = 2.5
    assert abs(powerlaw_fit(x)["tail_alpha"] - 2.5) < 0.15


def test_dfa_white_noise_near_half():
    assert abs(dfa_alpha(rng.normal(size=4000)) - 0.5) < 0.1


def test_growth_fit_prefers_saturating_law():
    t = np.linspace(0, 30, 60)
    y = richards(t, 100, 0.4, 15, 1.0) * (1 + 0.01 * rng.normal(size=t.size))
    g = fit_growth(Series(t, y, cumulative=True))
    assert g["best"] in {"richards", "logistic", "gompertz"} and g["r2"] > 0.99


def test_drift_detects_restoring_force():
    x = np.zeros(3000)
    for i in range(1, 3000):
        x[i] = 0.7 * x[i - 1] + rng.normal()
    assert fit_drift(Series(np.arange(3000.0), x))["a1"] < -0.2


def test_track_features_on_aligned_group():
    rows = []
    for t in range(60):
        for i in range(6):
            rows.append((0, t * 0.1, i, i * 1.0 + t * 0.1, (i % 2) * 1.0))
    tr = Tracks(pd.DataFrame(rows, columns=["ep", "t", "id", "x", "y"]))
    f = track_features(tr, max_frames=50)
    assert f["polarization"] > 0.99


def test_cosmology_models_reduce_to_lcdm():
    z = np.array([0.0, 0.5, 1.0, 2.0])
    lcdm = E(z, 0.3, 0.7, "LCDM", {})
    assert abs(lcdm[0] - 1) < 1e-9
    near = E(z, 0.3, 0.7, "SU-B quorum emergence", {"a_t": 0.01, "s": 0.001})
    assert np.allclose(near, lcdm, rtol=2e-3)
    assert abs(w_eff(0.5, "wCDM (= SU-A homeostatic vacuum)", {"w": -0.9}) + 0.9) < 1e-6
    assert set(MODELS) >= {"LCDM", "SU-C regulated overshoot"}


def test_regulator_settles_on_set_point():
    reg, x = Regulator(omega=0.3, zeta=0.7), 10.0
    for _ in range(300):
        x += reg.step(x, 2.0)
    assert abs(x - 2.0) < 1e-3


def test_nature_rule_and_logistics_run():
    pos, vel = rng.normal(size=(20, 2)), rng.normal(size=(20, 2))
    assert NatureRule().accel(pos, vel).shape == (20, 2)
    r = logistics.simulate(steps=200)
    assert r["mean_queue"] >= 0
