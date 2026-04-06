#!/usr/bin/env python3
"""
yaml_to_publications_by_type_tex.py

Read publications.yaml (from your ORCID/Scholar script) and generate
one LaTeX snippet per publication type:

  - publications_journal.tex
  - publications_conference.tex
  - publications_workshop.tex
  - publications_bookchapter.tex
  - publications_other.tex

Each file contains ONLY \\item lines (no \\begin{enumerate}/\\end{enumerate}),
so you can wrap them in enumerate environments in cv.tex as you prefer.

Usage:
    python yaml_to_publications_by_type_tex.py
    python yaml_to_publications_by_type_tex.py input.yaml
"""

import sys
from pathlib import Path
import unicodedata
import yaml  # pip install pyyaml


# ----------------- Helpers ----------------- #

def escape_latex(s: str) -> str:
    """Minimal LaTeX escaping for text fields."""
    if not s:
        return ""
    s = unicodedata.normalize("NFC", s)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "_": r"\_",
        "#": r"\#",
        "$": r"\$",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    return s


def sort_key(pub):
    """Sort by year (desc), then title (asc)."""
    year = pub.get("year", "")
    try:
        yval = int(str(year))
    except Exception:
        yval = -9999  # unknown years go last
    title = (pub.get("title") or "")
    return (-yval, title.lower())


def make_item_line(pub):
    """Create one \\item line (without the leading '\\item') for a publication."""
    title = (pub.get("title") or "").strip()
    authors = (pub.get("authors") or "").strip()
    venue = (pub.get("venue") or "").strip()
    year = str(pub.get("year", "")).strip()
    doi = (pub.get("doi") or "").strip()
    paper_url = (pub.get("paper_url") or "").strip()

    title_tex = escape_latex(title)
    authors_tex = escape_latex(authors)
    venue_tex = escape_latex(venue)

    # Build URL (prefer explicit paper_url, else DOI)
    url = ""
    if paper_url:
        url = paper_url
    elif doi:
        url = f"https://doi.org/{doi}"

    pieces = []
    if authors_tex:
        pieces.append(f"{authors_tex}.")
    if title_tex:
        pieces.append(f"\\emph{{“{title_tex},”}}")
    if venue_tex:
        pieces.append(f"\\textit{{{venue_tex}}}")
    if year:
        pieces.append(year)

    line = " ".join(pieces)

    if url:
        url_escaped = escape_latex(url)
        if doi:
            doi_tex = escape_latex(doi)
            line += f" DOI: \\href{{{url_escaped}}}{{{doi_tex}}}."
        else:
            line += f" \\href{{{url_escaped}}}{{link}}."

    return line


def write_tex_for_category(pubs, filename: Path):
    """Write \\item lines for the given list of pubs to filename."""
    pubs_sorted = sorted(pubs, key=sort_key)

    lines = []
    lines.append("% Auto-generated from publications.yaml")
    lines.append("% Do not edit by hand; edit the YAML instead.")

    for pub in pubs_sorted:
        item_line = make_item_line(pub)
        lines.append(f"\\item {item_line}")

    with filename.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        f.write("\n")


# ----------------- Main ----------------- #

def main():
    # --- CLI args ---
    if len(sys.argv) == 1:
        in_path = Path("publications.yaml")
    else:
        in_path = Path(sys.argv[1])

    if not in_path.exists():
        print(f"❌ Input file not found: {in_path}")
        sys.exit(1)

    # --- Load YAML ---
    with in_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    pubs = data.get("publications", [])
    if not isinstance(pubs, list):
        print("❌ YAML does not contain a 'publications' list")
        sys.exit(1)

    print(f"Loaded {len(pubs)} publications from {in_path}")

    # Buckets by type
    buckets = {
        "journal": [],
        "conference": [],
        "workshop": [],
        "book-chapter": [],
        "other": [],  # catch-all
    }

    for pub in pubs:
        ptype = (pub.get("type") or "other").strip().lower()
        if ptype not in buckets:
            ptype = "other"
        buckets[ptype].append(pub)

    # Output file names
    out_files = {
        "journal": Path("publications_journal.tex"),
        "conference": Path("publications_conference.tex"),
        "workshop": Path("publications_workshop.tex"),
        "book-chapter": Path("publications_bookchapter.tex"),
        "other": Path("publications_other.tex"),
    }

    for ptype, plist in buckets.items():
        fname = out_files[ptype]
        print(f"  - {ptype}: {len(plist)} -> {fname}")
        write_tex_for_category(plist, fname)

    print("✅ Finished generating per-type publication .tex snippets")


if __name__ == "__main__":
    main()
