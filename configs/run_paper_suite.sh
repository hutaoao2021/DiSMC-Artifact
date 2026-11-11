#!/usr/bin/env bash
# DiSMC paper parameter runner. Existing outputs are never overwritten.
set -euo pipefail
FIG=${1:-}; ROOT=$(cd "$(dirname "$0")/.." && pwd)
SRC=${SOURCE_DIR:-"$ROOT/DiSMC-source"}
DATA_DIR=${DATA_DIR:-"$ROOT/data/historical"}
OUT_DIR=${OUT_DIR:-"$ROOT/results/paper-rerun"}
TRIALS=${TRIALS:-1}; DRY_RUN=${DRY_RUN:-0}
# Heavy complete-query paper controls use an 8 GiB driver.
export DRIVER_MEMORY=${DRIVER_MEMORY:-8G}
if [[ -z "$FIG" || "$FIG" == "--help" ]]; then
  echo "Usage: DATA_DIR=/data OUT_DIR=/results TRIALS=3 bash configs/run_paper_suite.sh {fig4|fig5|fig6|fig7|fig8|fig9|table1|fig10|fig11a|fig11b|fig12|fig13|fig14}"
  echo "Use DRY_RUN=1 to print commands. Source ZIP must be extracted and built."
  exit 0
fi
[[ "$TRIALS" =~ ^[1-9][0-9]*$ ]] || { echo "TRIALS must be a positive integer" >&2; exit 2; }
[[ "$DRY_RUN" == 1 || -f "$SRC/scripts/run_profile.sh" ]] || { echo "Extract artifact/DiSMC-source-release.zip first" >&2; exit 2; }
# The 1M position-control median is a runnable example for qM, not a verified
# numeric match to the 2M/3M qM of other figures. Override when known.
MEDIUM_GEOLIFE_X=${MEDIUM_GEOLIFE_X:-122287.250}
MEDIUM_GEOLIFE_Y=${MEDIUM_GEOLIFE_Y:-105282.863}
MEDIUM_TDRIVE_X=${MEDIUM_TDRIVE_X:-106516.154}
MEDIUM_TDRIVE_Y=${MEDIUM_TDRIVE_Y:-134723.013}
run_one() {
  local figure=$1 ds=$2 size=$3 label=$4 x=$5 y=$6 radius=$7 method=$8
  local input output profile mode budget signal planner selector frontier lane refresh reuse
  if [[ "$size" == full ]]; then input="$DATA_DIR/${ds}_xy.txt"
  else input="$DATA_DIR/${ds}_${size}_xy.txt"; fi
  # Also accept the fresh preparation workspace without copying GB-scale files.
  if [[ ! -f "$input" ]]; then
    local candidate
    if [[ "$size" == full ]]; then candidate="$DATA_DIR/prepared/${ds}_xy.txt"
    else candidate="$DATA_DIR/subsets/${ds}_${size}_xy.txt"; fi
    [[ ! -f "$candidate" ]] || input="$candidate"
  fi
  output="$OUT_DIR/$figure/${ds}_${size}_${label}_${method}_trial${TRIAL}.txt"
  if [[ "$DRY_RUN" != 1 ]]; then
    [[ -f "$input" ]] || { echo "Missing input: $input" >&2; exit 2; }
    mkdir -p "$(dirname "$output")"
  fi
  profile=$method
  [[ "$method" == dismc || "$method" == static ]] && profile=hilbert_full
  if [[ "$method" == operator ]]; then
    local -a op=(bash "$ROOT/configs/run_spatial_operator.sh" "$input" "$output" 200 "$radius" 2 "$x" "$y")
    if [[ "$DRY_RUN" == 1 ]]; then
      printf 'QUERY_X=%q QUERY_Y=%q TOTAL_EXECUTOR_CORES=%q DRIVER_MEMORY=%q ' "$x" "$y" "${TOTAL_EXECUTOR_CORES:-40}" "$DRIVER_MEMORY"
      printf '%q ' "${op[@]}"; echo
    else
      "${op[@]}"
    fi
    return
  fi
  local -a cmd=(bash "$SRC/scripts/run_profile.sh" "$profile" "$input" "$output" 200 "$radius" 2 1)
  if [[ "$profile" == hilbert_full ]]; then
    mode=${MODE:-dependency}; budget=${BUDGET:-0.05}; signal=${SIGNAL:-sampled}
    if [[ "$method" == static ]]; then
      # Static-Greedy is not sampled_peak+work_greedy: it has no online probes.
      planner=peak; selector=work_greedy; frontier=false; lane=false; refresh=false; reuse=false
    else
      planner=sampled_peak; selector=${SELECTOR:-joint_peak}; frontier=${FRONTIER:-true}
      lane=${LANE:-true}; refresh=${REFRESH:-true}; reuse=${REUSE:-true}
    fi
    cmd+=(--
      --conf spark.skyline.experiment.enabled=true
      --conf spark.skyline.experiment.partitionStrategy=workload
      --conf spark.skyline.experiment.organization=independent_owner
      --conf spark.skyline.experiment.shardStrategy=none
      --conf spark.skyline.experiment.transportEncoding=deduplicated_union
      --conf spark.skyline.experiment.ownerThreads=1
      --conf spark.skyline.experiment.maxPieces=4
      --conf spark.skyline.experiment.preparedMode=private_owner_index
      --conf spark.skyline.experiment.projectionCache=on
      --conf spark.skyline.experiment.microPartition=true
      --conf "spark.skyline.experiment.microPartitionMode=$mode"
      --conf spark.skyline.experiment.microCostModel=cell_quadratic
      --conf spark.skyline.experiment.microTaskOrder=cost
      --conf "spark.skyline.experiment.microPlannerPolicy=$planner"
      --conf "spark.skyline.experiment.microCostSignal=$signal"
      --conf "spark.skyline.experiment.microCompletionReuse=$reuse"
      --conf spark.skyline.experiment.microRefinedCounting=true
      --conf spark.skyline.experiment.microCountingCellMultiplier=2.0
      --conf spark.skyline.experiment.geometricBounds=true
      --conf "spark.skyline.experiment.microProbeFrontier=$frontier"
      --conf spark.skyline.experiment.microDenseBoundaryCounting=true
      --conf "spark.skyline.microSelector=$selector"
      --conf "spark.skyline.microAdaptiveAcquisition=$refresh"
      --conf "spark.skyline.microRefreshCandidates=$refresh"
      --conf "spark.skyline.microProbeOwnerLimit=${PROBE_OWNER_LIMIT:-32}"
      --conf "spark.skyline.microProbeCoverageAnchors=${COVERAGE:-0}"
      --conf spark.skyline.microAcquisitionCoverageFirst=true
      --conf "spark.skyline.microAcquisitionOwnerLimit=${ACQUISITION_OWNER_LIMIT:-200}"
      --conf spark.skyline.microAuditAllCandidates=true
      --conf spark.skyline.microSpatialCostCalibration=true
      --conf "spark.skyline.microLaneProbeRefinement=$lane"
      --conf spark.skyline.microLaneProbeMaxAnchors=256
      --conf "spark.skyline.microLaneProbeMaxOwners=${LANE_OWNERS:-4}"
      --conf "spark.skyline.microLaneParentReplay=${PARENT_REPLAY:-true}"
      --conf spark.skyline.microLaneProbeMinimum=4
      --conf spark.skyline.microLaneProbeMaximum=8
      --conf spark.skyline.microDiagnosticMaxPieces=16
      --conf spark.skyline.microDiagnosticTargetAnchors=0
      --conf spark.skyline.microPlanAuditOnly=false
      --conf "spark.skyline.microCalibratePooledFrontier=$frontier"
      --conf spark.skyline.microLaneProbeCoverUnsplit=true
      --conf "spark.skyline.shardReadBudget=$budget"
      --conf spark.skyline.budgetDiagnostic=true
      --conf spark.skyline.stableInputIds=true
      --conf spark.skyline.materializeMembers=true
      --conf spark.skyline.memberOutputMode=partitioned
      --conf spark.skyline.cacheMemberText=true
      --conf spark.locality.wait=0s)
    # Replays use a single captured candidate/work/probe state, never new probes.
    if [[ -n "${FROZEN_ACTION:-}" ]]; then
      [[ -n "${FROZEN_INPUT_SHA:-}" ]] || { echo "Frozen execution needs source SHA-256" >&2; exit 2; }
      cmd+=(--conf "spark.skyline.inputSha256=$FROZEN_INPUT_SHA"
             --conf "spark.skyline.experiment.outputPrefix=$output")
      if [[ "$FROZEN_ACTION" == capture ]]; then
        cmd+=(--conf spark.skyline.microFrozenStateExport=true)
      elif [[ "$FROZEN_ACTION" == load ]]; then
        [[ -n "${FROZEN_STATE_PATH:-}" && -n "${FROZEN_STATE_SHA:-}" ]] || {
          echo "Frozen load requires state path and SHA-256" >&2; exit 2; }
        cmd+=(--conf "spark.skyline.microFrozenStateLoad=$FROZEN_STATE_PATH"
               --conf "spark.skyline.microFrozenStateSha256=$FROZEN_STATE_SHA")
      else
        echo "Invalid FROZEN_ACTION=$FROZEN_ACTION" >&2; exit 2
      fi
    fi
  elif [[ "$profile" != single_esmc ]]; then
    cmd+=(-- --conf spark.locality.wait=0s)
  fi
  if [[ "$DRY_RUN" == 1 ]]; then
    printf 'QUERY_X=%q QUERY_Y=%q TOTAL_EXECUTOR_CORES=%q DRIVER_MEMORY=%q ' "$x" "$y" "${TOTAL_EXECUTOR_CORES:-40}" "$DRIVER_MEMORY"
    printf '%q ' "${cmd[@]}"; echo
  elif [[ "$profile" == single_esmc ]]; then
    QUERY_X="$x" QUERY_Y="$y" JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:-} -Xmx4g" timeout 7200s "${cmd[@]}"
  else
    QUERY_X="$x" QUERY_Y="$y" "${cmd[@]}"
  fi
}

# Use the integrated frozen capture/load mechanism for controls that MUST
# share acquired alternatives, work observations, probe IDs and task inputs.
if [[ "$FIG" == fig11b || "$FIG" == fig13 ]]; then
  for ds in geolife tdrive; do
    if [[ "$FIG" == fig11b ]]; then
      size=2m; radius=40
      if [[ "$ds" == geolife ]]; then x=$MEDIUM_GEOLIFE_X; y=$MEDIUM_GEOLIFE_Y
      else x=$MEDIUM_TDRIVE_X; y=$MEDIUM_TDRIVE_Y; fi
    else
      x=15; y=15
      if [[ "$ds" == geolife ]]; then size=2m; radius=20
      else size=3m; radius=75; fi
    fi
    flat="$DATA_DIR/${ds}_${size}_xy.txt"
    nested="$DATA_DIR/subsets/${ds}_${size}_xy.txt"
    input=$flat
    [[ ! -f "$flat" && -f "$nested" ]] && input=$nested
    if [[ "$DRY_RUN" == 1 ]]; then
      input_sha=DRY_RUN_INPUT_SHA256
    else
      [[ -f "$input" ]] || { echo "Missing frozen input $input" >&2; exit 2; }
      input_sha=$(sha256sum "$input" | awk '{print $1}')
    fi
    TRIAL=1
    FROZEN_ACTION=capture FROZEN_INPUT_SHA="$input_sha" \
      SELECTOR=joint_peak REFRESH=true LANE=true REUSE=true FRONTIER=true \
      run_one "$FIG" "$ds" "$size" frozen_capture "$x" "$y" "$radius" dismc
    state="$OUT_DIR/$FIG/${ds}_${size}_frozen_capture_dismc_trial1.txt.frozen_calibration.bin"
    if [[ "$DRY_RUN" == 1 ]]; then state_sha=DRY_RUN_FROZEN_SHA256
    else
      [[ -f "$state" ]] || { echo "Frozen capture not created: $state" >&2; exit 2; }
      state_sha=$(sha256sum "$state" | awk '{print $1}')
    fi
    for ((rep=1;rep<=TRIALS;rep++)); do
      TRIAL=$rep
      if [[ "$FIG" == fig11b ]]; then
        for selector in joint_peak work_greedy; do
          FROZEN_ACTION=load FROZEN_INPUT_SHA="$input_sha" \
            FROZEN_STATE_PATH="$state" FROZEN_STATE_SHA="$state_sha" \
            SELECTOR="$selector" REFRESH=false LANE=false REUSE=true FRONTIER=true \
            run_one "$FIG" "$ds" "$size" "$selector" "$x" "$y" "$radius" dismc
        done
      else
        for R in 0 1; do
          for W in 0 1; do
            reuse=false; frontier=false
            [[ "$R" == 1 ]] && reuse=true
            [[ "$W" == 1 ]] && frontier=true
            FROZEN_ACTION=load FROZEN_INPUT_SHA="$input_sha" \
              FROZEN_STATE_PATH="$state" FROZEN_STATE_SHA="$state_sha" \
              SELECTOR=joint_peak REFRESH=false LANE=false \
              REUSE="$reuse" FRONTIER="$frontier" \
              run_one "$FIG" "$ds" "$size" "R${R}W${W}" "$x" "$y" "$radius" dismc
          done
        done
      fi
    done
  done
  exit 0
fi
if [[ "$FIG" == fig14 ]]; then
  if [[ "$DRY_RUN" == 1 ]]; then
    echo "python3 $ROOT/configs/derive_fig14.py $OUT_DIR/fig13 $OUT_DIR/fig14_checks.csv"
  else
    python3 "$ROOT/configs/derive_fig14.py" "$OUT_DIR/fig13" "$OUT_DIR/fig14_checks.csv"
  fi
  exit 0
fi

for ((TRIAL=1;TRIAL<=TRIALS;TRIAL++)); do
  case "$FIG" in
    fig4)
      for spec in \
        "geolife 110607.167 92027.241 100 q20" "geolife 111637.570 84896.430 100 q40" \
        "geolife 115704.130 107435.830 100 q60" "geolife 122321.748 107853.175 100 q80" \
        "tdrive 136512.651 116175.856 300 q20" "tdrive 112403.370 98369.878 300 q40" \
        "tdrive 122969.369 103183.266 300 q60" "tdrive 120662.702 109883.629 300 q80"; do
        read -r ds x y radius label <<< "$spec"
        run_one fig4 "$ds" 3m "$label" "$x" "$y" "$radius" dismc
        run_one fig4 "$ds" 3m "$label" "$x" "$y" "$radius" static
      done
      ;;
    fig5) echo "Fig. 5 uses Fig. 4 stage metrics; no additional execution"; exit 0 ;;
    fig6)
      for spec in "geolife 1m 20" "tdrive 3m 75"; do
        read -r ds size radius <<< "$spec"
        for method in dismc grid_d0 hilbert_d0 z_d0 operator; do
          run_one fig6 "$ds" "$size" external 15 15 "$radius" "$method"
        done
      done
      ;;
    fig7)
      for spec in \
        "geolife sparse 121585.662 102389.276 20" "geolife medium 122287.250 105282.863 20" \
        "geolife dense 114693.645 108474.258 20" "tdrive sparse 120924.613 114579.245 75" \
        "tdrive medium 106516.154 134723.013 75" "tdrive dense 126175.926 103115.703 75"; do
        read -r ds label x y radius <<< "$spec"
        run_one fig7 "$ds" 1m "$label" "$x" "$y" "$radius" dismc
        run_one fig7 "$ds" 1m "$label" "$x" "$y" "$radius" operator
      done
      ;;
    fig8)
      for ds in geolife tdrive porto; do
        radius=20; [[ "$ds" == tdrive ]] && radius=75
        for size in 100k 200k 400k 600k 800k 1m; do
          run_one fig8 "$ds" "$size" external 15 15 "$radius" single_esmc
          run_one fig8 "$ds" "$size" external 15 15 "$radius" dismc
        done
      done
      ;;
    fig9)
      for ds in geolife tdrive; do
        if [[ "$ds" == geolife ]]; then x=$MEDIUM_GEOLIFE_X; y=$MEDIUM_GEOLIFE_Y; radius=60
        else x=$MEDIUM_TDRIVE_X; y=$MEDIUM_TDRIVE_Y; radius=200; fi
        for cores in 8 16 24 32 40; do
          TOTAL_EXECUTOR_CORES="$cores" run_one fig9 "$ds" 3m "cores${cores}" "$x" "$y" "$radius" dismc
        done
      done
      ;;
    table1)
      BUDGET=0.10 COVERAGE=8 LANE_OWNERS=8 run_one table1 geolife full full 124414.676 106577.117 20 dismc
      BUDGET=0.10 COVERAGE=8 LANE_OWNERS=8 run_one table1 tdrive full full 116808.495 114686.700 200 dismc
      ;;
    fig10)
      for ds in geolife tdrive; do
        if [[ "$ds" == geolife ]]; then size=2m; x=$MEDIUM_GEOLIFE_X; y=$MEDIUM_GEOLIFE_Y; radii=(15 20 30)
        else size=3m; x=$MEDIUM_TDRIVE_X; y=$MEDIUM_TDRIVE_Y; radii=(56.25 75 112.5); fi
        for radius in "${radii[@]}"; do
          for mode in spatial_full dependency; do
            MODE="$mode" REFRESH=false LANE=false PROBE_OWNER_LIMIT=8 ACQUISITION_OWNER_LIMIT=8 \
              run_one fig10 "$ds" "$size" "r${radius}_${mode}" "$x" "$y" "$radius" dismc
          done
        done
      done
      ;;
    fig11a)
      for ds in geolife tdrive; do
        if [[ "$ds" == geolife ]]; then size=2m; x=$MEDIUM_GEOLIFE_X; y=$MEDIUM_GEOLIFE_Y; radius=40
        else size=3m; x=$MEDIUM_TDRIVE_X; y=$MEDIUM_TDRIVE_Y; radius=150; fi
        for paired in false true; do
          REFRESH=true LANE=true PARENT_REPLAY="$paired" PROBE_OWNER_LIMIT=8 ACQUISITION_OWNER_LIMIT=8 \
            run_one fig11a "$ds" "$size" "paired${paired}" "$x" "$y" "$radius" dismc
        done
      done
      ;;
    fig12)
      echo "NOTE: Independent signal runs; paper Fig. 12 matched-information requires fixed acquired candidates/probe identities, not supplied by this command." >&2
      for ds in geolife tdrive; do
        if [[ "$ds" == geolife ]]; then size=2m; x=$MEDIUM_GEOLIFE_X; y=$MEDIUM_GEOLIFE_Y; radius=40
        else size=3m; x=$MEDIUM_TDRIVE_X; y=$MEDIUM_TDRIVE_Y; radius=150; fi
        for signal in unit static sampled; do
          SIGNAL="$signal" REFRESH=false LANE=false PROBE_OWNER_LIMIT=8 ACQUISITION_OWNER_LIMIT=8 \
            run_one fig12 "$ds" "$size" "$signal" "$x" "$y" "$radius" dismc
        done
      done
      ;;
    *) echo "Unknown entry: $FIG; frozen-state controls Fig. 11(b)/13/14 are separate" >&2; exit 2 ;;
  esac
done
