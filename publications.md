---
layout: page
title: "Publications"
---

{% assign pubs = site.data.publications | sort: "year" | reverse %}
{% assign journals = pubs | where: "type", "journal" %}
{% assign conferences = pubs | where: "type", "conference" %}
{% assign books = pubs | where: "type", "bookchapter" %}

<div class="local-nav">
  <strong>Jump to:</strong>
  <a href="#journals">Journals ({{ journals | size }})</a> ·
  <a href="#conferences">Conferences ({{ conferences | size }})</a> ·
  <a href="#book-chapters">Book Chapters ({{ books | size }})</a>
</div>

## <span id="journals"></span>Journal Articles

{% assign years = journals | map: "year" | uniq | sort | reverse %}
{% for y in years %}

### {{ y }}

{% for p in journals %}{% if p.year == y %}

- **{{ p.title }}**  
   {{ p.authors }}  
   _{{ p.venue }}_, {{ p.year }}{% if p.doi %}. DOI: {{ p.doi }}{% endif %}{% if p.url %}. [Link]({{ p.url }}){% endif %}
  {% endif %}{% endfor %}
  {% endfor %}

<p class="back-top"><a href="#top">Back to top ↑</a></p>

## <span id="conferences"></span>Conference Papers

{% assign years = conferences | map: "year" | uniq | sort | reverse %}
{% for y in years %}

### {{ y }}

{% for p in conferences %}{% if p.year == y %}

- **{{ p.title }}**  
   {{ p.authors }}  
   _{{ p.venue }}_, {{ p.year }}{% if p.doi %}. DOI: {{ p.doi }}{% endif %}{% if p.url %}. [Link]({{ p.url }}){% endif %}
  {% endif %}{% endfor %}
  {% endfor %}

<p class="back-top"><a href="#top">Back to top ↑</a></p>

## <span id="book-chapters"></span>Book Chapters

{% assign years = books | map: "year" | uniq | sort | reverse %}
{% for y in years %}

### {{ y }}

{% for p in books %}{% if p.year == y %}

- **{{ p.title }}**  
   {{ p.authors }}  
   _{{ p.venue }}_, {{ p.year }}{% if p.doi %}. DOI: {{ p.doi }}{% endif %}{% if p.url %}. [Link]({{ p.url }}){% endif %}
  {% endif %}{% endfor %}
  {% endfor %}

<p class="back-top"><a href="#top">Back to top ↑</a></p>
