# David Pugmire — Professional Site (GitHub Pages)

This repo hosts a Jekyll site for **David Pugmire, Distinguished Scientist, Oak Ridge National Laboratory**.

## Quick Start
1. Create a GitHub repo named `<yourusername>.github.io`.
2. Download `pugmire_site.zip` from this chat and unzip its contents into your repo.
3. Edit `_config.yml` and set `url: "https://<YOUR_GITHUB_USERNAME>.github.io"`.
4. Commit & push. Enable GitHub Pages (Settings → Pages → Build from `main`).
5. Optional: add `assets/DavidPugmire_CV.pdf` and a portrait at `assets/img/portrait.jpg`.
6. Edit `_data/talks.yml` to add your talk coordinates.

## Scholar Automation
- A GitHub Action runs weekly to fetch publications from Google Scholar using the Python package **scholarly**.
- If you set the repo secret `SERPAPI_API_KEY`, the fetch becomes far more reliable (uses SerpAPI proxy inside scholarly).
- The script writes:
  - `_data/publications.yml` (drives the website pages)
  - `assets/publications.bib` (for LaTeX/CV use)

If Google rate-limits/blocks, the script keeps your **last good** files (safe fallback).

## Local preview
- Install Ruby, then: `bundle install` and `bundle exec jekyll serve`.
- Or skip local preview and rely on GitHub Pages builds.

