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


def load_jackdaw_flocks(path: str | Path, body_length: float = 0.34) -> list[Tracks]:
    """Ling et al. 2019 DataS1.txt: one block per flock ('*****flock 01******'), columns
    ID x y z t u v w ax ay az f_wb (metres, seconds). Track IDs can be more than birds,
    because a bird lost by the cameras comes back with a new ID; gaps are NaN."""
    blocks: dict[str, list[list[float]]] = {}
    cur = None
    with open(path) as f:
        next(f)
        for line in f:
            if line.startswith("*"):
                cur = "".join(ch for ch in line if ch.isdigit())
                blocks[cur] = []
            elif line.strip():
                blocks[cur].append([float(v) for v in line.split()])
    out = []
    for flock, rows in blocks.items():
        a = np.asarray(rows)
        dt = float(np.median(np.diff(np.unique(np.round(a[:, 4], 4)))))
        frame = np.round((a[:, 4] - a[:, 4].min()) / dt).astype(int)
        ids, col = np.unique(a[:, 0], return_inverse=True)
        pos = np.full((frame.max() + 1, len(ids), 3), np.nan)
        pos[frame, col] = a[:, 1:4]
        out.append(Tracks(pos, dt, f"jackdaw_flock_{flock}", body_length,
                          {"species": "jackdaw", "source": "jackdaw-2019", "track_ids": int(len(ids))}))
    return out


def load_pigeon_flights(path: str | Path, body_length: float = 0.32) -> list[Tracks]:
    """Papadopoulou et al. 2022 all_emp_data.csv (GPS, 5 Hz), one Tracks per flight.

    lon/lat are projected to local metres. Extra per-frame series kept in meta:
    distance to the robotic falcon (NaN in control flights)."""
    d = pd.read_csv(path)
    out = []
    for fl, g in d.groupby("study.flight"):
        lat0, lon0 = g["lat"].mean(), g["lon"].mean()
        x = (g["lon"] - lon0).to_numpy() * 111_320.0 * np.cos(np.radians(lat0))
        y = (g["lat"] - lat0).to_numpy() * 110_540.0
        frame = np.round(g["time"].to_numpy() / 0.2).astype(int)
        frame -= frame.min()
        ids, col = np.unique(g["pigeon"].to_numpy(), return_inverse=True)
        pos = np.full((frame.max() + 1, len(ids), 2), np.nan)
        pos[frame, col] = np.stack([x, y], axis=-1)
        pred = np.full(frame.max() + 1, np.nan)
        dp = g["dist2pred"].to_numpy()
        for f_, v_ in zip(frame, dp):
            if np.isfinite(v_):
                pred[f_] = v_ if np.isnan(pred[f_]) else min(pred[f_], v_)
        out.append(Tracks(pos, 0.2, f"pigeon_flight_{fl}", body_length, {
            "species": "homing pigeon", "source": "pigeon-predation-2022",
            "condition": "predator" if g["condition"].iloc[0] == "p" else "control",
            "flock_size": "big" if g["small.big"].iloc[0] == "b" else "small",
            "group": int(g["group.num"].iloc[0]), "dist_to_predator_m": pred,
            "given_speed_median": float(g["speed"].median()), "given_nn_median": float(g["nn1dist"].median()),
        }))
    return out


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
