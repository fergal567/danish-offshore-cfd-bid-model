"""Step 7 – headline numbers after the insurance and tax-pool changes.

Prints, per site (S1 price scenario, base inputs):
  - break-even strike, NPV at the awarded strike
  - implied CfD-period rate (tail +2 pp) and all-in capex that give NPV = 0 at the awarded strike
  - share of the net cap used at the awarded strike
and the break-even under the step-5 settings, to show what each step-7 change does.

Run from the repo root (takes about a minute):  python step7/headline_check.py
"""
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "step5"))
import dcf_model as d  # noqa: E402

inp = d.load_inputs()
rows = []
for s in d.SITES:
    sc, _ = d.build_price_scenarios(inp, s)
    s1 = sc["S1"]
    p = d.make_params(inp, s)                                   # new base (step 7)
    res = d.run_model(p, s1)
    be = d.breakeven_strike(p, s1)
    r = d.solve_wacc(p, s1)
    cx = d.solve_capex(p, s1)
    # step-5 settings, one change at a time
    ins_step5 = inp.cost["opex"]["insurance_dkk_k_per_mw_yr"]["high"]   # = old base 74.6
    be_old_ins = d.breakeven_strike(replace(p, insurance_k_per_mw=ins_step5), s1)
    be_old_tax = d.breakeven_strike(d.make_params(inp, s, tax7_scope="export_only"), s1)
    be_step5 = d.breakeven_strike(d.make_params(inp, s, tax7_scope="export_only",
                                                insurance_k_per_mw=ins_step5), s1)
    rows.append((s, p.strike, be, res.npv, r, cx, p.capex_per_mw, res.cap_used_share,
                 be_step5, be_old_ins, be_old_tax))

for (s, k, be, npv, r, cx, cx0, cap, be5, be_i, be_t) in rows:
    print(f"\n== {s} (awarded {k:.0f} DKK/MWh) ==")
    print(f"Break-even strike, new base     : {be:7.1f}  ({(be / k - 1):+.1%} vs awarded)")
    print(f"NPV at awarded strike           : {npv:7.0f} DKK m")
    print(f"Implied CfD-period rate (real)  : {r:7.2%}  (tail +2 pp)")
    print(f"Capex giving NPV=0 at 5 %       : {cx:7.2f} DKK m/MW  (base {cx0:.2f}, {cx / cx0 - 1:+.1%})")
    print(f"Net cap used at awarded strike  : {cap:7.0%}")
    print(f"Step-5 settings break-even      : {be5:7.1f}")
    print(f"  only insurance back in        : {be_i:7.1f}  (insurance effect {be - be_i:+.1f})")
    print(f"  only old tax scope            : {be_t:7.1f}  (tax-pool effect {be - be_t:+.1f})")
