"""Figures for the one-page summary (summary/project1_summary.tex).

Values are copied from step5/bid_calibration_memo.md (21 Oct 2026, step-7 re-run) and
step5/outputs/tornado.csv, real 2026 DKK.
If step 5 is re-run, update the numbers below to match the memo.

Figures are drawn at the size they are printed (the .tex includes them at their natural
width), so FS is the printed font size in points and matches the page's small text.

Run from the repo root:  python summary/make_figures.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.patches import Patch

OUT = Path(__file__).resolve().parent

INK = "#222222"
MID = "#8a8a8a"
LIGHT = "#c8c8c8"
ACCENT = "#a8432a"  # used only where the subsidy cap binds / the gap
FS = 8.5            # printed font size (pt)
TEXT_W = 6.85       # printed text width of the A4 page (in), 1.8 cm margins

plt.rcParams.update({
    "font.family": "Liberation Sans",
    "font.size": FS,
    "axes.edgecolor": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "xtick.labelsize": FS,
    "ytick.labelsize": FS,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.6,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "xtick.major.width": 0.6,
    "ytick.major.size": 0,
})

# ---------------------------------------------------------------- gap chart
sites = [("Nordsøen Midt", 504, 532.6), ("Hesselø", 542, 559.4)]

fig, ax = plt.subplots(figsize=(TEXT_W * 0.48, 1.9))
for i, (name, awarded, breakeven) in enumerate(sites):
    y = 1 - i
    ax.plot([awarded, breakeven], [y, y], color=ACCENT, lw=2.4, zorder=1)
    ax.scatter(awarded, y, s=50, facecolor="white", edgecolor=INK, lw=1.3, zorder=2)
    ax.scatter(breakeven, y, s=50, color=INK, zorder=2)
    ax.text(awarded - 3, y, f"{awarded}", ha="right", va="center")
    ax.text(breakeven + 3, y, f"{breakeven:.0f}", ha="left", va="center")
    gap = breakeven - awarded
    ax.text((awarded + breakeven) / 2, y + 0.24, f"+{gap:.0f} (+{gap / awarded:.1%})",
            ha="center", va="bottom", color=ACCENT)
ax.set_yticks([1, 0], [s[0] for s in sites])
ax.set_ylim(-0.55, 1.65)
ax.set_xlim(485, 595)
ax.set_xticks(range(500, 591, 30))
ax.set_xlabel("Strike price, DKK/MWh (real 2026)")
ax.spines["left"].set_visible(False)
handles = [
    plt.Line2D([], [], marker="o", ls="", mfc="white", mec=INK, label="Awarded"),
    plt.Line2D([], [], marker="o", ls="", color=INK, label="Break-even, base case"),
]
ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(-0.02, 1.0), frameon=False,
          handletextpad=0.2, borderaxespad=0, ncol=2, columnspacing=1.0)
fig.tight_layout(pad=0.2)
fig.savefig(OUT / "fig_gap.png", dpi=300)
plt.close(fig)

# ------------------------------------------------------------- tornado chart
# Same input order in both panels. None = no break-even strike exists.
# (low case, high case); a value above XMAX means the subsidy cap binds.
rows = [
    "Capex",
    "Discount rate",
    "Operating costs",
    "Wind output (P10 / P90)",
    "Price outlook",
    "Asset life (35 / 25 yrs)",
    "Availability 93.5 %",
]
data = {
    "Nordsøen Midt": dict(base=533, awarded=504, vals=[
        (456, 977), (474, 811), (504, 727), (493, 581), (526, None), (512, 562), (None, 547)]),
    "Hesselø": dict(base=559, awarded=542, vals=[
        (477, 656), (498, 657), (530, 631), (517, 609), (553, 584), (537, 591), (None, 575)]),
}
XMIN, XMAX = 425, 760
SMALL = FS - 0.5

fig, axes = plt.subplots(1, 2, figsize=(TEXT_W, 2.75), sharey=True)
for ax, (site, d) in zip(axes, data.items()):
    base = d["base"]
    for i, (lo, hi) in enumerate(d["vals"]):
        y = len(rows) - 1 - i
        if lo is not None:
            ax.barh(y, lo - base, left=base, height=0.64, color=LIGHT, edgecolor="none")
            ax.text(lo - 4, y, f"{lo}", ha="right", va="center", fontsize=SMALL,
                    bbox=dict(facecolor="white", edgecolor="none", pad=0.5))
        if hi is None and i == 4:  # no strike gives NPV = 0
            ax.barh(y, XMAX - base, left=base, height=0.64, color=ACCENT, edgecolor="none")
            ax.text(XMAX - 6, y, "no break-even", ha="right", va="center",
                    fontsize=SMALL, color="white")
        elif hi is not None and hi > XMAX:
            ax.barh(y, XMAX - base, left=base, height=0.64, color=ACCENT, edgecolor="none")
            ax.text(XMAX - 6, y, f"{hi:,}", ha="right", va="center", fontsize=SMALL, color="white")
        elif hi is not None:
            ax.barh(y, hi - base, left=base, height=0.64, color=MID, edgecolor="none")
            ax.text(hi + 4, y, f"{hi}", ha="left", va="center", fontsize=SMALL)
    ax.axvline(base, color=INK, lw=0.9)
    ax.axvline(d["awarded"], color=INK, lw=0.8, ls=(0, (3, 2)))
    ax.text(base + 4, -1.05, f"base {base}", fontsize=SMALL, va="center")
    ax.text(d["awarded"] - 4, -1.05, f"awarded {d['awarded']}", fontsize=SMALL,
            va="center", ha="right")
    ax.set_xlim(XMIN, XMAX)
    ax.set_xticks(range(450, 701, 50))
    ax.set_ylim(-1.5, len(rows) - 0.4)
    ax.set_title(site, fontsize=FS + 0.5, loc="left", fontweight="bold", color=INK)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Break-even strike, DKK/MWh")
axes[0].set_yticks(range(len(rows)), rows[::-1])
fig.legend(handles=[Patch(color=LIGHT, label="Favourable case"),
                    Patch(color=MID, label="Unfavourable case"),
                    Patch(color=ACCENT, label="Unfavourable, payment cap binds")],
           loc="upper right", ncol=3, frameon=False, bbox_to_anchor=(1, 1.02),
           handlelength=1.2, columnspacing=1.0)
fig.tight_layout(pad=0.2, rect=(0, 0, 1, 0.92))
fig.savefig(OUT / "fig_tornado_summary.png", dpi=300)
plt.close(fig)

# Drop the alpha channel: some PDF viewers draw it as a faint grey box.
for name in ("fig_gap.png", "fig_tornado_summary.png"):
    Image.open(OUT / name).convert("RGB").save(OUT / name, dpi=(300, 300))
print("written:", OUT / "fig_gap.png", OUT / "fig_tornado_summary.png")
