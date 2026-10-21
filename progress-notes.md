# Wind Portfolio Projects – progress notes

## Project 1 – Reverse-engineering the Danish CfD bids (NSM DKK 504/MWh, Hesselø DKK 542/MWh)

| Step | Status | Output | Notes |
|---|---|---|---|
| 1. Contract terms | Done (20 Oct 2026) | `contract_assumptions.md` | Based on Nordsøen Syd documents; NSM/Hesselø own Annex F and Appendix 1 still missing (rows marked ⚠ site) |
| 2. Yield model | Done (21 Oct 2026); committed to GitHub | `step2/era5_openmeteo.py` (used), `step2/era5_download.py` (CDS fallback), `step2/yield_model.ipynb`, `step2/data/IEA_Reference_15MW_240.csv`; exports `step2/data/aap_hourly_<SITE>.csv` (time_utc hour-beginning, aap_mwh, metered_mwh) | ERA5 2006–2025 + 1995 via Open-Meteo (CDS queue stalled). Calibration = quantile mapping onto Energinet Weibull. Results under 'Step 2 results'. Validation vs CDS passed (hourly r 0.998). Base losses kept (10 % internal wake); 12–13 % wake tested as a step-5 sensitivity instead of forcing the DEA match |
| 3. Prices & reference price | Done with wind proxy (21 Oct 2026); **next: rerun with YIELD_SOURCE="era5"** (ERA5 hand-over files now exist locally) | `step3/eds_price_download.py`, `step3/price_analysis.ipynb`, `step3/price_scenarios_method.md`, `step3/tests/` (9 tests) | Real 2016–2025 DK1/DK2 data: 0 missing hours. Fixed New-Year duplicate rows (wind proxy was double-counted). Results under 'Step 3 results'. Switch to YIELD_SOURCE="era5" once step 2 exports `aap_hourly_<SITE>.csv` (time_utc, aap_mwh). 2033–2052 scenarios: method B chosen (AF25 hourly × ERA5 same weather year), run in step 5 |
| 4. Capex / opex / tax / WACC | **Done (21 Oct 2026)** | `step4/cost_assumptions.md` (memo), `step4/cost_inputs.yaml` (step-5 input, generated), `step4/build_cost_inputs.py`, `step4/dea_extract.py`, `step4/dea_offshore_ac_2030.yaml` (DEA values), `step4/outputs/dea_*.csv` (DEA sheet extracts, CC BY 4.0), `step4/outputs/cost_table.md`, `step4/tests/` (9 tests) | DEA v0019 "21 Offshore Wind AC Fixed", 2030 column, site-adjusted by interpolating between DEA's own sheets. Price base real 2026 DKK (NPI May 2026). Results under 'Step 4 results' |
| 5. DCF & bid calibration | Not started | – | Solve for capex/WACC combinations giving NPV = 0 at 504 / 542. Real post-tax WACC on real (NPI-indexed) cash flows; higher rate for the merchant tail. Read `step4/cost_inputs.yaml` |

### Step 4 results (21 Oct 2026; real 2026 DKK)
- **DEA source:** workbook v0019 (Aug 2026), sheet "21 Offshore Wind AC Fixed" (chapter 21 updated 3 Feb 2025; 2020 EUR). 2030 column: investment **2.393 M€2020/MW** (dev 0.168, turbines 0.931, foundation 0.414, array 0.042, OSS 0.574, export 0.265); fixed O&M €34,000/MW/yr; variable €3.45/MWh; life 30 (25–40); FID→COD 3.5 yr (3–4). DEA site: 60 km, 30 m, 70 × **20 MW**. The 2025 column (15 MW units) is 2.780 / €44k / €4.41 → used as the **high** case.
- **Site adjustment (Asm):** the DEA formulas are in the chapter text (not read). Instead: export cable linear through the AC sheets at 35 km (0.1765) and 60 km (0.2648); foundation piecewise through 15/30/40 m. NSM 2.252 (−5.9 %), Hesselø 2.284 (−4.6 %) M€2020/MW.
- **Price base:** NPI (PRIS04) 2020 avg 85.522 → May 2026 102.13 = **×1.1942**; €1 (2020) = **DKK 8.909 (2026)**. Euro-area HICP ×1.2638 as a sensitivity only.
- **Capex excl. Energinet** (DEA + 7.5 % contingency + DKK 100m owner devex): NSM **€2.90m/MW** (2.41–3.49), Hesselø **€2.95m/MW** (2.44–3.54) – same as the report's base.
- **Energinet contribution:** NSM DKK 663m; Hesselø DKK 176m (0.175m/MW consumption-dominated rate, 2026 catalogue), high DKK 532m.
- **All-in capex:** NSM **DKK 22.4bn** (18.6–26.9); Hesselø **DKK 17.7bn** (14.6–21.5).
- **Opex:** fixed O&M DKK 303k/MW/yr + insurance 75k (Asm) = €50.6k/MW/yr (report €55k); variable 30.7 DKK/MWh (= €4.12, above the report's €2.5 – the report mixed a 2050 DC figure in 2020 €); Energinet tariffs 9.2; balancing 15 DKK/MWh; compliance DKK 3m/yr.
- **Decommissioning:** 12 % of DEA base = DKK 2.41m/MW (NSM), 2063; security fee 0.5 %/yr from 2047.
- **Tax:** 22 %; plant 15 % DB; export cable **7 % DB** (§5C stk. 2 – base); Energinet contribution 20 % SL from payment (§43); group relief in base; deflate nominal shields in the real model; CfD outside VAT (SKM2026.175.SR).
- **WACC:** report ranges kept (CfD 4.0/5.0/6.5 %, tail 6.0/7.0/8.5 %). New point: the DEA 2030 cost assumes 20 MW turbines, so a low bid may embed a technology bet – pair the 2025-column cost with base WACC as a step-5 sensitivity.

### Step 2 results (ERA5 2006–2025, IEA 15 MW, base losses; 21 Oct 2026)
| | NSM (1,005 MW) | HES (795 MW) |
|---|---|---|
| ERA5 raw mean @150 m / Energinet | 10.19 / 10.44 m/s (−2.4 %) | 9.20 / 9.63 m/s (−4.5 %) |
| ERA5 Weibull k / Energinet k | 2.34 / 2.25 | 2.29 / 2.22 |
| Gross CF (calibrated) | 64.6 % | 60.4 % |
| AAP′ proxy | 4,820 GWh/yr, CF 54.8 % | 3,589 GWh/yr, CF 51.5 % |
| Metered at POC | 4,651 GWh/yr, CF 52.8 % | 3,463 GWh/yr, CF 49.7 % |
| Inter-annual variability (AAP′, 1σ) | 3.5 % | 5.3 % |
| Lowest / highest year (AAP′ CF) | 2021 50.7 % / 2012 57.9 % | 2021 47.4 % / 2015 57.1 % |

- Data validation (21 Oct 2026): Open-Meteo vs Copernicus CDS, HES Jan 2025 (744 h): hourly correlation 0.998, mean ws100 ratio 0.989 (10.65 vs 10.77 m/s; nearest cell vs 4-cell blend). Open-Meteo route accepted.
- DEA check (NSM, per GW): metered 4,628 GWh/yr = +3.3 % vs DEA 4,479 (OK); AAP′ 4,796 = +7.1 % (high). DEA figure implies 20.9 % total loss from our gross; our stack is 18.2 % to metered. Reading: DEA's interim estimate is closer to a net/metered figure, or assumes ~2–3 points more wake loss.
- DEA's NSM monthly table (Guide Table 1.5) does not follow the wind climate (correlation 0.09 with our monthly profile; e.g. Nov 233 GWh is the lowest month). The NSS table (Appendix 3 Table 1) does (correlation 0.88). Treat the NSM table as illustrative.
- Mean-only scaling instead of quantile mapping gives ~2 % more energy (ERA5 distribution too narrow).
- 2025 is a below-average wind year in ERA5 (NSM AAP′ CF 53.5 %, HES 49.9 %) but not the lowest of the decade (2021 is) — revisit the step 3 note on 2025 capture factors with the ERA5 AAP.

### Cost & WACC research (research report, 21 Oct 2026 – verified/updated in step 4, see above)
Recommended inputs, 2026 prices, €1 = DKK 7.46:

| Input | Low | Base | High | Basis |
|---|---|---|---|---|
| Capex NSM (excl. Energinet POC; incl. export cable, OSS, development, contingency; excl. IDC) | €2.5m/MW | €2.9m/MW (DKK 21.6m) | €3.4m/MW | Thor escalated (low) to 2023–25 FID benchmarks (high); short export cable |
| Capex Hesselø | €2.6m/MW | €3.0m/MW (DKK 22.4m) | €3.6m/MW | Smaller scale, Kattegat, nature-inclusive design |
| Fixed O&M incl. insurance | €45k/MW/yr | €55k/MW/yr | €65k/MW/yr | Wind Denmark 2021 inflated; DEA long-run 33k as floor |
| Variable O&M | €0/MWh | €2.5/MWh | €4/MWh | DEA (via 2025 paper) |
| Seabed / concession fee | 0 | 0 | 0 | None in 2025/26 design |
| Decommissioning cost | 10 % of capex | 12 % (≈€0.35m/MW) | 15 % | Older DEA permits 10 %; Wind Denmark ≈15 % |
| Decommissioning security | posted by year 15 after first power | parent guarantee, 1 %/yr fee | bank guarantee | DEA model establishment permit, 12 Mar 2026 (third-party estimate, updated every 5 yrs) |
| Economic life | 25 yrs | 30 yrs (to 2062) | 35 yrs | 30-yr production permit, extendable 10 |
| FID / capex phasing | FID 2030 | FID mid-2029; 15/35/35/15 % over 2029–2032; development ≈6 % over 2026–2029 | FID 2028 | DEA ≈3.5 yr FID→COD; phasing is an assumption |
| WACC, real post-tax unlevered, CfD period | 4.0 % | 5.0 % | 6.5 % | RWE (>8.5 % IRR target, 150–350 bp over WACC; 7–11 % offshore range) and Ørsted (150–300 bp over WACC), nominal → real at ~2 %; CfD effect −50 to −100 bp (NERA 2013 via Europe Economics/BEIS 2020) |
| WACC, merchant tail | 6.0 % | 7.0 % | 8.5 % | Judgement (+150–250 bp) |
| Corporate tax | 22 % | 22 % | 22 % | Statutory |
| Tax depreciation | – | turbines/plant 15 % declining balance (separate pool); grid contribution 20 %/yr | export cable 7 % if classed as infrastructure | Afskrivningsloven §5C, §43 |
| Inflation 2020→2026 (for DEA 2020-EUR values) | ×1.20 | ×1.22 | ×1.25 | Approximate – **replaced in step 4 by NPI ×1.1942** |

Key points:
- DEA catalogue conventions: values are 2020 EUR, real, excl. VAT; columns are **FID year** (FID mid-2029 → use the **2030 column**, not 2035); scope includes export cable and offshore substation up to the nearest onshore substation; **excludes** contingency, interest during construction, decommissioning and onshore grid reinforcement (DEA suggests +0.15 M€2020/MW if needed). FID-2025 split: development 6 %, turbines 43 %, foundations 19 %, array 2 %, substation 21 %, export cable 9 %. DEA representative site is far offshore → scale export cable/substation down for NSM/Hesselø with DEA's distance formula.
- DEA Feb 2025 update: Danish capex up ≈30 % in real terms vs 2022 edition; component prices easing from peak but not back to 2020 levels.
- Benchmarks (nominal €m/MW): Thor ≈1.9–2.1 (2021–22 contracting, press-reported); Baltic Power 3.55 capex / 4.15 all-in; East Anglia 3 3.3–3.7; Hornsea 3 ≈3.4 (Ørsted "supply-chain investment" figure, not stated capex); Borkum Riffgrund 3 ≈2.6 (implied, excl. grid). Grid scopes differ by country (DE/NL exclude grid, UK/PL include it).
- DEA's own LCoE uses a 3.5 % real WACC (socio-economic, not a private hurdle).
- Expected strike-price sensitivity: capex ±10 % → ≈±7 %; WACC +100 bp → ≈+8–10 %; opex ±10 % → ≈±2–3 %; merchant-tail value is the hardest-to-verify lever behind an aggressive bid. Use a **real** WACC on real cash flows (CfD is NPI-indexed).
- Vattenfall reports 93.5 % offshore fleet availability in 2025 (92.0 % in 2024) – lower than our 96 % assumption (3 % unscheduled + 1 % scheduled); consider in the step-5 sensitivity.
- Not found / not sourced: DEA 2030 datasheet values, insurance cost (embedded in fixed O&M), capex phasing, any Vattenfall statement on NSM/Hesselø capex or FID date.

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
- ERA5 source: Open-Meteo archive API (nearest ERA5 cell) instead of the CDS queue.
- Calibration: quantile-map ERA5 hub-height wind onto Energinet's Weibull at 150 m (NSM A 11.76 / k 2.25; HES A 10.99 / k 2.22); keeps ERA5 timing, fixes level and shape.
- First-pass losses: internal wake 10 %, external 1.0 % (NSM, Thor) / 0.3 % (Hesselø, Anholt), other 2 %, unscheduled 3 %, scheduled 1 %, electrical 2.5 % (metered only).
- Pre-check with Energinet's Weibull fits: NSM gross CF ≈ 64.6 %; Hesselø ≈ 60.4 %.
- Step 4: model price base = real 2026 DKK deflated with NPI May 2026 (= strike base). DEA 2030 column as base capex/O&M, 2025 column as high case. Export cable taxed at 7 % in base. Tax losses used via group relief in base.

### Next session
1. Step 3 chat: rerun `price_analysis.ipynb` with `YIELD_SOURCE="era5"`; update the Step 3 results table (reference prices, capture factors, 2025 question).
2. New chat: step 5 – DCF and bid calibration reading `step4/cost_inputs.yaml` (real 2026 DKK; nominal tax shields deflated; IDC on the capex phasing; two-rate discounting CfD/tail). Key paired sensitivity: DEA 2025-column cost (15 MW) vs 2030 column (20 MW).

### Open items
- Step 2 hand-over done: `aap_hourly_<SITE>.csv`, hour-beginning UTC; ERA5 top-of-hour values converted to interval energy by trapezoid. Rerun step 3 with YIELD_SOURCE="era5".
- .gitignore now also excludes `step2/data/aap_hourly_*.csv` and `step2/outputs/*.csv.gz` (recreated by the notebook); `step2/outputs/yield_annual_summary.csv` and `yield_config.json` are committed. Step 4 adds `step4/data/` (DEA Excel) to .gitignore; `step4/outputs/` (small CSV/MD extracts) is committed.
- DEA AF25 price dataset inspected (21 Oct 2026): hourly DK1/DK2 per climate year 1995/2008/2009 for 2030/2040/2050 (CET, 2025 DKK) → scenario method B (pair with ERA5 same weather year). AF26 not yet published. ERA5 1995 for both sites: `era5_openmeteo.py --extra-years 1995`.
- Net-cap screen with DEA offshore-weighted prices (DK1 avg ≈348, DK2 ≈316 DKK/MWh, 2033–52): NSM uses ≈89–96 % of its DKK 15.7bn cap, Hesselø ≈74 % of 21.9bn. NSM cap likely binds in downside cases. Test properly in step 5.
- NSM representative coordinate is an assumption (56.00 N, 7.55 E) – replace with Appendix 2 centroid.
- Get NSM/Hesselø Annex F, Appendix 1, Appendix 2 from EU-Supply.
- Confirm Hesselø POC and Energinet area classification (connection contribution DKK 157–532m range). Cable route surveys point to a landfall near Gilleleje.
- DEA workbook v0019 saved in `step4/data/` (git-ignored). Still open: check the step-4 distance/depth interpolation against the chapter 21 text formulas (catalogue PDF https://ens.dk/media/8614/download) and whether DEA fixed O&M includes insurance.
- Hesselø has no scale or nature-inclusive capex premium in the DEA data – decide in step 5 whether to add one.
- Verify export-cable tax class (§5C stk. 2 vs stk. 1) and §43 applicability to the Energinet contribution.
- Pull Vattenfall/Ørsted 2025 impairment-test WACCs as a primary check on the WACC range.
- CDS requests still queued on the CDS website can be cancelled (Your requests → delete) once the Open-Meteo files are in.
