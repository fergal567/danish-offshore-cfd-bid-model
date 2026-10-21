"""
Project 1 – Step 2: fast ERA5 download via the Open-Meteo Historical Weather API.

Why this exists
---------------
The Copernicus CDS queue for ERA5 single levels was jammed in Oct 2026
(~2,500 requests queued, 30 slots), so the monthly CDS route in
era5_download.py would take days. Open-Meteo serves the same ECMWF ERA5
reanalysis from its own point-optimised archive, with no queue and no
account. One request per site per year, ~40 requests in total, a few
minutes end to end.

Differences from the CDS route (era5_download.py)
-------------------------------------------------
* Grid point: the ERA5 cell nearest to the site (cell_selection=nearest),
  not a bilinear blend of the four surrounding cells. The yield notebook
  rescales the wind level to Energinet's LiDAR-based mean anyway.
* Variables arrive as wind speed + direction; converted here to u/v so the
  output CSV has exactly the same columns as era5_download.py and the
  yield notebook needs no changes.
* --validate compares Open-Meteo with any CDS month already downloaded
  (e.g. data/era5_raw/era5_HES_2025-01.nc) as a data-quality check.

Licence: Open-Meteo data are CC BY 4.0, free for non-commercial use.
Cite "Open-Meteo.com (Zippenfenig, 2023)" and "Hersbach et al. (2023),
ERA5 hourly data on single levels, Copernicus C3S CDS" in the memo.

USAGE (inside the step2 venv)
-----------------------------
    python era5_openmeteo.py                       # NSM + HES, 2006–2025
    python era5_openmeteo.py --extra-years 1995    # also 1995 (DEA AF25 weather year)
    python era5_openmeteo.py --validate            # compare with CDS months on disk

Outputs (same format as era5_download.py):
    data/era5_NSM_2006_2025.csv, data/era5_HES_2006_2025.csv
    data/era5_<SITE>_1995_1995.csv  (if --extra-years 1995)
    data/era5_openmeteo_raw/<SITE>_<year>.json  (raw responses, reused on re-runs)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from era5_download import SITES  # single source of truth for coordinates

API = "https://archive-api.open-meteo.com/v1/archive"
HOURLY = [
    "wind_speed_100m", "wind_direction_100m",
    "wind_speed_10m", "wind_direction_10m",
    "temperature_2m", "surface_pressure",
]
RAW_DIR = Path("data/era5_openmeteo_raw")
OUT_DIR = Path("data")


def fetch_year(site: str, year: int, retries: int = 5) -> dict:
    """Download one calendar year for one site (cached as JSON)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache = RAW_DIR / f"{site}_{year}.json"
    if cache.exists() and cache.stat().st_size > 1000:
        return json.loads(cache.read_text())

    cfg = SITES[site]
    params = {
        "latitude": cfg["lat"], "longitude": cfg["lon"],
        "start_date": f"{year}-01-01", "end_date": f"{year}-12-31",
        "hourly": ",".join(HOURLY),
        "models": "era5",
        "wind_speed_unit": "ms",
        "timezone": "GMT",
        "cell_selection": "nearest",
    }
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(API, params=params, timeout=120)
            if r.status_code == 429:  # rate limited – back off
                wait = 60 * attempt
                print(f"    rate limited; waiting {wait} s")
                time.sleep(wait)
                continue
            r.raise_for_status()
            data = r.json()
            if "hourly" not in data:
                raise ValueError(f"unexpected response: {str(data)[:300]}")
            cache.write_text(json.dumps(data))
            return data
        except Exception as exc:  # noqa: BLE001
            print(f"    {site} {year} attempt {attempt} failed: {exc}")
            if attempt == retries:
                raise
            time.sleep(10 * attempt)
    raise RuntimeError("unreachable")


def to_frame(data: dict) -> pd.DataFrame:
    h = data["hourly"]
    ws100, wd100 = np.asarray(h["wind_speed_100m"], float), np.asarray(h["wind_direction_100m"], float)
    ws10, wd10 = np.asarray(h["wind_speed_10m"], float), np.asarray(h["wind_direction_10m"], float)
    # Meteorological direction (where the wind comes FROM) -> u (eastward), v (northward)
    df = pd.DataFrame({
        "time_utc": pd.to_datetime(h["time"]),
        "u100": -ws100 * np.sin(np.radians(wd100)),
        "v100": -ws100 * np.cos(np.radians(wd100)),
        "u10": -ws10 * np.sin(np.radians(wd10)),
        "v10": -ws10 * np.cos(np.radians(wd10)),
        "t2m_K": np.asarray(h["temperature_2m"], float) + 273.15,
        "sp_Pa": np.asarray(h["surface_pressure"], float) * 100.0,
    })
    return df


def build(site: str, years: list[int]) -> Path:
    frames, grid = [], None
    for y in years:
        print(f"  {site} {y} …", end=" ", flush=True)
        data = fetch_year(site, y)
        grid = (data.get("latitude"), data.get("longitude"))
        df = to_frame(data)
        print(f"{len(df):,} h, mean ws100 {np.hypot(df.u100, df.v100).mean():.2f} m/s")
        frames.append(df)
    df = pd.concat(frames).drop_duplicates("time_utc").sort_values("time_utc")
    df = df.dropna(subset=["u100", "v100"])

    expected = pd.date_range(f"{years[0]}-01-01 00:00", f"{years[-1]}-12-31 23:00", freq="h")
    missing = len(expected.difference(df["time_utc"]))
    out = OUT_DIR / f"era5_{site}_{years[0]}_{years[-1]}.csv"
    df.to_csv(out, index=False, float_format="%.4f")
    print(f"[{site}] wrote {out}  rows={len(df):,}  missing hours={missing:,}  "
          f"ERA5 cell used: {grid[0]} N, {grid[1]} E  (site {SITES[site]['lat']}, {SITES[site]['lon']})")
    return out


def validate() -> None:
    """Compare Open-Meteo with CDS months already on disk (bilinear 4-point CDS vs nearest cell)."""
    from era5_download import _open  # noqa: PLC0415
    raw = sorted(Path("data/era5_raw").glob("era5_*_*.nc"))
    if not raw:
        print("No CDS files in data/era5_raw – nothing to validate.")
        return
    rows = []
    for p in raw:
        site, tag = p.stem.split("_")[1], p.stem.split("_")[2]
        year = int(tag[:4])
        ds = _open(p).sortby("latitude").sortby("longitude")
        pt = ds.interp(latitude=SITES[site]["lat"], longitude=SITES[site]["lon"])
        cds = pd.Series(np.hypot(pt.u100.values, pt.v100.values),
                        index=pd.to_datetime(pt.time.values), name="cds")
        om = to_frame(fetch_year(site, year)).set_index("time_utc")
        om = np.hypot(om.u100, om.v100).rename("openmeteo")
        j = pd.concat([cds, om], axis=1, join="inner").dropna()
        rows.append({"file": p.name, "hours": len(j),
                     "CDS mean ws100": j.cds.mean(), "Open-Meteo mean ws100": j.openmeteo.mean(),
                     "ratio": j.openmeteo.mean() / j.cds.mean(),
                     "hourly correlation": j.cds.corr(j.openmeteo)})
    print(pd.DataFrame(rows).round(3).to_string(index=False))
    print("\nExpect correlation > 0.97 and ratio within ~0.97–1.03 (nearest cell vs 4-cell blend).")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", type=int, default=2006)
    ap.add_argument("--end", type=int, default=2025)
    ap.add_argument("--sites", nargs="+", default=list(SITES), choices=list(SITES))
    ap.add_argument("--extra-years", nargs="*", type=int, default=[],
                    help="single years written to separate files, e.g. 1995 for the DEA AF25 weather year")
    ap.add_argument("--validate", action="store_true",
                    help="only compare with CDS NetCDF months in data/era5_raw")
    args = ap.parse_args()

    if args.validate:
        validate()
        return
    for site in args.sites:
        build(site, list(range(args.start, args.end + 1)))
        for y in args.extra_years:
            build(site, [y])
    print("\nDone. Next: upload data/era5_NSM_2006_2025.csv and data/era5_HES_2006_2025.csv.")


if __name__ == "__main__":
    sys.exit(main())
