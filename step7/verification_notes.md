# Project 1 – Step 7: primary-source verification

**Prepared:** 21 Oct 2026 · **Status:** findings recorded; model changes not yet run
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
| V6 | Does DEA fixed O&M include insurance? (O2) | Yes, per the catalogue guideline: fixed O&M includes administration, staff, service agreements, **network or system charges**, property tax and **insurance** | DEA Technology Data, Guideline, "O&M costs", pp. 27–28 (via report) | Ext; general guideline, chapter 21 not checked | Set O2 insurance **base to 0** (low 0, high = old base DKK 75k/MW/yr as a "not included after all" case). Test Energinet producer tariffs (O4) for double counting as a sensitivity only |
| V7 | Impairment discount rates | **Vattenfall AB FY2025, BA Wind: 6.9–9.2 % before tax / 5.7–7.4 % after tax** (2024: 6.3–8.9 / 4.4–6.7). Rates vary by cash-generating unit "depending on their risk"; market-based information used. Nominal/real not stated, but the terminal value uses "a steady growth rate of 2 % (0 %)", i.e. nominal cash flows → rates read as **nominal** (inference) → ≈ **3.6–5.3 % real** after tax. Context: Vattenfall NV (Dutch subsidiary) FY2024 Wind Offshore 5.0 % after tax; Ørsted discloses only US CGU rates (6.0–7.0 %, 30 Jun 2026) | Vattenfall Annual and Sustainability Report 2025, Note 27 "Impairments and reversed impairments" (consolidated notes); Vattenfall NV AR 2024; Ørsted AR 2025 note 3.2, H1 2026 notes 4 and 12 (via report) | Ext; nominal = inference | No input change. **Reframe** (see §2) |
| V8 | Return targets | RWE: target IRR > 8.5 % (post-tax, unlevered, nominal) = 150–350 bp over WACC → WACC ≈ 5.0–7.0 % nominal ≈ 2.9–4.9 % real. Ørsted: 150–300 bp spread to WACC at bid/FID ("not a hurdle rate") | RWE investor presentations 2025; Ørsted AR 2025 pp. 15, 22 (via report) | Ext | Use for the reframing |
| V9 | AF25 technology-weighted prices (S1-B′) | The price note says prices come from Ramses, climate years 1995/2008/2009 weighted by an ENTSO-E method (weights not published). It does **not** explain how offshore-weighted prices are computed. The report's suggestion that a single-year hourly series is being paired with a weighted price does not apply: method B pairs each climate year's own hourly series (progress notes) | DEA price note ens.dk/media/7614, pp. 2–7 (via report) | Open | Keep S1 and S1-B′ side by side. Email the DEA (journal no. 2025-3657) |
| V10 | AF25 assumptions for the two sites | AF25 assumes NSM 1,000 MW (+500 MW overplanting from 2035), **4,800 full-load hours**; Hesselø **1,100 MW**, **4,450 h** | DEA "AF25 – Havvind" note, ens.dk/media/7608, tables 1–2 (via report) | Ext | Cross-check passes: my AAP is 4,796 h (NSM) and 4,514 h (HES). DEA assumes overplanting at both sites; overplanting is merchant upside not in my base case (F5) – add as an open item |
| V11 | DEA ch. 21 distance/depth formulas | Not readable. DEA's Feb 2025 brief says the costs can be adjusted for depth and distance within stated ranges, and discourages interpolating **between years** | DEA brief ens.dk/media/6572 (via report) | Open | Keep the site adjustment, labelled "my interpolation between DEA sheets; DEA formula unverified". Note: the capex low case (−15 %, interpolated between the 2025 and 2050 bands) is an interpolation between years |

## 2. Reframing the cost-of-capital finding

The rate that sets NPV = 0 at the awarded strike is the project's **implied return** (an IRR-like discount rate), not a WACC. It should be compared with what developers target over their WACC:

| | Real post-tax |
|---|---|
| Implied return at the awarded strikes (CfD period; tail +2 pp) | **4.25 % (NSM), 4.5 % (HES)** |
| Vattenfall AB, BA Wind discount rate after tax, FY2025 (read as nominal) | ≈ 3.6–5.3 % |
| Vattenfall NV offshore impairment rate, FY2024 (if nominal) | ≈ 2.9 % |
| RWE implied WACC range | ≈ 2.9–4.9 % |
| RWE target IRR (> 8.5 % nominal) | > ≈ 6.4 % |

Reading (Asm): Vattenfall's own after-tax discount rate for wind is about 3.6–5.3 % real across its wind units. A Danish offshore farm with a 20-year two-sided CfD should sit towards the low end (≈ 3.6 %), so the bids imply a return only about **0.6–0.9 pp** above it – well below the 150–350 bp spreads RWE and Ørsted say they target. The bids therefore look aggressive on return, not just plausible. The 5.0 % real base case sits mid-range of Vattenfall's own rates, which supports it as a neutral central case. Final numbers depend on the step-5 re-run (§3), which raises the implied return slightly.

Wording to use from now on: "the bids imply a real after-tax return of about 4.25–4.5 %", not "a cost of capital of 4.25–4.5 %".

## 3. Expected effect of V1 and V6 (rough, before re-running step 5)

Scaled from the step-5 sensitivities (Asm):
- V6, insurance out of base opex (−DKK 75k/MW/yr): break-even about **−20 DKK/MWh** at both sites (from the Hesselø opex sensitivity, ≈ 0.27 DKK/MWh per DKK 1k/MW/yr).
- V1, cables and substation to 7 %: about **+5 to +7 DKK/MWh** (export cable alone was ≈ 1 DKK/MWh for 5.5 % of K1; this moves ≈ 33 %).
- Net: break-even roughly 10–15 DKK/MWh lower, so the gap to the awarded strikes narrows from 6–9 % to roughly 3–6 %. **To be confirmed by re-running step 5.**

## 4. Still open

1. ~~Vattenfall AB 2025 Note 27~~ – read (V7). BA Wind covers on- and offshore; no offshore-only rate is disclosed.
2. How AF25 offshore-weighted prices are computed (S1-B′): not documented; not pursuing a DEA query (slow). S1-B′ stays a labelled downside.
3. DEA chapter 21 formulas; whether chapter 21's O&M definition matches the guideline (insurance, network charges).
4. Overplanting as merchant upside (AF25 assumes it at both sites).
5. Hesselø scale / nature-inclusive capex premium (unchanged).
