"""HARLTON-01: hotel equipment swarm that keeps load out of the grid's peak hours."""

from .baselines import BASELINES
from .env import HotelEnergySwarmEnv, make_env

KEY_METRICS = ["net_saving_usd", "peak_cut_kw", "peak_cut_pct", "peaks_hit", "ga_saving_usd", "extra_energy_usd", "missed_kwh"]

__all__ = ["BASELINES", "HotelEnergySwarmEnv", "KEY_METRICS", "make_env"]
