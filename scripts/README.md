# Academic Website

## Quick Start

1. Edit `data/about.md` with your bio and research overview.
2. Edit `data/publications.yaml` with your publications (optionally include `abstract`).
3. Edit `data/talks.yaml` with your talks (including lat/lon for the map).
4. Edit `data/mentorship.yaml` and `data/professional_activities.yaml` with your mentorship and professional service.
5. Optionally edit `data/fun-facts.md` and `data/quotes.md`.
6. Run locally: `python -m http.server 8000`
7. Open: http://localhost:8000

## Structure

- `index.html`                      - Main website (single-page app)
- `data/about.md`                   - About/Bio (Markdown)
- `data/publications.yaml`          - Publications
- `data/talks.yaml`                 - Talks (drives the Leaflet map and talk list)
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
