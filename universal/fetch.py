"""Download the open datasets in sources.yaml into data/universal/raw/<key>/.

    python -m universal.fetch            # everything marked auto
    python -m universal.fetch --only fish pantheon
"""
from __future__ import annotations

import argparse
import shutil
import urllib.request
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
PREFIX = {"Z/": "https://zenodo.org/api/records/", "GH/": "https://raw.githubusercontent.com/"}


def raw_dir() -> Path:
    import os

    return Path(os.environ.get("UNIVERSAL_DATA", ROOT.parent / "data" / "universal" / "raw"))


def sources() -> dict:
    return yaml.safe_load((ROOT / "sources.yaml").read_text())


def url_of(u: str) -> str:
    for p, full in PREFIX.items():
        if u.startswith(p):
            return full + u[len(p):]
    return u


def fetch(keys: list[str] | None = None, force: bool = False) -> None:
    for d in sources()["datasets"]:
        if keys and d["key"] not in keys:
            continue
        out = raw_dir() / d["key"]
        out.mkdir(parents=True, exist_ok=True)
        for f in d.get("files", []):
            dest = out / f["name"]
            if dest.exists() and not force:
                continue
            print(f"[{d['key']}] {f['name']}")
            req = urllib.request.Request(url_of(f["url"]), headers={"User-Agent": "swarm-research"})
            with urllib.request.urlopen(req, timeout=600) as r, open(dest, "wb") as w:
                shutil.copyfileobj(r, w)
            if f.get("unzip"):
                with zipfile.ZipFile(dest) as z:
                    z.extractall(out / ("unz_" + dest.stem))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    fetch(a.only, a.force)


if __name__ == "__main__":
    main()
