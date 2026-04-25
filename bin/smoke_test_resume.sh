#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${TMPDIR:-/tmp}/codex-resume-smoke"
PDF_OUT="$OUT_DIR/example_resume.pdf"
HTML_OUT="$OUT_DIR/example_resume.html"

mkdir -p "$OUT_DIR"

"$ROOT/bin/run_resume.sh" "$ROOT/examples/example_resume.xml" "$PDF_OUT" --html-output "$HTML_OUT"

test -f "$PDF_OUT"
test -f "$HTML_OUT"

"$ROOT/bin/validate_resume.sh" "$ROOT/examples/example_resume.xml"

echo "Resume smoke test passed."
echo "HTML: $HTML_OUT"
echo "PDF:  $PDF_OUT"
