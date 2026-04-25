#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.validate_resume_xml import ValidationError as ResumeValidationError
    from scripts.validate_resume_xml import validate_resume_xml_path
except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
    from validate_resume_xml import ValidationError as ResumeValidationError
    from validate_resume_xml import validate_resume_xml_path


ALLOWED_LAYOUT_PROFILES = {"focused_one_page", "dense_one_page", "technical_extended"}
REQUIRED_TEXT_FIELDS = (
    "company",
    "role_title",
    "role_type",
    "location_or_remote",
    "resume_strategy",
    "cover_letter_strategy",
)
REQUIRED_LIST_FIELDS = (
    "top_keywords",
    "top_requirements",
    "requirement_to_evidence",
    "selected_projects",
    "selected_employment",
    "selected_skills",
    "gaps",
)


class ValidationError(ValueError):
    """Raised when match_matrix.json fails validation."""


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValidationError(f"{path}: match matrix does not exist.")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: JSON parse failed: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"{path}: match matrix must be a JSON object.")
    return payload


def layout_profile(matrix: dict[str, Any]) -> str:
    return normalize_text(matrix.get("layout_profile") or matrix.get("chosen_layout_profile"))


def _name_from_entry(entry: Any) -> str:
    if isinstance(entry, str):
        return normalize_text(entry)
    if isinstance(entry, dict):
        return normalize_text(entry.get("name") or entry.get("title"))
    return ""


def validate_match_matrix_payload(matrix: dict[str, Any], *, source: str = "<match-matrix>") -> None:
    errors: list[str] = []

    for field in REQUIRED_TEXT_FIELDS:
        if not normalize_text(matrix.get(field)):
            errors.append(f"{source}: missing required text field: {field}")

    for field in REQUIRED_LIST_FIELDS:
        value = matrix.get(field)
        if not isinstance(value, list):
            errors.append(f"{source}: required field must be a list: {field}")
        elif field != "gaps" and not value:
            errors.append(f"{source}: required list must not be empty: {field}")

    gap_mitigation = matrix.get("gap_mitigation")
    if isinstance(gap_mitigation, str):
        has_gap_mitigation = bool(normalize_text(gap_mitigation))
    elif isinstance(gap_mitigation, list):
        has_gap_mitigation = any(normalize_text(value) for value in gap_mitigation)
    else:
        has_gap_mitigation = False
        errors.append(f"{source}: required field must be a string or list: gap_mitigation")

    if matrix.get("gaps") and not has_gap_mitigation:
        errors.append(f"{source}: gap_mitigation must not be empty when gaps are listed.")

    profile = layout_profile(matrix)
    if profile not in ALLOWED_LAYOUT_PROFILES:
        allowed = ", ".join(sorted(ALLOWED_LAYOUT_PROFILES))
        errors.append(f"{source}: layout_profile must be one of {allowed}; found {profile or '<missing>'}.")

    for index, item in enumerate(matrix.get("requirement_to_evidence") or [], start=1):
        if not isinstance(item, dict):
            errors.append(f"{source}: requirement_to_evidence[{index}] must be an object.")
            continue
        if not normalize_text(item.get("requirement")):
            errors.append(f"{source}: requirement_to_evidence[{index}] is missing requirement.")
        evidence = item.get("evidence")
        if not isinstance(evidence, list) or not any(normalize_text(value) for value in evidence):
            errors.append(f"{source}: requirement_to_evidence[{index}] must include at least one evidence item.")

    for field in ("selected_projects", "selected_employment"):
        for index, item in enumerate(matrix.get(field) or [], start=1):
            if not isinstance(item, dict):
                errors.append(f"{source}: {field}[{index}] must be an object.")
                continue
            if not _name_from_entry(item):
                errors.append(f"{source}: {field}[{index}] is missing name.")
            if not normalize_text(item.get("reason_selected")):
                errors.append(f"{source}: {field}[{index}] is missing reason_selected.")

    for index, item in enumerate(matrix.get("gaps") or [], start=1):
        if isinstance(item, str):
            continue
        if not isinstance(item, dict):
            errors.append(f"{source}: gaps[{index}] must be a string or object.")
            continue
        if not normalize_text(item.get("gap")):
            errors.append(f"{source}: gaps[{index}] is missing gap.")
        if not normalize_text(item.get("mitigation") or item.get("gap_mitigation")):
            errors.append(f"{source}: gaps[{index}] is missing mitigation.")

    if errors:
        raise ValidationError("\n".join(errors))


def validate_match_matrix_path(path: Path, *, resume_xml: Path | None = None) -> dict[str, Any]:
    matrix = load_json_object(path)
    validate_match_matrix_payload(matrix, source=str(path))

    if resume_xml is not None:
        try:
            validate_resume_xml_path(resume_xml)
        except ResumeValidationError as exc:
            raise ValidationError(str(exc)) from exc

    return matrix


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate match_matrix.json and optional tailored resume XML.")
    parser.add_argument("match_matrix", help="Path to match_matrix.json.")
    parser.add_argument("--resume-xml", help="Optional tailored resume XML to validate with the match matrix.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        resume_xml = Path(args.resume_xml).expanduser() if args.resume_xml else None
        validate_match_matrix_path(Path(args.match_matrix).expanduser(), resume_xml=resume_xml)
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print("Match matrix validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
