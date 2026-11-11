#!/usr/bin/env bash
# Create paper size-sweep prefixes from the existing fixed nested subsets.
# No resampling, and no overwrite of existing data.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
DATA_DIR=${DATA_DIR:-"$ROOT/data/historical/reproduction"}
SUBSETS=${SUBSETS:-"$DATA_DIR/subsets"}
[[ -d "$SUBSETS" ]] || { echo "Missing subset directory: $SUBSETS" >&2; exit 2; }
jobs=()
for dataset in geolife tdrive porto; do
  src="$SUBSETS/${dataset}_1m_xy.txt"
  for size in 100 200 400 600 800; do
    jobs+=("$src|$SUBSETS/${dataset}_${size}k_xy.txt|$((size * 1000))")
  done
done
for dataset in geolife tdrive; do
  jobs+=("$SUBSETS/${dataset}_3m_xy.txt|$SUBSETS/${dataset}_2m_xy.txt|2000000")
done
for job in "${jobs[@]}"; do
  IFS="|" read -r src dst count <<< "$job"
  [[ -f "$src" ]] || { echo "Missing required source: $src" >&2; exit 2; }
  [[ ! -e "$dst" ]] || { echo "Refusing to overwrite: $dst" >&2; exit 2; }
  actual=$(wc -l < "$src")
  (( actual >= count )) || { echo "Source too short: $src ($actual < $count)" >&2; exit 2; }
done
for job in "${jobs[@]}"; do
  IFS="|" read -r src dst count <<< "$job"
  temp=$(mktemp "${dst}.part.XXXXXX")
  if ! head -n "$count" "$src" > "$temp"; then rm -f "$temp"; exit 2; fi
  actual=$(wc -l < "$temp")
  if (( actual != count )); then rm -f "$temp"; echo "Bad prefix count: $dst" >&2; exit 2; fi
  if ! ln "$temp" "$dst"; then rm -f "$temp"; echo "Refusing to overwrite: $dst" >&2; exit 2; fi
  rm -f "$temp"
  echo "Created $dst ($count points)"
done
