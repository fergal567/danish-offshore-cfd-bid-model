# What Vattenfall's Danish CfD bids imply — Nordsøen Midt and Hesselø

**Project 1, step 5 · 21 Oct 2026 · Fergal Israel (MSc Wind Energy, DTU)**
Model: `step5/dcf_model.py` (26 tests), run in `step5/bid_calibration.ipynb`. All figures are in real 2026 DKK. NPVs are stated at the bid date (20 May 2026).
Tags: **Doc** = tender documents · **Ext** = named outside source · **Asm** = my assumption.

## Bottom line

1. **My base case needs strikes about 6–9 % above the awarded ones.** Nordsøen Midt (NSM) breaks even at **DKK 547/MWh** against the awarded 504 (A2, Ext). Hesselø breaks even at **DKK 575/MWh** against 542. At the awarded strikes, NPV is **−DKK 1.5bn** for NSM and **−0.8bn** for Hesselø. That is about −1.5 and −1.1 DKK m/MW, or 5–7 % of capex.
2. **The bids work with costs and returns that are plausible but at the aggressive end.** Any one of the following closes the gap:
   - a real post-tax CfD-period WACC of **4.3 % (NSM) or 4.5 % (Hesselø)**, against my 5.0 % base (Asm). The tail WACC is set 2 pp higher.
   - or, at a 5.0 % WACC, all-in capex of **DKK 20.2m/MW (NSM) or 20.7m/MW (Hesselø)**. That is about €2.7–2.8m/MW, 7–10 % below the DEA-based base case of DKK 22.3m/MW (Ext + Asm).
   - or a P10 rather than P50 yield.
3. **The bids look like a bet on 20 MW-class turbine costs.** With the DEA's 2025-column costs (15 MW units), the bids clear only at a **2.6–2.8 % WACC**, which is implausible for a private developer. With the 2030 column and the matching 20 MW yield, they clear at **4.6–4.8 %**. A 20 MW strategy can therefore carry about **2 pp more return** for technology risk and still beat the 15 MW route.
4. **The net cap on state payments makes NSM much riskier than Hesselø.** NSM's cap (DKK 16.1bn in 2026 prices, B9, Doc/Ext ⚠ site) averages only **DKK 167/MWh** of subsidy over 20 years. Hesselø's averages **313/MWh**.
   - In the low-hydrogen scenario (S4), NSM's cap runs out in **Sep 2047**, and DKK 5.2bn of contractual payments are never made. No strike then gives NPV = 0.
   - Hesselø never exhausts its cap in any scenario; the most it uses is 75 %.
   - This may help explain why NSM drew only two bids (interpretation).

## Base case and price scenarios

S1 is the DEA AF25 central price level (Ext). Its capture factor comes from method B: AF25 hourly prices paired with ERA5 site AAP for the same weather year. The table also gives the break-even strike in each scenario and when the net cap runs out at the awarded strike.

| Scenario (step 3 method §4) | NSM avg RP 2033–52 | NSM break-even | NSM cap at 504 | HES avg RP | HES break-even | HES cap at 542 |
|---|---|---|---|---|---|---|
| S1 AF25 central (Ext; CF method B) | 404 | **547** | 63 % used | 435 | **575** | 36 % used |
| S2 weather low / high (Ext) | 355 / 443 | 649 / 542 | 91 % / 39 % | 384 / 481 | 583 / 569 | 52 % / 21 % |
| S3 low gas, −15 % (Asm) | 343 | 779 | 98 % | 370 | 588 | 56 % |
| S4 low PtX, −20 %, CF −0.10 (Asm) | 285 | **none (cap-limited)** | **exhausted Sep 2047** | 308 | 600 | 75 % |
| S5 historical capture factors (Ext data, Asm use) | 423 | 541 | 51 % | 439 | 572 | 34 % |
| S1-B′ DEA fleet offshore-weighted ratio (Ext) | 358 | 683 | 89 % | 326 | 607 | 69 % |

- **Why NSM's break-even jumps in low-price cases.** Once a case pushes NSM's break-even above roughly the average reference price + 167, the cap binds. From that point a higher strike only uses the cap up sooner.
- **Why Hesselø is so stable.** Its break-even moves by only about 30 DKK/MWh across S1–S5. The two-way CfD hedges the price level, and the cap has room to spare.

**A data finding to verify with the DEA.** Pairing the AF25 hourly prices with ERA5 site yield gives offshore capture factors of **0.86–0.91** within each month. On an annual basis they are **0.91–0.99**, because AF25's winter-heavy price shape favours wind. The DEA's own published offshore-wind-weighted ÷ spot ratios are much lower: **0.57 / 0.95 / 0.76** for DK1 in 2030 / 2040 / 2050 (Ext).
- **It is not a timing error.** Only the matching ERA5 weather year correlates negatively with the AF25 prices.
- **Leap-day handling, checked from the data.** In 2008 the DEA dropped 31 Dec, not 29 Feb (Asm, evidence-based).
- **How the scenarios treat it.** I keep method B as the central case (S1) and run the DEA ratio as S1-B′.
- **What is missing.** ERA5 1995 was not in the step-2 export. Capture factors therefore use 2008/2009 only, with weights renormalised to 0.47/0.53 (Asm). Price levels still use all three climate years.

## Sensitivities (break-even strike, DKK/MWh; base NSM 547 / HES 575)

| Input (one at a time) | NSM low / high | HES low / high | Status |
|---|---|---|---|
| Capex, step-4 low / high | 471 / 1,168 (cap binds) | 493 / 670 | Ext + Asm |
| WACC 4.0/6.0 % vs 6.5/8.5 % | 489 / 883 (cap binds) | 514 / 671 | Ext/Asm |
| Opex, all lines low / high | 511 / 728 | 538 / 636 | Ext/Asm |
| Yield P10 / P90 (20-yr; σ_LT 6 %) | 506 / 615 | 532 / 625 | Asm |
| Tail value, life 35 / 25 years | 526 / 587 | 553 / 606 | Doc/Asm |
| Price scenario S1–S5 | 541 / none | 569 / 600 | Ext/Asm |
| Availability 96 % → 93.5 % (Vattenfall 2025 fleet) | 562 | 591 | Ext/Asm |
| Internal wake 12 % / 13 % (vs 10 %) | 559 / 566 | 588 / 595 | Asm |
| 2025 column + 15 MW vs 2030 column + 20 MW, both at 5 % | none / 528 | 689 / 555 | Ext + Asm |

- **Capex and WACC dominate.** Opex is third.
- **Yield and wakes are second-order.** The 13 % wake case moves break-even by about 20 DKK/MWh. It would bring the yield close to the DEA's interim NSM estimate (B11, Doc).

Modelling choices, one at a time (break-even change, NSM / Hesselø, DKK/MWh):

| Choice | Change | Status |
|---|---|---|
| Discount tail flows at the tail WACC from today instead of chaining after 2052 | +20 / +22 | Asm |
| Strike indexed with the Sep(y−1) NPI reset instead of a constant real strike | +9 / +9 | Doc/Asm |
| Standalone tax (SEL §12) instead of group relief | +6 / +5 | Ext |
| FID 2028 / FID 2030 phasing | +15 / −18 (NSM) | Asm |
| Payment lag (B7) | ≈ +1 | Doc |
| Export cable taxed at 15 % instead of 7 % | ≈ −1 | Ext |

The indexation lag matters: a bidder who prices in the January reset needs about 1.6 % more strike in real terms.

## Method in one paragraph

- **Price base and timeline.** Real 2026 DKK, deflated with the NPI at May 2026, the strike's own base (Doc). Development spend 2026–29, construction 2029–32 at 15/35/35/15 %, COD 1 Jan 2033, CfD 2033–52, merchant tail 2053–62, decommissioning 2063 (Asm, step 4).
- **CfD settlement.** Settled monthly: AAP × (strike − RP). A running net cap applies, which clawbacks replenish (B6–B9, Doc). Each payment is discounted at its own date, the 25th of the following month (B7, Doc).
- **Market sales.** Metered output × RP, with zero output in negative-price hours (C1, Doc). Variable O&M, tariffs and balancing are charged on the MWh actually sold (Ext/Asm).
- **Tax.** 22 %, with 15 % and 7 % declining-balance pools and §43 straight-line depreciation on nominal cost, deflated at 2 %/yr. Group relief in the base case (Ext + Asm).
- **IDC.** Not added as a cash flow: discounting capex from its spend date at the unlevered WACC already charges it. Compounded to COD at 5 %, it is DKK 2.6bn for NSM and 2.0bn for Hesselø (Asm).

## Caveats and next steps

1. **Contract terms.** NSS documents stand in for NSM and Hesselø (⚠ site). This covers the net cap amounts, guarantees and the CfD start. Get the sites' own Annex F and Appendix 3 from EU-Supply.
2. **1995 climate year.** Re-export the step-2 hourly AAP with 1995 (`era5_openmeteo.py --extra-years 1995`) and re-run. S1 capture factors may move by a few points.
3. **The DEA ratio gap.** Ask the DEA, or check the AF25 price background note, how the published technology-weighted prices are computed. Until then, treat S1-B′ as a serious downside for NSM.
4. **Hesselø capex.** No scale or nature-inclusive premium is included, and the Energinet classification is unconfirmed. The high Energinet case adds 10 DKK/MWh to break-even.
5. **WACC check.** Pull Vattenfall's and Ørsted's 2025 impairment-test discount rates as a primary check on 4.3–4.5 % real.
