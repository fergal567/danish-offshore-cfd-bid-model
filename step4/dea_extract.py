"""Extract offshore-wind datasheet values from the DEA Technology Data Excel.

The DEA workbook ("Data sheet for Electricity and district heat production",
https://ens.dk/node/3449) has one sheet per technology. Each datasheet has:
  - a row whose first cell is 'year' (column years: 2020/2021, 2025, 2030, ...),
  - a row whose first cell is 'est' (ctrl / lower / upper / note / ref),
  - one row per parameter, label in column A.

Usage (PowerShell, from the repo root):
    python step4/dea_extract.py "step4/data/technology_data_for_el_and_dh_-_0019.xlsx"            (lists sheets)
    python step4/dea_extract.py "step4/data/technology_data_for_el_and_dh_-_0019.xlsx" --sheet "21 Offshore Wind AC Fixed" --year 2030

Writes step4/outputs/dea_offshore_<sheet>_<year>.csv (label, central, lower, upper,
note, ref) and prints the table. The .xlsx stays git-ignored; link the source instead.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import openpyxl


def _norm(x) -> str:
    return re.sub(r"\s+", " ", str(x)).strip() if x is not None else ""


def list_offshore_sheets(path: Path) -> list[str]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    return [s for s in wb.sheetnames if s.startswith("21")]


def read_sheet(path: Path, sheet: str):
    """Return (rows, header_years, header_est, notes) for one datasheet."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet]
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    years = est = None
    for i, r in enumerate(rows):
        first = _norm(r[0]).lower() if r else ""
        if first == "year" and years is None:
            years = r
        elif first == "est" and est is None:
            est = r
    if years is None or est is None:
        raise ValueError(f"No 'year'/'est' header rows found on sheet {sheet!r}")
    notes = []
    for r in rows:
        cells = [_norm(c) for c in (r or [])[:2] if _norm(c)]
        txt = " ".join(cells)
        # 2022 edition: "F. The cost includes…" in one cell; 2025 edition: "F" | "text" in two cells
        if re.match(r"^([A-Z]{1,2}[.:)]? |General note|[0-9]{1,2}\.? )", txt) and len(txt) > 4:
            notes.append(txt)
    return rows, years, est, notes


def columns_for_year(years, est, year: int) -> dict[str, int]:
    """Map 'central', 'lower', 'upper', 'note', 'ref' to column indices for one FID year.

    Lower/upper columns only exist for some years; if absent for `year`, they are None.
    """
    cols = {"central": None, "lower": None, "upper": None, "note": None, "ref": None}
    for j, (y, e) in enumerate(zip(years, est)):
        e_ = _norm(e).lower()
        try:
            y_ = int(float(y))
        except (TypeError, ValueError):
            y_ = None
        if y_ == year and e_ == "ctrl" and cols["central"] is None:
            cols["central"] = j
        elif y_ == year and e_ == "lower":
            cols["lower"] = j
        elif y_ == year and e_ == "upper":
            cols["upper"] = j
        elif e_ == "note" or _norm(y).lower() == "note":      # 2022 edition: est row; 2025 edition: year row
            cols["note"] = j
        elif e_ == "ref" or _norm(y).lower() == "ref":
            cols["ref"] = j
    if cols["central"] is None:
        raise ValueError(f"FID year {year} not found in the 'year' row: {years}")
    return cols


def extract(path: Path, sheet: str, year: int):
    rows, years, est, notes = read_sheet(path, sheet)
    cols = columns_for_year(years, est, year)
    first_data_col = min(j for j, e in enumerate(est) if _norm(e).lower() == "ctrl")
    out = []
    for r in rows:
        # parameter label = first text cell left of the data columns (col A or B)
        label = next((_norm(c) for c in r[:first_data_col] if _norm(c)), "") if r else ""
        if not label or label.lower() in ("year", "est", "cat"):
            continue
        val = r[cols["central"]] if cols["central"] < len(r) else None
        if not isinstance(val, (int, float)):
            continue
        def pick(k):
            j = cols[k]
            return r[j] if j is not None and j < len(r) else None
        out.append({
            "label": label,
            "central": val,
            "lower": pick("lower"),
            "upper": pick("upper"),
            "note": pick("note"),
            "ref": pick("ref"),
        })
    return out, notes, [_norm(y) for y in years], [_norm(e) for e in est]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx", type=Path)
    ap.add_argument("--sheet", default=None, help="sheet name; default: list '21 ...' sheets")
    ap.add_argument("--year", type=int, default=2030, help="FID-year column (default 2030)")
    ap.add_argument("--outdir", type=Path, default=Path(__file__).parent / "outputs")
    a = ap.parse_args()

    if a.sheet is None:
        print("Offshore sheets:", list_offshore_sheets(a.xlsx))
        return
    data, notes, years, est = extract(a.xlsx, a.sheet, a.year)
    print("year row:", years)
    print("est  row:", est)
    for d in data:
        print(f"{d['label'][:70]:70s} {d['central']!s:>22} {d['lower']!s:>22} {d['upper']!s:>22}  {d['note'] or ''}")
    print("\nNotes:")
    for n in notes:
        print(" ", n)
    a.outdir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9]+", "_", a.sheet).strip("_")
    f = a.outdir / f"dea_{safe}_{a.year}.csv"
    with f.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["label", "central", "lower", "upper", "note", "ref"])
        w.writeheader()
        w.writerows(data)
    print("\nwrote", f)


if __name__ == "__main__":
    main()
