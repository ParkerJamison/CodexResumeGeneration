#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_resume_xml import validate_resume_xml_path

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

try:
    from lxml import etree
except ModuleNotFoundError as exc:  # pragma: no cover - environment-specific
    raise SystemExit(
        "Missing dependency: lxml.\n"
        "Install the project dependencies with:\n"
        "  ./.venv/bin/python -m pip install -r requirements.txt"
    ) from exc


PRESENT_TOKENS = {"present", "current", "now"}


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.split())


def find_text(element: etree._Element, path: str) -> str:
    return normalize_text(element.findtext(path))


def bullet_texts(element: etree._Element, path: str) -> list[str]:
    bullets: list[str] = []
    for bullet in element.findall(path):
        text = normalize_text(bullet.text)
        if text:
            bullets.append(text)
    return bullets


def format_date(raw_value: str) -> str:
    raw_value = normalize_text(raw_value)
    if not raw_value:
        return ""

    if raw_value.lower() in PRESENT_TOKENS:
        return "Present"

    for input_format, output_format in (
        ("%Y-%m-%d", "%b %Y"),
        ("%Y-%m", "%b %Y"),
        ("%Y", "%Y"),
    ):
        try:
            return datetime.strptime(raw_value, input_format).strftime(output_format)
        except ValueError:
            continue

    return raw_value


def format_date_range(start_date: str, end_date: str) -> str:
    start_label = format_date(start_date)
    end_label = format_date(end_date)

    if start_label and end_label:
        return f"{start_label} - {end_label}"
    return start_label or end_label


def normalize_url(value: str) -> str:
    value = normalize_text(value)
    if not value:
        return ""
    if value.startswith(("http://", "https://", "mailto:")):
        return value
    return f"https://{value}"


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


def build_contact_items(candidate: dict[str, str]) -> dict[str, list[dict[str, str]]]:
    primary: list[dict[str, str]] = []
    secondary: list[dict[str, str]] = []

    if candidate.get("phone"):
        primary.append({"label": candidate["phone"], "url": ""})
    if candidate.get("email"):
        primary.append({"label": candidate["email"], "url": f"mailto:{candidate['email']}"})
    if candidate.get("github_label") and candidate.get("github_url"):
        secondary.append({"label": candidate["github_label"], "url": candidate["github_url"]})
    if candidate.get("linkedin_label") and candidate.get("linkedin_url"):
        secondary.append({"label": candidate["linkedin_label"], "url": candidate["linkedin_url"]})
    if candidate.get("portfolio_label") and candidate.get("portfolio_url"):
        secondary.append({"label": candidate["portfolio_label"], "url": candidate["portfolio_url"]})

    return {"primary": primary, "secondary": secondary}


def build_summary(root: etree._Element, profile: dict[str, Any]) -> str:
    xml_summary = find_text(root, "summary")
    if xml_summary:
        return xml_summary

    narrative = profile.get("narrative", {})
    return normalize_text(narrative.get("headline"))


def parse_education(root: etree._Element) -> list[dict[str, str]]:
    education_entries: list[dict[str, str]] = []

    for entry in root.findall("./education/entry"):
        school = find_text(entry, "school")
        degree = find_text(entry, "degree")
        major = find_text(entry, "major")
        gpa = find_text(entry, "gpa")
        graduation = find_text(entry, "graduation_date") or find_text(entry, "graduation_year")

        degree_line = ""
        if degree and major:
            degree_line = f"{degree} in {major}"
        else:
            degree_line = degree or major

        subline_parts = [part for part in (degree_line, f"GPA: {gpa}" if gpa else "") if part]

        education_entries.append(
            {
                "school": school,
                "date": format_date(graduation),
                "subline": ", ".join(subline_parts),
            }
        )

    return [entry for entry in education_entries if entry["school"]]


def parse_skills(root: etree._Element) -> list[dict[str, Any]]:
    categories: list[dict[str, Any]] = []

    for category in root.findall("./technical_skills/category"):
        name = normalize_text(category.get("name")) or find_text(category, "name")
        items = [normalize_text(skill.text) for skill in category.findall("./skill")]
        items = [item for item in items if item]
        if name and items:
            categories.append({"name": name, "skill_list": items})

    return categories


def parse_projects(root: etree._Element) -> list[dict[str, Any]]:
    projects: list[dict[str, Any]] = []

    for project in root.findall("./projects/project"):
        title = find_text(project, "title")
        if not title:
            continue

        projects.append(
            {
                "title": title,
                "meta": find_text(project, "tech_stack"),
                "summary": find_text(project, "description"),
                "bullets": bullet_texts(project, "./highlights/bullet"),
            }
        )

    return projects


def parse_employment(root: etree._Element) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []

    for job in root.findall("./employment/job"):
        title = find_text(job, "title")
        company = find_text(job, "company")
        if not (title or company):
            continue

        jobs.append(
            {
                "title": title,
                "company": company,
                "location": find_text(job, "location"),
                "date_range": format_date_range(find_text(job, "start_date"), find_text(job, "end_date")),
                "bullets": bullet_texts(job, "./responsibilities/bullet"),
            }
        )

    return jobs


def load_profile(profile_path: Path) -> dict[str, Any]:
    if not profile_path.exists():
        raise FileNotFoundError(f"Profile not found: {profile_path}")

    with profile_path.open("r", encoding="utf-8") as handle:
        profile = yaml.safe_load(handle) or {}

    if not isinstance(profile, dict):
        raise ValueError(f"Profile must deserialize to a mapping: {profile_path}")

    return profile


def build_context(xml_path: Path, profile_path: Path) -> dict[str, Any]:
    if not xml_path.exists():
        raise FileNotFoundError(f"XML resume input not found: {xml_path}")

    validate_resume_xml_path(xml_path)

    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(str(xml_path), parser)
    root = tree.getroot()

    profile = load_profile(profile_path)
    candidate = build_candidate(profile)

    contact_items = build_contact_items(candidate)

    return {
        "candidate": candidate,
        "contact_primary_items": contact_items["primary"],
        "contact_secondary_items": contact_items["secondary"],
        "summary": build_summary(root, profile),
        "education": parse_education(root),
        "skills": parse_skills(root),
        "projects": parse_projects(root),
        "employment": parse_employment(root),
    }


def render_html(context: dict[str, Any], template_path: Path) -> str:
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    environment = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = environment.get_template(template_path.name)
    return template.render(**context)


def write_pdf_with_weasyprint(rendered_html: str, template_path: Path, output_pdf: Path) -> None:
    try:
        from weasyprint import HTML
    except Exception as exc:  # pragma: no cover - environment-specific
        message = [
            "WeasyPrint is installed but could not initialize its native libraries.",
            str(exc),
        ]
        if sys.platform == "darwin":
            message.extend(
                [
                    "",
                    "On macOS, run the generator through bin/run_resume.sh so the",
                    "required Homebrew library paths and Fontconfig cache paths are set.",
                ]
            )
        raise RuntimeError(
            "\n".join(message)
        ) from exc

    try:
        HTML(string=rendered_html, base_url=str(template_path.parent.resolve())).write_pdf(str(output_pdf))
    except Exception as exc:  # pragma: no cover - environment-specific
        raise RuntimeError(f"WeasyPrint failed to generate the PDF.\n{exc}") from exc


def write_pdf(rendered_html: str, template_path: Path, output_pdf: Path) -> None:
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    if output_pdf.exists():
        output_pdf.unlink()
    write_pdf_with_weasyprint(rendered_html, template_path, output_pdf)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a resume PDF from tailored XML input.")
    parser.add_argument("xml_input", help="Path to the tailored XML resume input.")
    parser.add_argument(
        "output_pdf",
        nargs="?",
        help="Path to the output PDF. Defaults to the XML filename with a .pdf extension.",
    )
    parser.add_argument(
        "--template",
        default="templates/resumeTemplate.html",
        help="Path to the Jinja HTML template. Defaults to templates/resumeTemplate.html.",
    )
    parser.add_argument(
        "--profile",
        default="GenFiles/profile.yml",
        help="Path to the profile.yml file used for header and summary data.",
    )
    parser.add_argument(
        "--html-output",
        help="Optional path to write the rendered HTML for inspection.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    xml_path = Path(args.xml_input).expanduser().resolve()
    template_path = Path(args.template).expanduser().resolve()
    profile_path = Path(args.profile).expanduser().resolve()

    if args.output_pdf:
        output_pdf = Path(args.output_pdf).expanduser().resolve()
    else:
        output_pdf = xml_path.with_suffix(".pdf")

    context = build_context(xml_path, profile_path)
    rendered_html = render_html(context, template_path)

    if args.html_output:
        html_output = Path(args.html_output).expanduser().resolve()
        html_output.parent.mkdir(parents=True, exist_ok=True)
        html_output.write_text(rendered_html, encoding="utf-8")
        print(f"Wrote HTML preview to {html_output}")

    write_pdf(rendered_html, template_path, output_pdf)
    print(f"Wrote resume PDF to {output_pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
