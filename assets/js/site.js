      function updateTopbarHeightVar() {
        const topbar = document.getElementById("topbar");
        if (!topbar) return;
        const h = topbar.getBoundingClientRect().height;
        document.documentElement.style.setProperty(
          "--topbar-height",
          Math.ceil(h) + "px",
        );
      }
      window.addEventListener("resize", updateTopbarHeightVar);
      updateTopbarHeightVar();

      function scrollToHashTarget(id) {
        const target = document.getElementById(id);
        if (!target) return;

        const topbar = document.getElementById("topbar");
        const section = target.closest("section");
        const stickySubheader = section ? section.querySelector(".pub-header") : null;
        const topbarHeight = topbar ? topbar.getBoundingClientRect().height : 0;
        const stickySubheaderHeight = stickySubheader
          ? stickySubheader.getBoundingClientRect().height
          : 0;
        const offset = topbarHeight + stickySubheaderHeight + 10;
        const top = target.getBoundingClientRect().top + window.scrollY - offset;

        window.scrollTo({
          top: Math.max(0, top),
          behavior: "auto",
        });

        history.replaceState(null, "", "#" + id);
      }

      // Navigation: show/hide sections (only for in-page nav links)
      document.querySelectorAll(".nav-link").forEach((link) => {
        link.addEventListener("click", (e) => {
          e.preventDefault();
          const target = e.target.getAttribute("href").substring(1);
          document
            .querySelectorAll("section")
            .forEach((s) => s.classList.remove("active"));
          document
            .querySelectorAll(".nav-link")
            .forEach((l) => l.classList.remove("active"));
          document.getElementById(target).classList.add("active");
          e.target.classList.add("active");
        });
      });

      document.querySelectorAll(".pub-nav a").forEach((link) => {
        link.addEventListener("click", (e) => {
          const href = link.getAttribute("href") || "";
          if (!href.startsWith("#")) return;

          const targetId = href.substring(1);
          if (!document.getElementById(targetId)) return;

          e.preventDefault();
          scrollToHashTarget(targetId);
        });
      });

      async function loadYAML(url) {
        try {
          const response = await fetch(url);
          const text = await response.text();
          return jsyaml.load(text);
        } catch (error) {
          console.error("Error loading " + url + ":", error);
          return null;
        }
      }

      async function loadMarkdown(url, containerId, fallbackMessage) {
        const container = document.getElementById(containerId);
        try {
          const resp = await fetch(url);
          if (!resp.ok) {
            container.innerHTML = "<p>" + fallbackMessage + "</p>";
            return;
          }
          const text = await resp.text();
          container.innerHTML = marked.parse(text);
        } catch (err) {
          console.error("Error loading " + url + ":", err);
          container.innerHTML = "<p>" + fallbackMessage + "</p>";
        }
      }

      // HTML-escape helper
      function escHtml(s) {
        return String(s || "").replace(/[&<>"']/g, function (m) {
          return {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;",
          }[m];
        });
      }

      function publicationFallbackImage(pub) {
        const title = String(pub.title || "Untitled Publication").trim();
        const venue = String(pub.venue || "").trim();
        const year = String(pub.year || "").trim();
        const type = String(pub.type || "publication")
          .replace(/-/g, " ")
          .replace(/\b\w/g, (c) => c.toUpperCase());

        const svg = `
<svg xmlns="http://www.w3.org/2000/svg" width="390" height="276" viewBox="0 0 390 276">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0f3d68"/>
      <stop offset="100%" stop-color="#1f7a8c"/>
    </linearGradient>
  </defs>
  <rect width="390" height="276" rx="18" fill="url(#bg)"/>
  <rect x="16" y="16" width="358" height="244" rx="14" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.18)"/>
  <foreignObject x="26" y="26" width="338" height="224">
    <div xmlns="http://www.w3.org/1999/xhtml" style="height:224px;display:flex;flex-direction:column;font-family:'Source Sans 3','Segoe UI',sans-serif;color:#ffffff;">
      <div style="display:inline-block;align-self:flex-start;padding:5px 10px;border-radius:999px;background:rgba(255,255,255,0.16);font-size:13px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;">${escHtml(type)}</div>
      <div style="margin-top:16px;font-size:25px;line-height:1.18;font-weight:700;display:-webkit-box;-webkit-line-clamp:5;-webkit-box-orient:vertical;overflow:hidden;">${escHtml(title)}</div>
      <div style="margin-top:auto;font-size:16px;line-height:1.3;color:rgba(255,255,255,0.84);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;">${escHtml(venue)}</div>
      <div style="margin-top:10px;font-size:14px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;color:rgba(255,255,255,0.72);">${escHtml(year)}</div>
    </div>
  </foreignObject>
</svg>`;

        return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
      }

      function renderInlineMathText(s) {
        return escHtml(s)
          .replace(/\^\{([^}]+)\}/g, "<sup>$1</sup>")
          .replace(/_\{([^}]+)\}/g, "<sub>$1</sub>")
          .replace(/\^([^^_{}])/g, "<sup>$1</sup>")
          .replace(/_([^^_{}])/g, "<sub>$1</sub>");
      }

      function generateBibtex(pub) {
        const typeMap = {
          journal: "article",
          conference: "inproceedings",
          workshop: "inproceedings",
          "book-chapter": "incollection",
          preprint: "misc",
          other: "misc",
        };
        const entryType = typeMap[pub.type] || "misc";
        const venueKey = pub.type === "journal" ? "journal" : "booktitle";

        let bibtex = "@" + entryType + "{" + pub.id + ",\n";
        bibtex += "  title = {" + (pub.title || "") + "},\n";
        bibtex += "  author = {" + (pub.authors || "") + "},\n";

        if (pub.editors) {
          bibtex += "  editor = {" + pub.editors + "},\n";
        }

        bibtex += "  " + venueKey + " = {" + (pub.venue || "") + "},\n";
        bibtex += "  year = {" + (pub.year || "") + "}";

        if (pub.doi) {
          bibtex += ",\n  doi = {" + pub.doi + "}";
        }

        if (pub.note) {
          bibtex += ",\n  note = {" + pub.note + "}";
        }

        bibtex += "\n}";
        return bibtex;
      }

      function toggleBibtex(id) {
        const el = document.getElementById("bibtex-" + id);
        if (el) el.classList.toggle("show");
      }

      async function copyTextToClipboard(text) {
        try {
          await navigator.clipboard.writeText(text);
          return true;
        } catch (e) {
          // Fallback for older browsers / some local contexts
          const ta = document.createElement("textarea");
          ta.value = text;
          ta.style.position = "fixed";
          ta.style.left = "-9999px";
          document.body.appendChild(ta);
          ta.select();
          let ok = false;
          try {
            ok = document.execCommand("copy");
          } catch (_) {
            ok = false;
          }
          document.body.removeChild(ta);
          return ok;
        }
      }

      async function renderPublications() {
        const data = await loadYAML("data/publications.yaml");
        const container = document.getElementById("publications-content");

        if (!data || !data.publications) {
          container.innerHTML =
            "<p>No publications found. Check data/publications.yaml</p>";
          return;
        }

        const pubs = data.publications;

        const types = {
          journal: { name: "Journal Articles", color: "#0066cc", pubs: [] },
          conference: { name: "Conference Papers", color: "#10b981", pubs: [] },
          workshop: { name: "Workshop Papers", color: "#f59e0b", pubs: [] },
          "book-chapter": { name: "Book Chapters", color: "#8b5cf6", pubs: [] },
          preprint: { name: "Preprints", color: "#ec4899", pubs: [] },
          other: { name: "Other Publications", color: "#6b7280", pubs: [] },
        };

        pubs.forEach((pub) => {
          const t = pub.type || "other";
          (types[t] ? types[t].pubs : types["other"].pubs).push(pub);
        });

        Object.values(types).forEach((type) => {
          type.pubs.sort(
            (a, b) => parseInt(b.year || "0", 10) - parseInt(a.year || "0", 10),
          );
        });

        const doiHtml = (doi) => {
          const d = String(doi || "").trim();
          if (!d) return "";
          const url = "https://doi.org/" + d;
          return (
            ' doi: <a href="' +
            url +
            '" target="_blank" rel="noopener noreferrer">' +
            escHtml(d) +
            "</a>"
          );
        };

        let html = "";

        Object.entries(types).forEach(([key, type]) => {
          if (type.pubs.length === 0) return;

          html +=
            '<div id="pub-' +
            key +
            '" class="category-header" style="border-left-color: ' +
            type.color +
            '">';
          html += "  <h3>" + escHtml(type.name) + "</h3>";
          html +=
            '  <span class="category-count" style="background: ' +
            type.color +
            '">' +
            type.pubs.length +
            "</span>";
          html += "</div>";

          type.pubs.forEach((pub) => {
            const id = pub.id;
            const bibtex = generateBibtex(pub);
            const bibtexEsc = escHtml(bibtex);

            const paperUrl =
              pub.paper_url || (pub.doi ? "https://doi.org/" + pub.doi : null);

            // Citation: authors. "title." venue year. + DOI appended at end
            const pieces = [];
            if (pub.authors) pieces.push(escHtml(pub.authors) + ".");
            if (pub.title) pieces.push('"' + renderInlineMathText(pub.title) + '."');
            if (pub.venue) pieces.push("<i>" + escHtml(pub.venue) + "</i>");
            if (pub.year) pieces.push(escHtml(String(pub.year)) + ".");

            const citationBase = pieces.join(" ");

            // Inline [Paper] [BibTeX] on same line
            let links = '<span class="pub-links">';
            if (paperUrl) {
              links +=
                ' <a href="' +
                paperUrl +
                '" target="_blank" rel="noopener noreferrer">[Paper]</a>';
            }
            links +=
              ' <a href="#" class="bibtex-toggle" data-pub-id="' +
              escHtml(id) +
              '">[BibTeX]</a>';
            links += "</span>";

            html += '<div class="publication">';
            html += '  <div class="pub-image">';
            const imageSrc = pub.image
              ? "images/papers/" + escHtml(pub.image)
              : publicationFallbackImage(pub);
            html +=
              '    <img src="' +
              imageSrc +
              '" alt="' +
              escHtml(pub.title || "") +
              '">';
            html += "  </div>";

            html += '  <div class="pub-content">';
            html +=
              '    <div class="pub-citation">' +
              citationBase +
              doiHtml(pub.doi) +
              links +
              "</div>";

            if (pub.summary) {
              html +=
                '    <div class="pub-summary">' +
                escHtml(pub.summary) +
                "</div>";
            }
            if (pub.note) {
              html +=
                '    <div class="pub-note">' +
                escHtml(pub.note) +
                "</div>";
            }

            // Abstract toggle if present
            if (pub.abstract) {
              html += '    <details class="pub-abstract">';
              html += "      <summary>Abstract</summary>";
              html +=
                '      <div class="pub-abstract-body">' +
                escHtml(pub.abstract) +
                "</div>";
              html += "    </details>";
            }

            // BibTeX block
            html +=
              '    <div id="bibtex-' +
              escHtml(id) +
              '" class="bibtex-container">';
            html +=
              '      <div class="bibtex-header"><strong>BibTeX Citation</strong>';
            html +=
              '        <button id="copy-btn-' +
              escHtml(id) +
              '" class="btn bibtex-copy" data-pub-id="' +
              escHtml(id) +
              '">Copy</button>';
            html += "      </div>";
            html +=
              '      <pre class="bibtex-code" id="bibtex-code-' +
              escHtml(id) +
              '">' +
              bibtexEsc +
              "</pre>";
            html += "    </div>";

            html += "  </div>";
            html += "</div>";
          });
        });

        container.innerHTML = html;

        // Wire up [BibTeX] toggles
        container.querySelectorAll("a.bibtex-toggle").forEach((a) => {
          a.addEventListener("click", (e) => {
            e.preventDefault();
            toggleBibtex(a.dataset.pubId);
          });
        });

        // Wire up Copy buttons
        container.querySelectorAll("button.bibtex-copy").forEach((btn) => {
          btn.addEventListener("click", async () => {
            const id = btn.dataset.pubId;
            const pre = document.getElementById("bibtex-code-" + id);
            const ok = await copyTextToClipboard(pre ? pre.innerText : "");
            const original = btn.textContent;
            btn.textContent = ok ? "✓ Copied!" : "Copy failed";
            setTimeout(() => {
              btn.textContent = original;
            }, 1500);
          });
        });

        const links = document.getElementById("publication-links");
        if (links) links.style.display = "flex";
      }

      async function renderTalks() {
        const container = document.getElementById("talks-content");

        // Load talks + tutorials
        const [talksData, tutorialsData] = await Promise.all([
          loadYAML("data/talks.yaml"),
          loadYAML("data/tutorials.yaml"),
        ]);

        const talks = talksData && talksData.talks ? talksData.talks : [];
        const tutorials =
          tutorialsData && Array.isArray(tutorialsData.tutorials)
            ? tutorialsData.tutorials
            : tutorialsData && Array.isArray(tutorialsData.talks)
              ? tutorialsData.talks
              : [];

        const categories = {
          talks: { name: "Talks", color: "#1f7a8c", items: talks },
          tutorials: { name: "Tutorials", color: "#f59e0b", items: tutorials },
        };

        if (talks.length + tutorials.length === 0) {
          container.innerHTML =
            "<p>No talks found. Check data/talks.yaml and data/tutorials.yaml</p>";
          return;
        }

        const renderList = (items) => {
          if (!items || items.length === 0)
            return '<p style="color:#666;">None yet.</p>';

          let h = "";
          items
            .slice()
            .sort((a, b) => new Date(b.date) - new Date(a.date))
            .forEach(function (talk) {
              const formattedDate = talk.date
                ? new Date(talk.date).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })
                : "";

              h += '<div class="talk-item">';
              h += '<div class="talk-title">' + escHtml(talk.title) + "</div>";
              h += '<div class="talk-details">';

              const locParts = [];
              if (talk.venue) locParts.push(talk.venue);
              if (talk.city) locParts.push(talk.city);
              if (talk.country) locParts.push(talk.country);
              if (locParts.length > 0)
                h += "<strong>Location:</strong> " + escHtml(locParts.join(", ")) + "<br>";
              if (formattedDate) h += "<strong>Date:</strong> " + escHtml(formattedDate);
              if (talk.slides) {
                h +=
                  '<br><strong>Slides:</strong> <a href="slides/' +
                  encodeURIComponent(talk.slides) +
                  '" target="_blank" rel="noopener noreferrer">View Slides</a>';
              }
              h += "</div></div>";
            });

          return h;
        };

        let html = "";
        html += '<div id="talk-map"></div>';

        Object.entries(categories).forEach(([key, cat]) => {
          if (!cat.items || cat.items.length === 0) return;

          html +=
            '<div id="talk-' +
            key +
            '" class="category-header" style="border-left-color: ' +
            cat.color +
            '">';
          html += "  <h3>" + escHtml(cat.name) + "</h3>";
          html +=
            '  <span class="category-count" style="background: ' +
            cat.color +
            '">' +
            cat.items.length +
            "</span>";
          html += "</div>";

          html += renderList(cat.items);
        });

        container.innerHTML = html;

        // Map pins from ALL talks
        const all = [...talks, ...tutorials];
        const sortedAll = all
          .slice()
          .sort((a, b) => new Date(b.date) - new Date(a.date));

        const map = L.map("talk-map", { worldCopyJump: true }).setView(
          [20, 0],
          2,
        );

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          maxZoom: 10,
          attribution: "&copy; OpenStreetMap contributors",
        }).addTo(map);

        const keyFor = function (t) {
          const lat = parseFloat(t.lat);
          const lon = parseFloat(t.lon);
          if (isNaN(lat) || isNaN(lon)) return null;
          return lat.toFixed(3) + "," + lon.toFixed(3);
        };

        const groups = {};
        sortedAll.forEach(function (t) {
          const k = keyFor(t);
          if (!k) return;
          if (!groups[k]) groups[k] = [];
          groups[k].push(t);
        });

        const bounds = [];
        Object.values(groups).forEach(function (group) {
          group.sort(function (a, b) {
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
              locLabel = parts.join(", ");
              break;
            }
          }

          const items = group
            .map(function (t) {
              const datePart = t.date ? " — " + escHtml(t.date) : "";
              const parts = [];
              if (t.venue) parts.push(t.venue);
              if (t.city) parts.push(t.city);
              if (t.country) parts.push(t.country);
              const locPart = parts.length
                ? ", " + escHtml(parts.join(", "))
                : "";
              const linkPart = t.slides
                ? ' — <a href="slides/' +
                  encodeURIComponent(t.slides) +
                  '" target="_blank" rel="noopener noreferrer">slides</a>'
                : "";
              return (
                "• <b>" +
                escHtml(t.title) +
                "</b>" +
                datePart +
                locPart +
                linkPart
              );
            })
            .join("<br>");

          const header = locLabel
            ? '<div style="margin-bottom:0.25rem;"><b>' +
              escHtml(locLabel) +
              "</b></div>"
            : "";
          const popupHtml = header + items;

          L.marker([lat, lon])
            .addTo(map)
            .bindPopup(popupHtml, { maxWidth: 360 });
          bounds.push([lat, lon]);
        });

        if (bounds.length > 0) {
          map.fitBounds(bounds, { padding: [24, 24] });
        }

        const links = document.getElementById("talk-links");
        if (links) links.style.display = "flex";
      }

      async function renderProfessionalActivities() {
        const container = document.getElementById("professional-activities-content");
        if (!container) return;

        const mentorshipData = (await loadYAML("data/mentorship.yaml")) || {};
        const activitiesData = (await loadYAML("data/professional_activities.yaml")) || {};

        const postdocs = Array.isArray(mentorshipData.postdoctoral_students)
          ? mentorshipData.postdoctoral_students
          : Array.isArray(mentorshipData.postdocs)
            ? mentorshipData.postdocs
            : [];

        const advisees = Array.isArray(mentorshipData.thesis_advisees)
          ? mentorshipData.thesis_advisees
          : Array.isArray(mentorshipData.advisees)
            ? mentorshipData.advisees
            : [];

        const renderEntry = (entry, type) => {
          const name = escHtml(entry.name || "");
          const institution = escHtml(entry.institution || "");
          const years = escHtml(entry.years || "");
          const topic = escHtml(entry.topic || "");
          const current = escHtml(entry.current_position || "");
          const degree = escHtml(entry.degree || "");
          const gradYear = escHtml(String(entry.graduation_year || ""));
          const thesisTitle = escHtml(entry.thesis_title || "");
          const advisor = escHtml(entry.advisor || entry.co_advisor || "");

          const rawWebsite = String(
            entry.website || entry.url || entry.website_url || "",
          ).trim();
          let websiteLink = "";
          if (rawWebsite) {
            const href = /^https?:\/\//i.test(rawWebsite)
              ? rawWebsite
              : `https://${rawWebsite}`;
            const safeHref = escHtml(href);
            websiteLink = ` <a href="${safeHref}" target="_blank" rel="noopener noreferrer">Website</a>`;
          }

          const details = [];
          if (type === "advisee" && degree) details.push(degree);
          if (type === "advisee" && gradYear)
            details.push(`Graduated ${gradYear}`);
          if (topic) details.push(`Topic: ${topic}`);
          if (thesisTitle) details.push(`Thesis: ${thesisTitle}`);
          if (advisor) details.push(`Advisor: ${advisor}`);

          let currentPositionText = "";
          if (institution && current) {
            currentPositionText = `Current position: ${current} at ${institution}`;
          } else if (current) {
            currentPositionText = `Current position: ${current}`;
          } else if (institution) {
            currentPositionText = `Current position: ${institution}`;
          }

          if (currentPositionText && type !== "advisee") {
            details.push(currentPositionText);
          }

          const label = name || "(Unnamed entry)";
          const yearsLabel = years ? ` (${years})` : "";

          const detailsHtml = details.length
            ? `<span style="color:#4d6278;">${details.join(" | ")}</span>`
            : "";
          const adviseeCurrentHtml =
            type === "advisee" && currentPositionText
              ? `<span style="color:#4d6278;">${currentPositionText}</span>`
              : "";

          let detailText = "";
          if (detailsHtml && adviseeCurrentHtml) {
            detailText = `<br>${detailsHtml}<br>${adviseeCurrentHtml}`;
          } else if (detailsHtml) {
            detailText = `<br>${detailsHtml}`;
          } else if (adviseeCurrentHtml) {
            detailText = `<br>${adviseeCurrentHtml}`;
          }

          return `<li><strong>${label}${yearsLabel}</strong>${websiteLink}${detailText}</li>`;
        };

        const postdocItems = postdocs.map((e) => renderEntry(e, "postdoc")).join("");
        const adviseeItems = advisees.map((e) => renderEntry(e, "advisee")).join("");

        const mentorshipHtml = `
          <h3>Mentorship</h3>
          <h4>Postdoctoral Students</h4>
          ${postdocItems ? `<ul>${postdocItems}</ul>` : "<p>No postdoctoral entries yet.</p>"}
          <h4>Thesis Advisees</h4>
          ${adviseeItems ? `<ul>${adviseeItems}</ul>` : "<p>No thesis advisee entries yet.</p>"}
        `;

        const organizations = Array.isArray(activitiesData.organizations)
          ? activitiesData.organizations
          : [];
        const professionalOrganizations = Array.isArray(activitiesData.professional_organizations)
          ? activitiesData.professional_organizations
          : Array.isArray(activitiesData.professionalOrganizations)
            ? activitiesData.professionalOrganizations
            : [];
        const programCommittee = Array.isArray(activitiesData.program_committee)
          ? activitiesData.program_committee
          : [];
        const reviewerEntries = Array.isArray(activitiesData.reviewer)
          ? activitiesData.reviewer
          : Array.isArray(activitiesData.reviewers)
            ? activitiesData.reviewers
            : [];

        const formatYears = (yearsVal) => {
          if (Array.isArray(yearsVal)) {
            return yearsVal.map((y) => escHtml(String(y))).join(", ");
          }
          if (yearsVal === undefined || yearsVal === null || yearsVal === "") {
            return "";
          }
          return escHtml(String(yearsVal));
        };

        const renderEventYearSection = (title, items) => {
          if (!items || items.length === 0) return "";

          let html = `<h3>${title}</h3><ul>`;
          items.forEach((item) => {
            const event = escHtml(item.event || item.name || "");
            const years = formatYears(item.years || item.year);
            const note = escHtml(item.note || "");

            let line = "";
            if (event && years) {
              line = `<strong>${event}</strong>: ${years}`;
            } else {
              line = event || years;
            }

            if (note) {
              line += ` (${note})`;
            }

            if (line) {
              html += `<li>${line}</li>`;
            }
          });
          html += "</ul>";
          return html;
        };

        const renderProfessionalOrganizations = (items) => {
          if (!items || items.length === 0) return "";

          let html = "<h3>Professional Organizations</h3><ul>";
          items.forEach((item) => {
            const org = escHtml(item.organization || item.name || "");
            const role = escHtml(item.role || "");
            const years = formatYears(item.years || item.year);

            let line = "";
            if (org && role && years) {
              line = `<strong>${org}</strong>, ${role} (${years})`;
            } else if (org && role) {
              line = `<strong>${org}</strong>, ${role}`;
            } else if (org && years) {
              line = `<strong>${org}</strong>: ${years}`;
            } else {
              line = org || role || years;
            }

            if (line) {
              html += `<li>${line}</li>`;
            }
          });
          html += "</ul>";
          return html;
        };

        let serviceHtml = "";
        if (organizations.length > 0) {
          serviceHtml += "<h3>Conference and Workshop Service</h3>";

          organizations.forEach((org) => {
            const orgName = escHtml(org.name || "");
            const entries = Array.isArray(org.entries) ? org.entries : [];
            if (!orgName && entries.length === 0) return;

            if (orgName) {
              serviceHtml += `<h4>${orgName}</h4>`;
            }

            if (entries.length > 0) {
              serviceHtml += "<ul>";
              entries.forEach((item) => {
                const yearVal = item.year;
                const year =
                  yearVal === undefined || yearVal === null || yearVal === ""
                    ? ""
                    : escHtml(String(yearVal));
                const role = escHtml(item.role || "");
                const note = escHtml(item.note || "");

                let line = "";
                if (year && role) {
                  line = `<strong>${year}</strong> - ${role}`;
                } else {
                  line = year || role;
                }

                if (note) {
                  line += ` (${note})`;
                }

                if (line) {
                  serviceHtml += `<li>${line}</li>`;
                }
              });
              serviceHtml += "</ul>";
            }
          });
        }

        serviceHtml += renderEventYearSection("Program Committee", programCommittee);
        serviceHtml += renderEventYearSection("Reviewer", reviewerEntries);

        const professionalOrganizationsHtml = renderProfessionalOrganizations(
          professionalOrganizations,
        );

        container.innerHTML =
          mentorshipHtml + professionalOrganizationsHtml + serviceHtml;
      }

      function splitMarkdownSections(markdown) {
        const lines = String(markdown || "").split("\n");
        const sections = [];
        let current = null;

        lines.forEach((line) => {
          const match = line.match(/^###\s+(.*?)\s*$/);
          if (match) {
            if (current) {
              const body = current.lines.join("\n").trim();
              sections.push({
                heading: current.heading,
                markdown: body
                  ? `### ${current.heading}\n\n${body}\n`
                  : `### ${current.heading}\n`,
              });
            }

            current = {
              heading: match[1].trim(),
              lines: [],
            };
            return;
          }

          if (current) {
            current.lines.push(line);
          }
        });

        if (current) {
          const body = current.lines.join("\n").trim();
          sections.push({
            heading: current.heading,
            markdown: body
              ? `### ${current.heading}\n\n${body}\n`
              : `### ${current.heading}\n`,
          });
        }

        return sections;
      }

      function awardYear(value) {
        const year = Number.parseInt(String(value || "").trim(), 10);
        return Number.isFinite(year) ? year : 0;
      }

      function isPublicationAwardNote(note) {
        const normalized = String(note || "").trim();
        if (!normalized) return false;

        return (
          (normalized.startsWith("Best ") &&
            (normalized.includes("Award") || normalized.includes("Finalist"))) ||
          normalized.includes("Honorable Mention Best Paper")
        );
      }

      function buildAwards(manualAwardsData, publicationsData) {
        const manualAwards = Array.isArray(manualAwardsData?.awards)
          ? manualAwardsData.awards
          : [];
        const publicationAwards = Array.isArray(publicationsData?.publications)
          ? publicationsData.publications
              .filter((pub) => isPublicationAwardNote(pub.note))
              .map((pub) => ({
                year: pub.year,
                title: String(pub.note || "").trim(),
                organization: pub.venue || "",
                detail_label: "Paper",
                detail: pub.title || "",
              }))
          : [];

        return [...manualAwards, ...publicationAwards].sort((a, b) => {
          const yearDiff = awardYear(b.year) - awardYear(a.year);
          if (yearDiff !== 0) return yearDiff;

          const aKey = [a.title, a.organization, a.detail]
            .map((value) => String(value || ""))
            .join(" ");
          const bKey = [b.title, b.organization, b.detail]
            .map((value) => String(value || ""))
            .join(" ");
          return aKey.localeCompare(bKey);
        });
      }

      function renderAwardSummary(award) {
        const title = String(award.title || "").trim();
        const organization = String(award.organization || "").trim();
        const organizationUrl = String(award.organization_url || "").trim();
        const detail = String(award.detail || "").trim();
        const detailLabel = String(award.detail_label || "").trim();
        const isPaperAward =
          detail &&
          detailLabel === "Paper" &&
          title.toLowerCase().includes("paper");

        if (isPaperAward) {
          const venueHtml = organization
            ? organizationUrl
              ? '<a href="' +
                escHtml(organizationUrl) +
                '" target="_blank" rel="noopener noreferrer">' +
                escHtml(organization) +
                "</a>"
              : escHtml(organization)
            : "";
          const parts = ["<strong>" + escHtml(title) + "</strong>"];
          parts.push('"' + renderInlineMathText(detail) + '"');
          if (venueHtml) parts.push(venueHtml);
          return parts.join(", ");
        }

        const parts = [];
        if (title) {
          parts.push("<strong>" + escHtml(title) + "</strong>");
        }

        if (organization) {
          if (organizationUrl) {
            parts.push(
              '<a href="' +
                escHtml(organizationUrl) +
                '" target="_blank" rel="noopener noreferrer">' +
                escHtml(organization) +
                "</a>",
            );
          } else {
            parts.push(escHtml(organization));
          }
        }

        if (detail) {
          if (detailLabel) {
            parts.push(escHtml(detailLabel) + ": " + renderInlineMathText(detail));
          } else {
            parts.push(renderInlineMathText(detail));
          }
        }

        return parts.join(", ");
      }

      function renderAwardsSection(awards) {
        if (!awards.length) return "";

        let html = "<h3>Awards</h3>";
        html += "<table><tbody>";

        awards.forEach((award) => {
          html += "<tr>";
          html += "<td>" + escHtml(String(award.year || "")) + "</td>";
          html += "<td>" + renderAwardSummary(award) + "</td>";
          html += "</tr>";
        });

        html += "</tbody></table>";
        return html;
      }

      async function renderAbout() {
        const introContainer = document.getElementById("about-intro");
        const detailsContainer = document.getElementById("about-experience");
        const awardsHeadings = new Set(["Awards", "Awards & Honors"]);

        try {
          const [resp, manualAwardsData, publicationsData] = await Promise.all([
            fetch("data/about.md"),
            loadYAML("data/awards.yaml"),
            loadYAML("data/publications.yaml"),
          ]);

          if (!resp.ok) {
            introContainer.innerHTML = "<p>Could not load about information.</p>";
            detailsContainer.innerHTML = "";
            return;
          }

          const text = await resp.text();
          const introText = text.split(/^###\s+/m)[0].trim();
          const sections = splitMarkdownSections(text);
          const sectionMap = new Map(
            sections.map((section) => [section.heading, section]),
          );
          const awards = buildAwards(manualAwardsData, publicationsData);

          awardsHeadings.forEach((heading) => sectionMap.delete(heading));

          introContainer.innerHTML = introText ? marked.parse(introText) : "";

          let detailsHtml = "";

          ["Professional Experience", "Education"].forEach((heading) => {
            const section = sectionMap.get(heading);
            if (!section) return;

            detailsHtml += marked.parse(section.markdown);
            sectionMap.delete(heading);
          });

          detailsHtml += renderAwardsSection(awards);

          sections.forEach((section) => {
            if (!sectionMap.has(section.heading)) return;
            detailsHtml += marked.parse(section.markdown);
          });

          if (detailsHtml) {
            detailsContainer.innerHTML = detailsHtml;
          } else {
            introContainer.innerHTML = marked.parse(text);
            detailsContainer.innerHTML = "";
          }
        } catch (err) {
          console.error("Error loading about.md:", err);
          introContainer.innerHTML = "<p>Could not load about information.</p>";
          detailsContainer.innerHTML = "";
        }
      }

      async function renderFunFacts() {
        await loadMarkdown(
          "data/fun-facts.md",
          "fun-facts-content",
          "Could not load fun facts. Ensure data/fun-facts.md exists.",
        );
      }

      async function renderQuotes() {
        await loadMarkdown(
          "data/quotes.md",
          "quotes-content",
          "Could not load quotes. Ensure data/quotes.md exists.",
        );
      }

      let aboutLoaded = false;
      let publicationsLoaded = false;
      let talksLoaded = false;
      let professionalActivitiesLoaded = false;
      let funFactsLoaded = false;
      let quotesLoaded = false;

      // Attach lazy-loading behavior
      document.querySelectorAll(".nav-link").forEach((link) => {
        link.addEventListener("click", (e) => {
          const target = e.target.getAttribute("href").substring(1);
          if (target === "about" && !aboutLoaded) {
            renderAbout();
            aboutLoaded = true;
          }
          if (target === "publications" && !publicationsLoaded) {
            renderPublications();
            publicationsLoaded = true;
          }
          if (target === "talks" && !talksLoaded) {
            renderTalks();
            talksLoaded = true;
          }
          if (
            target === "professional-activities" &&
            !professionalActivitiesLoaded
          ) {
            renderProfessionalActivities();
            professionalActivitiesLoaded = true;
          }
          if (target === "fun-facts" && !funFactsLoaded) {
            renderFunFacts();
            funFactsLoaded = true;
          }
          if (target === "quotes" && !quotesLoaded) {
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

      // ============================================
      // About Section Carousel Functionality
      // ============================================
      let currentSlide = 0;
      let autoSlideInterval = null;
      const slideCount = document.querySelectorAll('.about-carousel-item').length;

      function initCarousel() {
        const indicatorsContainer = document.getElementById('carouselIndicators');
        if (indicatorsContainer) {
          for (let i = 0; i < slideCount; i++) {
            const indicator = document.createElement('button');
            indicator.className = 'carousel-indicator';
            indicator.onclick = () => goToSlide(i);
            indicatorsContainer.appendChild(indicator);
          }
        }
        updateCarousel();
        startAutoSlide();
      }

      function updateCarousel() {
        const inner = document.getElementById('aboutCarouselInner');
        if (inner) {
          inner.style.transform = `translateX(-${currentSlide * 100}%)`;
        }

        const indicators = document.querySelectorAll('.carousel-indicator');
        indicators.forEach((indicator, index) => {
          indicator.classList.toggle('active', index === currentSlide);
        });
      }

      function changeSlide(direction) {
        currentSlide += direction;
        if (currentSlide < 0) currentSlide = slideCount - 1;
        if (currentSlide >= slideCount) currentSlide = 0;
        updateCarousel();
        resetAutoSlide();
      }

      function goToSlide(index) {
        currentSlide = index;
        updateCarousel();
        resetAutoSlide();
      }

      function startAutoSlide() {
        autoSlideInterval = setInterval(() => {
          currentSlide = (currentSlide + 1) % slideCount;
          updateCarousel();
        }, 5000);
      }

      function resetAutoSlide() {
        clearInterval(autoSlideInterval);
        startAutoSlide();
      }

      const carousel = document.querySelector('.about-carousel');
      if (carousel) {
        carousel.addEventListener('mouseenter', () => clearInterval(autoSlideInterval));
        carousel.addEventListener('mouseleave', () => startAutoSlide());
      }

      initCarousel();
