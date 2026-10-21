"""Tests for step5/dcf_model.py. Run from the repo root:  python -m pytest step5/tests -q

Most tests use small synthetic inputs, so they run without the git-ignored data files.
Integration tests at the end are skipped when step2/step4/step5 data are missing.
"""
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dcf_model as d  # noqa: E402


# ----------------------------------------------------------------------------- fixtures
def synth_params(**kw) -> d.Params:
    p = d.Params(
        site="NSM", mw=1000.0, strike=500.0, net_cap=1e9,
        dea_base=20_000.0, contingency=1_500.0, owner_devex=100.0, energinet=600.0,
        dev_share=0.075, export_share=0.055,
        dev_profile={2027: 0.5, 2028: 0.5}, constr_profile={2030: 0.5, 2031: 0.5},
        devex_profile={2026: 1.0}, energinet_profile={2029: 1.0},
        fixed_om_k_per_mw=300.0, insurance_k_per_mw=75.0, var_om=30.0, tariffs=9.0, balancing=15.0,
        compliance_mdkk=3.0, aap_commissioning_mdkk=5.0, decom_mdkk=2_400.0, decom_security_fee=0.005,
        aap_monthly=np.full(12, 400_000.0), metered_monthly=np.full(12, 386_000.0),
    )
    return replace(p, **kw)


def flat_scenario(rp: float = 300.0, neg: float = 0.0, years=range(2026, 2080)) -> d.PriceScenario:
    yrs = np.arange(years.start, years.stop)
    return d.PriceScenario("flat", yrs, np.full(len(yrs), rp), np.full((len(yrs), 12), rp),
                           np.full((len(yrs), 12), neg))


# ----------------------------------------------------------------------------- CfD settlement
def test_settle_cfd_uncapped_equals_need():
    aap = np.full(6, 1e5); rp = np.array([300, 600, 300, 300, 700, 300.0]); k = np.full(6, 500.0)
    pay, rem, bind = d.settle_cfd(aap, rp, k, cap=1e6)
    np.testing.assert_allclose(pay, aap * (k - rp) / 1e6)
    assert not bind.any()
    assert rem[-1] == pytest.approx(1e6 - pay.sum())


def test_settle_cfd_cap_binds_and_clawback_replenishes():
    aap = np.full(4, 1e5); k = np.full(4, 500.0)
    rp = np.array([300.0, 300.0, 700.0, 300.0])       # need +20, +20, −20, +20 (DKK m)
    pay, rem, bind = d.settle_cfd(aap, rp, k, cap=30.0)
    np.testing.assert_allclose(pay, [20, 10, -20, 20])  # cap hits in month 2; clawback frees 20
    assert list(bind) == [False, True, False, False]
    assert rem[-1] == pytest.approx(0.0)
    assert (pay.cumsum() <= 30.0 + 1e-9).all()          # net state payments never exceed cap


def test_settle_cfd_payments_to_state_uncapped():
    pay, _, _ = d.settle_cfd(np.full(2, 1e5), np.array([5000.0, 5000.0]), np.full(2, 500.0), cap=1.0)
    np.testing.assert_allclose(pay, [-450, -450])


def test_cap_switch_off():
    p = synth_params(net_cap=10.0, apply_cap=False)
    r = d.run_model(p, flat_scenario(100.0))
    assert r.cap_exhausted is None and r.subsidy_lost == pytest.approx(0.0)


# ----------------------------------------------------------------------------- revenue identity, lag
def test_revenue_identity_strike_times_aap():
    """Metered = AAP, no cap binding, no negative prices -> CfD + market = strike × AAP (step 3 §1)."""
    p = synth_params(metered_monthly=np.full(12, 400_000.0))
    r = d.run_model(p, flat_scenario(320.0))
    a = r.annual.loc[p.cod:p.cfd_end - 1]
    np.testing.assert_allclose(a["cfd_accrued"] + a["merchant"], p.strike * a["aap_gwh"] * 1e3 / 1e6)


def test_payment_lag_shifts_but_preserves_total():
    p = synth_params()
    sc = flat_scenario(300.0)
    r1, r0 = d.run_model(p, sc), d.run_model(replace(p, payment_lag_months=0), sc)
    assert r1.annual["cfd_cash"].sum() == pytest.approx(r1.annual["cfd_accrued"].sum())
    np.testing.assert_allclose(r0.annual["cfd_cash"], r0.annual["cfd_accrued"])
    assert r1.annual.loc[p.cfd_end, "cfd_cash"] > 0          # Dec of last CfD year paid next January
    assert r1.npv < r0.npv                                    # a lag on net receipts costs value
    # size ≈ PV(CfD) × (1 − DF of ~0.6 month extra): mid-month -> 25th of next month
    pv_cfd = r0.annual["cfd_pv"].sum()
    expected = pv_cfd * (1 - 1.05 ** -((1 + 24 / 365 * 12 - 0.5) / 12))
    assert r0.npv - r1.npv == pytest.approx(expected, rel=0.05)


def test_payment_lag_small_with_seasonal_sign_flip():
    """Winter clawbacks / summer payouts: the lag must stay a ~1-month effect, not a 1-year one."""
    yrs = np.arange(2026, 2080)
    rp = np.tile(np.array([900, 800, 400, 300, 200, 200, 200, 200, 300, 400, 800, 1200.0]), (len(yrs), 1))
    sc = d.PriceScenario("seasonal", yrs, rp.mean(1), rp, np.zeros_like(rp))
    p = synth_params()
    r1, r0 = d.run_model(p, sc), d.run_model(replace(p, payment_lag_months=0), sc)
    assert abs(r1.npv - r0.npv) < 0.01 * abs(r0.annual["cfd_pv"]).sum() + 1.0


def test_negative_hours_cut_variable_cost_not_rp_revenue():
    p = synth_params()
    r0, r1 = d.run_model(p, flat_scenario(300.0, 0.0)), d.run_model(p, flat_scenario(300.0, 0.05))
    assert r1.annual["merchant"].sum() == pytest.approx(r0.annual["merchant"].sum())
    assert r1.annual["variable_opex"].sum() == pytest.approx(0.95 * r0.annual["variable_opex"].sum())


def test_overplanting_zero_is_neutral():
    p = synth_params()
    assert d.run_model(replace(p, overplant_mw=0.0), flat_scenario()).npv == pytest.approx(
        d.run_model(p, flat_scenario()).npv)


def test_lagged_strike_indexation_lowers_value():
    p = synth_params()
    assert d.run_model(replace(p, strike_indexation="lagged"), flat_scenario()).npv < d.run_model(p, flat_scenario()).npv


# ----------------------------------------------------------------------------- capex, tax
def test_capex_schedule_sums_to_total():
    p = synth_params()
    cs = d.capex_schedule(p)
    assert cs["total"].sum() == pytest.approx(p.capex_total)
    assert cs["export_cable"].sum() == pytest.approx(p.dea_base * p.export_share)
    assert cs["plant_pool"].sum() == pytest.approx(p.capex_total - p.energinet - p.dea_base * p.export_share)


def test_depreciation_recovers_full_nominal_cost():
    p = synth_params()
    cs = d.capex_schedule(p)
    years = np.arange(2026, p.last_op_year + 2)
    dep = d.depreciation(p, cs, years)
    nominal_cost = (cs["total"] * d.price_index(cs.index.values, p)).sum()
    assert dep["total"].sum() == pytest.approx(nominal_cost)
    assert dep.loc[:p.cod - 1, ["plant", "export"]].to_numpy().sum() == 0      # starts at COD
    assert dep.loc[2029:2033, "grid"].gt(0).all() and dep.loc[2034:, "grid"].eq(0).all()   # §43 5 yrs


def test_plant_pool_15pct_declining_balance_first_year():
    p = synth_params(inflation=0.0)
    cs = d.capex_schedule(p)
    dep = d.depreciation(p, cs, np.arange(2026, 2064))
    assert dep.loc[p.cod, "plant"] == pytest.approx(0.15 * cs["plant_pool"].sum())
    assert dep.loc[p.cod, "export"] == pytest.approx(0.07 * cs["export_cable"].sum())


def test_tax_shield_deflated():
    """With inflation, the same nominal depreciation is worth less in real terms."""
    r0 = d.run_model(synth_params(inflation=0.0), flat_scenario())
    r2 = d.run_model(synth_params(inflation=0.02), flat_scenario())
    assert r2.pv("tax_shield_real") < r0.pv("tax_shield_real")


def test_standalone_tax_loss_rule():
    p = synth_params(tax_mode="standalone", loss_floor_mdkk=20.0)
    tax = d.tax_nominal(np.array([-100.0, 50.0, 100.0]), p)
    # year 2: 20 + 0.6·30 = 38 offset -> taxable 12; year 3: 20 + 0.6·80 = 68 > 62 left -> taxable 38
    np.testing.assert_allclose(tax, [0.0, 0.22 * 12, 0.22 * 38])
    assert d.tax_nominal(np.array([-100.0, 50.0]), synth_params())[0] == pytest.approx(-22.0)  # group relief


# ----------------------------------------------------------------------------- discounting
def test_chained_discounting_continuous_and_lower_rate_before_tail():
    p = synth_params()
    yrs = np.arange(2026, 2064)
    dfc = d.discount_factors(yrs, p)
    dff = d.discount_factors(yrs, replace(p, tail_discounting="full"))
    np.testing.assert_allclose(dfc[yrs < p.cfd_end], dff[yrs < p.cfd_end])
    assert (dfc[yrs >= p.cfd_end] > dff[yrs >= p.cfd_end]).all()
    i = np.where(yrs == p.cfd_end)[0][0]
    assert dfc[i - 1] / dfc[i] == pytest.approx((1.05 ** 0.5) * (1.07 ** 0.5))   # mid-year to mid-year


def test_idc_zero_at_zero_wacc():
    assert d.run_model(synth_params(wacc_cfd=0.0), flat_scenario()).idc_implicit == pytest.approx(0.0)


# ----------------------------------------------------------------------------- volumes, alignment
def test_volume_factors():
    assert d.volume_factors() == pytest.approx((1.0, 1.0))
    aap_f, met_f = d.volume_factors(availability=0.935)
    assert aap_f == pytest.approx(0.945 / 0.97) and met_f == pytest.approx(0.935 / 0.96)
    assert d.volume_factors(internal_wake=0.13)[0] == pytest.approx(0.87 / 0.90)


def test_p90_factor_range():
    assert 0.90 < d.p90_factor(0.035) < 0.93


def test_align_era5_to_af25_cet_and_leap_year():
    idx = pd.date_range("2007-12-31 00:00", "2009-01-01 00:00", freq="h")   # UTC
    s = pd.DataFrame({"aap_mwh": np.arange(len(idx), dtype=float)}, index=idx)
    out = d.align_era5_to_af25(s, 2008)
    assert len(out) == 8760
    assert out[0] == s.loc["2007-12-31 23:00", "aap_mwh"]            # 00:00 CET = 23:00 UTC
    assert out[-1] == s.loc["2008-12-30 22:00", "aap_mwh"]          # 31 Dec dropped (default)
    out2 = d.align_era5_to_af25(s, 2008, leap_drop="feb29")
    assert out2[-1] == s.loc["2008-12-31 22:00", "aap_mwh"]
    assert d.align_era5_to_af25(s, 1995) is None


# ----------------------------------------------------------------------------- solvers
def test_breakeven_strike_and_wacc_solvers():
    p = synth_params()
    sc = flat_scenario(300.0)
    k = d.breakeven_strike(p, sc)
    assert d.npv(replace(p, strike=k), sc) == pytest.approx(0.0, abs=1e-3)
    r = d.solve_wacc(replace(p, strike=k + 50), sc)
    assert r > p.wacc_cfd                                            # higher strike supports higher WACC
    assert d.npv(replace(p, strike=k + 50, wacc_cfd=r, wacc_tail=r + 0.02), sc) == pytest.approx(0.0, abs=1e-2)


def test_set_capex_per_mw():
    p = d.set_capex_per_mw(synth_params(), 18.0)
    assert p.capex_per_mw == pytest.approx(18.0)


def test_cap_makes_strike_ineffective_when_binding():
    """With a tiny cap, raising the strike barely helps: NPV is bounded above."""
    p = synth_params(net_cap=500.0)
    sc = flat_scenario(200.0)
    assert d.npv(replace(p, strike=2000), sc) - d.npv(replace(p, strike=1000), sc) < 50


# ----------------------------------------------------------------------------- integration (real data)
DATA = all(x.exists() for x in [d.Paths().cost_yaml, d.Paths().af25_xlsx,
                                d.Paths().aap_dir / "aap_hourly_NSM.csv", d.Paths().hist_monthly])


@pytest.fixture(scope="module")
def inputs():
    return d.load_inputs()


@pytest.mark.skipif(not DATA, reason="step2/4/5 data files not present")
def test_capex_matches_step4_all_in(inputs):
    for site in d.SITES:
        p = d.make_params(inputs, site)
        assert p.capex_total == pytest.approx(inputs.cost["capex"][site]["capex_all_in_mdkk_total"]["base"], rel=1e-3)


@pytest.mark.skipif(not DATA, reason="step2/4/5 data files not present")
def test_af25_published_levels_and_weather_band(inputs):
    assert inputs.af25_annual["Spot"]["DK1"] == [460.0, 400.0, 450.0]
    mb = d.method_b(inputs.af25_hourly, inputs.aap["NSM"], "DK1")
    by_c = np.stack([mb.level_by_climate[c] for c in d.CLIMATE_WEIGHTS])
    np.testing.assert_allclose(by_c.min(0), [420, 330, 420], atol=5)    # price note Table 1, low
    np.testing.assert_allclose(by_c.max(0), [510, 450, 480], atol=5)    # high
    w = sum(d.CLIMATE_WEIGHTS[c] * mb.level_by_climate[c] for c in d.CLIMATE_WEIGHTS)
    np.testing.assert_allclose(w, [460, 400, 450], atol=3)              # 0.25/0.35/0.40 weights
    assert np.allclose(mb.seasonal.mean(1), 1.0, atol=0.02)
    assert ((mb.cf > 0.5) & (mb.cf < 1.1)).all()


@pytest.mark.skipif(not DATA, reason="step2/4/5 data files not present")
def test_yield_profile_matches_step2(inputs):
    ys = inputs.yield_summary
    for site in d.SITES:
        prof = d.monthly_profile(inputs.aap[site])
        assert prof["aap_mwh"].sum() / 1e3 == pytest.approx(ys[ys.site == site]["aap_proxy_GWh"].mean(), rel=2e-3)


@pytest.mark.skipif(not DATA, reason="step2/4/5 data files not present")
def test_1995_used_for_pairing_only(inputs):
    """Reconstructed 1995 AAP feeds method B but must not change the P50 yield profile."""
    if not inputs.aap_1995:
        pytest.skip("run step5/reconstruct_aap_1995.py first")
    for site in inputs.aap_1995:
        pair = inputs.aap_for_pairing(site)
        assert pair.index.year.min() == 1995 and len(pair) == len(inputs.aap[site]) + 8760
        p = d.make_params(inputs, site)
        assert p.aap_monthly.sum() == pytest.approx(d.monthly_profile(inputs.aap[site])["aap_mwh"].sum())
        assert d.method_b(inputs.af25_hourly, pair, d.SITES[site]["zone"]).climate_years_used == (1995, 2008, 2009)
