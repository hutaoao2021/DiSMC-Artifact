#!/usr/bin/env bash
# Actual Spark 3.2.0 local execution: one capture, four R/W replays, one greedy replay.
set -euo pipefail
: "${ARTIFACT_CLASSPATH:?Set source jar and Spark 3.2.0 classpath}"
: "${ARTIFACT_SOURCE_DIR:?Set extracted source directory}"
: "${ARTIFACT_RESULTS_DIR:?Set a fresh results directory}"
[[ ! -e "$ARTIFACT_RESULTS_DIR" ]] || { echo "Existing output: $ARTIFACT_RESULTS_DIR" >&2; exit 2; }
mkdir -p "$ARTIFACT_RESULTS_DIR"
INPUT="$ARTIFACT_SOURCE_DIR/examples/five_points.txt"
[[ -s "$INPUT" ]] || { echo "Missing fixture $INPUT" >&2; exit 2; }
HASH=$(sha256sum "$INPUT" | cut -d ' ' -f1)
export SPARK_LOCAL_IP=127.0.0.1
common=(
 -Dspark.master=local[2] -Dspark.ui.enabled=false -Dspark.driver.bindAddress=127.0.0.1
 -Dspark.driver.host=127.0.0.1 -Dspark.locality.wait=0s
 -Dspark.sql.shuffle.partitions=2
 -Dspark.skyline.experiment.enabled=true
 -Dspark.skyline.experiment.partitionStrategy=workload
 -Dspark.skyline.experiment.organization=independent_owner
 -Dspark.skyline.experiment.shardStrategy=none
 -Dspark.skyline.experiment.transportEncoding=deduplicated_union
 -Dspark.skyline.experiment.ownerThreads=1
 -Dspark.skyline.experiment.maxPieces=4
 -Dspark.skyline.experiment.preparedMode=private_owner_index
 -Dspark.skyline.experiment.projectionCache=on
 -Dspark.skyline.experiment.microPartition=true
 -Dspark.skyline.experiment.microPartitionMode=dependency
 -Dspark.skyline.experiment.microCostModel=cell_quadratic
 -Dspark.skyline.experiment.microTaskOrder=cost
 -Dspark.skyline.experiment.microPlannerPolicy=sampled_peak
 -Dspark.skyline.experiment.microCostSignal=sampled
 -Dspark.skyline.experiment.microRefinedCounting=true
 -Dspark.skyline.experiment.microCountingCellMultiplier=2.0
 -Dspark.skyline.experiment.geometricBounds=true
 -Dspark.skyline.experiment.microDenseBoundaryCounting=true
 -Dspark.skyline.microAdaptiveAcquisition=false
 -Dspark.skyline.microRefreshCandidates=false
 -Dspark.skyline.microProbeOwnerLimit=8
 -Dspark.skyline.microProbeCoverageAnchors=0
 -Dspark.skyline.microAcquisitionCoverageFirst=true
 -Dspark.skyline.microAcquisitionOwnerLimit=200
 -Dspark.skyline.microAuditAllCandidates=true
 -Dspark.skyline.microSpatialCostCalibration=true
 -Dspark.skyline.microLaneProbeRefinement=false
 -Dspark.skyline.microLaneProbeMaxOwners=4
 -Dspark.skyline.microLaneParentReplay=false
 -Dspark.skyline.microPlanAuditOnly=false
 -Dspark.skyline.shardReadBudget=0.05
 -Dspark.skyline.budgetDiagnostic=true
 -Dspark.skyline.stableInputIds=true
 -Dspark.skyline.materializeMembers=true
 -Dspark.skyline.memberOutputMode=partitioned
 -Dspark.skyline.cacheMemberText=true
 "-Dspark.skyline.inputSha256=$HASH"
)
query() {
  local label=$1 action=$2 reuse=$3 frontier=$4 selector=$5
  local output="$ARTIFACT_RESULTS_DIR/$label"
  local -a extra=(
    "-Dspark.skyline.experiment.outputPrefix=$output"
    "-Dspark.skyline.experiment.microCompletionReuse=$reuse"
    "-Dspark.skyline.experiment.microProbeFrontier=$frontier"
    "-Dspark.skyline.microSelector=$selector"
  )
  if [[ "$action" == capture ]]; then
    extra+=(-Dspark.skyline.microFrozenStateExport=true)
  else
    extra+=("-Dspark.skyline.microFrozenStateLoad=$FROZEN_FILE"
            "-Dspark.skyline.microFrozenStateSha256=$FROZEN_SHA")
  fi
  echo "Running actual Spark local[2]: $label" >&2
  java -Xmx2g "${common[@]}" "${extra[@]}" \
    -cp "$ARTIFACT_CLASSPATH" com.DistributedSMC \
    hilbert_full "file://$INPUT" "$output" 2 1 2 1 0 0
  [[ -s "$output" && -s "$output.micro_tasks.csv" && -d "$output.members" ]] || {
    echo "Result/task/member output missing: $output" >&2; exit 1;
  }
}
query capture capture true true joint_peak
FROZEN_FILE="$ARTIFACT_RESULTS_DIR/capture.frozen_calibration.bin"
[[ -s "$FROZEN_FILE" ]] || { echo "Frozen capture not written" >&2; exit 1; }
FROZEN_SHA=$(sha256sum "$FROZEN_FILE" | cut -d ' ' -f1)
for reuse in false true; do
  for frontier in false true; do
    query "R${reuse}_W${frontier}" replay "$reuse" "$frontier" joint_peak
  done
done
query greedy replay true true work_greedy
python3 - "$ARTIFACT_RESULTS_DIR" <<'PY'
from pathlib import Path
import json
import sys
root=Path(sys.argv[1])
names=["capture","Rfalse_Wfalse","Rfalse_Wtrue",
       "Rtrue_Wfalse","Rtrue_Wtrue","greedy"]
def find(obj, key):
    if isinstance(obj, dict):
        if key in obj: return obj[key]
        for value in obj.values():
            found=find(value,key)
            if found is not None: return found
    if isinstance(obj,list):
        for value in obj:
            found=find(value,key)
            if found is not None: return found
    return None
def exported(name):
    folder=root/(name+".members")
    parts=list(sorted(folder.glob("part-*")))
    assert parts, "No Spark member part files: "+name
    rows=[]
    for part in parts: rows.extend(part.read_text().splitlines())
    assert rows, "No exported members: "+name
    return sorted(rows)
reference=None
for name in names:
    assert (root/name).stat().st_size > 0, name
    assert (root/(name+".micro_tasks.csv")).stat().st_size > 0, name
    assert (root/(name+".members")).is_dir(), name
    diagnostic=root/(name+".json")
    assert diagnostic.is_file(), name
    details=json.loads(diagnostic.read_text())
    if name.startswith("R"):
        expected_reuse,expected_frontier=name.split("_")
        expected_reuse=expected_reuse[1:]=="true"
        expected_frontier=expected_frontier[1:]=="true"
        assert find(details,"micro_completion_reuse")==expected_reuse, name+" R misconfigured"
        assert find(details,"micro_probe_frontier")==expected_frontier, name+" W misconfigured"
    rows=exported(name)
    if reference is None: reference=rows
    assert rows==reference, "Formal result member mismatch: "+name
print("PASS: 1 capture + 4 R/W + 1 greedy actual Spark local runs")
print("PASS: all six complete member exports match; recorded R/W flags checked")
PY
