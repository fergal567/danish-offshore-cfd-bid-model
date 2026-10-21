"""Project 1 · Step 5 — DCF and bid calibration for Nordsøen Midt (NSM) and Hesselø (HES).

Real 2026 DKK (NPI May 2026 = 102.13, the strike's own indexation base). Annual cash
flows, with the CfD settled month by month so that the net cap on state payments (B9)
and the one-month payment lag (B7) are modelled explicitly.

Status tags used in comments and docstrings (as in contract_assumptions.md):
    Doc = tender documents in the project files · Ext = named outside source ·
    Asm = my modelling assumption (change freely).

Main entry points
-----------------
load_inputs()            -> Inputs (cost YAML, hourly AAP, AF25 prices, step-3 history)
build_price_scenarios()  -> {name: PriceScenario}  (S1, S2_low, S2_high, S3, S4, S5)
make_params()            -> Params for one site and one set of sensitivity cases
run_model()              -> Result (annual cash flows, NPV, net-cap path, IDC, ...)
breakeven_strike()       -> strike giving NPV = 0
solve_wacc()             -> CfD-period WACC giving NPV = 0 at a given strike
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import brentq

REPO = Path(__file__).resolve().parents[1]

# --------------------------------------------------------------------------------------
# Constants (each tagged)
# --------------------------------------------------------------------------------------
SITES = {
    # zone: B5 (Asm, verify) · mw: F6 (Doc) · strike: A2 (Ext) · cap: B9 (Doc/Ext, 2025 prices)
    "NSM": dict(name="Nordsøen Midt", zone="DK1", mw=1005.0, strike=504.0, net_cap_2025_mdkk=15_700.0),
    "HES": dict(name="Hesselø", zone="DK2", mw=795.0, strike=542.0, net_cap_2025_mdkk=21_900.0),
}
NPI_MAY2026 = 102.13      # Ext: DST PRIS04 — strike indexation base (A3)
NPI_MAY2025 = 99.43       # Ext: DST PRIS04 — proxy for the cap's "1 Jun 2025" base (Asm: May index)
NPI_2025_AVG = 100.0      # Ext: PRIS04 is 2025 = 100; AF25 "2025-niveau" read as the 2025 average (Asm)
AF25_TO_2026 = NPI_MAY2026 / NPI_2025_AVG          # 1.0213
CAP_TO_2026 = NPI_MAY2026 / NPI_MAY2025            # 1.0272
VALUATION_DATE = 2026 + 140 / 365                  # bid deadline 20 May 2026 (Proc Spec) — NPV date (Asm)
PRICE_BASE_DATE = 2026 + 4.5 / 12                  # mid-May 2026: real/nominal crossover (Asm)
CLIMATE_WEIGHTS = {1995: 0.25, 2008: 0.35, 2009: 0.40}   # Asm (inferred in step 3, method §2)
AF25_SIM_YEARS = (2030, 2040, 2050)                       # Ext: AF25 dataset
BASE_INTERNAL_WAKE = 0.10      # step 2 base loss (Asm)
BASE_AVAILABILITY = 0.96       # step 2: 3 % unscheduled + 1 % scheduled (Asm)
SCHEDULED_DOWNTIME = 0.01      # counts in AAP (B2, Doc); unscheduled does not
P90_LONG_TERM_SIGMA = 0.06     # Asm: wind resource + model + wake + power-curve uncertainty, 1σ
Z90 = 1.2816


# --------------------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------------------
@dataclass
class Paths:
    cost_yaml: Path = REPO / "step4" / "cost_inputs.yaml"
    aap_dir: Path = REPO / "step2" / "data"                    # aap_hourly_<SITE>.csv (git-ignored)
    yield_summary: Path = REPO / "step2" / "outputs" / "yield_annual_summary.csv"
    hist_monthly: Path = REPO / "step3" / "data" / "outputs" / "reference_price_monthly_era5.csv"
    af25_xlsx: Path = REPO / "step5" / "data" / "AF25 - datasæt - elprisfremskrivning.xlsx"
    aap_1995_dir: Path = REPO / "step5" / "data"               # aap_hourly_1995_<SITE>.csv (reconstruct_aap_1995.py)


@dataclass
class Inputs:
    cost: dict
    aap: dict            # site -> hourly DataFrame (index time_utc; aap_mwh, metered_mwh)
    af25_hourly: pd.DataFrame
    af25_annual: dict
    hist_monthly: pd.DataFrame
    yield_summary: pd.DataFrame
    aap_1995: dict = field(default_factory=dict)   # site -> hourly 1995 AAP (method B only, not P50 yield)

    def aap_for_pairing(self, site: str) -> pd.DataFrame:
        """2006–2025 AAP plus reconstructed 1995 if available (for AF25 climate-year pairing)."""
        if site in self.aap_1995:
            return pd.concat([self.aap_1995[site], self.aap[site]]).sort_index()
        return self.aap[site]


def load_cost_inputs(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_aap_hourly(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["time_utc"]).set_index("time_utc").sort_index()
    return df[["aap_mwh", "metered_mwh"]]


@lru_cache(maxsize=2)
def _read_af25(path_str: str):
    path = Path(path_str)
    hourly = pd.read_excel(path, sheet_name="Timepriser", header=None, skiprows=8, usecols="B:I")
    hourly.columns = ["sim", "t", "DK1_1995", "DK2_1995", "DK1_2008", "DK2_2008", "DK1_2009", "DK2_2009"]
    hourly = hourly.dropna(subset=["sim"]).astype({"sim": int})
    raw = pd.read_excel(path, sheet_name="Elpriser", header=None, usecols="B:E")
    annual, block = {}, None
    for _, row in raw.iterrows():
        label = row.iloc[0]
        if isinstance(label, str) and label.startswith("Relative priser"):
            break                                  # ratio block below repeats the labels
        if isinstance(label, str) and row.iloc[1:].isna().all():
            block = label.strip()
        elif isinstance(label, str) and ("DK1" in label or "DK2" in label) and block:
            zone = "DK1" if "DK1" in label else "DK2"
            annual.setdefault(block, {})[zone] = [float(v) for v in row.iloc[1:4]]
    return hourly, annual


def load_af25(path: Path):
    """AF25 hourly (sheet Timepriser) and annual (sheet Elpriser) prices, 2025 DKK (Ext)."""
    hourly, annual = _read_af25(str(path))
    return hourly.copy(), {k: dict(v) for k, v in annual.items()}


def load_inputs(paths: Paths | None = None) -> Inputs:
    paths = paths or Paths()
    hourly, annual = load_af25(paths.af25_xlsx)
    return Inputs(
        cost=load_cost_inputs(paths.cost_yaml),
        aap={s: load_aap_hourly(paths.aap_dir / f"aap_hourly_{s}.csv") for s in SITES},
        af25_hourly=hourly,
        af25_annual=annual,
        hist_monthly=pd.read_csv(paths.hist_monthly),
        yield_summary=pd.read_csv(paths.yield_summary),
        aap_1995={s: load_aap_hourly(paths.aap_1995_dir / f"aap_hourly_1995_{s}.csv") for s in SITES
                  if (paths.aap_1995_dir / f"aap_hourly_1995_{s}.csv").exists()},
    )


# --------------------------------------------------------------------------------------
# Yield
# --------------------------------------------------------------------------------------
def monthly_profile(aap: pd.DataFrame) -> pd.DataFrame:
    """P50 monthly AAP and metered volume (MWh): mean over all full calendar years in the file."""
    g = aap.groupby([aap.index.year, aap.index.month]).sum()
    g.index.names = ["year", "month"]
    counts = g.groupby(level="year").size()
    full = counts[counts == 12].index
    g = g.loc[g.index.get_level_values("year").isin(full)]
    return g.groupby(level="month").mean()


def p90_factor(iav_sigma: float, years: int = 20, lt_sigma: float = P90_LONG_TERM_SIGMA) -> float:
    """P90 of the 20-year mean yield relative to P50 (Asm: normal, IAV averaged over `years`)."""
    sigma = np.sqrt(iav_sigma**2 / years + lt_sigma**2)
    return 1.0 - Z90 * sigma


def volume_factors(internal_wake: float = BASE_INTERNAL_WAKE, availability: float = BASE_AVAILABILITY):
    """(AAP factor, metered factor) relative to the step-2 base losses.

    Wake scales both. Lower availability is treated as extra *unscheduled* downtime (Asm),
    which reduces AAP (B2: unscheduled excluded) and metered output alike.
    """
    wake = (1 - internal_wake) / (1 - BASE_INTERNAL_WAKE)
    unsched_base = 1 - BASE_AVAILABILITY - SCHEDULED_DOWNTIME
    unsched = 1 - availability - SCHEDULED_DOWNTIME
    return wake * (1 - unsched) / (1 - unsched_base), wake * availability / BASE_AVAILABILITY


# --------------------------------------------------------------------------------------
# Prices — method B (price_scenarios_method.md §3)
# --------------------------------------------------------------------------------------
AF25_MONTHS = pd.date_range("2018-01-01", periods=8760, freq="h").month.values   # Ext: CET on 2018 calendar


def align_era5_to_af25(aap: pd.DataFrame, climate_year: int, col: str = "aap_mwh", leap_drop: str = "dec31"):
    """Return 8,760 hourly values for `climate_year` in AF25 order, or None if unavailable.

    AF25 t0001 = 1 Jan 00:00 CET (no DST) = 31 Dec 23:00 UTC of the previous year (Ext).
    Leap years: the DEA does not say which day it dropped. Step 5 tested both: for 2008 the
    price/AAP correlation from March onwards peaks at lag 0 only if **31 Dec** is dropped
    (2030 prices: −0.28 vs −0.13 with 29 Feb dropped), so "dec31" is the default (Asm, evidence in the
    notebook §2). A missing first hour is filled from the next hour (Asm); fewer than 99 %
    of hours present -> None.
    """
    cet = aap[col].copy()
    cet.index = cet.index + pd.Timedelta(hours=1)
    full = pd.date_range(f"{climate_year}-01-01", f"{climate_year}-12-31 23:00", freq="h")
    if leap_drop == "dec31":
        full = full[:8760]
    else:
        full = full[~((full.month == 2) & (full.day == 29))]
    s = cet.reindex(full)
    if s.notna().mean() < 0.99:
        return None
    return s.ffill().bfill().to_numpy()


@dataclass
class MethodB:
    """Per AF25 simulated year (rows 2030/2040/2050) and month (cols 1..12)."""
    seasonal: np.ndarray        # monthly baseload / annual baseload (climate-weighted)
    cf: np.ndarray              # AAP-weighted price / baseload (climate-weighted)
    level_by_climate: dict      # climate year -> annual mean (2025 DKK) per sim year
    climate_years_used: tuple   # those with ERA5 AAP
    weights_used: dict


def method_b(af25_hourly: pd.DataFrame, aap: pd.DataFrame, zone: str,
             weights: dict = CLIMATE_WEIGHTS, leap_drop: str = "dec31") -> MethodB:
    aligned = {c: align_era5_to_af25(aap, c, leap_drop=leap_drop) for c in weights}
    used = tuple(c for c in weights if aligned[c] is not None)
    if not used:
        raise ValueError("No ERA5 AAP for any AF25 climate year")
    w_cf = {c: weights[c] / sum(weights[c2] for c2 in used) for c in used}   # renormalised (Asm)
    seasonal = np.zeros((3, 12)); cf = np.zeros((3, 12)); level = {c: [] for c in weights}
    for i, sim in enumerate(AF25_SIM_YEARS):
        sub = af25_hourly[af25_hourly["sim"] == sim]
        mon_base = {}
        for c in weights:
            p = sub[f"{zone}_{c}"].to_numpy(float)
            level[c].append(p.mean())
            mon_base[c] = np.array([p[AF25_MONTHS == m].mean() for m in range(1, 13)])
        hours = np.array([(AF25_MONTHS == m).sum() for m in range(1, 13)])
        wb = sum(weights[c] * mon_base[c] for c in weights)
        seasonal[i] = wb / (np.sum(wb * hours) / hours.sum())
        for c in used:
            p = sub[f"{zone}_{c}"].to_numpy(float)
            a = aligned[c]
            pw = np.array([np.sum(a[AF25_MONTHS == m] * np.maximum(p[AF25_MONTHS == m], 0))
                           / np.sum(a[AF25_MONTHS == m]) for m in range(1, 13)])
            cf[i] += w_cf[c] * pw / mon_base[c]
    return MethodB(seasonal, cf, {c: np.array(v) for c, v in level.items()}, used, w_cf)


def interp_years(values_by_sim: np.ndarray, years: np.ndarray) -> np.ndarray:
    """Linear between 2030/2040/2050, flat after 2050 (merchant tail, method §3 D, Asm)."""
    values_by_sim = np.asarray(values_by_sim, float)
    if values_by_sim.ndim == 1:
        return np.interp(years, AF25_SIM_YEARS, values_by_sim)
    return np.stack([np.interp(years, AF25_SIM_YEARS, values_by_sim[:, m])
                     for m in range(values_by_sim.shape[1])], axis=1)


@dataclass
class PriceScenario:
    name: str
    years: np.ndarray           # calendar years covered
    level: np.ndarray           # annual baseload, real 2026 DKK/MWh
    rp: np.ndarray              # (n_years, 12) AAP-weighted price, negatives floored (= RP, B4)
    neg_share: np.ndarray       # (n_years, 12) share of AAP in negative-price hours (curtailed, C1)
    note: str = ""

    def rp_at(self, year: int, month: int) -> float:
        return float(self.rp[year - self.years[0], month - 1])

    def neg_at(self, year: int, month: int) -> float:
        return float(self.neg_share[year - self.years[0], month - 1])

    def annual_rp(self, aap_monthly: np.ndarray) -> np.ndarray:
        return (self.rp * aap_monthly).sum(1) / aap_monthly.sum()


def historical_cf(hist_monthly: pd.DataFrame, site: str, years=range(2016, 2026)):
    """S5: mean monthly RP/baseload and negative-hour AAP share over 2016–2025 (step 3, Ext data)."""
    h = hist_monthly[hist_monthly["site"] == site].copy()
    h["year"] = h["month"].str[:4].astype(int)
    h["m"] = h["month"].str[5:7].astype(int)
    h = h[h["year"].isin(list(years))]
    h["cf"] = h["rp_dkk"] / h["baseload_dkk"]
    g = h.groupby("m")
    return g["cf"].mean().reindex(range(1, 13)).to_numpy(), g["aap_share_neg"].mean().reindex(range(1, 13)).to_numpy()


def build_price_scenarios(inputs: Inputs, site: str, years=range(2026, 2075)) -> dict:
    """S1–S5 from price_scenarios_method.md §4 for one site, real 2026 DKK."""
    zone = SITES[site]["zone"]
    years = np.arange(years.start, years.stop)
    mb = method_b(inputs.af25_hourly, inputs.aap_for_pairing(site), zone)
    central = np.array(inputs.af25_annual["Spot"][zone]) * AF25_TO_2026            # Ext (published)
    by_c = np.stack([mb.level_by_climate[c] for c in CLIMATE_WEIGHTS]) * AF25_TO_2026
    low, high = by_c.min(0), by_c.max(0)                                            # Ext (= price note T1)
    seas = interp_years(mb.seasonal, years)
    cf = interp_years(mb.cf, years)
    zeros = np.zeros_like(cf)
    cf_h, neg_h = historical_cf(inputs.hist_monthly, site)

    def mk(name, lvl_sim, cf_arr, neg, note):
        lvl = interp_years(lvl_sim, years)
        return PriceScenario(name, years, lvl, lvl[:, None] * seas * np.clip(cf_arr, 0, None), neg, note)

    # B′ (method §3 fallback, run here as a sensitivity): DEA published offshore-wind ÷ spot
    # ratio as the annual CF, monthly shape from 2016–25 history (Ext ratio, Asm shape)
    # normalised so that the AAP-weighted annual RP equals level × ratio exactly
    ratio = np.array(inputs.af25_annual["Havvind"][zone]) / np.array(inputs.af25_annual["Spot"][zone])
    w = monthly_profile(inputs.aap[site])["aap_mwh"].to_numpy(float)
    shape = seas * cf_h[None, :]
    shape = shape / ((shape * w).sum(1, keepdims=True) / w.sum())
    cf_bp = interp_years(ratio, years)[:, None] * shape / seas
    used = "/".join(map(str, mb.climate_years_used))
    return {
        "S1": mk("S1", central, cf, zeros, f"AF25 central; CF method B ({used})"),
        "S2_low": mk("S2_low", low, cf, zeros, "AF25 weather band, low climate year"),
        "S2_high": mk("S2_high", high, cf, zeros, "AF25 weather band, high climate year"),
        "S3": mk("S3", central * 0.85, cf, zeros, "Low gas: level −15 % (Asm)"),
        "S4": mk("S4", central * 0.80, cf - 0.10, zeros, "Low PtX: level −20 %, CF −0.10 (Asm)"),
        "S5": mk("S5", central, np.tile(cf_h, (len(years), 1)), np.tile(neg_h, (len(years), 1)),
                 "Historical replay: 2016–25 monthly CF and negative-hour share on S1 level"),
        "S1_Bprime": mk("S1_Bprime", central, cf_bp, zeros,
                        "AF25 central level; DEA published fleet offshore-weighted ratio (B′ fallback)"),
    }, mb


# --------------------------------------------------------------------------------------
# Parameters
# --------------------------------------------------------------------------------------
@dataclass
class Params:
    site: str
    mw: float
    strike: float                     # DKK/MWh, real 2026 (A2/A3)
    net_cap: float                    # DKK m, real 2026 (B9 × CAP_TO_2026)
    # capex, real 2026 DKK m (excl. IDC — IDC is implicit in discounting, see run_model)
    dea_base: float
    contingency: float
    owner_devex: float
    energinet: float
    dev_share: float                  # DEA development share of dea_base
    export_share: float               # export-cable share of dea_base (tax pool)
    dev_profile: dict
    constr_profile: dict
    devex_profile: dict
    energinet_profile: dict
    # opex (real 2026)
    fixed_om_k_per_mw: float
    insurance_k_per_mw: float
    var_om: float
    tariffs: float
    balancing: float
    compliance_mdkk: float
    aap_commissioning_mdkk: float
    decom_mdkk: float
    decom_security_fee: float
    perf_guarantee_mdkk: float = 308.8
    perf_guarantee_fee: float = 0.01
    perf_guarantee_years: tuple = (2027, 2032)
    decom_security_from: int = 2047
    # volumes
    aap_monthly: np.ndarray = field(default_factory=lambda: np.zeros(12))      # MWh, P50 base losses
    metered_monthly: np.ndarray = field(default_factory=lambda: np.zeros(12))
    yield_factor: float = 1.0
    aap_factor: float = 1.0
    metered_factor: float = 1.0
    overplant_mw: float = 0.0         # F5: 0 in base (Asm); merchant-only, pro rata, no wake effect
    # timing
    cod: int = 2033
    cfd_years: int = 20
    life: int = 30
    payment_lag_months: int = 1       # B7 (Doc)
    apply_cap: bool = True            # B9
    strike_indexation: str = "real"   # "real" = constant real strike; "lagged" = Sep(y−1) NPI reset (A4)
    # tax
    tax_rate: float = 0.22
    plant_rate: float = 0.15
    export_rate: float = 0.07
    energinet_sl_years: int = 5
    tax_mode: str = "group"           # "group" relief (base) or "standalone" (SEL §12)
    loss_floor_mdkk: float = 20.829
    inflation: float = 0.02
    # discounting
    wacc_cfd: float = 0.05
    wacc_tail: float = 0.07
    tail_discounting: str = "chained"  # "chained": tail flows at CfD rate to 2053 then tail rate; "full"
    valuation_date: float = VALUATION_DATE

    @property
    def cfd_end(self) -> int:          # first year after the CfD
        return self.cod + self.cfd_years

    @property
    def last_op_year(self) -> int:
        return self.cod + self.life - 1

    @property
    def capex_total(self) -> float:
        return self.dea_base + self.contingency + self.owner_devex + self.energinet

    @property
    def capex_per_mw(self) -> float:
        return self.capex_total / self.mw


def make_params(inputs: Inputs, site: str, *, capex_case: str = "base", energinet_case: str = "base",
                opex_case: str = "base", fixed_om_case: str | None = None, var_om_case: str | None = None,
                decom_case: str = "base", phasing: str = "base", capex_scale: float = 1.0,
                yield_factor: float = 1.0, internal_wake: float = BASE_INTERNAL_WAKE,
                availability: float = BASE_AVAILABILITY, life: int = 30, **overrides) -> Params:
    """Concrete Params from cost_inputs.yaml cases.

    capex_case: low/base/high (YAML) or "col2025" = DEA 2025 column (15 MW units) with base
    contingency rate and base owner's devex (paired sensitivity, Asm).
    """
    c = inputs.cost
    s = SITES[site]
    mw = s["mw"]
    cx = c["capex"][site]
    if capex_case == "col2025":
        dea = cx["dea_components_2025col_meur2020_per_mw"]["total"] * c["meta"]["dkk2026_per_eur2020"]
        cont = dea * cx["contingency_mdkk_per_mw"]["base"] / cx["dea_base_mdkk_per_mw"]["base"]
        devex = cx["owner_devex_mdkk_per_mw"]["base"]
    else:
        dea = cx["dea_base_mdkk_per_mw"][capex_case]
        cont = cx["contingency_mdkk_per_mw"][capex_case]
        devex = cx["owner_devex_mdkk_per_mw"][capex_case]
    prof = c["capex_phasing"]["profiles"][phasing]
    ox = c["opex"]
    fo = fixed_om_case or opex_case
    vo = var_om_case or opex_case
    prof_m = monthly_profile(inputs.aap[site])
    aap_f, met_f = volume_factors(internal_wake, availability)
    p = Params(
        site=site, mw=mw, strike=s["strike"], net_cap=s["net_cap_2025_mdkk"] * CAP_TO_2026,
        dea_base=dea * mw * capex_scale, contingency=cont * mw * capex_scale,
        owner_devex=devex * mw * capex_scale,
        energinet=cx["energinet_connection_mdkk_total"][energinet_case],
        dev_share=c["capex_phasing"]["dea_development_share"][site],
        export_share=c["tax"]["export_cable_share_of_dea_base"][site],
        dev_profile={int(k): v for k, v in prof["development"].items()},
        constr_profile={int(k): v for k, v in prof["construction"].items()},
        devex_profile={int(k): v for k, v in c["capex_phasing"]["owner_devex"].items()},
        energinet_profile={int(k): v for k, v in c["capex_phasing"]["energinet_connection"].items()},
        fixed_om_k_per_mw=ox["fixed_om_dkk_k_per_mw_yr"][fo],
        insurance_k_per_mw=ox["insurance_dkk_k_per_mw_yr"][opex_case],
        var_om=ox["variable_om_dkk_per_mwh"][vo],
        tariffs=ox["energinet_tariffs_dkk_per_mwh"][opex_case],
        balancing=ox["balancing_dkk_per_mwh"][opex_case],
        compliance_mdkk=ox["capability_compliance_mdkk_per_yr"][opex_case],
        aap_commissioning_mdkk=ox["aap_commissioning_oneoff_mdkk"][opex_case],
        decom_mdkk=c["decommissioning"]["cost_mdkk_per_mw"][site][decom_case] * mw,
        decom_security_fee=c["decommissioning"]["security_fee_pct_per_yr"][opex_case] / 100,
        perf_guarantee_mdkk=c["guarantees"]["performance_guarantee_mdkk"],
        perf_guarantee_fee=c["guarantees"]["performance_guarantee_fee_pct_per_yr"][opex_case] / 100,
        aap_monthly=prof_m["aap_mwh"].to_numpy(float),
        metered_monthly=prof_m["metered_mwh"].to_numpy(float),
        yield_factor=yield_factor, aap_factor=aap_f, metered_factor=met_f,
        life=life,
        tax_rate=c["tax"]["corporate_tax_rate"],
        plant_rate=c["tax"]["pools"]["plant_15pct_db"]["rate"],
        export_rate=c["tax"]["pools"]["export_cable"]["rate"]["base"],
        inflation=c["wacc"]["inflation_for_nominal_conversion"],
        wacc_cfd=c["wacc"]["cfd_period"]["base"], wacc_tail=c["wacc"]["merchant_tail"]["base"],
    )
    return replace(p, **overrides)


def set_capex_per_mw(p: Params, capex_all_in_mdkk_per_mw: float) -> Params:
    """Scale DEA base + contingency + owner devex so that all-in capex (excl. IDC) hits the target."""
    scalable = p.dea_base + p.contingency + p.owner_devex
    k = (capex_all_in_mdkk_per_mw * p.mw - p.energinet) / scalable
    return replace(p, dea_base=p.dea_base * k, contingency=p.contingency * k, owner_devex=p.owner_devex * k)


# --------------------------------------------------------------------------------------
# Building blocks
# --------------------------------------------------------------------------------------
def price_index(year, p: Params):
    """Nominal/real factor at mid-year (NPI path 2 %/yr from May 2026, contract A5, Asm)."""
    return (1 + p.inflation) ** (np.asarray(year, float) + 0.5 - PRICE_BASE_DATE)


def capex_schedule(p: Params) -> pd.DataFrame:
    """Real capex by year and tax pool (DKK m)."""
    rows = {}
    def add(year, col, v):
        rows.setdefault(year, {}).setdefault(col, 0.0)
        rows[year][col] += v
    dev = p.dea_base * p.dev_share
    construction = p.dea_base * (1 - p.dev_share) + p.contingency
    export = p.dea_base * p.export_share
    for y, w in p.dev_profile.items():
        add(y, "development", dev * w)
    for y, w in p.constr_profile.items():
        add(y, "construction", construction * w)
        add(y, "export_cable", export * w)          # subset of construction (for tax only)
    for y, w in p.devex_profile.items():
        add(y, "owner_devex", p.owner_devex * w)
    for y, w in p.energinet_profile.items():
        add(y, "energinet", p.energinet * w)
    df = pd.DataFrame(rows).T.fillna(0.0).sort_index()
    for col in ["development", "construction", "export_cable", "owner_devex", "energinet"]:
        if col not in df:
            df[col] = 0.0
    df["total"] = df[["development", "construction", "owner_devex", "energinet"]].sum(axis=1)
    df["plant_pool"] = df["total"] - df["energinet"] - df["export_cable"]
    return df


def settle_cfd(aap: np.ndarray, rp: np.ndarray, strike: np.ndarray, cap: float, apply_cap: bool = True):
    """Monthly CfD with a running net cap on state payments (B6, B8, B9).

    aap (MWh), rp and strike (DKK/MWh) are 1-D monthly arrays. Positive = state pays.
    State payments are limited to the remaining cap; payments to the state are uncapped
    and replenish the cap (net cap). Returns (payment DKK m, cap remaining after, binding flag).
    """
    need = aap * (strike - rp) / 1e6
    pay = np.empty_like(need); remaining = np.empty_like(need); binding = np.zeros(len(need), bool)
    room = cap
    for i, n in enumerate(need):
        if n > 0 and apply_cap:
            pay[i] = min(n, max(room, 0.0))
            binding[i] = pay[i] < n - 1e-12
        else:
            pay[i] = n
        room -= pay[i]
        remaining[i] = room
    return pay, remaining, binding


def depreciation(p: Params, capex: pd.DataFrame, years: np.ndarray) -> pd.DataFrame:
    """Nominal tax depreciation by pool (cost_inputs.yaml tax.pools; Ext Afskrivningsloven)."""
    pi = price_index(capex.index.values, p)
    plant_add = pd.Series(capex["plant_pool"].values * pi, capex.index)
    export_add = pd.Series(capex["export_cable"].values * pi, capex.index)
    grid_add = pd.Series(capex["energinet"].values * pi, capex.index)
    out = pd.DataFrame(0.0, index=years, columns=["plant", "export", "grid"])
    bal_plant = bal_export = 0.0
    for y in years:
        bal_plant += plant_add.get(y, 0.0)
        bal_export += export_add.get(y, 0.0)
        if y >= p.cod:                                    # depreciation starts in COD year (Ext/Asm)
            if y == p.last_op_year:                       # remaining balance written off at end of life (Asm)
                d_p, d_e = bal_plant, bal_export
            elif y > p.last_op_year:
                d_p = d_e = 0.0
            else:
                d_p, d_e = p.plant_rate * bal_plant, p.export_rate * bal_export
            bal_plant -= d_p; bal_export -= d_e
            out.loc[y, ["plant", "export"]] = [d_p, d_e]
    for y0, amt in grid_add.items():                      # §43: straight line from payment year
        for k in range(p.energinet_sl_years):
            if y0 + k in out.index:
                out.loc[y0 + k, "grid"] += amt / p.energinet_sl_years
    out["total"] = out[["plant", "export", "grid"]].sum(axis=1)
    return out


def tax_nominal(taxable: np.ndarray, p: Params) -> np.ndarray:
    """Nominal tax. group: losses used at once (negative tax). standalone: SEL §12 carry-forward."""
    if p.tax_mode == "group":
        return p.tax_rate * taxable
    tax = np.zeros_like(taxable); cf = 0.0
    for i, ti in enumerate(taxable):
        if ti <= 0:
            cf += -ti
            continue
        usable = min(cf, min(ti, p.loss_floor_mdkk) + 0.6 * max(ti - p.loss_floor_mdkk, 0.0))
        cf -= usable
        tax[i] = p.tax_rate * (ti - usable)
    return tax


def discount_at(t_abs, p: Params) -> np.ndarray:
    """Discount factor at calendar time t_abs (e.g. 2033.5) back to the valuation date.

    chained (base, Asm): CfD WACC up to the end of the CfD (1 Jan of cfd_end), tail WACC after.
    full: flows after the CfD discounted at the tail WACC all the way from the valuation date.
    """
    t_abs = np.atleast_1d(np.asarray(t_abs, float))
    t = t_abs - p.valuation_date
    t_end = p.cfd_end - p.valuation_date
    r1, r2 = p.wacc_cfd, p.wacc_tail
    df = (1 + r1) ** -t
    tail = t_abs >= p.cfd_end
    if p.tail_discounting == "chained":
        df[tail] = (1 + r1) ** -t_end * (1 + r2) ** -(t[tail] - t_end)
    elif p.tail_discounting == "full":
        df[tail] = (1 + r2) ** -t[tail]
    else:
        raise ValueError(p.tail_discounting)
    return df


def discount_factors(years: np.ndarray, p: Params) -> np.ndarray:
    """Mid-year discount factors for annual flows."""
    return discount_at(np.asarray(years, float) + 0.5, p)


# --------------------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------------------
@dataclass
class Result:
    params: Params
    scenario: str
    annual: pd.DataFrame
    monthly: pd.DataFrame
    npv: float
    cap_exhausted: str | None          # "YYYY-MM" of the first month the cap binds
    cap_used_share: float               # max cumulative net state payment / cap
    subsidy_lost: float                 # DKK m of CfD need not paid because of the cap
    idc_implicit: float                 # DKK m: capitalised cost of capital to COD at the CfD WACC

    def pv(self, col: str) -> float:
        return float((self.annual[col] * self.annual["df"]).sum())


def run_model(p: Params, scen: PriceScenario) -> Result:
    years = np.arange(min(2026, min(p.devex_profile)), p.last_op_year + 2)   # to decommissioning year
    capex = capex_schedule(p).reindex(years, fill_value=0.0)

    # ---- monthly operations
    ops_years = np.arange(p.cod, p.last_op_year + 1)
    n = len(ops_years) * 12
    yy = np.repeat(ops_years, 12); mm = np.tile(np.arange(1, 13), len(ops_years))
    aap = np.tile(p.aap_monthly, len(ops_years)) * p.yield_factor * p.aap_factor
    met = np.tile(p.metered_monthly, len(ops_years)) * p.yield_factor * p.metered_factor
    met *= 1 + p.overplant_mw / p.mw                              # overplanting: merchant only (F2)
    rp = np.array([scen.rp_at(y, m) for y, m in zip(yy, mm)])
    neg = np.array([scen.neg_at(y, m) for y, m in zip(yy, mm)])
    in_cfd = yy < p.cfd_end
    if p.strike_indexation == "lagged":                           # A4: Sep(y−1) NPI applies all year
        k = p.strike * (1 + p.inflation) ** (-(3.5 + mm - 0.5) / 12)
    else:
        k = np.full(n, p.strike)
    pay = np.zeros(n); remaining = np.full(n, np.nan); binding = np.zeros(n, bool)
    need = np.zeros(n)
    idx = np.where(in_cfd)[0]
    need[idx] = aap[idx] * (k[idx] - rp[idx]) / 1e6
    pay[idx], remaining[idx], binding[idx] = settle_cfd(aap[idx], rp[idx], k[idx], p.net_cap, p.apply_cap)
    sold = met * (1 - neg)                                        # zero output in negative hours (C1)
    merchant = met * rp / 1e6                                     # = Σ sold·p⁺  (RP floors negatives)
    variable = sold * (p.var_om + p.tariffs + p.balancing) / 1e6
    monthly = pd.DataFrame(dict(year=yy, month=mm, aap_mwh=aap, metered_mwh=met, sold_mwh=sold, rp=rp,
                                strike=k, cfd_need=need, cfd_paid=pay, cap_remaining=remaining,
                                cap_binding=binding, merchant=merchant, variable_opex=variable))
    # payment lag (B7): month m settled on the 25th of month m + lag. CfD payments are discounted
    # at their own payment date (their sign flips with the season, so annual timing would distort)
    if p.payment_lag_months:
        t_pay = yy + (mm - 1 + p.payment_lag_months) / 12 + 24 / 365
    else:
        t_pay = yy + (mm - 0.5) / 12
    monthly["pay_time"] = t_pay
    monthly["cfd_cash_year"] = np.floor(t_pay).astype(int)
    monthly["cfd_pv"] = pay * discount_at(t_pay, p)

    a = pd.DataFrame(index=years)
    a["aap_gwh"] = monthly.groupby("year")["aap_mwh"].sum() / 1e3
    a["metered_gwh"] = monthly.groupby("year")["metered_mwh"].sum() / 1e3
    a["rp"] = monthly.groupby("year").apply(lambda g: np.average(g.rp, weights=g.aap_mwh), include_groups=False)
    a["cfd_accrued"] = monthly.groupby("year")["cfd_paid"].sum()
    a["cfd_cash"] = monthly.groupby("cfd_cash_year")["cfd_paid"].sum()
    a["cfd_pv"] = monthly.groupby("cfd_cash_year")["cfd_pv"].sum()
    a["merchant"] = monthly.groupby("year")["merchant"].sum()
    a["variable_opex"] = monthly.groupby("year")["variable_opex"].sum()
    a = a.fillna(0.0)
    op = (years >= p.cod) & (years <= p.last_op_year)
    mw_tot = p.mw + p.overplant_mw
    a["fixed_opex"] = np.where(op, (p.fixed_om_k_per_mw + p.insurance_k_per_mw) * mw_tot / 1e3, 0.0)
    a["compliance"] = np.where(op & (years < p.cfd_end), p.compliance_mdkk, 0.0)
    a["compliance"] += np.where(years == p.cod, p.aap_commissioning_mdkk, 0.0)
    g0, g1 = p.perf_guarantee_years
    a["guarantee_fees"] = np.where((years >= g0) & (years <= g1),
                                   p.perf_guarantee_fee * p.perf_guarantee_mdkk / price_index(years, p), 0.0)
    a["guarantee_fees"] += np.where(op & (years >= p.decom_security_from), p.decom_security_fee * p.decom_mdkk, 0.0)
    a["decommissioning"] = np.where(years == p.last_op_year + 1, p.decom_mdkk, 0.0)
    a["capex"] = capex["total"].values
    if p.overplant_mw:
        extra = (p.dea_base + p.contingency) / p.mw * p.overplant_mw
        a["capex"] += pd.Series(capex["construction"].values / max(capex["construction"].sum(), 1e-9) * extra, years)
        capex = capex.copy(); capex["plant_pool"] += a["capex"].values - capex["total"].values

    opex_cols = ["variable_opex", "fixed_opex", "compliance", "guarantee_fees", "decommissioning"]
    a["opex"] = a[opex_cols].sum(axis=1)
    a["ebitda"] = a["cfd_accrued"] + a["merchant"] - a["opex"]
    pi = price_index(years, p)
    dep = depreciation(p, capex, years)
    a["tax_depr_nominal"] = dep["total"].values
    a["taxable_nominal"] = a["ebitda"] * pi - a["tax_depr_nominal"]
    a["tax"] = tax_nominal(a["taxable_nominal"].to_numpy(), p) / pi          # deflated to real
    a["tax_shield_real"] = p.tax_rate * a["tax_depr_nominal"] / pi
    a["fcf"] = a["cfd_cash"] + a["merchant"] - a["opex"] - a["capex"] - a["tax"]
    a["df"] = discount_factors(years, p)
    a["pv"] = (a["fcf"] - a["cfd_cash"]) * a["df"] + a["cfd_pv"]

    first_bind = monthly.loc[monthly["cap_binding"]]
    cap_ex = None if first_bind.empty else f"{int(first_bind.year.iloc[0])}-{int(first_bind.month.iloc[0]):02d}"
    cum = np.nancumsum(np.where(in_cfd, pay, 0.0))
    pre = years < p.cod
    t_pre = years[pre] + 0.5
    idc = float(np.sum(a.loc[pre, "capex"].values * ((1 + p.wacc_cfd) ** (p.cod - t_pre) - 1)))
    return Result(p, scen.name, a, monthly, float(a["pv"].sum()), cap_ex,
                  float(cum.max() / p.net_cap) if p.net_cap else np.nan,
                  float(need[in_cfd].sum() - pay[in_cfd].sum()), idc)


# --------------------------------------------------------------------------------------
# Solvers
# --------------------------------------------------------------------------------------
def npv(p: Params, scen: PriceScenario) -> float:
    return run_model(p, scen).npv


def breakeven_strike(p: Params, scen: PriceScenario, lo: float = 100.0, hi: float = 2000.0) -> float:
    """Strike (real 2026 DKK/MWh) at which NPV = 0. NaN if no root in [lo, hi]."""
    f = lambda k: npv(replace(p, strike=k), scen)
    flo, fhi = f(lo), f(hi)
    if np.sign(flo) == np.sign(fhi):
        return np.nan
    return brentq(f, lo, hi, xtol=1e-4)


def solve_wacc(p: Params, scen: PriceScenario, strike: float | None = None, tail_spread: float = 0.02,
               lo: float = -0.02, hi: float = 0.20) -> float:
    """CfD-period WACC giving NPV = 0 at `strike` (default p.strike); tail WACC = CfD + spread (Asm)."""
    k = p.strike if strike is None else strike
    f = lambda r: npv(replace(p, strike=k, wacc_cfd=r, wacc_tail=r + tail_spread), scen)
    flo, fhi = f(lo), f(hi)
    if np.sign(flo) == np.sign(fhi):
        return np.nan
    return brentq(f, lo, hi, xtol=1e-6)


def solve_capex(p: Params, scen: PriceScenario, strike: float | None = None,
                lo: float = 5.0, hi: float = 60.0) -> float:
    """All-in capex (DKK m/MW, excl. IDC) giving NPV = 0 at `strike`."""
    k = p.strike if strike is None else strike
    f = lambda x: npv(replace(set_capex_per_mw(p, x), strike=k), scen)
    flo, fhi = f(lo), f(hi)
    if np.sign(flo) == np.sign(fhi):
        return np.nan
    return brentq(f, lo, hi, xtol=1e-5)


def pv_breakdown(res: Result) -> pd.Series:
    """PV (DKK m) by line, at the valuation date."""
    a = res.annual
    d = a["df"]
    return pd.Series({
        "CfD payments (net)": a["cfd_pv"].sum(),
        "Market sales": (a["merchant"] * d).sum(),
        "Opex": -(a["opex"] - a["decommissioning"]).mul(d).sum(),
        "Decommissioning": -(a["decommissioning"] * d).sum(),
        "Capex": -(a["capex"] * d).sum(),
        "Tax": -(a["tax"] * d).sum(),
        "NPV": res.npv,
    })
