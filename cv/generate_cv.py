#!/usr/bin/env python3
"""
generate_cv.py - Comprehensive CV Generator

Generates a complete academic CV from website data sources:
- data/about.md: Professional Experience, Education
- data/publications.yaml: Publications
- data/talks.yaml: Invited talks
- data/keynotes.yaml: Keynote presentations
- data/tutorials.yaml: Tutorials

Usage:
    python generate_cv.py

Output:
    cv/generated/cv.tex (ready to compile with pdflatex)
"""

import re
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class CVGenerator:
    def __init__(self, data_dir: Path, cv_dir: Path):
        self.data_dir = data_dir
        self.cv_dir = cv_dir
        self.output_dir = cv_dir / "generated"
        self.output_dir.mkdir(exist_ok=True)

        # Data containers
        self.education = []
        self.experience = []
        self.awards = []
        self.publications = []
        self.talks = []
        self.keynotes = []
        self.tutorials = []

    def escape_latex(self, s: str) -> str:
        """Escape special LaTeX characters."""
        if not s:
            return ""
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

        # Extract Professional Experience table
        exp_match = re.search(
            r'### Professional Experience\s*\n\s*\|.*?\n\s*\|.*?\n((?:\s*\|.*?\n)+)',
            content,
            re.MULTILINE | re.DOTALL
        )
        if exp_match:
            table_rows = exp_match.group(1).strip().split('\n')
            for row in table_rows:
                # Parse: | 2021–Present | **Position**, Org |
                match = re.match(r'\|\s*([^|]+)\s*\|\s*(.+?)\s*\|', row)
                if match:
                    years = match.group(1).strip()
                    desc = match.group(2).strip()
                    # Remove markdown formatting
                    desc = re.sub(r'\*\*([^*]+)\*\*', r'\1', desc)
                    desc = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', desc)
                    self.experience.append((years, desc))

        # Extract Education table
        edu_match = re.search(
            r'### Education\s*\n\s*\|.*?\n\s*\|.*?\n((?:\s*\|.*?\n)+)',
            content,
            re.MULTILINE | re.DOTALL
        )
        if edu_match:
            table_rows = edu_match.group(1).strip().split('\n')
            for row in table_rows:
                match = re.match(r'\|\s*([^|]+)\s*\|\s*(.+?)\s*\|', row)
                if match:
                    year = match.group(1).strip()
                    desc = match.group(2).strip()
                    # Remove markdown formatting from both year and description
                    year = re.sub(r'\*\*([^*]+)\*\*', r'\1', year)
                    desc = re.sub(r'\*\*([^*]+)\*\*', r'\1', desc)
                    desc = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', desc)
                    # Skip empty rows
                    if year and desc:
                        self.education.append((year, desc))

        # Extract Awards & Honors table
        awards_match = re.search(
            r'### Awards & Honors\s*\n\s*\|.*?\n\s*\|.*?\n((?:\s*\|.*?\n)+)',
            content,
            re.MULTILINE | re.DOTALL
        )
        if awards_match:
            table_rows = awards_match.group(1).strip().split('\n')
            current_year = None
            for row in table_rows:
                match = re.match(r'\|\s*([^|]+)\s*\|\s*(.+?)\s*\|', row)
                if match:
                    year = match.group(1).strip()
                    desc = match.group(2).strip()
                    # Remove markdown formatting
                    year = re.sub(r'\*\*([^*]+)\*\*', r'\1', year)
                    desc = re.sub(r'\*\*([^*]+)\*\*', r'\1', desc)
                    desc = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', desc)

                    # Handle multi-row awards (where year is empty on continuation rows)
                    if year:
                        current_year = year
                        if desc:  # Only add if there's a description
                            self.awards.append((current_year, desc))
                    elif desc and current_year:
                        # Continuation row - append to previous award
                        if self.awards:
                            prev_year, prev_desc = self.awards[-1]
                            self.awards[-1] = (prev_year, f"{prev_desc} {desc}")

        print(f"✓ Parsed {len(self.experience)} experience entries, {len(self.education)} education entries, {len(self.awards)} awards")

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

    def parse_keynotes_yaml(self):
        """Parse keynotes.yaml."""
        keynotes_file = self.data_dir / "keynotes.yaml"
        if not keynotes_file.exists():
            print(f"⚠️  {keynotes_file} not found")
            return

        with keynotes_file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.keynotes = data.get("keynotes", [])
        print(f"✓ Parsed {len(self.keynotes)} keynotes")

    def parse_tutorials_yaml(self):
        """Parse tutorials.yaml."""
        tutorials_file = self.data_dir / "tutorials.yaml"
        if not tutorials_file.exists():
            print(f"⚠️  {tutorials_file} not found")
            return

        with tutorials_file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.tutorials = data.get("tutorials", [])
        print(f"✓ Parsed {len(self.tutorials)} tutorials")

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
        """Generate invited talks, keynotes, and tutorials section."""
        sections = []

        # Keynotes
        if self.keynotes:
            sections.append("\\subsection*{Keynote Presentations}")
            sections.append("\\begin{itemize}[leftmargin=2em]")
            for talk in sorted(self.keynotes, key=lambda t: t.get("date", ""), reverse=True):
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

        # Invited Talks
        if self.talks:
            sections.append("\\subsection*{Invited Talks}")
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

        # Replace placeholders in template
        cv_content = template.replace("{{PROFESSIONAL_EXPERIENCE}}", experience_content)
        cv_content = cv_content.replace("{{EDUCATION}}", education_content)
        cv_content = cv_content.replace("{{AWARDS}}", awards_content)
        cv_content = cv_content.replace("{{PUBLICATIONS}}", publications_content)
        cv_content = cv_content.replace("{{PRESENTATIONS}}", presentations_content)
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
        print(f"  cd {self.cv_dir}/generated")
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
    generator.parse_publications_yaml()
    generator.parse_talks_yaml()
    generator.parse_keynotes_yaml()
    generator.parse_tutorials_yaml()
    print()

    # Generate CV
    print("Generating CV...")
    generator.generate_cv()


if __name__ == "__main__":
    main()
