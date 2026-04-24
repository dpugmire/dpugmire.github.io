#!/usr/bin/env python3
"""Validate the data contracts used by the website and CV generator."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

ALLOWED_PUBLICATION_TYPES = {
    "journal",
    "conference",
    "workshop",
    "techreport",
    "abstract",
    "book-chapter",
    "preprint",
    "other",
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ValidationError(Exception):
    """Raised when validation fails."""


def relpath(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_yaml(path: Path) -> Any:
    if not path.exists():
        raise ValidationError(f"Missing required file: {relpath(path)}")

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise ValidationError(f"Invalid YAML in {relpath(path)}: {exc}") from exc

    return {} if data is None else data


def load_optional_yaml(path: Path) -> Any:
    if not path.exists():
        return {}
    return load_yaml(path)


def expect_mapping(data: Any, path: Path) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError(f"{relpath(path)} must contain a top-level mapping")
    return data


def expect_list(data: dict[str, Any], key: str, path: Path) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list):
        raise ValidationError(
            f"{relpath(path)} must contain a top-level '{key}' list"
        )
    return value


def clean_markdown_cell(value: str) -> str:
    text = str(value or "").strip()
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.strip()


def extract_table_entries(markdown: str, heading: str) -> list[tuple[str, str]]:
    match = re.search(
        rf"### {re.escape(heading)}\s*\n\s*\|.*?\n\s*\|.*?\n((?:\s*\|.*?\n)+)",
        markdown,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise ValidationError(
            f"data/about.md must contain a Markdown table under '### {heading}'"
        )

    entries: list[tuple[str, str]] = []
    rows = match.group(1).strip().splitlines()
    for row in rows:
        row_match = re.match(r"\|\s*([^|]*)\s*\|\s*(.+?)\s*\|", row)
        if not row_match:
            continue

        key = clean_markdown_cell(row_match.group(1))
        desc = clean_markdown_cell(row_match.group(2))
        if not desc:
            continue

        if key:
            entries.append((key, desc))
        elif entries:
            prev_key, prev_desc = entries[-1]
            entries[-1] = (prev_key, f"{prev_desc} {desc}")
        else:
            raise ValidationError(
                f"Found a continuation row before the first entry in '{heading}'"
            )

    if not entries:
        raise ValidationError(
            f"No table entries found under '### {heading}' in data/about.md"
        )

    return entries


def validate_about_md() -> tuple[int, int]:
    path = DATA_DIR / "about.md"
    if not path.exists():
        raise ValidationError("Missing required file: data/about.md")

    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValidationError("data/about.md must not be empty")

    intro = text.split("### ", 1)[0].strip()
    if len(intro) < 80:
        raise ValidationError("data/about.md should contain a non-trivial intro above the tables")

    experience_entries = extract_table_entries(text, "Professional Experience")
    education_entries = extract_table_entries(text, "Education")
    return len(experience_entries), len(education_entries)


def validate_presentations(path: Path, top_level_key: str) -> int:
    data = expect_mapping(load_yaml(path), path)
    items = expect_list(data, top_level_key, path)

    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValidationError(f"{relpath(path)} entry {idx} must be a mapping")

        for field in ("title", "venue", "date"):
            if not str(item.get(field, "")).strip():
                raise ValidationError(
                    f"{relpath(path)} entry {idx} is missing required field '{field}'"
                )

        date = str(item.get("date", "")).strip()
        if not DATE_RE.match(date):
            raise ValidationError(
                f"{relpath(path)} entry {idx} has invalid date '{date}'; use YYYY-MM-DD"
            )

        lat = item.get("lat")
        lon = item.get("lon")
        if (lat is None) != (lon is None):
            raise ValidationError(
                f"{relpath(path)} entry {idx} must provide both lat and lon or neither"
            )

    return len(items)


def validate_keynotes_deprecated() -> None:
    path = DATA_DIR / "keynotes.yaml"
    data = expect_mapping(load_optional_yaml(path), path)
    legacy_talks = data.get("talks", [])
    legacy_keynotes = data.get("keynotes", [])

    if isinstance(legacy_talks, list) and legacy_talks:
        raise ValidationError(
            "data/keynotes.yaml is deprecated; move those entries into data/talks.yaml"
        )
    if isinstance(legacy_keynotes, list) and legacy_keynotes:
        raise ValidationError(
            "data/keynotes.yaml is deprecated; move those entries into data/talks.yaml"
        )


def validate_publications() -> int:
    path = DATA_DIR / "publications.yaml"
    data = expect_mapping(load_yaml(path), path)
    publications = expect_list(data, "publications", path)
    seen_ids: set[str] = set()

    for idx, pub in enumerate(publications, start=1):
        if not isinstance(pub, dict):
            raise ValidationError(f"data/publications.yaml entry {idx} must be a mapping")

        for field in ("id", "title", "authors", "venue", "year", "type"):
            if not str(pub.get(field, "")).strip():
                raise ValidationError(
                    f"data/publications.yaml entry {idx} is missing required field '{field}'"
                )

        pub_id = str(pub["id"]).strip()
        if pub_id in seen_ids:
            raise ValidationError(f"Duplicate publication id '{pub_id}' in data/publications.yaml")
        seen_ids.add(pub_id)

        pub_type = str(pub["type"]).strip()
        if pub_type not in ALLOWED_PUBLICATION_TYPES:
            raise ValidationError(
                "Publication "
                f"'{pub_id}' has invalid type '{pub_type}'. "
                f"Use one of: {', '.join(sorted(ALLOWED_PUBLICATION_TYPES))}"
            )

        year_text = str(pub["year"]).strip()
        if not year_text.isdigit():
            raise ValidationError(f"Publication '{pub_id}' has non-numeric year '{year_text}'")

    return len(publications)


def validate_awards() -> int:
    path = DATA_DIR / "awards.yaml"
    data = expect_mapping(load_yaml(path), path)
    awards = expect_list(data, "awards", path)

    for idx, award in enumerate(awards, start=1):
        if not isinstance(award, dict):
            raise ValidationError(f"data/awards.yaml entry {idx} must be a mapping")
        if not str(award.get("year", "")).strip():
            raise ValidationError(f"data/awards.yaml entry {idx} is missing 'year'")
        if not str(award.get("title", "")).strip():
            raise ValidationError(f"data/awards.yaml entry {idx} is missing 'title'")

    return len(awards)


def validate_professional_activities() -> None:
    path = DATA_DIR / "professional_activities.yaml"
    data = expect_mapping(load_yaml(path), path)

    for key in (
        "professional_organizations",
        "organizations",
        "program_committee",
        "reviewer",
    ):
        value = data.get(key, [])
        if not isinstance(value, list):
            raise ValidationError(f"{relpath(path)} key '{key}' must be a list")


def validate_mentorship() -> None:
    path = DATA_DIR / "mentorship.yaml"
    data = expect_mapping(load_yaml(path), path)

    for key in ("postdoctoral_students", "thesis_advisees"):
        value = data.get(key, [])
        if not isinstance(value, list):
            raise ValidationError(f"{relpath(path)} key '{key}' must be a list")


def main() -> int:
    try:
        exp_count, edu_count = validate_about_md()
        publication_count = validate_publications()
        award_count = validate_awards()
        talk_count = validate_presentations(DATA_DIR / "talks.yaml", "talks")
        tutorial_count = validate_presentations(DATA_DIR / "tutorials.yaml", "tutorials")
        validate_keynotes_deprecated()
        validate_professional_activities()
        validate_mentorship()
    except ValidationError as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1

    print("Validation passed")
    print(f"- about.md: {exp_count} experience entries, {edu_count} education entries")
    print(f"- publications.yaml: {publication_count} publications")
    print(f"- awards.yaml: {award_count} awards")
    print(f"- talks.yaml: {talk_count} talks")
    print(f"- tutorials.yaml: {tutorial_count} tutorials")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
