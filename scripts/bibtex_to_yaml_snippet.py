#!/usr/bin/env python3
"""
Convert one or more BibTeX entries into YAML snippets suitable for
pasting into publications.yaml (under the `publications:` list).

Usage:
    python bibtex_to_yaml_snippet.py entry.bib

Where entry.bib contains one or more BibTeX entries (e.g., copied
from Google Scholar, DBLP, or a publisher's DOI page).
"""

import sys
import os
import re
import argparse

try:
    import bibtexparser
except ImportError:
    print("Error: bibtexparser is not installed.", file=sys.stderr)
    print("Install it with: pip install bibtexparser", file=sys.stderr)
    sys.exit(1)


# ----------------- LaTeX -> Unicode helpers ----------------- #

def latex_to_unicode(text: str) -> str:
    """
    Convert common LaTeX accent commands to Unicode, and strip braces.
    Examples:
      'Poincar{\\\'e}' -> 'Poincaré'
      'Garc{\\\'i}a'  -> 'García'
    """
    if not text:
        return ""

    s = str(text)

    # Replace accent commands like \'{e}, \"{o}, \c{c}, etc.
    # Handles both \'{e} and \\'e styles via optional braces.
    accent_map = {
        ("'", "a"): "á", ("'", "e"): "é", ("'", "i"): "í",
        ("'", "o"): "ó", ("'", "u"): "ú", ("'", "y"): "ý",
        ("", "a"): "à", ("", "e"): "è", ("", "i"): "ì",
        ("", "o"): "ò", ("", "u"): "ù",
        ("^", "a"): "â", ("^", "e"): "ê", ("^", "i"): "î",
        ("^", "o"): "ô", ("^", "u"): "û",
        ('"', "a"): "ä", ('"', "e"): "ë", ('"', "i"): "ï",
        ('"', "o"): "ö", ('"', "u"): "ü", ('"', "y"): "ÿ",
        ("~", "a"): "ã", ("~", "n"): "ñ", ("~", "o"): "õ",
        ("c", "c"): "ç",
    }

    def accent_replacer(match):
        cmd = match.group(1)   # accent command (', ", , ^, ~, c)
        ch = match.group(2)    # base letter
        base = ch.lower()
        rep = accent_map.get((cmd, base))
        if not rep:
            return ch  # fallback: just return character
        return rep.upper() if ch.isupper() else rep

    # Match \'{e}, \'{E}, \"{o}, \c{c}, etc. Optional braces.
    pattern = re.compile(r"\\([\'\"\^~c])\{?([A-Za-z])\}?")
    s = pattern.sub(accent_replacer, s)

    # Other common LaTeX sequences
    replacements = {
        r"\\ss": "ß",
        r"\\ae": "æ",
        r"\\AE": "Æ",
        r"\\oe": "œ",
        r"\\OE": "Œ",
        r"\\aa": "å",
        r"\\AA": "Å",
        r"\\o": "ø",
        r"\\O": "Ø",
        r"\\&": "&",
    }
    for pat, repl in replacements.items():
        s = re.sub(pat, repl, s)

    # Remove remaining braces (mostly used for capitalization in BibTeX)
    s = s.replace("{", "").replace("}", "")

    return s


def clean_text(text: str) -> str:
    """Convert LaTeX accents to Unicode, normalize whitespace."""
    if not text:
        return ""
    text = latex_to_unicode(text)
    return " ".join(str(text).split())


def yaml_str(s: str) -> str:
    """
    Return a YAML-safe single-quoted string.
    Handles None, escapes single quotes by doubling them.
    """
    if s is None:
        s = ""
    s = str(s)
    s = s.replace("'", "''")
    return f"'{s}'"


# ----------------- Type / author / metadata helpers ----------------- #

def map_type(entry_type: str, entry: dict) -> str:
    """
    Map BibTeX entry types to our categories:
    journal, conference, workshop, book-chapter, preprint, other.
    """
    if not entry_type:
        return "other"
    t = entry_type.lower()

    # Heuristic for preprints (arXiv, etc.)
    journal = (entry.get("journal") or "").lower()
    if "arxiv" in journal or "preprint" in journal:
        return "preprint"

    if t == "article":
        return "journal"
    if t in ("inproceedings", "conference", "proceedings"):
        return "conference"
    if t in ("incollection", "inbook"):
        return "book-chapter"
    if t in ("proceedings", "collection"):
        return "conference"
    if t in ("phdthesis", "mastersthesis"):
        return "other"
    if t in ("unpublished", "manual", "techreport"):
        return "other"
    return "other"


def parse_name_list(field_value: str) -> str:
    """
    Parse a BibTeX name list field (author/editor) into
    'Last, F., Last2, F2.' format.
    Handles multi-line DBLP/TeX "X and\n  Y and\n  Z" style.
    """
    if not field_value:
        return ""

    # Convert LaTeX and collapse all whitespace (newlines, tabs -> spaces)
    field_value = latex_to_unicode(field_value)
    field_value = " ".join(field_value.split())

    # Now "Hank Childs and David Pugmire and Sean Ahern ..."
    people_raw = [a.strip() for a in field_value.split(" and ") if a.strip()]
    formatted = []

    for person in people_raw:
        # Try "Last, First" form first
        if "," in person:
            parts = [p.strip() for p in person.split(",", 1)]
            last = parts[0]
            first = parts[1] if len(parts) > 1 else ""
        else:
            # Assume "First Middle Last"
            parts = person.split()
            if len(parts) == 1:
                last = parts[0]
                first = ""
            else:
                last = parts[-1]
                first = " ".join(parts[:-1])

        first_initial = first[0] + "." if first else ""
        last = last.strip()
        if last and first_initial:
            formatted.append(f"{last}, {first_initial}")
        elif last:
            formatted.append(last)
        else:
            formatted.append(person)

    if len(formatted) > 20:
        return ", ".join(formatted[:20]) + ", et al."
    return ", ".join(formatted)


def generate_id(title: str, year: str, authors_str: str, editors_str: str = "") -> str:
    """
    Generate an ID like lastname2024keyword based on first author
    (or editor if no authors), year, and first >=4-letter word in title.
    """
    base_str = authors_str or editors_str
    first_author = "author"
    if base_str:
        first_part = base_str.split(",")[0].strip()  # "Childs" from "Childs, H."
        first_author = re.sub(r"[^a-zA-Z]", "", first_part).lower() or "author"

    title_words = re.findall(r"\b[a-zA-Z]{4,}\b", (title or "").lower())
    keyword = title_words[0] if title_words else "paper"

    year_str = str(year) if year else "0000"

    return f"{first_author}{year_str}{keyword}"


def extract_venue(entry: dict) -> str:
    """
    Extract a venue name from a BibTeX entry:
    prefer journal, then booktitle, then publisher.
    """
    venue = (
        entry.get("journal")
        or entry.get("booktitle")
        or entry.get("publisher")
        or ""
    )
    return clean_text(venue) or "Unknown Venue"


def extract_year(entry: dict) -> str:
    """Get the year as a string; non-numeric becomes '0'."""
    year = entry.get("year", "")
    year = str(year).strip()
    if not year.isdigit():
        return "0"
    return year


def normalize_doi(doi: str) -> str:
    """
    Normalize DOI:
    - Extract the core 10.xxxx/... pattern from any surrounding URL/prefix.
    - Lowercase the result.
    """
    if not doi:
        return ""
    doi = doi.strip()

    m = re.search(r"10\.\d{4,9}/\S+", doi, flags=re.IGNORECASE)
    if m:
        return m.group(0).lower()

    if doi.lower().startswith("doi:"):
        return doi[4:].strip().lower()

    return doi.lower()


def extract_doi_and_url(entry: dict) -> (str, str):
    """Get DOI and paper_url from BibTeX entry."""
    doi = entry.get("doi", "") or ""
    doi = normalize_doi(doi)

    url = entry.get("url", "") or ""
    url = url.strip()

    # If no URL but we have DOI, construct DOI URL
    if not url and doi:
        url = f"https://doi.org/{doi}"

    return doi, url


# ----------------- Main conversion ----------------- #

def entry_to_publication(entry: dict) -> dict:
    entry_type = entry.get("ENTRYTYPE", "")
    raw_title = entry.get("title", "Untitled")
    title = clean_text(raw_title)

    authors_raw = entry.get("author", "")
    editors_raw = entry.get("editor", "")

    authors = parse_name_list(authors_raw)
    editors = parse_name_list(editors_raw)

    venue = extract_venue(entry)
    year = extract_year(entry)
    pub_type = map_type(entry_type, entry)
    doi, url = extract_doi_and_url(entry)

    pub_id = generate_id(title, year, authors, editors)

    return {
        "id": pub_id,
        "title": title,
        "authors": authors or "Authors not available",
        "editors": editors or None,
        "venue": venue,
        "year": year,
        "type": pub_type,
        "doi": doi or None,
        "paper_url": url or None,
    }


def print_yaml_snippet(pub: dict) -> None:
    """
    Print a YAML block for a single publication, indented so you can paste
    directly under `publications:` in publications.yaml.
    """
    print("  - id:", yaml_str(pub["id"]))
    print("    title:", yaml_str(pub["title"]))
    print("    authors:", yaml_str(pub["authors"]))

    if pub["editors"]:
        print("    editors:", yaml_str(pub["editors"]))

    print("    venue:", yaml_str(pub["venue"]))
    print(f"    year: {pub['year']}")
    print(f"    type: {pub['type']}  # journal, conference, workshop, book-chapter, preprint, other")

    if pub["doi"]:
        print("    doi:", yaml_str(pub["doi"]))
    else:
        print("    # doi: ''")

    if pub["paper_url"]:
        print("    paper_url:", yaml_str(pub["paper_url"]))
    else:
        print("    # paper_url: ''  # Add direct link to paper if available")

    print("    # summary: ''  # Optional one-sentence summary")
    print("    # image:", yaml_str(pub["id"] + ".jpg"), "# Optional image in images/papers/")
    print()  # blank line between entries


def main():
    parser = argparse.ArgumentParser(
        description="Convert BibTeX entries to YAML snippets for publications.yaml"
    )
    parser.add_argument("bibfile", help="Input BibTeX file (one or more entries)")
    args = parser.parse_args()

    if not os.path.isfile(args.bibfile):
        print(f"Error: file not found: {args.bibfile}", file=sys.stderr)
        sys.exit(1)

    with open(args.bibfile, "r", encoding="utf-8") as f:
        bib_str = f.read()

    parser_obj = bibtexparser.bparser.BibTexParser(common_strings=True)
    parser_obj.ignore_nonstandard_types = False
    bib_db = bibtexparser.loads(bib_str, parser=parser_obj)

    entries = bib_db.entries or []
    if not entries:
        print("No BibTeX entries found.", file=sys.stderr)
        sys.exit(1)

    # For each entry in the file, print a YAML snippet
    for entry in entries:
        pub = entry_to_publication(entry)
        print_yaml_snippet(pub)


if __name__ == "__main__":
    main()
