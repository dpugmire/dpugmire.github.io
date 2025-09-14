#!/usr/bin/env python3
"""
Google Scholar (via SerpAPI) → YAML + BibTeX with Crossref enrichment.

Env:
  SERPAPI_API_KEY  (required)
  SCHOLAR_ID       (default: FmxWGN0AAAAJ)

Outputs:
  _data/publications.yml
  assets/publications.bib
"""
import os, re, time, json, requests, yaml, hashlib
from pathlib import Path

# ---- Config ----
AUTHOR_ID = os.getenv("SCHOLAR_ID", "FmxWGN0AAAAJ")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")

YAML_OUT = Path("_data/publications.yml")
BIB_OUT  = Path("assets/publications.bib")
VENUE_MAP_FILE = Path("_data/venue_map.yml")  # optional overrides

# ---- Helpers ----
def load_overrides():
    if VENUE_MAP_FILE.exists():
        data = yaml.safe_load(VENUE_MAP_FILE.read_text()) or {}
        return data.get("overrides", [])
    return []

def apply_overrides(venue: str, overrides):
    v = (venue or "").lower()
    for rule in overrides:
        m = (rule.get("match") or "").lower()
        if m and m in v:
            t = (rule.get("type") or "").lower().strip()
            if t in {"journal", "conference", "bookchapter"}:
                return t
    return None

def norm_year(y):
    if y is None:
        return None
    s = str(y)
    m = re.search(r"(19|20)\d{2}", s)
    return int(m.group(0)) if m else None

def slug_key(title: str, year: int | None):
    t = re.sub(r"\W+", "", (title or "").lower())[:80]
    return f"{t}_{year or 'na'}"

def join_authors(auth):
    """
    SerpAPI returns authors either as list of dicts: [{"name": "A. Author"}, ...]
    or sometimes a string. Normalize to 'A. Author, B. Author'.
    """
    if isinstance(auth, list):
        names = [a.get("name") for a in auth if isinstance(a, dict) and a.get("name")]
        return ", ".join(names)
    if isinstance(auth, str):
        return auth
    return ""

# ---- Crossref ----
def crossref_lookup(title: str, year: int | None):
    """
    Return {doi, type, container} using Crossref works search.
    """
    if not title:
        return {}
    params = {"query.bibliographic": title, "rows": 1}
    if year:
        params["filter"] = f"from-pub-date:{year}-01-01,until-pub-date:{year}-12-31"
    try:
        r = requests.get("https://api.crossref.org/works", params=params, timeout=20)
        r.raise_for_status()
        items = r.json().get("message", {}).get("items", [])
        if items:
            it = items[0]
            return {
                "doi": it.get("DOI"),
                "type": (it.get("type") or "").lower(),  # journal-article, proceedings-article, book-chapter, ...
                "container": (it.get("container-title") or [None])[0],
            }
    except Exception as e:
        print("Crossref lookup failed:", e)
    return {}

def crossref_bibtex(doi: str | None):
    if not doi:
        return None
    try:
        r = requests.get(
            f"https://api.crossref.org/works/{doi}/transform/application/x-bibtex",
            timeout=20,
        )
        if r.ok and r.text.strip():
            return r.text.strip()
    except Exception:
        pass
    return None

def map_type(crossref_type: str | None, venue: str | None, overrides):
    # 1) explicit overrides
    t = apply_overrides(venue, overrides)
    if t:
        return t
    # 2) Crossref authoritative
    ct = (crossref_type or "").lower()
    if ct == "journal-article":
        return "journal"
    if ct == "proceedings-article" or "proceedings" in ct:
        return "conference"
    if "book-chapter" in ct or "reference-entry" in ct or "book-part" in ct:
        return "bookchapter"
    # 3) Heuristics
    v = (venue or "").lower()
    if any(k in v for k in ["tvcg", "journal", "transactions", "letters", "computer graphics forum"]):
        return "journal"
    if any(k in v for k in ["conference", "symposium", "workshop", "proceedings", "eurovis", "siggraph", "supercomputing", " sc ", "vis "]):
        return "conference"
    if any(k in v for k in ["book", "chapter", "handbook", "springer book", "wiley handbook"]):
        return "bookchapter"
    return "conference"

# ---- SerpAPI (Google Scholar Author) ----
def serpapi_fetch_all(author_id: str, api_key: str):
    """
    Paginate through all articles for the author.
    """
    if not api_key:
        raise RuntimeError("SERPAPI_API_KEY not set")
    all_articles = []
    start, num = 0, 100
    while True:
        params = {
            "engine": "google_scholar_author",
            "author_id": author_id,
            "api_key": api_key,
            "hl": "en",
            "start": start,
            "num": num,
            "sort": "pubdate",
            "no_cache": True,
        }
        r = requests.get("https://serpapi.com/search.json", params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        articles = data.get("articles", [])
        if not articles:
            break
        all_articles.extend(articles)
        if len(articles) < num:
            break
        start += num
        time.sleep(0.5)  # be polite
    return all_articles

# ---- YAML & BIB safe write ----
def safe_write(path: Path, new_text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    old_text = path.read_text() if path.exists() else ""
    if new_text != old_text:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(new_text)
        tmp.replace(path)
        print("Updated", path)
    else:
        print("No changes for", path)

def synth_bibtex(ptype: str, key: str, title: str, authors: str, venue: str, year: int, doi: str | None, url: str | None):
    # Minimal fallback when DOI→BibTeX isn’t available
    entry_type = {"journal": "@article", "conference": "@inproceedings", "bookchapter": "@incollection"}.get(ptype, "@misc")
    fields = []
    if authors: fields.append(f"  author = {{{authors}}}")
    if title:   fields.append(f"  title = {{{title}}}")
    if year:    fields.append(f"  year = {{{year}}}")
    if venue:
        tag = {"journal": "journal", "conference": "booktitle", "bookchapter": "booktitle"}.get(ptype, "howpublished")
        fields.append(f"  {tag} = {{{venue}}}")
    if doi:     fields.append(f"  doi = {{{doi}}}")
    if url:     fields.append(f"  url = {{{url}}}")
    body = ",\n".join(fields)
    return f"{entry_type}{{{key},\n{body}\n}}"

def main():
    overrides = load_overrides()

    articles = serpapi_fetch_all(AUTHOR_ID, SERPAPI_API_KEY)
    print(f"Fetched {len(articles)} articles from SerpAPI")

    records = []
    bib_chunks = []
    seen = set()

    for a in articles:
        title = (a.get("title") or "").strip()
        if not title:
            continue
        year = norm_year(a.get("year") or a.get("publication"))
        if not year:
            # Skip items without a reasonable year
            continue
        venue_guess = a.get("publication")
        authors = join_authors(a.get("authors"))
        url = a.get("link")

        key = slug_key(title, year)
        if key in seen:
            continue
        seen.add(key)

        # Enrich via Crossref
        cx = crossref_lookup(title, year)
        doi = cx.get("doi")
        container = cx.get("container") or venue_guess
        ptype = map_type(cx.get("type"), container, overrides)

        # YAML record
        rec = {
            "title": title,
            "authors": authors,
            "venue": container,
            "year": year,
            "type": ptype,
        }
        if doi: rec["doi"] = doi
        if url: rec["url"] = url
        records.append(rec)

        # BibTeX
        b = crossref_bibtex(doi) if doi else None
        if not b:
            b = synth_bibtex(ptype, key, title, authors, container or "", year, doi, url)
        bib_chunks.append(b)

    # Sort YAML by year desc then title
    records.sort(key=lambda r: (r.get("year", 0), r.get("title", "")), reverse=True)

    # Write files (only if changed)
    safe_write(YAML_OUT, yaml.dump(records, sort_keys=False, allow_unicode=True))
    safe_write(BIB_OUT, "\n\n".join(bib_chunks))

if __name__ == "__main__":
    main()
