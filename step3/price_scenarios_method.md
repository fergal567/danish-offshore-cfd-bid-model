# Project 1 · Step 3 — Method for 2033–2052 price scenarios (DK1 / DK2)

**Prepared:** 21 Oct 2026 · updated same day after inspecting the AF25 price dataset and sensitivity annex · Status: method chosen, not yet run.
**Feeds:** step 5 (DCF and bid calibration) for Nordsøen Midt (NSM, DK1) and Hesselø (HES, DK2), CfD 2033–2052 (contract_assumptions D4) plus merchant tail 2053–2062 (D5).

Status tags as in `contract_assumptions.md`: **Doc** (project tender files), **Ext** (named outside source), **Asm** (my assumption — change freely).

---

## 1. Why price scenarios matter less than they look — and where they still bite

If the farm stops in negative-price MTUs (C1) and metered output equals AAP, merchant revenue is Σ AAP_h · max(p,0)_h = RP · AAP, so total revenue = strike × AAP (see notebook, last section). The two-sided CfD hedges the price level almost completely. Prices still matter through five channels:

| Channel | Why it matters | Needs |
|---|---|---|
| **Net cap on state payments** (B9) | Once cumulative net subsidy hits the cap, the farm is merchant for the rest of the 20 years | Level and capture factor, by year |
| **Merchant tail 2053–2062** (D5) | No CfD after 20 years | Level and capture factor |
| Metered output ≠ AAP | Electrical losses (2.5 %) and unscheduled downtime (3 %) are sold at market but AAP-based settlement is unaffected | Capture price |
| Balancing / route-to-market (B14) | Cost per MWh; rises with price volatility | Not modelled from prices (flat Asm) |
| Overplanting (F2) | Overplanted MW are fully merchant | Capture price (scenario only) |

### Net-cap screen (back-of-envelope, Asm)
Cap ÷ (20 years × annual AAP) gives the average subsidy per MWh the cap can absorb. The cap binds if the 20-year average reference price falls below strike minus that amount. All values in real terms; the cap (2025 prices) and strike (2026 prices) are both NPI-indexed, so the ~1-year base mismatch is ignored.

| Site | Strike | Net cap | AAP assumed | Cap binds if 20-yr avg RP < |
|---|---|---|---|---|
| NSM | 504 | DKK 15.7bn | 4,479 GWh/yr (DEA interim estimate, B11) | **≈ 329 DKK/MWh** |
| NSM | 504 | DKK 15.7bn | 4,817 GWh/yr (progress-notes losses on 64.6 % gross CF) | ≈ 341 DKK/MWh |
| HES | 542 | DKK 21.9bn | 3,588 GWh/yr (same losses on 60.4 % gross CF) | **≈ 237 DKK/MWh** |

**Screen with the DEA's own offshore-wind-weighted prices** (AF25 dataset, §2; linear interpolation, 2025 prices): DK1 averages ≈ 348 DKK/MWh over 2033–2052 and DK2 ≈ 316. Running the cap year by year with these prices as the reference price:

| Site | 20-yr subsidy needed | Net cap | Share of cap used |
|---|---|---|---|
| NSM (4,479 GWh) | ≈ DKK 14.0bn | 15.7bn | **≈ 89 %** |
| NSM (4,817 GWh) | ≈ DKK 15.0bn | 15.7bn | **≈ 96 %** |
| HES (3,588 GWh) | ≈ DKK 16.3bn | 21.9bn | ≈ 74 % |

**Under the DEA's central case NSM uses roughly 90 % or more of its cap; a modest downside (e.g. 5–10 % lower offshore-weighted prices) would exhaust it before 2052. Hesselø keeps about a quarter of its cap in reserve.** This is the main reason step 5 needs explicit price scenarios, and it may be part of why NSM drew only two bids (interpretation, to be tested in step 5). Caveats: the DEA's weighting uses the whole Danish offshore fleet, not the site (method B below fixes this), and the 2025→2026 price-base conversion (~2 %) is ignored here.

## 2. Primary source: DEA Analysis Assumptions for Energinet 2025 (AF25)

| Item | Detail | Source |
|---|---|---|
| Publication | AF25, published 9 Nov 2025 (journal no. 2025-3657). AF26 is not yet listed on the DEA page; AF24 came out 9 Oct 2024 and AF25 9 Nov 2025, so AF26 may appear soon — **check before running step 5** | [DEA AF page](https://ens.dk/analyser-og-statistik/analyseforudsaetninger-til-energinet) (Ext) |
| Price note | *Baggrundsnotat om elprisfremskrivninger i AF25* | [ens.dk/media/7614](https://ens.dk/media/7614/download) (Ext) |
| Price dataset | *AF25 – datasæt – elprisfremskrivning* (Excel, inspected 21 Oct 2026). Sheets: **Elpriser** (annual DK1/DK2 spot, consumption-, offshore-, onshore- and solar-weighted prices for 2030/2040/2050); **Elpriser nabolande** (neighbouring zones); **Timepriser** (8,760 hourly prices per simulated year 2030/2040/2050 × climate year 1995/2008/2009 × DK1/DK2). Hours are in CET (no DST) laid out on calendar year 2018; prices in fixed 2025 DKK/MWh | [ens.dk/media/7632](https://ens.dk/media/7632/download) (Ext) |
| Fuel / CO₂ sensitivity | *AF25 – Bilag – Følsomhedsanalyse med alternative brændselspriser*. Prepared for Energinet to test **gas consumption** under lower gas prices (pure forwards short-term, pure IEA prices from 2030). States only that lower gas prices lower electricity prices in about the same relative proportion; **gives no electricity price figures** | [ens.dk/media/7615](https://ens.dk/media/7615/download) (Ext) |
| Model | DEA's Ramses hourly dispatch model; ENTSO-E ERAA24 for Europe to 2035, TYNDP24 "Distributed Energy" after 2035 (DEA-adjusted) | Price note (Ext) |
| Framing | Target-compliance scenario; DEA states the results are model simulations, not price forecasts | Price note, summary note (Ext) |
| System assumptions | DK offshore ≈ 4 GW end-2030, ≈ 27 GW end-2040, ≥ 35 GW 2050; grid-connected demand ≈ 63 TWh (2030) → ≈ 169 TWh (2050), of which ≈ 54 TWh electrolysis | [AF25 summary note](https://ens.dk/media/7600/download) (Ext) |
| CO₂ (ETS1) | ≈ 600 DKK/t (2025) → just over 700 (2030) → just under 2,000 (2050), 2025 prices | [AF25 fuel & quota note](https://ens.dk/media/7612/download) (Ext) |

**AF25 annual average spot prices, DKK/MWh, 2025 prices** (price note, Table 1):

| Year | DK1 low | DK1 central | DK1 high | DK2 low | DK2 central | DK2 high |
|---|---|---|---|---|---|---|
| 2030 | 420 | 460 | 510 | 450 | 500 | 560 |
| 2040 | 330 | 400 | 450 | 350 | 410 | 460 |
| 2050 | 420 | 450 | 480 | 410 | 460 | 500 |

⚠ The DEA's low/high columns are the spread across **weather (climate) years** 1995, 2008 and 2009, not market or policy uncertainty. They should not be used as the only downside case.

**AF25 technology-weighted prices, DKK/MWh, 2025 prices** (dataset, sheet *Elpriser*):

| | 2030 | 2040 | 2050 |
|---|---|---|---|
| Offshore wind-weighted, DK1 | 260 | 380 | 340 |
| Offshore wind-weighted, DK2 | 230 | 360 | 290 |
| Offshore ÷ spot, DK1 | 0.57 | 0.95 | 0.76 |
| Offshore ÷ spot, DK2 | 0.46 | 0.88 | 0.63 |

**What the hourly data show (my analysis of sheet *Timepriser*):**
- **No negative prices** in any year or climate year. The floor is 0, and zero-price hours occur only in 2030 (5–134 hours depending on climate year and zone). From 2040 the minimum is about 16 DKK/MWh, which reflects the large flexible demand (electrolysis, heat pumps) assumed in AF25. For the CfD reference price this matters less than it seems, because negative prices are floored at 0 anyway, but it means the DEA series cannot be used to project negative-price hours or merchant losses in them.
- **Climate-year weights.** The annual spot table is reproduced within rounding (max error 2.5 DKK/MWh) by weights of about **0.25 / 0.35 / 0.40** for 1995 / 2008 / 2009. Equal weights miss by up to 11. These weights are my inference; the DEA note only says it follows ENTSO-E's weighting method (Asm).
- Prices are stepwise (≈ 280–390 distinct values per series), typical of a dispatch model's merit order.

## 3. Proposed method

**A. Price level by year (Ext + Asm).** Annual DK1/DK2 average for 2033–2052 by linear interpolation of AF25 central between 2030, 2040 and 2050. Convert from 2025 to 2026 prices with Statistics Denmark's net price index ([DST NPI](https://www.dst.dk/en/Statistik/emner/oekonomi/prisindeks/nettoprisindeks), the index used for strike indexation, A4). Model in real 2026 DKK, consistent with a constant real strike.

**B. Capture factor from weather-consistent pairing (chosen — the dataset supports it).**
1. Pair each AF25 hourly series with site AAP from ERA5 for the **same weather year** (1995, 2008, 2009). 2008 and 2009 are already inside the step-2 ERA5 window (2006–2025); **1995 needs a one-year add-on ERA5 request for both sites.**
2. Time alignment: AF25 hour t0001 = 1 Jan 00:00 CET = 31 Dec 23:00 UTC of the previous year; CET has no DST. 2008 is a leap year (8,784 ERA5 hours) but AF25 has 8,760 — which day the DEA dropped is not stated. Base case: drop 29 Feb from ERA5 (Asm; test dropping 31 Dec instead).
3. For 2030, 2040 and 2050 compute, per site and month, the AAP-weighted price (floor at 0 is already met by the data) ÷ baseload → monthly capture factor CF(y, m).
4. Combine climate years with weights 0.25 / 0.35 / 0.40 (Asm, see §2); interpolate CF linearly between 2030, 2040 and 2050.
5. Check: weighting the AF25 hourly prices by ERA5 AAP should give capture factors broadly comparable to the DEA's fleet-weighted ratios above; large gaps point to a timing error or a real site effect.

**B′. Fallback (only if the pairing fails a sanity check).** Use the DEA's offshore-weighted ÷ spot ratio as the annual capture factor, with the monthly shape from the 2016–2025 history in `price_analysis.ipynb`.

**C. Monthly reference price.** RP(y, m) = level(y) × seasonal index(m) × CF(y, m). Feed into the DCF with the running net cap (B9) and the one-month payment lag (B7).

**D. Merchant tail 2053–2062 (Asm).** Hold the 2050 real level and capture factor flat. AF25 stops at 2050.

**E. Sanity checks.** (i) AF25-based 2030 capture factors vs observed 2016–2025 values from the notebook (ERA5 run); (ii) hours with negative prices in the AF25 hourly series vs history; (iii) AF25 offshore-weighted price for DK1 vs DK2 (sign of the DK1/DK2 spread).

## 4. Scenario set for step 5

| Scenario | Level | Capture factor | Basis | Status |
|---|---|---|---|---|
| **S1 Central** | AF25 central | Method B (or B′) | DEA AF25 | Ext |
| S2 Weather band | AF25 low / high | Same | DEA climate-year spread | Ext |
| S3 Low gas price | −15 % vs S1 (all years) | Same | Direction from the AF25 sensitivity annex (lower gas → proportionally lower electricity prices); the annex gives no electricity numbers, so the size is mine | Asm |
| S4 Low PtX / cannibalisation | −20 % vs S1 | −0.10 vs S1 | DEA's own uncertainty section says less electrolysis would lower prices and widen the gap between technology prices and the average spot price. The AF25 hourly data have no negative and almost no zero prices from 2040, so they rest heavily on that flexible demand; the size is my assumption | Asm |
| S5 Historical replay | S1 level | 2016–2025 observed capture factors and negative-hour frequency | `price_analysis.ipynb` (ERA5 run) | Doc/Ext data, Asm use |

Report for each scenario: year the net cap is exhausted (if any), NPV impact vs S1, and the bid (strike) needed for NPV = 0.

## 5. Secondary and cross-check sources (not used as inputs)
- **ENTSO-E ERAA 2024 / TYNDP 2024** — the DEA's own European inputs. Whether zonal hourly price outputs are published for download is not verified; the input scenarios are.
- **Open-TYNDP** (PyPSA implementation of TYNDP 2024, [docs](https://open-tyndp.readthedocs.io/en/latest/tyndp_2024/)) — a route to run an own market model later; out of scope for Project 1.
- **DEA KF26 (climate status and projection)** — the DEA has said it may move its socio-economic price assumptions to KF-based prices; KF horizons are shorter (typically to 2035 — verify), so it is a check on the early CfD years only.
- Commercial curves (Aurora, AFRY, etc.) are not public; press coverage is not used.

## 6. Open items
1. ~~Inspect the AF25 dataset~~ — done 21 Oct 2026: per-climate-year hourly prices available → method B.
2. AF26 not published as of 21 Oct 2026 (DEA page lists AF25 as latest). Re-check before running step 5; if out, swap all AF25 values.
3. Add ERA5 1995 for both sites to the step-2 download (needed for method B).
4. Pull the NPI series (2025 → 2026 conversion and history).
5. Confirm NSM = DK1 and HES = DK2 (B5) and Hesselø's POC (G5).
