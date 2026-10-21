# Wind Portfolio Projects – progress notes

## Project 1 – Reverse-engineering the Danish CfD bids (NSM DKK 504/MWh, Hesselø DKK 542/MWh)

| Step | Status | Output | Notes |
|---|---|---|---|
| 1. Contract terms | Done (20 Oct 2026) | `contract_assumptions.md` | Based on Nordsøen Syd documents; NSM/Hesselø own Annex F and Appendix 1 still missing (rows marked ⚠ site) |
| 2. Yield model | Done (21 Oct 2026); committed to GitHub | `step2/era5_openmeteo.py` (used), `step2/era5_download.py` (CDS fallback), `step2/yield_model.ipynb`, `step2/data/IEA_Reference_15MW_240.csv`; exports `step2/data/aap_hourly_<SITE>.csv` (time_utc hour-beginning, aap_mwh, metered_mwh) | ERA5 2006–2025 + 1995 via Open-Meteo (CDS queue stalled). Calibration = quantile mapping onto Energinet Weibull. Results under 'Step 2 results'. Validation vs CDS passed (hourly r 0.998). Base losses kept (10 % internal wake); 12–13 % wake tested as a step-5 sensitivity instead of forcing the DEA match |
| 3. Prices & reference price | **Done (21 Oct 2026)** – ERA5 site yield run | `step3/eds_price_download.py`, `step3/price_analysis.ipynb` (YIELD_SOURCE="era5" default; section 5b compares with proxy), `step3/price_scenarios_method.md`, `step3/tests/` (9 tests); outputs `step3/data/outputs/reference_price_*_era5.csv` | Real 2016–2025 DK1/DK2 data, 0 missing hours. Results under 'Step 3 results'. 2033–2052 scenarios: method B (AF25 hourly × ERA5 same weather year incl. 1995), run in step 5 |
| 4. Capex / opex / tax / WACC | **Done (21 Oct 2026)** | `step4/cost_assumptions.md` (memo), `step4/cost_inputs.yaml` (step-5 input, generated), `step4/build_cost_inputs.py`, `step4/dea_extract.py`, `step4/dea_offshore_ac_2030.yaml` (DEA values), `step4/outputs/dea_*.csv` (DEA sheet extracts, CC BY 4.0), `step4/outputs/cost_table.md`, `step4/tests/` (9 tests) | DEA v0019 "21 Offshore Wind AC Fixed", 2030 column, site-adjusted by interpolating between DEA's own sheets. Price base real 2026 DKK (NPI May 2026). Results under 'Step 4 results' |
| 5. DCF & bid calibration | **Done (21 Oct 2026)**; committed to GitHub (3514e30, notes 4ec7ba7) | `step5/dcf_model.py`, `step5/bid_calibration.ipynb`, `step5/bid_calibration_memo.md`, `step5/README.md`, `step5/reconstruct_aap_1995.py`, `step5/tests/` (27 tests), `step5/outputs/` (CSVs + 5 charts) | Real 2026 DKK; monthly CfD with net cap + payment lag; nominal tax shields deflated; chained two-rate discounting. AF25 xlsx in `step5/data/` (git-ignored). Results under 'Step 5 results'. ERA5 1995 AAP reconstructed from ERA5 wind (`reconstruct_aap_1995.py`, holdout R² 0.998/0.991) → method B uses 1995/2008/2009 at 0.25/0.35/0.40. 1995 re-run committed: pending |

### Step 5 results (21 Oct 2026; real 2026 DKK, NPV at bid date 20 May 2026)
- **Base case (S1, DEA 2030-column capex, P50, WACC 5.0 / 7.0 %):** break-even strike **NSM 547** (awarded 504, +8.5 %), **HES 575** (awarded 542, +6.1 %). NPV at awarded strike NSM −1.47bn, HES −0.84bn (≈ −1.5 / −1.1 DKK m/MW).
- **What closes the gap:** CfD WACC **4.25 % NSM / 4.5 % HES** at base capex (tail +2 pp); or capex **20.2 / 20.7 DKK m/MW** at 5 % (≈ €2.7–2.8m/MW all-in, −7 to −10 % vs base); or P10 yield. Full capex × yield × WACC grid in `outputs/wacc_solver_grid.csv`.
- **Paired sensitivity:** DEA 2025 column + 15 MW → bids clear only at **2.6 % (NSM) / 2.8 % (HES)** WACC; 2030 column + 20 MW yield (+3.4 %) → 4.6 / 4.8 %. A 20 MW bet can carry ≈ 2 pp extra return → bids look like a bet on next-generation turbine costs.
- **Net cap:** cap ÷ 20 yrs P50 AAP = **167 DKK/MWh (NSM)** vs **313 (HES)**. At awarded strike NSM uses 65 % (S1), 89 % (S1-B′), 93 % (S2 low), exhausts Oct 2052 in S3 and **Jul 2047 in S4** (DKK 5.5bn unpaid; no strike gives NPV = 0). HES never exhausts (max 76 % in S4). NSM break-even jumps when cases push it above ≈ RP + 167.
- **Price scenarios (20-yr avg RP NSM / HES):** S1 399 / 432; S2 351–438 / 381–478; S3 339 / 367; S4 281 / 306; S5 423 / 439; S1-B′ 358 / 326. HES break-even varies only 569–600 across S1–S5.
- **Method-B finding:** AF25 hourly × ERA5 gives capture factors 0.84–0.91 within month (0.89–0.99 annual, AF25 winter-heavy price shape) vs DEA published fleet ratio DK1 0.57/0.95/0.76. Timing verified (only the matching ERA5 year correlates negatively). **DEA dropped 31 Dec (not 29 Feb) in 2008** (correlation test). Kept method B as S1, DEA ratio as S1-B′.
- **Tornado (break-even, NSM / HES):** capex 471–1,375 (cap) / 493–670; WACC 490–937 (cap) / 514–671; opex 511–766 / 538–636; yield P10–P90 507–628 / 532–625; tail life 35–25 yrs 527–598 / 553–606; availability 93.5 % +15 / +16; wake 12–13 % +13–19 / +14–21.
- **Modelling choices:** tail discounted at tail WACC from today +28/+22; Sep(y−1) strike indexation lag +9/+9 (≈1.6 % of strike); standalone tax +6/+5; FID 2028 +15, FID 2030 −18 (NSM); payment lag ≈ +1; IDC implicit (NSM 2.6bn, HES 2.0bn compounded to COD at 5 %).

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

### Step 3 results (ERA5 site yield, nominal DKK; 21 Oct 2026)
| Year | DK1 baseload | NSM RP | NSM RP/baseload | DK2 baseload | HES RP | HES RP/baseload | DK1 / DK2 neg. hours |
|---|---|---|---|---|---|---|---|
| 2016 | 199 | 186 | 0.94 | 219 | 210 | 0.96 | 62 / 49 |
| 2019 | 287 | 273 | 0.95 | 297 | 284 | 0.95 | 132 / 95 |
| 2020 | 186 | 152 | 0.82 | 212 | 180 | 0.85 | 192 / 89 |
| 2021 | 655 | 593 | 0.91 | 654 | 569 | 0.87 | 87 / 24 |
| 2022 | 1,629 | 1,341 | 0.82 | 1,563 | 1,172 | 0.75 | 38 / 5 |
| 2023 | 647 | 555 | 0.86 | 605 | 493 | 0.81 | 281 / 231 |
| 2024 | 527 | 436 | 0.83 | 529 | 430 | 0.81 | 375 / 275 |
| 2025 | 605 | 531 | 0.88 | 616 | 535 | 0.87 | 441 / 265 |

- Mean RP/baseload 2016–2025: **NSM 0.885, HES 0.875**; recent years 2023–25: **NSM 0.854, HES 0.833**. Range NSM 0.82–0.95, HES 0.75–0.96.
- ERA5 vs proxy: site yield gives a slightly higher RP than the fleet proxy (mean +6 DKK/MWh NSM, +17 HES; largest in 2022: +36 / +76). Hesselø's Kattegat wind is less correlated with the (mostly Baltic) DK2 fleet than the proxy implied, so less cannibalisation. Proxy was a reasonable placeholder for NSM, conservative for HES.
- **2025 question answered:** ERA5 AAP CF in 2025 was near average (NSM 53.5 %, HES 49.9 %) and yearly wind level is uncorrelated with capture factor (r −0.02 NSM, +0.22 HES). 2025's higher capture factor is a market/price effect (e.g. 15-min MTU from Oct, more flexibility, gas-driven price shape), not a low-wind effect.
- Negative-price exposure rising: share of AAP in negative-price hours NSM 1.0 % (2016–18) → 4.6 / 5.2 / 5.5 % (2023/24/25); HES up to 3.9–4.2 %. RP floor adds only 1–4 DKK/MWh, but metered sales in those hours earn nothing (or are curtailed) – relevant to the merchant tail.
- DEA AF25 offshore-weighted/spot (0.57 DK1, 0.46 DK2 in 2030) is far below every observed year (lowest observed 0.82 / 0.75). Keep S5 (historical replay, ≈0.85 / 0.83) as a main alternative to the DEA path in step 5.
- MTU-level vs hour-level floor since Oct 2025: immaterial (<0.001 DKK/MWh).
- DK1 2023 low −3,277 DKK/MWh confirmed at 2 July 2023, 14:00–15:00 Danish time.

### Decisions so far
- Turbine: IEA 15 MW reference, hub 150 m. NSM 67 turbines (1,005 MW), Hesselø 53 (795 MW).
- Wind level anchored to Energinet's LiDAR studies (NSM 10.44 m/s, Hesselø 9.63 m/s at 150 m); ERA5 scaled to match.
- ERA5 source: Open-Meteo archive API (nearest ERA5 cell) instead of the CDS queue.
- Calibration: quantile-map ERA5 hub-height wind onto Energinet's Weibull at 150 m (NSM A 11.76 / k 2.25; HES A 10.99 / k 2.22); keeps ERA5 timing, fixes level and shape.
- First-pass losses: internal wake 10 %, external 1.0 % (NSM, Thor) / 0.3 % (Hesselø, Anholt), other 2 %, unscheduled 3 %, scheduled 1 %, electrical 2.5 % (metered only).
- Pre-check with Energinet's Weibull fits: NSM gross CF ≈ 64.6 %; Hesselø ≈ 60.4 %.
- Step 4: model price base = real 2026 DKK deflated with NPI May 2026 (= strike base). DEA 2030 column as base capex/O&M, 2025 column as high case. Export cable taxed at 7 % in base. Tax losses used via group relief in base.

### Next session
1. ~~Commit and push step 5~~ – done 21 Oct 2026 (step5/data/ added to .gitignore).
2. ~~ERA5 1995~~ – done 21 Oct 2026 via `step5/reconstruct_aap_1995.py`; commit the re-run.
3. Then: top-level README (question, method, findings, how to run) before making the repo public.

### Open items
- Step 5: ask DEA / check AF25 price background note how the published technology-weighted prices are computed (fleet ratio 0.57 vs 0.86–0.91 from hourly pairing).
- Step 5: pull Vattenfall/Ørsted 2025 impairment-test WACCs to test the implied 4.3–4.5 % real CfD WACC.
- Step 2 hand-over done and used in step 3 (ERA5 run 21 Oct 2026).
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
