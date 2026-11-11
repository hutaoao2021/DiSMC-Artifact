#!/usr/bin/env bash
set -euo pipefail
[[ $# -eq 7 ]] || { echo "Usage: $0 INPUT OUTPUT PARTITIONS RADIUS DENSITY QUERY_X QUERY_Y" >&2; exit 2; }
ROOT=$(cd "$(dirname "$0")/.." && pwd)
SRC=${SOURCE_DIR:-"$ROOT/DiSMC-source"}
: "${SPARK_HOME:?Set SPARK_HOME to Spark 3.2.0}"
: "${SPARK_MASTER:?Set SPARK_MASTER to Spark master}"
JAR="$SRC/target/dismc-unified-1.0.0.jar"
[[ -f "$JAR" ]] || bash "$SRC/build.sh"
WORK="$ROOT/configs/target"
BRIDGE="$WORK/spatial-operator-bridge.jar"
SOURCE="$ROOT/configs/tools/ArtifactSpatialOperatorMain.java"
if [[ ! -f "$BRIDGE" || "$SOURCE" -nt "$BRIDGE" || "$JAR" -nt "$BRIDGE" ]]; then
  mkdir -p "$WORK/classes"
  javac -encoding UTF-8 -source 8 -target 8 -cp "$JAR:$SPARK_HOME/jars/*" -d "$WORK/classes" "$SOURCE"
  jar cf "$BRIDGE" -C "$WORK/classes" com/ArtifactSpatialOperatorMain.class
fi
INPUT=$1 OUTPUT=$2
[[ ! -e "$OUTPUT" && ! -e "$OUTPUT.members" ]] || { echo "Refusing to overwrite: $OUTPUT" >&2; exit 2; }
"$SPARK_HOME/bin/spark-submit" \
  --class com.ArtifactSpatialOperatorMain --master "$SPARK_MASTER" --deploy-mode client \
  --total-executor-cores "${TOTAL_EXECUTOR_CORES:-40}" \
  --executor-memory "${EXECUTOR_MEMORY:-4G}" --executor-cores "${EXECUTOR_CORES:-4}" \
  --driver-memory "${DRIVER_MEMORY:-8G}" --jars "$JAR" \
  --conf spark.locality.wait=0s --conf "spark.driver.extraClassPath=$JAR" \
  "$BRIDGE" "$@"
{
 echo "method_profile=assembled_spatial_operator"
 echo "input=$INPUT"
 echo "output=$OUTPUT"
 echo "total_executor_cores=${TOTAL_EXECUTOR_CORES:-40}"
 echo "driver_memory=${DRIVER_MEMORY:-8G}"
 echo "jar_sha256=$(sha256sum "$JAR" | awk '{print $1}')"
 echo "bridge_sha256=$(sha256sum "$BRIDGE" | awk '{print $1}')"
} > "$OUTPUT.manifest"
