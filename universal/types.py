"""Common data shapes for every swarm dataset."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class Tracks:
    """Agent trajectories. ``df`` has columns ep, t, id, x, y and optionally z (any units).

    ``ep`` separates independent recordings (flocks, flights, sites). Positions are in
    ``unit`` and time in seconds. Everything measured on tracks is made dimensionless
    with the median nearest-neighbour distance and the median speed.
    """

    df: pd.DataFrame
    unit: str = "m"
    dims: int = 2

    def episodes(self):
        for ep, g in self.df.groupby("ep", sort=False):
            yield ep, g.sort_values(["t", "id"])


@dataclass
class Series:
    """One collective observable over time (cases, load, area burned, speed of a flock...)."""

    t: np.ndarray
    x: np.ndarray
    label: str = ""
    cumulative: bool = False  # True when x is a running total (growth curves)


@dataclass
class Events:
    """Sizes of discrete events (fire days, cascades, quakes as energy, evacuations)."""

    sizes: np.ndarray
    label: str = ""
    times: np.ndarray | None = None


@dataclass
class Dataset:
    key: str
    category: str
    group: str
    tracks: Tracks | None = None
    series: list[Series] = field(default_factory=list)
    events: list[Events] = field(default_factory=list)
    notes: str = ""
