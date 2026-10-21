# Step 4 – Cost and financing inputs

Builds the capex, opex, decommissioning, guarantee, tax and WACC inputs for Nordsøen Midt (NSM) and Hesselø.
Everything is in **real 2026 DKK**, deflated with the Danish Net Price Index at May 2026 (the CfD strike's indexation base).

| File | What it is |
|---|---|
| `cost_assumptions.md` | Memo: DEA values, site adjustment, price base, full input table (low/base/high, source, status), tax and WACC notes |
| `cost_inputs.yaml` | **Generated** input file read by step 5 – do not edit by hand |
| `build_cost_inputs.py` | Holds every input and its source; writes `cost_inputs.yaml` and `outputs/cost_table.md` |
| `dea_offshore_ac_2030.yaml` | DEA Technology Data values (2025 and 2030 columns + interpolation points), transcribed from the workbook |
| `dea_extract.py` | Reads any datasheet from the DEA workbook into `outputs/dea_<sheet>_<year>.csv` |
| `outputs/` | `cost_table.md` (summary table) and DEA sheet extracts |
| `tests/` | Sanity checks on the generated inputs |
| `data/` | DEA workbook (git-ignored) |

## Data

DEA *Technology Data for power and heat production plants*, workbook version 0019 (Aug 2026), sheet
"21 Offshore Wind AC Fixed", from https://ens.dk/node/3449 (CC BY 4.0). Save it as
`step4/data/technology_data_for_el_and_dh_-_0019.xlsx`.

## Run (from the repo root, venv active)

```powershell
python step4\dea_extract.py "step4\data\technology_data_for_el_and_dh_-_0019.xlsx" --sheet "21 Offshore Wind AC Fixed" --year 2030
python step4\build_cost_inputs.py
python -m pytest step4\tests -q
```

Requires `pyyaml`, `openpyxl`, `pytest`.
