# Project 1 · Step 2 – Yield model

Hourly potential output for **Nordsøen Midt** (DK1) and **Hesselø** (DK2): the proxy for the CfD settlement volume (Available Active Power) and for metered market sales.

## Files
| File | What it is |
|---|---|
| `era5_openmeteo.py` | **Used.** Downloads ECMWF ERA5 (nearest grid cell) from the Open-Meteo archive API – no queue, ~5 minutes for 2006–2025 + 1995. `--validate` compares with any CDS months on disk |
| `era5_download.py` | Fallback: same variables from the Copernicus CDS with 4-cell interpolation (needs `--chunk month`; the CDS queue made this impractically slow in Oct 2026) |
| `yield_model.ipynb` | Hub-height extrapolation, quantile-mapping calibration to Energinet's LiDAR-based Weibull, IEA 15 MW power curve, first-pass loss stack, DEA check; exports `data/aap_hourly_<SITE>.csv` for step 3 and summaries to `outputs/` |
| `data/IEA_Reference_15MW_240.csv` | IEA 15 MW reference turbine power/thrust curve, from NREL's `turbine-models` repository (`turbine_models/data/Offshore/`) |

## Run order
1. `pip install "cdsapi>=0.7.4" xarray netCDF4 pandas numpy scipy matplotlib jupyter requests` (Python 3.13)
2. `python era5_openmeteo.py --extra-years 1995` → `data/era5_NSM_2006_2025.csv`, `data/era5_HES_2006_2025.csv`, plus 1995 files
3. Optional check: `python era5_openmeteo.py --validate`
4. Open `yield_model.ipynb` and run all cells → `data/aap_hourly_*.csv`, `outputs/`

## Data credits
- ERA5: Hersbach et al. (2023), *ERA5 hourly data on single levels from 1940 to present*, Copernicus Climate Change Service (C3S) Climate Data Store, accessed via Open-Meteo.com (Zippenfenig, 2023), CC BY 4.0.

## Key sources
- Energinet / C2Wind, *Lot 3 (North Sea I) Wind Assessment – Supplementary Note*, rev. 3, Nov 2024 (shear 0.07; point A2 P2 long-term mean 10.44 m/s at 150 m).
- Energinet / EMD, *Hesselø South Site Wind Conditions Assessment*, rev. 3, Dec 2025 (shear 0.09; long-term means 9.58–9.67 m/s at 150 m; site coordinates).
- DTU Wind report E-0255 (2025) for the DEA, *Environmental Mapping and Screening of the Offshore Wind Potential in Denmark – Wind*: domain wake losses 6.6–12 % (current fleet), 12–21 % (2030 scenario).
- DEA Step-by-Step Guide (Mar 2026) Table 1.5: interim estimate 4,479 GWh/yr for 1 GW at Nordsøen Midt.
