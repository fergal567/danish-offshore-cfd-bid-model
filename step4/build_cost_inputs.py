"""Step 4 – build the cost and financing inputs for the step-5 cash-flow model.

Reads  step4/dea_offshore_ac_2030.yaml  (DEA datasheet values, 2020 EUR)
Writes step4/cost_inputs.yaml           (all inputs, real 2026 DKK, low/base/high)
       step4/outputs/cost_table.md      (summary table pasted into cost_assumptions.md)

Price base of every output: real DKK, 2026 prices, deflated with the Danish Net Price
Index (NPI) at May 2026 – the same base as the CfD strike (indexation base NPI May 2026,
contract row A3). Run from the repo root:  python step4/build_cost_inputs.py
"""
from __future__ import annotations

from pathlib import Path

import yaml

HERE = Path(__file__).parent

# ---------------------------------------------------------------------------
# 1. Price base
# ---------------------------------------------------------------------------
EUR_DKK = 7.46  # project convention (Danish central rate 7.46038)

# Statistics Denmark, StatBank PRIS04, "00 Nettoprisindeks i alt", Indeks (2025=100).
# Retrieved 21 Oct 2026 via api.statbank.dk/v1/data/PRIS04 (VAREGR=000005, ENHED=100).
NPI = {
    "2020M01": 85.29, "2020M02": 85.87, "2020M03": 85.58, "2020M04": 85.53,
    "2020M05": 85.38, "2020M06": 85.48, "2020M07": 86.10, "2020M08": 85.58,
    "2020M09": 85.39, "2020M10": 85.62, "2020M11": 85.31, "2020M12": 85.13,
    "2021M09": 87.10, "2022M09": 95.88, "2023M09": 97.13, "2024M09": 98.13,
    "2025M05": 99.43, "2025M09": 100.42,
    "2026M01": 100.27, "2026M02": 101.36, "2026M03": 101.25, "2026M04": 101.49,
    "2026M05": 102.13, "2026M06": 102.38, "2026M07": 103.96, "2026M08": 103.50,
}
NPI_2020_AVG = sum(v for k, v in NPI.items() if k.startswith("2020")) / 12
NPI_BASE = NPI["2026M05"]                      # strike indexation base (contract A3)
F_NPI = NPI_BASE / NPI_2020_AVG                # 2020 avg -> May 2026

# Cross-check only: euro-area HICP (Eurostat, 2025=100), via FRED series CP00MI15EA20M086NEST
HICP_EA_2020_AVG = (81.05 + 81.19 + 81.63 + 81.87 + 81.79 + 82.07
                    + 81.78 + 81.44 + 81.51 + 81.66 + 81.38 + 81.65) / 12
HICP_EA_2026M05 = 103.11
F_HICP = HICP_EA_2026M05 / HICP_EA_2020_AVG

DKK26_PER_EUR20 = EUR_DKK * F_NPI              # 1 EUR(2020) -> DKK(2026, NPI)
DKK26_PER_EUR26 = EUR_DKK                      # for inputs already in 2026 EUR

# ---------------------------------------------------------------------------
# 2. Sites (from step 2 decisions / contract rows F6, B5)
# ---------------------------------------------------------------------------
SITES = {
    "NSM": {"name": "Nordsøen Midt", "mw": 1005, "dist_km": 20, "depth_m": [25, 35], "zone": "DK1"},
    "HES": {"name": "Hesselø", "mw": 795, "dist_km": 33, "depth_m": [18, 30], "zone": "DK2"},
}
COD = "2033-01-01"  # contract D4 (assumption)


def lbh(low, base, high):
    return {"low": low, "base": base, "high": high}


def scale(d: dict, f: float, nd: int = 3) -> dict:
    return {k: (None if v is None else round(v * f, nd)) for k, v in d.items()}


# ---------------------------------------------------------------------------
# 3. DEA base capex per site
# ---------------------------------------------------------------------------
dea = yaml.safe_load((HERE / "dea_offshore_ac_2030.yaml").read_text(encoding="utf-8"))
DEA_STATUS = dea["status"]
AC = dea["ac_fixed"]
SI = dea["site_interpolation"]
COMPONENTS = ["project_development", "turbines", "foundation", "array_cables", "substation", "export_cables"]
BAND_2030 = 0.15   # note F: ±10 % (2025) -> ±35 % (2050); linear in time gives ±15 % for 2030 (Asm)


def interp(x: float, pts: list[tuple[float, float]]) -> float:
    """Piecewise-linear interpolation; linear extrapolation beyond the end points."""
    pts = sorted(pts)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x <= x1 or (x1, y1) == pts[-1]:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    raise ValueError


def site_components(site: str, year: str) -> dict:
    """DEA component costs (M EUR2020/MW) moved from the 60 km / 30 m DEA site to our site."""
    s = SITES[site]
    comp = {k: AC[year][k] for k in COMPONENTS}
    comp["export_cables"] = interp(s["dist_km"], [(p["distance_km"], p["value"])
                                                  for p in SI["export_cables_vs_distance"]])
    depth = sum(s["depth_m"]) / 2
    comp["foundation"] = interp(depth, [(p["depth_m"], p["value"])
                                        for p in SI[f"foundation_vs_depth_{year}"]])
    comp["total"] = sum(comp[k] for k in COMPONENTS)
    return comp


SITE_DEA = {s: {"2030": site_components(s, "2030"), "2025": site_components(s, "2025")} for s in SITES}


def dea_capex_meur20(site: str) -> dict:
    """Low = 2030 column −15 %; base = 2030 column; high = 2025 column (15 MW units). All site-adjusted."""
    b = SITE_DEA[site]["2030"]["total"]
    return lbh(b * (1 - BAND_2030), b, max(SITE_DEA[site]["2025"]["total"], b * (1 + BAND_2030)))


# ---------------------------------------------------------------------------
# 4. Capex build-up (DKK m 2026)
# ---------------------------------------------------------------------------
CONTINGENCY = lbh(0.05, 0.075, 0.10)   # share of DEA base; DEA excludes contingency (Asm)
OWNER_DEVEX_MDKK = lbh(50, 100, 200)   # bid/tender, owner's team, own surveys not in DEA (Asm)

# Energinet connection contribution, 2026 tariffs (Energinet tarifkatalog 2026 p. 9;
# NSS structure in Bilag 2.3): 400 kV bay 18.3m each + per-MW contribution.
BAY_400KV = 18.3
RATE_SURPLUS = 0.623     # DKK m/MW, production-surplus areas
RATE_CONSUMPTION = 0.175 # DKK m/MW, consumption-dominated areas
CONNECTION_MDKK = {
    # NSM: West Jutland assumed production-surplus (as Endrup for NSS); ±10 % tariff revision
    "NSM": {k: round(v, 1) for k, v in lbh(0.9 * (2 * BAY_400KV + 1005 * RATE_SURPLUS),
                                          2 * BAY_400KV + 1005 * RATE_SURPLUS,
                                          1.1 * (2 * BAY_400KV + 1005 * RATE_SURPLUS)).items()},
    # Hesselø: North Zealand assumed consumption-dominated (base); high = production-surplus rate
    "HES": {k: round(v, 1) for k, v in lbh(1 * BAY_400KV + 795 * RATE_CONSUMPTION,
                                          2 * BAY_400KV + 795 * RATE_CONSUMPTION,
                                          2 * BAY_400KV + 795 * RATE_SURPLUS).items()},
}

capex = {}
for s, sd in SITES.items():
    mw = sd["mw"]
    d = dea_capex_meur20(s)
    dea_dkk_mw = {k: v * DKK26_PER_EUR20 for k, v in d.items()}          # DKK m/MW
    cont = {k: dea_dkk_mw[k] * CONTINGENCY[k] for k in d}
    dev = {k: OWNER_DEVEX_MDKK[k] / mw for k in d}
    grid = {k: CONNECTION_MDKK[s][k] / mw for k in d}
    total_excl_grid = {k: dea_dkk_mw[k] + cont[k] + dev[k] for k in d}
    total = {k: total_excl_grid[k] + grid[k] for k in d}
    capex[s] = {
        "dea_components_meur2020_per_mw": {k: round(v, 4) for k, v in SITE_DEA[s]["2030"].items()},
        "dea_components_2025col_meur2020_per_mw": {k: round(v, 4) for k, v in SITE_DEA[s]["2025"].items()},
        "dea_unadjusted_2030_meur2020_per_mw": round(AC["2030"]["nominal_investment_total"], 4),
        "dea_base_meur2020_per_mw": scale(d, 1, 4),
        "dea_base_mdkk_per_mw": scale(dea_dkk_mw, 1),
        "contingency_mdkk_per_mw": scale(cont, 1),
        "owner_devex_mdkk_per_mw": scale(dev, 1),
        "energinet_connection_mdkk_total": CONNECTION_MDKK[s],
        "energinet_connection_mdkk_per_mw": scale(grid, 1),
        "capex_excl_energinet_mdkk_per_mw": scale(total_excl_grid, 1),
        "capex_excl_energinet_meur2026_per_mw": scale(total_excl_grid, 1 / DKK26_PER_EUR26),
        "capex_all_in_mdkk_per_mw": scale(total, 1),
        "capex_all_in_mdkk_total": scale(total, mw, 0),
    }

# Phasing (share of each component by calendar year; IDC is added in step 5)
PHASING = {
    "dea_development_share": {s: round(SITE_DEA[s]["2030"]["project_development"] / SITE_DEA[s]["2030"]["total"], 4)
                              for s in SITES},
    "profiles": {
        "base":  {"fid": "mid-2029", "development": {2027: 1/3, 2028: 1/3, 2029: 1/3},
                  "construction": {2029: 0.15, 2030: 0.35, 2031: 0.35, 2032: 0.15}},
        "early": {"fid": "2028", "development": {2026: 1/3, 2027: 1/3, 2028: 1/3},
                  "construction": {2028: 0.10, 2029: 0.25, 2030: 0.30, 2031: 0.25, 2032: 0.10}},
        "late":  {"fid": "2030", "development": {2028: 1/3, 2029: 1/3, 2030: 1/3},
                  "construction": {2030: 0.20, 2031: 0.45, 2032: 0.35}},
    },
    "owner_devex": {2026: 0.20, 2027: 0.30, 2028: 0.30, 2029: 0.20},
    "energinet_connection": {2029: 1.0},
    "contingency": "follows construction profile",
    "note": "development = DEA development share; construction = rest of DEA base + contingency",
}
for p in PHASING["profiles"].values():
    for k in ("development", "construction"):
        p[k] = {y: round(v, 4) for y, v in p[k].items()}
PHASING["owner_devex"] = {y: round(v, 4) for y, v in PHASING["owner_devex"].items()}

# ---------------------------------------------------------------------------
# 5. Opex and other costs (real 2026 DKK)
# ---------------------------------------------------------------------------
# Low = 2030 column −15 %; base = 2030 column; high = 2025 column (15 MW units: 44k / 4.41)
fom_c = AC["2030"]["fixed_om_eur_per_mw_yr"]
vom_c = AC["2030"]["variable_om_eur_per_mwh"]
fom = lbh(fom_c * (1 - BAND_2030), fom_c, AC["2025"]["fixed_om_eur_per_mw_yr"])
vom = lbh(vom_c * (1 - BAND_2030), vom_c, AC["2025"]["variable_om_eur_per_mwh"])
# DEA Technology Data guideline, 'O&M costs' (pp. 27–28): fixed O&M already includes insurance
# (and network/system charges). Base 0 to avoid double counting; high = the old EUR 10k/MW/yr base,
# in case chapter 21 differs from the guideline (step 7, V6; Ext guideline, Asm high case).
INSURANCE_EUR26 = lbh(0, 0, 10000)          # EUR 2026 /MW/yr, operational insurance on top of DEA O&M

opex = {
    "fixed_om_dkk_k_per_mw_yr": scale(fom, DKK26_PER_EUR20 / 1000, 1),
    "insurance_dkk_k_per_mw_yr": scale(INSURANCE_EUR26, DKK26_PER_EUR26 / 1000, 1),
    "variable_om_dkk_per_mwh": scale(vom, DKK26_PER_EUR20, 2),
    "energinet_tariffs_dkk_per_mwh": lbh(8.0, 9.2, 12.0),   # 2027: 0.50 + 0.42 øre/kWh (contract G6)
    "balancing_dkk_per_mwh": lbh(8.0, 15.0, 25.0),          # contract B14 (Asm)
    "capability_compliance_mdkk_per_yr": lbh(1.5, 3.0, 5.0),  # contract I5 (Asm)
    "aap_commissioning_oneoff_mdkk": lbh(2.0, 5.0, 10.0),     # App 3 §5, COD year (Asm)
    "seabed_fee": lbh(0, 0, 0),                              # contract H3
}

# Decommissioning and guarantees
decom = {
    "cost_share_of_dea_base": lbh(0.10, 0.12, 0.15),
    "cost_mdkk_per_mw": {s: scale(capex[s]["dea_base_mdkk_per_mw"], 1, 2) for s in SITES},
    "timing": "year after end of economic life (base 2063)",
    "security_posted_from": "15 years after first power (assume 2047)",
    "security_fee_pct_per_yr": lbh(0.0, 0.5, 1.0),
}
for s in SITES:
    decom["cost_mdkk_per_mw"][s] = {
        k: round(capex[s]["dea_base_mdkk_per_mw"][k] * decom["cost_share_of_dea_base"]["base"], 2)
        for k in ("low", "base", "high")}
    # use the matching share in each case
    for k in ("low", "high"):
        decom["cost_mdkk_per_mw"][s][k] = round(
            capex[s]["dea_base_mdkk_per_mw"][k] * decom["cost_share_of_dea_base"][k], 2)

guarantees = {
    "performance_guarantee_mdkk": 308.8,        # Annex F 17.2 (NSS), contract E5
    "performance_guarantee_fee_pct_per_yr": lbh(0.5, 1.0, 1.5),   # contract E7 (Asm)
    "performance_guarantee_period": "signing (assume 2027) to MinCap COD (end-2032)",
    "parent_company_guarantee_mdkk": 463.2,     # Annex F 17.3, contract E6; no cash cost
}

# ---------------------------------------------------------------------------
# 6. Tax and cost of capital
# ---------------------------------------------------------------------------
tax = {
    "corporate_tax_rate": 0.22,
    "pools": {
        "plant_15pct_db": {"rate": 0.15, "method": "declining balance",
                           "assets": "turbines, foundations (incl. transport and installation), "
                                     "development, contingency",
                           "law": "Afskrivningsloven §5C stk. 1 nr. 4 (el-production plant >1 MW; "
                                  "wind turbines acquired from 2013), stk. 4"},
        "infrastructure_7pct": {"rate": lbh(0.15, 0.07, 0.07), "method": "declining balance",
                                "assets": "array cables, export cable, offshore substation",
                                "law": "§5C stk. 2 nr. 1 (infrastructure for transport of electricity); "
                                       "Skatterådet SKM2025.37.SR (19 Nov 2024), Q5: 'forskellige typer kabler og "
                                       "transformatorstationer mv.' up to 7 % (step 7, V1). Low case 15 % = "
                                       "treated as production plant"},
        "export_cable": {"rate": lbh(0.15, 0.07, 0.07), "method": "declining balance",
                         "law": "superseded by infrastructure_7pct; kept for the old-scope sensitivity "
                                "(export cable only at 7 %)"},
        "energinet_contribution": {"rate": 0.20, "method": "straight line",
                                   "law": "§43 (tilslutningsafgifter), from when the fee is due"},
    },
    "export_cable_share_of_dea_base": {s: round(SITE_DEA[s]["2030"]["export_cables"] / SITE_DEA[s]["2030"]["total"], 4)
                                       for s in SITES},
    # 7 % pool per SKM2025.37.SR: array cables + export cable + offshore substation (step 7, V1)
    "infra_7pct_share_of_dea_base": {s: round(sum(SITE_DEA[s]["2030"][k] for k in
                                                  ("array_cables", "substation", "export_cables"))
                                              / SITE_DEA[s]["2030"]["total"], 4) for s in SITES},
    "depreciation_start": "COD year (2033) for plant/cable; payment year for §43 contribution",
    "losses": {"base": "used immediately via Danish joint taxation (sambeskatning)",
               "sensitivity": "standalone: SEL §12 – full offset up to DKK 20.829m (2025), "
                              "60 % of income above; no expiry"},
    "real_model_note": "tax depreciation is on nominal historical cost; deflate shields with "
                       "the NPI path (2 %/yr) in the real model",
    "vat": "CfD payments both ways outside VAT scope (SKM2026.175.SR)",
}

wacc = {
    "basis": "real, post-tax, unlevered; apply to real NPI-indexed cash flows",
    "cfd_period": lbh(0.040, 0.050, 0.065),
    "merchant_tail": lbh(0.060, 0.070, 0.085),
    "inflation_for_nominal_conversion": 0.02,
}

life = {"economic_life_yr": lbh(25, 30, 35), "cod": COD,
        "technical_lifetime_dea_yr": lbh(25, AC["2030"]["technical_lifetime_yr"], 40),
        "construction_time_dea_yr": lbh(3, AC["2030"]["construction_time_yr"], 4)}

out = {
    "meta": {
        "step": "Project 1 step 4 – cost & financing inputs",
        "price_base": "real DKK, 2026 prices (NPI May 2026 = 102.13, 2025=100)",
        "eur_dkk": EUR_DKK,
        "npi_2020_avg": round(NPI_2020_AVG, 3),
        "npi_base_2026M05": NPI_BASE,
        "factor_2020_to_2026_npi": round(F_NPI, 4),
        "factor_2020_to_2026_hicp_ea_crosscheck": round(F_HICP, 4),
        "dkk2026_per_eur2020": round(DKK26_PER_EUR20, 4),
        "dea_status": DEA_STATUS,
        "npi_series_PRIS04": NPI,
    },
    "sites": SITES,
    "capex": capex,
    "capex_phasing": PHASING,
    "opex": opex,
    "decommissioning": decom,
    "guarantees": guarantees,
    "tax": tax,
    "wacc": wacc,
    "life": life,
}

(HERE / "cost_inputs.yaml").write_text(
    "# GENERATED by step4/build_cost_inputs.py – edit inputs there, not here.\n"
    + yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=110),
    encoding="utf-8")


# ---------------------------------------------------------------------------
# 7. Summary table for the memo
# ---------------------------------------------------------------------------
def fmt(d, nd=1):
    return " / ".join(f"{d[k]:,.{nd}f}" for k in ("low", "base", "high"))


rows = []
for s in SITES:
    cp = capex[s]
    rows += [
        (f"{s} DEA base capex", fmt(cp["dea_base_meur2020_per_mw"], 3), "M€2020/MW"),
        (f"{s} DEA base capex", fmt(cp["dea_base_mdkk_per_mw"], 2), "DKK m/MW"),
        (f"{s} capex excl. Energinet", fmt(cp["capex_excl_energinet_mdkk_per_mw"], 2), "DKK m/MW"),
        (f"{s} capex excl. Energinet", fmt(cp["capex_excl_energinet_meur2026_per_mw"], 2), "M€2026/MW"),
        (f"{s} Energinet contribution", fmt(cp["energinet_connection_mdkk_total"], 1), "DKK m"),
        (f"{s} capex all-in", fmt(cp["capex_all_in_mdkk_per_mw"], 2), "DKK m/MW"),
        (f"{s} capex all-in", fmt(cp["capex_all_in_mdkk_total"], 0), "DKK m"),
    ]
rows += [
    ("Fixed O&M", fmt(opex["fixed_om_dkk_k_per_mw_yr"]), "DKK k/MW/yr"),
    ("Insurance", fmt(opex["insurance_dkk_k_per_mw_yr"]), "DKK k/MW/yr"),
    ("Variable O&M", fmt(opex["variable_om_dkk_per_mwh"], 2), "DKK/MWh"),
]
(HERE / "outputs").mkdir(exist_ok=True)
tbl = "| Item | Low / Base / High | Unit |\n|---|---|---|\n" + "\n".join(
    f"| {a} | {b} | {u} |" for a, b, u in rows)
(HERE / "outputs" / "cost_table.md").write_text(tbl + "\n", encoding="utf-8")

print(f"DEA status: {DEA_STATUS}")
print(f"NPI 2020 avg {NPI_2020_AVG:.3f} -> May 2026 {NPI_BASE}: x{F_NPI:.4f} "
      f"(HICP-EA cross-check x{F_HICP:.4f}); 1 EUR2020 = {DKK26_PER_EUR20:.3f} DKK2026")
print(tbl)
