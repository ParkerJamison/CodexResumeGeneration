#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_cover_letter import (
    validate_cover_letter_rendered_html,
    validate_cover_letter_source_path,
)

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - environment-specific
    raise SystemExit(
        "Missing dependency: PyYAML.\n"
        "Install the project dependencies with:\n"
        "  ./.venv/bin/python -m pip install -r requirements.txt"
    ) from exc

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ModuleNotFoundError as exc:  # pragma: no cover - environment-specific
    raise SystemExit(
        "Missing dependency: Jinja2.\n"
        "Install the project dependencies with:\n"
        "  ./.venv/bin/python -m pip install -r requirements.txt"
    ) from exc


GREETING_PREFIXES = (
    "dear ",
    "hello ",
    "hi ",
    "to whom it may concern",
)

SIGNOFF_PHRASES = (
    "sincerely",
    "best",
    "best regards",
    "regards",
    "respectfully",
    "kind regards",
    "warm regards",
    "thank you",
    "thanks",
    "yours truly",
)

TRAILING_SIGNOFF_RE = re.compile(
    rf"^(?P<body>.*?)(?:\s+)?(?P<closing>(?:{'|'.join(re.escape(phrase) for phrase in SIGNOFF_PHRASES)})[,!:.;]?)"
    rf"(?:\s+(?P<signature>[A-Za-z][A-Za-z .'\-]*))?\s*$",
    re.IGNORECASE,
)


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.split())


def canonicalize_for_match(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", normalize_text(value).lower())


def normalize_url(value: str) -> str:
    value = normalize_text(value)
    if not value:
        return ""
    if value.startswith(("http://", "https://", "mailto:")):
        return value
    return f"https://{value}"


def load_profile(profile_path: Path) -> dict[str, Any]:
    if not profile_path.exists():
        raise FileNotFoundError(f"Profile not found: {profile_path}")

    with profile_path.open("r", encoding="utf-8") as handle:
        profile = yaml.safe_load(handle) or {}

    if not isinstance(profile, dict):
        raise ValueError(f"Profile must deserialize to a mapping: {profile_path}")

    return profile


def build_candidate(profile: dict[str, Any]) -> dict[str, str]:
    candidate = profile.get("candidate", {})
    return {
        "full_name": normalize_text(candidate.get("full_name")),
        "email": normalize_text(candidate.get("email")),
        "phone": normalize_text(candidate.get("phone")),
        "location": normalize_text(candidate.get("location")),
        "linkedin_label": normalize_text(candidate.get("linkedin")),
        "linkedin_url": normalize_url(candidate.get("linkedin")),
        "portfolio_label": normalize_text(candidate.get("portfolio_url")),
        "portfolio_url": normalize_url(candidate.get("portfolio_url")),
        "github_label": normalize_text(candidate.get("github")),
        "github_url": normalize_url(candidate.get("github")),
    }


def build_contact_items(candidate: dict[str, str]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []

    if candidate.get("phone"):
        items.append({"label": candidate["phone"], "url": ""})
    if candidate.get("email"):
        items.append({"label": candidate["email"], "url": f"mailto:{candidate['email']}"})
    if candidate.get("linkedin_label") and candidate.get("linkedin_url"):
        items.append({"label": candidate["linkedin_label"], "url": candidate["linkedin_url"]})
    if candidate.get("portfolio_label") and candidate.get("portfolio_url"):
        items.append({"label": candidate["portfolio_label"], "url": candidate["portfolio_url"]})
    if candidate.get("github_label") and candidate.get("github_url"):
        items.append({"label": candidate["github_label"], "url": candidate["github_url"]})

    return items


def parse_cover_letter_input(input_path: Path) -> list[str]:
    if not input_path.exists():
        raise FileNotFoundError(f"Cover letter input not found: {input_path}")

    raw_text = input_path.read_text(encoding="utf-8").strip()
    if not raw_text:
        raise ValueError(f"Cover letter input is empty: {input_path}")

    paragraphs = [normalize_text(part) for part in re.split(r"\n\s*\n", raw_text) if normalize_text(part)]
    if not paragraphs:
        raise ValueError(f"Cover letter body is empty: {input_path}")

    return paragraphs


def strip_leading_salutation(paragraph: str) -> str:
    normalized = normalize_text(paragraph)
    if not normalized:
        return ""

    lowered = normalized.lower()
    prefix = next((candidate for candidate in GREETING_PREFIXES if lowered.startswith(candidate)), "")
    if not prefix:
        return normalized

    remainder = normalized[len(prefix) :].lstrip()
    if not remainder:
        return ""

    for separator in (",", ":", ";", ".", "!"):
        separator_index = remainder.find(separator)
        if separator_index != -1:
            body = normalize_text(remainder[separator_index + 1 :])
            return body

    return ""


def strip_trailing_signoff(paragraph: str, signature_values: set[str]) -> str:
    normalized = normalize_text(paragraph)
    if not normalized:
        return ""

    if canonicalize_for_match(normalized) in signature_values:
        return ""

    match = TRAILING_SIGNOFF_RE.match(normalized)
    if not match:
        return normalized

    tail = normalize_text(match.group("signature"))
    if tail and canonicalize_for_match(tail) not in signature_values:
        return normalized

    return normalize_text(match.group("body"))


def sanitize_cover_letter_paragraphs(
    paragraphs: list[str],
    *,
    candidate_name: str,
    signature: str,
) -> list[str]:
    cleaned = [normalize_text(paragraph) for paragraph in paragraphs if normalize_text(paragraph)]
    if not cleaned:
        return cleaned

    signature_values = {
        canonicalize_for_match(candidate_name),
        canonicalize_for_match(signature),
    }
    signature_values.discard("")

    while cleaned:
        first_cleaned = strip_leading_salutation(cleaned[0])
        if first_cleaned:
            cleaned[0] = first_cleaned
            break
        cleaned.pop(0)

    if not cleaned:
        return cleaned

    while cleaned:
        last_index = len(cleaned) - 1
        last_cleaned = strip_trailing_signoff(cleaned[last_index], signature_values)
        if last_cleaned:
            cleaned[last_index] = last_cleaned
            break
        cleaned.pop(last_index)

    return [paragraph for paragraph in cleaned if paragraph]


def build_letter_context(input_path: Path, profile_path: Path) -> dict[str, Any]:
    validate_cover_letter_source_path(input_path)

    profile = load_profile(profile_path)
    candidate = build_candidate(profile)
    paragraphs = parse_cover_letter_input(input_path)
    paragraphs = sanitize_cover_letter_paragraphs(
        paragraphs,
        candidate_name=candidate.get("full_name", ""),
        signature=candidate.get("full_name", ""),
    )

    today_label = datetime.now().strftime("%B %-d, %Y")

    context = {
        "candidate": candidate,
        "contact_items": build_contact_items(candidate),
        "date": today_label,
        "salutation": "Dear Hiring Team,",
        "paragraphs": paragraphs,
        "closing": "Sincerely,",
        "signature": candidate.get("full_name", ""),
    }

    return context


def render_html(context: dict[str, Any], template_path: Path) -> str:
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    environment = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = environment.get_template(template_path.name)
    rendered_html = template.render(**context)
    validate_cover_letter_rendered_html(rendered_html, source=f"rendered HTML from {template_path}")
    return rendered_html


def write_pdf_with_weasyprint(rendered_html: str, template_path: Path, output_pdf: Path) -> None:
    try:
        from weasyprint import HTML
    except Exception as exc:  # pragma: no cover - environment-specific
        raise RuntimeError(
            "WeasyPrint is installed but could not initialize its native libraries.\n"
            f"{exc}\n\n"
            "On macOS, run the generator through bin/run_cover_letter.sh so the\n"
            "required Homebrew library paths and Fontconfig cache paths are set."
        ) from exc

    try:
        HTML(string=rendered_html, base_url=str(template_path.parent.resolve())).write_pdf(str(output_pdf))
    except Exception as exc:  # pragma: no cover - environment-specific
        raise RuntimeError(f"WeasyPrint failed to generate the cover letter PDF.\n{exc}") from exc


def write_pdf(rendered_html: str, template_path: Path, output_pdf: Path) -> None:
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    if output_pdf.exists():
        output_pdf.unlink()
    write_pdf_with_weasyprint(rendered_html, template_path, output_pdf)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a cover letter PDF from tailored text input.")
    parser.add_argument("text_input", help="Path to the tailored TXT cover letter input.")
    parser.add_argument(
        "output_pdf",
        nargs="?",
        help="Path to the output PDF. Defaults to the TXT filename with a .pdf extension.",
    )
    parser.add_argument(
        "--template",
        default="templates/coverLetterTemplate.html",
        help="Path to the Jinja HTML template. Defaults to templates/coverLetterTemplate.html.",
    )
    parser.add_argument(
        "--profile",
        default="GenFiles/profile.yml",
        help="Path to the profile.yml file used for candidate contact data.",
    )
    parser.add_argument(
        "--html-output",
        help="Optional path to write the rendered HTML for inspection.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    input_path = Path(args.text_input).expanduser().resolve()
    template_path = Path(args.template).expanduser().resolve()
    profile_path = Path(args.profile).expanduser().resolve()

    if args.output_pdf:
        output_pdf = Path(args.output_pdf).expanduser().resolve()
    else:
        output_pdf = input_path.with_suffix(".pdf")

    context = build_letter_context(input_path, profile_path)
    rendered_html = render_html(context, template_path)

    if args.html_output:
        html_output = Path(args.html_output).expanduser().resolve()
        html_output.parent.mkdir(parents=True, exist_ok=True)
        html_output.write_text(rendered_html, encoding="utf-8")
        print(f"Wrote HTML preview to {html_output}")

    write_pdf(rendered_html, template_path, output_pdf)
    print(f"Wrote cover letter PDF to {output_pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
