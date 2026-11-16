# Project 1 – Step 7: source verification

**Prepared:** 21 Oct 2026 · **Status:** findings recorded; V1 and V6 applied and step 5 re-run on 21 Oct 2026; V6 applied to producer tariffs and steps 2–5 re-run on 16 Nov 2026 after an external review (results in `step5/bid_calibration_memo.md`, "What changed after review").
**Sources:** V1–V4 were checked directly against SKM2025.37.SR on retsinformation.dk. Rows marked "(via report)" rely on a secondary research report and still need checking against the primary document; they are the open items in §4.
**Input:** focused research report "Primary-source verification of WACC, AF25 prices, Danish tax classes and DEA offshore data" (21 Oct 2026), checked against `step4/cost_assumptions.md` and `step5/bid_calibration_memo.md`. SKM2025.37.SR wording re-checked directly on retsinformation.dk.

Tags as elsewhere: **Doc** (tender documents) · **Ext** (named outside source) · **Asm** (my assumption).

## 1. Findings and what they change

| # | Question | Finding | Source | Status | Model action |
|---|---|---|---|---|---|
| V1 | Tax class of cables and substations (T3) | Skatterådet: "forskellige typer kabler og transformatorstationer mv." can be depreciated at up to **7 %** as infrastructure. The answer does not separate array cables, export cable and offshore substation | SKM2025.37.SR (19 Nov 2024), Q5, retsinformation.dk/api/pdf/247807 | Ext, **verified** | Move array cables, export cable **and offshore substation** to the 7 % pool (base). Model had only the export cable there (≈ 5.5 % of K1); the ruling puts ≈ 33 % of K1 at 7 % |
| V2 | Main plant and foundations | 15 %; foundations incl. transport and installation are part of the main plant | SKM2025.37.SR, Q3–Q4 | Ext, verified | No change |
| V3 | Energinet connection payment (T4) | §43, 20 % a year from each instalment's due date; public or private owner makes no difference | SKM2025.37.SR, Q11; JV C.C.2.4.5.5 | Ext, verified | No change. T4 closed |
| V4 | External admin costs in construction | Neither deductible nor capitalisable (Q14, Q14.1: "Nej") | SKM2025.37.SR | Ext, verified | Small. Treat the owner-team share of K3 as non-deductible (Asm: 50 % of K3) |
| V5 | Decommissioning; payments to the state under the CfD | Decommissioning deductible when incurred; CfD payments to the state are operating costs | SKM2025.37.SR, Q15, Q17 (via report) | Ext | Check the model does both |
| V6 | Does DEA fixed O&M include insurance? (O2) | Yes, per the catalogue guideline: fixed O&M includes administration, staff, service agreements, **network or system charges**, property tax and **insurance** | DEA Technology Data, Guideline, "O&M costs", pp. 27–28 (via report) | Ext; general guideline, chapter 21 not checked | Set O2 insurance **base to 0** (low 0, high = old base DKK 75k/MW/yr as a "not included after all" case). **16 Nov 2026:** applied to network charges too: Energinet producer tariffs (O4) are out of the base (0 / 0 / 9.2 DKK/MWh), charging them is a sensitivity (+80 NSM / +11 HES on break-even). Chapter 21 (v0017, May 2025, p. 142), read since, lists insurance in fixed OPEX but does not mention network or system charges, so the tariff removal rests on the general guideline |
| V7 | Impairment discount rates | **Vattenfall AB FY2025, BA Wind: 6.9–9.2 % before tax / 5.7–7.4 % after tax** (2024: 6.3–8.9 / 4.4–6.7). Rates vary by cash-generating unit "depending on their risk"; market-based information used. Nominal/real not stated, but the terminal value uses "a steady growth rate of 2 % (0 %)", i.e. nominal cash flows → rates read as **nominal** (inference) → ≈ **3.6–5.3 % real** after tax. Context: Vattenfall NV (Dutch subsidiary) FY2024 Wind Offshore 5.0 % after tax; Ørsted discloses only US CGU rates (6.0–7.0 %, 30 Jun 2026) | Vattenfall Annual and Sustainability Report 2025, Note 27 "Impairments and reversed impairments" (consolidated notes); Vattenfall NV AR 2024; Ørsted AR 2025 note 3.2, H1 2026 notes 4 and 12 (via report) | Ext; nominal = inference | No input change. **Reframe** (see §2) |
| V8 | Return targets | RWE: target IRR > 8.5 % (post-tax, unlevered, nominal) = 150–350 bp over WACC → WACC ≈ 5.0–7.0 % nominal ≈ 2.9–4.9 % real. Ørsted: 150–300 bp spread to WACC at bid/FID ("not a hurdle rate") | RWE investor presentations 2025; Ørsted AR 2025 pp. 15, 22 (via report) | Ext | Use for the reframing |
| V9 | AF25 technology-weighted prices (S1-B′) | The price note says prices come from Ramses, climate years 1995/2008/2009 weighted by an ENTSO-E method (weights not published). It does **not** explain how offshore-weighted prices are computed. The report's suggestion that a single-year hourly series is being paired with a weighted price does not apply: method B pairs each climate year's own hourly series (progress notes) | DEA price note ens.dk/media/7614, pp. 2–7 (via report) | Open | Keep S1 and S1-B′ side by side. Email the DEA (journal no. 2025-3657) |
| V10 | AF25 assumptions for the two sites | AF25 assumes NSM 1,000 MW (+500 MW overplanting from 2035), **4,800 full-load hours**; Hesselø **1,100 MW**, **4,450 h** | DEA "AF25 – Havvind" note, ens.dk/media/7608, tables 1–2 (via report) | Ext | Cross-check passes: my AAP is 4,690 h (NSM, before Nordsøen Syd's wake) and 4,367 h (HES) after the Nov 2026 re-run (was 4,796 / 4,514). DEA assumes overplanting at both sites; overplanting is merchant upside not in my base case (F5) – add as an open item |
| V11 | DEA ch. 21 distance/depth formulas | Read 16 Nov 2026 (ens.dk/media/8614, v0017 May 2025, pp. 142–143, Table 7, 2023 prices): export cables 5.05 k€/MW/km AC (proportional to distance), foundations 0.45 M€/MW + 5 k€/MW per m depth; "Point of connection is defined at the coastline, i.e. costs associated with onshore cables are not included". The Feb 2025 brief discourages interpolating **between years** | DEA chapter 21 text; DEA brief ens.dk/media/6572 (via report) | Ext; formula comparison open | Site adjustment unchanged (my interpolation between DEA sheets, which has an intercept: at 45.7 km it gives 0.214 M€₂₀₂₀/MW against ≈ 0.20 from a distance-proportional rate). The coastline boundary confirms that NSM's onshore cable (G2) is not in the DEA offshore figures. Note: the capex low case (−15 %, interpolated between the 2025 and 2050 bands) is an interpolation between years |

## 2. Reframing the cost-of-capital finding

The rate that sets NPV = 0 at the awarded strike is the project's **implied return** (an IRR-like discount rate), not a WACC. It should be compared with what developers target over their WACC:

| | Real post-tax |
|---|---|
| Implied return at the awarded strikes (CfD period; tail +2 pp), after the Nov 2026 re-run | **3.4 % (NSM), 4.5 % (HES)** (step-7 run: 4.5 % / 4.7 %) |
| Vattenfall AB, BA Wind discount rate after tax, FY2025 (read as nominal) | ≈ 3.6–5.3 % |
| Vattenfall NV offshore impairment rate, FY2024 (if nominal) | ≈ 2.9 % |
| RWE implied WACC range | ≈ 2.9–4.9 % |
| RWE target IRR (> 8.5 % nominal) | > ≈ 6.4 % |

Reading (Asm): Vattenfall's own after-tax discount rate for wind is about 3.6–5.3 % real across its wind units. A Danish offshore farm with a 20-year two-sided CfD should sit towards the low end (≈ 3.6 %). Hesselø's implied return sits at the midpoint of Vattenfall's range, about **0.9 pp above its low end** – below the 150–350 bp spreads RWE and Ørsted say they target. Since NSM's developer-built grid connection was costed (Nov 2026), NSM's implied return (3.4 %) sits **below** the range. The 5.0 % real base case sits in the upper third of Vattenfall's range, so it is a slightly conservative central case rather than a neutral one.

Wording to use from now on: "the bids imply a real after-tax return of about 4.5 % (Hesselø) and 3.4 % (NSM)", not "a cost of capital of …".

## 3. Effect of V1 and V6

**Re-run result (21 Oct 2026):** V6 −19 / −20 DKK/MWh, V1 +4.5 / +4.8, net break-even 533 (NSM) / 559 (HES), a 3–6 % gap. The rough estimate below is kept for the record. After the Nov 2026 review the base is 713 / 577; `step7/headline_check.py` prints each change reverted from the new base.

Rough estimate made before the re-run

Scaled from the step-5 sensitivities (Asm):
- V6, insurance out of base opex (−DKK 75k/MW/yr): break-even about **−20 DKK/MWh** at both sites (from the Hesselø opex sensitivity, ≈ 0.27 DKK/MWh per DKK 1k/MW/yr).
- V1, cables and substation to 7 %: about **+5 to +7 DKK/MWh** (export cable alone was ≈ 1 DKK/MWh for 5.5 % of K1; this moves ≈ 33 %).
- Net: break-even roughly 10–15 DKK/MWh lower, so the gap to the awarded strikes narrows from 6–9 % to roughly 3–6 % (confirmed by the re-run).

## 4. Still open

1. ~~Vattenfall AB 2025 Note 27~~ – read (V7). BA Wind covers on- and offshore; no offshore-only rate is disclosed.
2. How AF25 offshore-weighted prices are computed (S1-B′): not documented; not pursuing a DEA query (slow). S1-B′ stays a labelled downside.
3. DEA chapter 21 formulas; whether chapter 21's O&M definition matches the guideline (insurance, network charges).
4. Overplanting as merchant upside (AF25 assumes it at both sites).
5. Hesselø scale / nature-inclusive capex premium (unchanged).
6. Check the "(via report)" rows against their primary documents, starting with V6 (insurance, the largest step-7 change) and V7 (Vattenfall's rate). Name the research report or replace it with primary citations.
7. ~~V6 network charges vs Energinet producer tariffs (O4)~~ – applied 16 Nov 2026: tariffs out of the base, kept as a sensitivity. Chapter 21 itself lists insurance but not network charges (V6 row), so this rests on the guideline.
8. Net cap: does the contract count past payments against the cap in real or nominal terms (Appendix 3 §2.5)? The model deflates them; the tender documents aren't in the repo. Open.
9. Hesselø's onshore scope under the 2025 framework (earlier planning: winner builds land cables from Gilbjerg Hoved to Hovegård). Not costed. Open.
10. Compare the step-4 site interpolation with the chapter 21 formulas (V11). Open.
