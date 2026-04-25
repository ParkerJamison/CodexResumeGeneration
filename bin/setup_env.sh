#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$ROOT/.venv"
RECREATE=0

if [[ "${1:-}" == "--recreate" ]]; then
  RECREATE=1
fi

choose_python() {
  local candidate path version major minor
  for candidate in /opt/homebrew/bin/python3 /usr/local/bin/python3 "$(command -v python3 2>/dev/null || true)"; do
    if [[ -z "$candidate" ]]; then
      continue
    fi

    if [[ "$candidate" != /* ]]; then
      path="$(command -v "$candidate" 2>/dev/null || true)"
    else
      path="$candidate"
    fi

    if [[ ! -x "$path" ]]; then
      continue
    fi

    if [[ "$path" == *anaconda* || "$path" == *conda* ]]; then
      continue
    fi

    version="$("$path" - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)"
    major="${version%%.*}"
    minor="${version##*.}"
    if (( major > 3 || (major == 3 && minor >= 10) )); then
      printf '%s\n' "$path"
      return 0
    fi
  done

  echo "Could not find a non-Conda Python 3.10+ interpreter." >&2
  echo "Install Homebrew Python first, for example:" >&2
  echo "  brew install python" >&2
  return 1
}

bootstrap_python="$(choose_python)"

if [[ -e "$VENV_DIR/bin/python3" ]]; then
  existing_target="$(python3 - <<PY
from pathlib import Path
print(Path("$VENV_DIR/bin/python3").resolve())
PY
)"
  if [[ "$RECREATE" -eq 1 || "$existing_target" == *anaconda* || "$existing_target" == *conda* ]]; then
    rm -rf "$VENV_DIR"
  fi
fi

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  "$bootstrap_python" -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r "$ROOT/requirements.txt"

mkdir -p "$ROOT/.runtime-cache"

cat <<EOF
Environment ready.

Python bootstrap interpreter:
  $bootstrap_python

Virtual environment:
  $VENV_DIR

Next commands:
  bin/smoke_test_application_package.sh
  bin/run_resume.sh examples/example_resume.xml examples/output/output.pdf --html-output examples/output/output.html
  bin/smoke_test_resume.sh
EOF
