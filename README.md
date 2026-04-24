# Academic Website

## TL;DR

Test the website locally:

```bash
python3 scripts/validate_site_data.py
python3 -m http.server 8000
```

Then open [http://localhost:8000](http://localhost:8000).

Create the CV:

```bash
cd cv
make validate
make
```

## Quick Start

1. Edit `data/about.md` with your bio and research overview.
2. Edit `data/publications.yaml` with your publications (optionally include `abstract`; use `note: "Best Paper Award"` for publication-linked honors).
3. Edit `data/awards.yaml` with manual awards and honors.
4. Edit `data/talks.yaml` and `data/tutorials.yaml` (including lat/lon for the map).
5. Edit `data/mentorship.yaml` and `data/professional_activities.yaml` with your mentorship and professional service.
6. Optionally edit `data/fun-facts.md` and `data/quotes.md`.
7. Validate data: `python3 scripts/validate_site_data.py`
8. Run locally: `python -m http.server 8000`
9. Open: http://localhost:8000

## Structure

- `index.html`                      - Main website HTML shell
- `assets/css/site.css`             - Site styles
- `assets/js/site.js`               - Client-side rendering and interactions
- `data/about.md`                   - About/Bio (Markdown)
- `data/awards.yaml`                - Manual awards and honors
- `data/publications.yaml`          - Publications
- `data/talks.yaml`                 - Talks (drives the Leaflet map and list)
- `data/tutorials.yaml`             - Tutorials (drives the Leaflet map and list)
- `data/mentorship.yaml`            - Mentorship entries (postdocs and thesis advisees)
- `data/professional_activities.yaml` - Professional activities and service
- `data/fun-facts.md`               - Fun facts (Markdown)
- `data/quotes.md`                  - Favorite quotes (Markdown)
- `images/papers/`                  - Paper images
- `slides/`                         - Talk PDFs
- `scripts/`                        - Helper scripts (e.g., ORCID export, LaTeX CV)
- `cv/`                             - CV and related documents

## Validation

Run `python3 scripts/validate_site_data.py` after editing `data/` files.

The validator checks the schema used by both `index.html` and `cv/generate_cv.py`, including:
- publication types and required fields
- the canonical `talks` and `tutorials` top-level keys
- the required `about.md` sections used by the CV generator

## Customization

Edit the header in `index.html` to update:
- Your name
- Title
- Institution
- Email
- Links

Use `assets/css/site.css` for visual styling and `assets/js/site.js` for page behavior.
