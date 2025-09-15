---
layout: page
title: "Publications"
---

{% assign pubs = site.data.publications | default: empty | sort: "year" | reverse %}
{% assign journals = pubs | where: "type", "journal" %}
{% assign conferences = pubs | where: "type", "conference" %}
{% assign books = pubs | where: "type", "bookchapter" %}

<div class="pubs-layout">
  <nav class="pubs-sidenav">
    <div class="pubs-sidenav__title">Publications</div>
    <a href="#journals">Journals ({{ journals | size }})</a>
    <a href="#conferences">Conferences ({{ conferences | size }})</a>
    <a href="#book-chapters">Book Chapters ({{ books | size }})</a>
    <hr>
    <a href="{{ '/assets/publications.bib.txt' | relative_url }}" target="_blank" rel="noopener">Open BibTeX (all)</a>
  </nav>

  <div class="pubs-content" markdown="1">

## Journal Articles {: #journals data-section="1"}

{% assign years = journals | map: "year" | uniq | sort | reverse %}
{% for y in years %}

### {{ y }}

{% for p in journals %}{% if p.year == y %}
{% assign title_href = p.title_url | default: p.url %}
{% capture authors_display %}
{% assign auth_str = p.authors | default: "" | replace: "…", "" | replace: " ...", "" | replace: "...", "" %}
{% assign auths = auth_str | split: ", " %}
{% if auths.size > 10 %}{{ auths[0] }}, et al.{% else %}{{ auth_str }}{% endif %}
{% endcapture %}

- {% if title_href %}<a href="{{ title_href }}" class="title-link" target="_blank" rel="noopener"><strong>{{ p.title }}</strong></a>{% else %}<strong class="title-link">{{ p.title }}</strong>{% endif %} — {{ authors_display | strip }}. _{{ p.venue }}_, {{ p.year }}{% if p.doi %}. DOI: <a href="https://doi.org/{{ p.doi }}" target="_blank" rel="noopener">{{ p.doi }}</a>{% endif %}{% if p.bibfile_txt or p.bibfile %} — <a href="{{ p.bibfile_txt | default: p.bibfile | relative_url }}" target="_blank" rel="noopener">[Bibtex]</a>{% endif %}
  {% endif %}{% endfor %}
  {% endfor %}

---

## Conference Papers {: #conferences data-section="1"}

{% assign years = conferences | map: "year" | uniq | sort | reverse %}
{% for y in years %}

### {{ y }}

{% for p in conferences %}{% if p.year == y %}
{% assign title_href = p.title_url | default: p.url %}
{% capture authors_display %}
{% assign auth_str = p.authors | default: "" | replace: "…", "" | replace: " ...", "" | replace: "...", "" %}
{% assign auths = auth_str | split: ", " %}
{% if auths.size > 10 %}{{ auths[0] }}, et al.{% else %}{{ auth_str }}{% endif %}
{% endcapture %}

- {% if title_href %}<a href="{{ title_href }}" class="title-link" target="_blank" rel="noopener"><strong>{{ p.title }}</strong></a>{% else %}<strong class="title-link">{{ p.title }}</strong>{% endif %} — {{ authors_display | strip }}. _{{ p.venue }}_, {{ p.year }}{% if p.doi %}. DOI: <a href="https://doi.org/{{ p.doi }}" target="_blank" rel="noopener">{{ p.doi }}</a>{% endif %}{% if p.bibfile_txt or p.bibfile %} — <a href="{{ p.bibfile_txt | default: p.bibfile | relative_url }}" target="_blank" rel="noopener">[Bibtex]</a>{% endif %}
  {% endif %}{% endfor %}
  {% endfor %}

---

## Book Chapters {: #book-chapters data-section="1"}

{% assign years = books | map: "year" | uniq | sort | reverse %}
{% for y in years %}

### {{ y }}

{% for p in books %}{% if p.year == y %}
{% assign title_href = p.title_url | default: p.url %}
{% capture authors_display %}
{% assign auth_str = p.authors | default: "" | replace: "…", "" | replace: " ...", "" | replace: "...", "" %}
{% assign auths = auth_str | split: ", " %}
{% if auths.size > 10 %}{{ auths[0] }}, et al.{% else %}{{ auth_str }}{% endif %}
{% endcapture %}

- {% if title_href %}<a href="{{ title_href }}" class="title-link" target="_blank" rel="noopener"><strong>{{ p.title }}</strong></a>{% else %}<strong class="title-link">{{ p.title }}</strong>{% endif %} — {{ authors_display | strip }}. _{{ p.venue }}_, {{ p.year }}{% if p.doi %}. DOI: <a href="https://doi.org/{{ p.doi }}" target="_blank" rel="noopener">{{ p.doi }}</a>{% endif %}{% if p.bibfile_txt or p.bibfile %} — <a href="{{ p.bibfile_txt | default: p.bibfile | relative_url }}" target="_blank" rel="noopener">[Bibtex]</a>{% endif %}
{% endif %}{% endfor %}
{% endfor %}

  </div>
</div>

<script>
// Optional: highlight the active section link as you scroll
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
