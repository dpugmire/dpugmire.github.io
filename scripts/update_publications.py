#!/usr/bin/env python3
import os, re, time, requests, yaml, difflib, html
from pathlib import Path

# -------------------------
# Configuration
# -------------------------
AUTHOR_ID = os.getenv("SCHOLAR_ID", "FmxWGN0AAAAJ")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")

YAML_OUT = Path("_data/publications.yml")
BIB_OUT = Path("assets/publications.bib")
BIB_OUT_TXT = Path("assets/publications.bib.txt")
BIB_DIR = Path("assets/bib")
VENUE_MAP_FILE = Path("_data/venue_map.yml")
VENUE_REPORT = Path("assets/venue_mismatches.txt")

# -------------------------
# Known preprint DOI prefixes
# -------------------------
PREPRINT_PREFIXES = (
    "10.48550",  # arXiv (DataCite)
    "10.1101",   # bioRxiv/medRxiv
    "10.36227",  # TechRxiv
    "10.21203",  # ResearchSquare
    "10.31219",  # OSF Preprints
    "10.2139",   # SSRN
    "10.5281",   # Zenodo
    "10.22541",  # Preprints.org
)

# -------------------------
# Helpers
# -------------------------
def load_overrides():
    if VENUE_MAP_FILE.exists():
        data = yaml.safe_load(VENUE_MAP_FILE.read_text()) or {}
        return data.get("overrides", [])
    return []

def apply_overrides(venue, overrides):
    v = (venue or "").lower()
    for rule in overrides:
        if (rule.get("match") or "").lower() in v:
            t = (rule.get("type") or "").lower().strip()
            if t in {"journal", "conference", "bookchapter"}:
                return t
    return None

def norm_year(y):
    if y is None: return None
    m = re.search(r"(19|20)\d{4}", str(y))
    if m: return int(m.group(0))
    m = re.search(r"(19|20)\d{2}", str(y))
    return int(m.group(0)) if m else None

def slug_key(title, year):
    t = re.sub(r"\W+", "", (title or "").lower())[:80]
    return f"{t}_{year or 'na'}"

def join_authors(auth):
    if isinstance(auth, list):
        names = [a.get("name") for a in auth if isinstance(a, dict) and a.get("name")]
        return ", ".join(names)
    if isinstance(auth, str):
        return auth
    return ""

def is_preprint_doi(doi: str | None) -> bool:
    if not doi: return False
    d = doi.strip().lower()
    return any(d.startswith(p) for p in PREPRINT_PREFIXES)

def _norm_text(s: str | None) -> str:
    if not s: return ""
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return re.sub(r"[^\w]+", "", s)

def _clean_container_hint(venue: str | None) -> str:
    if not venue: return ""
    v = venue.split(" …")[0]
    v = re.sub(r"\b\d{4}\b.*$", "", v)
    v = re.sub(r"\d+\s*\(.*?\).*", "", v)
    return v.strip()

# -------------------------
# Crossref lookup
# -------------------------
def crossref_lookup(title: str, year: int | None, venue_hint: str | None = None, expect_journal: bool = False):
    if not title: return {}

    title_q = title.strip()
    container_hint = _clean_container_hint(venue_hint)
    year_from = (year - 2) if year else None
    year_to   = (year + 1) if year else None

    def query_crossref(params):
        try:
            r = requests.get("https://api.crossref.org/works", params=params, timeout=20)
            r.raise_for_status()
            return r.json().get("message", {}).get("items", [])
        except Exception as e:
            print("Crossref request failed:", e)
            return []

    def score_item(it):
        cr_title = (it.get("title") or [""])[0]
        t_score = difflib.SequenceMatcher(None, _norm_text(title_q), _norm_text(cr_title)).ratio()
        container = (it.get("container-title") or [None])[0] or ""
        c_bonus = 0.08 if container_hint and _norm_text(container_hint) in _norm_text(container) else 0.0
        typ = (it.get("type") or "").lower()
        j_bonus = 0.06 if typ == "journal-article" else 0.0
        doi = (it.get("DOI") or "").lower()
        p_penalty = -0.12 if is_preprint_doi(doi) else 0.0
        return t_score + c_bonus + j_bonus + p_penalty, t_score, container, typ, doi

    flt = []
    if expect_journal:
        flt.append("type:journal-article")
    if year_from and year_to:
        flt.append(f"from-pub-date:{year_from}-01-01")
        flt.append(f"until-pub-date:{year_to}-12-31")
    filt = ",".join(flt) if flt else None

    attempts = []
    if container_hint:
        params = {"query.title": title_q, "rows": 10, "select": "DOI,type,URL,container-title,title"}
        if filt: params["filter"] = filt
        params["query.container-title"] = container_hint
        attempts.append(params)
    params = {"query.title": title_q, "rows": 10, "select": "DOI,type,URL,container-title,title"}
    if filt: params["filter"] = filt
    attempts.append(params)
    params = {"query.bibliographic": title_q, "rows": 10, "select": "DOI,type,URL,container-title,title"}
    if filt: params["filter"] = filt
    attempts.append(params)

    best = None
    best_s = 0.0
    items = []
    for p in attempts:
        items = query_crossref(p)
        for it in items:
            s, *_ = score_item(it)
            if s > best_s:
                best, best_s = it, s
        if best and best_s >= 0.90:
            break

    if not best:
        return {}

    if expect_journal:
        alt_items = items if items else []
        journal_alts = []
        for it in alt_items:
            typ = (it.get("type") or "").lower()
            doi = (it.get("DOI") or "").lower()
            if typ == "journal-article" and not is_preprint_doi(doi):
                journal_alts.append(it)
        if journal_alts:
            journal_alts.sort(
                key=lambda it: difflib.SequenceMatcher(
                    None, _norm_text(title_q), _norm_text((it.get("title") or [""])[0])
                ).ratio(),
                reverse=True,
            )
            best = journal_alts[0]

    return {
        "doi": best.get("DOI"),
        "type": (best.get("type") or "").lower(),
        "container": (best.get("container-title") or [None])[0],
        "url": best.get("URL"),
    }

# -------------------------
# BibTeX helpers
# -------------------------
def crossref_bibtex(doi):
    if not doi: return None
    try:
        r = requests.get(f"https://api.crossref.org/works/{doi}/transform/application/x-bibtex", timeout=20)
        if r.ok and r.text.strip():
            return r.text.strip()
    except Exception: pass
    return None

def synth_bibtex(ptype, key, title, authors, venue, year, doi, url):
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
    return f"{entry_type}{{{key},\n{',\n'.join(fields)}\n}}"

def best_title_url(doi, serp_link, cross_url):
    if doi: return f"https://doi.org/{doi}"
    if serp_link and "scholar.google" not in serp_link: return serp_link
    if cross_url: return cross_url
    return serp_link

# -------------------------
# SerpAPI fetch
# -------------------------
def serpapi_fetch_all(author_id, api_key):
    if not api_key:
        raise RuntimeError("SERPAPI_API_KEY not set")
    all_articles, start, num = [], 0, 100
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
        if not articles: break
        all_articles.extend(articles)
        if len(articles) < num: break
        start += num
        time.sleep(0.5)
    return all_articles

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

# -------------------------
# Main
# -------------------------
def main():
    overrides = load_overrides()
    articles = serpapi_fetch_all(AUTHOR_ID, SERPAPI_API_KEY)
    print(f"Fetched {len(articles)} articles from SerpAPI")

    records, bib_chunks, seen = [], [], set()
    BIB_DIR.mkdir(parents=True, exist_ok=True)

    for a in articles:
        title = (a.get("title") or "").strip()
        if not title: continue
        year = norm_year(a.get("year") or a.get("publication"))
        if not year: continue

        venue_guess = a.get("publication")
        authors     = join_authors(a.get("authors"))
        serp_link   = a.get("link")
        key         = slug_key(title, year)
        if key in seen: continue
        seen.add(key)

        looks_like_journal = bool(venue_guess) and any(
            k in venue_guess.lower()
            for k in ["journal", "transactions", "letters", "proceedings of the ieee",
                      "computer graphics forum", "international journal", "j. ", "trans. "]
        )
        cx = crossref_lookup(title, year, venue_hint=venue_guess, expect_journal=looks_like_journal)

        doi       = cx.get("doi")
        container = cx.get("container") or venue_guess
        cross_url = cx.get("url")
        ptype     = apply_overrides(container, overrides) or (
            "journal" if looks_like_journal else "conference"
        )

        title_url = best_title_url(doi, serp_link, cross_url)

        bib = crossref_bibtex(doi) if doi else None
        if not bib:
            bib = synth_bibtex(ptype, key, title, authors, container or "", year, doi, title_url)

        bib_path = BIB_DIR / f"{key}.bib"
        bib_path.write_text(bib + "\n")
        bib_txt_path = bib_path.with_name(bib_path.name + ".txt")
        bib_txt_path.write_text(bib + "\n")

        rec = {
            "title": title,
            "authors": authors,
            "venue": container,
            "year": year,
            "type": ptype,
            "title_url": title_url,
            "bibfile": f"assets/bib/{bib_path.name}",
            "bibfile_txt": f"assets/bib/{bib_txt_path.name}",
        }
        if doi: rec["doi"] = doi
        if serp_link: rec["url"] = serp_link
        records.append(rec)
        bib_chunks.append(bib)

    # Sort and write YAML + BibTeX
    records.sort(key=lambda r: (r.get("year", 0), r.get("title", "")), reverse=True)
    safe_write(YAML_OUT, yaml.dump(records, sort_keys=False, allow_unicode=True))
    agg_bib = "\n\n".join(bib_chunks)
    safe_write(BIB_OUT, agg_bib)
    safe_write(BIB_OUT_TXT, agg_bib + "\n")

    # Venue mismatch report
    venue_report = [f"{rec.get('year')} | {rec.get('venue')} -> {rec.get('type')}" for rec in records]
    report_text = "\n".join(sorted(set(venue_report)))
    safe_write(VENUE_REPORT, report_text)

if __name__ == "__main__":
    main()
