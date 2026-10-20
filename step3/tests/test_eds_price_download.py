"""Offline tests for eds_price_download.py (no network needed).

Run from the step3 folder:  python -m pytest -q tests
API responses are mocked with records in the schema published in the
Energi Data Service metadata for Elspotprices, DayAheadPrices and
ProductionConsumptionSettlement.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import eds_price_download as eds  # noqa: E402

UTC = "UTC"


def _iso(ts):
    return ts.strftime("%Y-%m-%dT%H:%M:%S")


def fake_records(dataset, start_utc, end_utc, areas, columns=None, **_):
    """Mimic the API: naive ISO timestamps, padded window, DKK and EUR prices."""
    out = []
    if dataset == "Elspotprices":
        idx = pd.date_range(start_utc, end_utc, freq="h", inclusive="left")
        idx = idx[idx < eds.CUTOVER_UTC]  # dataset ends at the cutover
        for a_i, area in enumerate(areas):
            for t in idx:
                eur = 50 + 30 * np.sin(t.hour / 24 * 2 * np.pi) + a_i
                out.append({"HourUTC": _iso(t), "HourDK": _iso(t.tz_convert(eds.LOCAL_TZ)),
                            "PriceArea": area, "SpotPriceDKK": eur * 7.46, "SpotPriceEUR": eur})
    elif dataset == "DayAheadPrices":
        idx = pd.date_range(start_utc, end_utc, freq="15min", inclusive="left")
        idx = idx[idx >= eds.CUTOVER_UTC]
        for a_i, area in enumerate(areas):
            for t in idx:
                eur = 40 + 30 * np.sin(t.hour / 24 * 2 * np.pi) + a_i
                out.append({"TimeUTC": _iso(t), "TimeDK": _iso(t.tz_convert(eds.LOCAL_TZ)),
                            "PriceArea": area, "DayAheadPriceEUR": eur, "DayAheadPriceDKK": eur * 7.46})
    elif dataset == eds.WIND_DATASET:
        idx = pd.date_range(start_utc, end_utc, freq="h", inclusive="left")
        for area in areas:
            for t in idx:
                out.append({"HourUTC": _iso(t), "PriceArea": area,
                            "OffshoreWindLt100MW_MWh": 10.0, "OffshoreWindGe100MW_MWh": 500.0})
    return out


# ---------------------------------------------------------------- unit tests
def test_mtu_floor_applied_before_hourly_average():
    t0 = pd.Timestamp("2025-11-03 10:00", tz=UTC)
    recs = [{"TimeUTC": _iso(t0 + pd.Timedelta(minutes=15 * i)), "PriceArea": "DK1",
             "DayAheadPriceDKK": p, "DayAheadPriceEUR": p / 7.46}
            for i, p in enumerate([-10.0, 20.0, 30.0, -40.0])]
    mtu = eds.records_to_mtu_frame(recs, "DayAheadPrices")
    h = eds.mtu_to_hourly(mtu, t0, t0 + pd.Timedelta(hours=1)).iloc[0]
    assert h["price_dkk"] == pytest.approx(0.0)            # (-10+20+30-40)/4
    assert h["price_dkk_floored"] == pytest.approx(12.5)   # (0+20+30+0)/4
    assert h["frac_neg_mtu"] == pytest.approx(0.5)
    assert h["n_mtu"] == 4 and bool(h["complete"])


def test_hourly_mtu_floor_equals_hour_floor():
    t0 = pd.Timestamp("2020-05-01", tz=UTC)
    recs = [{"HourUTC": _iso(t0), "PriceArea": "DK2", "SpotPriceDKK": -55.0, "SpotPriceEUR": -7.4}]
    h = eds.mtu_to_hourly(eds.records_to_mtu_frame(recs, "Elspotprices"), t0, t0 + pd.Timedelta(hours=1)).iloc[0]
    assert h["price_dkk"] == -55.0 and h["price_dkk_floored"] == 0.0 and h["frac_neg_mtu"] == 1.0


def test_cutover_stitching_no_gap_no_overlap():
    s = pd.Timestamp("2025-09-30 18:00", tz=UTC)
    e = pd.Timestamp("2025-10-01 02:00", tz=UTC)
    # Both datasets padded beyond the cutover; DayAheadPrices also returns
    # (synthetic) rows before the cutover, which must be dropped.
    el = eds.records_to_mtu_frame(fake_records("Elspotprices", s, e, ["DK1"]), "Elspotprices")
    da_recs = fake_records("DayAheadPrices", s, e, ["DK1"])
    da_recs.append({"TimeUTC": "2025-09-30T21:00:00", "PriceArea": "DK1",
                    "DayAheadPriceDKK": 9999.0, "DayAheadPriceEUR": 1340.0})
    da = eds.records_to_mtu_frame(da_recs, "DayAheadPrices")
    h = eds.mtu_to_hourly(pd.concat([el, da]), s, e)
    assert len(h) == 8 and h["price_dkk"].notna().all() and h["complete"].all()
    src = h.set_index("time_utc")["source"]
    assert src[pd.Timestamp("2025-09-30 21:00", tz=UTC)] == "Elspotprices"
    assert src[pd.Timestamp("2025-09-30 22:00", tz=UTC)] == "DayAheadPrices"
    assert h["price_dkk"].max() < 9999


def test_dst_days_are_continuous_in_utc():
    # 2024-03-31 (23 local hours) and 2024-10-27 (25 local hours)
    for day in ("2024-03-30 22:00", "2024-10-26 22:00"):
        s = pd.Timestamp(day, tz=UTC)
        e = s + pd.Timedelta(hours=48)
        h = eds.mtu_to_hourly(eds.records_to_mtu_frame(fake_records("Elspotprices", s, e, ["DK1"]), "Elspotprices"), s, e)
        assert len(h) == 48 and h["price_dkk"].notna().all()
        assert h["time_utc"].diff().dropna().eq(pd.Timedelta(hours=1)).all()


def test_missing_hour_and_missing_quarter_are_flagged_not_filled():
    s = pd.Timestamp("2025-11-01", tz=UTC)
    e = s + pd.Timedelta(hours=4)
    recs = fake_records("DayAheadPrices", s, e, ["DK2"])
    recs = [r for r in recs if not r["TimeUTC"].startswith("2025-11-01T02")]  # drop hour 02
    recs = [r for r in recs if r["TimeUTC"] != "2025-11-01T01:30:00"]         # drop one quarter
    h = eds.mtu_to_hourly(eds.records_to_mtu_frame(recs, "DayAheadPrices"), s, e).set_index("time_utc")
    assert np.isnan(h.loc[s + pd.Timedelta(hours=2), "price_dkk"])
    assert h.loc[s + pd.Timedelta(hours=2), "n_mtu_expected"] == 4
    assert h.loc[s + pd.Timedelta(hours=1), "n_mtu"] == 3
    assert not h.loc[s + pd.Timedelta(hours=1), "complete"]
    qa = eds.qa_table(h.reset_index())
    assert int(qa["missing_hours"].iloc[0]) == 1 and int(qa["incomplete_hours"].iloc[0]) == 2


def test_dkk_filled_from_eur_and_flagged():
    t0 = pd.Timestamp("2016-01-01", tz=UTC)
    recs = [{"HourUTC": _iso(t0), "PriceArea": "DK1", "SpotPriceDKK": None, "SpotPriceEUR": 20.0}]
    h = eds.mtu_to_hourly(eds.records_to_mtu_frame(recs, "Elspotprices"), t0, t0 + pd.Timedelta(hours=1)).iloc[0]
    assert h["price_dkk"] == pytest.approx(20.0 * eds.EURDKK_FALLBACK) and bool(h["dkk_from_eur"])


def test_wind_hourly_sum():
    s = pd.Timestamp("2021-06-01", tz=UTC)
    w = eds.wind_records_to_hourly(fake_records(eds.WIND_DATASET, s, s + pd.Timedelta(hours=3), ["DK1"]),
                                   s, s + pd.Timedelta(hours=3))
    assert len(w) == 3 and (w["offshore_mwh"] == 510.0).all()


# ---------------------------------------------------------------- end to end
def test_main_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setattr(eds, "fetch_records", fake_records)
    monkeypatch.setattr(eds.time, "sleep", lambda *_: None)
    rc = eds.main(["--start", "2025", "--end", "2025", "--outdir", str(tmp_path), "--wind", "--pause", "0"])
    assert rc == 0
    p = pd.read_csv(tmp_path / "prices_hourly_utc_2025_2025.csv", parse_dates=["time_utc"])
    assert len(p) == 2 * 8760 and p["price_dkk"].notna().all()
    assert set(p["source"]) == {"Elspotprices", "DayAheadPrices"}
    q = pd.read_csv(tmp_path / "download_qa_2025_2025.csv")
    assert q["missing_hours"].sum() == 0 and q["incomplete_hours"].sum() == 0
    w = pd.read_csv(tmp_path / "offshore_wind_hourly_utc_2025_2025.csv")
    assert len(w) == 2 * 8760
    # second run uses the cache (fetch would now fail)
    monkeypatch.setattr(eds, "fetch_records", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("no net")))
    assert eds.main(["--start", "2025", "--end", "2025", "--outdir", str(tmp_path), "--pause", "0"]) == 0
