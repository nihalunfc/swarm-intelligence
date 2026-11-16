"""Readers for the cosmic datasets (Pantheon+, DESI DR2 BAO, cosmic chronometers, SPARC)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..fetch import raw_dir


def pantheon(zmin=0.01):
    """Pantheon+ SNe Ia without the SH0ES Cepheid calibrators (H0 is then degenerate with M)."""
    d = raw_dir() / "pantheon"
    t = pd.read_csv(d / "Pantheon+SH0ES.dat", sep=r"\s+")
    raw = np.loadtxt(d / "Pantheon+SH0ES_STAT+SYS.cov")
    n = int(raw[0])
    cov = raw[1:].reshape(n, n)
    keep = (t["zHD"].to_numpy() > zmin) & (t["IS_CALIBRATOR"].to_numpy() == 0)
    idx = np.where(keep)[0]
    return {"z": t["zHD"].to_numpy()[idx], "zhel": t["zHEL"].to_numpy()[idx],
            "mb": t["m_b_corr"].to_numpy()[idx], "mu": t["MU_SH0ES"].to_numpy()[idx],
            "cov": cov[np.ix_(idx, idx)]}


def bao():
    d = raw_dir() / "bao"
    rows = [ln.split() for ln in open(d / "mean.txt") if not ln.startswith("#") and ln.strip()]
    return {"z": np.array([float(r[0]) for r in rows]), "value": np.array([float(r[1]) for r in rows]),
            "kind": [r[2] for r in rows], "cov": np.loadtxt(d / "cov.txt")}


def chronometers():
    t = pd.read_csv(raw_dir() / "chronometers" / "HzTable_MM_BC03.dat", comment="#", header=None,
                    names=["z", "H", "err", "stat", "met", "ref"])
    return {"z": t["z"].to_numpy(float), "H": t["H"].to_numpy(float), "err": t["err"].to_numpy(float)}


def sparc_rar(ups_disk=0.5, ups_bul=0.7, max_rel_err=0.1, min_inc=30.0, max_q=2):
    """Radial acceleration relation points, with the selection of Lelli et al. 2017."""
    base = raw_dir() / "sparc"
    meta = {}
    for ln in open(base / "SPARC_Lelli2016c.mrt").read().splitlines()[98:]:
        f = ln.split()
        if len(f) >= 18:
            meta[f[0]] = (float(f[5]), int(f[17]))
    rows = []
    kpc = 3.0857e19
    for p in sorted(base.rglob("*_rotmod.dat")):
        name = p.name.replace("_rotmod.dat", "")
        inc, q = meta.get(name, (90.0, 1))
        if inc < min_inc or q > max_q:
            continue
        a = np.loadtxt(p, comments="#")
        if a.ndim == 1:
            a = a[None]
        r, v, e, vg, vd, vb = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4], a[:, 5]
        ok = (r > 0) & (v > 0) & (e / np.maximum(v, 1e-9) < max_rel_err)
        vbar2 = vg * np.abs(vg) + ups_disk * vd * np.abs(vd) + ups_bul * vb * np.abs(vb)
        gobs = (v * 1e3) ** 2 / (r * kpc)
        gbar = vbar2 * 1e6 / (r * kpc)
        ok &= gbar > 0
        for i in np.where(ok)[0]:
            rows.append((name, r[i], gobs[i], gbar[i], 2 * e[i] / v[i]))
    return pd.DataFrame(rows, columns=["galaxy", "r_kpc", "gobs", "gbar", "rel_err_g"])
