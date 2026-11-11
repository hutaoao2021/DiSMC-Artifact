#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
WORK_ROOT=${WORK_ROOT:-"$ROOT/reproduction"}
python3 "$ROOT/scripts/create_subsets.py" --root "$WORK_ROOT" "$@"
