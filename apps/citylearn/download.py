"""Download a CityLearn dataset and the package's sizing files from GitHub (raw files only).

CityLearn's own downloader lists files through the GitHub API, which is rate
limited and blocked on some networks; this fetches the same files directly.

    python -m apps.citylearn.download            # citylearn_challenge_2022_phase_all
"""

import argparse
import json
import urllib.request
from pathlib import Path

RAW = "https://raw.githubusercontent.com/intelligent-environments-lab/CityLearn/v{version}/data"
REPO = Path(__file__).resolve().parents[2]
DEFAULT = "citylearn_challenge_2022_phase_all"
MISC = ["battery_choices.yaml", "lbl-tracking_the_sun-res-pv.csv"]


def _get(url: str, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as r:
        dest.write_bytes(r.read())


def download(name: str = DEFAULT, version: str = "2.3.1", root: Path | None = None) -> Path:
    base = RAW.format(version=version)
    out = (root or REPO / "data" / "citylearn") / name
    _get(f"{base}/datasets/{name}/schema.json", out / "schema.json")
    schema = json.loads((out / "schema.json").read_text())
    files: set[str] = set()

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                if isinstance(v, str) and v.endswith((".csv", ".json")):
                    files.add(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(schema)
    for f in sorted(files):
        _get(f"{base}/datasets/{name}/{f}", out / f)
    cache = Path.home() / ".cache" / "citylearn" / f"v{version}" / "misc"
    for f in MISC:
        _get(f"{base}/misc/{f}", cache / f)
    return out / "schema.json"


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--name", default=DEFAULT)
    p.add_argument("--version", default="2.3.1")
    print(download(p.parse_args().name, p.parse_args().version))
