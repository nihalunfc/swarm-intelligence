"""Flexible equipment of the five sample hotels, as swarm agents.

Every agent is one piece of shiftable equipment in one hotel. Each has a
baseline hourly use (what it draws when left alone) and an energy buffer that
lets it move load in time:

* ``chiller``: pre-cools the building (buffer 0..E, leaks as the building warms).
* ``laundry``: defers cycles (buffer -D..0), must catch up by the end of the day.
* ``ev``: defers EV charging (buffer -D..0), same end-of-day deadline.
* ``pool``: lets pool or waterpark water drift within its temperature band (-E..E).

The sizes below are engineering assumptions scaled by room count, written down
in one place so they can be replaced with each property's real equipment list
(HARLTON-01, step 2).
"""

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

HOTELS_CSV = Path(__file__).resolve().parents[1] / "data" / "sample" / "hotels.csv"
TYPES = ["chiller", "laundry", "ev", "pool"]

# Which hotels have a heated pool or EV chargers (by style in hotels.csv).
POOL_KW = {"Full-service tower": 60.0, "Resort with indoor waterpark": 250.0, "Upscale all-suite": 50.0}
EV_STYLES = {"Full-service tower", "Resort with indoor waterpark", "Upscale all-suite"}


@dataclass
class Fleet:
    """Arrays over agents (one entry per piece of equipment)."""

    hotel: np.ndarray            # hotel index 0..H-1
    kind: np.ndarray             # index into TYPES
    power: np.ndarray            # kW it can shift in one hour
    e_min: np.ndarray            # kWh, buffer floor (negative = backlog allowed)
    e_max: np.ndarray            # kWh, buffer ceiling
    leak: np.ndarray             # share of the buffer lost per hour
    eta: np.ndarray              # share of extra energy that ends up stored
    deadline: np.ndarray         # bool: backlog must be cleared by the end of each day
    rooms: np.ndarray            # rooms of the agent's hotel
    names: list[str] = field(default_factory=list)
    hotel_names: list[str] = field(default_factory=list)
    hotel_rooms: np.ndarray = field(default_factory=lambda: np.zeros(0))

    @property
    def n(self) -> int:
        return len(self.kind)


def occupancy(timestamps: pd.Series) -> np.ndarray:
    """A simple weekly occupancy pattern: busier on Friday and Saturday nights."""
    dow = timestamps.dt.dayofweek.to_numpy()
    return np.where((dow == 4) | (dow == 5), 0.88, 0.72)


def build_fleet(hotels_csv: str | Path | None = None) -> Fleet:
    hotels = pd.read_csv(hotels_csv or HOTELS_CSV)
    rows = []
    for h, hotel in enumerate(hotels.itertuples()):
        r = float(hotel.rooms)
        rows.append((h, "chiller", 0.30 * r, 0.0, 0.9 * r, 0.15, 0.85, False))
        laundry = 0.9 * r * 0.8 / 9.0  # kWh per occupied room per day, run over 9 hours
        rows.append((h, "laundry", laundry, -4 * laundry, 0.0, 0.0, 1.0, True))
        if hotel.style in EV_STYLES:
            ev = 0.8 * (r / 60.0) * 7.0  # one 7 kW charger per 60 rooms
            rows.append((h, "ev", ev, -3 * ev, 0.0, 0.0, 1.0, True))
        if hotel.style in POOL_KW:
            p = 0.7 * POOL_KW[hotel.style]
            rows.append((h, "pool", p, -2 * p, 2 * p, 0.05, 1.0, False))
    a = list(zip(*rows))
    fleet = Fleet(
        hotel=np.array(a[0]), kind=np.array([TYPES.index(k) for k in a[1]]),
        power=np.array(a[2], dtype=float), e_min=np.array(a[3], dtype=float), e_max=np.array(a[4], dtype=float),
        leak=np.array(a[5], dtype=float), eta=np.array(a[6], dtype=float), deadline=np.array(a[7], dtype=bool),
        rooms=np.array([float(hotels.rooms[h]) for h in a[0]]),
        names=[f"{hotels.hotel_name[h]}: {k}" for h, k in zip(a[0], a[1])],
        hotel_names=list(hotels.hotel_name), hotel_rooms=hotels.rooms.to_numpy(float),
    )
    return fleet


def baseline_kw(fleet: Fleet, timestamps: pd.Series, temp_c: np.ndarray) -> np.ndarray:
    """Hourly use of each agent's equipment when left alone, shape (T, n_agents)."""
    hour = timestamps.dt.hour.to_numpy()
    occ = occupancy(timestamps)
    T = len(hour)
    out = np.zeros((T, fleet.n))
    for i in range(fleet.n):
        kind, r, p = TYPES[fleet.kind[i]], fleet.rooms[i], fleet.power[i]
        if kind == "chiller":
            out[:, i] = 0.04 * r * np.maximum(0.0, temp_c - 16.0) * (0.6 + 0.4 * occ)
        elif kind == "laundry":
            out[:, i] = np.where((hour >= 8) & (hour < 17), p * occ / 0.8, 0.0)
        elif kind == "ev":
            chargers_kw = p / 0.8
            out[:, i] = np.where((hour >= 16) & (hour < 23), 0.6 * chargers_kw, 0.1 * chargers_kw)
        else:  # pool heater duty cycle, a little higher at night
            out[:, i] = p * np.where((hour < 7) | (hour >= 22), 1.0, 0.85)
    return out


def hotel_base_kw(fleet: Fleet, timestamps: pd.Series) -> np.ndarray:
    """Non-shiftable load of each hotel (lighting, kitchens, elevators...), shape (T, H)."""
    hour = timestamps.dt.hour.to_numpy()
    occ = occupancy(timestamps)
    day = 0.85 + 0.15 * np.clip(np.sin(np.pi * (hour - 6) / 16), 0, None)
    return 0.55 * fleet.hotel_rooms[None, :] * (day * (0.7 + 0.3 * occ))[:, None]
