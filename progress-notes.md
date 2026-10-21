# Wind Portfolio Projects – progress notes

## Project 1 – Reverse-engineering the Danish CfD bids (NSM DKK 504/MWh, Hesselø DKK 542/MWh)

| Step | Status | Output | Notes |
|---|---|---|---|
| 1. Contract terms | Done (20 Oct 2026) | `contract_assumptions.md` | Based on Nordsøen Syd documents; NSM/Hesselø own Annex F and Appendix 1 still missing (rows marked ⚠ site) |
| 2. Yield model | ERA5 download running since 20 Oct 2026 (Windows laptop, Python 3.13 venv) | `step2/era5_download.py`, `step2/yield_model.ipynb`, `step2/data/IEA_Reference_15MW_240.csv` | Yearly requests exceed CDS cost limits → using `--chunk month`. Three windows: HES 2025 (test), NSM 2006–2025, HES 2006–2024. CDS queue very busy (~2,500 queued); expect 1–2+ days. When done: `python era5_download.py --start 2006 --end 2025 --postprocess-only`, then upload `data/era5_NSM_2006_2025.csv` and `data/era5_HES_2006_2025.csv` and run the notebook. Notebook so far tested on synthetic data only |
| 3. Prices & reference price | Done with wind proxy (21 Oct 2026); ERA5 rerun pending step 2 | `step3/eds_price_download.py`, `step3/price_analysis.ipynb`, `step3/price_scenarios_method.md`, `step3/tests/` (9 tests) | Real 2016–2025 DK1/DK2 data: 0 missing hours. Fixed New-Year duplicate rows (wind proxy was double-counted). Results under 'Step 3 results'. Switch to YIELD_SOURCE="era5" once step 2 exports `aap_hourly_<SITE>.csv` (time_utc, aap_mwh). 2033–2052 scenarios: method B chosen (AF25 hourly × ERA5 same weather year), run in step 5 |
| 4. Capex / opex | Not started | – | DEA Technology Catalogue + connection contribution (G3–G5) |
| 5. DCF & bid calibration | Not started | – | Solve for capex/WACC combinations giving NPV = 0 at 504 / 542 |

### Step 3 results (wind proxy, nominal DKK; 21 Oct 2026)
| Year | DK1 baseload | NSM RP | NSM RP/baseload | DK2 baseload | HES RP | HES RP/baseload | DK1 / DK2 neg. hours |
|---|---|---|---|---|---|---|---|
| 2016 | 199 | 185 | 0.93 | 219 | 201 | 0.92 | 62 / 49 |
| 2019 | 287 | 268 | 0.93 | 297 | 277 | 0.93 | 132 / 95 |
| 2020 | 186 | 149 | 0.80 | 212 | 165 | 0.78 | 192 / 89 |
| 2022 | 1,629 | 1,304 | 0.80 | 1,563 | 1,096 | 0.70 | 38 / 5 |
| 2023 | 647 | 544 | 0.84 | 605 | 465 | 0.77 | 281 / 231 |
| 2024 | 527 | 435 | 0.82 | 529 | 419 | 0.79 | 375 / 275 |
| 2025 | 605 | 545 | 0.90 | 616 | 537 | 0.87 | 441 / 265 |

- Observed RP/baseload 2016–2025: NSM proxy 0.80–0.93, HES proxy 0.70–0.93. DEA AF25 assumes offshore-weighted/spot of 0.57 (DK1) and 0.46 (DK2) in 2030 — far below anything observed — rising to 0.95/0.88 in 2040. The DEA path is a structural break from history; use S5 (historical replay) as a real alternative, not just a check.
- Negative-price floor matters little for RP: only 1–4.5 % of AAP falls in negative hours; RP is 1–4 DKK/MWh above the unfloored capture price.
- MTU-level vs hour-level floor (Oct–Dec 2025): difference ≈ 0.0004 DKK/MWh — immaterial so far.
- DK1 2023 low of −3,277 DKK/MWh (≈ −440 EUR) confirmed in the data at 2 July 2023, 14:00–15:00 Danish time (12:00 UTC) — the record north-west European negative-price Sunday.
- 2025 capture factors jump (NSM 0.90, HES 0.87) while proxy AAP is the lowest of the decade (low-wind year → less cannibalisation?). Check with ERA5.
- Proxy caveats: DK2 proxy is Baltic farms, not Kattegat; metered output patched in negative hours.

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
