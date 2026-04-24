#!/usr/bin/env python3
"""
generate_cv.py - Comprehensive CV Generator

Generates a complete academic CV from website data sources:
- data/about.md: Professional Experience, Education
- data/awards.yaml: Awards
- data/publications.yaml: Publications
- data/talks.yaml: Talks
- data/tutorials.yaml: Tutorials
- data/professional_activities.yaml: Professional activities and service

Usage:
    python generate_cv.py

Output:
    cv/output/cv.tex (ready to compile with pdflatex)
"""

import re
import unicodedata
import yaml
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class CVGenerator:
    def __init__(self, data_dir: Path, cv_dir: Path):
        self.data_dir = data_dir
        self.cv_dir = cv_dir
        self.output_dir = cv_dir / "output"
        self.output_dir.mkdir(exist_ok=True)

        # Data containers
        self.education = []
        self.experience = []
        self.manual_awards = []
        self.awards = []
        self.publications = []
        self.talks = []
        self.tutorials = []
        self.professional_organizations = []
        self.organizations = []
        self.program_committee = []
        self.reviewer = []

    def escape_latex(self, s: str) -> str:
        """Escape special LaTeX characters."""
        if not s:
            return ""
        s = unicodedata.normalize("NFC", s)
        replacements = {
            "\\": r"\textbackslash{}",
            "&": r"\&",
            "%": r"\%",
            "_": r"\_",
            "#": r"\#",
            "$": r"\$",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }
        for k, v in replacements.items():
            s = s.replace(k, v)
        return s

    def parse_about_md(self):
        """Parse about.md for Professional Experience and Education."""
        about_file = self.data_dir / "about.md"
        if not about_file.exists():
            print(f"⚠️  {about_file} not found")
            return

        with about_file.open("r", encoding="utf-8") as f:
            content = f.read()

        self.experience = self._parse_markdown_table_section(
            content, "Professional Experience"
        )
        self.education = self._parse_markdown_table_section(content, "Education")

        print(f"✓ Parsed {len(self.experience)} experience entries and {len(self.education)} education entries")

    def _clean_markdown_text(self, text: str) -> str:
        """Remove simple Markdown formatting used in the data files."""
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', str(text or ""))
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        return text.strip()

    def _parse_markdown_table_section(self, content: str, heading: str) -> List[tuple[str, str]]:
        """Parse a two-column Markdown table, merging continuation rows."""
        match = re.search(
            rf'### {re.escape(heading)}\s*\n\s*\|.*?\n\s*\|.*?\n((?:\s*\|.*?\n)+)',
            content,
            re.MULTILINE | re.DOTALL
        )
        if not match:
            return []

        entries: List[tuple[str, str]] = []
        table_rows = match.group(1).strip().split('\n')
        for row in table_rows:
            row_match = re.match(r'\|\s*([^|]*)\s*\|\s*(.+?)\s*\|', row)
            if not row_match:
                continue

            key = self._clean_markdown_text(row_match.group(1))
            desc = self._clean_markdown_text(row_match.group(2))
            if not desc:
                continue

            if key:
                entries.append((key, desc))
            elif entries:
                prev_key, prev_desc = entries[-1]
                entries[-1] = (prev_key, f"{prev_desc} {desc}")

        return entries

    def parse_awards_yaml(self):
        """Parse manually managed awards from awards.yaml."""
        awards_file = self.data_dir / "awards.yaml"
        if not awards_file.exists():
            print(f"⚠️  {awards_file} not found")
            return

        with awards_file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        self.manual_awards = data.get("awards", []) or []
        print(f"✓ Parsed {len(self.manual_awards)} manual awards")

    def parse_publications_yaml(self):
        """Parse publications.yaml."""
        pub_file = self.data_dir / "publications.yaml"
        if not pub_file.exists():
            print(f"⚠️  {pub_file} not found")
            return

        with pub_file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.publications = data.get("publications", [])
        print(f"✓ Parsed {len(self.publications)} publications")

    def build_awards(self):
        """Combine manual awards with publication-derived best paper awards."""
        combined_awards = []

        def is_publication_award_note(note: Any) -> bool:
            normalized = str(note or "").strip()
            if not normalized:
                return False

            return (
                normalized.startswith("Best ") and (
                    "Award" in normalized or "Finalist" in normalized
                )
            ) or (
                "Honorable Mention Best Paper" in normalized
            )

        for item in self.manual_awards:
            combined_awards.append({
                "year": item.get("year", ""),
                "title": item.get("title", ""),
                "organization": item.get("organization", ""),
                "detail_label": item.get("detail_label", ""),
                "detail": item.get("detail", ""),
            })

        for pub in self.publications:
            if not is_publication_award_note(pub.get("note", "")):
                continue

            combined_awards.append({
                "year": pub.get("year", ""),
                "title": str(pub.get("note", "")).strip(),
                "organization": pub.get("venue", ""),
                "detail_label": "Paper",
                "detail": pub.get("title", ""),
            })

        def award_sort_key(item: Dict[str, Any]):
            try:
                year = int(str(item.get("year", "")).strip())
            except ValueError:
                year = 0

            return (
                -year,
                str(item.get("title", "")),
                str(item.get("organization", "")),
                str(item.get("detail", "")),
            )

        def award_description(item: Dict[str, Any]) -> str:
            parts = []
            title = str(item.get("title", "")).strip()
            organization = str(item.get("organization", "")).strip()
            detail = str(item.get("detail", "")).strip()
            detail_label = str(item.get("detail_label", "")).strip()

            if title:
                parts.append(title)
            if organization:
                parts.append(organization)

            description = ", ".join(parts)

            if detail:
                if detail_label == "Paper":
                    description += f' {detail_label}: "{detail}"'
                elif detail_label:
                    description += f" {detail_label}: {detail}"
                else:
                    description += f" {detail}"

            return description.strip()

        combined_awards.sort(key=award_sort_key)
        self.awards = [
            (str(item.get("year", "")).strip(), award_description(item))
            for item in combined_awards
            if str(item.get("year", "")).strip() and award_description(item)
        ]
        print(f"✓ Built {len(self.awards)} awards")

    def parse_talks_yaml(self):
        """Parse talks.yaml."""
        talks_file = self.data_dir / "talks.yaml"
        if not talks_file.exists():
            print(f"⚠️  {talks_file} not found")
            return

        with talks_file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.talks = data.get("talks", [])
        print(f"✓ Parsed {len(self.talks)} talks")

    def parse_tutorials_yaml(self):
        """Parse tutorials.yaml."""
        tutorials_file = self.data_dir / "tutorials.yaml"
        if not tutorials_file.exists():
            print(f"⚠️  {tutorials_file} not found")
            return

        with tutorials_file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.tutorials = data.get("tutorials", data.get("talks", []))
        print(f"✓ Parsed {len(self.tutorials)} tutorials")

    def parse_professional_activities_yaml(self):
        """Parse professional_activities.yaml."""
        activities_file = self.data_dir / "professional_activities.yaml"
        if not activities_file.exists():
            print(f"⚠️  {activities_file} not found")
            return

        with activities_file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        self.professional_organizations = data.get("professional_organizations", []) or []
        self.organizations = data.get("organizations", []) or []
        self.program_committee = data.get("program_committee", []) or []
        self.reviewer = data.get("reviewer", data.get("reviewers", [])) or []

        print(
            "✓ Parsed "
            f"{len(self.professional_organizations)} professional organizations, "
            f"{len(self.organizations)} conference/workshop organizations, "
            f"{len(self.program_committee)} program committee entries, "
            f"{len(self.reviewer)} reviewer entries"
        )

    def _format_years(self, years: Any) -> str:
        """Format single year or year list as plain text."""
        if isinstance(years, list):
            vals = [str(y).strip() for y in years if str(y).strip()]
            return ", ".join(vals)
        if years is None:
            return ""
        val = str(years).strip()
        return val

    def generate_publications_section(self) -> str:
        """Generate publications section grouped by type with continuous numbering."""
        # Group by type
        by_type = {
            "journal": [],
            "conference": [],
            "workshop": [],
            "book-chapter": [],
            "preprint": [],
            "abstract": [],
            "techreport": [],
            "other": []
        }

        for pub in self.publications:
            pub_type = pub.get("type", "other").strip().lower()
            if pub_type not in by_type:
                pub_type = "other"
            by_type[pub_type].append(pub)

        # Sort each type by year (descending)
        for ptype in by_type:
            by_type[ptype].sort(key=lambda p: -int(p.get("year", 0)))

        sections = []

        # Start enumerate once at the beginning
        sections.append("\\begin{enumerate}[leftmargin=2em]")

        # Journal Articles
        if by_type["journal"]:
            sections.append("\\subsection*{Journal Articles}")
            for pub in by_type["journal"]:
                sections.append(self._format_publication(pub))
            sections.append("")

        # Conference Papers
        if by_type["conference"]:
            sections.append("\\subsection*{Conference Papers}")
            for pub in by_type["conference"]:
                sections.append(self._format_publication(pub))
            sections.append("")

        # Workshop Papers
        if by_type["workshop"]:
            sections.append("\\subsection*{Workshop Papers}")
            for pub in by_type["workshop"]:
                sections.append(self._format_publication(pub))
            sections.append("")

        # Book Chapters
        if by_type["book-chapter"]:
            sections.append("\\subsection*{Book Chapters}")
            for pub in by_type["book-chapter"]:
                sections.append(self._format_publication(pub))
            sections.append("")

        # Technical Reports
        if by_type["techreport"]:
            sections.append("\\subsection*{Technical Reports}")
            for pub in by_type["techreport"]:
                sections.append(self._format_publication(pub))
            sections.append("")

        # Close enumerate once at the end
        sections.append("\\end{enumerate}")

        return "\n".join(sections)

    def _format_publication(self, pub: Dict[str, Any]) -> str:
        """Format a single publication entry."""
        title = self.escape_latex(pub.get("title", ""))
        authors = self.escape_latex(pub.get("authors", ""))
        venue = self.escape_latex(pub.get("venue", ""))
        year = pub.get("year", "")
        doi = pub.get("doi", "")
        paper_url = pub.get("paper_url", "")
        note = pub.get("note", "")

        # Build the entry
        parts = []
        if authors:
            parts.append(f"{authors}.")
        if title:
            parts.append(f"\\emph{{{title}}}.")
        if venue:
            parts.append(f"\\textit{{{venue}}},")
        if year:
            parts.append(f"{year}.")

        entry = " ".join(parts)

        # Add DOI as hyperlink
        if doi:
            doi_escaped = self.escape_latex(doi)
            entry += f" DOI: \\href{{https://doi.org/{doi}}}{{{doi_escaped}}}"
        elif paper_url:
            # If no DOI but there's a URL, show the URL
            entry += f" \\href{{{paper_url}}}{{[link]}}"

        # Add note (e.g., Best Paper Award)
        if note:
            note_escaped = self.escape_latex(note)
            entry += f" \\textbf{{({note_escaped})}}"

        return f"  \\item {entry}"

    def generate_presentations_section(self) -> str:
        """Generate talks and tutorials section."""
        sections = []

        # Talks
        if self.talks:
            sections.append("\\subsection*{Talks}")
            sections.append("\\begin{itemize}[leftmargin=2em]")
            # Show only recent talks (last 5 years)
            current_year = datetime.now().year
            recent_talks = [t for t in self.talks
                          if int(t.get("date", "2000").split("-")[0]) >= current_year - 5]

            for talk in sorted(recent_talks, key=lambda t: t.get("date", ""), reverse=True):
                title = self.escape_latex(talk.get("title", ""))
                venue = self.escape_latex(talk.get("venue", ""))
                city = talk.get("city", "")
                country = talk.get("country", "")
                date = talk.get("date", "")

                location = f"{city}, {country}" if city and country else ""
                year = date.split("-")[0] if date else ""

                sections.append(f"  \\item \\textit{{{title}}}, {venue}, {location}, {year}.")
            sections.append("\\end{itemize}")
            sections.append("")

        # Tutorials
        if self.tutorials:
            sections.append("\\subsection*{Tutorials}")
            sections.append("\\begin{itemize}[leftmargin=2em]")
            for talk in sorted(self.tutorials, key=lambda t: t.get("date", ""), reverse=True):
                title = self.escape_latex(talk.get("title", ""))
                venue = self.escape_latex(talk.get("venue", ""))
                city = talk.get("city", "")
                country = talk.get("country", "")
                date = talk.get("date", "")

                location = f"{city}, {country}" if city and country else ""
                year = date.split("-")[0] if date else ""

                sections.append(f"  \\item \\textit{{{title}}}, {venue}, {location}, {year}.")
            sections.append("\\end{itemize}")
            sections.append("")

        return "\n".join(sections)

    def generate_professional_activities_section(self) -> str:
        """Generate professional activities section from professional_activities.yaml."""
        sections = []

        if self.professional_organizations:
            sections.append("\\subsection*{Professional Organizations}")
            sections.append("\\begin{itemize}[leftmargin=2em]")
            for item in self.professional_organizations:
                org = self.escape_latex(str(item.get("organization", item.get("name", ""))))
                role = self.escape_latex(str(item.get("role", "")))
                years = self.escape_latex(self._format_years(item.get("years", item.get("year"))))

                line = ""
                if org and role and years:
                    line = f"\\textbf{{{org}}}, {role} ({years})"
                elif org and role:
                    line = f"\\textbf{{{org}}}, {role}"
                elif org and years:
                    line = f"\\textbf{{{org}}}: {years}"
                else:
                    line = org or role or years

                if line:
                    sections.append(f"  \\item {line}")
            sections.append("\\end{itemize}")
            sections.append("")

        if self.organizations:
            sections.append("\\subsection*{Conference and Workshop Service}")
            sections.append("\\begin{itemize}[leftmargin=2em]")
            for org in self.organizations:
                org_name = self.escape_latex(str(org.get("name", "")))
                entries = org.get("entries", []) or []
                if not org_name and not entries:
                    continue

                if org_name:
                    sections.append(f"  \\item \\textbf{{{org_name}}}")
                else:
                    sections.append("  \\item")

                if entries:
                    sections.append("  \\begin{itemize}[leftmargin=2em]")
                    for entry in entries:
                        year = self.escape_latex(str(entry.get("year", "")))
                        role = self.escape_latex(str(entry.get("role", "")))
                        note = self.escape_latex(str(entry.get("note", "")))

                        line = ""
                        if year and role:
                            line = f"\\textbf{{{year}}} -- {role}"
                        else:
                            line = year or role
                        if note:
                            line += f" ({note})"
                        if line:
                            sections.append(f"    \\item {line}")
                    sections.append("  \\end{itemize}")
            sections.append("\\end{itemize}")
            sections.append("")

        def add_event_year_subsection(title: str, items: List[Dict[str, Any]]) -> None:
            if not items:
                return
            sections.append(f"\\subsection*{{{title}}}")
            sections.append("\\begin{itemize}[leftmargin=2em]")
            for item in items:
                event = self.escape_latex(str(item.get("event", item.get("name", ""))))
                years = self.escape_latex(self._format_years(item.get("years", item.get("year"))))
                note = self.escape_latex(str(item.get("note", "")))

                line = ""
                if event and years:
                    line = f"\\textbf{{{event}}}: {years}"
                else:
                    line = event or years
                if note:
                    line += f" ({note})"
                if line:
                    sections.append(f"  \\item {line}")
            sections.append("\\end{itemize}")
            sections.append("")

        add_event_year_subsection("Program Committee", self.program_committee)
        add_event_year_subsection("Reviewer", self.reviewer)

        return "\n".join(sections)

    def generate_cv(self):
        """Generate the complete CV LaTeX file."""
        # Read template
        template_file = self.cv_dir / "templates" / "cv_template.tex"
        if not template_file.exists():
            print(f"❌ Template not found: {template_file}")
            print("   Please create the template first.")
            return

        with template_file.open("r", encoding="utf-8") as f:
            template = f.read()

        # Generate content sections

        # Professional Experience
        experience_lines = []
        for years, desc in self.experience:
            years_tex = self.escape_latex(years)
            desc_tex = self.escape_latex(desc)
            experience_lines.append(f"{years_tex} & {desc_tex} \\\\")
        experience_content = "\n".join(experience_lines)

        # Education
        education_lines = []
        for year, desc in self.education:
            year_tex = self.escape_latex(year)
            desc_tex = self.escape_latex(desc)
            education_lines.append(f"{year_tex} & {desc_tex} \\\\")
        education_content = "\n".join(education_lines)

        # Awards
        awards_lines = []
        for year, desc in self.awards:
            year_tex = self.escape_latex(year)
            desc_tex = self.escape_latex(desc)
            awards_lines.append(f"  \\item \\textbf{{{year_tex}}} - {desc_tex}")
        awards_content = "\n".join(awards_lines)

        # Publications
        publications_content = self.generate_publications_section()

        # Presentations
        presentations_content = self.generate_presentations_section()

        # Professional Activities
        professional_activities_content = self.generate_professional_activities_section()

        # Replace placeholders in template
        cv_content = template.replace("{{PROFESSIONAL_EXPERIENCE}}", experience_content)
        cv_content = cv_content.replace("{{EDUCATION}}", education_content)
        cv_content = cv_content.replace("{{AWARDS}}", awards_content)
        cv_content = cv_content.replace("{{PUBLICATIONS}}", publications_content)
        cv_content = cv_content.replace("{{PRESENTATIONS}}", presentations_content)
        cv_content = cv_content.replace("{{PROFESSIONAL_ACTIVITIES}}", professional_activities_content)
        cv_content = cv_content.replace("{{GENERATION_DATE}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Write output
        output_file = self.output_dir / "cv.tex"
        with output_file.open("w", encoding="utf-8") as f:
            f.write(cv_content)

        print(f"\n✅ CV generated successfully: {output_file}")
        print(f"\nTo compile:")
        print(f"  cd {self.cv_dir}")
        print(f"  make")
        print(f"\nOr manually:")
        print(f"  cd {self.cv_dir}/output")
        print(f"  pdflatex cv.tex")


def main():
    # Paths
    script_dir = Path(__file__).parent.resolve()
    cv_dir = script_dir
    data_dir = script_dir.parent / "data"

    print("=" * 60)
    print("CV Generator - Auto-generating from website data")
    print("=" * 60)
    print()

    # Create generator
    generator = CVGenerator(data_dir, cv_dir)

    # Parse all data sources
    print("Parsing data sources...")
    generator.parse_about_md()
    generator.parse_awards_yaml()
    generator.parse_publications_yaml()
    generator.build_awards()
    generator.parse_talks_yaml()
    generator.parse_tutorials_yaml()
    generator.parse_professional_activities_yaml()
    print()

    # Generate CV
    print("Generating CV...")
    generator.generate_cv()


if __name__ == "__main__":
    main()
