# Academic Website

## Quick Start

1. Edit `data/about.md` with your bio and research overview.
2. Edit `data/publications.yaml` with your publications (optionally include `abstract`).
3. Edit `data/talks.yaml` and `data/tutorials.yaml` (including lat/lon for the map).
4. Edit `data/mentorship.yaml` and `data/professional_activities.yaml` with your mentorship and professional service.
5. Optionally edit `data/fun-facts.md` and `data/quotes.md`.
6. Validate data: `python3 scripts/validate_site_data.py`
7. Run locally: `python -m http.server 8000`
8. Open: http://localhost:8000

## Structure

- `index.html`                      - Main website HTML shell
- `assets/css/site.css`             - Site styles
- `assets/js/site.js`               - Client-side rendering and interactions
- `data/about.md`                   - About/Bio (Markdown)
- `data/publications.yaml`          - Publications
- `data/talks.yaml`                 - Talks (drives the Leaflet map and talk list)
- `data/tutorials.yaml`             - Tutorials (drives the Leaflet map and talk list)
- `data/mentorship.yaml`            - Mentorship entries (postdocs and thesis advisees)
- `data/professional_activities.yaml` - Professional activities and service
- `data/fun-facts.md`               - Fun facts (Markdown)
- `data/quotes.md`                  - Favorite quotes (Markdown)
- `images/papers/`                  - Paper images
- `slides/`                         - Talk PDFs
- `scripts/`                        - Helper scripts (e.g., ORCID export, LaTeX CV)
- `cv/`                             - CV and related documents

## Customization

Edit the header in `index.html` to update:
- Your name
- Title
- Institution
- Email
- Links
