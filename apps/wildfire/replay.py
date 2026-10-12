"""Record episodes as JSON for the web dashboard (docs/app.js replays them)."""

import json
from pathlib import Path

from .env import WildfireSwarmEnv


def record(env: WildfireSwarmEnv, policy, seed: int) -> dict:
    obs = env.reset(seed=seed)
    frames = [_frame(env)]
    done = False
    while not done:
        obs, _, term, trunc, _ = env.step(policy(env, obs, env.action_mask()))
        frames.append(_frame(env))
        done = term or trunc
    return {"seed": seed, "wind": list(env.wind), "metrics": env.episode_metrics(), "frames": frames}


def _frame(env) -> dict:
    return {
        "grid": "".join(str(int(c)) for c in env.grid.ravel()),
        "drones": env.pos.tolist(),
        "payload": env.payload.tolist(),
        "burning": int((env.grid == 1).sum()),
    }


def export_replay(env_cfg: dict, policies: dict, path: str, episodes: int = 3, seed: int = 20_000) -> None:
    out = {"grid_size": env_cfg.get("grid_size", 16), "max_payload": env_cfg.get("max_payload", 6), "policies": {}}
    for name, policy in policies.items():
        env = WildfireSwarmEnv(seed=seed, **env_cfg)
        out["policies"][name] = [record(env, policy, seed + k) for k in range(episodes)]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(out, separators=(",", ":")))
