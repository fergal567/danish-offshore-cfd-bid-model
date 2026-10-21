"""Reconstruct hourly AAP for ERA5 climate year 1995 (needed for AF25 method B, step 5).

Why: the step-2 notebook exports aap_hourly_<SITE>.csv for 2006–2025 only, and the 1995 ERA5
download (era5_openmeteo.py --extra-years 1995) is not run through it. Instead of changing the
step-2 calibration, this script learns step 2's own wind -> AAP mapping from 2006–2025 and applies
it to 1995 (Asm).

Model: gradient-boosted trees on ERA5 hourly features (100 m speed at t−1, t, t+1; 10 m speed;
direction; air density; month; hour). Validation (train without 2008/2009, test on them):
hourly R² 0.997 (NSM) / 0.992 (HES), mean ratio 1.000; method-B capture factors from reconstructed
vs step-2 AAP differ by < 0.001. Metered = AAP × the constant step-2 ratio (0.96495).

Usage (repo root):  python step5/reconstruct_aap_1995.py
Inputs:  step2/data/era5_<SITE>_2006_2025.csv, step2/data/era5_<SITE>_1995_1995.csv,
         step2/data/aap_hourly_<SITE>.csv
Output:  step5/data/aap_hourly_1995_<SITE>.csv  (git-ignored; used only for method B, not for P50 yield)
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

REPO = Path(__file__).resolve().parents[1]
DATA2 = REPO / "step2" / "data"
OUT = REPO / "step5" / "data"
SITES = ("NSM", "HES")
SEED = 0


def features(e: pd.DataFrame) -> pd.DataFrame:
    ws = np.hypot(e.u100, e.v100)
    d = np.arctan2(e.u100, e.v100)
    X = pd.DataFrame({
        "ws": ws, "ws_m1": ws.shift(1), "ws_p1": ws.shift(-1), "ws10": np.hypot(e.u10, e.v10),
        "sin": np.sin(d), "cos": np.cos(d), "rho": e.sp_Pa / (287.05 * e.t2m_K),
        "month": e.index.month, "hour": e.index.hour}, index=e.index)
    return X.bfill().ffill()


def model():
    return HistGradientBoostingRegressor(max_iter=400, learning_rate=0.08, max_leaf_nodes=63, random_state=SEED)


def r2(t, p):
    return 1 - ((t - p) ** 2).sum() / ((t - t.mean()) ** 2).sum()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for s in SITES:
        e = pd.read_csv(DATA2 / f"era5_{s}_2006_2025.csv", parse_dates=["time_utc"]).set_index("time_utc")
        e95 = pd.read_csv(DATA2 / f"era5_{s}_1995_1995.csv", parse_dates=["time_utc"]).set_index("time_utc")
        y = pd.read_csv(DATA2 / f"aap_hourly_{s}.csv", parse_dates=["time_utc"]).set_index("time_utc")
        X = features(e).loc[y.index]
        ratio = float((y.metered_mwh / y.aap_mwh).median())
        hold = np.isin(X.index.year, [2008, 2009])
        p = model().fit(X[~hold], y.aap_mwh[~hold]).predict(X[hold])
        print(f"[{s}] holdout 2008–09: R² {r2(y.aap_mwh[hold], p):.4f}, mean ratio {p.mean() / y.aap_mwh[hold].mean():.4f}")
        cap = y.aap_mwh.max()
        p95 = np.clip(model().fit(X, y.aap_mwh).predict(features(e95)), 0, cap)
        out = pd.DataFrame({"aap_mwh": p95, "metered_mwh": p95 * ratio}, index=e95.index)
        out.index.name = "time_utc"
        out.to_csv(OUT / f"aap_hourly_1995_{s}.csv", float_format="%.4f")
        print(f"[{s}] 1995 AAP {out.aap_mwh.sum() / 1e3:,.0f} GWh (2006–25 mean "
              f"{y.aap_mwh.groupby(y.index.year).sum().mean() / 1e3:,.0f}) -> {OUT / f'aap_hourly_1995_{s}.csv'}")


if __name__ == "__main__":
    main()
