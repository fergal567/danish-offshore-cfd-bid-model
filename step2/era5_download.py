"""
Project 1 – Step 2: download hourly ERA5 wind for Nordsøen Midt and Hesselø.

Run on your own laptop (not in Claude). It:
  1. requests ERA5 single-level data (100 m and 10 m u/v wind, 2 m temperature,
     surface pressure) for the 2x2 grid box around each site, one year per request;
  2. keeps the raw NetCDF files in data/era5_raw/;
  3. bilinearly interpolates to the site coordinate and writes one CSV per site:
       data/era5_NSM_<y0>_<y1>.csv  and  data/era5_HES_<y0>_<y1>.csv
     These two CSVs (~8–10 MB each) are what you upload for the yield notebook.

-----------------------------------------------------------------------------
ONE-OFF SETUP (Copernicus Climate Data Store, CDS)
-----------------------------------------------------------------------------
1. Create a free ECMWF account at https://cds.climate.copernicus.eu  (top right:
   "Login - Register").
2. Accept the dataset licence: open the dataset page
   https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels
   -> "Download" tab -> scroll to "Terms of use" -> accept
   "Licence to use Copernicus Products". Requests fail with a 403 until you do.
3. Copy your Personal Access Token from your CDS profile page
   (https://cds.climate.copernicus.eu/profile).
4. Create the file  ~/.cdsapirc  (Windows: C:\\Users\\<you>\\.cdsapirc) containing
   exactly two lines:
       url: https://cds.climate.copernicus.eu/api
       key: <YOUR-PERSONAL-ACCESS-TOKEN>
5. Install packages (a fresh venv/conda env is a good idea):
       pip install "cdsapi>=0.7.4" xarray netCDF4 pandas numpy

USAGE
       python era5_download.py                      # 2006–2025, both sites
       python era5_download.py --start 2016 --end 2025
       python era5_download.py --sites HES --chunk month   # if a yearly request is refused

Requests are queued at CDS; expect minutes to hours in total. The script skips
files that already exist, so you can stop it and re-run.
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Site coordinates (WGS84). See step-2 notes for sources.
#  NSM: ASSUMPTION – representative point in Energinet's sub-area A2
#       (Nordsøen I Midt), ~20 km off Hvide Sande. Replace with the centroid of
#       Appendix 2 coordinates once available.
#  HES: centroid of Energinet/EMD siting positions HS-A, HS-B, HS-C (the three
#       corners of the Hesselø South OWF area), EMD Site Wind Conditions
#       Assessment rev. 3 (23 Dec 2025), Table 25.
# ---------------------------------------------------------------------------
SITES = {
    "NSM": {"name": "Nordsøen Midt (North Sea I Mid, DK1)", "lat": 56.00, "lon": 7.55},
    "HES": {"name": "Hesselø (Hesselø South area, DK2)", "lat": 56.352, "lon": 11.698},
}

DATASET = "reanalysis-era5-single-levels"
VARIABLES = [
    "100m_u_component_of_wind",
    "100m_v_component_of_wind",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "2m_temperature",
    "surface_pressure",
]
GRID = 0.25  # ERA5 native grid spacing (degrees)

RAW_DIR = Path("data/era5_raw")
OUT_DIR = Path("data")


def grid_box(lat: float, lon: float) -> list[float]:
    """Return CDS 'area' [N, W, S, E] covering the four grid points around the site."""
    s = math.floor(lat / GRID) * GRID
    n = math.ceil(lat / GRID) * GRID
    w = math.floor(lon / GRID) * GRID
    e = math.ceil(lon / GRID) * GRID
    if n == s:
        n += GRID
    if e == w:
        e += GRID
    return [round(n, 3), round(w, 3), round(s, 3), round(e, 3)]


def build_request(year: int, months: list[int], area: list[float]) -> dict:
    return {
        "product_type": ["reanalysis"],
        "variable": VARIABLES,
        "year": [str(year)],
        "month": [f"{m:02d}" for m in months],
        "day": [f"{d:02d}" for d in range(1, 32)],
        "time": [f"{h:02d}:00" for h in range(24)],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": area,
    }


def download(site: str, start: int, end: int, chunk: str, retries: int = 3) -> list[Path]:
    import cdsapi  # imported here so --postprocess-only works without cdsapi

    client = cdsapi.Client()
    cfg = SITES[site]
    area = grid_box(cfg["lat"], cfg["lon"])
    print(f"[{site}] {cfg['name']}  site=({cfg['lat']}, {cfg['lon']})  area N,W,S,E={area}")
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    files = []
    for year in range(start, end + 1):
        month_groups = [list(range(1, 13))] if chunk == "year" else [[m] for m in range(1, 13)]
        for months in month_groups:
            tag = f"{year}" if chunk == "year" else f"{year}-{months[0]:02d}"
            target = RAW_DIR / f"era5_{site}_{tag}.nc"
            files.append(target)
            if target.exists() and target.stat().st_size > 0:
                print(f"  {target.name} exists – skipping")
                continue
            for attempt in range(1, retries + 1):
                try:
                    print(f"  requesting {target.name} (attempt {attempt})")
                    client.retrieve(DATASET, build_request(year, months, area)).download(str(target))
                    break
                except Exception as exc:  # noqa: BLE001 – report and retry
                    print(f"    failed: {exc}")
                    if attempt == retries:
                        print("    giving up on this chunk; re-run later or use --chunk month")
                    else:
                        time.sleep(30 * attempt)
    return files


def _open(path: Path):
    import xarray as xr

    ds = xr.open_dataset(path)
    # New CDS NetCDF uses 'valid_time'; older files use 'time'.
    if "valid_time" in ds.dims or "valid_time" in ds.coords:
        ds = ds.rename({"valid_time": "time"})
    # Drop helper coords that appear in some new-CDS files.
    for c in ("number", "expver"):
        if c in ds.coords and c not in ds.dims:
            ds = ds.drop_vars(c)
    if "expver" in ds.dims:  # ERA5/ERA5T mix: combine
        ds = ds.reduce(np.nanmax, dim="expver")
    return ds


def postprocess(site: str, start: int, end: int) -> Path:
    """Merge raw files, interpolate to the site point, write a tidy CSV."""
    import xarray as xr

    cfg = SITES[site]
    paths = sorted(RAW_DIR.glob(f"era5_{site}_*.nc"))
    paths = [p for p in paths if start <= int(p.stem.split("_")[2][:4]) <= end]
    if not paths:
        sys.exit(f"No raw files for {site} in {RAW_DIR}")

    ds = xr.concat([_open(p) for p in paths], dim="time").sortby("time")
    ds = ds.sel(time=~ds.get_index("time").duplicated())
    # latitude is stored north->south; interp needs monotonic coords
    ds = ds.sortby("latitude").sortby("longitude")
    pt = ds.interp(latitude=cfg["lat"], longitude=cfg["lon"], method="linear")

    df = pd.DataFrame(
        {
            "time_utc": pd.to_datetime(pt["time"].values),
            "u100": pt["u100"].values,
            "v100": pt["v100"].values,
            "u10": pt["u10"].values,
            "v10": pt["v10"].values,
            "t2m_K": pt["t2m"].values,
            "sp_Pa": pt["sp"].values,
        }
    )
    df = df.dropna(subset=["u100", "v100"])

    expected = pd.date_range(f"{start}-01-01 00:00", f"{end}-12-31 23:00", freq="h")
    missing = len(expected.difference(df["time_utc"]))
    out = OUT_DIR / f"era5_{site}_{start}_{end}.csv"
    df.to_csv(out, index=False, float_format="%.4f")

    ws100 = np.hypot(df.u100, df.v100)
    print(
        f"[{site}] wrote {out}  rows={len(df):,}  missing hours={missing:,}  "
        f"mean ws100={ws100.mean():.2f} m/s"
    )
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", type=int, default=2006)
    ap.add_argument("--end", type=int, default=2025)
    ap.add_argument("--sites", nargs="+", default=list(SITES), choices=list(SITES))
    ap.add_argument("--chunk", choices=["year", "month"], default="year",
                    help="request size; use 'month' if CDS refuses yearly requests")
    ap.add_argument("--postprocess-only", action="store_true",
                    help="skip downloading; just rebuild the CSVs from data/era5_raw/")
    args = ap.parse_args()

    if args.end - args.start + 1 < 10:
        print("Warning: fewer than 10 years requested; inter-annual statistics will be weak.")

    for site in args.sites:
        if not args.postprocess_only:
            download(site, args.start, args.end, args.chunk)
        postprocess(site, args.start, args.end)


if __name__ == "__main__":
    main()
