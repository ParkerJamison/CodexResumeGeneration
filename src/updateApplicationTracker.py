#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any


TRACKER_HEADERS = [
    "Date Added",
    "Company",
    "Role",
    "Location",
    "Work Type",
    "Source",
    "Job Link",
    "Job Description / Key Details",
    "Priority",
    "Match Notes",
    "Resume Used",
    "Cover Letter File",
    "Cover Letter Status",
    "Application Date",
    "Current Status",
    "Last Status Update",
    "Response Date",
    "Response Outcome",
    "Follow-up Date",
    "Interview Date",
    "Contact Name",
    "Contact Email",
    "Days Since Applied",
    "Next Action",
    "Notes",
]

CONTEXT_TO_HEADER = {
    "date_added": "Date Added",
    "company": "Company",
    "role": "Role",
    "location": "Location",
    "work_type": "Work Type",
    "source": "Source",
    "job_link": "Job Link",
    "job_description": "Job Description / Key Details",
    "priority": "Priority",
    "match_notes": "Match Notes",
    "resume_used": "Resume Used",
    "cover_letter_file": "Cover Letter File",
    "cover_letter_status": "Cover Letter Status",
    "application_date": "Application Date",
    "current_status": "Current Status",
    "last_status_update": "Last Status Update",
    "response_date": "Response Date",
    "response_outcome": "Response Outcome",
    "follow_up_date": "Follow-up Date",
    "interview_date": "Interview Date",
    "contact_name": "Contact Name",
    "contact_email": "Contact Email",
    "days_since_applied": "Days Since Applied",
    "next_action": "Next Action",
    "notes": "Notes",
}

REQUIRED_HEADERS = {
    "Date Added",
    "Company",
    "Role",
    "Resume Used",
    "Cover Letter File",
    "Cover Letter Status",
    "Current Status",
}


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def load_json_mapping(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def coerce_date_string(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()

    text = normalize_text(value)
    if not text:
        return ""

    for parser in (
        date.fromisoformat,
        lambda raw: datetime.strptime(raw, "%Y-%m-%d").date(),
        lambda raw: datetime.strptime(raw, "%B %d, %Y").date(),
        lambda raw: datetime.strptime(raw, "%b %d, %Y").date(),
    ):
        try:
            return parser(text).isoformat()
        except ValueError:
            continue

    return text


def compute_days_since_applied(application_date: str) -> str:
    if not application_date:
        return ""
    try:
        applied = date.fromisoformat(application_date)
    except ValueError:
        return ""
    return str((date.today() - applied).days)


def build_tracker_record(context: dict[str, Any], resume_used: str, cover_letter_file: str) -> dict[str, str]:
    today_iso = date.today().isoformat()
    application_date = coerce_date_string(context.get("application_date"))
    record = {
        "date_added": coerce_date_string(context.get("date_added")) or today_iso,
        "company": normalize_text(context.get("company")),
        "role": normalize_text(context.get("role")),
        "location": normalize_text(context.get("location")),
        "work_type": normalize_text(context.get("work_type")),
        "source": normalize_text(context.get("source")) or "Pasted JD",
        "job_link": normalize_text(context.get("job_link")),
        "job_description": normalize_text(context.get("job_description")),
        "priority": normalize_text(context.get("priority")) or "Medium",
        "match_notes": normalize_text(context.get("match_notes")),
        "resume_used": normalize_text(resume_used),
        "cover_letter_file": normalize_text(cover_letter_file),
        "cover_letter_status": normalize_text(context.get("cover_letter_status")) or "Drafted",
        "application_date": application_date,
        "current_status": normalize_text(context.get("current_status")) or "Cover Letter Drafted",
        "last_status_update": coerce_date_string(context.get("last_status_update")) or today_iso,
        "response_date": coerce_date_string(context.get("response_date")),
        "response_outcome": normalize_text(context.get("response_outcome")),
        "follow_up_date": coerce_date_string(context.get("follow_up_date")),
        "interview_date": coerce_date_string(context.get("interview_date")),
        "contact_name": normalize_text(context.get("contact_name")),
        "contact_email": normalize_text(context.get("contact_email")),
        "days_since_applied": compute_days_since_applied(application_date),
        "next_action": normalize_text(context.get("next_action")),
        "notes": normalize_text(context.get("notes")),
    }

    if not record["company"]:
        raise ValueError("Tracker update requires 'company' in the job context.")
    if not record["role"]:
        raise ValueError("Tracker update requires 'role' in the job context.")

    return record


def load_existing_rows(tracker_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not tracker_path.exists():
        return TRACKER_HEADERS[:], []

    with tracker_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        if not headers:
            return TRACKER_HEADERS[:], []
        missing_headers = REQUIRED_HEADERS.difference(headers)
        if missing_headers:
            missing = ", ".join(sorted(missing_headers))
            raise ValueError(f"Tracker file is missing required columns: {missing}")
        rows = [{header: normalize_text(row.get(header, "")) for header in headers} for row in reader]
        return headers, rows


def update_tracker_csv(tracker_path: Path, output_path: Path, tracker_record: dict[str, str]) -> dict[str, Any]:
    headers, rows = load_existing_rows(tracker_path)

    for header in TRACKER_HEADERS:
        if header not in headers:
            headers.append(header)

    row_map = {header: "" for header in headers}
    for context_key, header in CONTEXT_TO_HEADER.items():
        row_map[header] = tracker_record.get(context_key, "")

    rows.append(row_map)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    return {
        "tracker_path": str(output_path),
        "headers": headers,
        "application_row": len(rows) + 1,
        "row_count": len(rows),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Append an application record to the CSV tracker text file.")
    parser.add_argument("tracker", help="Path to the existing Application Tracker text file.")
    parser.add_argument("job_context", help="Path to a JSON job context file.")
    parser.add_argument("--resume-path", required=True, help="Resume PDF path to store in the tracker.")
    parser.add_argument("--cover-letter-path", required=True, help="Cover letter PDF path to store in the tracker.")
    parser.add_argument(
        "--output-tracker",
        help="Output tracker path. Defaults to the input tracker name with .updated.txt.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    tracker_path = Path(args.tracker).expanduser().resolve()
    job_context_path = Path(args.job_context).expanduser().resolve()
    if args.output_tracker:
        output_path = Path(args.output_tracker).expanduser().resolve()
    else:
        output_path = tracker_path.with_name(f"{tracker_path.stem}.updated{tracker_path.suffix}")

    context = load_json_mapping(job_context_path)
    record = build_tracker_record(context, args.resume_path, args.cover_letter_path)
    result = update_tracker_csv(tracker_path, output_path, record)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
