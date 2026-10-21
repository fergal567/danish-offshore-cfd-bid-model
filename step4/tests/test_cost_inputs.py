"""Sanity checks on step4/cost_inputs.yaml.  Run:  python -m pytest step4/tests -q"""
from pathlib import Path

import pytest
import yaml

Y = yaml.safe_load((Path(__file__).parents[1] / "cost_inputs.yaml").read_text(encoding="utf-8"))


def _lbh_dicts(node, path=""):
    if isinstance(node, dict):
        if set(node) == {"low", "base", "high"} and all(isinstance(v, (int, float)) for v in node.values()):
            yield path, node
        for k, v in node.items():
            yield from _lbh_dicts(v, f"{path}/{k}")


def test_npi_factor():
    m = Y["meta"]
    assert m["npi_base_2026M05"] == 102.13
    assert 1.19 < m["factor_2020_to_2026_npi"] < 1.20
    assert m["dkk2026_per_eur2020"] == pytest.approx(7.46 * m["factor_2020_to_2026_npi"], rel=1e-3)


@pytest.mark.parametrize("name", ["base", "early", "late"])
def test_phasing_sums_to_one(name):
    p = Y["capex_phasing"]["profiles"][name]
    assert sum(p["development"].values()) == pytest.approx(1, abs=1e-3)
    assert sum(p["construction"].values()) == pytest.approx(1, abs=1e-3)
    assert sum(Y["capex_phasing"]["owner_devex"].values()) == pytest.approx(1, abs=1e-3)


def test_connection_contributions():
    assert Y["capex"]["NSM"]["energinet_connection_mdkk_total"]["base"] == pytest.approx(2 * 18.3 + 1005 * 0.623, abs=0.1)
    assert Y["capex"]["HES"]["energinet_connection_mdkk_total"]["base"] == pytest.approx(2 * 18.3 + 795 * 0.175, abs=0.1)


def test_ranges_ordered():
    bad = [p for p, d in _lbh_dicts(Y) if not d["low"] <= d["base"] <= d["high"]
           and "export_cable" not in p and "infrastructure_7pct" not in p]          # export-cable rate: 'low' case = faster 15 % (tax-favourable)
    assert not bad, bad


def test_dea_components_sum_to_sheet_total():
    d = yaml.safe_load((Path(__file__).parents[1] / "dea_offshore_ac_2030.yaml").read_text(encoding="utf-8"))
    for col in ("2030", "2025"):
        c = d["ac_fixed"][col]
        parts = sum(c[k] for k in ("project_development", "turbines", "foundation",
                                   "array_cables", "substation", "export_cables"))
        assert parts == pytest.approx(c["nominal_investment_total"], rel=1e-6)


def test_site_adjustment_direction():
    # both sites are closer to shore than the DEA 60 km site -> cheaper export cable and lower total
    for s in ("NSM", "HES"):
        c = Y["capex"][s]
        assert c["dea_components_meur2020_per_mw"]["export_cables"] < 0.2648
        assert c["dea_base_meur2020_per_mw"]["base"] < c["dea_unadjusted_2030_meur2020_per_mw"]
    assert (Y["capex"]["NSM"]["dea_components_meur2020_per_mw"]["export_cables"]
            < Y["capex"]["HES"]["dea_components_meur2020_per_mw"]["export_cables"])


def test_all_in_adds_up():
    for s in ("NSM", "HES"):
        c = Y["capex"][s]
        parts = (c["dea_base_mdkk_per_mw"]["base"] + c["contingency_mdkk_per_mw"]["base"]
                 + c["owner_devex_mdkk_per_mw"]["base"] + c["energinet_connection_mdkk_per_mw"]["base"])
        assert parts == pytest.approx(c["capex_all_in_mdkk_per_mw"]["base"], abs=0.01)
