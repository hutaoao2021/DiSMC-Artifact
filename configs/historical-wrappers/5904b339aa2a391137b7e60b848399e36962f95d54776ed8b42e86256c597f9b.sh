#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 7 ]]; then
  echo "usage: $0 PROFILE INPUT OUTPUT PARTITIONS RADIUS DENSITY CELL_FACTOR [-- extra spark-submit options]" >&2
  exit 2
fi

PROFILE=$1
INPUT=$2
OUTPUT=$3
PARTITIONS=$4
RADIUS=$5
DENSITY=$6
CELL_FACTOR=$7
shift 7

QUERY_ARGS=()
if [[ ${QUERY_X+x} != ${QUERY_Y+x} ]]; then
  echo "QUERY_X and QUERY_Y must both be set" >&2
  exit 2
fi
if [[ ${QUERY_X+x} ]]; then
  [[ -n "$QUERY_X" && -n "$QUERY_Y" ]] || { echo "query coordinates must not be empty" >&2; exit 2; }
  QUERY_ARGS=("$QUERY_X" "$QUERY_Y")
fi

case "$PROFILE" in
  single_esmc|z_d0|hilbert_d0|grid_d0|full|hilbert_full|hilbert_wo_planner|hilbert_wo_engine|wo_planner|wo_engine|wo_dependency_partition|wo_sharing|wo_refinement|wo_new_bounds|wo_prepared_reuse) ;;
  *) echo "unknown profile: $PROFILE" >&2; exit 2 ;;
esac

if [[ -e "$OUTPUT" || -e "$OUTPUT.manifest" || -e "$OUTPUT.json" || -e "$OUTPUT.local_tasks.csv" || -e "$OUTPUT.spark_tasks.csv" || -e "$OUTPUT.observation.json" ]]; then
  echo "output already exists: $OUTPUT" >&2
  exit 2
fi

EXTRA=()
if [[ $# -gt 0 ]]; then
  [[ $1 == "--" ]] || { echo "extra options must follow --" >&2; exit 2; }
  shift
  EXTRA=("$@")
fi

ROOT=$(cd "$(dirname "$0")/.." && pwd)
SPARK_HOME=${SPARK_HOME:-${SPARK_HOME}}
SPARK_MASTER=${SPARK_MASTER:-spark://${SPARK_MASTER_HOST}:7077}
JAR="$ROOT/target/dismc-unified-1.0.0.jar"

[[ -f "$JAR" ]] || "$ROOT/build.sh" >/dev/null

if [[ "$PROFILE" == "single_esmc" ]]; then
  SINGLE_JAVA_OPTIONS=()
  while [[ ${#EXTRA[@]} -gt 0 ]]; do
    [[ ${#EXTRA[@]} -ge 2 && ${EXTRA[0]} == "--conf" && ${EXTRA[1]} =~ ^spark\.[A-Za-z0-9_.-]+= ]] || {
      echo "single_esmc accepts only --conf spark.KEY=VALUE options" >&2
      exit 2
    }
    SINGLE_JAVA_OPTIONS+=("-D${EXTRA[1]}")
    EXTRA=("${EXTRA[@]:2}")
  done
  java "${SINGLE_JAVA_OPTIONS[@]}" -cp "$JAR:$SPARK_HOME/jars/*" com.DistributedSMC \
    "$PROFILE" "$INPUT" "$OUTPUT" "$PARTITIONS" "$RADIUS" "$DENSITY" "$CELL_FACTOR" "${QUERY_ARGS[@]}"
else
  "$SPARK_HOME/bin/spark-submit" \
    --class com.DistributedSMC \
    --master "$SPARK_MASTER" \
    --deploy-mode client \
    --total-executor-cores "${TOTAL_EXECUTOR_CORES:-40}" \
    --executor-memory "${EXECUTOR_MEMORY:-4G}" \
    --executor-cores "${EXECUTOR_CORES:-4}" \
    --driver-memory "${DRIVER_MEMORY:-4G}" \
    --conf spark.eventLog.enabled=false \
    --conf spark.task.maxDirectResultSize=1m \
    "${EXTRA[@]}" \
    "$JAR" "$PROFILE" "$INPUT" "$OUTPUT" "$PARTITIONS" "$RADIUS" "$DENSITY" "$CELL_FACTOR" "${QUERY_ARGS[@]}"
fi

{
  echo "method_profile=$PROFILE"
  echo "input=$INPUT"
  echo "output=$OUTPUT"
  echo "partitions=$PARTITIONS"
  echo "radius=$RADIUS"
  echo "density=$DENSITY"
  echo "cell_factor=$CELL_FACTOR"
  echo "query_x=${QUERY_X:-15}"
  echo "query_y=${QUERY_Y:-15}"
  echo "spark_master=$SPARK_MASTER"
  echo "total_executor_cores=${TOTAL_EXECUTOR_CORES:-40}"
  echo "executor_cores=${EXECUTOR_CORES:-4}"
  echo "executor_memory=${EXECUTOR_MEMORY:-4G}"
  echo "driver_memory=${DRIVER_MEMORY:-4G}"
  echo "jar_sha256=$(sha256sum "$JAR" | awk '{print $1}')"
  grep -E '^(method_composition|routing_strategy|partitioning_strategy|local_engine_class|member_materialization_enabled|result_fingerprint_scope|original_points|assigned_points|clone_points|replication_multiplier|shard_tasks|m4_physical_tasks|result_fingerprint|skyline_count|end_to_end_time_s)[:=]' "$OUTPUT" || true
} > "$OUTPUT.manifest"
