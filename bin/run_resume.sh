#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PY="$ROOT/.venv/bin/python"
GENERATOR="$ROOT/src/generateResume.py"
CACHE_ROOT="${XDG_CACHE_HOME:-$ROOT/.runtime-cache}"

if [[ ! -x "$VENV_PY" ]]; then
  echo "Missing virtual environment Python: $VENV_PY" >&2
  echo "Run bin/setup_env.sh first." >&2
  exit 1
fi

BASE_PY="$("$VENV_PY" - <<'PY'
import sys
print(getattr(sys, "_base_executable", sys.executable))
PY
)"

if [[ "$BASE_PY" == *anaconda* || "$BASE_PY" == *conda* ]]; then
  echo "The current .venv is based on Anaconda: $BASE_PY" >&2
  echo "Rebuild it with bin/setup_env.sh --recreate before running the generator." >&2
  exit 1
fi

mkdir -p "$CACHE_ROOT" "$CACHE_ROOT/fontconfig"
export XDG_CACHE_HOME="$CACHE_ROOT"

if [[ -d /opt/homebrew/lib ]]; then
  export DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib:/opt/homebrew/opt/libffi/lib:${DYLD_FALLBACK_LIBRARY_PATH:-}"
fi

if [[ -f /opt/homebrew/etc/fonts/fonts.conf ]]; then
  export FONTCONFIG_PATH="${FONTCONFIG_PATH:-/opt/homebrew/etc/fonts}"
  export FONTCONFIG_FILE="${FONTCONFIG_FILE:-/opt/homebrew/etc/fonts/fonts.conf}"
fi

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
exec "$VENV_PY" "$GENERATOR" "$@"
