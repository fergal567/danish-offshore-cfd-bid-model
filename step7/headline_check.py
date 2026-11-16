"""Headline numbers, plus what the step-7 and Nov 2026 review changes do one at a time.

Prints, per site (S1 price scenario, base inputs):
  - break-even strike, NPV at the awarded strike, and whether the net cap binds at the break-even strike
  - implied CfD-period rate (tail +2 pp) and all-in capex that give NPV = 0 at the awarded strike
  - share of the net cap used at the awarded strike; S4 cap exhaustion and payments lost; S1-B′ break-even
and the break-even with each change reverted on its own (from the current base, so effects are not additive:
at Nordsøen Midt the net cap binds at the break-even strike, which magnifies every change).

Run from the repo root (takes about a minute):  python step7/headline_check.py
"""
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "step5"))
import dcf_model as d  # noqa: E402

inp = d.load_inputs()


def fmt(v):
    return f"{v:7.1f}" if np.isfinite(v) else "   none (cap-limited)"


for s in d.SITES:
    sc, _ = d.build_price_scenarios(inp, s)
    s1 = sc["S1"]
    p = d.make_params(inp, s)
    res = d.run_model(p, s1)
    be = d.breakeven_strike(p, s1)
    res_be = d.run_model(replace(p, strike=be), s1)
    r = d.solve_wacc(p, s1)
    cx = d.solve_capex(p, s1)
    s4 = d.run_model(p, sc["S4"])
    bp = d.breakeven_strike(p, sc["S1_Bprime"])

    print(f"\n== {s} (awarded {p.strike:.0f} DKK/MWh) ==")
    print(f"Break-even strike               : {be:7.1f}  ({(be / p.strike - 1):+.1%} vs awarded); "
          f"net cap at break-even: {'exhausted ' + res_be.cap_exhausted if res_be.cap_exhausted else 'not exhausted'}")
    print(f"NPV at awarded strike           : {res.npv:7.0f} DKK m")
    print(f"Implied CfD-period rate (real)  : {r:7.2%}  (tail +2 pp)")
    print(f"Capex giving NPV=0 at 5 %       : {cx:7.2f} DKK m/MW  (base {p.capex_per_mw:.2f}, {cx / p.capex_per_mw - 1:+.1%})")
    print(f"Net cap used at awarded strike  : {res.cap_used_share:7.0%}")
    print(f"S4 at awarded strike            : cap {'exhausted ' + s4.cap_exhausted if s4.cap_exhausted else 'not exhausted'}"
          f", payments lost DKK {s4.subsidy_lost:,.0f}m, max cap use {s4.cap_used_share:.0%}")
    print(f"Break-even, S1-B′ (DEA ratio)   : {fmt(bp)}")

    print("  Reverted one at a time (break-even strike):")
    reverts = {
        "constant real strike (A4 lag off)": replace(p, strike_indexation="real"),
        "producer tariffs 9.2 back in (O4)": replace(p, tariffs=9.2),
        "internal wake 10 % (volume factor)": d.make_params(inp, s, internal_wake=0.10),
        "insurance back in (step 7, V6)": replace(p, insurance_k_per_mw=inp.cost["opex"]["insurance_dkk_k_per_mw_yr"]["high"]),
        "export cable only in 7 % pool (V1)": d.make_params(inp, s, tax7_scope="export_only"),
    }
    if p.ext_wake_late:
        reverts["no Nordsøen Syd wake"] = d.make_params(inp, s, nss_wake=0.0)
    for name, q in reverts.items():
        b = d.breakeven_strike(q, s1)
        print(f"    {name:36s}: {fmt(b)}  ({b - be:+.1f})" if np.isfinite(b) else f"    {name:36s}: {fmt(b)}")
