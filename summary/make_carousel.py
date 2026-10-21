"""LinkedIn document carousel for Project 1: 4 pages, 1080 x 1350 px (4:5).

Numbers are from step5/bid_calibration_memo.md (21 Oct 2026, after the step-7 re-run), real 2026 DKK.
The Nordsøen Syd figure is the DKK 6.6bn net cap (Annex F 11.5.2, 2025 prices)
spread over 20 years of the DEA interim estimate of 4,483 GWh/yr (App 3 Table 1).

Run from the repo root:  python summary/make_carousel.py
Writes summary/linkedin_carousel.pdf and a PNG preview per page.
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

OUT = Path(__file__).resolve().parent

INK = "#1a1a1a"
GREY = "#6b6b6b"
LIGHT = "#cfcfcf"
ACCENT = "#a8432a"
SERIF = "Liberation Serif"
SANS = "Liberation Sans"

W, H = 10.8, 13.5  # inches at 100 dpi = 1080 x 1350 px
PAGES = 4
plt.rcParams.update({"font.family": SANS, "axes.edgecolor": INK,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "white", "savefig.facecolor": "white"})


def new_page(n, kicker):
    fig = plt.figure(figsize=(W, H))
    fig.text(0.08, 0.935, kicker.upper(), fontsize=17, color=GREY, family=SANS,
             fontweight="bold")
    fig.add_artist(plt.Line2D([0.08, 0.92], [0.075, 0.075], color=LIGHT, lw=1.2))
    fig.text(0.08, 0.045, "Fergal Israel  ·  MSc Wind Energy, DTU", fontsize=17, color=GREY)
    fig.text(0.92, 0.045, f"{n}/{PAGES}", fontsize=17, color=GREY, ha="right")
    return fig


def headline(fig, text, y=0.87, size=50):
    # One line at a time, so every line gets the same spacing.
    step = size * 1.18 / 72 / H
    for i, line in enumerate(text.split("\n")):
        fig.text(0.08, y - i * step, line, fontsize=size, color=INK, family=SERIF,
                 fontweight="bold", va="top")


pages = []

# ---------------------------------------------------------------- page 1
fig = new_page(1, "Denmark’s 2026 offshore wind tenders")
headline(fig, "Vattenfall’s winning bids\nsit 3–6 % below\nbreak-even in my model")
fig.text(0.08, 0.665, "Rebuilt from public data: tender documents,\nhourly wind, DEA cost data, Danish tax rules.",
         fontsize=22, color=GREY, va="top", linespacing=1.35)

ax = fig.add_axes([0.08, 0.22, 0.84, 0.34])
sites = [("Nordsøen Midt", 504, 533), ("Hesselø", 542, 559)]
for i, (name, awarded, be) in enumerate(sites):
    y = 1 - i
    ax.plot([awarded, be], [y, y], color=ACCENT, lw=7, solid_capstyle="butt", zorder=1)
    ax.scatter(awarded, y, s=520, facecolor="white", edgecolor=INK, lw=3, zorder=2)
    ax.scatter(be, y, s=520, color=INK, zorder=2)
    ax.text(awarded, y - 0.24, f"{awarded}", ha="center", va="top", fontsize=24, color=INK)
    ax.text(be, y - 0.24, f"{be}", ha="center", va="top", fontsize=24, color=INK, fontweight="bold")
    ax.text(480, y + 0.24, name, ha="left", va="bottom", fontsize=26, color=INK, fontweight="bold")
    ax.text(be + 6, y, f"+{be - awarded}", ha="left", va="center", fontsize=24, color=ACCENT,
            fontweight="bold")
ax.set_xlim(480, 600)
ax.set_ylim(-0.7, 1.75)
ax.axis("off")
fig.text(0.08, 0.17, "○ awarded price    ● break-even, base case    (DKK/MWh)",
         fontsize=19, color=GREY)
pages.append(fig)

# ---------------------------------------------------------------- page 2
fig = new_page(2, "So what makes them work?")
headline(fig, "Any one of these\ncloses the gap")
items = [
    ("4.5–4.7 %", "return, real after tax (my base: 5.0 %),\nabout 1 pp above Vattenfall’s own rate"),
    ("4–6 % lower", "build cost than my estimate\nfrom DEA data"),
    ("P10 wind", "a high-output year, not the median"),
]
y = 0.70
for big, small in items:
    fig.text(0.08, y, big, fontsize=58, color=ACCENT, family=SERIF, fontweight="bold", va="top")
    fig.text(0.08, y - 0.07, small, fontsize=24, color=INK, va="top", linespacing=1.3)
    y -= 0.175
fig.add_artist(plt.Line2D([0.08, 0.92], [0.2, 0.2], color=INK, lw=1.5))
fig.text(0.08, 0.18, "My read: a bet on next-generation 20 MW turbines.",
         fontsize=24, color=INK, fontweight="bold", va="top")
fig.text(0.08, 0.135, "With 15 MW turbine costs it drops to 2.8–3.1 %, below Vattenfall’s rate.",
         fontsize=19, color=GREY, va="top")
pages.append(fig)

# ---------------------------------------------------------------- page 3
fig = new_page(3, "The bigger risk")
headline(fig, "The state’s payment\ncap is much tighter\nat Nordsøen Midt")
fig.text(0.08, 0.665, "Average top-up the cap can fund over 20 years, DKK/MWh",
         fontsize=21, color=GREY, va="top")
ax = fig.add_axes([0.08, 0.33, 0.84, 0.31])
bars = [("Hesselø", 313, LIGHT, INK), ("Nordsøen Midt", 167, INK, INK),
        ("Nordsøen Syd*", 75, ACCENT, ACCENT)]
for i, (name, val, col, txt) in enumerate(bars):
    y = 2 - i
    ax.barh(y, val, height=0.42, color=col)
    ax.text(0, y + 0.3, name, fontsize=24, color=INK, fontweight="bold", va="bottom")
    ax.text(val + 6, y, f"{'≈' if name.startswith('Nordsøen Syd') else ''}{val}",
            fontsize=28, color=txt, fontweight="bold", va="center")
ax.set_xlim(0, 360)
ax.set_ylim(-0.4, 2.95)
ax.axis("off")
fig.text(0.08, 0.29, "In a low-price scenario, Nordsøen Midt’s cap runs out\nin July 2047. Hesselø’s never does.",
         fontsize=23, color=INK, va="top", linespacing=1.35)
fig.text(0.08, 0.135, "*Next tender, bids due Oct 2028: DKK 6.6bn cap over 20 years of the DEA’s output estimate.",
         fontsize=15.5, color=GREY, va="top")
pages.append(fig)

# ---------------------------------------------------------------- page 4
fig = new_page(4, "What it means")
headline(fig, "For the next round,\ncost of capital and\nprice risk decide bids")
fig.text(0.08, 0.665, "Nordsøen Syd’s cap is under half of Nordsøen Midt’s.\nBidders will have to price low power prices explicitly.",
         fontsize=22, color=INK, va="top", linespacing=1.35)
fig.add_artist(plt.Line2D([0.08, 0.92], [0.555, 0.555], color=LIGHT, lw=1.2))
fig.text(0.08, 0.525, "HOW I BUILT IT", fontsize=17, color=GREY, fontweight="bold", va="top")
steps = ["Contract rules from the tender documents",
         "20 years of hourly wind, 15 MW turbine",
         "Danish power prices and DEA price outlook",
         "Monthly 30-year cash-flow model in Python"]
for i, s in enumerate(steps):
    fig.text(0.08, 0.48 - i * 0.052, f"{i + 1}   {s}", fontsize=23, color=INK, va="top")
fig.text(0.08, 0.235, "Full one-pager, model and code", fontsize=20, color=GREY, va="top")
fig.text(0.08, 0.2, "github.com/fergal567/danish-offshore-cfd-bid-model",
         fontsize=22, color=ACCENT, fontweight="bold", va="top")
fig.text(0.08, 0.135, "Independent student analysis from public data. Not affiliated with Vattenfall or the DEA.",
         fontsize=14, color=GREY, va="top")
pages.append(fig)

with PdfPages(OUT / "linkedin_carousel.pdf") as pdf:
    for i, fig in enumerate(pages, 1):
        pdf.savefig(fig)
        fig.savefig(OUT / f"carousel_p{i}.png", dpi=100)
        plt.close(fig)
print("written:", OUT / "linkedin_carousel.pdf")
