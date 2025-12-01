# Academic Website

## Quick Start

1. Edit `data/publications.yaml` with your publications
2. Edit `data/talks.yaml` with your talks (including lat/lon for the map)
3. Edit `data/professional-activities.md` with your professional service
4. Run locally: `python -m http.server 8000`
5. Open: http://localhost:8000

## Structure

- `index.html`                     - Main website (single-page app)
- `data/publications.yaml`         - Your publications
- `data/talks.yaml`                - Your talks (drives the Leaflet map and talk list)
- `data/professional-activities.md`- Professional activities in Markdown (rendered into the SPA)
- `images/papers/`                 - Paper images
- `slides/`                        - Talk PDFs
- `scripts/`                       - Helper scripts (e.g., ORCID export, LaTeX CV)
- `cv/`                            - CV and related documents

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

Edit `data/professional-activities.md` to keep your service/leadership record up to date.
