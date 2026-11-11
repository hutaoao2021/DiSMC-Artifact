# Running DiSMC

These commands use the public source archive and its `scripts/run_profile.sh` launcher. Replace paths and the Spark master with locations in your environment. Every output path must be new.

## 1. Build and smoke test

From the repository root:

```bash
unzip artifact/DiSMC-source-release.zip
cd DiSMC-source
export JAVA_HOME=/path/to/jdk8
export PATH="$JAVA_HOME/bin:$PATH"
export SPARK_HOME=/path/to/spark-3.2.0

bash build.sh
bash scripts/check_selected.sh
OUT_DIR="$(mktemp -d)"
bash scripts/run_small_online.sh "$OUT_DIR/smoke.txt"
```

## 2. Distributed DiSMC run

Set the cluster resources and query location, then run the complete profile. The example uses a GeoLife 3M query from Fig. 4:

```bash
export SPARK_HOME=/path/to/spark-3.2.0
export SPARK_MASTER=spark://your-master:7077
export TOTAL_EXECUTOR_CORES=40
export EXECUTOR_CORES=4
export EXECUTOR_MEMORY=4G
export DRIVER_MEMORY=8G
export QUERY_X=110607.167
export QUERY_Y=92027.241

INPUT=/path/to/geolife_3m_xy.txt
OUTPUT=/path/to/new-output/geolife-q20-dismc.txt
RADIUS=100
BUDGET=0.05
SELECTOR=joint_peak
PROBE_COVERAGE_ANCHORS=0
LANE_PROBE_MAX_OWNERS=4

bash scripts/run_profile.sh hilbert_full \
  "$INPUT" "$OUTPUT" 200 "$RADIUS" 2 1 \
  -- \
  --conf spark.skyline.experiment.enabled=true \
  --conf spark.skyline.experiment.partitionStrategy=workload \
  --conf spark.skyline.experiment.organization=independent_owner \
  --conf spark.skyline.experiment.shardStrategy=none \
  --conf spark.skyline.experiment.transportEncoding=deduplicated_union \
  --conf spark.skyline.experiment.ownerThreads=1 \
  --conf spark.skyline.experiment.maxPieces=4 \
  --conf spark.skyline.experiment.preparedMode=private_owner_index \
  --conf spark.skyline.experiment.projectionCache=on \
  --conf spark.skyline.experiment.microPartition=true \
  --conf spark.skyline.experiment.microPartitionMode=dependency \
  --conf spark.skyline.experiment.microCostModel=cell_quadratic \
  --conf spark.skyline.experiment.microTaskOrder=cost \
  --conf spark.skyline.experiment.microPlannerPolicy=sampled_peak \
  --conf spark.skyline.experiment.microRefinedCounting=true \
  --conf spark.skyline.experiment.microCountingCellMultiplier=2.0 \
  --conf spark.skyline.experiment.geometricBounds=true \
  --conf spark.skyline.experiment.microProbeFrontier=true \
  --conf spark.skyline.experiment.microDenseBoundaryCounting=true \
  --conf spark.skyline.microSelector="$SELECTOR" \
  --conf spark.skyline.microAdaptiveAcquisition=true \
  --conf spark.skyline.microRefreshCandidates=true \
  --conf spark.skyline.microProbeOwnerLimit=32 \
  --conf spark.skyline.microProbeCoverageAnchors="$PROBE_COVERAGE_ANCHORS" \
  --conf spark.skyline.microAcquisitionCoverageFirst=true \
  --conf spark.skyline.microAcquisitionOwnerLimit=200 \
  --conf spark.skyline.microAuditAllCandidates=true \
  --conf spark.skyline.microSpatialCostCalibration=true \
  --conf spark.skyline.microLaneProbeRefinement=true \
  --conf spark.skyline.microLaneProbeMaxAnchors=256 \
  --conf spark.skyline.microLaneProbeMaxOwners="$LANE_PROBE_MAX_OWNERS" \
  --conf spark.skyline.microLaneProbeMinimum=4 \
  --conf spark.skyline.microLaneProbeMaximum=8 \
  --conf spark.skyline.microDiagnosticMaxPieces=16 \
  --conf spark.skyline.microDiagnosticTargetAnchors=0 \
  --conf spark.skyline.microPlanAuditOnly=false \
  --conf spark.skyline.microCalibratePooledFrontier=true \
  --conf spark.skyline.microLaneProbeCoverUnsplit=true \
  --conf spark.skyline.shardReadBudget="$BUDGET" \
  --conf spark.skyline.budgetDiagnostic=true \
  --conf spark.skyline.stableInputIds=true \
  --conf spark.skyline.materializeMembers=true \
  --conf spark.skyline.memberOutputMode=partitioned \
  --conf spark.skyline.cacheMemberText=true \
  --conf spark.locality.wait=0s
```

For the same workload, set `SELECTOR=work_greedy` to run the greedy selector comparison. Use a separate output path for each method and trial.

## 3. Table I full-data settings

Use the same launcher and Micro-Partition configuration above, with the full prepared input and a 10% cap:

| Dataset | Input | Query `(x,y)` | Radius | Budget |
| --- | --- | --- | ---: | ---: |
| GeoLife | `geolife_xy.txt` (18,355,282 points) | `(124414.676, 106577.117)` | 20 | 10% |
| TDrive | `tdrive_xy.txt` (11,274,655 points) | `(116808.495, 114686.700)` | 200 | 10% |

Set `QUERY_X`, `QUERY_Y`, `INPUT`, and `RADIUS` to the row being run, and set `BUDGET=0.10`, `PROBE_COVERAGE_ANCHORS=8`, and `LANE_PROBE_MAX_OWNERS=8`. Keep `spark.skyline.budgetDiagnostic=true`. Run the three trials serially with distinct output paths.

## 4. Baselines and ablations

- Greedy selector comparison: keep `hilbert_full` and set `SELECTOR=work_greedy` instead of `joint_peak`.
- ESMC: use profile `single_esmc`.
- Distributed baseline profiles: `z_d0`, `hilbert_d0`, and `grid_d0`.
- Principal ablations: `hilbert_wo_planner` and `hilbert_wo_engine`.
- Additional supported profiles: `wo_planner`, `wo_engine`, `wo_dependency_partition`, `wo_sharing`, `wo_refinement`, `wo_new_bounds`, and `wo_prepared_reuse`.

For Fig. 10, use `microPartitionMode=spatial_full` for Full-parent and `dependency` for Dependency while keeping the acquired workload matched. For Fig. 12, set `microCostSignal` to `unit`, `static`, or `sampled` with the matching captured state. Fig. 11b and Fig. 13 replay comparisons require their corresponding frozen state; they cannot be recreated by changing the profile alone. The exact dataset, query, radius, budget, and measurement scope for each figure are listed in [`experiment-settings.md`](experiment-settings.md).
