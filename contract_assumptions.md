# Project 1 – Contract assumptions (Danish capability-based CfD)

**Scope:** contract terms feeding the cash-flow model for Nordsøen Midt (NSM, North Sea I Mid) and Hesselø, using the Nordsøen Syd (NSS, North Sea I South) tender documents (Nov 2025) as the framework basis.
**Prepared:** 20 Oct 2026 · Step 1 of Project 1.

**Status key**
- **Doc** – stated in the NSS tender documents in the project files (Annex F = Concession Agreement; App 3 / App 3.1; Proc Spec = Procurement Specifications; Guide = DEA Step-by-Step Guide, which is illustrative and yields to Annex F; Bilag 2.3 = Energinet draft connection contribution).
- **Ext** – from an outside source (named in the Source column).
- **Asm** – my modelling assumption; not settled by any source. Change freely.
- **⚠ site** – value is NSS-specific and may differ for NSM / Hesselø.

## A. Bid and strike price

| # | Assumption | Value (base case) | Source | Status | How it enters the model |
|---|---|---|---|---|---|
| A1 | What is bid | One strike price, DKK/MWh excl. VAT, max 4 decimals; lowest bid wins; price is the only award criterion; ties drawn by lot | Proc Spec §10.1–10.2; Annex F 2.49 | Doc | The calibration target: solve for capex/WACC/yield combinations that give NPV = 0 at the awarded strike |
| A2 | Awarded strike prices | NSM **DKK 504/MWh**; Hesselø **DKK 542/MWh** (Vattenfall, 4 Aug 2026; 2 and 5 bids) | DEA/KEFM award announcement, as reported by Reuters (via Baird Maritime) and DI Energi | Ext | `K0_NSM = 504`, `K0_HES = 542` |
| A3 | Strike price base | 2026 prices; indexation base = NPI May 2026 (bid deadline 20 May 2026) | Guide §2.3 (NSS itself: 2028 prices, base NPI Oct 2028, App 3 §2.1.1) | Doc (Guide) ⚠ site | `K_y = K0 × NPI_Sep(y−1) / NPI_May2026` |
| A4 | Strike indexation | 100% Danish Net Price Index (NPI), reset each 1 Jan using previous September NPI, for the full 20 years | App 3 §2.1.1; Annex F 11.1.12 | Doc | Model in real 2026 DKK (strike constant in real terms), or nominal with an NPI path |
| A5 | NPI forecast (only if modelling nominal) | 2.0%/yr | Guide §2.3 uses 2% purely as an example | Asm | Inflation path for strike, net cap, opex |
| A6 | Maximum bid price | None found in tender documents or ministry summary; the binding limit is the net payment cap (B5) | Proc Spec §10; KEFM one-pager (May 2025) | Doc (absence) | No bid ceiling constraint |

## B. Settlement mechanics

| # | Assumption | Value (base case) | Source | Status | How it enters the model |
|---|---|---|---|---|---|
| B1 | Settlement volume | Available Active Power (AAP′) of the **Minimum Capacity** only, per 10-min interval, summed monthly: `AAP′ = 1/6 Σ (WF_avail + DR + SM) × AAP_table` | App 3 §§2.1, 5.2; App 3.1 §3.2; Guide §1.2 | Doc | Proxy: modelled potential output of MinCap turbines (net of internal + external wakes) × (1 − unscheduled-downtime share) |
| B2 | What counts in volume | Normal operation + forced curtailment (TSO) + market-based curtailment + scheduled maintenance (pre-notified on a REMIT IIP). Unscheduled maintenance excluded | App 3 §2.6; Annex F 11.1.5 | Doc | `CfD_volume = potential × (1 − unscheduled_unavail)` |
| B3 | Unscheduled unavailability | 3% of potential | — | Asm | Reduces CfD volume and actual sales |
| B4 | Reference price | Monthly; AAP-weighted average day-ahead price of the farm's bidding zone; negative MTU prices set to 0 | App 3 §2.1 eq. (1), §2.6.3; Annex F 2.45 | Doc | `RP_m = Σ AAP_h · max(p_h, 0) / Σ AAP_h` |
| B5 | Bidding zone | NSM = DK1; Hesselø = DK2 | Geography; research report | Asm (verify) | Selects the price series |
| B6 | Payment formula | `Pay_m = AAP_m × (K_y − RP_m)`; positive → state pays; negative → developer pays | App 3 eq. (2); Annex F 11.4.1, 11.5.1 | Doc | Monthly CfD cash flow |
| B7 | Payment timing | Both directions settled on the 25th of the following month; AAP data due 6 workdays after month-end | Annex F 10.3.1, 11.4.2, 11.5.3 | Doc | One-month lag (working capital) |
| B8 | Payments to the state | Uncapped; no opt-out | App 3 §2.1; Annex F 11.4.1 | Doc | Clawback has no ceiling |
| B9 | Net cap on state payments | NSM **DKK 15.7bn**; Hesselø **DKK 21.9bn**; NSS 6.6bn. All excl. VAT, 2025 prices, NPI-indexed from 1 Jun 2025; clawbacks replenish the cap | NSS: App 3 §2.5, Annex F 11.5.2. NSM: Guide §2.4. Hesselø: EU contract notice (Mercell/TED). Sum 44.2bn excl. VAT = 55.2bn incl. VAT (KEFM) | Doc / Ext ⚠ site | Running cap; `subsidy_m = min(need_m, cap_remaining)`; cap += clawbacks; cap indexed yearly |
| B10 | Interim settlement | From CfD start until the AAP table is approved (≥12 months + approval): `DEA_estimate_m × (K − RP_interim_m)`, with RP weighted by **actual** production. Trued up once the table is approved, NPI-indexed, no interest | App 3 §§2.2–2.3; Annex F 11.1.8, 11.2 | Doc | Year 1–2 handling; base case may ignore true-up (small NPV effect) |
| B11 | DEA interim production estimate | NSM 4,479 GWh/yr (≈51% CF on 1 GW); NSS 4,483 GWh/yr; Hesselø not available | Guide Table 1.5; App 3 Table 1 | Doc ⚠ site | Interim volume; also a DEA yield benchmark to compare against the ERA5 yield |
| B12 | Boosting | Allowed; settlement capped at Minimum Capacity | App 3 §2.6.4 | Doc | `AAP ≤ MinCap` each interval |
| B13 | Market sales and balancing | Developer sells all output at its own cost and risk; balancing costs not reimbursed | Annex F 11.6.4 | Doc | Merchant revenue `Σ gen_h × p_h` minus balancing cost |
| B14 | Balancing / route-to-market cost | DKK 15/MWh of metered output | — | Asm | Opex per MWh |

## C. Negative prices, curtailment, wakes

| # | Assumption | Value (base case) | Source | Status | How it enters the model |
|---|---|---|---|---|---|
| C1 | Negative-price hours | No suspension of support. AAP still counts; price floored at 0 in RP only. Developer may curtail for market reasons and still be settled on AAP | App 3 §§2.6.1, 2.6.3; Guide §1.5 (Example 2), §2.1 | Doc | Dispatch rule: `gen_h = 0` when `p_h < 0`; AAP_h still in volume and RP weights |
| C2 | Forced (TSO) curtailment | Settled as normal on AAP; needs a log and an annual solemn declaration, otherwise subsidy can be reclaimed | App 3 §2.6.1; Annex F 11.1.6–11.1.7 | Doc | AAP unaffected; only merchant sales lost |
| C3 | Wake treatment | AAP table is built empirically from the farm's own SCADA in a 12-month commissioning campaign, so internal wakes and any external wakes present at that time are embedded in AAP. A later neighbour changes AAP only via recalibration (every 5 yrs, or if AAP exceeds actual by >5% in >3 months per 12) or recommissioning | App 3 §§4, 5.3–5.4; App 3.1 §§2, 4 | Doc + interpretation | AAP = potential **net** of wakes; external wake risk stays with the developer |
| C4 | External wake scenario | NSM: Thor wake from COD; NSS wake on NSM from 2035 | Thor in operation 2027 (research report); NSS deadline Annex F 7.3.1 | Asm | Later PyWake step (Project 2) supplies the % loss |
| C5 | Overplanting wakes | Overplanted turbines are in the upstream ranking; their wake on MinCap turbines lowers MinCap's AAP | App 3 §4.1.1; App 3.1 §2.1 | Doc | Overplanting scenarios must reduce MinCap AAP |

## D. Term and timing

| # | Assumption | Value (base case) | Source | Status | How it enters the model |
|---|---|---|---|---|---|
| D1 | CfD start | 00:00 the day after Operational Capability Minimum Capacity. Annex F adds "or, if relevant, Operational Capability Overplanting Capacity" (ambiguous; Annex F prevails over the Guide) | Annex F 11.1.2; Guide §1.6 | Doc (ambiguous) | Base case has no overplanting, so start = MinCap COD |
| D2 | CfD term | 20 years from actual start (floating, no fixed end date) | Annex F 11.1.3 | Doc | 240 monthly periods |
| D3 | Completion deadline (MinCap) | NSM and Hesselø: end-2032. NSS: construction start 31 Dec 2033, operational capability 31 Dec 2034 | NSM/Hesselø: DEA press release 20 Nov 2025. NSS: Annex F 7.3.1 | Ext / Doc ⚠ site | Timing anchor |
| D4 | Assumed COD | 1 Jan 2033 (NSM and Hesselø); CfD runs 2033–2052 | — | Asm | First CfD month |
| D5 | Asset life | Electricity production permit 30 years (extendable ≤10) → 20 yrs CfD + ~10 yrs merchant | Annex F 19.2 | Doc | Merchant tail 2053–2062 |
| D6 | Late delivery | Support period not shortened (starts at actual COD); delay damages apply (E-rows) | Annex F 11.1.3, 15.1 | Doc | Delay scenario: shift COD + add LDs |

## E. Delay damages, guarantees, termination (NSS values – may differ for NSM, and likely scale for 0.8 GW Hesselø) ⚠ site

| # | Assumption | Value | Source | Status | How it enters the model |
|---|---|---|---|---|---|
| E1 | Construction start delay | DKK 2.5m per commenced month, first 12 months; forfeited if MinCap COD is met on time | Annex F 15.1.3, 15.3.1 | Doc | Delay scenario only |
| E2 | COD delay damages | DKK 2.5m/month (months 1–12), 6m (13–24), 17.5m (25–36), 34m (37–48); cap DKK 720m (= 48 months), after which DEA may terminate | Annex F 15.1.6–15.1.7 | Doc | Delay scenario only |
| E3 | Termination lump sum | DKK 750m less LDs already paid | Annex F 20.2.3.1 | Doc | Downside scenario |
| E4 | Overall liability cap | DKK 772m (+ DKK 498k/MW overplanting) | Annex F 16.5.1 | Doc | Reference only |
| E5 | Performance guarantee | ≥40% × 772m = **DKK 308.8m**, A- rated EU/EEA bank, held from signing until MinCap COD verified | Annex F 17.2 | Doc | Guarantee fee signing→COD |
| E6 | Parent company guarantee | ≤60% × 772m = **DKK 463.2m** (parent revenue ≥ DKK 32bn, solvency ≥20% or BBB-); can be replaced by a larger performance guarantee | Annex F 17.3 | Doc | No cash cost if parent qualifies |
| E7 | Guarantee fee | 1.0%/yr on the performance guarantee | — | Asm | Pre-COD cost |
| E8 | Overplanting LDs / guarantees | DKK 2,500 / 10,000 / 24,000 per MW per month by delay band; guarantee basis DKK 498k/MW | Annex F 15.2, 17.2.5 | Doc | Overplanting scenario only |

## F. Overplanting

| # | Assumption | Value (base case) | Source | Status | How it enters the model |
|---|---|---|---|---|---|
| F1 | Allowed? | Yes, optional; binding notice within 6 months of signing. NSM free (area-limited); Hesselø total ≤1.2 GW | Annex F 7.2; KEFM one-pager | Doc / Ext ⚠ site | Scenario switch |
| F2 | CfD coverage | Minimum Capacity only; neither production nor capability of overplanted turbines is supported → merchant | Annex F 11.1.9; App 3 §4.1.1 | Doc | Overplanted MW earn `Σ gen_h × p_h` only |
| F3 | Grid for overplanting | Guaranteed connection covers the minimum capacity; extra exchange capacity needs a separate Energinet application (possibly slow). Hesselø's grid option is ≥1 GW | Proc Spec §1; Bech-Bruun summary of the tender | Doc / Ext | Cap export; overplanting above grid option curtailed |
| F4 | Final area | NSS area trimmed at 4 MW/km² of notified capacity | Annex F 8.2.2 | Doc ⚠ site | Layout constraint (Project 2) |
| F5 | Base case overplanting | 0 MW | — | Asm | Keep base clean; test later |
| F6 | Minimum Capacity rounding | MinCap = 1,000 MW ÷ turbine size, rounded up or down at developer's choice × turbine size (e.g. 15 MW: 990 or 1,005 MW) | Annex F 2.32, 7.1.2 | Doc | `AAPmax = MinCap`; supported turbine count |

## G. Grid connection

| # | Assumption | Value (base case) | Source | Status | How it enters the model |
|---|---|---|---|---|---|
| G1 | Voluntary? | Yes; if connecting, Grid Connection Agreement with Energinet required (notify within 1 month of signing) | Proc Spec §1; Annex F 1.7, 7.1.4–7.1.5 | Doc | Base case: grid-connected |
| G2 | Who builds what | Energinet builds the point of connection (POC); developer builds export and onshore cable to the POC and refunds certain Energinet costs | Annex F 1.8, 2.36 | Doc (detail in App 1, not in project files) | Export/onshore cable in developer capex |
| G3 | Connection contribution – NSS | **DKK 659.6m** excl. VAT at 2026 tariffs = 2 × 400 kV bays × 18.3m + 1,000 MW × 623,000 DKK/MW (production-surplus area); Endrup 400 kV; final amount at tariffs in force when the GCA is signed | Bilag 2.3 (draft) | Doc ⚠ site | One-off capex |
| G4 | Connection contribution – NSM | ≈ DKK 0.66bn (same rate structure; West Jutland assumed production-surplus area) | — | Asm (verify) | One-off capex |
| G5 | Connection contribution – Hesselø | Depends on area classification of its North Zealand POC. Consumption-dominated areas carry a much lower per-MW rate (Nov 2024 ministerial answer: 193k vs 663k DKK/MW in production-surplus areas). Base: 193k/MW × 800 MW + 2 × 18.3m ≈ DKK 0.19bn | Ministerial answer KEF spm. 7 (Nov 2024) | Asm (verify) | One-off capex |
| G6 | Ongoing producer tariffs | 0.50 øre/kWh feed-in + 0.42 øre/kWh balance (2027) ≈ **DKK 9.2/MWh** metered; not reimbursed | Energinet press release 4 Sep 2026; Annex F 11.6.6 | Ext / Doc | Opex per MWh |
| G7 | Grid delivery date / Energinet liability | NSS: connection of MinCap guaranteed by 1 Jul 2030; Energinet liability cap DKK 1.54bn (RE Act §31) | Annex F 7.1.4 | Doc ⚠ site | Not modelled (risk note) |
| G8 | Unbundling | State may transfer export/onshore cable to Energinet without purchase price (direct transfer costs compensated) | Annex F 12 | Doc | Ignore in base case |

## H. Costs the developer does not bear

| # | Assumption | Value | Source | Status | How it enters the model |
|---|---|---|---|---|---|
| H1 | Energinet preliminary investigations | Data provided free, no warranty; state budget DKK 731.5m (2025) + 25.6m (2026) across the three sites | Proc Spec §1.1.2; Annex F 1.6; KEFM one-pager | Doc / Ext | No reimbursement of state surveys; own surveys remain in devex |
| H2 | Danish Defence radar mitigation | Borne by Danish Defence (est. DKK 1.1bn total) | Annex F 7.9.3; Proc Spec §1.2; KEFM one-pager | Doc / Ext | Zero cost |
| H3 | Concession fee / state co-ownership | None (both features of the failed 2024 design are dropped) | KEFM one-pager; research report | Ext | Zero |

## I. Other developer costs and obligations

| # | Assumption | Value | Source | Status | How it enters the model |
|---|---|---|---|---|---|
| I1 | UXO clearance | Full cost of Naval Command / Naval Diving Service | Annex F 11.6.2 | Doc | Inside capex |
| I2 | Navigational chart update | ≈ DKK 0.6m | Annex F 11.6.3 | Doc | Immaterial |
| I3 | Decommissioning | Full cost and a decommissioning guarantee set by the permits (amount not in tender docs; Danish permits typically require the cost estimate to be updated every 5 years) | Annex F 11.6.5; ENS production permits | Doc / Ext | Decom cost at end of life + security cost |
| I4 | Decommissioning cost | DEA Technology Catalogue value (to be pulled in step 2) | — | Asm | End-of-life cash flow |
| I5 | Capability compliance | Lidar ≥1, SCADA data packages, annual auditor statement, possible third-party verification of the AAP table – all at developer's cost | App 3 §§5.1, 5.5–5.6; Annex F 10.1.4 | Doc | Small opex line |
| I6 | Data-penalty regime | Late data → AAP set to 0 (subsidy months) or to theoretical max (clawback months) | Annex F 10.5 | Doc | Not modelled (operational risk) |
| I7 | Other state aid | Not allowed without DEA consent | Annex F 11.1.10 | Doc | No grants |
| I8 | Insurance | All-risk property + liability from construction start | Annex F 18 | Doc | Opex |
| I9 | Sustainability conditions | Recyclable blades, LCA, EPDs, CSR; nature-inclusive design at Hesselø | Annex F 7.5, 7.7; DEA press release | Doc / Ext | Inside capex (possible Hesselø premium) |

## Open items to close before step 2
1. Upload NSM and Hesselø Annex F / Appendix 3 if obtainable (EU-Supply), to replace NSS proxies in rows marked ⚠ site.
2. Appendix 1 (Project Specifications) is not in the project files – needed for grid scope (G2) and overplanting detail (F1, F3).
3. Confirm Hesselø's POC and Energinet area classification (G5).
4. Confirm the D1 ambiguity (CfD start when overplanting) – only matters for overplanting scenarios.
