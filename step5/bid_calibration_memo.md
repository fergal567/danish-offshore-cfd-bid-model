# What Vattenfall's Danish CfD bids imply — Nordsøen Midt and Hesselø

**Project 1, step 5 · 21 Oct 2026, updated after step 7 (primary-source verification) · Fergal Israel (MSc Wind Energy, DTU)**
Model: `step5/dcf_model.py` (27 tests), run in `step5/bid_calibration.ipynb`. All figures are in real 2026 DKK. NPVs are stated at the bid date (20 May 2026).
Tags: **Doc** = tender documents · **Ext** = named outside source · **Asm** = my assumption.

## Bottom line

1. **My base case needs strikes about 3–6 % above the awarded ones.** Nordsøen Midt (NSM) breaks even at **DKK 533/MWh** against the awarded 504 (A2, Ext). Hesselø breaks even at **DKK 559/MWh** against 542. At the awarded strikes, NPV is **−DKK 1.0bn** for NSM and **−0.45bn** for Hesselø, about 4 % and 2.5 % of capex.
2. **The bids work at returns that are plausible but thin.** Any one of the following closes the gap:
   - an implied real after-tax return of **4.5 % (NSM) or 4.7 % (Hesselø)** in the CfD period, against my 5.0 % base (Asm). The tail rate is set 2 pp higher. This is the rate that sets NPV = 0 at the awarded strike, so it is a return, not a WACC.
   - or, at 5.0 %, all-in capex of **DKK 20.9m/MW (NSM) or 21.4m/MW (Hesselø)**. That is about €2.8–2.9m/MW, 4–6 % below my estimate from Danish Energy Agency (DEA) data of DKK 22.3m/MW (Ext + Asm).
   - or a P10 rather than P50 yield.
3. **Against Vattenfall's own cost of capital, the margin is thin.** Vattenfall's 2025 annual report gives an after-tax discount rate of 5.7–7.4 % for its wind business (Note 27, Ext), about **3.6–5.3 % real** if nominal (Asm: the note's 2 % terminal growth implies nominal cash flows). A CfD-backed Danish offshore farm should sit near the low end. The bids therefore imply a return roughly **1 pp above** Vattenfall's discount rate, below the 150–350 bp spreads RWE and Ørsted say they target (Ext).
4. **The bids look like a bet on 20 MW-class turbines.** With the DEA's 2025-column costs (15 MW units), the implied return is only **2.8 % (NSM) / 3.1 % (Hesselø)**, below Vattenfall's own discount rate. With the 2030 column and the matching 20 MW yield, it is **4.8 % / 5.0 %**.
5. **The net cap on state payments makes NSM much riskier than Hesselø.** NSM's cap (DKK 16.1bn in 2026 prices, B9, Doc/Ext ⚠ site) averages only **DKK 167/MWh** of subsidy over 20 years. Hesselø's averages **313/MWh**.
   - In the low-hydrogen scenario (S4), NSM's cap runs out in **Jul 2047**, and DKK 5.5bn of contractual payments are never made. In the low-gas scenario (S3) it runs out in Oct 2052. In S4 no strike gives NPV = 0.
   - Hesselø never exhausts its cap in any scenario; the most it uses is 76 %.
   - This may help explain why NSM drew only two bids (interpretation).

## What changed in step 7

Two inputs were corrected against primary sources (`step7/verification_notes.md`):
- **Insurance.** The DEA Technology Data guideline says fixed O&M already includes insurance. The separate insurance line (DKK 75k/MW/yr) was double counting and is now 0 in the base case. Break-even **−19 (NSM) / −20 (Hesselø)** DKK/MWh.
- **Tax pools.** Skatterådet's binding answer SKM2025.37.SR puts "various types of cables and transformer stations" at up to 7 %. Array cables, export cable and offshore substation (about a third of the DEA base) now sit in the 7 % pool, not only the export cable. Break-even **+4.5 / +4.8**.

Net effect: break-even 14–15 DKK/MWh lower than in the first step-5 run (547 / 575).

## Base case and price scenarios

S1 is the DEA AF25 central price level (Ext). Its capture factor comes from method B: AF25 hourly prices paired with ERA5 site AAP for the same weather year. The table also gives the break-even strike in each scenario and when the net cap runs out at the awarded strike.

| Scenario (step 3 method §4) | NSM avg RP 2033–52 | NSM break-even | NSM cap at 504 | HES avg RP | HES break-even | HES cap at 542 |
|---|---|---|---|---|---|---|
| S1 AF25 central (Ext; CF method B) | 399 | **533** | 65 % used | 432 | **559** | 36 % used |
| S2 weather low / high (Ext) | 351 / 438 | 592 / 528 | 93 % / 42 % | 381 / 478 | 568 / 553 | 52 % / 22 % |
| S3 low gas, −15 % (Asm) | 339 | 683 | exhausted Oct 2052 | 367 | 572 | 57 % |
| S4 low PtX, −20 %, CF −0.10 (Asm) | 281 | **none (cap-limited)** | **exhausted Jul 2047** | 306 | 584 | 76 % |
| S5 historical capture factors (Ext data, Asm use) | 423 | 526 | 51 % | 439 | 557 | 34 % |
| S1-B′ DEA fleet offshore-weighted ratio (Ext) | 358 | 606 | 89 % | 326 | 591 | 69 % |

- **Why NSM's break-even jumps in low-price cases.** Once a case pushes NSM's break-even above roughly the average reference price + 167, the cap binds. From that point a higher strike only uses the cap up sooner.
- **Why Hesselø is so stable.** Its break-even moves by only about 30 DKK/MWh across S1–S5. The two-way CfD hedges the price level, and the cap has room to spare.

**A data finding the DEA does not explain.** Pairing the AF25 hourly prices with ERA5 site yield gives offshore capture factors of **0.84–0.91** within each month. On an annual basis they are **0.89–0.99**, because AF25's winter-heavy price shape favours wind. The DEA's own published offshore-wind-weighted ÷ spot ratios are much lower: **0.57 / 0.95 / 0.76** for DK1 in 2030 / 2040 / 2050 (Ext). The AF25 price note does not document how the weighted prices are built (step 7).
- **It is not a timing error.** Only the matching ERA5 weather year correlates negatively with the AF25 prices.
- **Leap-day handling, checked from the data.** In 2008 the DEA dropped 31 Dec, not 29 Feb (Asm, evidence-based).
- **How the scenarios treat it.** I keep method B as the central case (S1) and run the DEA ratio as S1-B′.
- **Climate year 1995.** The step-2 export stops at 2006–2025, so `reconstruct_aap_1995.py` rebuilds 1995 AAP from the ERA5 wind data. It learns step 2's own wind → AAP mapping (Asm). On held-out 2008–09 it reproduces hourly AAP with R² 0.998 (NSM) and 0.991 (Hesselø), and the capture factors to within 0.001. All three climate years then carry the 0.25/0.35/0.40 weights.

## Sensitivities (break-even strike, DKK/MWh; base NSM 533 / HES 559)

| Input (one at a time) | NSM low / high | HES low / high | Status |
|---|---|---|---|
| Capex, step-4 low / high | 456 / 977 (cap binds) | 477 / 656 | Ext + Asm |
| Discount rate 4.0/6.0 % vs 6.5/8.5 % | 474 / 811 (cap binds) | 498 / 657 | Ext/Asm |
| Opex, all lines low / high | 504 / 727 | 530 / 631 | Ext/Asm |
| Yield P10 / P90 (20-yr; σ_LT 6 %) | 493 / 581 | 517 / 609 | Asm |
| Tail value, life 35 / 25 years | 512 / 562 | 537 / 591 | Doc/Asm |
| Price scenario S1–S5 | 526 / none | 553 / 584 | Ext/Asm |
| Availability 96 % → 93.5 % (Vattenfall 2025 fleet) | 547 | 575 | Ext/Asm |
| 2025 column + 15 MW vs 2030 column + 20 MW, both at 5 % | 1,692 (cap binds) / 515 | 674 / 540 | Ext + Asm |

- **Capex and the discount rate dominate.** Opex is third.
- **Yield and wakes are second-order.** See `outputs/wake_case.csv` for the 12–13 % internal-wake cases, which bring the yield close to the DEA's interim NSM estimate (B11, Doc).

Modelling choices, one at a time (break-even change, NSM / Hesselø, DKK/MWh):

| Choice | Change | Status |
|---|---|---|
| Discount tail flows at the tail rate from today instead of chaining after 2052 | +22 / +24 | Asm |
| Strike indexed with the Sep(y−1) NPI reset instead of a constant real strike | +8 / +9 | Doc/Asm |
| Standalone tax (SEL §12) instead of group relief | +4 / +4 | Ext |
| Cables and substation at 15 % instead of 7 % | −5 / −6 | Ext |
| FID 2028 / FID 2030 phasing | +14 / −17 (NSM); +16 / −19 (HES) | Asm |
| Energinet contribution, high case | +1 / +10 | Asm |
| Decommissioning at 15 % of DEA base | +4 / +4 | Ext/Asm |
| Payment lag (B7) | ≈ +1 | Doc |

The indexation lag matters: a bidder who prices in the January reset needs about 1.6 % more strike in real terms. A later FID (2030) is enough on its own to make Hesselø's NPV positive at the awarded strike.

## Method in one paragraph

- **Price base and timeline.** Real 2026 DKK, deflated with the NPI at May 2026, the strike's own base (Doc). Development spend 2026–29, construction 2029–32 at 15/35/35/15 %, COD 1 Jan 2033, CfD 2033–52, merchant tail 2053–62, decommissioning 2063 (Asm, step 4).
- **CfD settlement.** Settled monthly: AAP × (strike − RP). A running net cap applies, which clawbacks replenish (B6–B9, Doc). Each payment is discounted at its own date, the 25th of the following month (B7, Doc).
- **Market sales.** Metered output × RP, with zero output in negative-price hours (C1, Doc). Variable O&M, tariffs and balancing are charged on the MWh actually sold (Ext/Asm). Fixed O&M follows the DEA, which includes insurance (Ext).
- **Tax.** 22 %, with a 15 % declining-balance pool for the plant and foundations, a 7 % pool for cables and substation (SKM2025.37.SR) and §43 straight-line depreciation for the Energinet contribution, all on nominal cost and deflated at 2 %/yr. Group relief in the base case (Ext + Asm).
- **IDC.** Not added as a cash flow: discounting capex from its spend date at the unlevered rate already charges it. Compounded to COD at 5 %, it is DKK 2.6bn for NSM and 2.0bn for Hesselø (Asm).

## Caveats and next steps

1. **Contract terms.** NSS documents stand in for NSM and Hesselø (⚠ site). This covers the net cap amounts, guarantees and the CfD start. Get the sites' own Annex F and Appendix 3 from EU-Supply.
2. **1995 climate year.** It is reconstructed rather than run through the step-2 notebook. If step 2 is ever re-run, export 1995 there and delete `step5/data/aap_hourly_1995_*.csv`.
3. **The DEA ratio gap.** The AF25 notes do not explain how the published technology-weighted prices are built. Until they do, treat S1-B′ as a serious downside for NSM.
4. **Hesselø capex.** No scale or nature-inclusive premium is included, and the Energinet classification is unconfirmed. The high Energinet case adds 10 DKK/MWh to break-even.
5. **Vattenfall's discount rate.** Note 27 gives a range for its whole wind business (on- and offshore) and does not say nominal or real; I read it as nominal. No offshore-only rate is disclosed.
6. **Overplanting.** The DEA's AF25 assumes overplanting at both sites (NSM +500 MW, Hesselø 1,100 MW). It earns merchant revenue only and is not in my base case, so it is a further possible lever behind the bids.
