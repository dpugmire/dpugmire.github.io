#!/usr/bin/env python3
"""
yaml_to_bibtex.py

Convert publications.yaml (from your ORCID/Scholar script) into publications.bib.

Usage:
    python yaml_to_bibtex.py              # uses publications.yaml -> publications.bib
    python yaml_to_bibtex.py input.yaml   # input -> publications.bib
    python yaml_to_bibtex.py input.yaml output.bib
"""

import sys
import re
from pathlib import Path

import yaml  # pip install pyyaml


def escape_latex(s: str) -> str:
    """Minimal LaTeX escaping for BibTeX fields."""
    if not s:
        return s
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "_": r"\_",
        "#": r"\#",
        "$": r"\$",
        "{": r"\{",
        "}": r"\}",
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    return s


def authors_yaml_to_bibtex(authors: str) -> str:
    """
    Convert authors string like:
        "Wang, X., Choi, J., Kurihaya, T., ..."
    into BibTeX 'author' list:
        "Wang, X. and Choi, J. and Kurihaya, T. and ..."
    """
    if not authors or authors.strip().lower().startswith("authors not available"):
        return ""

    parts = [p.strip() for p in authors.split(",")]
    names = []
    i = 0
    while i < len(parts):
        part = parts[i]
        if part.lower().startswith("et al"):
            break

        # If next token looks like initials ("X." or "X. Y.")
        if i + 1 < len(parts) and re.search(r"\.$", parts[i + 1].strip()):
            name = f"{part}, {parts[i + 1].strip()}"
            i += 2
        else:
            # Single token, just treat as a surname or already-complete name
            name = part
            i += 1

        if name:
            names.append(name)

    if not names:
        return authors  # fall back to original

    return " and ".join(names)


def map_type_to_bibtype(pub_type: str) -> str:
    """Map YAML 'type' to BibTeX entry type."""
    t = (pub_type or "").lower()
    if t == "journal":
        return "article"
    if t in ("conference", "workshop"):
        return "inproceedings"
    if t == "book-chapter":
        return "incollection"
    if t == "preprint":
        return "article"
    return "misc"


def main():
    # --- Parse CLI args ---
    if len(sys.argv) == 1:
        in_path = Path("publications.yaml")
        out_path = Path("publications.bib")
    elif len(sys.argv) == 2:
        in_path = Path(sys.argv[1])
        out_path = Path("publications.bib")
    else:
        in_path = Path(sys.argv[1])
        out_path = Path(sys.argv[2])

    if not in_path.exists():
        print(f"❌ Input file not found: {in_path}")
        sys.exit(1)

    # --- Load YAML ---
    with in_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    pubs = data.get("publications", [])
    if not isinstance(pubs, list):
        print("❌ publications.yaml does not contain a 'publications' list")
        sys.exit(1)

    print(f"Loaded {len(pubs)} publications from {in_path}")

    # --- Convert to BibTeX ---
    entries = []
    for pub in pubs:
        try:
            pid = pub.get("id", "").strip()
            title = pub.get("title", "").strip()
            authors = pub.get("authors", "").strip()
            venue = pub.get("venue", "").strip()
            year = str(pub.get("year", "")).strip()
            ptype = pub.get("type", "other").strip().lower()
            doi = (pub.get("doi") or "").strip()
            url = (pub.get("paper_url") or "").strip()

            if not pid:
                # generate a fallback key
                pid = "pub" + re.sub(r"\W+", "", title.lower())[:16]

            bibtype = map_type_to_bibtype(ptype)
            author_field = authors_yaml_to_bibtex(authors)

            # Basic fields (with LaTeX escaping)
            title_b = escape_latex(title)
            venue_b = escape_latex(venue)
            author_b = escape_latex(author_field)

            # Decide whether venue goes in 'journal' vs 'booktitle' vs 'howpublished'
            fields = []
            fields.append(f"  title   = {{{title_b}}}")
            if author_b:
                fields.append(f"  author  = {{{author_b}}}")
            if year and year.isdigit():
                fields.append(f"  year    = {{{year}}}")

            if bibtype == "article":
                if venue_b:
                    fields.append(f"  journal = {{{venue_b}}}")
            elif bibtype in ("inproceedings", "incollection"):
                if venue_b:
                    fields.append(f"  booktitle = {{{venue_b}}}")
            else:  # misc or other
                if venue_b:
                    fields.append(f"  howpublished = {{{venue_b}}}")

            if doi:
                fields.append(f"  doi     = {{{escape_latex(doi)}}}")
            if url:
                fields.append(f"  url     = {{{escape_latex(url)}}}")

            # Add a keyword for category so biblatex can filter:
            #   journal, conference, workshop, book-chapter, preprint, other
            if ptype:
                fields.append(f"  keywords = {{{ptype}}}")

            entry = "@{bibtype}{{{key},\n{fields}\n}}".format(
                bibtype=bibtype,
                key=pid,
                fields=",\n".join(fields),
            )
            entries.append(entry)

        except Exception as e:
            print(f"⚠️ Error converting publication with id={pub.get('id')}: {e}")
            continue

    # --- Write .bib file ---
    with out_path.open("w", encoding="utf-8") as f:
        f.write("% Auto-generated from publications.yaml\n")
        f.write(f"% {in_path}\n\n")
        for e in entries:
            f.write(e)
            f.write("\n\n")

    print(f"✅ Wrote {len(entries)} BibTeX entries to {out_path}")


if __name__ == "__main__":
    main()
