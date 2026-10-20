"""
Download DK1/DK2 day-ahead prices from Energinet's Energi Data Service and
save them as hourly UTC series (Project 1, step 3).

Data sources (Energi Data Service, CC BY 4.0, Energinet):
  * Elspotprices    - hourly MTU, 1999-07-01 .. 2025-09-30 (discontinued)
                      columns HourUTC, PriceArea, SpotPriceDKK, SpotPriceEUR
  * DayAheadPrices  - 15-minute MTU, from 2025-10-01
                      columns TimeUTC, PriceArea, DayAheadPriceDKK, DayAheadPriceEUR
  * ProductionConsumptionSettlement (optional, --wind)
                    - hourly metered offshore wind per price area, from 2005
                      columns HourUTC, PriceArea, OffshoreWindLt100MW_MWh,
                      OffshoreWindGe100MW_MWh

How the 15-minute switch is handled
  The day-ahead MTU became 15 minutes for delivery day 1 Oct 2025
  (= 2025-09-30 22:00 UTC). Hours before that come from Elspotprices,
  hours from then on from DayAheadPrices. Each hour gets two prices:

    price_dkk          simple average of the MTU prices in the hour
    price_dkk_floored  average of the MTU prices after setting negative
                       MTU prices to 0

  price_dkk_floored is the input for the CfD reference price. Appendix 3
  sec. 2.6.3 floors negative prices "in a given market time unit", and
  sec. 2.1 defines the hourly price as the simple average of the MTU prices
  in that hour. With 15-minute MTUs the floor is therefore applied before
  averaging. For hourly MTUs (before Oct 2025) the two orders are identical.

Timestamps are hour-beginning, UTC, so DST days need no special handling.

Usage (Windows, from the step3 folder, venv active):
    python eds_price_download.py --start 2016 --end 2025
    python eds_price_download.py --start 2016 --end 2025 --wind
    python eds_price_download.py --start 2016 --end 2026 --refresh   # re-fetch cached years

Outputs (in --outdir, default ./data):
    prices_hourly_utc_<start>_<end>.csv          long format, one row per hour and area
    offshore_wind_hourly_utc_<start>_<end>.csv   only with --wind
    download_qa_<start>_<end>.csv                coverage check per area and year
    raw/                                         cached API responses (one JSON per dataset and year)

Requires: pandas, requests (Python 3.10+).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://api.energidataservice.dk/dataset/"
LOCAL_TZ = "Europe/Copenhagen"

# First 15-minute delivery period: 1 Oct 2025 00:00 CEST = 30 Sep 2025 22:00 UTC.
CUTOVER_UTC = pd.Timestamp("2025-09-30 22:00", tz="UTC")

# Fallback only: used if a DKK price is missing and the EUR price is not.
# DKK is pegged to EUR (central rate 7.46038); flagged per row in dkk_from_eur.
EURDKK_FALLBACK = 7.46

DATASETS = {
    "Elspotprices": {
        "time_col": "HourUTC",
        "dkk_col": "SpotPriceDKK",
        "eur_col": "SpotPriceEUR",
        "mtu_minutes": 60,
        "valid_to": CUTOVER_UTC,  # exclusive
        "valid_from": pd.Timestamp("1999-07-01", tz="UTC"),
    },
    "DayAheadPrices": {
        "time_col": "TimeUTC",
        "dkk_col": "DayAheadPriceDKK",
        "eur_col": "DayAheadPriceEUR",
        "mtu_minutes": 15,
        "valid_from": CUTOVER_UTC,
        "valid_to": pd.Timestamp("2100-01-01", tz="UTC"),
    },
}

WIND_DATASET = "ProductionConsumptionSettlement"
WIND_COLS = ["OffshoreWindLt100MW_MWh", "OffshoreWindGe100MW_MWh"]


# --------------------------------------------------------------------------
# API access
# --------------------------------------------------------------------------
def _local_str(ts_utc: pd.Timestamp) -> str:
    """API start/end are interpreted as Danish local time (API guide)."""
    return ts_utc.tz_convert(LOCAL_TZ).strftime("%Y-%m-%dT%H:%M")


def fetch_records(
    dataset: str,
    start_utc: pd.Timestamp,
    end_utc: pd.Timestamp,
    areas: list[str],
    columns: list[str] | None = None,
    max_retries: int = 6,
    timeout: int = 180,
) -> list[dict]:
    """Fetch all records of `dataset` for [start_utc, end_utc).

    The request window is padded by one day on each side (the API filters
    in Danish local time); the caller trims on the UTC column afterwards.
    """
    params = {
        "start": _local_str(start_utc - pd.Timedelta(days=1)),
        "end": _local_str(end_utc + pd.Timedelta(days=1)),
        "filter": json.dumps({"PriceArea": areas}),
        "limit": 0,  # 0 = all records
    }
    if columns:
        params["columns"] = ",".join(columns)

    url = BASE_URL + dataset
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url, params=params, timeout=timeout)
        except requests.RequestException as exc:
            wait = min(60, 2 ** attempt)
            print(f"    network error ({exc.__class__.__name__}); retry in {wait}s")
            time.sleep(wait)
            continue

        if r.status_code == 200:
            return r.json().get("records", [])

        if r.status_code == 429:
            # "Rate limit is exceeded. Try again in X seconds"
            m = re.search(r"(\d+)\s*second", r.text)
            wait = int(r.headers.get("Retry-After", m.group(1) if m else 30)) + 1
            print(f"    rate limited (429); waiting {wait}s")
            time.sleep(wait)
            continue

        if r.status_code >= 500:
            wait = min(60, 2 ** attempt)
            print(f"    server error {r.status_code}; retry in {wait}s")
            time.sleep(wait)
            continue

        raise RuntimeError(f"{dataset}: HTTP {r.status_code}: {r.text[:300]}")

    raise RuntimeError(f"{dataset}: giving up after {max_retries} attempts")


def fetch_year_cached(
    dataset: str,
    year: int,
    areas: list[str],
    raw_dir: Path,
    refresh: bool,
    pause: float,
    columns: list[str] | None = None,
    window: tuple[pd.Timestamp, pd.Timestamp] | None = None,
) -> list[dict]:
    """One calendar year (UTC) per request, cached as JSON in raw_dir."""
    y0 = pd.Timestamp(f"{year}-01-01", tz="UTC")
    y1 = pd.Timestamp(f"{year + 1}-01-01", tz="UTC")
    if window is not None:
        y0, y1 = max(y0, window[0]), min(y1, window[1])
    if y0 >= y1:
        return []

    cache = raw_dir / f"{dataset}_{year}_{'-'.join(areas)}.json"
    if cache.exists() and not refresh:
        print(f"  {dataset} {year}: cached")
        return json.loads(cache.read_text(encoding="utf-8"))

    print(f"  {dataset} {year}: downloading ...", flush=True)
    recs = fetch_records(dataset, y0, y1, areas, columns)
    cache.write_text(json.dumps(recs), encoding="utf-8")
    print(f"  {dataset} {year}: {len(recs):,} records")
    time.sleep(pause)
    return recs


# --------------------------------------------------------------------------
# Cleaning and aggregation (pure functions, tested offline)
# --------------------------------------------------------------------------
def records_to_mtu_frame(records: list[dict], dataset: str) -> pd.DataFrame:
    """API records -> tidy MTU-level frame in UTC.

    Columns: time_utc, area, price_dkk, price_eur, dkk_from_eur, mtu_minutes, source
    """
    spec = DATASETS[dataset]
    cols = ["time_utc", "area", "price_dkk", "price_eur", "dkk_from_eur", "mtu_minutes", "source"]
    if not records:
        return pd.DataFrame(columns=cols)

    df = pd.DataFrame.from_records(records)
    out = pd.DataFrame(
        {
            # API returns naive ISO strings; the *UTC column is UTC by definition.
            "time_utc": pd.to_datetime(df[spec["time_col"]]).dt.tz_localize("UTC"),
            "area": df["PriceArea"].astype(str),
            "price_dkk": pd.to_numeric(df[spec["dkk_col"]], errors="coerce"),
            "price_eur": pd.to_numeric(df[spec["eur_col"]], errors="coerce"),
        }
    )
    fill = out["price_dkk"].isna() & out["price_eur"].notna()
    out.loc[fill, "price_dkk"] = out.loc[fill, "price_eur"] * EURDKK_FALLBACK
    out["dkk_from_eur"] = fill
    out["mtu_minutes"] = spec["mtu_minutes"]
    out["source"] = dataset

    # Keep only the period for which this dataset is the designated source.
    keep = (out["time_utc"] >= spec["valid_from"]) & (out["time_utc"] < spec["valid_to"])
    out = out.loc[keep]

    dup = out.duplicated(["time_utc", "area"], keep="last")
    if dup.any():
        print(f"    note: dropped {int(dup.sum())} duplicate {dataset} rows")
        out = out.loc[~dup]
    return out[cols].sort_values(["area", "time_utc"]).reset_index(drop=True)


def mtu_to_hourly(mtu: pd.DataFrame, start_utc: pd.Timestamp, end_utc: pd.Timestamp) -> pd.DataFrame:
    """Aggregate MTU prices to hour-beginning UTC, per area, on a complete hourly index.

    price_dkk          mean of MTU prices
    price_dkk_floored  mean of max(MTU price, 0)   <- CfD reference-price input
    n_mtu              number of MTU prices found in the hour
    n_mtu_expected     60 / MTU length
    frac_neg_mtu       share of MTUs in the hour with a negative price
    Missing hours stay NaN (never filled silently).
    """
    m = mtu.copy()
    m["hour"] = m["time_utc"].dt.floor("h")
    m["price_dkk_floored"] = m["price_dkk"].clip(lower=0)
    m["price_eur_floored"] = m["price_eur"].clip(lower=0)
    m["neg"] = (m["price_dkk"] < 0).astype(float)

    g = m.groupby(["area", "hour"])
    hourly = pd.DataFrame(
        {
            "price_dkk": g["price_dkk"].mean(),
            "price_dkk_floored": g["price_dkk_floored"].mean(),
            "price_eur": g["price_eur"].mean(),
            "price_eur_floored": g["price_eur_floored"].mean(),
            "n_mtu": g["price_dkk"].count(),
            "mtu_minutes": g["mtu_minutes"].max(),
            "frac_neg_mtu": g["neg"].mean(),
            "dkk_from_eur": g["dkk_from_eur"].any(),
            "source": g["source"].first(),
        }
    ).reset_index()

    full_idx = pd.date_range(start_utc, end_utc, freq="h", inclusive="left")
    frames = []
    for area, sub in hourly.groupby("area"):
        sub = sub.set_index("hour").reindex(full_idx)
        sub.index.name = "time_utc"
        sub["area"] = area
        frames.append(sub.reset_index())
    out = pd.concat(frames, ignore_index=True)

    out["n_mtu"] = out["n_mtu"].fillna(0).astype(int)
    out["dkk_from_eur"] = out["dkk_from_eur"].astype("boolean").fillna(False).astype(bool)
    out["n_mtu_expected"] = (60 // out["mtu_minutes"]).astype("Int64")
    # Hours that are missing entirely: infer the expected MTU from the cutover.
    miss = out["mtu_minutes"].isna()
    out.loc[miss, "n_mtu_expected"] = (out.loc[miss, "time_utc"] >= CUTOVER_UTC).map({True: 4, False: 1})
    out["complete"] = out["n_mtu"] == out["n_mtu_expected"]

    cols = [
        "time_utc", "area", "price_dkk", "price_dkk_floored", "price_eur", "price_eur_floored",
        "n_mtu", "n_mtu_expected", "complete", "frac_neg_mtu", "dkk_from_eur", "source",
    ]
    return out[cols].sort_values(["area", "time_utc"]).reset_index(drop=True)


def wind_records_to_hourly(records: list[dict], start_utc: pd.Timestamp, end_utc: pd.Timestamp) -> pd.DataFrame:
    """Metered offshore wind (MWh) per area -> hour-beginning UTC sums.

    Accepts HourUTC (current) or a finer TimeUTC column (in case the dataset
    moves to 15-minute resolution); sub-hourly energy is summed per hour.
    """
    if not records:
        return pd.DataFrame(columns=["time_utc", "area", "offshore_mwh"])
    df = pd.DataFrame.from_records(records)
    tcol = next(c for c in ("HourUTC", "TimeUTC", "Minutes15UTC") if c in df.columns)
    # Overlapping yearly requests return New-Year days twice; energy must not be summed twice.
    df = df.drop_duplicates([tcol, "PriceArea"], keep="last")
    df["time_utc"] = pd.to_datetime(df[tcol]).dt.tz_localize("UTC").dt.floor("h")
    df["area"] = df["PriceArea"].astype(str)
    for c in WIND_COLS:
        df[c] = pd.to_numeric(df.get(c), errors="coerce")
    df = df[(df["time_utc"] >= start_utc) & (df["time_utc"] < end_utc)]
    g = df.groupby(["area", "time_utc"])[WIND_COLS].sum(min_count=1).reset_index()
    g = g.rename(columns={"OffshoreWindLt100MW_MWh": "offshore_lt100_mwh",
                          "OffshoreWindGe100MW_MWh": "offshore_ge100_mwh"})
    g["offshore_mwh"] = g[["offshore_lt100_mwh", "offshore_ge100_mwh"]].sum(axis=1, min_count=1)

    full_idx = pd.date_range(start_utc, end_utc, freq="h", inclusive="left")
    frames = []
    for area, sub in g.groupby("area"):
        sub = sub.set_index("time_utc").reindex(full_idx)
        sub.index.name = "time_utc"
        sub["area"] = area
        frames.append(sub.reset_index())
    out = pd.concat(frames, ignore_index=True)
    return out[["time_utc", "area", "offshore_mwh", "offshore_ge100_mwh", "offshore_lt100_mwh"]]


def qa_table(hourly: pd.DataFrame) -> pd.DataFrame:
    """Coverage per area and year: missing / incomplete hours, negatives, extremes."""
    h = hourly.copy()
    h["year"] = h["time_utc"].dt.year
    g = h.groupby(["area", "year"])
    return pd.DataFrame(
        {
            "hours": g.size(),
            "missing_hours": g["price_dkk"].apply(lambda s: int(s.isna().sum())),
            "incomplete_hours": g["complete"].apply(lambda s: int((~s).sum())),
            "neg_hours": g["price_dkk"].apply(lambda s: int((s < 0).sum())),
            "dkk_from_eur_hours": g["dkk_from_eur"].sum().astype(int),
            "min_dkk": g["price_dkk"].min().round(1),
            "mean_dkk": g["price_dkk"].mean().round(1),
            "max_dkk": g["price_dkk"].max().round(1),
        }
    ).reset_index()


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Download DK1/DK2 day-ahead prices as hourly UTC series.")
    ap.add_argument("--start", type=int, default=2016, help="first calendar year (UTC), default 2016")
    ap.add_argument("--end", type=int, default=2025, help="last calendar year (UTC), inclusive, default 2025")
    ap.add_argument("--areas", nargs="+", default=["DK1", "DK2"])
    ap.add_argument("--outdir", default="data")
    ap.add_argument("--wind", action="store_true", help="also download metered offshore wind per area (wind proxy)")
    ap.add_argument("--refresh", action="store_true", help="ignore cached raw files and re-download")
    ap.add_argument("--pause", type=float, default=1.0, help="seconds between API requests")
    args = ap.parse_args(argv)

    outdir = Path(args.outdir)
    raw_dir = outdir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    start_utc = pd.Timestamp(f"{args.start}-01-01", tz="UTC")
    end_utc = pd.Timestamp(f"{args.end + 1}-01-01", tz="UTC")
    now_utc = pd.Timestamp.now(tz="UTC").floor("h")
    if end_utc > now_utc:
        print(f"Note: end year runs past today; series will stop at the last published hour.")
    tag = f"{args.start}_{args.end}"

    print(f"Prices {args.start}-{args.end}, areas {args.areas}")
    mtu_frames = []
    for year in range(args.start, args.end + 1):
        for ds, spec in DATASETS.items():
            window = (max(start_utc, spec["valid_from"]), min(end_utc, spec["valid_to"]))
            recs = fetch_year_cached(ds, year, args.areas, raw_dir, args.refresh, args.pause, window=window)
            if recs:
                mtu_frames.append(records_to_mtu_frame(recs, ds))
    mtu = pd.concat(mtu_frames, ignore_index=True)
    # Yearly requests are padded by a day on each side, so New-Year days arrive twice.
    mtu = mtu.drop_duplicates(["time_utc", "area"], keep="last")

    last_hour = min(end_utc, mtu["time_utc"].max().floor("h") + pd.Timedelta(hours=1))
    hourly = mtu_to_hourly(mtu, start_utc, last_hour)
    f_prices = outdir / f"prices_hourly_utc_{tag}.csv"
    hourly.to_csv(f_prices, index=False)

    qa = qa_table(hourly)
    f_qa = outdir / f"download_qa_{tag}.csv"
    qa.to_csv(f_qa, index=False)

    print("\nCoverage check (per area and year):")
    print(qa.to_string(index=False))
    n_missing = int(qa["missing_hours"].sum())
    n_incomplete = int(qa["incomplete_hours"].sum()) - n_missing
    if n_missing or n_incomplete:
        print(f"\nWARNING: {n_missing} missing hours and {n_incomplete} hours with fewer MTUs than expected. "
              "They are left as NaN / partial means; inspect before use.")
    print(f"\nSaved {f_prices} ({len(hourly):,} rows)")

    if args.wind:
        print(f"\nOffshore wind (metered) {args.start}-{args.end}")
        recs = []
        for year in range(args.start, args.end + 1):
            recs += fetch_year_cached(
                WIND_DATASET, year, args.areas, raw_dir, args.refresh, args.pause,
                columns=["HourUTC", "PriceArea", *WIND_COLS],
                window=(start_utc, end_utc),
            )
        wind = wind_records_to_hourly(recs, start_utc, last_hour)
        f_wind = outdir / f"offshore_wind_hourly_utc_{tag}.csv"
        wind.to_csv(f_wind, index=False)
        miss = wind.groupby("area")["offshore_mwh"].apply(lambda s: int(s.isna().sum()))
        print(f"Missing wind hours per area: {miss.to_dict()}")
        print(f"Saved {f_wind} ({len(wind):,} rows)")

    print(f"Saved {f_qa}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
