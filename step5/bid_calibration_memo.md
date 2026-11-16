# What Vattenfall's Danish CfD bids imply — Nordsøen Midt and Hesselø

**Project 1, step 5 · 21 Oct 2026, updated after step 7 (source verification); wording revised and numbers re-run 16 Nov 2026 after an external review · Fergal Israel (MSc Wind Energy, DTU)**
Model: `step5/dcf_model.py` (29 tests), run in `step5/bid_calibration.ipynb`. All figures are in real 2026 DKK. NPVs are stated at the bid date (20 May 2026).
Tags: **Doc** = tender documents · **Ext** = named outside source · **Asm** = my assumption.

## Bottom line

1. **Hesselø's price is close to my base-case break-even; Nordsøen Midt's is not.** Hesselø breaks even at **DKK 577/MWh** against the awarded 542 (A2, Ext), a 6.5 % gap. NPV at the awarded strike is **−DKK 0.86bn**, about 5 % of capex. Nordsøen Midt (NSM) needs **DKK 713/MWh** against 504, and NPV at 504 is **−DKK 3.6bn**, about 14 % of capex.
   - **Hesselø's gap is at the edge of the model's error band.** It equals a 7 % capex change, and single judgement calls are each about that size: the site cost adjustment (−4.6 %), NPI rather than HICP indexation of DEA costs (+5.8 %), and contingency (7.5 %). Read Hesselø as consistent with break-even at about 4.5 % real.
   - **NSM's gap is several times that band, and one input drives it.** The concession winner must build the export cable to a landfall at Nymindegab (45.7 km from my yield point) and the 53 km onshore cable to Endrup (Energinet, project description doc. 23/02056-2, Nov 2025, Ext). Costed at DEA unit rates this adds DKK 2.8bn (+12.7 % of capex) and moves NSM's implied return from 4.25 % to 3.4 %. The NSM break-even of 713 sits where the net cap binds (it runs out in Oct 2043 at that strike), so a higher strike buys little; the return and capex below are the cleaner measures.
2. **What closes the gap at each site** (any one of):
   - an implied real after-tax return of **4.5 % (Hesselø)** or **3.4 % (NSM)** in the CfD period, against my 5.0 % base (Asm). The tail rate is set 2 pp higher. This is the rate that sets NPV = 0 at the awarded strike, so it is a return, not a WACC, and because of the higher tail rate it is not a single-rate IRR.
   - or, at 5.0 %, all-in capex of **DKK 20.7m/MW (Hesselø)** or **20.2m/MW (NSM)**, about €2.8m and €2.7m/MW. That is 7 % and 20 % below my estimates from Danish Energy Agency (DEA) data (22.2 and 25.2m/MW, Ext + Asm).
   - or about **6 % (Hesselø)** or **20 % (NSM)** more output than my P50. My P10 (+7.8 %, σ_LT 6 %, Asm) covers Hesselø's but not NSM's, and no one bids on P10.
3. **Against Vattenfall's own discount rate.** Vattenfall's 2025 annual report gives an after-tax discount rate of 5.7–7.4 % for its wind business (Note 27, Ext), about **3.6–5.3 % real** if nominal (Asm: the note's 2 % terminal growth implies nominal cash flows). Hesselø's 4.5 % sits **at the midpoint** of that range, about 0.9 pp above its low end. NSM's 3.4 % is **below the range**. The range is an impairment-test rate covering on- and offshore, and real only by my inference. If a CfD-backed project belongs at the low end, Hesselø's margin is thin next to the 150–350 bp spreads RWE and Ørsted say they target (Ext), and NSM has none.
4. **Hesselø only works at the DEA's FID-2030 cost level, which assumes 20 MW-class turbines; NSM falls short even there.** The DEA columns differ by FID vintage, not only turbine size (turbines −22 %, foundations −22 %, fixed O&M −23 % from the 2025 to the 2030 column, `step4/dea_offshore_ac_2030.yaml`). With the 2025 column the implied return is only **1.9 % (NSM) / 2.8 % (Hesselø)**. With the 2030 column and the matching 20 MW yield it is **3.7 % / 4.8 %**. With FID in 2029 the 2030 column is the right vintage, so the bids rely on the DEA's expected cost fall arriving on time.
5. **The net cap on state payments makes NSM much riskier than Hesselø.** NSM's cap (DKK 16.1bn in 2026 prices, B9, Doc/Ext ⚠ site) averages only **DKK 173/MWh** of subsidy over 20 years. Hesselø's averages **324/MWh**.
   - In my low-hydrogen stress case (S4: prices −20 %, capture factor −0.10, both Asm), NSM's cap runs out around **2048** and roughly DKK 4bn of contractual payments are never made (tested on the P50 path only). In S4, as in the weather-low, low-gas and DEA-ratio cases, no strike gives NPV = 0.
   - Hesselø never exhausts its cap in any scenario; the most it uses is 71 %.
   - This may help explain why NSM drew only two bids (interpretation).

## What changed after review (16 Nov 2026)

An external review (Nov 2026) found base-case choices that moved the numbers. Applied:
- **Hesselø wind.** Weibull A 10.99 → **10.87** (k 2.22 kept), so the fitted mean equals the measured 9.63 m/s (was 9.73). No EMD table in the repo gives a consistent A/k pair, so A = 9.63 / Γ(1 + 1/k) (Ext mean and k, Asm A).
- **Wakes.** Internal wake **12 %** at both sites (was 10 %; DTU E-0255's 2030 range is 12–21 %, Ext/Asm). New: **Nordsøen Syd's wake on NSM, 1.5 % from 2035** to end of life (contract C4). Nordsøen Syd lies ≈40 km south of the NSM yield point; that ±25° sector carries 14.6 % of NSM's ERA5 energy, and ≈10 % in-sector loss gives 1.5 % (Asm). Total NSM wake ≈ 12 + 1 (Thor) + 1.5 ≈ 14.3 %, inside DTU's 2030 range. NSM's AAP is now 4,690 GWh per GW before the Nordsøen Syd wake, +4.7 % against the DEA's interim 4,479 (B11), down from +7.1 %. The AF25 cross-check for Hesselø is now 4,367 h against the DEA's 4,450.
- **Strike indexation.** The Sep(y−1) NPI reset (A4, Doc) is now the base; a constant real strike is the sensitivity.
- **Producer tariffs.** Removed from the base (O4 0 / 0 / 9.2) because the DEA guideline puts network charges in fixed O&M (step 7, V6). Charging them is a sensitivity.
- **NSM distance and onshore cable (G2).** Export cable distance 20 → **45.7 km**, from the yield point (56.00 N, 7.55 E) to Energinet's landfall just south of Nymindegab. Added the **53 km onshore cable** (≈49 km 275 kV, 2 systems, to the Hjortkær coupling station + ≈4 km 400 kV to Endrup), which KEFM has decided the concession winner "skal anlægge, eje og drive" (SGAV draft §25 permit, Jan 2026, Ext). Cost: DEA Technology Data for Energy Transport, sheet 1.7, AC onshore cable 4.51 k€₂₀₂₅/km/MW (2030), DKK 1.83bn, which ACER's 2023 unit cost (€4.40m/km for 220 kV, 2 circuits) supports. DEA chapter 21 puts the offshore point of connection at the coastline, so there is no double count. In the 7 % tax pool; out of decommissioning. Together with the longer export cable and contingency: +DKK 2.84bn.

Effect, one change added at a time (break-even strike, DKK/MWh; `step7/headline_check.py` gives each change reverted from the new base):

| Step | NSM | Hesselø |
|---|---|---|
| Base before review | 532.6 | 559.4 |
| + lagged strike reset | +8.4 | +8.8 |
| + no producer tariffs | −11.0 | −11.0 |
| + internal wake 12 % | +12.6 | +13.4 |
| + Hesselø Weibull (step-2 re-run) | −0.1 | +6.6 |
| + Nordsøen Syd wake on NSM | +7.5 | – |
| + NSM 45.7 km export and onshore cable | +163.3 (net cap binds) | – |
| **New base** | **713.3** | **577.2** |
| Implied CfD-period return | 4.51 % → **3.37 %** | 4.72 % → **4.46 %** |

The order matters at NSM: once its break-even passes about 570 (average reference price + cap headroom), the net cap binds and every later change moves the break-even more.

## What changed in step 7

Two inputs were corrected against primary sources (`step7/verification_notes.md`), on the 21 Oct base:
- **Insurance.** The DEA Technology Data guideline says fixed O&M already includes insurance. The separate insurance line (DKK 75k/MW/yr) was double counting and is now 0 in the base case. Break-even **−19 (NSM) / −20 (Hesselø)** DKK/MWh at the time.
- **Tax pools.** Skatterådet's binding answer SKM2025.37.SR puts "various types of cables and transformer stations" at up to 7 %. Array cables, export cable and offshore substation (about a third of the DEA base) now sit in the 7 % pool, not only the export cable. Break-even **+4.5 / +4.8**.

Net effect then: break-even 14–15 DKK/MWh lower than in the first step-5 run (547 / 575 → 533 / 559).

## Base case and price scenarios

S1 is the DEA AF25 central price level (Ext). Its capture factor comes from method B: AF25 hourly prices paired with ERA5 site AAP for the same weather year. The table also gives the break-even strike in each scenario and the cap use at the awarded strike. "None" means no strike gives NPV = 0 because the net cap limits the subsidy.

| Scenario (step 3 method §4) | NSM avg RP 2033–52 | NSM break-even | NSM cap at 504 | HES avg RP | HES break-even | HES cap at 542 |
|---|---|---|---|---|---|---|
| S1 AF25 central (Ext; CF method B) | 398 | **713** (cap binds Oct 2043) | 59 % used | 431 | **577** | 33 % used |
| S2 weather low / high (Ext) | 351 / 437 | none / 607 | 86 % / 37 % | 380 / 477 | 585 / 571 | 48 % / 19 % |
| S3 low gas, −15 % (Asm) | 339 | none | 93 % | 367 | 590 | 52 % |
| S4 low PtX, −20 %, CF −0.10 (Asm) | 281 | **none** | **exhausted Aug 2048** | 305 | 602 | 71 % |
| S5 historical capture factors (Ext data, Asm use) | 422 | 614 | 45 % | 438 | 575 | 31 % |
| S1-B′ DEA fleet offshore-weighted ratio (Ext) | 358 | none | 81 % | 326 | 610 | 65 % |

- **Why NSM's break-even disappears in low-price cases.** Once a case pushes NSM's break-even above roughly the average reference price + 173, the cap binds. From that point a higher strike only uses the cap up sooner. In the base case NSM is already past that point.
- **Why Hesselø is so stable.** Its break-even moves by only about 30 DKK/MWh across S1–S5. The two-way CfD hedges the price level, and the cap has room to spare.

**A data finding the DEA does not explain.** Pairing the AF25 hourly prices with ERA5 site yield gives offshore capture factors of **0.84–0.90** within each month. On an annual basis they are **0.89–0.99**, because AF25's winter-heavy price shape favours wind. The DEA's own published offshore-wind-weighted ÷ spot ratios are much lower: **0.57 / 0.95 / 0.76** for DK1 in 2030 / 2040 / 2050 (Ext). The AF25 price note does not document how the weighted prices are built (step 7).
- **The weather year is aligned.** Only the matching ERA5 weather year correlates negatively with the AF25 prices (−0.28). This confirms the year, not the hour-by-hour alignment.
- **Leap-day handling, checked from the data.** In 2008 the DEA dropped 31 Dec, not 29 Feb (Asm, evidence-based).
- **How the scenarios treat it.** I show method B (S1) and the DEA ratio (S1-B′) as co-equal cases. With the DEA ratio, Hesselø breaks even at **610**, above every other price scenario, and NSM has no break-even.
- **Climate year 1995.** The step-2 export stops at 2006–2025, so `reconstruct_aap_1995.py` rebuilds 1995 AAP from the ERA5 wind data. It learns step 2's own wind → AAP mapping (Asm). On held-out 2008–09 it reproduces hourly AAP with R² 0.998 (NSM) and 0.991 (Hesselø), and the capture factors to within 0.001. All three climate years then carry the 0.25/0.35/0.40 weights.

## Sensitivities (break-even strike, DKK/MWh; base NSM 713 / HES 577)

| Input (one at a time) | NSM low / high | HES low / high | Status |
|---|---|---|---|
| Capex, step-4 low / high | 522 / none | 490 / 678 | Ext + Asm |
| Discount rate 4.0/6.0 % vs 6.5/8.5 % | 545 / none | 512 / 680 | Ext/Asm |
| Opex, all lines low / high | 597 / none | 548 / 659 | Ext/Asm |
| Yield P10 / P90 (20-yr; σ_LT 6 %) | 570 / 1,160 (cap binds) | 533 / 629 | Asm |
| Tail value, life 35 / 25 years | 616 / 1,046 (cap binds) | 553 / 610 | Doc/Asm |
| Price scenario S1–S5 | 607 / none | 571 / 602 | Ext/Asm |
| Availability 96 % → 93.5 % (Vattenfall 2025 fleet) | 804 | 593 | Ext/Asm |
| 2025 column + 15 MW vs 2030 column + 20 MW, both at 5 % | none / 634 | 697 / 557 | Ext + Asm |

- **Capex and the discount rate dominate.** Opex is third. At NSM every adverse case lands in the cap-binding region, which is why the high cases show no break-even.
- **Wakes.** `outputs/wake_case.csv`: internal wake 10 / 12 / 13 % gives 657 / 713 / 749 (NSM) and 564 / 577 / 584 (Hesselø); Nordsøen Syd wake 0 / 1 / 3 % gives 679 / 701 / 754 at NSM.

Modelling choices, one at a time from the new base (break-even change, NSM / Hesselø, DKK/MWh; NSM changes are magnified because the cap binds at its break-even):

| Choice | Change | Status |
|---|---|---|
| Discount tail flows at the tail rate from today instead of chaining after 2052 | +216 / +25 | Asm |
| Constant real strike instead of the Sep(y−1) NPI reset | −11 / −9 | Doc/Asm |
| Energinet producer tariffs charged (9.2 DKK/MWh) | +80 / +11 | Ext/Asm |
| No Nordsøen Syd wake | −34 / – | Asm |
| Standalone tax (SEL §12) instead of group relief | +19 / +4 | Ext |
| Cables and substations at 15 % instead of 7 % | −43 / −6 | Ext |
| FID 2028 / FID 2030 phasing | +138 / −94 (NSM); +16 / −20 (HES) | Asm |
| Energinet contribution, high case | +9 / +10 | Asm |
| Decommissioning at 15 % of DEA base | +26 / +4 | Ext/Asm |
| Payment lag (B7) | +8 / +1 | Doc |

A later FID (2030) no longer closes Hesselø's gap on its own (557.5 against 542).

## Method in one paragraph

- **Price base and timeline.** Real 2026 DKK, deflated with the NPI at May 2026, the strike's own base (Doc). Development spend 2026–29, construction 2029–32 at 15/35/35/15 %, COD 1 Jan 2033, CfD 2033–52, merchant tail 2053–62, decommissioning 2063 (Asm, step 4).
- **CfD settlement.** Settled monthly: AAP × (strike − RP), with the strike reset each January to the September NPI (A4, Doc). A running net cap applies, which clawbacks replenish (B6–B9, Doc). Each payment is discounted at its own date, the 25th of the following month (B7, Doc).
- **Market sales.** Metered output × RP, with zero output in negative-price hours (C1, Doc). Variable O&M and balancing are charged on the MWh actually sold (Ext/Asm). Fixed O&M follows the DEA, which includes insurance and network charges (Ext, guideline).
- **Tax.** 22 %, with a 15 % declining-balance pool for the plant and foundations, a 7 % pool for cables (array, export, onshore) and the offshore substation (SKM2025.37.SR) and §43 straight-line depreciation for the Energinet contribution, all on nominal cost and deflated at 2 %/yr. Group relief in the base case (Ext + Asm).
- **IDC.** Not added as a cash flow: discounting capex from its spend date at the unlevered rate already charges it. Compounded to COD at 5 %, it is DKK 2.9bn for NSM and 2.0bn for Hesselø (Asm).

## Caveats and next steps

1. **Contract terms.** NSS documents stand in for NSM and Hesselø (⚠ site). This covers the net cap amounts, guarantees and the CfD start. Get the sites' own Annex F and Appendix 3 from EU-Supply.
2. **Net cap in real or nominal terms (open).** `settle_cfd` deflates past payments before summing them against the NPI-indexed cap. If the contract indexes the whole cap but counts past payments in nominal DKK (App 3 §2.5), headroom is larger and the S4 exhaustion date moves. The tender documents aren't in the repo, so this is unchecked.
3. **NSM grid connection.** The onshore cable is costed at DEA unit rates; the DEA notes that permits, rights, landowner compensation and planning "may add up to 50 %", and that cable O&M is 2.5 % of capex a year (≈ DKK 46m/yr), neither of which is in the model. The Hjortkær 275/400 kV coupling station is not costed (the DEA's onshore-substation rate would add ≈ DKK 1.9bn, partly overlapping the cable's compensation). The export distance runs from my yield point; the real substation position, inside an area 20–80 km from the coast, is unknown.
4. **Hesselø onshore leg.** Earlier Hesselø planning documents (landfall Gilbjerg Hoved, connection at Hovegård) had the concession winner building the land cables to the connection point. I have not checked the 2025 framework, so Hesselø carries no onshore cable. If it does bear one, its result worsens too, and the comparison between the sites is uneven until then.
5. **1995 climate year.** It is reconstructed rather than run through the step-2 notebook. If step 2 is ever re-run with a 1995 export, delete `step5/data/aap_hourly_1995_*.csv`.
6. **The DEA ratio gap.** The AF25 notes do not explain how the published technology-weighted prices are built. Until they do, S1-B′ is a co-equal case for both sites.
7. **Hesselø capex.** No scale or nature-inclusive premium is included, and the Energinet classification is unconfirmed. The high Energinet case adds 10 DKK/MWh to break-even.
8. **Vattenfall's discount rate.** Note 27 gives a range for its whole wind business (on- and offshore) and does not say nominal or real; I read it as nominal. No offshore-only rate is disclosed.
9. **Overplanting.** The DEA's AF25 assumes overplanting at both sites (NSM +500 MW, Hesselø 1,100 MW). It earns merchant revenue only and is not in my base case, so it is a further possible lever behind the bids.
10. **Nordsøen Syd timing.** The wake starts in 2035 (C4). Nordsøen Syd's bids are due in October 2028, so its start may be later, which would lower NSM's wake loss in the first years.
