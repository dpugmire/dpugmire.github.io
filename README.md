# Academic Website

## Quick Start

1. Edit `data/publications.yaml` with your publications
2. Edit `data/talks.yaml` with your talks (including lat/lon for the map)
3. Run locally: `python -m http.server 8000`
4. Open: http://localhost:8000

## Structure

- `index.html` - Main website (don't edit)
- `data/publications.yaml` - Your publications
- `data/talks.yaml` - Your talks (drives the Leaflet map and talk list)
- `images/papers/` - Paper images
- `slides/` - Talk PDFs

## Scripts

Download full versions from artifacts:
- `scripts/orcid_exporter.py` - Export from ORCID
- `scripts/yaml_to_latex.py` - Generate LaTeX CV

## Customization

Edit the header in `index.html` to update:
- Your name
- Title
- Institution
- Email
- Links
