#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
SORT_MEMORY=${SORT_MEMORY:-4G}
SORT_PARALLELISM=${SORT_PARALLELISM:-4}

prepare() {
  local dataset=$1
  local input=$2
  python3 "$ROOT/scripts/prepare_dataset.py" \
    --dataset "$dataset" \
    --input "$input" \
    --output "$ROOT/prepared/${dataset}_xy.txt" \
    --stats "$ROOT/metadata/${dataset}_stats.json" \
    --temp-root "$ROOT/prepared/tmp" \
    --sort-memory "$SORT_MEMORY" \
    --sort-parallelism "$SORT_PARALLELISM"
}

prepare geonames "$ROOT/raw/geonames/extracted/allCountries.txt"
prepare tdrive "$ROOT/raw/tdrive/extracted/release/taxi_log_2008_by_id"
prepare porto "$ROOT/raw/porto/extracted/train.csv"
