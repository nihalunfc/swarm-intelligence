"""Loaders that turn each real dataset into one common shape.

Every loader returns a :class:`Tracks` object: positions in metres, shape (T, N, D),
with NaN where an animal was not tracked in that frame.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

NATURE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = NATURE_DIR / "data" / "raw"


@dataclass
class Tracks:
    """Positions of N animals over T frames in D dimensions (metres)."""

    pos: np.ndarray            # (T, N, D) metres, NaN = missing
    dt: float                  # seconds between frames
    name: str
    body_length: float | None = None   # metres
    meta: dict = field(default_factory=dict)

    @property
    def T(self) -> int:
        return self.pos.shape[0]

    @property
    def N(self) -> int:
        return self.pos.shape[1]

    @property
    def D(self) -> int:
        return self.pos.shape[2]

    def window(self, start_s: float, stop_s: float) -> "Tracks":
        a, b = int(start_s / self.dt), int(stop_s / self.dt)
        return Tracks(self.pos[a:b], self.dt, self.name, self.body_length, dict(self.meta))


def load_sources() -> dict:
    with open(NATURE_DIR / "sources.yaml") as f:
        return {d["id"]: d for d in yaml.safe_load(f)["datasets"]}


def load_fish_tetra(path: str | Path, px_per_cm: float = 27.45, fps: float = 50.0) -> Tracks:
    """Puy et al. 2024 fish CSV: 'Time [frame], X_0 [px], Y_0 [px], X_1 [px], ...'."""
    df = pd.read_csv(path)
    xcols = [c for c in df.columns if c.startswith("X_")]
    ycols = [c.replace("X_", "Y_") for c in xcols]
    x = df[xcols].to_numpy(dtype=float)
    y = df[ycols].to_numpy(dtype=float)
    pos = np.stack([x, y], axis=-1) / px_per_cm / 100.0   # px -> m
    name = Path(path).stem
    return Tracks(pos=pos, dt=1.0 / fps, name=name, body_length=0.025,
                  meta={"species": "black neon tetra", "source": "fish-tetra-2024"})


def load_dataset(dataset_id: str, file: str | None = None) -> Tracks:
    src = load_sources()[dataset_id]
    fname = file or src["files"][0]
    path = RAW_DIR / dataset_id / fname
    if not path.exists():
        raise FileNotFoundError(
            f"{path} is missing. Run `python nature/fetch.py {dataset_id}` "
            f"(or, for fetch: manual, download it from {src['url']})."
        )
    if dataset_id == "fish-tetra-2024":
        return load_fish_tetra(path, px_per_cm=src["px_per_cm"], fps=src["fps"])
    raise NotImplementedError(
        f"No loader yet for {dataset_id}: its column layout will be checked against the real file first."
    )
