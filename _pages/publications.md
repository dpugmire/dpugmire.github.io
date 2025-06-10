---
layout: single
title: "Publications"
permalink: /publications/
author_profile: true
---

[Journal Articles](#journal-articles) • [Conference Papers](#conference-papers) • [Book Chapters](#book-chapters) • [Technical Reports](#technical-reports)

{% assign journals = site.data.publications_journals %}
{% assign conferences = site.data.publications_conferences %}
{% assign books = site.data.publications_books %}
{% assign tech_reports = site.data.publications_techreports %}

### Journal Articles {#journal-articles}

<ul>
{% for pub in journals %}
  <li>
    <strong>{{ pub.title }}</strong>,
    {{ pub.citation }}
    {% if pub.doi %}
    <a href="https://doi.org/{{ pub.doi }}" target="_blank" rel="noopener noreferrer">
        https://doi.org/{{ pub.doi }}
    </a>
    {% endif %}
    {% if pub.bibtex %}
      <button onclick="copyBibtex('bibtex-{{ forloop.index }}')">Cite</button>
      <pre id="bibtex-{{ forloop.index }}" style="display: none;">{{ pub.bibtex }}</pre>
    {% endif %}
  </li>
{% endfor %}
</ul>

### Conference Papers {#conference-papers}

<ul>
{% for pub in conferences %}
  <li>
    <strong>{{ pub.title }}</strong>,
    {{ pub.citation }}
    {% if pub.doi %}
    <a href="https://doi.org/{{ pub.doi }}" target="_blank" rel="noopener noreferrer">
        https://doi.org/{{ pub.doi }}
    </a>
    {% endif %}
    {% if pub.bibtex %}
      <button onclick="copyBibtex('bibtex-{{ forloop.index }}')">Cite</button>
      <pre id="bibtex-{{ forloop.index }}" style="display: none;">{{ pub.bibtex }}</pre>
    {% endif %}
  </li>
{% endfor %}
</ul>

### Book Chapters {#book-chapters}

<ul>
{% for pub in books %}
  <li>
    <strong>{{ pub.title }}</strong>,
    {{ pub.citation }}
    {% if pub.doi %}
    <a href="https://doi.org/{{ pub.doi }}" target="_blank" rel="noopener noreferrer">
        https://doi.org/{{ pub.doi }}
    </a>
    {% endif %}
    {% if pub.bibtex %}
      <button onclick="copyBibtex('bibtex-{{ forloop.index }}')">Cite</button>
      <pre id="bibtex-{{ forloop.index }}" style="display: none;">{{ pub.bibtex }}</pre>
    {% endif %}
  </li>
{% endfor %}
</ul>

### Technical Reports {#technical-reports}

<ul>
{% for pub in tech_reports %}
  <li>
    <strong>{{ pub.title }}</strong>,
    {{ pub.citation }}
    {% if pub.doi %}
    <a href="https://doi.org/{{ pub.doi }}" target="_blank" rel="noopener noreferrer">
        https://doi.org/{{ pub.doi }}
    </a>
    {% endif %}
    {% if pub.bibtex %}
      <button onclick="copyBibtex('bibtex-{{ forloop.index }}')">Cite</button>
      <pre id="bibtex-{{ forloop.index }}" style="display: none;">{{ pub.bibtex }}</pre>
    {% endif %}
  </li>
{% endfor %}
</ul>

<script>
function copyBibtex(id) {
  const pre = document.getElementById(id);
  const text = pre.textContent;
  navigator.clipboard.writeText(text).then(() => {
    alert("BibTeX copied to clipboard!");
  }, () => {
    alert("Failed to copy BibTeX.");
  });
}
</script>
