"""Download the open datasets listed in sources.yaml into nature/data/raw/<id>/.

    python nature/fetch.py                 # every dataset that can be fetched automatically
    python nature/fetch.py fish-tetra-2024 # one dataset

Datasets marked `fetch: manual` (Dryad) print where to download them in a browser.
Nothing under nature/data/ is committed.
"""

from __future__ import annotations

import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nature.flock.io import RAW_DIR, load_sources  # noqa: E402


def fetch_zenodo(src: dict) -> None:
    out = RAW_DIR / src["id"]
    out.mkdir(parents=True, exist_ok=True)
    for name in src["files"]:
        dest = out / name
        if dest.exists():
            print(f"have {dest}")
            continue
        url = (f"https://zenodo.org/api/records/{src['zenodo_record']}/files/"
               f"{urllib.parse.quote(name)}/content")
        print(f"get  {url}")
        tmp = dest.with_suffix(dest.suffix + ".part")
        urllib.request.urlretrieve(url, tmp)
        tmp.rename(dest)


def main(argv: list[str]) -> None:
    sources = load_sources()
    ids = argv or list(sources)
    for i in ids:
        src = sources[i]
        if src["fetch"] == "zenodo":
            fetch_zenodo(src)
        else:
            missing = [f for f in src["files"] if not (RAW_DIR / i / f).exists()]
            if missing:
                print(f"manual: download {missing} from {src['url']} into {RAW_DIR / i}/")
            else:
                print(f"have {i}")


if __name__ == "__main__":
    main(sys.argv[1:])
