#!/usr/bin/env bash
# One-command local MVP: install deps + pytest + 10s contest demo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PY=""
for candidate in python3.13 python3.12 python3.11 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PY="$candidate"
    break
  fi
done
if [[ -z "$PY" ]]; then
  echo "No python3 found" >&2
  exit 1
fi
echo "Using $PY ($($PY --version))"
"$PY" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements.txt
python -m pip install -q -e .

echo "=== pytest ==="
python -m pytest

echo ""
echo "=== 10s contest demo ==="
python -m scrapwood demo --ascii --env-steps 3

echo ""
echo "=== baseline freeze ==="
python -m scrapwood check-baseline

echo ""
echo "OK — scrapwood-tetris local MVP green."
