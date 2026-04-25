#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/codex-application-package-smoke.XXXXXX")"
TEMP_ROOT="$OUT_DIR/GenFiles/tmp"
TRACKER_COPY="$OUT_DIR/Application Tracker.txt"
JOB_CONTEXT="$TEMP_ROOT/job_context.json"
MATCH_MATRIX="$TEMP_ROOT/match_matrix.json"
RESUME_XML="$TEMP_ROOT/input.xml"
COVER_TXT="$TEMP_ROOT/input.txt"
MANIFEST_OUT="$OUT_DIR/manifest.json"
RESUME_OUT="$OUT_DIR/ExampleRobotics-Resume.pdf"
COVER_OUT="$OUT_DIR/ExampleRobotics-Cover-Letter.pdf"

mkdir -p "$TEMP_ROOT"
cp "$ROOT/examples/example_job_context.json" "$JOB_CONTEXT"
cp "$ROOT/examples/example_match_matrix.json" "$MATCH_MATRIX"
cp "$ROOT/examples/example_resume.xml" "$RESUME_XML"
cp "$ROOT/examples/example_cover_letter.txt" "$COVER_TXT"
cp "$ROOT/data/Application Tracker.txt" "$TRACKER_COPY"

"$ROOT/bin/run_application_package.sh" \
  "$JOB_CONTEXT" \
  "$RESUME_XML" \
  "$COVER_TXT" \
  --tracker "$TRACKER_COPY" \
  --resume-output "$RESUME_OUT" \
  --cover-letter-output "$COVER_OUT" \
  --manifest-output "$MANIFEST_OUT" \
  --temp-root "$OUT_DIR/GenFiles/tmp"

test -f "$RESUME_OUT"
test -f "$COVER_OUT"
test -f "$MANIFEST_OUT"
test -f "$TEMP_ROOT/generation_report.md"
test ! -f "$RESUME_XML"
test ! -f "$COVER_TXT"

"$ROOT/bin/validate_application_package.sh" "$MANIFEST_OUT"

python3 - <<PY
import csv
import json
from pathlib import Path

manifest = json.loads(Path("$MANIFEST_OUT").read_text(encoding="utf-8"))
assert manifest["tracker_updated"] is True

with Path("$TRACKER_COPY").open("r", encoding="utf-8", newline="") as handle:
    rows = list(csv.DictReader(handle))

assert any(row["Company"] == "Example Robotics" and row["Role"] == "Software Engineering Intern" for row in rows)
assert any(str(row["Resume Used"]).endswith("ExampleRobotics-Resume.pdf") for row in rows)
assert any(str(row["Cover Letter File"]).endswith("ExampleRobotics-Cover-Letter.pdf") for row in rows)
PY

echo "Application package smoke test passed."
echo "Manifest: $MANIFEST_OUT"
echo "Resume:   $RESUME_OUT"
echo "Cover:    $COVER_OUT"
