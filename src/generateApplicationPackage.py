#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from generateCoverLetter import (
    build_letter_context,
    render_html as render_cover_letter_html,
    write_pdf as write_cover_letter_pdf,
)
from generateResume import build_context as build_resume_context
from generateResume import render_html as render_resume_html
from generateResume import write_pdf as write_resume_pdf
from scripts.validate_match_matrix import layout_profile, validate_match_matrix_path
from updateApplicationTracker import build_tracker_record, update_tracker_csv


def load_job_context(job_context_path: Path) -> dict[str, Any]:
    if not job_context_path.exists():
        raise FileNotFoundError(f"Job context not found: {job_context_path}")

    payload = json.loads(job_context_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {job_context_path}")
    return payload


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def build_output_basename(job_context: dict[str, Any]) -> str:
    explicit = normalize_text(job_context.get("output_basename"))
    source = explicit or normalize_text(job_context.get("company")) or "ApplicationPackage"
    parts = ["".join(character for character in token if character.isalnum()) for token in source.replace("/", " ").split()]
    parts = [part for part in parts if part]
    if not parts:
        return "ApplicationPackage"
    return "".join(part[:1].upper() + part[1:] for part in parts)


def repo_relative_string(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def write_text_file(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


def first_text(value: Any, *keys: str) -> str:
    if isinstance(value, dict):
        for key in keys:
            text = normalize_text(value.get(key))
            if text:
                return text
        return ""
    return normalize_text(value)


def bullet_lines(values: Any, *, name_keys: tuple[str, ...] = ("name", "title")) -> list[str]:
    if not isinstance(values, list):
        return []

    lines: list[str] = []
    for value in values:
        if isinstance(value, dict):
            name = first_text(value, *name_keys)
            reason = first_text(value, "reason_selected", "mitigation", "gap_mitigation")
            priority = first_text(value, "priority")
            details = " - ".join(part for part in (reason, f"priority: {priority}" if priority else "") if part)
            lines.append(f"- {name}: {details}" if details else f"- {name}")
        else:
            text = normalize_text(value)
            if text:
                lines.append(f"- {text}")
    return [line for line in lines if line != "- "]


def write_generation_report(
    report_path: Path,
    match_matrix: dict[str, Any],
    validation: dict[str, str],
    resume_output: Path,
    cover_letter_output: Path,
) -> None:
    profile = layout_profile(match_matrix)
    lines = [
        "# Generation Report",
        "",
        f"- Role type: {normalize_text(match_matrix.get('role_type'))}",
        f"- Chosen layout profile: {profile}",
        f"- Resume PDF: {resume_output}",
        f"- Cover letter PDF: {cover_letter_output}",
        "",
        "## Top Keywords",
        *bullet_lines(match_matrix.get("top_keywords")),
        "",
        "## Selected Projects",
        *bullet_lines(match_matrix.get("selected_projects")),
        "",
        "## Selected Employment",
        *bullet_lines(match_matrix.get("selected_employment")),
        "",
        "## Known Gaps And Mitigation",
        *bullet_lines(match_matrix.get("gaps"), name_keys=("gap", "name", "title")),
        "",
        "## Validation Results",
        *(f"- {key}: {value}" for key, value in validation.items()),
        "",
    ]
    write_text_file(report_path, "\n".join(lines))


def render_resume_package(
    resume_xml: Path,
    template_path: Path,
    profile_path: Path,
    output_pdf: Path,
    html_output: Path | None,
) -> dict[str, str]:
    context = build_resume_context(resume_xml, profile_path)
    rendered_html = render_resume_html(context, template_path)
    if html_output:
        write_text_file(html_output, rendered_html)
    write_resume_pdf(rendered_html, template_path, output_pdf)
    return {
        "pdf": str(output_pdf),
        "html": str(html_output) if html_output else "",
    }


def render_cover_letter_package(
    cover_letter_txt: Path,
    template_path: Path,
    profile_path: Path,
    output_pdf: Path,
    html_output: Path | None,
) -> dict[str, str]:
    context = build_letter_context(cover_letter_txt, profile_path)
    rendered_html = render_cover_letter_html(context, template_path)
    if html_output:
        write_text_file(html_output, rendered_html)
    write_cover_letter_pdf(rendered_html, template_path, output_pdf)
    return {
        "pdf": str(output_pdf),
        "html": str(html_output) if html_output else "",
    }


def should_delete_input(path: Path, temp_root: Path) -> bool:
    try:
        path.resolve().relative_to(temp_root.resolve())
        return True
    except ValueError:
        return False


def run_tracker_update(
    tracker_path: Path,
    job_context: dict[str, Any],
    resume_tracker_path: str,
    cover_letter_tracker_path: str,
) -> dict[str, Any]:
    tracker_temp_path = tracker_path.with_name(f"{tracker_path.stem}.updated{tracker_path.suffix}")
    tracker_record = build_tracker_record(job_context, resume_tracker_path, cover_letter_tracker_path)
    result = update_tracker_csv(tracker_path, tracker_temp_path, tracker_record)
    tracker_temp_path.replace(tracker_path)
    result["replaced_tracker"] = str(tracker_path)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate resume and cover letter PDFs, update the tracker, and emit a manifest.",
    )
    parser.add_argument("job_context", help="Path to the shared JSON job context.")
    parser.add_argument("resume_xml", help="Path to the tailored resume XML input.")
    parser.add_argument("cover_letter_txt", help="Path to the tailored cover letter TXT input.")
    parser.add_argument("--profile", default="GenFiles/profile.yml", help="Profile YAML path.")
    parser.add_argument("--resume-template", default="templates/resumeTemplate.html", help="Resume template path.")
    parser.add_argument("--cover-letter-template", default="templates/coverLetterTemplate.html", help="Cover letter template path.")
    parser.add_argument("--tracker", default="data/Application Tracker.txt", help="Application tracker text file path.")
    parser.add_argument("--resume-output", help="Resume PDF output path.")
    parser.add_argument("--cover-letter-output", help="Cover letter PDF output path.")
    parser.add_argument("--manifest-output", help="Manifest JSON output path.")
    parser.add_argument("--html-output-dir", help="Optional directory for rendered HTML previews.")
    parser.add_argument("--match-matrix", help="Path to match_matrix.json. Defaults to a sibling of job_context.json.")
    parser.add_argument("--generation-report", help="Path to write generation_report.md. Defaults to a sibling of job_context.json.")
    parser.add_argument("--temp-root", default="GenFiles/tmp", help="Root directory for temp artifacts and manifests.")
    parser.add_argument("--skip-tracker", action="store_true", help="Generate PDFs without updating the tracker.")
    parser.add_argument("--keep-inputs", action="store_true", help="Keep the resume XML and cover letter TXT even if they are under the temp root.")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    repo_root = REPO_ROOT
    job_context_path = Path(args.job_context).expanduser().resolve()
    resume_xml = Path(args.resume_xml).expanduser().resolve()
    cover_letter_txt = Path(args.cover_letter_txt).expanduser().resolve()
    profile_path = Path(args.profile).expanduser().resolve()
    resume_template_path = Path(args.resume_template).expanduser().resolve()
    cover_letter_template_path = Path(args.cover_letter_template).expanduser().resolve()
    tracker_path = Path(args.tracker).expanduser().resolve()
    temp_root = Path(args.temp_root).expanduser().resolve()
    match_matrix_path = (
        Path(args.match_matrix).expanduser().resolve()
        if args.match_matrix
        else (job_context_path.parent / "match_matrix.json").resolve()
    )
    generation_report_path = (
        Path(args.generation_report).expanduser().resolve()
        if args.generation_report
        else (job_context_path.parent / "generation_report.md").resolve()
    )

    job_context = load_job_context(job_context_path)
    output_basename = build_output_basename(job_context)
    match_matrix = validate_match_matrix_path(match_matrix_path, resume_xml=resume_xml)
    selected_layout_profile = layout_profile(match_matrix)

    if args.resume_output:
        resume_output = Path(args.resume_output).expanduser().resolve()
    else:
        resume_output = (repo_root / "GenCoverLetters" / f"{output_basename}-Resume.pdf").resolve()

    if args.cover_letter_output:
        cover_letter_output = Path(args.cover_letter_output).expanduser().resolve()
    else:
        cover_letter_output = (repo_root / "GenCoverLetters" / f"{output_basename}-Cover-Letter.pdf").resolve()

    package_temp_dir = (temp_root / output_basename).resolve()
    package_temp_dir.mkdir(parents=True, exist_ok=True)

    if args.manifest_output:
        manifest_output = Path(args.manifest_output).expanduser().resolve()
    else:
        manifest_output = (package_temp_dir / "application_package_manifest.json").resolve()

    if args.html_output_dir:
        html_output_dir = Path(args.html_output_dir).expanduser().resolve()
    else:
        html_output_dir = None

    resume_html_output = html_output_dir / "resume.html" if html_output_dir else None
    cover_letter_html_output = html_output_dir / "cover_letter.html" if html_output_dir else None

    resume_artifacts = render_resume_package(
        resume_xml,
        resume_template_path,
        profile_path,
        resume_output,
        resume_html_output,
    )
    cover_letter_artifacts = render_cover_letter_package(
        cover_letter_txt,
        cover_letter_template_path,
        profile_path,
        cover_letter_output,
        cover_letter_html_output,
    )

    resume_tracker_path = repo_relative_string(resume_output, repo_root)
    cover_letter_tracker_path = repo_relative_string(cover_letter_output, repo_root)

    tracker_result: dict[str, Any] | None = None
    if not args.skip_tracker:
        tracker_result = run_tracker_update(
            tracker_path,
            job_context,
            resume_tracker_path,
            cover_letter_tracker_path,
        )

    deleted_inputs: list[str] = []
    if not args.keep_inputs:
        for input_path in (resume_xml, cover_letter_txt):
            if should_delete_input(input_path, temp_root) and input_path.exists():
                input_path.unlink()
                deleted_inputs.append(str(input_path))

    validation = {
        "match_matrix": "passed",
        "resume_xml": "passed",
        "cover_letter_txt": "passed",
        "cover_letter_rendered_html": "passed",
    }

    write_generation_report(
        generation_report_path,
        match_matrix,
        validation,
        resume_output,
        cover_letter_output,
    )

    manifest = {
        "company": normalize_text(job_context.get("company")),
        "role": normalize_text(job_context.get("role")),
        "output_basename": output_basename,
        "job_context": str(job_context_path),
        "match_matrix": str(match_matrix_path),
        "layout_profile": selected_layout_profile,
        "generation_report": str(generation_report_path),
        "resume_pdf": str(resume_output),
        "cover_letter_pdf": str(cover_letter_output),
        "resume_pdf_tracker_path": resume_tracker_path,
        "cover_letter_pdf_tracker_path": cover_letter_tracker_path,
        "resume_html": resume_artifacts["html"],
        "cover_letter_html": cover_letter_artifacts["html"],
        "tracker_updated": tracker_result is not None,
        "tracker": tracker_result,
        "deleted_inputs": deleted_inputs,
        "validation": validation,
        "assumptions": job_context.get("assumptions", []),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }

    write_text_file(manifest_output, json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
