"""Applied test: real human bottlenecks (study stage 8, first step).

Two real datasets, both CC BY 4.0:

* Pedestrians (Juelich HERMES 2009, Zenodo 1054017): 150 people leave a 1.8 m wide corridor
  through an exit of width 0.7, 0.95, 1.2 or 1.8 m. Units cm, 16 frames/s.
* Vehicles (DRaT 2025, Zenodo 20171110): drone-tracked cars where a highway narrows from four
  lanes to three, with a free-flow and a congested period. 8 samples/s.

Questions:
1. Does a crowd at an exit behave like the flocks (spacing rule, neighbours, fluid fit)?
2. Is a more ordered (polarised) crowd followed by more flow through the exit?
3. Do flock terms (match the speed of your k nearest, stay with the group) describe real
   drivers better than a standard car-following rule that only looks at the car ahead?
   Fit on the first half of each period, scored on the second half.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .fields import fit_equation
from .io import Tracks
from .kinematics import derivatives, group_order, summary
from .rules import distance_response, topological_vs_metric

# ---------------------------------------------------------------- pedestrians

PED_FPS = 16.0
EXIT_Y_CM = -450.0         # exit line, found from where the walkable width narrows (y about -500 cm)


def load_ped(path: Path) -> Tracks:
    a = np.loadtxt(path)
    ids, col = np.unique(a[:, 0].astype(int), return_inverse=True)
    fr = a[:, 1].astype(int)
    fr -= fr.min()
    pos = np.full((fr.max() + 1, len(ids), 2), np.nan)
    pos[fr, col] = a[:, 2:4] / 100.0
    width = int(path.stem.split("-")[-1]) / 100.0
    return Tracks(pos, 1 / PED_FPS, f"pedestrians_exit_{width:.2f}m", 0.45,   # 0.45 m: typical shoulder width
                  {"exit_width_m": width, "species": "human", "source": "ped-bottleneck-2009"})


def exit_flow(tr: Tracks) -> dict:
    """People per second through the exit in the steady phase (10th to 90th percentile of crossings)."""
    y = tr.pos[..., 1]
    cross = []
    for i in range(tr.N):
        yi = y[:, i]
        ok = np.isfinite(yi)
        idx = np.where(ok[:-1] & ok[1:] & (yi[:-1] > EXIT_Y_CM / 100) & (yi[1:] <= EXIT_Y_CM / 100))[0]
        if len(idx):
            cross.append(idx[0] * tr.dt)
    cross = np.sort(cross)
    lo, hi = np.percentile(cross, [10, 90])
    n = np.sum((cross >= lo) & (cross <= hi))
    J = (n - 1) / (hi - lo)
    w = tr.meta["exit_width_m"]
    return {"people_through": int(len(cross)), "flow_per_s": float(J), "specific_flow_per_m_s": float(J / w),
            "crossing_times": cross.tolist()}


def order_vs_flow(tr: Tracks, window_s: float = 2.0, lead_s: float = 1.0) -> dict:
    """Correlation between polarisation of people waiting before the exit and exit flow just after."""
    x, v, _ = derivatives(tr, window_s=0.5)
    y = x[..., 1]
    near = (y > EXIT_Y_CM / 100) & (y < EXIT_Y_CM / 100 + 3.0)      # 3 m queue in front of the exit
    xs = np.where(near[..., None], x, np.nan)
    vs = np.where(near[..., None], v, np.nan)
    P = group_order(xs, vs)["polarisation"]
    cross = np.array(exit_flow(tr)["crossing_times"])
    w = int(window_s / tr.dt)
    lead = int(lead_s / tr.dt)
    pol, flow = [], []
    for t0 in range(0, tr.T - w - lead, w):
        n_near = np.nanmean(np.sum(near[t0:t0 + w], axis=1))
        if n_near < 5:
            continue
        pol.append(np.nanmean(P[t0:t0 + w]))
        a, b = (t0 + lead) * tr.dt, (t0 + lead + w) * tr.dt
        flow.append(np.sum((cross >= a) & (cross < b)) / window_s)
    pol, flow = np.array(pol), np.array(flow)
    ok = np.isfinite(pol)
    r = float(np.corrcoef(pol[ok], flow[ok])[0, 1]) if ok.sum() > 5 else None
    return {"windows": int(ok.sum()), "corr_polarisation_next_flow": r,
            "mean_polarisation_queue": float(np.nanmean(pol))}


def run_pedestrians(raw: Path) -> list[dict]:
    out = []
    for f in sorted((raw / "bn").glob("uo-*.txt")):
        tr = load_ped(f)
        nn_bl = None
        r = {"recording": tr.name, "exit_width_m": tr.meta["exit_width_m"], "summary": summary(tr),
             "flow": {k: v for k, v in exit_flow(tr).items() if k != "crossing_times"},
             "order_vs_flow": order_vs_flow(tr), "neighbours": topological_vs_metric(tr),
             "spacing": distance_response(tr)}
        nn_bl = r["summary"]["median_nn_distance_m"] / tr.body_length
        r["equation_2nn"] = fit_equation(tr, sigma_bl=2 * nn_bl, cell_bl=nn_bl, max_frames=1500)
        out.append(r)
        print(tr.name, "done")
    return out


# ---------------------------------------------------------------- vehicles

def load_cars(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path)
    d["y"] = d["local_y_ft"] * 0.3048
    x = d["local_x_ft"] * 0.3048
    slope = np.polyfit(d["y"], x, 1)[0]              # road runs at a slight angle in the sensor frame
    d["lat"] = x - slope * d["y"]                     # lateral position across the road
    d["t"] = d["timestamp"] - d["timestamp"].min()
    d = d[(d["speed_mps"] < 50)].copy()               # drop a few impossible speeds (detector glitches)
    # direction of travel along y
    g = d.sort_values("t").groupby("track_id")
    sign = np.sign(np.nanmedian(g["y"].last() - g["y"].first()))
    d["s"] = d["y"] * sign                            # distance along the road, increasing in travel direction
    return d


def car_samples(d: pd.DataFrame, k: int = 6, horizon: float = 1.0, max_range: float = 60.0) -> pd.DataFrame:
    """Per vehicle and time: gap to leader in lane, speeds, k-nearest mean speed, and acceleration
    over the next `horizon` seconds (from the tracked speed)."""
    d = d.sort_values(["track_id", "t"]).copy()
    # speeds from video tracking have spikes: rolling median then mean over about 1 s per vehicle
    d["speed_mps"] = (d.groupby("track_id")["speed_mps"]
                      .transform(lambda x: x.rolling(9, center=True, min_periods=3).median()
                                 .rolling(5, center=True, min_periods=2).mean()))
    # future speed from each track
    fut = []
    for _, g in d.groupby("track_id"):
        tt, vv = g["t"].to_numpy(), g["speed_mps"].to_numpy()
        fut.append(np.interp(tt + horizon, tt, vv, right=np.nan))
    d["v_future"] = np.concatenate(fut)
    d["a_next"] = (d["v_future"] - d["speed_mps"]) / horizon
    rows = []
    for t, g in d.groupby(np.round(d["t"], 2)):
        if len(g) < 3:
            continue
        s, lat, v, L = g["s"].to_numpy(), g["lat"].to_numpy(), g["speed_mps"].to_numpy(), g["length_m"].to_numpy()
        ds = s[None, :] - s[:, None]                  # ds[i, j] = s_j - s_i
        dl = np.abs(lat[None, :] - lat[:, None])
        np.fill_diagonal(ds, np.nan)
        ahead_same = (ds > 0) & (dl < 1.8)
        gap = np.where(ahead_same, ds, np.inf).min(1)
        lead = np.where(ahead_same, ds, np.inf).argmin(1)
        dist = np.hypot(np.nan_to_num(ds, nan=np.inf), dl)
        np.fill_diagonal(dist, np.inf)
        kk = min(k, len(g) - 1)
        nbr = np.argsort(dist, 1)[:, :kk]
        mask = np.take_along_axis(dist, nbr, 1) < max_range
        vk = np.where(mask, v[nbr], np.nan)
        sk = np.where(mask, np.take_along_axis(np.nan_to_num(ds), nbr, 1), np.nan)
        for i in range(len(g)):
            if not np.isfinite(gap[i]) or gap[i] > max_range or not mask[i].any():
                continue
            rows.append((t, g["track_id"].iloc[i], v[i], gap[i] - 0.5 * (L[i] + L[lead[i]]), v[i] - v[lead[i]],
                         np.nanmean(vk[i]) - v[i], np.nanmean(sk[i]), g["a_next"].iloc[i]))
    S = pd.DataFrame(rows, columns=["t", "id", "v", "gap", "dv", "align", "centre", "a"]).dropna()
    # physically plausible samples only (cars rarely exceed 4 m/s^2; larger values are tracking errors)
    return S[(S["a"].abs() < 4) & (S["dv"].abs() < 15) & (S["align"].abs() < 15) & (S["gap"] > 0)]


def fit_drivers(S: pd.DataFrame) -> dict:
    """Car-following vs car-following + flock terms. Fit on the first half of the period, scored on the second.

    Car-following (Helly model, linear): a = c0 + c1 gap + c2 v + c3 (v_leader - v). It looks only at the car ahead.
    Flock terms add: match the mean speed of the k nearest vehicles in any lane (alignment) and move toward their
    centre (cohesion), the two rules measured in the bird flocks.
    """
    split = S["t"].median()
    tr, te = S[S["t"] <= split], S[S["t"] > split]
    base_cols = ["gap", "v", "dv"]
    flock_cols = base_cols + ["align", "centre"]

    def r2(cols):
        X = np.column_stack([np.ones(len(tr))] + [tr[c].to_numpy() for c in cols])
        if "dv" in cols:
            X[:, 1 + cols.index("dv")] *= -1            # use v_leader - v
        coef, *_ = np.linalg.lstsq(X, tr["a"].to_numpy(), rcond=None)
        Xt = np.column_stack([np.ones(len(te))] + [te[c].to_numpy() for c in cols])
        if "dv" in cols:
            Xt[:, 1 + cols.index("dv")] *= -1
        y = te["a"].to_numpy()
        res = y - Xt @ coef
        return float(1 - np.sum(res ** 2) / np.sum((y - y.mean()) ** 2)), dict(zip(["const"] + cols, map(float, coef)))

    r_base, c_base = r2(base_cols)
    r_align, c_align = r2(base_cols + ["align"])
    r_flock, c_flock = r2(flock_cols)
    return {"samples_train": int(len(tr)), "samples_test": int(len(te)),
            "car_following": {"r2_test": r_base, "coef": c_base},
            "plus_alignment": {"r2_test": r_align, "coef": c_align},
            "plus_alignment_and_cohesion": {"r2_test": r_flock, "coef": c_flock}}


def run_cars(raw: Path) -> dict:
    d = load_cars(raw / "drone_GT.csv")
    # split the recording into free-flow and congested minutes by median speed
    minute = (d["t"] // 60).astype(int)
    speed = d.groupby(minute)["speed_mps"].median()
    d["regime"] = np.where(minute.map(speed) < 15, "congested", "free flow")
    out = {}
    for regime, g in d.groupby("regime"):
        S = car_samples(g)
        dens = g.groupby(np.round(g["t"], 1))["track_id"].nunique().mean() / (g["s"].max() - g["s"].min()) * 1000
        out[regime] = {"minutes": int(minute[g.index].nunique()), "vehicles": int(g["track_id"].nunique()),
                       "median_speed_m_s": float(g["speed_mps"].median()), "density_veh_per_km_all_lanes": float(dens),
                       **fit_drivers(S)}
        print(regime, "done")
    return out
