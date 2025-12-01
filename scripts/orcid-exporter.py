#!/usr/bin/env python3
"""
ORCID + Google Scholar (SerpAPI) to YAML Exporter

Usage:
    python orcid_scholar_exporter.py YOUR_ORCID_ID

Example:
    python orcid_scholar_exporter.py 0000-0003-0647-2634
"""

import os
import sys
import re
import html
import time
from datetime import datetime
from difflib import SequenceMatcher

import requests


# ----------------- Utility helpers ----------------- #

def clean_text(text):
    """Remove HTML tags, decode entities, normalize whitespace, escape quotes for YAML."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)   # strip HTML tags
    text = html.unescape(text)            # &amp; -> &
    text = " ".join(text.split())         # normalize whitespace
    text = text.replace('"', '\\"')       # escape for YAML double quotes
    return text


def safe_get(obj, *keys, default=""):
    """Safely get nested dictionary values."""
    for key in keys:
        if obj is None:
            return default
        if isinstance(obj, dict):
            obj = obj.get(key)
        else:
            return default
    return obj if obj is not None else default


def normalize_doi(doi):
    """Normalize DOI: strip URL prefixes, lowercase."""
    if not doi:
        return None
    doi = doi.strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    return doi.lower()


def generate_id(title, year, authors):
    """Generate a publication ID like lastname2025keyword."""
    first_author = "author"
    if authors:
        first_part = authors.split(",")[0].strip()  # "Wang" from "Wang, X."
        first_author = re.sub(r"[^a-zA-Z]", "", first_part).lower() or "author"

    title_words = re.findall(r"\b[a-zA-Z]{4,}\b", (title or "").lower())
    keyword = title_words[0] if title_words else "paper"

    return f"{first_author}{year}{keyword}"


def categorize_type(work_type):
    """Map ORCID work type to our categories."""
    if not work_type:
        return "other"
    w = work_type.lower()
    if any(x in w for x in ["journal", "article"]):
        return "journal"
    if "workshop" in w:
        return "workshop"
    if any(x in w for x in ["conference", "proceedings"]):
        return "conference"
    if any(x in w for x in ["book", "chapter"]):
        return "book-chapter"
    if "preprint" in w:
        return "preprint"
    return "other"


# ----------------- ORCID API ----------------- #

def get_orcid_publications(orcid_id):
    """Fetch ORCID works summary list."""
    print(f"Fetching ORCID works summary for: {orcid_id}")
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    headers = {"Accept": "application/vnd.orcid+json"}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"Error fetching ORCID works: {e}")
        return None


# ----------------- SerpAPI / Google Scholar ----------------- #

def get_serpapi_key():
    """Return SerpAPI key from common env var names."""
    return (
        os.getenv("SERPAPI_API_KEY")
        or os.getenv("SERPAPI_KEY")
        or os.getenv("SERP_API_KEY")
    )


def search_scholar_by_title(title, year=None, serpapi_key=None):
    """Search Google Scholar (via SerpAPI) by title (+ optional year)."""
    if not serpapi_key:
        return None

    params = {
        "engine": "google_scholar",
        "q": title,
        "api_key": serpapi_key,
    }
    if year and str(year).isdigit():
        params["as_ylo"] = year
        params["as_yhi"] = year

    try:
        resp = requests.get("https://serpapi.com/search", params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return data.get("organic_results", [])
    except requests.RequestException as e:
        print(f"    ⚠️  SerpAPI/Scholar error: {e}")
        return None


def best_scholar_match(orcid_title, results):
    """Pick the best Scholar result by fuzzy title match."""
    if not results:
        return None

    def norm(s):
        return re.sub(r"\W+", "", (s or "")).lower()

    target = norm(orcid_title)
    best = None
    best_score = 0.0

    for r in results:
        s_title = r.get("title")
        score = 0.0
        if s_title:
            score = SequenceMatcher(None, target, norm(s_title)).ratio()
        if score > best_score:
            best_score = score
            best = r

    # Require some minimum similarity to avoid random matches
    if best_score < 0.6:
        return None
    return best

def enrich_from_scholar(title, year, serpapi_key):
    """Return dict with metadata from Scholar for a given title/year."""
    results = search_scholar_by_title(title, year, serpapi_key)
    if not results:
        return None

    match = best_scholar_match(title, results)
    if not match:
        return None

    pub_info = match.get("publication_info", {}) or {}
    authors_field = pub_info.get("authors", [])

    authors_list = []
    if isinstance(authors_field, list):
        for a in authors_field:
            if isinstance(a, str):
                authors_list.append(a)
            elif isinstance(a, dict):
                # SerpAPI typically uses {"name": "..."}
                name = a.get("name") or a.get("author") or a.get("title")
                if name:
                    authors_list.append(name)
    elif isinstance(authors_field, str):
        authors_list = [authors_field]

    authors_str = ", ".join(authors_list) if authors_list else ""

    venue = pub_info.get("summary", "") or ""
    scholar_year = pub_info.get("year") or year
    link = match.get("link")

    return {
        "title": match.get("title") or title,
        "authors_raw": authors_str,
        "venue": venue,
        "year": str(scholar_year),
        "scholar_url": link,
    }


# ----------------- CrossRef ----------------- #

def format_authors_from_crossref(crossref_data):
    """Format author list from CrossRef as 'Last, F.'"""
    if not crossref_data or "author" not in crossref_data:
        return None

    authors = []
    for a in crossref_data["author"]:
        family = a.get("family", "")
        given = a.get("given", "")
        if family and given:
            authors.append(f"{family}, {given[0]}.")
        elif family:
            authors.append(family)

    if not authors:
        return None

    if len(authors) > 10:
        return ", ".join(authors[:10]) + ", et al."
    return ", ".join(authors)


def find_doi_with_crossref(title, authors=None, year=None):
    """
    Try to find DOI using CrossRef by title (+ first author + year).
    Returns (doi, crossref_message_dict or None)
    """
    query_parts = [title]
    if authors:
        # Use only first author token to keep query short
        first_author = authors.split(",")[0]
        query_parts.append(first_author)
    if year and str(year).isdigit():
        query_parts.append(str(year))

    query = " ".join(query_parts)
    params = {
        "query.bibliographic": query,
        "rows": 1,
        # polite but optional; fill with your email if you want
        # "mailto": "you@example.com",
    }

    try:
        resp = requests.get("https://api.crossref.org/works", params=params, timeout=20)
        if not resp.ok:
            return None, None
        items = resp.json().get("message", {}).get("items", [])
        if not items:
            return None, None
        item = items[0]
        doi = item.get("DOI")
        return normalize_doi(doi), item
    except Exception:
        return None, None


# ----------------- Core processing ----------------- #

def process_publications(orcid_data, serpapi_key):
    """Process ORCID works, enrich with Scholar+CrossRef, and produce pub dicts."""
    if not orcid_data or "group" not in orcid_data:
        return []

    publications = []
    groups = orcid_data.get("group", [])
    total = len(groups)

    print(f"\nProcessing {total} ORCID groups...\n")

    for i, group in enumerate(groups, 1):
        try:
            work_summaries = group.get("work-summary", [])
            if not work_summaries:
                continue

            work = work_summaries[0]

            raw_title = safe_get(work, "title", "title", "value", default="Untitled")
            title = clean_text(raw_title)

            year = safe_get(work, "publication-date", "year", "value", default="")
            year_str = str(year) if year else "Unknown"

            work_type = safe_get(work, "type", default="other")
            category = categorize_type(work_type)

            # DOI from ORCID summary external-ids (if present)
            doi = None
            external_ids = safe_get(work, "external-ids", "external-id", default=[])
            if isinstance(external_ids, list):
                for ext in external_ids:
                    if ext.get("external-id-type", "").lower() == "doi":
                        doi = ext.get("external-id-value")
                        break
            doi = normalize_doi(doi)

            venue = safe_get(work, "journal-title", "value", default="") or "Unknown Venue"
            venue = clean_text(venue)

            authors = None
            paper_url = None

            print(f"[{i}/{total}] {title[:70]}...")
            # --- Enrich with Scholar ---
            scholar_meta = enrich_from_scholar(title, year_str, serpapi_key)
            if scholar_meta:
                print("    Using Google Scholar metadata")
                title = clean_text(scholar_meta["title"])
                venue = clean_text(scholar_meta["venue"]) or venue
                year_str = scholar_meta["year"] or year_str
                scholar_authors_raw = scholar_meta["authors_raw"]
                paper_url = scholar_meta["scholar_url"]
            else:
                scholar_authors_raw = None

            # --- Enrich with CrossRef ---
            crossref_data = None
            if doi:
                print("    CrossRef lookup by DOI...")
                try:
                    resp = requests.get(
                        f"https://api.crossref.org/works/{doi}", timeout=10
                    )
                    if resp.ok:
                        crossref_data = resp.json().get("message", None)
                except Exception:
                    crossref_data = None
            else:
                print("    No DOI in ORCID; CrossRef lookup by title...")
                # Use Scholar authors if we have them to help the query
                doi, crossref_data = find_doi_with_crossref(
                    title, authors=scholar_authors_raw, year=year_str
                )

            # If CrossRef returned metadata, use it for authors/venue/url
            if crossref_data:
                cr_authors = format_authors_from_crossref(crossref_data)
                if cr_authors:
                    authors = cr_authors

                ct = crossref_data.get("container-title") or []
                if ct:
                    venue = clean_text(ct[0])

                cr_url = crossref_data.get("URL")
                if cr_url:
                    paper_url = cr_url

                # Use DOI from CrossRef if we didn't have one
                if not doi:
                    doi = normalize_doi(crossref_data.get("DOI"))
            else:
                # If no CrossRef authors but we have Scholar authors, use those
                if scholar_authors_raw:
                    authors = scholar_authors_raw

            if not authors:
                authors = "Authors not available"

            pub_id = generate_id(title, year_str, authors)

            pub = {
                "id": pub_id,
                "title": title,
                "authors": authors,
                "venue": venue,
                "year": year_str,
                "type": category,
                "doi": doi,
                "paper_url": paper_url,
            }

            publications.append(pub)
            # be nice to APIs
            time.sleep(0.3)

        except Exception as e:
            print(f"    ⚠️  Error processing group {i}: {e}")
            continue

    # Sort by year desc, then title
    def sort_key(p):
        y = p.get("year", "")
        y_val = int(y) if str(y).isdigit() else 0
        return (-y_val, p.get("title", ""))

    publications.sort(key=sort_key)
    return publications


# ----------------- YAML output + summary ----------------- #

def write_yaml(publications, filename="publications.yaml"):
    """Write publications to YAML file, matching your desired format."""
    print(f"\n{'=' * 60}")
    print(f"Writing {len(publications)} publications to {filename}...")
    print(f"{'=' * 60}\n")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("# publications.yaml\n")
        f.write("# Generated from ORCID + Google Scholar (SerpAPI) + CrossRef on "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("publications:\n")

        for pub in publications:
            type_label = pub["type"].upper()
            year = pub["year"]
            f.write(f"\n  # {type_label} - {year}\n")
            f.write(f"  - id: {pub['id']}\n")
            f.write(f"    title: \"{pub['title']}\"\n")
            f.write(f"    authors: \"{pub['authors']}\"\n")
            f.write(f"    venue: \"{pub['venue']}\"\n")
            f.write(f"    year: {year}\n")
            f.write(
                "    type: {type}  # journal, conference, workshop, book-chapter, preprint, other\n".format(
                    type=pub["type"]
                )
            )

            if pub["doi"]:
                f.write(f"    doi: \"{pub['doi']}\"\n")

            if pub["paper_url"]:
                f.write(f"    paper_url: \"{pub['paper_url']}\"\n")
            else:
                f.write('    # paper_url: ""  # Add direct link to paper if available\n')

            f.write('    # summary: ""  # Add a one-sentence summary of the paper\n')
            f.write(f"    # image: \"{pub['id']}.jpg\"  # Optional - add image file to images/papers/\n")

        f.write("\n\n# --------------------------------------------------\n")
        f.write("# TEMPLATE: Copy this to add a new publication\n")
        f.write("# --------------------------------------------------\n")
        f.write("#  - id: lastname2024keyword\n")
        f.write("#    title: \"Your Paper Title\"\n")
        f.write("#    authors: \"Last, F., Last, F., Last, F.\"\n")
        f.write("#    venue: \"Journal or Conference Name\"\n")
        f.write("#    year: 2024\n")
        f.write("#    type: journal  # journal, conference, workshop, book-chapter, preprint, other\n")
        f.write("#    doi: \"10.xxxx/xxxxx\"\n")
        f.write("#    paper_url: \"https://...\"\n")
        f.write("#    # summary: \"One sentence summary of the paper.\"\n")
        f.write("#    # image: \"lastname2024keyword.jpg\"  # Optional\n")

    print(f"✅ Successfully created {filename}\n")


def print_summary(publications):
    """Print summary statistics."""
    print(f"{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}\n")

    type_counts = {}
    for pub in publications:
        t = pub["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    print(f"Total publications: {len(publications)}\n")

    type_names = {
        "journal": "Journal Articles",
        "conference": "Conference Papers",
        "workshop": "Workshop Papers",
        "book-chapter": "Book Chapters",
        "preprint": "Preprints",
        "other": "Other",
    }

    for type_key, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        name = type_names.get(type_key, type_key.title())
        print(f"  {name}: {count}")

    missing_doi = sum(1 for p in publications if not p["doi"])
    print("\n📋 Data completeness:")
    print(f"  Publications with DOI: {len(publications) - missing_doi}/{len(publications)}")

    print("\n✏️  Next steps:")
    print("  1. Review publications.yaml and tweak venue/type for key papers as needed")
    print("  2. Fill in # summary fields where helpful")
    print("  3. Remove any unwanted entries (talks, misc) from the YAML")
    print("  4. Add images to images/papers/ (optional)")
    print("  5. Move to data/: mv publications.yaml data/publications.yaml")
    print("  6. Test website: python -m http.server 8000\n")


# ----------------- Main ----------------- #

def main():
    if len(sys.argv) != 2:
        print("Usage: python orcid_scholar_exporter.py YOUR_ORCID_ID")
        print("Example: python orcid_scholar_exporter.py 0000-0003-0647-2634")
        sys.exit(1)

    orcid_id = sys.argv[1]
    if not re.match(r"\d{4}-\d{4}-\d{4}-\d{3}[0-9X]", orcid_id):
        print("❌ Error: Invalid ORCID ID format")
        print("Should be like: 0000-0003-0647-2634")
        sys.exit(1)

    serpapi_key = get_serpapi_key()
    if not serpapi_key:
        print("❌ Error: SERPAPI API key not found.")
        print("Set SERPAPI_API_KEY, SERPAPI_KEY, or SERP_API_KEY in your environment.")
        sys.exit(1)

    orcid_data = get_orcid_publications(orcid_id)
    if not orcid_data:
        print("❌ Failed to fetch ORCID data")
        sys.exit(1)

    pubs = process_publications(orcid_data, serpapi_key)
    if not pubs:
        print("❌ No publications found")
        sys.exit(1)

    write_yaml(pubs)
    print_summary(pubs)


if __name__ == "__main__":
    main()
