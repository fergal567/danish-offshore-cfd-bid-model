# Step 3 — DK1/DK2 prices and the CfD reference price

Part of Project 1 (reverse-engineering the Danish offshore wind CfD bids: Nordsøen Midt DKK 504/MWh, Hesselø DKK 542/MWh).

| File | What it does |
|---|---|
| `eds_price_download.py` | Downloads DK1/DK2 day-ahead prices (Energinet Energi Data Service) for any year range and saves hourly UTC series. Stitches `Elspotprices` (hourly, to 30 Sep 2025) and `DayAheadPrices` (15-min, from 1 Oct 2025). Optional `--wind` adds metered offshore wind per area as a placeholder AAP profile. |
| `price_analysis.ipynb` | Baseload prices, negative-price frequency and the AAP-weighted monthly reference price, by month and year. `YIELD_SOURCE = "proxy"` now; `"era5"` once step 2 exports hourly AAP. |
| `price_scenarios_method.md` | Method and sources for 2033–2052 price scenarios (DEA AF25), with a net-cap screen. |
| `tests/` | Offline tests of the download logic (mocked API). |

## Run (Windows, Python 3.13 venv)

```bat
pip install pandas requests matplotlib jupyter pytest
python -m pytest -q tests
python eds_price_download.py --start 2016 --end 2025 --wind
jupyter notebook price_analysis.ipynb
```

For 2016–2025 with `--wind` the download makes 21 requests (one per dataset and year) with a 1-second pause, and caches raw responses in `data/raw/`, so re-runs are instant. Use `--refresh` to re-fetch.

## Key conventions
- Timestamps are hour-beginning UTC. Months for the reference price are Danish calendar months.
- `price_dkk` = mean of the hour's MTU prices; `price_dkk_floored` = mean after flooring each MTU at 0, per Appendix 3 §2.6.3 (the reference-price input).
- Missing hours are left as NaN and reported, never filled. DKK prices missing in the source are filled from EUR × 7.46 and flagged (`dkk_from_eur`).

Data: Energinet, Energi Data Service (CC BY 4.0).
