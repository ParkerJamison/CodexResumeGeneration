#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${TMPDIR:-/tmp}/codex-cover-letter-smoke"
PDF_OUT="$OUT_DIR/example_cover_letter.pdf"
HTML_OUT="$OUT_DIR/example_cover_letter.html"

mkdir -p "$OUT_DIR"

"$ROOT/bin/run_cover_letter.sh" "$ROOT/examples/example_cover_letter.txt" "$PDF_OUT" --html-output "$HTML_OUT"

test -f "$PDF_OUT"
test -f "$HTML_OUT"

"$ROOT/bin/validate_cover_letter.sh" "$ROOT/examples/example_cover_letter.txt" "$HTML_OUT"

echo "Cover letter smoke test passed."
echo "HTML: $HTML_OUT"
echo "PDF:  $PDF_OUT"
