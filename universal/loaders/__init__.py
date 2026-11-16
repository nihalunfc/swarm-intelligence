"""One loader per dataset in ``universal/sources.yaml``.

Each loader reads ``data/universal/raw/<key>/`` (see ``universal.fetch``) and returns a
``Dataset`` holding ``Tracks``, ``Series`` and/or ``Events``. Loaders only reshape and
convert units; they never invent or smooth data.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from ..fetch import raw_dir, sources
from ..types import Dataset, Events, Series, Tracks

REPO = Path(__file__).resolve().parents[2]
LOADERS = {}


def loader(key):
    def deco(fn):
        LOADERS[key] = fn
        return fn

    return deco


def meta(key):
    for d in sources()["datasets"]:
        if d["key"] == key:
            return d
    raise KeyError(key)


def ds(key, **kw):
    m = meta(key)
    return Dataset(key=key, category=m["category"], group=m["group"], **kw)


def lonlat_to_m(lon, lat):
    lat0 = np.deg2rad(np.nanmean(lat))
    r = 6_371_000.0
    return np.deg2rad(lon) * r * np.cos(lat0), np.deg2rad(lat) * r


# ---------------------------------------------------------------- animal motion
@loader("fish")
def fish(max_frames=20000):
    p = raw_dir() / "fish" / "x8_0.csv"
    d = pd.read_csv(p, nrows=max_frames)
    d.columns = [c.split(" ")[0] for c in d.columns]
    ids = sorted({int(c.split("_")[1]) for c in d.columns if c.startswith("X_")})
    rows = [pd.DataFrame({"t": d["Time"] / 50.0, "id": i, "x": d[f"X_{i}"], "y": d[f"Y_{i}"]}) for i in ids]
    df = pd.concat(rows).dropna()
    df["ep"] = "rec0"
    # 50 frames/s per Puy et al. 2024; positions in pixels (all features are made dimensionless)
    return ds("fish", tracks=Tracks(df, unit="px", dims=2))


@loader("jackdaw")
def jackdaw():
    p = raw_dir() / "jackdaw" / "DataS1.txt"
    rows, flock = [], 0
    for line in open(p):
        if line.startswith("*"):
            m = re.search(r"(\d+)", line)
            flock = int(m.group(1)) if m else flock + 1
            continue
        if line.startswith("ID"):
            continue
        f = line.split()
        if len(f) >= 5:
            rows.append((flock, float(f[4]), int(f[0]), float(f[1]), float(f[2]), float(f[3])))
    df = pd.DataFrame(rows, columns=["ep", "t", "id", "x", "y", "z"])
    df["t"] = df["t"].round(4)
    return ds("jackdaw", tracks=Tracks(df, unit="m", dims=3))


@loader("pigeon")
def pigeon():
    d = pd.read_csv(raw_dir() / "pigeon" / "all_emp_data.csv")
    x, y = lonlat_to_m(d["lon"].to_numpy(), d["lat"].to_numpy())
    df = pd.DataFrame({
        "ep": d["condition"].astype(str) + "-" + d["small.big"].astype(str) + "-g" + d["group.num"].astype(str)
        + "-f" + d["study.flight"].astype(str),
        "t": d["time"].round(2), "id": d["pigeon"], "x": x, "y": y,
    })
    return ds("pigeon", tracks=Tracks(df, unit="m", dims=2))


@loader("ants")
def ants():
    rows = []
    for f in sorted((raw_dir() / "ants").rglob("*.txt")):
        a = np.loadtxt(f, delimiter=",")
        rows.append(pd.DataFrame({"ep": f.stem, "t": a[:, 0], "id": 0, "x": a[:, 1], "y": a[:, 2]}))
    return ds("ants", tracks=Tracks(pd.concat(rows), unit="cm", dims=2),
              notes="single ants exploring alone: individual motion statistics only")


@loader("zebrafish")
def zebrafish(max_files=12):
    rows = []
    files = sorted(f for f in (raw_dir() / "zebrafish").rglob("*formated.txt")
                   if "__MACOSX" not in f.parts and not f.name.startswith("._"))[:max_files]
    for f in files:
        a = np.loadtxt(f, comments="#")
        n = (a.shape[1] - 1) // 3
        for i in range(n):
            rows.append(pd.DataFrame({"ep": f.parent.name + "/" + f.stem[-30:], "t": a[:, 0], "id": i,
                                      "x": a[:, 1 + 3 * i], "y": a[:, 2 + 3 * i]}))
    return ds("zebrafish", tracks=Tracks(pd.concat(rows), unit="m", dims=2))


# ---------------------------------------------------------------- human and machine motion
@loader("crowd")
def crowd():
    rows = []
    for f in sorted((raw_dir() / "crowd").glob("*_trajs.txt")):
        d = pd.read_csv(f, sep=";")
        rows.append(pd.DataFrame({"ep": f.stem.replace("_trajs", ""), "t": d["time"].round(1), "id": d["ped_no"],
                                  "x": d["x"], "y": d["y"]}))
    return ds("crowd", tracks=Tracks(pd.concat(rows), unit="m", dims=2))


@loader("traffic")
def traffic(max_rows=400_000):
    src = raw_dir() / "traffic" / "ngsim_i80.xlsx"
    cache = src.with_suffix(".csv")
    if not cache.exists():  # the xlsx takes minutes to parse; cache it once as csv
        pd.read_excel(src).to_csv(cache, index=False)
    d = pd.read_csv(cache, nrows=max_rows)
    cols = {c.lower(): c for c in d.columns}

    def pick(*names):
        for n in names:
            for lc, c in cols.items():
                if n in lc:
                    return d[c]
        raise KeyError(names)

    vid = pick("vehicle_id", "vehicle", "id")
    frame = pick("frame_id", "frame", "time")
    x = pick("local_x", "x")
    y = pick("local_y", "y")
    t = frame.to_numpy(dtype=float)
    if np.nanmedian(np.diff(np.unique(t))) >= 1:  # NGSIM frames are 0.1 s
        t = t / 10.0
    ft = 0.3048  # NGSIM local coordinates are in feet
    df = pd.DataFrame({"ep": "i80", "t": np.round(t, 1), "id": vid, "x": x * ft, "y": y * ft})
    return ds("traffic", tracks=Tracks(df, unit="m", dims=2))


@loader("air")
def air():
    d = pd.read_csv(raw_dir() / "air" / "opensky.csv")
    x, y = lonlat_to_m(d["lon"].to_numpy(), d["lat"].to_numpy())
    t = d["time"].to_numpy()
    df = pd.DataFrame({"ep": "europe", "t": t - t.min(), "id": d["icao24"], "x": x, "y": y})
    df = df.drop_duplicates(["t", "id"])
    return ds("air", tracks=Tracks(df, unit="m", dims=2))


@loader("drones")
def drones():
    rows = []
    pat = re.compile(r'lat="([-\d.]+)" lon="([-\d.]+)">\s*<ele>([-\d.]+)</ele>\s*<time>([^<]+)</time>')
    for f in sorted((raw_dir() / "drones").rglob("*.gpx")):
        m = re.match(r"out_(\d+)_(\d+)", f.stem)
        txt = f.read_text()
        pts = pat.findall(txt)
        if not pts:
            continue
        a = pd.DataFrame(pts, columns=["lat", "lon", "ele", "time"])
        rows.append(pd.DataFrame({"ep": f.parent.name + "-" + m.group(2), "id": int(m.group(1)),
                                  "lat": a["lat"].astype(float), "lon": a["lon"].astype(float),
                                  "z": a["ele"].astype(float), "time": pd.to_datetime(a["time"])}))
    d = pd.concat(rows)
    x, y = lonlat_to_m(d["lon"].to_numpy(), d["lat"].to_numpy())
    t = (d["time"] - d["time"].min()).dt.total_seconds().to_numpy()
    df = pd.DataFrame({"ep": d["ep"].to_numpy(), "t": np.round(t * 5) / 5, "id": d["id"].to_numpy(), "x": x, "y": y})
    df = df.drop_duplicates(["ep", "t", "id"])
    return ds("drones", tracks=Tracks(df, unit="m", dims=2))


# ---------------------------------------------------------------- spreading
@loader("covid")
def covid(n_countries=25):
    d = pd.read_csv(raw_dir() / "covid" / "confirmed.csv")
    c = d.drop(columns=["Province/State", "Lat", "Long"]).groupby("Country/Region").sum()
    c = c.loc[:, :"6/30/20"]  # first wave, before mass testing changed reporting
    top = c.iloc[:, -1].sort_values(ascending=False).index[:n_countries].tolist()
    if "Canada" not in top:
        top.append("Canada")
    series = [Series(np.arange(c.shape[1], dtype=float), c.loc[k].to_numpy(float), k, cumulative=True) for k in top]
    new = np.diff(c.loc[top].to_numpy(float), axis=1).ravel()
    return ds("covid", series=series, events=[Events(new[new > 0], "daily new cases (country-days)")])


@loader("cascade_higgs")
def cascade_higgs():
    p = next((raw_dir() / "cascade_higgs").rglob("higgs-activity_time.txt"))
    d = pd.read_csv(p, sep=" ", header=None, names=["a", "b", "ts", "kind"])
    rt = d[d.kind == "RT"]
    sizes = rt.groupby("b").size().to_numpy(float)  # retweets each user received
    t = (d.ts - d.ts.min()) / 3600.0
    counts = np.bincount(t.astype(int)).astype(float)
    return ds("cascade_higgs", series=[Series(np.arange(len(counts), dtype=float), np.cumsum(counts),
                                              "cumulative actions", cumulative=True)],
              events=[Events(sizes, "retweets received per user", None)])


@loader("cascade_15m")
def cascade_15m():
    p = next((raw_dir() / "cascade_15m").rglob("15m.csv"))
    d = pd.read_csv(p, sep=";", usecols=["idt", "segs"])
    t = d["segs"].to_numpy(float) / 3600.0
    counts = np.bincount(t.astype(int)).astype(float)
    sizes = d.groupby("idt").size().to_numpy(float)
    return ds("cascade_15m", series=[Series(np.arange(len(counts), dtype=float), np.cumsum(counts),
                                            "cumulative tweets", cumulative=True)],
              events=[Events(sizes, "tweets per user")])


# ---------------------------------------------------------------- hazards
@loader("fire")
def fire(n_growth=300):
    d = pd.read_csv(raw_dir() / "fire" / "daily.csv")
    final = d.groupby("combined.ID")["area.m2"].sum() / 1e4
    big = d.groupby("combined.ID")["days.burned"].first()
    keep = big[big >= 8].index
    keep = final.loc[keep].sort_values(ascending=False).index[:n_growth]
    series = []
    for fid in keep:
        g = d[d["combined.ID"] == fid].sort_values("Chrono.DOB")
        series.append(Series(g["Chrono.DOB"].to_numpy(float), g["area.m2.cum"].to_numpy(float) / 1e4,
                             str(fid), cumulative=True))
    return ds("fire", series=series, events=[Events(d["area.ha"].to_numpy(float), "daily area burned (ha)"),
                                             Events(final.to_numpy(float), "final fire size (ha)")])


@loader("evac")
def evac():
    d = pd.read_csv(raw_dir() / "evac" / "evac.csv", encoding="latin-1")
    per_year = d.dropna(subset=["Year"]).astype({"Year": int}).groupby("Year").size()
    full = per_year.reindex(range(per_year.index.min(), per_year.index.max() + 1), fill_value=0)
    pop = pd.to_numeric(d["Population"], errors="coerce").dropna()
    return ds("evac", series=[Series(full.index.to_numpy(float), full.to_numpy(float), "evacuations per year")],
              events=[Events(pop[pop > 0].to_numpy(float), "people evacuated per event"),
                      Events(pd.to_numeric(d["FireSize"], errors="coerce").dropna().to_numpy(float), "fire size (ha)")])


@loader("quake")
def quake():
    d = pd.read_csv(raw_dir() / "quake" / "datasetS1.txt", sep=r"\s+", comment=None)
    d.columns = [c.strip("#") for c in d.columns]
    t = pd.to_datetime(dict(year=d.YEAR, month=d.MONTH, day=d.DAY, hour=d.HOUR, minute=d.MINUTE))
    days = ((t - t.min()).dt.total_seconds() / 86400).to_numpy()
    order = np.argsort(days)
    energy = 10 ** (1.5 * d["MAGNITUDE"].to_numpy() + 4.8)  # Gutenberg-Richter energy in joules
    counts = np.bincount(days.astype(int)).astype(float)
    return ds("quake", series=[Series(np.arange(len(counts), dtype=float), counts, "quakes per day")],
              events=[Events(energy[order], "radiated energy (J)", days[order])])


@loader("sunspots")
def sunspots():
    d = pd.read_csv(raw_dir() / "sunspots" / "sunspot.month.csv")
    return ds("sunspots", series=[Series(d["time"].to_numpy(float), d["value"].to_numpy(float), "monthly sunspots")])


# ---------------------------------------------------------------- ecology
@loader("lynx")
def lynx():
    d = pd.read_csv(raw_dir() / "lynx" / "lynx.csv")
    return ds("lynx", series=[Series(d["time"].to_numpy(float), d["value"].to_numpy(float), "lynx trapped")],
              events=[Events(d["value"].to_numpy(float), "annual lynx trappings")])


@loader("birdcounts")
def birdcounts(n_species=10):
    d = pd.read_csv(raw_dir() / "birdcounts" / "bird_counts.csv")
    tot = d.groupby("species")["count"].sum().sort_values(ascending=False)
    series = []
    for sp in tot.index[:n_species]:
        g = d[d.species == sp].sort_values("year")
        series.append(Series(g["year"].to_numpy(float), g["count_per_hour"].to_numpy(float), sp))
    return ds("birdcounts", series=series, events=[Events(d.loc[d["count"] > 0, "count"].to_numpy(float),
                                                          "birds counted per species-year")])


# ---------------------------------------------------------------- socio-technical
@loader("grid")
def grid():
    d = pd.read_csv(REPO / "apps" / "energy" / "data" / "sample" / "ercot_nrel_2020.csv")
    x = d["demand_mw"].to_numpy(float)
    return ds("grid", series=[Series(np.arange(len(x), dtype=float), x, "ERCOT COAST load (MW)")],
              events=[Events(np.abs(np.diff(x)), "hourly load change (MW)")])


@loader("bikes")
def bikes():
    d = pd.read_csv(raw_dir() / "bikes" / "bikes.csv")
    return ds("bikes", series=[Series(np.arange(len(d), dtype=float), d["rides"].to_numpy(float), "daily rides")])


@loader("markets")
def markets():
    d = pd.read_csv(raw_dir() / "markets" / "EuStockMarkets.csv")
    series, ev = [], []
    for c in ["DAX", "SMI", "CAC", "FTSE"]:
        x = d[c].to_numpy(float)
        series.append(Series(np.arange(len(x), dtype=float), x, c))
        ev.append(np.abs(np.diff(np.log(x))))
    e = np.concatenate(ev)
    return ds("markets", series=series, events=[Events(e[e > 0], "absolute daily log return")])


# ---------------------------------------------------------------- cosmic (analysed in universal.cosmos)
@loader("sparc")
def sparc():
    from ..cosmos.data import sparc_rar

    g = sparc_rar()
    return ds("sparc", events=[Events(g["gobs"].to_numpy(), "observed acceleration (m/s^2)")],
              notes="analysed in universal.cosmos.rar (radial acceleration relation)")


@loader("pantheon")
def pantheon():
    from ..cosmos.data import pantheon as load

    sn = load()
    return ds("pantheon", series=[Series(sn["z"], sn["mu"], "distance modulus")],
              notes="analysed in universal.cosmos.fit")


@loader("bao")
def bao():
    from ..cosmos.data import bao as load

    b = load()
    return ds("bao", series=[Series(b["z"], b["value"], "BAO distances / r_d")], notes="analysed in universal.cosmos.fit")


@loader("chronometers")
def chronometers():
    from ..cosmos.data import chronometers as load

    c = load()
    return ds("chronometers", series=[Series(c["z"], c["H"], "H(z)")], notes="analysed in universal.cosmos.fit")


def load(key, **kw) -> Dataset:
    return LOADERS[key](**kw)


def available() -> list[str]:
    return [d["key"] for d in sources()["datasets"] if (raw_dir() / d["key"]).exists() or d["key"] == "grid"]
