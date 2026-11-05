"""CityLearn Challenge 2022 as a swarm application: an external benchmark for the engine.

CityLearn (Vazquez-Canteli et al., 2019; Nweye et al., 2023) is the standard
multi-agent benchmark for building energy. In the 2022 challenge dataset, 17
homes each have rooftop solar and a 6.4 kWh home battery; every battery is an
agent. Running our unchanged engine on it answers "is the RL code right?"
against the benchmark's own reference controllers, with the benchmark's own
key performance indicators (each relative to having no batteries, so 1.0 =
no change and lower is better).

Needs the ``citylearn`` package (``pip install -e .[citylearn]``, Python 3.10
or 3.11) and the dataset (``python -m apps.citylearn.download``).
"""

from .env import BASELINES, KEY_METRICS, CityLearnSwarmEnv, make_env

__all__ = ["BASELINES", "CityLearnSwarmEnv", "KEY_METRICS", "make_env"]
