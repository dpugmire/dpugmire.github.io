# Academic Website

## Quick Start

1. Edit `data/about.md` with your bio
2. Edit `data/publications.yaml` with your publications
3. Edit `data/talks.yaml` with your talks (including lat/lon for the map)
4. Edit:
   - `data/professional-activities.md`
   - `data/quotes.md`
   - `data/fun-facts.md`
5. Run locally: `python -m http.server 8000`
6. Open: http://localhost:8000

## Structure

- `index.html`                      - Main website (single-page app)
- `data/about.md`                   - About / bio (Markdown, rendered with marked.js)
- `data/publications.yaml`          - Your publications
- `data/talks.yaml`                 - Your talks (drives the Leaflet map and talk list)
- `data/professional-activities.md` - Professional activities in Markdown
- `data/quotes.md`                  - Quotes (Markdown)
- `data/fun-facts.md`               - Fun facts (Markdown)
- `images/papers/`                  - Paper images
- `slides/`                         - Talk PDFs
- `scripts/`                        - Helper scripts (e.g., ORCID export, LaTeX CV)
- `cv/`                             - CV and related documents

## Scripts

Download full versions from artifacts:
- `scripts/orcid_exporter.py` - Export from ORCID
- `scripts/yaml_to_latex.py`  - Generate LaTeX CV

## Customization

Edit the header in `index.html` to update:
- Your name
- Title
- Institution
- Email
- Links

Edit the Markdown files under `data/` to keep your content up to date.
