# Step 5 — DCF and bid calibration

Cash-flow model for Nordsøen Midt (DK1, 1,005 MW, strike DKK 504/MWh) and Hesselø (DK2, 795 MW, strike DKK 542/MWh). It answers two questions: which capex / WACC / yield combinations give NPV = 0 at the awarded strikes, and what strike the base case implies.

| File | What it is |
|---|---|
| `dcf_model.py` | The model: input loaders, AF25 method-B price scenarios, monthly CfD settlement with net cap and payment lag, tax pools, two-rate discounting, solvers |
| `bid_calibration.ipynb` | Runs every analysis and writes `outputs/` |
| `bid_calibration_memo.md` | Two-page memo with the headline findings |
| `reconstruct_aap_1995.py` | Rebuilds hourly 1995 AAP from ERA5 wind by learning step 2's wind → AAP mapping (holdout R² 0.998 / 0.991). Writes `step5/data/aap_hourly_1995_<SITE>.csv`, which is used only for AF25 price pairing |
| `tests/test_dcf_model.py` | 27 pytest tests. The synthetic ones run without data; the integration ones are skipped if the data files are missing |
| `outputs/` | Result CSVs and PNG charts (small, committed) |

## Inputs (paths are relative to the repo root)
- `step4/cost_inputs.yaml` (committed)
- `step2/data/aap_hourly_<SITE>.csv` (git-ignored; recreated by `step2/yield_model.ipynb`)
- `step2/data/era5_<SITE>_2006_2025.csv` and `era5_<SITE>_1995_1995.csv` (git-ignored; from `era5_openmeteo.py --extra-years 1995`). These are only needed to run `reconstruct_aap_1995.py`. Without its output, method B falls back to the 2008 and 2009 climate years, with weights renormalised.
- `step2/outputs/yield_annual_summary.csv` (committed)
- `step3/data/outputs/reference_price_monthly_era5.csv` (git-ignored; recreated by `step3/price_analysis.ipynb`)
- `step5/data/AF25 - datasæt - elprisfremskrivning.xlsx` (git-ignored; download from https://ens.dk/media/7632/download)

## Run (PowerShell, from the repo root, venv active)
```powershell
python step5/reconstruct_aap_1995.py
python -m pytest step5/tests -q
cd step5
jupyter nbconvert --to notebook --execute --inplace bid_calibration.ipynb
```
A full run takes about 2–3 minutes. Most of that time goes on the break-even solvers.

## .gitignore additions
```
step5/data/
```
