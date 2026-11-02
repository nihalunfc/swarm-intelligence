"""Maps application names to their modules.

A trainable app module provides:

* ``make_env(env_cfg: dict, split: str, seed: int) -> SwarmEnv``
* ``BASELINES: dict[str, policy]`` where ``policy(env, obs, mask) -> actions``
* ``KEY_METRICS: list[str]`` shown in result tables

A results-only app (no environment yet) provides ``benchmark_rows(cfg) -> list[dict]``.
"""

import importlib

APPS = {
    "energy": "apps.energy",
    "wildfire": "apps.wildfire",
    "hotel": "apps.hotel",
    "hotel-energy": "apps.hotel.energy",
    "hotel-housekeeping": "apps.hotel.housekeeping",
    "hotel-relocation": "apps.hotel.relocation",
    "hotel-shifts": "apps.hotel.shifts",
    "citylearn": "apps.citylearn",          # optional: needs the citylearn package
    "vmas": "apps.vmas",                    # optional: needs the vmas package
}


def get_app(name: str):
    if name not in APPS:
        raise KeyError(f"Unknown app '{name}'. Known apps: {', '.join(APPS)}")
    return importlib.import_module(APPS[name])


def is_trainable(app) -> bool:
    return hasattr(app, "make_env")
