# Project 1 · Step 2 – Yield model

Hourly potential output for **Nordsøen Midt** (DK1) and **Hesselø** (DK2): the proxy for the CfD settlement volume (Available Active Power) and for metered market sales.

## Files
| File | What it is |
|---|---|
| `era5_download.py` | Downloads hourly ERA5 (100 m and 10 m wind, 2 m temperature, surface pressure) from the Copernicus CDS and writes one CSV per site |
| `yield_model.ipynb` | Hub-height extrapolation, calibration to Energinet's LiDAR-based wind level, IEA 15 MW power curve, first-pass loss stack, DEA check, outputs |
| `data/IEA_Reference_15MW_240.csv` | IEA 15 MW reference turbine power/thrust curve, from NREL's `turbine-models` repository (`turbine_models/data/Offshore/`) |

## Run order
1. One-off CDS setup – see the docstring at the top of `era5_download.py` (account, licence acceptance, `~/.cdsapirc`).
2. `pip install "cdsapi>=0.7.4" xarray netCDF4 pandas numpy matplotlib jupyter`
3. `python era5_download.py` → `data/era5_NSM_2006_2025.csv`, `data/era5_HES_2006_2025.csv`
4. Open `yield_model.ipynb` and run all cells → `outputs/`

## Key sources
- Energinet / C2Wind, *Lot 3 (North Sea I) Wind Assessment – Supplementary Note*, rev. 3, Nov 2024 (shear 0.07; point A2 P2 long-term mean 10.44 m/s at 150 m).
- Energinet / EMD, *Hesselø South Site Wind Conditions Assessment*, rev. 3, Dec 2025 (shear 0.09; long-term means 9.58–9.67 m/s at 150 m; site coordinates).
- DTU Wind report E-0255 (2025) for the DEA, *Environmental Mapping and Screening of the Offshore Wind Potential in Denmark – Wind*: domain wake losses 6.6–12 % (current fleet), 12–21 % (2030 scenario).
- DEA Step-by-Step Guide (Mar 2026) Table 1.5: interim estimate 4,479 GWh/yr for 1 GW at Nordsøen Midt.
