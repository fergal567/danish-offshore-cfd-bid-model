# Wind Portfolio Projects – progress notes

## Project 1 – Reverse-engineering the Danish CfD bids (NSM DKK 504/MWh, Hesselø DKK 542/MWh)

| Step | Status | Output | Notes |
|---|---|---|---|
| 1. Contract terms | Done (20 Oct 2026) | `contract_assumptions.md` | Based on Nordsøen Syd documents; NSM/Hesselø own Annex F and Appendix 1 still missing (rows marked ⚠ site) |
| 2. Yield model | ERA5 download running since 20 Oct 2026 (Windows laptop, Python 3.13 venv) | `step2/era5_download.py`, `step2/yield_model.ipynb`, `step2/data/IEA_Reference_15MW_240.csv` | Yearly requests exceed CDS cost limits → using `--chunk month`. Three windows: HES 2025 (test), NSM 2006–2025, HES 2006–2024. CDS queue very busy (~2,500 queued); expect 1–2+ days. When done: `python era5_download.py --start 2006 --end 2025 --postprocess-only`, then upload `data/era5_NSM_2006_2025.csv` and `data/era5_HES_2006_2025.csv` and run the notebook. Notebook so far tested on synthetic data only |
| 3. Prices & reference price | Code done (21 Oct 2026); real download not yet run | `step3/eds_price_download.py`, `step3/price_analysis.ipynb`, `step3/price_scenarios_method.md`, `step3/tests/` | Run `python eds_price_download.py --start 2016 --end 2025 --wind`, then the notebook (YIELD_SOURCE="proxy"). Tested offline on synthetic data only (EDS API blocked from Claude's workspace). Elspotprices to 30 Sep 2025, DayAheadPrices (15-min) from 1 Oct 2025; RP uses MTU-level zero floor (App 3 §2.6.3). Switch to YIELD_SOURCE="era5" once step 2 exports `aap_hourly_<SITE>.csv` (time_utc, aap_mwh). 2033–2052 scenarios: method B chosen (AF25 hourly × ERA5 same weather year), not yet run |
| 4. Capex / opex | Not started | – | DEA Technology Catalogue + connection contribution (G3–G5) |
| 5. DCF & bid calibration | Not started | – | Solve for capex/WACC combinations giving NPV = 0 at 504 / 542 |

### Decisions so far
- Turbine: IEA 15 MW reference, hub 150 m. NSM 67 turbines (1,005 MW), Hesselø 53 (795 MW).
- Wind level anchored to Energinet's LiDAR studies (NSM 10.44 m/s, Hesselø 9.63 m/s at 150 m); ERA5 scaled to match.
- First-pass losses: internal wake 10 %, external 1.0 % (NSM, Thor) / 0.3 % (Hesselø, Anholt), other 2 %, unscheduled 3 %, scheduled 1 %, electrical 2.5 % (metered only).
- Pre-check with Energinet's Weibull fits: NSM gross CF ≈ 64.6 %; Hesselø ≈ 60.4 %.

### Open items
- Step 2 notebook must export hourly AAP per site: `step2/data/aap_hourly_NSM.csv`, `aap_hourly_HES.csv` (columns time_utc hour-beginning UTC, aap_mwh); fix the ERA5 top-of-hour convention.
- DEA AF25 price dataset inspected (21 Oct 2026): hourly DK1/DK2 per climate year 1995/2008/2009 for 2030/2040/2050 (CET, 2025 DKK) → scenario method B (pair with ERA5 same weather year). AF26 not yet published. Need ERA5 1995 for both sites.
- Net-cap screen with DEA offshore-weighted prices (DK1 avg ≈348, DK2 ≈316 DKK/MWh, 2033–52): NSM uses ≈89–96 % of its DKK 15.7bn cap, Hesselø ≈74 % of 21.9bn. NSM cap likely binds in downside cases. Test properly in step 5.
- NSM representative coordinate is an assumption (56.00 N, 7.55 E) – replace with Appendix 2 centroid.
- Get NSM/Hesselø Annex F, Appendix 1, Appendix 2 from EU-Supply.
- Confirm Hesselø POC and Energinet area classification (connection contribution).
