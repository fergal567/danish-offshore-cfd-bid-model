# What do Vattenfall's Danish offshore wind CfD bids imply?

In August 2026 Vattenfall won Denmark's two offshore wind tenders: Nordsøen Midt (1 GW, West Denmark) at DKK 504/MWh and Hesselø (0.8 GW, East Denmark) at DKK 542/MWh. This project asks what those prices imply about build cost, required return and wind output.

I rebuilt both bids from public data – the tender's contract terms, an hourly yield model, Danish power prices and the DEA's price outlook and cost data – in a cash-flow model (annual cash flows, monthly CfD settlement), then solved for the inputs that make the project break even at the awarded prices. Figures are in real 2026 DKK, valued at the bid date (20 May 2026). The step memos tag each input by source: tender documents, a named outside source, or my own assumption.

## Why I built this

Denmark's 2024 offshore wind tender got zero bids, and that made me question whether the wind market was somewhere I really wanted to build a career. When Vattenfall won both sites in 2026, I wanted to find out what it actually takes to evaluate an investment that size: what data goes in, how the numbers are worked through, and what drives a company to bid the price it does. I also used it to test whether I'd enjoy analyst or consultancy work. The finding that surprised me most was how much the bids depend on the fall in costs the DEA expects by 2030.

With more time I'd run the full ERA5 dataset from Copernicus to check my wind data against it (the queue made even one month take hours), and look at what else could explain the bid: how the projects are financed, whether supply or offtake agreements sit behind them, and what strategic value Vattenfall sees in building a strong position in Danish offshore wind.

## Findings

Hesselø's price is close to my base-case break-even; Nordsøen Midt's is not. Hesselø needs DKK 577/MWh against the 542 awarded, a 6.5 % gap that is about the size of a single judgement call in the model (the site cost adjustment, the choice of price index or contingency). So Hesselø is **consistent with break-even at a real after-tax return of about 4.5 %**. Nordsøen Midt needs DKK 713/MWh against 504. Most of that gap comes from one input: the winner must build the export cable to a landfall at Nymindegab and a 53 km onshore cable to Endrup, which I cost at DKK 2.8bn from DEA unit rates. Without it Nordsøen Midt would sit at about 550.

At the awarded prices the bids imply a real after-tax return in the CfD period of about 4.5 % (Hesselø) and 3.4 % (Nordsøen Midt), against my 5.0 % (the merchant tail is discounted 2 pp higher). The alternatives are building for 7 % (Hesselø) or 20 % (Nordsøen Midt) less than my estimate from DEA cost data (DKK 20.7m and 20.2m/MW instead of 22.2m and 25.2m), or getting 6 % / 20 % more output than my median. Vattenfall discloses a 3.6–5.3 % real range for its wind business: Hesselø sits at its midpoint, Nordsøen Midt below it. That range is an impairment-test rate covering on- and offshore, and "real" is my inference. If a CfD-backed project belongs at the low end, Hesselø's margin of about 1 pp is thin next to the 150–350 bp RWE and Ørsted say they target.

Hesselø only works at the DEA's FID-2030 cost level, which assumes 20 MW-class turbines; Nordsøen Midt falls short even there (3.7 % with the 20 MW yield). With the DEA's FID-2025 column (15 MW turbines and older foundation and O&M costs) the implied return drops to 1.9–2.8 %. With FID expected in 2029 the 2030 column is the right vintage, so the bids rely on the DEA's expected cost fall arriving on time.

The biggest open question on the revenue side is the capture factor. Pairing the DEA's hourly price outlook with my site output gives annual capture factors of 0.89–0.99, well above the DEA's own published offshore ratios (0.57 / 0.95 / 0.76 for DK1 in 2030 / 2040 / 2050). With the DEA ratio, Hesselø's break-even rises to DKK 610/MWh and Nordsøen Midt has none. The DEA doesn't document how its ratios are built, so I show both cases.

The state's cap on CfD payments is the bigger difference between the two sites. Spread over 20 years it covers an average top-up of DKK 173/MWh at Nordsøen Midt but 324 at Hesselø. Nordsøen Midt's base-case break-even is already above the price at which the cap starts to bind, so a higher strike would have bought it little. In my low power-to-X stress case (prices −20 % and capture factor −0.10, both my assumptions), Nordsøen Midt's cap runs out around 2048 and roughly DKK 4bn of payments are never made, while Hesselø never uses more than 71 % of its cap. That may be part of why Nordsøen Midt drew two bids and Hesselø five, though that is my interpretation.

These numbers changed on 16 Nov 2026 after an external review: 12 % internal wake, Nordsøen Syd's wake on Nordsøen Midt, Hesselø's wind level, the strike's September index reset, producer tariffs and Nordsøen Midt's grid connection. Before the review the gap was 3–6 % at both sites. The memo shows what each change did.

More detail: the [two-page memo](step5/bid_calibration_memo.md), the [one-page summary](summary/project1_summary.pdf) and the [source checks](step7/verification_notes.md).

![Break-even strike sensitivity, Nordsøen Midt and Hesselø](step5/outputs/fig_tornado.png)

*Break-even strike, one input at a time. Capex and the discount rate dominate. At Nordsøen Midt the base case already sits where the net cap binds, so every adverse case either has no break-even or a very high one.*

![CfD-period discount rate giving NPV = 0 at the awarded strike, by capex and yield](step5/outputs/fig_wacc_vs_capex.png)

*Capex and CfD-period discount-rate combinations that give NPV = 0 at the awarded strikes, for P90 / P50 / P10 yield and a 13 % internal-wake case. The base inputs (◆) sit above the P50 line, so NPV is negative at the base case; at Nordsøen Midt they sit well above it.*

## Method

| Step | What it does | Read |
|---|---|---|
| 1. Contract terms | Turns the tender documents into model rules: settlement on Available Active Power (AAP), a monthly AAP-weighted reference price floored at 0, an NPI-indexed strike, a running net cap, and a one-month payment lag. | [contract_assumptions.md](contract_assumptions.md) |
| 2. Yield | ERA5 2006–2025 wind, quantile-mapped onto Energinet's LiDAR-based Weibull at 150 m, IEA 15 MW power curve, loss stack (12 % internal wake). Hourly AAP and metered output; AAP capacity factor 53.5 % (NSM, before Nordsøen Syd's wake from 2035) and 49.9 % (Hesselø). | [step2/](step2/README.md) · [yield_model.ipynb](step2/yield_model.ipynb) |
| 3. Prices | DK1/DK2 day-ahead prices 2016–2025 and the site reference price (capture ratio ≈ 0.88). 2033–2052 scenarios from DEA AF25 hourly prices, paired with site yield for the same weather year. | [step3/](step3/README.md) · [price_scenarios_method.md](step3/price_scenarios_method.md) · [price_analysis.ipynb](step3/price_analysis.ipynb) |
| 4. Costs, tax, discount rate | DEA Technology Data (FID-2030 column), site-adjusted for distance and depth; NSM's developer-built onshore cable (DEA energy-transport data); Energinet connection contribution; opex; Danish tax depreciation; discount-rate ranges from developer disclosures. | [step4/cost_assumptions.md](step4/cost_assumptions.md) |
| 5. DCF and calibration | Monthly CfD settlement with the September NPI strike reset, net cap and payment lag, tax pools on nominal cost deflated to real terms, separate CfD and merchant-tail discount rates, and solvers for the break-even strike and the NPV = 0 return and capex. | [bid_calibration_memo.md](step5/bid_calibration_memo.md) · [bid_calibration.ipynb](step5/bid_calibration.ipynb) |
| 7. Verification | Source checks of the open inputs. Skatterådet's ruling on tax pools was read directly; the DEA's O&M definition, Vattenfall's 2025 impairment discount rates and the AF25 price notes come via a secondary research report and are flagged as such. Two inputs corrected and step 5 re-run. | [verification_notes.md](step7/verification_notes.md) · [headline_check.py](step7/headline_check.py) |

## Data sources

| Source | Used for | Licence / terms | In this repo? |
|---|---|---|---|
| DEA tender documents for North Sea I South (Nordsøen Syd), Nov 2025: Annex F Concession Agreement, Appendix 3 and 3.1, Procurement Specifications; DEA *Step-by-Step Guide* (27 Mar 2026); Energinet draft Bilag 2.3 | Contract terms (step 1) | Tender material, no open licence | **No.** Cited by section number only |
| [DEA press release, 4 Aug 2026](https://via.ritzau.dk/pressemeddelelse/15074199/danmark-far-to-nye-havvindmolleparker?lang=da) | Awarded strikes and bid counts | – | Link only |
| ERA5 (Hersbach et al., C3S) via [Open-Meteo](https://open-meteo.com/) | Hourly wind, 1995 and 2006–2025 | CC BY 4.0 | Recreated by `step2/era5_openmeteo.py` |
| Energinet site wind assessments (C2Wind, North Sea I, rev. 3; EMD, Hesselø South, rev. 3) | Long-term wind level and shape at 150 m | Energinet site data | Values cited only |
| IEA 15 MW reference turbine, from NREL's `turbine-models` repository | Power curve | See the source repository | `step2/data/IEA_Reference_15MW_240.csv` |
| [Energi Data Service](https://www.energidataservice.dk/) (Energinet) | DK1/DK2 day-ahead prices, metered wind | CC BY 4.0 | Recreated by `step3/eds_price_download.py` |
| Skatterådet binding answer SKM2025.37.SR (19 Nov 2024), retsinformation.dk | Tax pools for cables, substations, foundations, Energinet contribution | Public | Cited |
| Vattenfall Annual and Sustainability Report 2025, Note 27 | Discount rates for the wind business (comparison only) | Company report | Values cited |
| [DEA Technology Data, generation of electricity and district heating](https://ens.dk/en/analyses-and-statistics/technology-data-generation-electricity-and-district-heating), workbook v0019, sheet "21 Offshore Wind AC Fixed" | Capex and O&M | CC BY 4.0 | Extracted rows only (`step4/outputs/`, `step4/dea_offshore_ac_2030.yaml`) |
| [DEA Analysis Assumptions for Energinet 2025 (AF25)](https://ens.dk/analyser-og-statistik/analyseforudsaetninger-til-energinet), [price dataset](https://ens.dk/media/7632/download) | 2033–2052 price scenarios | DEA publication | **No.** Download manually (see below) |
| Statistics Denmark PRIS04 (net price index) | Price base and strike indexation | Statistics Denmark terms (attribution) | Index values quoted |
| Energinet tariff catalogue 2026; Afskrivningsloven, Selskabsskatteloven | Connection contribution, producer tariffs (sensitivity), tax | Public | Cited |
| Energinet, *Projektbeskrivelse for Landanlæg, Nordsøen I Midt* (dok. 23/02056-2, Nov 2025); SGAV draft §25 permit (Jan 2026) | NSM landfall, onshore route and who builds it | Public | Cited |
| [DEA Technology Data for Energy Transport](https://ens.dk/en/analyses-and-statistics/technology-data-transport-energy), data sheets v8 (Jul 2025), sheet 1.7; ACER unit investment cost indicators (Jul 2023) | Onshore cable cost and benchmark | CC BY 4.0 / public | Values cited |

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

**Tests** (48 in total; integration tests skip themselves when their data files are missing):

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
├── summary/                       # One-page PDF (LaTeX), figure and LinkedIn carousel scripts
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
├── step4/                         # Cost, tax and discount-rate inputs
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
└── step7/                         # Source verification
    ├── verification_notes.md
    └── headline_check.py          # Prints the headline numbers and the step-7 effects
```

## Limitations and open items

- The contract terms come from the Nordsøen Syd tender documents, used as a proxy because Nordsøen Midt's and Hesselø's own Annex F and Appendix 3 weren't available. The cap amounts come from the DEA guide (Nordsøen Midt) and the EU contract notice (Hesselø).
- The DEA's price outlook uses weather years 1995, 2008 and 2009. Site output for 1995 is rebuilt from ERA5 wind with the step-2 wind-to-output relationship (held-out R² 0.998 and 0.991), not run through the step-2 notebook.
- My site capture factors (0.84–0.90 within each month, 0.89–0.99 annually) are well above the DEA's published fleet ratios (0.57 / 0.95 / 0.76 for DK1 in 2030 / 2040 / 2050), and the DEA doesn't document how it builds them. I treat the DEA ratio (S1-B′) as a co-equal case: it lifts Hesselø's break-even to DKK 610/MWh and leaves Nordsøen Midt with none. The weather-year check (only the matching ERA5 year correlates negatively with AF25 prices) confirms the year alignment, not the hourly alignment.
- Tax pools follow one binding ruling (SKM2025.37.SR), which puts cables and transformer stations at 7 % without naming each asset. Applying it to array cables, export cable and offshore substation is my reading.
- Capex is adjusted to each site by interpolating between DEA datasheets, not with the formulas in the DEA's chapter text. Nordsøen Midt's onshore cable is costed at DEA unit rates without the DEA's possible extras for permits and landowners (up to +50 %) or its O&M, and the 275/400 kV coupling station at Hjortkær isn't costed. Hesselø carries no onshore cable, although older planning documents had its winner building one. Hesselø has no premium for nature-inclusive design, and its grid-connection charge depends on an area classification I couldn't confirm (DKK 157–532m). Insurance is taken as part of DEA fixed O&M, per the DEA's general guideline.
- Vattenfall's disclosed discount rate covers its whole wind business, on- and offshore, and doesn't say nominal or real. I read it as nominal.
- Overplanting isn't in the base case. The DEA's outlook assumes it at both sites, so it is another possible lever behind the bids.
- Still open after the Nov 2026 review: whether the net cap counts past payments in real or nominal terms (Appendix 3 §2.5, not in the repo); Hesselø's onshore scope; and Nordsøen Syd's start date, which sets when its wake begins (assumed 2035).
- This is an outside-in reconstruction from public information. It isn't affiliated with Vattenfall, the DEA or Energinet and doesn't claim to match Vattenfall's own inputs.

## About

Fergal Israel. I'm an MSc Wind Energy student at DTU (2026–2028) with a BEng in Mechanical Engineering from Swansea, interested in the commercial side of offshore wind. This is an independent project, not part of my coursework.

Code is released under the [MIT licence](LICENSE). Data and values from third parties keep their own licences, listed above.
