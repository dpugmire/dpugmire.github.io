---
layout: single
title: "Publications"
permalink: /publications/
author_profile: true
---

{% assign journals = site.data.publications_journals %}
{% assign conferences = site.data.publications_conferences %}
{% assign books = site.data.publications_books %}

### 📘 Journal Articles TMP

<ul>
{% for pub in journals %}
  <li>
    <strong>{{ pub.title }}</strong><br>
    {{ pub.authors }}<br>
    <em>{{ pub.journal }}</em>, {{ pub.year }}.<br>
    {% if pub.url %}
      <a href="{{ pub.url }}">[PDF]</a>
    {% endif %}
    {% if pub.bibtex %}
      <button onclick="copyBibtex('bibtex-{{ forloop.index }}')">Copy BibTeX</button>
      <pre id="bibtex-{{ forloop.index }}" style="display: none;">{{ pub.bibtex }}</pre>
    {% endif %}
  </li>
{% endfor %}
</ul>

### 📗 Conference Papers

<ul>
{% for pub in conferences %}
  <li>
    <strong>{{ pub.title }}</strong><br>
    {{ pub.authors }}<br>
    <em>{{ pub.conference }}</em>, {{ pub.year }}.<br>
    {% if pub.url %}
      <a href="{{ pub.url }}">[PDF]</a>
    {% endif %}
    {% if pub.bibtex %}
      <button onclick="copyBibtex('bibtex-{{ forloop.index }}')">Copy BibTeX</button>
      <pre id="bibtex-{{ forloop.index }}" style="display: none;">{{ pub.bibtex }}</pre>
    {% endif %}    
  </li>
{% endfor %}
</ul>

### 📙 Book Chapters

<ul>
{% for pub in books %}
  <li>
    <strong>{{ pub.title }}</strong><br>
    {{ pub.authors }}<br>
    <em>{{ pub.book }}</em>, {{ pub.year }}.<br>
    {% if pub.url %}
      <a href="{{ pub.url }}">[PDF]</a>
    {% endif %}
    {% if pub.bibtex %}
      <button onclick="copyBibtex('bibtex-{{ forloop.index }}')">Copy BibTeX</button>
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
