"""Fit LCDM, its standard extensions and the swarm-universe models to real expansion data.

Data (all public, see universal/sources.yaml):
  * Pantheon+ SNe Ia (1,580 at z > 0.01 without Cepheid hosts, full STAT+SYS covariance;
    the absolute magnitude is marginalised analytically, so SNe constrain shape only)
  * DESI DR2 BAO (13 numbers with covariance), r_d free unless the CMB ruler is added
  * cosmic chronometers H(z) (15 Moresco BC03 points, diagonal errors)
  * optional early-universe ruler: r_d = 147.09 +- 0.26 Mpc (Planck 2018, TT,TE,EE+lowE+lensing)

    python -m universal.cosmos.fit       # writes results/universal/cosmology.{json,md} and plots
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

from . import data
from .models import C_KMS, MODELS, E, comoving, w_eff

OUT = Path(__file__).resolve().parents[2] / "results" / "universal"
RD_PLANCK = (147.09, 0.26)
H0_SH0ES = (73.04, 1.04)  # Riess et al. 2022


class Likelihood:
    def __init__(self, use_rd_prior: bool):
        sn = data.pantheon()
        self.sn_z, self.sn_zhel, self.sn_mb = sn["z"], sn["zhel"], sn["mb"]
        self.sn_cinv = np.linalg.inv(sn["cov"])
        self.sn_sum = self.sn_cinv.sum()
        b = data.bao()
        self.bao_z, self.bao_v, self.bao_kind = b["z"], b["value"], b["kind"]
        self.bao_cinv = np.linalg.inv(b["cov"])
        c = data.chronometers()
        self.cc_z, self.cc_H, self.cc_e = c["z"], c["H"], c["err"]
        self.use_rd_prior = use_rd_prior
        self.n = len(self.sn_z) + len(self.bao_z) + len(self.cc_z) + (1 if use_rd_prior else 0)

    def parts(self, Om, h, rd, model, p):
        # supernovae: offset (M and H0) marginalised analytically
        dl = (1 + self.sn_zhel) * comoving(self.sn_z, Om, h, model, p)
        d = self.sn_mb - 5 * np.log10(dl)
        cd = self.sn_cinv @ d
        chi_sn = float(d @ cd - cd.sum() ** 2 / self.sn_sum)
        # BAO
        dm = comoving(self.bao_z, Om, h, model, p)
        dh = C_KMS / (100 * h * E(self.bao_z, Om, h, model, p))
        th = []
        for z, k, m, hh in zip(self.bao_z, self.bao_kind, dm, dh):
            th.append({"DM_over_rs": m, "DH_over_rs": hh, "DV_over_rs": (z * m * m * hh) ** (1 / 3)}[k] / rd)
        r = self.bao_v - np.array(th)
        chi_bao = float(r @ self.bao_cinv @ r)
        # chronometers
        chi_cc = float(np.sum(((self.cc_H - 100 * h * E(self.cc_z, Om, h, model, p)) / self.cc_e) ** 2))
        chi_rd = ((rd - RD_PLANCK[0]) / RD_PLANCK[1]) ** 2 if self.use_rd_prior else 0.0
        return {"sn": chi_sn, "bao": chi_bao, "cc": chi_cc, "rd_prior": chi_rd}

    def chi2(self, theta, model):
        names = list(MODELS[model]["params"])
        Om, h, rd = theta[:3]
        p = dict(zip(names, theta[3:]))
        try:
            c = self.parts(Om, h, rd, model, p)
            v = sum(c.values())
            return v if np.isfinite(v) else 1e12
        except Exception:
            return 1e12


def fit_model(L: Likelihood, model: str, n_starts: int = 16, seed: int = 0) -> dict:
    spec = MODELS[model]
    names = list(spec["params"])
    bounds = [(0.1, 0.6), (0.5, 0.9), (120.0, 175.0)] + [spec["bounds"][k] for k in names]
    rng = np.random.default_rng(seed)
    starts = [np.r_[0.31, 0.68, 147.0, [spec["params"][k] for k in names]]]
    for _ in range(n_starts - 1):
        starts.append(np.array([rng.uniform(lo, hi) for lo, hi in bounds]))
    best = None
    for s in starts:
        r = minimize(L.chi2, s, args=(model,), method="L-BFGS-B", bounds=bounds)
        r2 = minimize(L.chi2, r.x, args=(model,), method="Nelder-Mead",
                      options={"maxiter": 4000, "xatol": 1e-6, "fatol": 1e-6})
        x = np.clip(r2.x, [b[0] for b in bounds], [b[1] for b in bounds])
        v = L.chi2(x, model)
        if best is None or v < best[1]:
            best = (x, v)
    x, chi = best
    k = len(x) - (0 if not L.use_rd_prior else 0)
    p = dict(zip(names, x[3:]))
    parts = L.parts(x[0], x[1], x[2], model, p)
    out = {"model": model, "chi2": float(chi), "k": int(k), "n": L.n,
           "aic": float(chi + 2 * k), "bic": float(chi + k * np.log(L.n)),
           "Om": float(x[0]), "H0": float(100 * x[1]), "rd": float(x[2]),
           "params": {k_: float(v) for k_, v in p.items()}, "chi2_parts": parts,
           "w_eff": {str(z): float(w_eff(z, model, p)) for z in [0.0, 0.5, 1.0, 2.0]}}
    out["errors"] = _errors(L, model, x, bounds)
    return out


def _errors(L, model, x, bounds, rel=1e-3):
    """1-sigma errors from the numerical Hessian of chi2 (Laplace approximation)."""
    n = len(x)
    H = np.zeros((n, n))
    step = np.array([max(abs(v) * rel, 1e-4) for v in x])
    f0 = L.chi2(x, model)
    for i in range(n):
        for j in range(i, n):
            ei, ej = np.eye(n)[i] * step[i], np.eye(n)[j] * step[j]
            fpp = L.chi2(x + ei + ej, model)
            fpm = L.chi2(x + ei - ej, model)
            fmp = L.chi2(x - ei + ej, model)
            fmm = L.chi2(x - ei - ej, model)
            H[i, j] = H[j, i] = (fpp - fpm - fmp + fmm) / (4 * step[i] * step[j])
    names = ["Om", "h", "rd"] + list(MODELS[model]["params"])
    try:
        cov = 2 * np.linalg.inv(H)
        d = np.sqrt(np.clip(np.diag(cov), 0, None))
        return {k: float(v) for k, v in zip(names, d)}
    except np.linalg.LinAlgError:
        return {k: None for k in names}
    finally:
        _ = f0


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    res = {}
    for label, prior in [("late (SN+BAO+CC, r_d free)", False), ("late + CMB ruler r_d", True)]:
        L = Likelihood(prior)
        rows = []
        for m in MODELS:
            n_starts = 30 if m.startswith("SU-C") else 12
            r = fit_model(L, m, n_starts=n_starts)
            print(label, m, round(r["chi2"], 2), "H0", round(r["H0"], 2), r["params"], flush=True)
            rows.append(r)
        base = rows[0]
        for r in rows:
            r["dAIC_vs_LCDM"] = r["aic"] - base["aic"]
            r["dBIC_vs_LCDM"] = r["bic"] - base["bic"]
            e = r["errors"].get("h")
            if e:
                sig = np.hypot(100 * e, H0_SH0ES[1])
                r["H0_tension_sigma_vs_SH0ES"] = float((H0_SH0ES[0] - r["H0"]) / sig)
        res[label] = rows
    (OUT / "cosmology.json").write_text(json.dumps(res, indent=1))
    _report(res)
    _plots(res)
    return res


def _report(res):
    L = ["# Swarm-universe cosmology: fits to real expansion data", "",
         "Generated by `python -m universal.cosmos.fit`. Pantheon+ (1,580 SNe, full covariance, "
         "magnitude offset marginalised), DESI DR2 BAO (13 numbers, covariance), 15 cosmic-chronometer H(z) points. "
         "Best fits by multi-start optimisation; errors from the chi2 Hessian (approximate). "
         "Negative dAIC/dBIC favours the model over LCDM; |dAIC| < 2 is no real preference, "
         "BIC penalises extra parameters harder.", ""]
    for label, rows in res.items():
        L += [f"## {label}", "",
              "| Model | chi2 | k | dAIC | dBIC | Om | H0 | r_d | extra parameters | w(z=0) | w(z=1) | H0 tension vs SH0ES |",
              "| :-- | --: | --: | --: | --: | --: | --: | --: | :-- | --: | --: | --: |"]
        for r in rows:
            e = r["errors"]
            ex = ", ".join(f"{k}={v:.3g}" + (f"±{e.get(k):.2g}" if e.get(k) else "") for k, v in r["params"].items())
            ten = r.get("H0_tension_sigma_vs_SH0ES")
            L.append(f"| {r['model']} | {r['chi2']:.1f} | {r['k']} | {r['dAIC_vs_LCDM']:+.1f} | {r['dBIC_vs_LCDM']:+.1f} "
                     f"| {r['Om']:.3f}" + (f"±{e['Om']:.3f}" if e.get("Om") else "") + f" | {r['H0']:.1f}"
                     + (f"±{100 * e['h']:.1f}" if e.get("h") else "") + f" | {r['rd']:.1f} | {ex or '-'} "
                     f"| {r['w_eff']['0.0']:.2f} | {r['w_eff']['1.0']:.2f} | "
                     + (f"{ten:.1f} sigma" if ten is not None else "-") + " |")
        L.append("")
        L.append("chi2 by dataset (SN / BAO / CC / r_d prior): " + "; ".join(
            f"{r['model'].split(' ')[0]} {r['chi2_parts']['sn']:.1f} / {r['chi2_parts']['bao']:.1f} / "
            f"{r['chi2_parts']['cc']:.1f} / {r['chi2_parts']['rd_prior']:.1f}" for r in rows))
        L.append("")
    (OUT / "cosmology.md").write_text("\n".join(L))


def _plots(res):
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    z = np.linspace(0, 2.5, 200)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    rows = res["late + CMB ruler r_d"]
    for r in rows:
        p = r["params"]
        ax[0].plot(z, w_eff(z, r["model"], p), label=r["model"])
        a = 1 / (1 + z)
        f = MODELS[r["model"]]["f"](a, p)
        ax[1].plot(z, (1 - r["Om"]) * f, label=r["model"])
    ax[0].axhline(-1, color="k", lw=0.5)
    ax[0].set(xlabel="z", ylabel="w_eff(z)", title="Dark-energy equation of state", ylim=(-3, 1))
    ax[1].set(xlabel="z", ylabel="Omega_DE0 f(a)", title="Dark-energy density relative to today's critical")
    ax[0].legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "cosmology_w.png", dpi=130)


if __name__ == "__main__":
    run()
