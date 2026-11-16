"""Checks of the Bird Flock study maths on small hand-built inputs (not study data)."""

import numpy as np

from nature.flock.fields import coarse_grain, stlsq
from nature.flock.io import Tracks
from nature.flock.kinematics import derivatives, fill_short_gaps, group_order


def test_polarisation_of_aligned_school_is_one():
    T, N = 50, 10
    x = np.zeros((T, N, 2))
    x[..., 0] = np.arange(T)[:, None] * 0.1
    x[..., 1] = np.arange(N)[None, :]
    v = np.zeros_like(x)
    v[..., 0] = 1.0
    order = group_order(x, v)
    assert np.allclose(order["polarisation"], 1.0)


def test_velocity_of_straight_line_motion():
    T = 200
    pos = np.zeros((T, 1, 2))
    pos[:, 0, 0] = 0.3 * np.arange(T) * 0.02          # 0.3 m/s at 50 fps
    _, v, a = derivatives(Tracks(pos, 0.02, "line"))
    mid = slice(20, -20)
    assert np.allclose(v[mid, 0, 0], 0.3, atol=1e-6)
    assert np.allclose(a[mid, 0, 0], 0.0, atol=1e-6)


def test_short_gaps_filled_long_gaps_kept():
    pos = np.arange(30, dtype=float).reshape(30, 1, 1).repeat(2, axis=2)
    pos[5:7] = np.nan      # 2-frame gap
    pos[15:25] = np.nan    # 10-frame gap
    out = fill_short_gaps(pos, max_gap=3)
    assert np.allclose(out[5:7, 0, 0], [5, 6])
    assert np.isnan(out[15:25]).all()


def test_coarse_grain_conserves_animal_count():
    rng = np.random.default_rng(0)
    x = rng.uniform(0.3, 0.7, size=(20, 2))
    v = rng.normal(size=(20, 2))
    h = 0.01
    gx, gy = np.meshgrid(np.arange(0, 1, h), np.arange(0, 1, h), indexing="ij")
    rho, _ = coarse_grain(x, v, (gx, gy), sigma=0.03)
    assert abs(rho.sum() * h * h - 20) < 0.05


def test_stlsq_drops_unused_terms():
    rng = np.random.default_rng(1)
    A = rng.normal(size=(2000, 5))
    b = 2.0 * A[:, 1] - 0.5 * A[:, 3] + 0.01 * rng.normal(size=2000)
    c = stlsq(A, b, threshold=0.1)
    assert np.allclose(c, [0, 2.0, 0, -0.5, 0], atol=0.01)
