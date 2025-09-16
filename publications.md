---
layout: page
title: "Publications"
---

{% assign pubs = site.data.publications | default: empty %}
{% assign journals    = pubs | where_exp: "p", "p.type == 'journal'" %}
{% assign conferences = pubs | where_exp: "p", "p.type == 'conference'" %}
{% assign books       = pubs | where_exp: "p", "p.type == 'bookchapter'" %}
{% assign techreports = pubs | where_exp: "p", "p.type == 'techreport'" %}

<div class="pubs-layout">

  <!-- Left sidebar -->
  <nav class="pubs-sidenav">
    <div class="pubs-sidenav__title">Publications</div>
    <a href="#journals">Journals ({{ journals | size }})</a>
    <a href="#conferences">Conferences ({{ conferences | size }})</a>
    <a href="#book-chapters">Book Chapters ({{ books | size }})</a>
    <a href="#techreports">Technical Reports ({{ techreports | size }})</a>
    <hr>
    <a href="{{ '/assets/publications.bib.txt' | relative_url }}" target="_blank" rel="noopener">Open BibTeX (all)</a>
    <a href="https://scholar.google.com/citations?user={{ site.scholar_id }}" target="_blank" rel="noopener">Google Scholar</a>
  </nav>

  <!-- Main content -->
  <div class="pubs-content">

    <h2 id="journals" data-section="journals">Journal Papers</h2>
    <ul>
    {% for p in journals %}
      {% assign title_href = p.title_url | default: p.url %}
      {% assign auth_str = p.authors | default: "" | replace: "…", "" | replace: " ...", "" | replace: "...", "" %}
      {% assign auths = auth_str | split: ", " %}
      {% if auths.size > 10 %}
        {% assign authors_display = auths[0] | append: ", et al." %}
      {% else %}
        {% assign authors_display = auth_str %}
      {% endif %}
      <li>
        {% if title_href %}
          <a href="{{ title_href }}" class="title-link" target="_blank" rel="noopener"><strong>{{ p.title }}</strong></a>
        {% else %}
          <strong class="title-link">{{ p.title }}</strong>
        {% endif %}
        — {{ authors_display | strip }}. <em>{{ p.venue }}</em>{% if p.doi %}. DOI: <a href="https://doi.org/{{ p.doi }}" target="_blank" rel="noopener">{{ p.doi }}</a>{% endif %}{% if p.bibfile_txt or p.bibfile %} — <a href="{{ p.bibfile_txt | default: p.bibfile | relative_url }}" target="_blank" rel="noopener">[Bibtex]</a>{% endif %}
      </li>
    {% endfor %}
    </ul>

    <hr>

    <h2 id="conferences" data-section="conferences">Conference Papers</h2>
    <ul>
    {% for p in conferences %}
      {% assign title_href = p.title_url | default: p.url %}
      {% assign auth_str = p.authors | default: "" | replace: "…", "" | replace: " ...", "" | replace: "...", "" %}
      {% assign auths = auth_str | split: ", " %}
      {% if auths.size > 10 %}
        {% assign authors_display = auths[0] | append: ", et al." %}
      {% else %}
        {% assign authors_display = auth_str %}
      {% endif %}
      <li>
        {% if title_href %}
          <a href="{{ title_href }}" class="title-link" target="_blank" rel="noopener"><strong>{{ p.title }}</strong></a>
        {% else %}
          <strong class="title-link">{{ p.title }}</strong>
        {% endif %}
        — {{ authors_display | strip }}. <em>{{ p.venue }}</em>{% if p.doi %}. DOI: <a href="https://doi.org/{{ p.doi }}" target="_blank" rel="noopener">{{ p.doi }}</a>{% endif %}{% if p.bibfile_txt or p.bibfile %} — <a href="{{ p.bibfile_txt | default: p.bibfile | relative_url }}" target="_blank" rel="noopener">[Bibtex]</a>{% endif %}
      </li>
    {% endfor %}
    </ul>

    <hr>

    <h2 id="book-chapters" data-section="book-chapters">Book Chapters</h2>
    <ul>
    {% for p in books %}
      {% assign title_href = p.title_url | default: p.url %}
      {% assign auth_str = p.authors | default: "" | replace: "…", "" | replace: " ...", "" | replace: "...", "" %}
      {% assign auths = auth_str | split: ", " %}
      {% if auths.size > 10 %}
        {% assign authors_display = auths[0] | append: ", et al." %}
      {% else %}
        {% assign authors_display = auth_str %}
      {% endif %}
      <li>
        {% if title_href %}
          <a href="{{ title_href }}" class="title-link" target="_blank" rel="noopener"><strong>{{ p.title }}</strong></a>
        {% else %}
          <strong class="title-link">{{ p.title }}</strong>
        {% endif %}
        — {{ authors_display | strip }}. <em>{{ p.venue }}</em>{% if p.doi %}. DOI: <a href="https://doi.org/{{ p.doi }}" target="_blank" rel="noopener">{{ p.doi }}</a>{% endif %}{% if p.bibfile_txt or p.bibfile %} — <a href="{{ p.bibfile_txt | default: p.bibfile | relative_url }}" target="_blank" rel="noopener">[Bibtex]</a>{% endif %}
      </li>
    {% endfor %}
    </ul>

    <hr>

    <h2 id="techreports" data-section="techreports">Technical Reports</h2>
    <ul>
    {% for p in techreports %}
      {% assign title_href = p.title_url | default: p.url %}
      {% assign auth_str = p.authors | default: "" | replace: "…", "" | replace: " ...", "" | replace: "...", "" %}
      {% assign auths = auth_str | split: ", " %}
      {% if auths.size > 10 %}
        {% assign authors_display = auths[0] | append: ", et al." %}
      {% else %}
        {% assign authors_display = auth_str %}
      {% endif %}
      <li>
        {% if title_href %}
          <a href="{{ title_href }}" class="title-link" target="_blank" rel="noopener"><strong>{{ p.title }}</strong></a>
        {% else %}
          <strong class="title-link">{{ p.title }}</strong>
        {% endif %}
        — {{ authors_display | strip }}. <em>{{ p.venue }}</em>{% if p.doi %}. DOI: <a href="https://doi.org/{{ p.doi }}" target="_blank" rel="noopener">{{ p.doi }}</a>{% endif %}{% if p.bibfile_txt or p.bibfile %} — <a href="{{ p.bibfile_txt | default: p.bibfile | relative_url }}" target="_blank" rel="noopener">[Bibtex]</a>{% endif %}
      </li>
    {% endfor %}
    </ul>

  </div>
</div>

<script>
// Optional: highlight active link while scrolling
(function () {
  const links = Array.from(document.querySelectorAll('.pubs-sidenav a[href^="#"]'));
  const map = new Map(links.map(a => [a.getAttribute('href').slice(1), a]));
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      const link = map.get(e.target.id);
      if (link) link.classList.toggle('active', e.isIntersecting);
    });
  }, { rootMargin: '0px 0px -65% 0px', threshold: 0.1 });
  document.querySelectorAll('[data-section]').forEach(sec => obs.observe(sec));
})();
</script>
