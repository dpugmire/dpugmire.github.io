#!/usr/bin/env python3
"""
Convert a BibTeX export into publications.yaml
for the academic website.

Features:
- Parses BibTeX from Google Scholar (or other sources).
- Uses a REQUIRED custom 'pubtype' field in each BibTeX entry.
- Allowed pubtype values (case-insensitive):
    journal, conference, workshop, techreport, abstract, bookchapter, preprint, other
- Extracts title, authors, venue, year, type.
- Converts common LaTeX accent sequences (e.g., Poincar{\'e} -> Poincaré).
- Extracts DOI and URL from BibTeX when present.
- Extracts abstract when present (BibTeX fields: 'abstract' and common aliases).
- If DOI or URL are missing, optionally queries Crossref by title
  (+ first author + year) to fill them in when possible.
- Carries through BibTeX 'note' (e.g., "Best Short Paper Award") into YAML.
- Emits safely quoted YAML using single quotes.

Usage:
    python bibtex_to_yaml.py input.bib > publications.yaml
    python bibtex_to_yaml.py input.bib -o publications.yaml
"""

import sys
import os
import re
import argparse
from datetime import datetime
import time

try:
    import bibtexparser
except ImportError:
    print("Error: bibtexparser is not installed.", file=sys.stderr)
    print("Install it with: pip install bibtexparser", file=sys.stderr)
    sys.exit(1)

try:
    import requests
    HAVE_REQUESTS = True
except ImportError:
    HAVE_REQUESTS = False
    print("Warning: requests is not installed; Crossref lookup will be disabled.",
          file=sys.stderr)


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
        cmd = match.group(1)   # accent command (', ", ^, ~, c)
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

    # Remove remaining braces (used for capitalization, etc.)
    s = s.replace("{", "").replace("}", "")

    return s


def clean_text(text: str) -> str:
    """Convert LaTeX accents to Unicode, normalize whitespace."""
    if not text:
        return ""
    text = latex_to_unicode(text)
    return " ".join(str(text).split())


def clean_abstract(text: str) -> str:
    """
    Clean abstract text:
    - Convert LaTeX accents
    - Normalize whitespace
    This intentionally produces a single-paragraph string (good for YAML + web display).
    """
    if not text:
        return ""
    s = latex_to_unicode(text)
    # BibTeX abstracts are often line-wrapped; collapse to single spaces.
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s


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

def describe_entry(entry: dict) -> str:
    """Return a human-friendly label for error messages."""
    bib_id = entry.get("ID")
    if bib_id:
        return bib_id
    title = clean_text(entry.get("title", "")).strip()
    if title:
        if len(title) > 60:
            title = title[:57] + "..."
        return f"title '{title}'"
    return "<unknown entry>"


def map_pubtype(entry: dict) -> str:
    """
    Map BibTeX 'pubtype' field to our normalized categories.

    Allowed pubtype values (case-insensitive):
      journal, conference, workshop, techreport, abstract, bookchapter, preprint, other

    Returns canonical values:
      'journal', 'conference', 'workshop', 'techreport', 'abstract',
      'book-chapter', 'preprint', 'other'
    """
    raw = (entry.get("pubtype") or "").strip()
    if not raw:
        raise ValueError(
            f"BibTeX entry {describe_entry(entry)} is missing required 'pubtype' field. "
            "Expected one of: journal, conference, workshop, techreport, abstract, "
            "bookchapter, preprint, other."
        )

    t = raw.lower()

    mapping = {
        "journal": "journal",
        "conference": "conference",
        "conf": "conference",
        "workshop": "workshop",
        "ws": "workshop",
        "techreport": "techreport",
        "tech-report": "techreport",
        "technicalreport": "techreport",
        "techrep": "techreport",
        "abstract": "abstract",
        "abs": "abstract",
        "bookchapter": "book-chapter",
        "book-chapter": "book-chapter",
        "preprint": "preprint",
        "arxiv": "preprint",
        "other": "other",
    }

    if t not in mapping:
        raise ValueError(
            f"BibTeX entry {describe_entry(entry)} has unknown pubtype '{raw}'. "
            "Expected one of: journal, conference, workshop, techreport, abstract, "
            "bookchapter, preprint, other."
        )

    return mapping[t]


def parse_authors(author_field: str) -> str:
    """
    Parse a BibTeX author field into 'Last, F., Last2, F2.' format.
    Google Scholar exports authors as 'First Last and First2 Last2 ...'.
    Also converts LaTeX accents in names to Unicode.
    """
    if not author_field:
        return ""

    author_field = latex_to_unicode(author_field)

    authors_raw = [a.strip() for a in author_field.split(" and ") if a.strip()]
    formatted = []

    for a in authors_raw:
        # Try "Last, First" form first
        if "," in a:
            parts = [p.strip() for p in a.split(",", 1)]
            last = parts[0]
            first = parts[1] if len(parts) > 1 else ""
        else:
            # Assume "First Middle Last"
            parts = a.split()
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
            formatted.append(a)

    if len(formatted) > 20:
        return ", ".join(formatted[:20]) + ", et al."
    return ", ".join(formatted)


def generate_id(title: str, year: str, authors_str: str) -> str:
    """
    Generate an ID like lastname2024keyword based on first author,
    year, and first >=4-letter word in title.
    """
    first_author = "author"
    if authors_str:
        first_part = authors_str.split(",")[0].strip()  # "Wang" from "Wang, X."
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
    """Get the year as a string; non-numeric becomes '0' so sorting works."""
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


def extract_abstract(entry: dict) -> str:
    """
    Extract abstract text from BibTeX entry.

    Common fields seen in the wild:
      - abstract (non-standard but widely used)
      - annote (BibTeX standard-ish annotation field; sometimes used for abstracts)
      - annotation (rare alias)
    """
    raw = (
        entry.get("abstract")
        or entry.get("annote")
        or entry.get("annotation")
        or ""
    )
    raw = str(raw).strip()
    if not raw:
        return ""
    return clean_abstract(raw)


def crossref_lookup(title: str, authors_str: str, year: str) -> (str, str):
    """
    Query Crossref by title (+ first author + year) to find DOI and URL.

    Returns (doi, url) where either can be empty string if not found.

    If 'requests' is not available, this returns ("", "").
    """
    if not HAVE_REQUESTS:
        return "", ""

    query_parts = [title]

    if authors_str:
        first_author = authors_str.split(",")[0]
        query_parts.append(first_author)

    if year and year.isdigit() and year != "0":
        query_parts.append(year)

    query = " ".join(query_parts)
    params = {
        "query.bibliographic": query,
        "rows": 1,
        # "mailto": "you@example.com",
    }

    try:
        resp = requests.get("https://api.crossref.org/works", params=params, timeout=10)
        if not resp.ok:
            return "", ""

        items = resp.json().get("message", {}).get("items", [])
        if not items:
            return "", ""

        item = items[0]
        doi = normalize_doi(item.get("DOI", ""))
        url = item.get("URL", "") or ""

        # Throttle a bit so we don't hammer Crossref
        time.sleep(0.2)

        return doi, url
    except Exception:
        return "", ""


# ----------------- Conversion ----------------- #

def bibtex_to_publications(entries):
    """
    Convert BibTeX entries to our internal publication dict list.
    Uses BibTeX for DOI/URL where present, and Crossref to fill gaps.
    Also converts LaTeX accents in titles/venues/authors to Unicode.
    Requires a valid 'pubtype' field in each entry.
    """
    publications = []

    for entry in entries:
        raw_title = entry.get("title", "Untitled")
        title = clean_text(raw_title)

        authors_raw = entry.get("author", "")
        authors = parse_authors(authors_raw)

        venue = extract_venue(entry)
        year = extract_year(entry)

        # Determine pub type from required 'pubtype' field
        pub_type = map_pubtype(entry)

        # DOI / URL
        doi, url = extract_doi_and_url(entry)

        # Abstract (NEW)
        abstract = extract_abstract(entry) or None

        # Optional note (e.g. Best Paper Award)
        raw_note = entry.get("note") or ""
        note = clean_text(raw_note) if str(raw_note).strip() else None

        # Enrich with Crossref if DOI or URL missing
        if (not doi or not url) and HAVE_REQUESTS:
            cr_doi, cr_url = crossref_lookup(title, authors, year)
            if not doi and cr_doi:
                doi = cr_doi
            if not url and cr_url:
                url = cr_url

        pub_id = generate_id(title, year, authors)

        pub = {
            "id": pub_id,
            "title": title,
            "authors": authors or "Authors not available",
            "venue": venue,
            "year": year,
            "type": pub_type,
            "doi": doi or None,
            "paper_url": url or None,
            "note": note,          # may be None
            "abstract": abstract,  # may be None
        }

        publications.append(pub)

    # Sort: year desc, then title
    def sort_key(p):
        y = p.get("year", "")
        y_val = int(y) if str(y).isdigit() else 0
        return (-y_val, p.get("title", ""))

    publications.sort(key=sort_key)
    return publications


def write_yaml(publications, out_file=None):
    """
    Write publications to YAML in the format your website expects.
    If out_file is None, write to stdout.
    """
    out = sys.stdout if out_file is None else open(out_file, "w", encoding="utf-8")

    try:
        out.write("# publications.yaml\n")
        out.write("# Generated from BibTeX on "
                  f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        out.write("publications:\n")

        for pub in publications:
            type_label = pub["type"].upper()
            year = pub["year"]
            out.write(f"\n  # {type_label} - {year}\n")
            out.write(f"  - id: {yaml_str(pub['id'])}\n")
            out.write(f"    title: {yaml_str(pub['title'])}\n")
            out.write(f"    authors: {yaml_str(pub['authors'])}\n")
            out.write(f"    venue: {yaml_str(pub['venue'])}\n")
            # year: keep as integer-ish for JS sorting
            out.write(f"    year: {year}\n")
            out.write(
                "    type: {type}  # journal, conference, workshop, techreport, abstract, book-chapter, preprint, other\n".format(
                    type=pub["type"]
                )
            )

            if pub["doi"]:
                out.write(f"    doi: {yaml_str(pub['doi'])}\n")

            if pub["paper_url"]:
                out.write(f"    paper_url: {yaml_str(pub['paper_url'])}\n")
            else:
                out.write('    # paper_url: ""  # Add direct link to paper if available\n')

            if pub.get("abstract"):
                out.write(f"    abstract: {yaml_str(pub['abstract'])}\n")
            else:
                out.write('    # abstract: ""  # Optional - full abstract text\n')

            if pub["note"]:
                out.write(f"    note: {yaml_str(pub['note'])}\n")
            else:
                out.write('    # note: ""  # e.g., Best Paper Award\n')

            out.write('    # summary: ""  # Add a one-sentence summary of the paper\n')
            out.write(f"    # image: {yaml_str(pub['id'] + '.jpg')}  # Optional - add image file to images/papers/\n")

        out.write("\n\n# --------------------------------------------------\n")
        out.write("# TEMPLATE: Copy this to add a new publication\n")
        out.write("# --------------------------------------------------\n")
        out.write("#  - id: 'lastname2024keyword'\n")
        out.write("#    title: 'Your Paper Title'\n")
        out.write("#    authors: 'Last, F., Last, F., Last, F.'\n")
        out.write("#    venue: 'Journal or Conference Name'\n")
        out.write("#    year: 2024\n")
        out.write("#    type: journal  # journal, conference, workshop, techreport, abstract, book-chapter, preprint, other\n")
        out.write("#    doi: '10.xxxx/xxxxx'\n")
        out.write("#    paper_url: 'https://...'\n")
        out.write("#    abstract: 'Optional abstract text...'\n")
        out.write("#    note: 'Best Paper Award'\n")
        out.write("#    # summary: 'One sentence summary of the paper.'\n")
        out.write("#    # image: 'lastname2024keyword.jpg'  # Optional\n")

    finally:
        if out is not sys.stdout:
            out.close()


# ----------------- Main ----------------- #

def main():
    parser = argparse.ArgumentParser(
        description="Convert BibTeX export to publications.yaml"
    )
    parser.add_argument("bibfile", help="Input BibTeX file")
    parser.add_argument(
        "-o", "--output", help="Output YAML file (default: stdout)", default=None
    )

    args = parser.parse_args()

    if not os.path.isfile(args.bibfile):
        print(f"Error: file not found: {args.bibfile}", file=sys.stderr)
        sys.exit(1)

    with open(args.bibfile, "r", encoding="utf-8") as f:
        bib_str = f.read()

    parser_obj = bibtexparser.bparser.BibTexParser(common_strings=True)
    parser_obj.ignore_nonstandard_types = False

    try:
        bib_db = bibtexparser.loads(bib_str, parser=parser_obj)
    except Exception as exc:
        print(f"Error parsing BibTeX file '{args.bibfile}': {exc}", file=sys.stderr)
        sys.exit(1)

    entries = bib_db.entries or []
    print(f"Loaded {len(entries)} BibTeX entries from {args.bibfile}", file=sys.stderr)

    try:
        publications = bibtex_to_publications(entries)
    except ValueError as exc:
        print(f"Error while converting BibTeX entries: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Converted to {len(publications)} publications", file=sys.stderr)

    write_yaml(publications, out_file=args.output)


if __name__ == "__main__":
    main()
