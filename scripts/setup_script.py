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
        'data',
        'images/papers',
        'slides',
        'scripts',
        'cv'
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
    <title>Dr. David R. Pugmire</title>

    <!-- js-yaml for loading YAML data -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/js-yaml/4.1.0/js-yaml.min.js"></script>

    <!-- marked.js for rendering Markdown -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

    <!-- Leaflet CSS & JS for talk map -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --topbar-height: 220px; /* set precisely by JS at runtime */
        }

        /* Make anchor navigation land below sticky topbar */
        html {
            scroll-padding-top: calc(var(--topbar-height) + 16px);
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }

        /* Top bar (header + nav) stays visible while scrolling */
        .topbar {
            position: sticky;
            top: 0;
            z-index: 1000;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        header {
            background: white;
            padding: 2rem;
        }

        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        h1 { font-size: 2rem; margin-bottom: 0.5rem; }
        .subtitle { color: #666; font-size: 1.1rem; }

        .contact-links { display: flex; gap: 1rem; }
        .contact-links a {
            color: #0066cc;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border: 1px solid #0066cc;
            border-radius: 4px;
            transition: all 0.3s;
        }
        .contact-links a:hover { background: #0066cc; color: white; }

        nav {
            background: white;
            border-top: 1px solid #eee;
            border-bottom: 2px solid #eee;
        }

        nav ul {
            max-width: 1200px;
            margin: 0 auto;
            list-style: none;
            display: flex;
            gap: 2rem;
            padding: 0 2rem;
        }

        nav a {
            display: block;
            padding: 1rem 0;
            text-decoration: none;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }

        nav a:hover, nav a.active {
            color: #0066cc;
            border-bottom-color: #0066cc;
        }

        main { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }

        section {
            background: white;
            padding: 2rem;
            margin-bottom: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            display: none;
        }
        section.active { display: block; }

        h2 {
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
            color: #222;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 0.5rem;
        }

        h3 { font-size: 1.3rem; margin: 2rem 0 1rem 0; color: #444; }

        .category-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            border-left: 4px solid #0066cc;
            padding-left: 1rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }

        .category-count {
            background: #0066cc;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.9rem;
        }

        .publication {
            display: flex;
            gap: 1.5rem;
            margin-bottom: 2rem;
            padding: 1.5rem;
            border: 1.5px solid #ddd;
            border-radius: 8px;
            transition: box-shadow 0.3s;
            background: #fff;
        }
        .publication:hover { box-shadow: 0 4px 8px rgba(0,0,0,0.1); }

        /* Thumbnail box for paper images */
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
            color: #999;
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

        /* Citation line + inline links */
        .pub-citation {
            color: #555;
            margin-bottom: 0.75rem;
            line-height: 1.45;
        }

        .pub-links a {
            text-decoration: none;
            margin-left: 0.35em;
            font-size: 0.95em;
            color: #0066cc;
        }
        .pub-links a:hover { text-decoration: underline; }

        .pub-summary { color: #555; margin-bottom: 0.75rem; line-height: 1.5; }
        .pub-note { margin-top: 0.25rem; font-weight: 600; color: #444; }

        /* BibTeX block */
        .bibtex-container {
            display: none;
            margin-top: 0.75rem;
            background: #f8f8f8;
            padding: 1rem;
            border-radius: 4px;
            border-left: 3px solid #0066cc;
        }
        .bibtex-container.show { display: block; }

        .bibtex-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }

        .bibtex-code {
            background: white;
            padding: 1rem;
            border-radius: 4px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            white-space: pre-wrap;
            margin: 0;
        }

        /* Small button style used only for Copy */
        .btn {
            padding: 0.35rem 0.65rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.85rem;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.3s;
            background: #f0f0f0;
            color: #333;
        }
        .btn:hover { background: #e0e0e0; }

        /* Abstract toggle */
        .pub-abstract { margin-top: 0.5rem; }
        .pub-abstract summary { cursor: pointer; user-select: none; color: #0066cc; }
        .pub-abstract summary:hover { text-decoration: underline; }

        /* NEW: keep long abstracts from widening the page */
        .pub-abstract-body {
            margin-top: 0.35rem;
            color: #555;

            white-space: pre-wrap;      /* preserve newlines, wrap long lines */
            overflow-wrap: anywhere;    /* break very long tokens/urls */
            word-break: break-word;

            max-width: 900px;           /* optional, match your bibtex-container */
        }

        /* Talks section */
        #talk-map { height: 520px; margin: 1rem 0; border-radius: 8px; overflow: hidden; }
        .talk-item { padding: 1rem; border-left: 4px solid #10b981; margin-bottom: 1rem; background: #f9f9f9; }
        .talk-title { font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem; }
        .talk-details { color: #666; font-size: 0.95rem; }

        /* Markdown containers */
        .markdown-body { line-height: 1.7; }
        .markdown-body h1, .markdown-body h2, .markdown-body h3 {
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }
        .markdown-body ul { margin-left: 1.25rem; margin-bottom: 1rem; }
        .markdown-body p { margin-bottom: 0.75rem; }

        /* Markdown tables: add breathing room between columns */
        .markdown-body table {
            border-collapse: separate;   /* allow padding to feel like column spacing */
            border-spacing: 0;           /* keep clean look */
            margin: 0.75rem 0 1rem 0;
            line-height: 1.4;
        }
        .markdown-body th,
        .markdown-body td {
            padding: 0.2rem 0.9rem;      /* general cell padding */
            vertical-align: top;
        }
        .markdown-body th:first-child,
        .markdown-body td:first-child {
            padding-right: 2.5rem;       /* increase space between col 1 and col 2 */
            white-space: nowrap;
            font-variant-numeric: tabular-nums;
        }

        footer { text-align: center; padding: 2rem; background: white; color: #666; margin-top: 3rem; }

        /* Publications section header */
        .pub-header {
            position: sticky;
            top: var(--topbar-height);
            background: white;
            padding: 1rem 0;
            border-bottom: 3px solid #0066cc;
            z-index: 50;
            display: flex;
            align-items: center;
            gap: 2rem;
        }

        .pub-header h2 { font-size: 1.8rem; margin: 0; color: #222; border: none; padding: 0; }

        .pub-nav { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
        .pub-nav a {
            color: #0066cc;
            text-decoration: none;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            transition: background 0.3s;
            font-size: 0.95rem;
        }
        .pub-nav a:hover { background: #f0f0f0; }
    </style>
</head>
<body>
    <div class="topbar" id="topbar">
        <header>
            <div class="header-content">
                <div>
                    <h1>Dr. David R. Pugmire</h1>
                    <div class="subtitle">Distinguished Research Scientist</div>
                    <div class="subtitle">Oak Ridge National Laboratory</div>
                </div>
                <div class="contact-links">
                    <a href="mailto:your.email@university.edu">Email</a>
                    <a href="https://github.com/yourusername" target="_blank" rel="noopener noreferrer">GitHub</a>
                    <a href="cv/cv.pdf" target="_blank" rel="noopener noreferrer">CV</a>
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
                <li><a href="#fun-facts" class="nav-link">Fun Facts</a></li>
                <li><a href="#quotes" class="nav-link">Quotes</a></li>
            </ul>
        </nav>
    </div>

    <main>
        <section id="about" class="active">
            <!-- No "About Me" heading here -->
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

        <section id="fun-facts">
            <h2>Fun Facts</h2>
            <div id="fun-facts-content" class="markdown-body">
                <p>Loading fun facts…</p>
            </div>
        </section>

        <section id="quotes">
            <h2>Quotes</h2>
            <div id="quotes-content" class="markdown-body">
                <p>Loading quotes…</p>
            </div>
        </section>
    </main>

    <footer>
        <p>&copy; 2025 Dr. David R. Pugmire. All rights reserved.</p>
    </footer>

    <script>
        function updateTopbarHeightVar() {
            const topbar = document.getElementById('topbar');
            if (!topbar) return;
            const h = topbar.getBoundingClientRect().height;
            document.documentElement.style.setProperty('--topbar-height', Math.ceil(h) + 'px');
        }
        window.addEventListener('resize', updateTopbarHeightVar);
        updateTopbarHeightVar();

        // Navigation: show/hide sections (only for in-page nav links)
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = e.target.getAttribute('href').substring(1);
                document.querySelectorAll('section').forEach(s => s.classList.remove('active'));
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                document.getElementById(target).classList.add('active');
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

        async function loadMarkdown(url, containerId, fallbackMessage) {
            const container = document.getElementById(containerId);
            try {
                const resp = await fetch(url);
                if (!resp.ok) {
                    container.innerHTML = '<p>' + fallbackMessage + '</p>';
                    return;
                }
                const text = await resp.text();
                container.innerHTML = marked.parse(text);
            } catch (err) {
                console.error('Error loading ' + url + ':', err);
                container.innerHTML = '<p>' + fallbackMessage + '</p>';
            }
        }

        // HTML-escape helper
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
            bibtex += '  title = {' + (pub.title || '') + '},\n';
            bibtex += '  author = {' + (pub.authors || '') + '},\n';

            if (pub.editors) {
                bibtex += '  editor = {' + pub.editors + '},\n';
            }

            bibtex += '  ' + venueKey + ' = {' + (pub.venue || '') + '},\n';
            bibtex += '  year = {' + (pub.year || '') + '}';

            if (pub.doi) {
                bibtex += ',\n  doi = {' + pub.doi + '}';
            }

            if (pub.note) {
                bibtex += ',\n  note = {' + pub.note + '}';
            }

            bibtex += '\n}';
            return bibtex;
        }

        function toggleBibtex(id) {
            const el = document.getElementById('bibtex-' + id);
            if (el) el.classList.toggle('show');
        }

        async function copyTextToClipboard(text) {
            try {
                await navigator.clipboard.writeText(text);
                return true;
            } catch (e) {
                // Fallback for older browsers / some local contexts
                const ta = document.createElement('textarea');
                ta.value = text;
                ta.style.position = 'fixed';
                ta.style.left = '-9999px';
                document.body.appendChild(ta);
                ta.select();
                let ok = false;
                try {
                    ok = document.execCommand('copy');
                } catch (_) {
                    ok = false;
                }
                document.body.removeChild(ta);
                return ok;
            }
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
                'journal':      { name: 'Journal Articles',    color: '#0066cc', pubs: [] },
                'conference':   { name: 'Conference Papers',  color: '#10b981', pubs: [] },
                'workshop':     { name: 'Workshop Papers',    color: '#f59e0b', pubs: [] },
                'book-chapter': { name: 'Book Chapters',      color: '#8b5cf6', pubs: [] },
                'preprint':     { name: 'Preprints',          color: '#ec4899', pubs: [] },
                'other':        { name: 'Other Publications', color: '#6b7280', pubs: [] }
            };

            pubs.forEach(pub => {
                const t = pub.type || 'other';
                (types[t] ? types[t].pubs : types['other'].pubs).push(pub);
            });

            Object.values(types).forEach(type => {
                type.pubs.sort((a, b) => (parseInt(b.year || '0', 10) - parseInt(a.year || '0', 10)));
            });

            const doiHtml = (doi) => {
                const d = String(doi || '').trim();
                if (!d) return '';
                const url = 'https://doi.org/' + d;
                return ' doi: <a href="' + url + '" target="_blank" rel="noopener noreferrer">' + escHtml(d) + '</a>';
            };

            let html = '';

            Object.entries(types).forEach(([key, type]) => {
                if (type.pubs.length === 0) return;

                html += '<div id="pub-' + key + '" class="category-header" style="border-left-color: ' + type.color + '">';
                html += '  <h3>' + escHtml(type.name) + '</h3>';
                html += '  <span class="category-count" style="background: ' + type.color + '">' + type.pubs.length + '</span>';
                html += '</div>';

                type.pubs.forEach(pub => {
                    const id = pub.id;
                    const bibtex = generateBibtex(pub);
                    const bibtexEsc = escHtml(bibtex);

                    const paperUrl = pub.paper_url || (pub.doi ? ('https://doi.org/' + pub.doi) : null);

                    // Citation: authors. "title." venue year. + DOI appended at end
                    const pieces = [];
                    if (pub.authors) pieces.push(escHtml(pub.authors) + '.');
                    if (pub.title) pieces.push('"' + escHtml(pub.title) + '."');
                    if (pub.venue) pieces.push('<i>' + escHtml(pub.venue) + '</i>');
                    if (pub.year) pieces.push(escHtml(String(pub.year)) + '.');

                    const citationBase = pieces.join(' ');

                    // Inline [Paper] [BibTeX] on same line
                    let links = '<span class="pub-links">';
                    if (paperUrl) {
                        links += ' <a href="' + paperUrl + '" target="_blank" rel="noopener noreferrer">[Paper]</a>';
                    }
                    links += ' <a href="#" class="bibtex-toggle" data-pub-id="' + escHtml(id) + '">[BibTeX]</a>';
                    links += '</span>';

                    html += '<div class="publication">';
                    html += '  <div class="pub-image">';
                    if (pub.image) {
                        html += '    <img src="images/papers/' + escHtml(pub.image) + '" alt="' + escHtml(pub.title || '') + '">';
                    } else {
                        html += '    No image';
                    }
                    html += '  </div>';

                    html += '  <div class="pub-content">';
                    html += '    <div class="pub-citation">' + citationBase + doiHtml(pub.doi) + links + '</div>';

                    if (pub.summary) {
                        html += '    <div class="pub-summary">' + escHtml(pub.summary) + '</div>';
                    }
                    if (pub.note) {
                        html += '    <div class="pub-note"><strong>' + escHtml(pub.note) + '</strong></div>';
                    }

                    // Abstract toggle if present
                    if (pub.abstract) {
                        html += '    <details class="pub-abstract">';
                        html += '      <summary>Abstract</summary>';
                        html += '      <div class="pub-abstract-body">' + escHtml(pub.abstract) + '</div>';
                        html += '    </details>';
                    }

                    // BibTeX block
                    html += '    <div id="bibtex-' + escHtml(id) + '" class="bibtex-container">';
                    html += '      <div class="bibtex-header"><strong>BibTeX Citation</strong>';
                    html += '        <button id="copy-btn-' + escHtml(id) + '" class="btn bibtex-copy" data-pub-id="' + escHtml(id) + '">Copy</button>';
                    html += '      </div>';
                    html += '      <pre class="bibtex-code" id="bibtex-code-' + escHtml(id) + '">' + bibtexEsc + '</pre>';
                    html += '    </div>';

                    html += '  </div>';
                    html += '</div>';
                });
            });

            container.innerHTML = html;

            // Wire up [BibTeX] toggles
            container.querySelectorAll('a.bibtex-toggle').forEach(a => {
                a.addEventListener('click', (e) => {
                    e.preventDefault();
                    toggleBibtex(a.dataset.pubId);
                });
            });

            // Wire up Copy buttons
            container.querySelectorAll('button.bibtex-copy').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const id = btn.dataset.pubId;
                    const pre = document.getElementById('bibtex-code-' + id);
                    const ok = await copyTextToClipboard(pre ? pre.innerText : '');
                    const original = btn.textContent;
                    btn.textContent = ok ? '✓ Copied!' : 'Copy failed';
                    setTimeout(() => { btn.textContent = original; }, 1500);
                });
            });

            const links = document.getElementById('publication-links');
            if (links) links.style.display = 'flex';
        }

        async function renderTalks() {
            const container = document.getElementById('talks-content');

            // Load all three categories (each file contains: talks: [ ... ])
            const [keynotesData, talksData, tutorialsData] = await Promise.all([
                loadYAML('data/keynotes.yaml'),
                loadYAML('data/talks.yaml'),
                loadYAML('data/tutorials.yaml'),
            ]);

            const keynotes = (keynotesData && keynotesData.talks) ? keynotesData.talks : [];
            const talks = (talksData && talksData.talks) ? talksData.talks : [];
            const tutorials = (tutorialsData && tutorialsData.talks) ? tutorialsData.talks : [];

            const tag = (arr, cat) => (arr || []).map(t => Object.assign({ _category: cat }, t));
            const all = [
                ...tag(keynotes, 'Keynote'),
                ...tag(talks, 'Talk'),
                ...tag(tutorials, 'Tutorial'),
            ];

            if (all.length === 0) {
                container.innerHTML = '<p>No talks found. Check data/keynotes.yaml, data/talks.yaml, data/tutorials.yaml</p>';
                return;
            }

            const renderList = (items) => {
                if (!items || items.length === 0) return '<p style="color:#666;">None yet.</p>';

                let h = '';
                items.slice().sort((a, b) => new Date(b.date) - new Date(a.date)).forEach(function(talk) {
                    const formattedDate = talk.date
                        ? new Date(talk.date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
                        : '';

                    h += '<div class="talk-item">';
                    h += '<div class="talk-title">' + escHtml(talk.title) + '</div>';
                    h += '<div class="talk-details">';
                    if (talk._category) h += '🏷️ ' + escHtml(talk._category) + '<br>';

                    const locParts = [];
                    if (talk.venue) locParts.push(talk.venue);
                    if (talk.city) locParts.push(talk.city);
                    if (talk.country) locParts.push(talk.country);
                    if (locParts.length > 0) h += '📍 ' + escHtml(locParts.join(', ')) + '<br>';
                    if (formattedDate) h += '📅 ' + escHtml(formattedDate);
                    if (talk.slides) {
                        h += '<br>📊 <a href="slides/' + encodeURIComponent(talk.slides) + '" target="_blank" rel="noopener noreferrer">View Slides</a>';
                    }
                    h += '</div></div>';
                });

                return h;
            };

            let html = '';
            html += '<div id="talk-map"></div>';

            html += '<div class="category-header" style="border-left-color:#8b5cf6;">';
            html += '  <h3>Keynotes</h3>';
            html += '  <span class="category-count" style="background:#8b5cf6;">' + keynotes.length + '</span>';
            html += '</div>';
            html += renderList(tag(keynotes, 'Keynote'));

            html += '<div class="category-header" style="border-left-color:#10b981;">';
            html += '  <h3>Talks</h3>';
            html += '  <span class="category-count" style="background:#10b981;">' + talks.length + '</span>';
            html += '</div>';
            html += renderList(tag(talks, 'Talk'));

            html += '<div class="category-header" style="border-left-color:#f59e0b;">';
            html += '  <h3>Tutorials</h3>';
            html += '  <span class="category-count" style="background:#f59e0b;">' + tutorials.length + '</span>';
            html += '</div>';
            html += renderList(tag(tutorials, 'Tutorial'));

            container.innerHTML = html;

            // Map pins from ALL categories
            const sortedAll = all.slice().sort((a, b) => new Date(b.date) - new Date(a.date));

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
            sortedAll.forEach(function(t) {
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
                    const catPart = t._category ? ' <span style="color:#666;">(' + escHtml(t._category) + ')</span>' : '';
                    const parts = [];
                    if (t.venue) parts.push(t.venue);
                    if (t.city) parts.push(t.city);
                    if (t.country) parts.push(t.country);
                    const locPart = parts.length ? ', ' + escHtml(parts.join(', ')) : '';
                    const linkPart = t.slides
                        ? ' — <a href="slides/' + encodeURIComponent(t.slides) + '" target="_blank" rel="noopener noreferrer">slides</a>'
                        : '';
                    return '• <b>' + escHtml(t.title) + '</b>' + catPart + datePart + locPart + linkPart;
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

        async function renderProfessionalActivities() {
            await loadMarkdown(
                'data/professional-activities.md',
                'professional-activities-content',
                'Could not load professional activities. Ensure data/professional-activities.md exists.'
            );
        }

        async function renderAbout() {
            await loadMarkdown(
                'data/about.md',
                'about-content',
                'Could not load about information. Ensure data/about.md exists.'
            );
        }

        async function renderFunFacts() {
            await loadMarkdown(
                'data/fun-facts.md',
                'fun-facts-content',
                'Could not load fun facts. Ensure data/fun-facts.md exists.'
            );
        }

        async function renderQuotes() {
            await loadMarkdown(
                'data/quotes.md',
                'quotes-content',
                'Could not load quotes. Ensure data/quotes.md exists.'
            );
        }

        let aboutLoaded = false;
        let publicationsLoaded = false;
        let talksLoaded = false;
        let professionalActivitiesLoaded = false;
        let funFactsLoaded = false;
        let quotesLoaded = false;

        // Attach lazy-loading behavior
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                const target = e.target.getAttribute('href').substring(1);
                if (target === 'about' && !aboutLoaded) {
                    renderAbout();
                    aboutLoaded = true;
                }
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
                if (target === 'fun-facts' && !funFactsLoaded) {
                    renderFunFacts();
                    funFactsLoaded = true;
                }
                if (target === 'quotes' && !quotesLoaded) {
                    renderQuotes();
                    quotesLoaded = true;
                }
            });
        });

        // Preload About + Professional Activities on first load
        renderAbout();
        aboutLoaded = true;
        renderProfessionalActivities();
        professionalActivitiesLoaded = true;
    </script>
</body>
</html>'''

    with open('index.html', 'w', encoding='utf-8') as f:
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
    type: journal  # journal, conference, workshop, book-chapter, preprint, other
    doi: "10.1038/nm.2024.001"
    paper_url: "https://doi.org/10.1038/nm.2024.001"
    summary: "We develop a deep learning framework for cancer detection."
    abstract: "This paper introduces ... (full abstract here)."

  - id: smith2023vision
    title: "Vision Transformers at Scale"
    authors: "Smith, J., Davis, C."
    venue: "NeurIPS"
    year: 2023
    type: conference
    doi: "10.48550/arXiv.2301.12345"
    summary: "Efficient vision transformers for high-resolution images."
    # abstract: "Optional abstract..."

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
#    abstract: "Optional abstract text..."
#    image: "yourname2024.jpg"
#    # note: "Best Paper Award"
'''

    os.makedirs('data', exist_ok=True)
    with open('data/publications.yaml', 'w', encoding='utf-8') as f:
        f.write(yaml_content)

    print("  ✓ Wrote data/publications.yaml\n")


def create_talks_yaml(overwrite=False):
    """Create or overwrite talks.yaml template (Talks category)."""
    action = "Overwriting" if overwrite else "Creating"
    print(f"{action} data/talks.yaml...")

    yaml_content = '''# talks.yaml
# Talks
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

    os.makedirs('data', exist_ok=True)
    with open('data/talks.yaml', 'w', encoding='utf-8') as f:
        f.write(yaml_content)

    print("  ✓ Wrote data/talks.yaml\n")


def create_keynotes_yaml(overwrite=False):
    """Create or overwrite keynotes.yaml template (Keynotes category)."""
    action = "Overwriting" if overwrite else "Creating"
    print(f"{action} data/keynotes.yaml...")

    yaml_content = '''# keynotes.yaml
# Keynotes
# lat/lon are used to place pins on the Leaflet world map in the Talks section.

talks:
  - title: "Keynote Title"
    venue: "Conference / Event"
    city: "City, ST"
    country: "USA"
    date: "2024-01-01"
    lat: 0.0
    lon: 0.0
    slides: "keynote.pdf"

# Template - copy and fill in:
#  - title: "Keynote Title"
#    venue: "Conference / Event"
#    city: "City"
#    country: "Country"
#    date: "YYYY-MM-DD"
#    lat: 00.0000      # latitude (used for map pin)
#    lon: 00.0000      # longitude (used for map pin)
#    slides: "file.pdf"
#    # optional:
#    # location: "Custom location label for popup"
'''

    os.makedirs('data', exist_ok=True)
    with open('data/keynotes.yaml', 'w', encoding='utf-8') as f:
        f.write(yaml_content)

    print("  ✓ Wrote data/keynotes.yaml\n")


def create_tutorials_yaml(overwrite=False):
    """Create or overwrite tutorials.yaml template (Tutorials category)."""
    action = "Overwriting" if overwrite else "Creating"
    print(f"{action} data/tutorials.yaml...")

    yaml_content = '''# tutorials.yaml
# Tutorials
# lat/lon are used to place pins on the Leaflet world map in the Talks section.

talks:
  - title: "Neural Networks Tutorial"
    venue: "MIT CSAIL"
    city: "Cambridge, MA"
    country: "USA"
    date: "2024-02-10"
    lat: 42.3601
    lon: -71.0902

# Template - copy and fill in:
#  - title: "Tutorial Title"
#    venue: "School / Workshop"
#    city: "City"
#    country: "Country"
#    date: "YYYY-MM-DD"
#    lat: 00.0000      # latitude (used for map pin)
#    lon: 00.0000      # longitude (used for map pin)
#    slides: "file.pdf"
#    # optional:
#    # location: "Custom location label for popup"
'''

    os.makedirs('data', exist_ok=True)
    with open('data/tutorials.yaml', 'w', encoding='utf-8') as f:
        f.write(yaml_content)

    print("  ✓ Wrote data/tutorials.yaml\n")


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

---

## Conference & Workshop Organization

- **[Conference / Workshop Name]**, [Year], [Location]  
  Role: [General Chair / Program Chair / etc.]  
  Notes: Brief description (e.g., size, focus area, notable aspects).

---

## Editorial Boards & Reviewing

- **[Journal Name]** — [Editorial Role], [Years]  
  Brief description (e.g., handled submissions in visualization and HCI).

---

_Last updated: YYYY-MM-DD_
'''

    os.makedirs('data', exist_ok=True)
    with open('data/professional-activities.md', 'w', encoding='utf-8') as f:
        f.write(content)

    print("  ✓ Wrote data/professional-activities.md\n")


def create_about_md(overwrite=False):
    """Create or overwrite data/about.md template."""
    action = "Overwriting" if overwrite else "Creating"
    print(f"{action} data/about.md...")

    # No "# About Me" header to avoid showing "About Me" at the top.
    content = '''I am a researcher specializing in machine learning and scientific visualization.
My work focuses on developing methods and tools that help scientists understand
and explore large and complex datasets.

## Research Interests

- Scientific visualization
- High-performance computing
- Machine learning for large-scale data
- Uncertainty quantification and visual analytics
'''

    os.makedirs('data', exist_ok=True)
    with open('data/about.md', 'w', encoding='utf-8') as f:
        f.write(content)

    print("  ✓ Wrote data/about.md\n")


def create_fun_facts_md(overwrite=False):
    """Create or overwrite data/fun-facts.md template."""
    action = "Overwriting" if overwrite else "Creating"
    print(f"{action} data/fun-facts.md...")

    content = '''# Fun Facts

- I enjoy working on woodworking projects in my spare time.
- I love watching college football in the fall.
- I have a soft spot for cats and their very specific opinions about everything.
- When I'm not at the computer, I'm probably lifting weights or reading.
'''

    os.makedirs('data', exist_ok=True)
    with open('data/fun-facts.md', 'w', encoding='utf-8') as f:
        f.write(content)

    print("  ✓ Wrote data/fun-facts.md\n")


def create_quotes_md(overwrite=False):
    """Create or overwrite data/quotes.md template."""
    action = "Overwriting" if overwrite else "Creating"
    print(f"{action} data/quotes.md...")

    content = '''# Favorite Quotes

> "Not everything that can be counted counts, and not everything that counts can be counted."

> "In theory, theory and practice are the same. In practice, they are not."

> "The important thing is not to stop questioning." — Albert Einstein
'''

    os.makedirs('data', exist_ok=True)
    with open('data/quotes.md', 'w', encoding='utf-8') as f:
        f.write(content)

    print("  ✓ Wrote data/quotes.md\n")


def create_readme():
    """Create README (always overwritten)."""
    print("Creating README.md...")

    readme = '''# Academic Website

## Quick Start

1. Edit `data/about.md` with your bio and research overview.
2. Edit `data/publications.yaml` with your publications (optionally include `abstract`).
3. Edit `data/keynotes.yaml`, `data/talks.yaml`, and `data/tutorials.yaml` (including lat/lon for the map).
4. Edit `data/professional-activities.md` with your professional service.
5. Optionally edit `data/fun-facts.md` and `data/quotes.md`.
6. Run locally: `python -m http.server 8000`
7. Open: http://localhost:8000

## Structure

- `index.html`                      - Main website (single-page app)
- `data/about.md`                   - About/Bio (Markdown)
- `data/publications.yaml`          - Publications
- `data/keynotes.yaml`              - Keynotes (drives the Leaflet map and list)
- `data/talks.yaml`                 - Talks (drives the Leaflet map and list)
- `data/tutorials.yaml`             - Tutorials (drives the Leaflet map and list)
- `data/professional-activities.md` - Professional activities (Markdown)
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
'''

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme)

    print("  ✓ Created README.md\n")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Set up an academic website (HTML, YAML/Markdown templates, and structure)."
    )
    parser.add_argument(
        '--reset-templates',
        action='store_true',
        help="Recreate data/*.yaml and data/*.md even if they already exist."
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
    pubs_path = 'data/publications.yaml'
    if args.reset_templates or not os.path.exists(pubs_path):
        create_publications_yaml(overwrite=args.reset_templates)
    else:
        print(f"Skipping {pubs_path} (already exists). Use --reset-templates to regenerate.\n")

    # keynotes.yaml
    keynotes_path = 'data/keynotes.yaml'
    if args.reset_templates or not os.path.exists(keynotes_path):
        create_keynotes_yaml(overwrite=args.reset_templates)
    else:
        print(f"Skipping {keynotes_path} (already exists). Use --reset-templates to regenerate.\n")

    # talks.yaml
    talks_path = 'data/talks.yaml'
    if args.reset_templates or not os.path.exists(talks_path):
        create_talks_yaml(overwrite=args.reset_templates)
    else:
        print(f"Skipping {talks_path} (already exists). Use --reset-templates to regenerate.\n")

    # tutorials.yaml
    tutorials_path = 'data/tutorials.yaml'
    if args.reset_templates or not os.path.exists(tutorials_path):
        create_tutorials_yaml(overwrite=args.reset_templates)
    else:
        print(f"Skipping {tutorials_path} (already exists). Use --reset-templates to regenerate.\n")

    # professional-activities.md
    pa_path = 'data/professional-activities.md'
    if args.reset_templates or not os.path.exists(pa_path):
        create_professional_activities_md(overwrite=args.reset_templates)
    else:
        print(f"Skipping {pa_path} (already exists). Use --reset-templates to regenerate.\n")

    # about.md
    about_path = 'data/about.md'
    if args.reset_templates or not os.path.exists(about_path):
        create_about_md(overwrite=args.reset_templates)
    else:
        print(f"Skipping {about_path} (already exists). Use --reset-templates to regenerate.\n")

    # fun-facts.md
    fun_facts_path = 'data/fun-facts.md'
    if args.reset_templates or not os.path.exists(fun_facts_path):
        create_fun_facts_md(overwrite=args.reset_templates)
    else:
        print(f"Skipping {fun_facts_path} (already exists). Use --reset-templates to regenerate.\n")

    # quotes.md
    quotes_path = 'data/quotes.md'
    if args.reset_templates or not os.path.exists(quotes_path):
        create_quotes_md(overwrite=args.reset_templates)
    else:
        print(f"Skipping {quotes_path} (already exists). Use --reset-templates to regenerate.\n")

    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run your bibtex_to_yaml.py to regenerate data/publications.yaml (include abstract if available).")
    print("2. Edit the markdown files in data/ (about, professional-activities, fun-facts, quotes).")
    print("3. Edit talk files in data/ (keynotes.yaml, talks.yaml, tutorials.yaml).")
    print("4. Test locally: python -m http.server 8000")
    print("5. Push to GitHub and enable GitHub Pages.")
    print("\nTo regenerate the YAML/Markdown templates, run:")
    print("   python setup_academic_website.py --reset-templates\n")


if __name__ == '__main__':
    main()
