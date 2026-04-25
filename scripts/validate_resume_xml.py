#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


MIN_BULLETS = 3
MIN_EMPLOYMENT_ENTRIES = 2


class ValidationError(ValueError):
    """Raised when a tailored resume XML file fails validation."""


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def _normalized_text(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.split())


def _first_descendant_text(element: ET.Element, names: set[str]) -> str:
    for descendant in element.iter():
        if descendant is element:
            continue
        if _local_name(descendant.tag).lower() in names:
            text = _normalized_text(descendant.text)
            if text:
                return text
    return ""


def _bullet_count(element: ET.Element) -> int:
    return sum(
        1
        for descendant in element.iter()
        if descendant is not element
        and _local_name(descendant.tag).lower() == "bullet"
        and _normalized_text(descendant.text)
    )


def _project_label(project: ET.Element, index: int) -> str:
    return _first_descendant_text(project, {"title", "name"}) or f"project #{index}"


def _employment_label(entry: ET.Element, index: int) -> str:
    title = _first_descendant_text(entry, {"title", "role", "position"})
    company = _first_descendant_text(entry, {"company", "employer", "organization"})
    if title and company:
        return f"{title}, {company}"
    return title or company or f"employment entry #{index}"


def _project_entries(root: ET.Element) -> list[ET.Element]:
    return [element for element in root.iter() if _local_name(element.tag).lower() == "project"]


def _employment_entries(root: ET.Element) -> list[ET.Element]:
    container_names = {"employment", "experience", "work_experience", "professional_experience"}
    entry_names = {"job", "entry", "position", "role", "employment_entry", "experience_entry"}
    entries: list[ET.Element] = []

    for container in root.iter():
        if _local_name(container.tag).lower() not in container_names:
            continue
        for child in list(container):
            if _local_name(child.tag).lower() in entry_names:
                entries.append(child)

    return entries


def validate_resume_xml_tree(root: ET.Element, *, source: str = "<resume-xml>") -> None:
    errors: list[str] = []
    employment_entries = _employment_entries(root)

    if len(employment_entries) < MIN_EMPLOYMENT_ENTRIES:
        errors.append(
            f"{source}: resume must include at least {MIN_EMPLOYMENT_ENTRIES} employment entries; "
            f"found {len(employment_entries)}."
        )

    for index, project in enumerate(_project_entries(root), start=1):
        count = _bullet_count(project)
        if count < MIN_BULLETS:
            errors.append(
                f"{source}: project '{_project_label(project, index)}' has {count} bullet(s); "
                f"minimum is {MIN_BULLETS}."
            )

    for index, entry in enumerate(employment_entries, start=1):
        count = _bullet_count(entry)
        if count < MIN_BULLETS:
            errors.append(
                f"{source}: employment entry '{_employment_label(entry, index)}' has {count} bullet(s); "
                f"minimum is {MIN_BULLETS}."
            )

    if errors:
        raise ValidationError("\n".join(errors))


def validate_resume_xml_path(path: Path) -> None:
    if not path.exists():
        raise ValidationError(f"{path}: file does not exist.")

    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        raise ValidationError(f"{path}: XML parse failed: {exc}") from exc

    validate_resume_xml_tree(tree.getroot(), source=str(path))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate tailored resume XML for minimum employment entry count, "
            "project bullet counts, and employment bullet counts."
        ),
    )
    parser.add_argument("paths", nargs="+", help="Tailored resume XML path(s).")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    errors: list[str] = []

    for raw_path in args.paths:
        try:
            validate_resume_xml_path(Path(raw_path).expanduser())
        except ValidationError as exc:
            errors.append(str(exc))

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print("Resume XML validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
