"""LinkedIn document carousel for Project 1: 4 pages, 1080 x 1350 px (4:5).

Numbers are from step5/bid_calibration_memo.md (re-run 16 Nov 2026 after the external review), real 2026 DKK.
The Nordsøen Syd figure is the DKK 6.6bn net cap (Annex F 11.5.2, 2025 prices)
spread over 20 years of the DEA interim estimate of 4,483 GWh/yr (App 3 Table 1).

Locator map on page 1: coastline from basemap-data-hires (GSHHG via basemap; pip install basemap
basemap-data-hires). Site positions are approximate: Nordsøen Midt = the model's representative
point (56.00 N, 7.55 E, Asm), Hesselø = Global Energy Monitor wiki (approx.), Nordsøen Syd = my
estimate south of Nordsøen Midt (Asm). Replace with the step-2 / Appendix 2 coordinates if available.

Run from the repo root:  python summary/make_carousel.py
Writes summary/linkedin_carousel.pdf and a PNG preview per page.
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.basemap import Basemap

OUT = Path(__file__).resolve().parent

INK = "#1a1a1a"
GREY = "#6b6b6b"
LIGHT = "#cfcfcf"
ACCENT = "#a8432a"
SERIF = ["Liberation Serif", "Times New Roman", "DejaVu Serif"]   # fallbacks are metric-compatible
SANS = ["Liberation Sans", "Arial", "DejaVu Sans"]

W, H = 10.8, 13.5  # inches at 100 dpi = 1080 x 1350 px
PAGES = 4
plt.rcParams.update({"font.family": SANS, "axes.edgecolor": INK,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "white", "savefig.facecolor": "white"})


def new_page(n):
    fig = plt.figure(figsize=(W, H))
    fig.add_artist(plt.Line2D([0.08, 0.92], [0.075, 0.075], color=LIGHT, lw=1.2))
    fig.text(0.08, 0.045, "Fergal Israel  ·  Independent analysis", fontsize=19, color=GREY)
    fig.text(0.92, 0.045, f"{n}/{PAGES}", fontsize=19, color=GREY, ha="right")
    return fig


def headline(fig, text, y=0.91, size=52):
    # One line at a time, so every line gets the same spacing.
    step = size * 1.18 / 72 / H
    for i, line in enumerate(text.split("\n")):
        fig.text(0.08, y - i * step, line, fontsize=size, color=INK, family=SERIF,
                 fontweight="bold", va="top")


SITES_MAP = [  # (label, lat, lon, filled) – approximate positions, see docstring
    ("Midt", 56.00, 7.55, True),
    ("Hesselø", 56.42, 11.93, True),
    ("Syd", 55.65, 7.45, False),
]


def locator_map(fig, rect):
    """Small map of Denmark with the three tender sites (approximate)."""
    ax = fig.add_axes(rect)
    m = Basemap(projection="merc", llcrnrlon=5.4, urcrnrlon=13.0, llcrnrlat=54.5, urcrnrlat=57.85,
                resolution="i", ax=ax)
    m.drawmapboundary(fill_color="white", linewidth=0)
    m.drawcoastlines(linewidth=0.9, color="#9c958c")
    for label, lat, lon, filled in SITES_MAP:
        x, y = m(lon, lat)
        ax.scatter(x, y, s=170, zorder=3, linewidths=2.5,
                   facecolor=ACCENT if filled else "white", edgecolor=ACCENT)
        if label == "Hesselø":
            off, ha, va = (0, 14), "center", "bottom"
        else:
            off, ha, va = (-14, 0), "right", "center"
        ax.annotate(label, (x, y), xytext=off, textcoords="offset points",
                    ha=ha, va=va, fontsize=17, color=INK, fontweight="bold")
    ax.set_axis_off()
    return ax


pages = []

# ---------------------------------------------------------------- page 1
fig = new_page(1)
headline(fig, "Hesselø’s bid is near\nbreak-even in my model.\nNordsøen Midt’s is not")
fig.text(0.08, 0.70, "Rebuilt from public data: tender documents,\nhourly wind, DEA cost data, Danish tax rules.",
         fontsize=23, color=GREY, va="top", linespacing=1.35)

ax = fig.add_axes([0.08, 0.15, 0.84, 0.47])
sites = [("Nordsøen Midt", 504, 713), ("Hesselø", 542, 577)]
for i, (name, awarded, be) in enumerate(sites):
    y = 1 - i
    ax.plot([awarded, be], [y, y], color=ACCENT, lw=11, solid_capstyle="butt", zorder=1)
    ax.scatter(awarded, y, s=1100, facecolor="white", edgecolor=INK, lw=4, zorder=2)
    ax.scatter(be, y, s=1100, color=INK, zorder=2)
    ax.text(awarded + 8, y - 0.2, f"{awarded}", ha="right", va="top", fontsize=34, color=INK)
    ax.text(be - 8, y - 0.2, f"{be}", ha="left", va="top", fontsize=34, color=INK, fontweight="bold")
    ax.text(480, y + 0.2, name, ha="left", va="bottom", fontsize=30, color=INK, fontweight="bold")
    ax.text(be + 18, y, f"+{be - awarded}", ha="left", va="center", fontsize=36, color=ACCENT,
            fontweight="bold")
ax.set_xlim(480, 1150)
ax.set_ylim(-0.6, 1.6)
ax.axis("off")
locator_map(fig, [0.58, 0.40, 0.34, 0.23])
fig.text(0.08, 0.115, "○ awarded price    ● break-even, base case    (DKK/MWh)",
         fontsize=21, color=GREY)
pages.append(fig)

# ---------------------------------------------------------------- page 2
fig = new_page(2)
headline(fig, "What each price\nneeds to break even")
items = [
    ("4.5 % · 3.4 %", "return, real after tax (Hesselø · Nordsøen Midt;\nmy base 5.0 %; Vattenfall’s wind range 3.6–5.3 %)"),
    ("7 % · 20 % lower", "build cost than my estimate\nfrom DEA data"),
    ("+6 % · +20 % wind", "more output than my median estimate"),
]
y = 0.70
for big, small in items:
    fig.text(0.08, y, big, fontsize=58, color=ACCENT, family=SERIF, fontweight="bold", va="top")
    fig.text(0.08, y - 0.07, small, fontsize=24, color=INK, va="top", linespacing=1.3)
    y -= 0.175
fig.add_artist(plt.Line2D([0.08, 0.92], [0.2, 0.2], color=INK, lw=1.5))
fig.text(0.08, 0.18, "Nordsøen Midt must also build a 53 km land cable.",
         fontsize=24, color=INK, fontweight="bold", va="top")
fig.text(0.08, 0.135, "Costed from DEA data, it cuts the implied return from 4.2 % to 3.4 %.",
         fontsize=19, color=GREY, va="top")
pages.append(fig)

# ---------------------------------------------------------------- page 3
fig = new_page(3)
headline(fig, "The state’s payment\ncap is much tighter\nat Nordsøen Midt")
fig.text(0.08, 0.665, "Average top-up the cap can fund over 20 years, DKK/MWh",
         fontsize=21, color=GREY, va="top")
ax = fig.add_axes([0.08, 0.33, 0.84, 0.31])
bars = [("Hesselø", 324, LIGHT, INK), ("Nordsøen Midt", 173, INK, INK),
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
fig.text(0.08, 0.29, "In my low-price stress case, Nordsøen Midt’s cap runs\nout around 2048. Hesselø’s never does.",
         fontsize=23, color=INK, va="top", linespacing=1.35)
fig.text(0.08, 0.15, "*Next tender (bids due Oct 2028): DKK 6.6bn cap\nover 20 years of the DEA’s output estimate.",
         fontsize=20, linespacing=1.3, color=GREY, va="top")
pages.append(fig)

# ---------------------------------------------------------------- page 4
fig = new_page(4)
headline(fig, "For the next round,\nreturn requirements and\nprice risk decide bids")
fig.text(0.08, 0.665, "Nordsøen Syd’s cap is under half of Nordsøen Midt’s.\nBidders will have to price low power prices explicitly.",
         fontsize=22, color=INK, va="top", linespacing=1.35)
fig.add_artist(plt.Line2D([0.08, 0.92], [0.555, 0.555], color=LIGHT, lw=1.2))
fig.text(0.08, 0.525, "How I built it", fontsize=22, color=INK, fontweight="bold", va="top")
steps = ["Contract rules from the tender documents",
         "20 years of hourly wind, 15 MW turbine",
         "Danish power prices and DEA price outlook",
         "Monthly 30-year cash-flow model in Python"]
for i, s in enumerate(steps):
    fig.text(0.08, 0.48 - i * 0.052, f"{i + 1}   {s}", fontsize=23, color=INK, va="top")
fig.text(0.08, 0.27, "Full one-pager, model and code", fontsize=20, color=GREY, va="top")
fig.text(0.08, 0.235, "github.com/fergal567/danish-offshore-cfd-bid-model",
         fontsize=22, color=ACCENT, fontweight="bold", va="top")
fig.text(0.08, 0.145, "Independent analysis from public data.\nNot affiliated with Vattenfall or the DEA.",
         fontsize=19, linespacing=1.3, color=GREY, va="top")
pages.append(fig)

with PdfPages(OUT / "linkedin_carousel.pdf") as pdf:
    for i, fig in enumerate(pages, 1):
        pdf.savefig(fig)
        fig.savefig(OUT / f"carousel_p{i}.png", dpi=100)
        plt.close(fig)
print("written:", OUT / "linkedin_carousel.pdf")
