#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.validate_match_matrix import ALLOWED_LAYOUT_PROFILES, ValidationError as MatchMatrixValidationError
    from scripts.validate_match_matrix import validate_match_matrix_path
except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
    from validate_match_matrix import ALLOWED_LAYOUT_PROFILES, ValidationError as MatchMatrixValidationError
    from validate_match_matrix import validate_match_matrix_path


class ValidationError(ValueError):
    """Raised when an application package manifest fails validation."""


def _resolve_path(raw_value: Any, *, manifest_path: Path) -> Path:
    path = Path(str(raw_value)).expanduser()
    if path.is_absolute():
        return path

    manifest_relative = (manifest_path.parent / path).resolve()
    if manifest_relative.exists():
        return manifest_relative

    return path.resolve()


def _validate_pdf(path: Path, *, key: str) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"Manifest {key} does not exist: {path}"]
    if not path.is_file():
        return [f"Manifest {key} is not a file: {path}"]
    if path.stat().st_size == 0:
        errors.append(f"Manifest {key} is empty: {path}")
    try:
        if not path.read_bytes().startswith(b"%PDF"):
            errors.append(f"Manifest {key} is not a PDF file: {path}")
    except OSError as exc:
        errors.append(f"Manifest {key} could not be read: {path} ({exc})")
    return errors


def validate_application_package_manifest(manifest: dict[str, Any], *, manifest_path: Path) -> None:
    errors: list[str] = []

    for key in ("resume_pdf", "cover_letter_pdf"):
        value = manifest.get(key)
        if not value:
            errors.append(f"Manifest is missing required artifact path: {key}")
            continue
        errors.extend(_validate_pdf(_resolve_path(value, manifest_path=manifest_path), key=key))

    match_matrix = manifest.get("match_matrix")
    if not match_matrix:
        errors.append("Manifest is missing required match_matrix path.")
    else:
        match_matrix_path = _resolve_path(match_matrix, manifest_path=manifest_path)
        try:
            validate_match_matrix_path(match_matrix_path)
        except MatchMatrixValidationError as exc:
            errors.append(str(exc))

    layout_profile = manifest.get("layout_profile")
    if layout_profile not in ALLOWED_LAYOUT_PROFILES:
        allowed = ", ".join(sorted(ALLOWED_LAYOUT_PROFILES))
        errors.append(f"Manifest layout_profile must be one of {allowed}; found {layout_profile or '<missing>'}.")

    generation_report = manifest.get("generation_report")
    if not generation_report:
        errors.append("Manifest is missing generation_report path.")
    else:
        generation_report_path = _resolve_path(generation_report, manifest_path=manifest_path)
        if not generation_report_path.exists():
            errors.append(f"Manifest generation_report does not exist: {generation_report_path}")
        elif generation_report_path.stat().st_size == 0:
            errors.append(f"Manifest generation_report is empty: {generation_report_path}")

    if "tracker_updated" not in manifest:
        errors.append("Manifest is missing tracker_updated status.")
    elif manifest.get("tracker_updated"):
        tracker = manifest.get("tracker")
        if not isinstance(tracker, dict):
            errors.append("Manifest reports tracker_updated=true but tracker details are missing.")
        else:
            for key in ("application_row", "row_count", "replaced_tracker"):
                if key not in tracker:
                    errors.append(f"Tracker details are missing required field: {key}")
            replaced_tracker = tracker.get("replaced_tracker")
            if replaced_tracker and not _resolve_path(replaced_tracker, manifest_path=manifest_path).exists():
                errors.append(f"Tracker replacement path does not exist: {replaced_tracker}")

    if "deleted_inputs" not in manifest:
        errors.append("Manifest is missing deleted_inputs cleanup status.")
    elif not isinstance(manifest.get("deleted_inputs"), list):
        errors.append("Manifest deleted_inputs must be a list.")
    else:
        for raw_path in manifest["deleted_inputs"]:
            deleted_path = _resolve_path(raw_path, manifest_path=manifest_path)
            if deleted_path.exists():
                errors.append(f"Manifest reports deleted input still exists: {deleted_path}")

    validation = manifest.get("validation")
    if validation is not None:
        if not isinstance(validation, dict):
            errors.append("Manifest validation field must be an object when present.")
        else:
            for key, value in validation.items():
                if value != "passed":
                    errors.append(f"Manifest reports validation failure or unknown status for {key}: {value}")

    if errors:
        raise ValidationError("\n".join(errors))


def validate_application_package_manifest_path(path: Path) -> None:
    if not path.exists():
        raise ValidationError(f"{path}: manifest does not exist.")

    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: manifest JSON parse failed: {exc}") from exc

    if not isinstance(manifest, dict):
        raise ValidationError(f"{path}: manifest must contain a JSON object.")

    validate_application_package_manifest(manifest, manifest_path=path.resolve())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate an application package manifest and generated artifacts.")
    parser.add_argument("manifest", help="Path to application_package_manifest.json.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        validate_application_package_manifest_path(Path(args.manifest).expanduser())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print("Application package validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
