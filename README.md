# What do Vattenfall's Danish offshore wind CfD bids imply?

**Question:** Vattenfall won Denmark's 2026 offshore wind tenders at **DKK 504/MWh (Nordsøen Midt, 1 GW, DK1)** and **DKK 542/MWh (Hesselø, 0.8 GW, DK2)**. What capex, cost of capital and yield do those strikes imply?

This repo rebuilds both bids from public data: the tender's contract terms, an hourly yield model, Danish power prices and DEA scenarios, DEA cost data, and a monthly DCF with the CfD's net payment cap. It then solves for the inputs that make NPV = 0 at the awarded strikes.

All figures are in **real 2026 DKK**, with NPV at the bid date (20 May 2026). Every input is tagged **Doc** (tender documents), **Ext** (named outside source) or **Asm** (my assumption) in the step memos.

## Findings

- **The awarded strikes are 6–9 % below my base-case break-even.** Nordsøen Midt (NSM) breaks even at **DKK 547/MWh** (awarded 504) and Hesselø at **DKK 575/MWh** (awarded 542). At the awarded strikes NPV is −DKK 1.5bn and −0.8bn, about 5–7 % of capex.
- **Any one of these closes the gap:** a real post-tax CfD-period WACC of **4.25 % (NSM) / 4.5 % (Hesselø)** instead of 5.0 %; or all-in capex of **DKK 20.2 / 20.7m/MW** (≈ €2.7–2.8m/MW, 7–10 % below the DEA-based base); or a P10 rather than P50 yield.
- **The bids look like a bet on 20 MW-class turbines.** With the DEA's FID-2025 costs (15 MW units) the bids clear only at a 2.6–2.8 % WACC, too low for a private developer. With FID-2030 costs (20 MW units) and the matching yield they clear at 4.6–4.8 %.
- **The net cap on state payments makes NSM much riskier than Hesselø.** NSM's cap covers on average only **DKK 167/MWh** of support over 20 years, against **313** at Hesselø. In a low power-to-X price scenario NSM's cap runs out in **July 2047**, DKK 5.5bn of payments are never made, and no strike gives NPV = 0. Hesselø never uses more than 76 % of its cap. This may help explain why NSM drew only two bids against Hesselø's five (interpretation).

Full write-up: **[step5/bid_calibration_memo.md](step5/bid_calibration_memo.md)** (two pages).

![Break-even strike sensitivity, Nordsøen Midt and Hesselø](step5/outputs/fig_tornado.png)

*Break-even strike, one input at a time. Capex and WACC dominate; at NSM their high cases push the break-even into the net cap. Yield, tail value and availability are second-order.*

![CfD WACC giving NPV = 0 at the awarded strike, by capex and yield](step5/outputs/fig_wacc_vs_capex.png)

*Capex and CfD-period WACC combinations that give NPV = 0 at the awarded strikes, for P90 / P50 / P10 yield and a 13 % wake case. The base inputs (◆) sit above the P50 line, so NPV is negative at the base case.*

## Method

| Step | What it does | Read |
|---|---|---|
| 1. Contract terms | Turns the tender documents into model rules: settlement on Available Active Power (AAP), a monthly AAP-weighted reference price floored at 0, an NPI-indexed strike, a running net cap, and a one-month payment lag. | [contract_assumptions.md](contract_assumptions.md) |
| 2. Yield | ERA5 2006–2025 wind, quantile-mapped onto Energinet's LiDAR-based Weibull at 150 m, IEA 15 MW power curve, loss stack. Hourly AAP and metered output; AAP capacity factor 54.8 % (NSM) and 51.5 % (Hesselø). | [step2/](step2/README.md) · [yield_model.ipynb](step2/yield_model.ipynb) |
| 3. Prices | DK1/DK2 day-ahead prices 2016–2025 and the site reference price (capture ratio ≈ 0.88). 2033–2052 scenarios from DEA AF25 hourly prices, paired with site yield for the same weather year. | [step3/](step3/README.md) · [price_scenarios_method.md](step3/price_scenarios_method.md) · [price_analysis.ipynb](step3/price_analysis.ipynb) |
| 4. Costs, tax, WACC | DEA Technology Data (FID-2030 column), site-adjusted for distance and depth; Energinet connection contribution; opex; Danish tax depreciation; WACC ranges from developer disclosures. | [step4/cost_assumptions.md](step4/cost_assumptions.md) |
| 5. DCF and calibration | Monthly CfD settlement with net cap and payment lag, tax pools on nominal cost deflated to real terms, separate CfD and merchant-tail discount rates, and solvers for the break-even strike and the NPV = 0 WACC and capex. | [bid_calibration_memo.md](step5/bid_calibration_memo.md) · [bid_calibration.ipynb](step5/bid_calibration.ipynb) |

## Data sources

| Source | Used for | Licence / terms | In this repo? |
|---|---|---|---|
| DEA tender documents for North Sea I South (Nordsøen Syd), Nov 2025: Annex F Concession Agreement, Appendix 3 and 3.1, Procurement Specifications; DEA *Step-by-Step Guide* (27 Mar 2026); Energinet draft Bilag 2.3 | Contract terms (step 1) | Tender material, no open licence | **No.** Cited by section number only |
| [DEA press release, 4 Aug 2026](https://via.ritzau.dk/pressemeddelelse/15074199/danmark-far-to-nye-havvindmolleparker?lang=da) | Awarded strikes and bid counts | – | Link only |
| ERA5 (Hersbach et al., C3S) via [Open-Meteo](https://open-meteo.com/) | Hourly wind, 1995 and 2006–2025 | CC BY 4.0 | Recreated by `step2/era5_openmeteo.py` |
| Energinet site wind assessments (C2Wind, North Sea I, rev. 3; EMD, Hesselø South, rev. 3) | Long-term wind level and shape at 150 m | Energinet site data | Values cited only |
| IEA 15 MW reference turbine, from NREL's `turbine-models` repository | Power curve | See the source repository | `step2/data/IEA_Reference_15MW_240.csv` |
| [Energi Data Service](https://www.energidataservice.dk/) (Energinet) | DK1/DK2 day-ahead prices, metered wind | CC BY 4.0 | Recreated by `step3/eds_price_download.py` |
| [DEA Technology Data, generation of electricity and district heating](https://ens.dk/en/analyses-and-statistics/technology-data-generation-electricity-and-district-heating), workbook v0019, sheet "21 Offshore Wind AC Fixed" | Capex and O&M | CC BY 4.0 | Extracted rows only (`step4/outputs/`, `step4/dea_offshore_ac_2030.yaml`) |
| [DEA Analysis Assumptions for Energinet 2025 (AF25)](https://ens.dk/analyser-og-statistik/analyseforudsaetninger-til-energinet), [price dataset](https://ens.dk/media/7632/download) | 2033–2052 price scenarios | DEA publication | **No.** Download manually (see below) |
| Statistics Denmark PRIS04 (net price index) | Price base and strike indexation | Statistics Denmark terms (attribution) | Index values quoted |
| Energinet tariff catalogue 2026; Afskrivningsloven, Selskabsskatteloven | Connection contribution, producer tariffs, tax | Public | Cited |

## How to run

Windows, PowerShell, Python 3.13. Run from the repo root unless a step says otherwise.

```powershell
git clone https://github.com/fergal567/danish-offshore-cfd-bid-model.git
cd danish-offshore-cfd-bid-model
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks the activation script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

**Manual downloads** (third-party files that are not redistributed here):

| File | Save as | Needed for |
|---|---|---|
| [AF25 – datasæt – elprisfremskrivning](https://ens.dk/media/7632/download) | `step5/data/AF25 - datasæt - elprisfremskrivning.xlsx` | Step 5 price scenarios |
| [DEA Technology Data workbook](https://ens.dk/en/analyses-and-statistics/technology-data-generation-electricity-and-district-heating) (v0019) | `step4/data/technology_data_for_el_and_dh_-_0019.xlsx` | Only to rebuild step 4. `step4/cost_inputs.yaml` is committed, so step 5 runs without it |

**Run order:** step 2 → step 3 → step 4 → step 5. Each step writes the files the next one reads.

| Step | Commands | Recreates (git-ignored) | Time |
|---|---|---|---|
| 2 | `cd step2`, then `python era5_openmeteo.py --extra-years 1995`, then `jupyter nbconvert --to notebook --execute --inplace yield_model.ipynb`, then `cd ..` | `step2/data/era5_*.csv`, `step2/data/aap_hourly_*.csv` | ≈ 5 min download, no API key |
| 3 | `cd step3`, then `python eds_price_download.py --start 2016 --end 2025 --wind`, then `jupyter nbconvert --to notebook --execute --inplace price_analysis.ipynb`, then `cd ..` | `step3/data/` (raw cache and reference-price outputs) | ≈ 1 min |
| 4 | Optional, from the repo root: `python step4\dea_extract.py "step4\data\technology_data_for_el_and_dh_-_0019.xlsx" --sheet "21 Offshore Wind AC Fixed" --year 2030`, then `python step4\build_cost_inputs.py` | `step4/outputs/dea_*.csv`, `step4/cost_inputs.yaml`, `step4/outputs/cost_table.md` (all committed) | seconds |
| 5 | `python step5/reconstruct_aap_1995.py`, then `cd step5`, then `jupyter nbconvert --to notebook --execute --inplace bid_calibration.ipynb`, then `cd ..` | `step5/data/aap_hourly_1995_*.csv`, `step5/outputs/` | ≈ 2–3 min |

**Tests** (45 in total; integration tests skip themselves when their data files are missing):

```powershell
python -m pytest step3/tests -q
python -m pytest step4/tests -q
python -m pytest step5/tests -q
```

## Repo layout

```
danish-offshore-cfd-bid-model/
├── README.md
├── LICENSE
├── requirements.txt
├── contract_assumptions.md        # Step 1: CfD terms, tagged Doc / Ext / Asm
├── progress-notes.md              # Working log: results and decisions by step
├── step2/                         # Yield model
│   ├── README.md
│   ├── era5_openmeteo.py          # ERA5 via Open-Meteo (used)
│   ├── era5_download.py           # Copernicus CDS fallback
│   ├── yield_model.ipynb
│   ├── data/IEA_Reference_15MW_240.csv
│   └── outputs/                   # yield_annual_summary.csv, yield_config.json
├── step3/                         # Prices and CfD reference price
│   ├── README.md
│   ├── eds_price_download.py
│   ├── price_analysis.ipynb
│   ├── price_scenarios_method.md
│   └── tests/
├── step4/                         # Cost, tax and WACC inputs
│   ├── README.md
│   ├── cost_assumptions.md        # Memo
│   ├── dea_extract.py             # DEA workbook → dea_offshore_ac_2030.yaml
│   ├── dea_offshore_ac_2030.yaml
│   ├── build_cost_inputs.py       # → cost_inputs.yaml
│   ├── cost_inputs.yaml           # Read by step 5
│   ├── outputs/                   # cost_table.md, DEA sheet extract
│   └── tests/
└── step5/                         # DCF and bid calibration
    ├── README.md
    ├── bid_calibration_memo.md    # Headline findings
    ├── dcf_model.py
    ├── reconstruct_aap_1995.py
    ├── bid_calibration.ipynb
    ├── outputs/                   # Result CSVs and charts
    └── tests/
```

## Limitations and open items

- **Contract terms are a proxy.** The tender documents in hand are for Nordsøen Syd. NSM's and Hesselø's own Annex F and Appendix 3 were not available, so guarantees, liability caps and CfD-start wording follow Nordsøen Syd. The net cap amounts come from the DEA guide (NSM) and the EU contract notice (Hesselø).
- **The 1995 climate year is reconstructed.** AF25 uses weather years 1995, 2008 and 2009. 1995 site output is rebuilt from ERA5 wind by learning step 2's wind → AAP mapping (held-out R² 0.998 NSM, 0.991 Hesselø), not run through the step-2 notebook.
- **There is a gap against the DEA's own capture factors.** Pairing AF25 hourly prices with site yield gives offshore capture factors of 0.84–0.91 within each month. The DEA's published fleet-weighted ratios are much lower (DK1: 0.57 / 0.95 / 0.76 in 2030 / 2040 / 2050). I keep my pairing as the central case and run the DEA ratio as a downside, where NSM's break-even rises to DKK 683/MWh. The DEA's method is still to be checked.
- **Tax classifications are unverified.** I depreciate the export cable at 7 % as electricity infrastructure (Afskrivningsloven §5C stk. 2) and treat the Energinet contribution as a §43 connection fee. No SKAT ruling was found. Switching the cable to 15 % moves break-even by only about −1 DKK/MWh.
- **Cost adjustments are approximations.** Capex is site-adjusted by interpolating between the DEA's own datasheets, not the chapter 21 formulas. Hesselø carries no scale or nature-inclusive design premium, and its Energinet area classification is unconfirmed (connection contribution DKK 157–532m). It is unclear whether DEA fixed O&M includes insurance.
- **The WACC is not yet checked against primary data.** The implied 4.25–4.5 % real CfD-period WACC should be compared with Vattenfall's and Ørsted's 2025 impairment-test discount rates.
- **This is an outside-in reconstruction.** It uses only public information, is not affiliated with Vattenfall, the DEA or Energinet, and does not claim to reproduce Vattenfall's actual inputs.

## About

Fergal Israel, MSc Wind Energy student at DTU (2026–2028), BEng Mechanical Engineering (Swansea University). Interested in the commercial and advisory side of offshore wind: site selection, feasibility and project development.

Code is released under the [MIT licence](LICENSE). Data and values from third parties keep their own licences, listed above.
