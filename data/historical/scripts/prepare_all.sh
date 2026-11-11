#!/usr/bin/env bash
# Prepare the three trajectory datasets without overwriting historical metadata.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
WORK_ROOT=${WORK_ROOT:-"$ROOT/reproduction"}
SORT_MEMORY=${SORT_MEMORY:-4G}
SORT_PARALLELISM=${SORT_PARALLELISM:-4}
GEOLIFE_INPUT=${GEOLIFE_INPUT:-"$ROOT/raw/Geolife Trajectories 1.3.zip"}
TDRIVE_INPUT=${TDRIVE_INPUT:-"$ROOT/raw/tdrive/extracted/release/taxi_log_2008_by_id"}
PORTO_INPUT=${PORTO_INPUT:-"$ROOT/raw/porto/extracted/train.csv"}
GEONAMES_INPUT=${GEONAMES_INPUT:-"$ROOT/raw/geonames/extracted/allCountries.txt"}
INCLUDE_GEONAMES=${INCLUDE_GEONAMES:-0}
if [[ "${1:-}" == --help || "${1:-}" == -h ]]; then
  cat <<'HELP'
Prepare GeoLife, TDrive and Porto using the historical parser.
Provide GEOLIFE_INPUT (ZIP), TDRIVE_INPUT (directory), PORTO_INPUT (train.csv).
WORK_ROOT defaults to data/historical/reproduction.
Optional: INCLUDE_GEONAMES=1 also processes the legacy GeoNames data.
Outputs: WORK_ROOT/prepared/*_xy.txt, WORK_ROOT/metadata/*_stats.json.
Existing files are never overwritten.
HELP
  exit 0
fi
if [[ $# -ne 0 ]]; then echo "Unknown argument: $1 (use --help)" >&2; exit 2; fi
DATASETS=(geolife tdrive porto)
INPUTS=("$GEOLIFE_INPUT" "$TDRIVE_INPUT" "$PORTO_INPUT")
if [[ "$INCLUDE_GEONAMES" == 1 ]]; then
  DATASETS+=(geonames)
  INPUTS+=("$GEONAMES_INPUT")
elif [[ "$INCLUDE_GEONAMES" != 0 ]]; then
  echo "INCLUDE_GEONAMES must be 0 or 1" >&2
  exit 2
fi
# Check everything before starting expensive conversions.
for i in "${!DATASETS[@]}"; do
  dataset=${DATASETS[$i]}
  input=${INPUTS[$i]}
  [[ -e "$input" ]] || { echo "Missing $dataset raw input: $input" >&2; exit 2; }
  for output in "$WORK_ROOT/prepared/${dataset}_xy.txt" "$WORK_ROOT/metadata/${dataset}_stats.json"; do
    [[ ! -e "$output" ]] || { echo "Refusing to overwrite: $output" >&2; exit 2; }
  done
done
for i in "${!DATASETS[@]}"; do
  dataset=${DATASETS[$i]}
  input=${INPUTS[$i]}
  echo "Preparing $dataset from $input" >&2
  python3 "$ROOT/scripts/prepare_dataset.py" \
    --dataset "$dataset" \
    --input "$input" \
    --output "$WORK_ROOT/prepared/${dataset}_xy.txt" \
    --stats "$WORK_ROOT/metadata/${dataset}_stats.json" \
    --temp-root "$WORK_ROOT/prepared/tmp" \
    --sort-memory "$SORT_MEMORY" \
    --sort-parallelism "$SORT_PARALLELISM"
done
