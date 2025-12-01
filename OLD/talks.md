---
layout: page
title: "Talks"
---

# Talks & Lectures

<!-- Leaflet CSS & JS -->
<link
  rel="stylesheet"
  href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<div id="mapid" style="height: 520px; margin: 1rem 0;"></div>

<script>
  // --- Map setup ---
  const map = L.map('mapid', { worldCopyJump: true }).setView([20, 0], 2);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 10,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  const talks = {{ site.data.talks | jsonify }};

  // --- Group by (rounded) lat/lon so multiple talks in the same city collapse into one marker ---
  // Adjust precision if needed:
  //   .toFixed(3) ≈ 100–120 m,
  //   .toFixed(2) ≈ 1.1 km,
  //   .toFixed(1) ≈ 11 km
  const keyFor = (t) => `${(+t.lat).toFixed(3)},${(+t.lon).toFixed(3)}`;

  // HTML-escape helper
  const esc = (s) => String(s || "").replace(/[&<>"']/g, m =>
    ({ "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;" }[m])
  );

  // Build groups
  const groups = {};
  talks.forEach(t => {
    const k = keyFor(t);
    (groups[k] ||= []).push(t);
  });

  // Add one marker per location with a popup listing all talks at that spot
  const bounds = [];
  Object.values(groups).forEach(group => {
    // Sort newest first if dates are ISO-like (YYYY-MM-DD)
    group.sort((a, b) => String(b.date).localeCompare(String(a.date)));

    const { lat, lon } = group[0];

    // Derive a location label (first defined one wins)
    const locLabel = group.find(g => g.location)?.location;

    const items = group.map(t =>
      `• <b>${esc(t.title)}</b>${t.date ? ` — ${esc(t.date)}` : ""}${t.location ? `, ${esc(t.location)}` : ""}${t.link ? ` — <a href="${esc(t.link)}" target="_blank" rel="noopener">link</a>` : ""}`
    ).join("<br>");

    const header = locLabel ? `<div style="margin-bottom:0.25rem;"><b>${esc(locLabel)}</b></div>` : "";
    const html = `${header}${items}`;

    L.marker([lat, lon]).addTo(map).bindPopup(html, { maxWidth: 360 });
    bounds.push([lat, lon]);
  });

  if (bounds.length > 0) {
    map.fitBounds(bounds, { padding: [24, 24] });
  }
</script>

## List

{% for t in site.data.talks %}

- **{{ t.title }}** — {{ t.date }}{% if t.location %}, {{ t.location }}{% endif %}{% if t.link %} — [link]({{ t.link }}){% endif %}
  {% endfor %}
