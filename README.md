# Academic Website

## Quick Start

1. Edit `data/about.md` with your bio and research overview.
2. Edit `data/publications.yaml` with your publications (optionally include `abstract`; use `note: "Best Paper Award"` for publication-linked honors).
3. Edit `data/awards.yaml` with manual awards and honors.
4. Edit `data/keynotes.yaml`, `data/talks.yaml`, and `data/tutorials.yaml` (including lat/lon for the map).
5. Edit `data/mentorship.yaml` and `data/professional_activities.yaml` with your mentorship and professional service.
6. Optionally edit `data/fun-facts.md` and `data/quotes.md`.
7. Run locally: `python -m http.server 8000`
8. Open: http://localhost:8000

## Structure

- `index.html`                      - Main website (single-page app)
- `data/about.md`                   - About/Bio (Markdown)
- `data/awards.yaml`                - Manual awards and honors
- `data/publications.yaml`          - Publications
- `data/keynotes.yaml`              - Keynotes (drives the Leaflet map and list)
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

## Customization

Edit the header in `index.html` to update:
- Your name
- Title
- Institution
- Email
- Links
