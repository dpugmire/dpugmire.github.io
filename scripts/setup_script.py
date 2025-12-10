#!/usr/bin/env python3
"""
Academic Website Setup Script

Creates the folder structure, index.html, README, and (optionally) template
files for publications, talks, and professional activities.

Usage:
    python setup_academic_website.py
    python setup_academic_website.py --reset-templates
"""

import os
import sys
import argparse


def create_directory_structure():
    """Create all necessary directories."""
    dirs = [
        "data",
        "images/papers",
        "slides",
        "scripts",
        "cv",
    ]

    print("Creating directory structure...")
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"  ✓ Ensured {d}/ exists")
    print()


def create_index_html():
    """Create the main website HTML file (always overwritten)."""
    print("Creating index.html...")

    # Reading the HTML as a raw string to avoid escape issues
    html_content = r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dr. Your Name - Academic Portfolio</title>

    <!-- js-yaml for loading YAML data -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/js-yaml/4.1.0/js-yaml.min.js"></script>

    <!-- marked.js for rendering Markdown (about, quotes, fun facts, professional activities) -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

    <!-- Leaflet CSS & JS for talk map -->
    <link
      rel="stylesheet"
      href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { scroll-padding-top: 200px; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; }
        header { background: white; padding: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        h1 { font-size: 2rem; margin-bottom: 0.5rem; }
        .subtitle { color: #666; font-size: 1.1rem; }
        .contact-links { display: flex; gap: 1rem; }
        .contact-links a { color: #0066cc; text-decoration: none; padding: 0.5rem 1rem; border: 1px solid #0066cc; border-radius: 4px; transition: all 0.3s; }
        .contact-links a:hover { background: #0066cc; color: white; }

        nav { background: white; border-bottom: 2px solid #eee; position: sticky; top: 100px; z-index: 99; }
        nav ul { max-width: 1200px; margin: 0 auto; list-style: none; display: flex; gap: 2rem; padding: 0 2rem; }
        nav a { display: block; padding: 1rem 0; text-decoration: none; color: #666; border-bottom: 3px solid transparent; transition: all 0.3s; }
        nav a:hover, nav a.active { color: #0066cc; border-bottom-color: #0066cc; }

        main { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        section { background: white; padding: 2rem; margin-bottom: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: none; }
        section.active { display: block; }
        h2 { font-size: 1.8rem; margin-bottom: 1.5rem; color: #222; border-bottom: 3px solid #0066cc; padding-bottom: 0.5rem; }
        h3 { font-size: 1.3rem; margin: 2rem 0 1rem 0; color: #444; }

        .category-header { display: flex; align-items: center; gap: 1rem; border-left: 4px solid #0066cc; padding-left: 1rem; margin-top: 2rem; margin-bottom: 1rem; }
        .category-count { background: #0066cc; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.9rem; }

        .publication { display: flex; gap: 1.5rem; margin-bottom: 2rem; padding: 1.5rem; border: 1px solid #ddd; border-radius: 8px; transition: box-shadow 0.3s; }
        .publication:hover { box-shadow: 0 4px 8px rgba(0,0,0,0.1); }

        .pub-image {
            flex-shrink: 0;
            width: 200px;
            height: 150px;
            background: #f0f0f0;
            border-radius: 4px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85rem;
            color: #888;
        }
        .pub-image img {
            max-width: 100%;
            max-height: 100%;
            width: auto;
            height: auto;
            object-fit: contain;
            display: block;
        }

        .pub-content { flex: 1; }
        .pub-title { font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem; color: #222; }
        .pub-authors { color: #666; margin-bottom: 0.25rem; }
        .pub-venue { color: #888; font-style: italic; margin-bottom: 0.75rem; }
        .pub-summary { color: #555; margin-bottom: 1rem; line-height: 1.5; }
        .pub-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; }
        .btn { padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; font-size: 0.9rem; text-decoration: none; display: inline-flex; align-items: center; gap: 0.5rem; transition: all 0.3s; }
        .btn-primary { background: #0066cc; color: white; }
        .btn-primary:hover { background: #0052a3; }
        .btn-secondary { background: #f0f0f0; color: #333; }
        .btn-secondary:hover { background: #e0e0e0; }

        .bibtex-container { display: none; margin-top: 1rem; background: #f8f8f8; padding: 1rem; border-radius: 4px; border-left: 3px solid #0066cc; }
        .bibtex-container.show { display: block; }
        .bibtex-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
        .bibtex-code { background: white; padding: 1rem; border-radius: 4px; overflow-x: auto; font-family: 'Courier New', monospace; font-size: 0.85rem; white-space: pre; }

        #talk-map { height: 520px; margin: 1rem 0; border-radius: 8px; overflow: hidden; }
        .talk-item { padding: 1rem; border-left: 4px solid #10b981; margin-bottom: 1rem; background: #f9f9f9; }
        .talk-title { font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem; }
        .talk-details { color: #666; font-size: 0.95rem; }

        .markdown-body {
            line-height: 1.7;
        }
        .markdown-body h1,
        .markdown-body h2,
        .markdown-body h3 {
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }
        .markdown-body ul {
            margin-left: 1.25rem;
            margin-bottom: 1rem;
        }
        .markdown-body p {
            margin-bottom: 0.75rem;
        }

        footer { text-align: center; padding: 2rem; background: white; color: #666; margin-top: 3rem; }

        .pub-header { position: sticky; top: 165px; background: white; padding: 1rem 0; border-bottom: 3px solid #0066cc; z-index: 50; display: flex; align-items: center; gap: 2rem; }
        .pub-header h2 { font-size: 1.8rem; margin: 0; color: #222; border: none; padding: 0; }
        .pub-nav { display: flex; gap: 1rem; align-items: center; }
        .pub-nav a { color: #0066cc; text-decoration: none; padding: 0.25rem 0.5rem; border-radius: 4px; transition: background 0.3s; font-size: 0.95rem; }
        .pub-nav a:hover { background: #f0f0f0; }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div>
                <h1>Dr. Your Name</h1>
                <div class="subtitle">Professor of Computer Science</div>
                <div class="subtitle">University Name</div>
            </div>
            <div class="contact-links">
                <a href="mailto:your.email@university.edu">Email</a>
                <a href="https://github.com/yourusername" target="_blank">GitHub</a>
                <a href="cv/cv.pdf" target="_blank">CV</a>
            </div>
        </div>
    </header>
    <nav>
        <ul>
            <li><a href="#about" class="nav-link active">About</a></li>
            <li><a href="#publications" class="nav-link">Publications</a></li>
            <li><a href="#talks" class="nav-link">Talks</a></li>
            <li><a href="#projects" class="nav-link">Projects</a></li>
            <li><a href="#professional-activities" class="nav-link">Professional Activities</a></li>
            <li><a href="#quotes" class="nav-link">Quotes</a></li>
            <li><a href="#fun-facts" class="nav-link">Fun Facts</a></li>
        </ul>
    </nav>
    <main>
        <section id="about" class="active">
            <h2>About Me</h2>
            <div id="about-content" class="markdown-body">
                <p>Loading about information…</p>
            </div>
        </section>

        <section id="publications">
            <div class="pub-header">
                <h2>Publications</h2>
                <div id="publication-links" class="pub-nav" style="display:none;">
                    <a href="#pub-journal">Journal Articles</a>
                    <a href="#pub-conference">Conference Papers</a>
                    <a href="#pub-workshop">Workshop Papers</a>
                    <a href="#pub-book-chapter">Book Chapters</a>
                    <a href="#pub-preprint">Preprints</a>
                    <a href="#pub-other">Other</a>
                </div>
            </div>
            <div id="publications-content" style="margin-top: 1.5rem;"></div>
        </section>

        <section id="talks">
            <h2>Invited Talks & Presentations</h2>
            <div id="talks-content"></div>
        </section>

        <section id="projects">
            <h2>Projects & Code</h2>
            <p>Coming soon...</p>
        </section>

        <section id="professional-activities">
            <h2>Professional Activities</h2>
            <div id="professional-activities-content" class="markdown-body">
                <p>Loading professional activities…</p>
            </div>
        </section>

        <section id="quotes">
            <h2>Quotes</h2>
            <div id="quotes-content" class="markdown-body">
                <p>Loading quotes…</p>
            </div>
        </section>

        <section id="fun-facts">
            <h2>Fun Facts</h2>
            <div id="fun-facts-content" class="markdown-body">
                <p>Loading fun facts…</p>
            </div>
        </section>
    </main>
    <footer>
        <p>&copy; 2024 Dr. Your Name. All rights reserved.</p>
    </footer>

    <script>
        // Basic navigation: show/hide sections and set active link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = e.target.getAttribute('href').substring(1);

                document.querySelectorAll('section').forEach(s => s.classList.remove('active'));
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

                const targetSection = document.getElementById(target);
                if (targetSection) {
                    targetSection.classList.add('active');
                }
                e.target.classList.add('active');
            });
        });

        async function loadYAML(url) {
            try {
                const response = await fetch(url);
                const text = await response.text();
                return jsyaml.load(text);
            } catch (error) {
                console.error('Error loading ' + url + ':', error);
                return null;
            }
        }

        // Generic helper to load Markdown into a container using marked.js
        async function renderMarkdownInto(url, elementId, emptyMessage) {
            const container = document.getElementById(elementId);
            if (!container) return;

            try {
                const resp = await fetch(url);
                if (!resp.ok) {
                    container.innerHTML = '<p>' + emptyMessage + '</p>';
                    return;
                }
                const text = await resp.text();
                container.innerHTML = marked.parse(text);
            } catch (err) {
                console.error('Error loading ' + url + ':', err);
                container.innerHTML = '<p>Error loading content.</p>';
            }
        }

        // Section-specific Markdown loaders
        function renderAbout() {
            return renderMarkdownInto(
                'data/about.md',
                'about-content',
                'Please create data/about.md to customize this section.'
            );
        }

        function renderQuotes() {
            return renderMarkdownInto(
                'data/quotes.md',
                'quotes-content',
                'Please create data/quotes.md to customize this section.'
            );
        }

        function renderFunFacts() {
            return renderMarkdownInto(
                'data/fun-facts.md',
                'fun-facts-content',
                'Please create data/fun-facts.md to customize this section.'
            );
        }

        async function renderProfessionalActivities() {
            return renderMarkdownInto(
                'data/professional-activities.md',
                'professional-activities-content',
                'Please create data/professional-activities.md to customize this section.'
            );
        }

        function generateBibtex(pub) {
            const typeMap = {
                'journal': 'article',
                'conference': 'inproceedings',
                'workshop': 'inproceedings',
                'book-chapter': 'incollection',
                'preprint': 'misc',
                'other': 'misc'
            };
            const entryType = typeMap[pub.type] || 'misc';
            const venueKey = pub.type === 'journal' ? 'journal' : 'booktitle';

            let bibtex = '@' + entryType + '{' + pub.id + ',\n';
            bibtex += '  title = {' + pub.title + '},\n';
            bibtex += '  author = {' + pub.authors + '},\n';

            if (pub.editors) {
                bibtex += '  editor = {' + pub.editors + '},\n';
            }

            bibtex += '  ' + venueKey + ' = {' + pub.venue + '},\n';
            bibtex += '  year = {' + pub.year + '}';

            if (pub.doi) {
                bibtex += ',\n  doi = {' + pub.doi + '}';
            }

            bibtex += '\n}';
            return bibtex;
        }

        function toggleBibtex(id) {
            const elem = document.getElementById('bibtex-' + id);
            if (elem) {
                elem.classList.toggle('show');
            }
        }

        function copyBibtex(id, bibtex) {
            navigator.clipboard.writeText(bibtex).then(() => {
                const btn = document.getElementById('copy-btn-' + id);
                if (!btn) return;
                const originalText = btn.textContent;
                btn.textContent = '✓ Copied!';
                setTimeout(() => { btn.textContent = originalText; }, 2000);
            });
        }

        async function renderPublications() {
            const data = await loadYAML('data/publications.yaml');
            const container = document.getElementById('publications-content');
            if (!data || !data.publications) {
                container.innerHTML = '<p>No publications found. Check data/publications.yaml</p>';
                return;
            }

            const pubs = data.publications;
            const types = {
                'journal':       { name: 'Journal Articles',      color: '#0066cc', pubs: [] },
                'conference':    { name: 'Conference Papers',    color: '#10b981', pubs: [] },
                'workshop':      { name: 'Workshop Papers',      color: '#f59e0b', pubs: [] },
                'book-chapter':  { name: 'Book Chapters',        color: '#8b5cf6', pubs: [] },
                'preprint':      { name: 'Preprints',            color: '#ec4899', pubs: [] },
                'other':         { name: 'Other Publications',   color: '#6b7280', pubs: [] }
            };

            pubs.forEach(pub => {
                const type = pub.type || 'other';
                if (types[type]) {
                    types[type].pubs.push(pub);
                } else {
                    types['other'].pubs.push(pub);
                }
            });

            Object.values(types).forEach(type => {
                type.pubs.sort((a, b) => (b.year || 0) - (a.year || 0));
            });

            let html = '';
            Object.entries(types).forEach(([key, type]) => {
                if (type.pubs.length === 0) return;

                html += '<div id="pub-' + key + '" class="category-header" style="border-left-color: ' + type.color + '">';
                html += '<h3>' + type.name + '</h3>';
                html += '<span class="category-count" style="background: ' + type.color + '">' + type.pubs.length + '</span>';
                html += '</div>';

                type.pubs.forEach(pub => {
                    const bibtex = generateBibtex(pub);
                    const paperUrl = pub.paper_url || (pub.doi ? ('https://doi.org/' + pub.doi) : '#');

                    html += '<div class="publication">';
                    html += '  <div class="pub-image">';
                    if (pub.image) {
                        html += '<img src="images/papers/' + pub.image + '" alt="' + pub.title + '">';
                    } else {
                        html += 'No image';
                    }
                    html += '  </div>';

                    html += '  <div class="pub-content">';
                    html += '    <div class="pub-title">' + pub.title + '</div>';
                    html += '    <div class="pub-authors">' + (pub.authors || '') + '</div>';
                    html += '    <div class="pub-venue">' + (pub.venue || '') + (pub.year ? (', ' + pub.year) : '') + '</div>';

                    if (pub.summary) {
                        html += '    <div class="pub-summary">' + pub.summary + '</div>';
                    }

                    html += '    <div class="pub-actions">';
                    if (paperUrl !== '#') {
                        html += '      <a href="' + paperUrl + '" class="btn btn-primary" target="_blank" rel="noopener">📄 View Paper</a>';
                    }
                    html += '      <button class="btn btn-secondary" onclick="toggleBibtex(\'' + pub.id + '\')">📋 BibTeX</button>';
                    html += '    </div>';

                    html += '    <div id="bibtex-' + pub.id + '" class="bibtex-container">';
                    html += '      <div class="bibtex-header"><strong>BibTeX Citation</strong>';
                    html += '        <button id="copy-btn-' + pub.id + '" class="btn btn-secondary" onclick="copyBibtex(\'' + pub.id + '\', `' + bibtex.replace(/`/g, '\\`') + '`)">Copy</button>';
                    html += '      </div>';
                    html += '      <div class="bibtex-code">' + bibtex.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</div>';
                    html += '    </div>';

                    html += '  </div>';
                    html += '</div>';
                });
            });

            container.innerHTML = html;

            const links = document.getElementById('publication-links');
            if (links) {
                links.style.display = 'block';
            }
        }

        function escHtml(s) {
            return String(s || '').replace(/[&<>"']/g, function(m) {
                return {
                    '&': '&amp;',
                    '<': '&lt;',
                    '>': '&gt;',
                    '"': '&quot;',
                    "'": '&#39;'
                }[m];
            });
        }

        async function renderTalks() {
            const data = await loadYAML('data/talks.yaml');
            const container = document.getElementById('talks-content');
            if (!data || !data.talks) {
                container.innerHTML = '<p>No talks found. Check data/talks.yaml</p>';
                return;
            }

            const talks = data.talks.slice().sort((a, b) => new Date(b.date) - new Date(a.date));

            let html = '';
            html += '<div id="talk-map"></div>';
            html += '<h3 style="margin-top: 2rem; margin-bottom: 1rem; font-size: 1.3rem; color: #444;">Talk History</h3>';
            html += '<div id="talks-list">';

            talks.forEach(function(talk) {
                const formattedDate = talk.date
                    ? new Date(talk.date).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                      })
                    : '';

                html += '<div class="talk-item">';
                html += '<div class="talk-title">' + escHtml(talk.title) + '</div>';
                html += '<div class="talk-details">';

                const locParts = [];
                if (talk.venue) locParts.push(talk.venue);
                if (talk.city) locParts.push(talk.city);
                if (talk.country) locParts.push(talk.country);
                if (locParts.length > 0) {
                    html += '📍 ' + escHtml(locParts.join(', ')) + '<br>';
                }
                if (formattedDate) {
                    html += '📅 ' + escHtml(formattedDate);
                }
                if (talk.slides) {
                    html += '<br>📊 <a href="slides/' + encodeURIComponent(talk.slides) + '" target="_blank">View Slides</a>';
                }
                html += '</div></div>';
            });

            html += '</div>';
            container.innerHTML = html;

            const map = L.map('talk-map', { worldCopyJump: true }).setView([20, 0], 2);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 10,
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);

            const keyFor = function(t) {
                const lat = parseFloat(t.lat);
                const lon = parseFloat(t.lon);
                if (isNaN(lat) || isNaN(lon)) return null;
                return lat.toFixed(3) + ',' + lon.toFixed(3);
            };

            const groups = {};
            talks.forEach(function(t) {
                const k = keyFor(t);
                if (!k) return;
                if (!groups[k]) groups[k] = [];
                groups[k].push(t);
            });

            const bounds = [];
            Object.values(groups).forEach(function(group) {
                group.sort(function(a, b) {
                    return String(b.date).localeCompare(String(a.date));
                });

                const lat = parseFloat(group[0].lat);
                const lon = parseFloat(group[0].lon);
                if (isNaN(lat) || isNaN(lon)) return;

                let locLabel = null;
                for (let i = 0; i < group.length; i++) {
                    const g = group[i];
                    if (g.location) {
                        locLabel = g.location;
                        break;
                    }
                    const parts = [];
                    if (g.venue) parts.push(g.venue);
                    if (g.city) parts.push(g.city);
                    if (g.country) parts.push(g.country);
                    if (parts.length > 0) {
                        locLabel = parts.join(', ');
                        break;
                    }
                }

                const items = group.map(function(t) {
                    const datePart = t.date ? ' — ' + escHtml(t.date) : '';
                    const parts = [];
                    if (t.venue) parts.push(t.venue);
                    if (t.city) parts.push(t.city);
                    if (t.country) parts.push(t.country);
                    const locPart = parts.length ? ', ' + escHtml(parts.join(', ')) : '';
                    const linkPart = t.slides
                        ? ' — <a href="slides/' + encodeURIComponent(t.slides) + '" target="_blank" rel="noopener">slides</a>'
                        : '';
                    return '• <b>' + escHtml(t.title) + '</b>' + datePart + locPart + linkPart;
                }).join('<br>');

                const header = locLabel
                    ? '<div style="margin-bottom:0.25rem;"><b>' + escHtml(locLabel) + '</b></div>'
                    : '';
                const popupHtml = header + items;

                L.marker([lat, lon]).addTo(map).bindPopup(popupHtml, { maxWidth: 360 });
                bounds.push([lat, lon]);
            });

            if (bounds.length > 0) {
                map.fitBounds(bounds, { padding: [24, 24] });
            }
        }

        let publicationsLoaded = false;
        let talksLoaded = false;
        let professionalActivitiesLoaded = false;
        let aboutLoaded = false;
        let quotesLoaded = false;
        let funFactsLoaded = false;

        // Lazy-load heavy / external data when sections are first visited
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                const target = e.target.getAttribute('href').substring(1);

                if (target === 'publications' && !publicationsLoaded) {
                    renderPublications();
                    publicationsLoaded = true;
                }
                if (target === 'talks' && !talksLoaded) {
                    renderTalks();
                    talksLoaded = true;
                }
                if (target === 'professional-activities' && !professionalActivitiesLoaded) {
                    renderProfessionalActivities();
                    professionalActivitiesLoaded = true;
                }
                if (target === 'about' && !aboutLoaded) {
                    renderAbout();
                    aboutLoaded = true;
                }
                if (target === 'quotes' && !quotesLoaded) {
                    renderQuotes();
                    quotesLoaded = true;
                }
                if (target === 'fun-facts' && !funFactsLoaded) {
                    renderFunFacts();
                    funFactsLoaded = true;
                }
            });
        });

        // Preload About + Professional Activities on first load (nice UX)
        renderAbout().then(() => { aboutLoaded = true; });
        renderProfessionalActivities().then(() => { professionalActivitiesLoaded = true; });
    </script>
</body>
</html>'''

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("  ✓ Created index.html\n")


def create_publications_yaml(overwrite=False):
    """Create or overwrite publications.yaml template."""
    action = "Overwriting" if overwrite else "Creating"
    print(f"{action} data/publications.yaml...")

    yaml_content = '''# publications.yaml
# Edit this file to manage your publications

publications:
  - id: smith2024neural
    title: "Neural Networks for Medical Image Analysis"
    authors: "Smith, J., Johnson, A., Williams, B."
    venue: "Nature Medicine"
    year: 2024
    type: journal
    doi: "10.1038/nm.2024.001"
    paper_url: "https://doi.org/10.1038/nm.2024.001"
    summary: "We develop a deep learning framework for cancer detection."

  - id: smith2023vision
    title: "Vision Transformers at Scale"
    authors: "Smith, J., Davis, C."
    venue: "NeurIPS"
    year: 2023
    type: conference
    doi: "10.48550/arXiv.2301.12345"
    summary: "Efficient vision transformers for high-resolution images."

# Template - copy and fill in:
#  - id: yourname2024keyword
#    title: "Paper Title"
#    authors: "Last, F., Last, F."
#    venue: "Journal or Conference"
#    year: 2024
#    type: journal  # or conference, workshop, book-chapter, preprint, other
#    doi: "10.xxxx/xxxxx"
#    paper_url: "https://..."
#    summary: "One sentence summary."
#    image: "yourname2024.jpg"
'''

    os.makedirs("data", exist_ok=True)
    with open("data/publications.yaml", "w", encoding="utf-8") as f:
        f.write(yaml_content)

    print("  ✓ Wrote data/publications.yaml\n")


def create_talks_yaml(overwrite=False):
    """Create or overwrite talks.yaml template."""
    action = "Overwriting" if overwrite else "Creating"
    print(f"{action} data/talks.yaml...")

    yaml_content = '''# talks.yaml
# Edit this file to manage your talks
# lat/lon are used to place pins on the Leaflet world map in the Talks section.

talks:
  - title: "AI in Healthcare"
    venue: "Stanford Medical School"
    city: "Stanford, CA"
    country: "USA"
    date: "2024-03-15"
    lat: 37.4275
    lon: -122.1697
    slides: "stanford2024.pdf"

  - title: "Neural Networks Tutorial"
    venue: "MIT CSAIL"
    city: "Cambridge, MA"
    country: "USA"
    date: "2024-02-10"
    lat: 42.3601
    lon: -71.0902

# Template - copy and fill in:
#  - title: "Talk Title"
#    venue: "Institution"
#    city: "City"
#    country: "Country"
#    date: "YYYY-MM-DD"
#    lat: 00.0000      # latitude (used for map pin)
#    lon: 00.0000      # longitude (used for map pin)
#    slides: "file.pdf"
#    # optional:
#    # location: "Custom location label for popup"
'''

    os.makedirs("data", exist_ok=True)
    with open("data/talks.yaml", "w", encoding="utf-8") as f:
        f.write(yaml_content)

    print("  ✓ Wrote data/talks.yaml\n")


def create_professional_activities_md(overwrite=False):
    """Create or overwrite data/professional-activities.md template."""
    action = "Overwriting" if overwrite else "Creating"
    print(f"{action} data/professional-activities.md...")

    content = '''---
title: "Professional Activities"
---

# Professional Activities

This page summarizes my professional service, leadership roles, and community activities.

---

## Leadership & Service Roles

- **[Role Title]**, [Organization or Conference], [Years]  
  Short one-line description of what you did.

- **[Role Title]**, [Organization], [Years]  
  Short description.

---

## Conference & Workshop Organization

### General Chair / Co-Chair

- **[Conference / Workshop Name]**, [Year], [Location]  
  Role: General Chair / Co-Chair  
  Notes: Brief description (e.g., size, focus area, notable aspects).

### Program Chair / Co-Chair

- **[Conference / Workshop Name]**, [Year], [Location]  
  Role: Program Chair / Co-Chair  
  Notes: Brief description (e.g., oversaw technical program, # papers, etc.).

### Other Organizing Roles

- **[Conference / Workshop Name]**, [Year]  
  Role: [Area Chair, Poster Chair, Doctoral Colloquium Chair, etc.]  
  Notes: One-line summary.

---

## Editorial Boards & Reviewing

### Editorial Boards

- **[Journal Name]** — [Editorial Role], [Years]  
  Brief description (e.g., handled submissions in visualization and HCI).

### Journal Reviewing

Regular reviewer for:

- **[Journal 1]**
- **[Journal 2]**
- **[Journal 3]**

### Conference Reviewing

Regular PC / reviewer for:

- **[Conference 1]** (years: 20XX–20YY)
- **[Conference 2]** (years: 20XX–20YY)
- **[Conference 3]**

---

## Panels, Tutorials, and Short Courses

- **[Title of Panel or Tutorial]**  
  Event: [Conference / Venue], [Year]  
  Role: [Panelist / Organizer / Tutorial Instructor]  
  Notes: One-line summary of topic and audience.

- **[Title]**, [Conference], [Year] — [Short description]

---

## Grants, Committees, and Review Panels

- **[Agency / Program Name]**, [Year(s)]  
  Role: [Panelist / Reviewer / Committee Member]  
  Brief description of scope (e.g., reviewed proposals in scientific computing and AI).

- **[Internal / Institutional Committee]**, [Institution], [Years]  
  Role and a one-line description.

---

## Professional Memberships

- Member, **[Society 1]** (since [Year])
- Member, **[Society 2]**
- [Any senior / fellow status]

---

## Outreach, Mentoring, and Community

- **Mentoring**  
  - [Description: e.g., mentor for graduate students, undergraduate research, REU programs, etc.]

- **Outreach & Public Engagement**
  - [Talks to general audiences, school visits, podcasts, public lectures, etc.]

- **Diversity, Equity, and Inclusion Activities**  
  - [Committees, initiatives, mentoring programs, etc.]

---

_Last updated: YYYY-MM-DD_
'''

    os.makedirs("data", exist_ok=True)
    with open("data/professional-activities.md", "w", encoding="utf-8") as f:
        f.write(content)

    print("  ✓ Wrote data/professional-activities.md\n")


def create_about_md(overwrite=False):
    """Create or overwrite data/about.md template."""
    action = "Overwriting" if overwrite else "Creating"
    print(f"{action} data/about.md...")

    content = '''---
title: "About Me"
---

## About Me

This is a placeholder **About** section for your academic website.

Replace this text with a short bio describing:

- Your current position and institution  
- Your main research areas  
- A sentence or two about what motivates your work

You can also include links, for example:

- [My GitHub](https://github.com/yourusername)  
- [My Google Scholar](https://scholar.google.com/)
'''

    os.makedirs("data", exist_ok=True)
    with open("data/about.md", "w", encoding="utf-8") as f:
        f.write(content)

    print("  ✓ Wrote data/about.md\n")


def create_quotes_md(overwrite=False):
    """Create or overwrite data/quotes.md template."""
    action = "Overwriting" if overwrite else "Creating"
    print(f"{action} data/quotes.md...")

    content = '''---
title: "Quotes"
---

## Quotes

Use this page to collect quotes that resonate with you — about science, creativity, leadership, or life in general.

> "The important thing is not to stop questioning."  
> — Albert Einstein

> "In the middle of difficulty lies opportunity."  
> — Albert Einstein

> "All models are wrong, but some are useful."  
> — George Box

You can add more quotes using Markdown blockquotes:

> Your quote here.  
> — Author Name
'''

    os.makedirs("data", exist_ok=True)
    with open("data/quotes.md", "w", encoding="utf-8") as f:
        f.write(content)

    print("  ✓ Wrote data/quotes.md\n")


def create_fun_facts_md(overwrite=False):
    """Create or overwrite data/fun-facts.md template."""
    action = "Overwriting" if overwrite else "Creating"
    print(f"{action} data/fun-facts.md...")

    content = '''---
title: "Fun Facts"
---

## Fun Facts

Use this section to share a more personal side of yourself.

- I enjoy teaching complex topics with clear visual explanations.  
- I prefer early-morning writing sessions with coffee.  
- My favorite debugging tool is still a whiteboard.  
- I keep a running list of "tiny experiments" I want to try in my research.

You can add as many bullet points as you like, or even include images:

![Example image](images/papers/example.jpg)
'''

    os.makedirs("data", exist_ok=True)
    with open("data/fun-facts.md", "w", encoding="utf-8") as f:
        f.write(content)

    print("  ✓ Wrote data/fun-facts.md\n")


def create_readme():
    """Create README (always overwritten)."""
    print("Creating README.md...")

    readme = '''# Academic Website

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
'''

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

    print("  ✓ Created README.md\n")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Set up an academic website (HTML, YAML/Markdown templates, and structure)."
    )
    parser.add_argument(
        "--reset-templates",
        action="store_true",
        help="Recreate data/*.yaml and data/*.md even if they already exist.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    print("\n" + "=" * 60)
    print("Academic Website Setup")
    print("=" * 60 + "\n")

    create_directory_structure()
    create_index_html()
    create_readme()

    # publications.yaml
    pubs_path = "data/publications.yaml"
    if args.reset_templates or not os.path.exists(pubs_path):
        create_publications_yaml(overwrite=args.reset_templates)
    else:
        print(f"Skipping {pubs_path} (already exists). Use --reset-templates to regenerate.\n")

    # talks.yaml
    talks_path = "data/talks.yaml"
    if args.reset_templates or not os.path.exists(talks_path):
        create_talks_yaml(overwrite=args.reset_templates)
    else:
        print(f"Skipping {talks_path} (already exists). Use --reset-templates to regenerate.\n")

    # professional-activities.md
    pa_path = "data/professional-activities.md"
    if args.reset_templates or not os.path.exists(pa_path):
        create_professional_activities_md(overwrite=args.reset_templates)
    else:
        print(f"Skipping {pa_path} (already exists). Use --reset-templates to regenerate.\n")

    # about.md
    about_path = "data/about.md"
    if args.reset_templates or not os.path.exists(about_path):
        create_about_md(overwrite=args.reset_templates)
    else:
        print(f"Skipping {about_path} (already exists). Use --reset-templates to regenerate.\n")

    # quotes.md
    quotes_path = "data/quotes.md"
    if args.reset_templates or not os.path.exists(quotes_path):
        create_quotes_md(overwrite=args.reset_templates)
    else:
        print(f"Skipping {quotes_path} (already exists). Use --reset-templates to regenerate.\n")

    # fun-facts.md
    funfacts_path = "data/fun-facts.md"
    if args.reset_templates or not os.path.exists(funfacts_path):
        create_fun_facts_md(overwrite=args.reset_templates)
    else:
        print(f"Skipping {funfacts_path} (already exists). Use --reset-templates to regenerate.\n")

    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Edit data/about.md with your bio.")
    print("2. Edit data/publications.yaml with your publications.")
    print("3. Edit data/talks.yaml with your talks (lat/lon for the map).")
    print("4. Edit data/professional-activities.md, data/quotes.md, data/fun-facts.md.")
    print("5. Test locally: python -m http.server 8000")
    print("6. Push to GitHub and enable GitHub Pages.")
    print("\nTo regenerate the YAML/Markdown templates, run:")
    print("   python setup_academic_website.py --reset-templates\n")


if __name__ == "__main__":
    main()
