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

For the paper's no-probe Static-Greedy comparator, use `microPlannerPolicy=peak` as well as `SELECTOR=work_greedy`, and disable `microProbeFrontier`, `microLaneProbeRefinement`, `microCalibratePooledFrontier` and `microCompletionReuse`. Merely changing the selector with `sampled_peak` active still invokes online probes. Use separate outputs for each method and trial.

## 3. Table I full-data settings

Use the same launcher and Micro-Partition configuration above, with the full prepared input and a 10% cap:

| Dataset | Input | Query `(x,y)` | Radius | Budget |
| --- | --- | --- | ---: | ---: |
| GeoLife | `geolife_xy.txt` (18,355,282 points) | `(124414.676, 106577.117)` | 20 | 10% |
| TDrive | `tdrive_xy.txt` (11,274,655 points) | `(116808.495, 114686.700)` | 200 | 10% |

Set `QUERY_X`, `QUERY_Y`, `INPUT`, and `RADIUS` to the row being run, and set `BUDGET=0.10`, `PROBE_COVERAGE_ANCHORS=8`, and `LANE_PROBE_MAX_OWNERS=8`. Keep `spark.skyline.budgetDiagnostic=true`. Run the three trials serially with distinct output paths.

## 4. Baselines and ablations

- Static-Greedy comparator: keep `hilbert_full`, set `SELECTOR=work_greedy`, `microPlannerPolicy=peak`, and disable online probing/reuse as above.
- ESMC: use profile `single_esmc`.
- Distributed baseline profiles: `z_d0`, `hilbert_d0`, and `grid_d0`.
- Principal ablations: `hilbert_wo_planner` and `hilbert_wo_engine`.
- Additional supported profiles: `wo_planner`, `wo_engine`, `wo_dependency_partition`, `wo_sharing`, `wo_refinement`, `wo_new_bounds`, and `wo_prepared_reuse`.

For Fig. 10, use `microPartitionMode=spatial_full` for Full-parent and `dependency` for Dependency while keeping the acquired workload matched. For Fig. 12, set `microCostSignal` to `unit`, `static`, or `sampled` with the matching captured state. Fig. 11b and Fig. 13 replay comparisons require their corresponding frozen state; they cannot be recreated by changing the profile alone. The exact dataset, query, radius, budget, and measurement scope for each figure are listed in [`experiment-settings.md`](experiment-settings.md).

## 5. Paper-parameter batch commands

`configs/run_paper_suite.sh` supplies source-backed calls for the published dataset sizes, coordinates, radii, methods, budgets, and repetition counts. No historical run log is necessary to use these commands. Extract and build the ZIP (Section 1) first; then, **from the repository root**:

```bash
export JAVA_HOME=/path/to/jdk8
export PATH="$JAVA_HOME/bin:$PATH"
export SPARK_HOME=/path/to/spark-3.2.0
export SPARK_MASTER=spark://your-master:7077
export DATA_DIR=/path/to/prepared-and-subsets
export OUT_DIR=/path/to/new-results

# Preview actual shell arguments without running:
DRY_RUN=1 TRIALS=1 bash configs/run_paper_suite.sh fig4

# Each figure/table may be run independently:
TRIALS=3 bash configs/run_paper_suite.sh fig4
TRIALS=3 bash configs/run_paper_suite.sh fig10
TRIALS=3 bash configs/run_paper_suite.sh fig11a
TRIALS=3 bash configs/run_paper_suite.sh fig12
TRIALS=3 bash configs/run_paper_suite.sh table1
```

The script also accepts `fig5` (derive stage metrics from Fig. 4; no new run), `fig6`, `fig7`, `fig8` and `fig9`. `TRIALS` defaults to 1 for a quick run; the paper uses three repetitions for the comparisons above. Existing output paths are never overwritten. Fig. 8 uses a 4 GiB single-machine ESMC Java heap and 7,200-second timeout.

**Data paths.** Inputs follow `$DATA_DIR/geolife_3m_xy.txt`, `$DATA_DIR/tdrive_3m_xy.txt`, `$DATA_DIR/porto_1m_xy.txt`, etc. Full prepared data are `$DATA_DIR/geolife_xy.txt` and `$DATA_DIR/tdrive_xy.txt`. For a 2M prefix of a frozen 3M sample, prepare:

```bash
head -n 2000000 "$DATA_DIR/geolife_3m_xy.txt" > "$DATA_DIR/geolife_2m_xy.txt"
head -n 2000000 "$DATA_DIR/tdrive_3m_xy.txt" > "$DATA_DIR/tdrive_2m_xy.txt"
```

Fig. 8 also needs 100k, 200k, 400k, 600k and 800k input prefixes. See `data/README.md` for preparing 1M/3M/full datasets.

| Experiment | Runnable parameter matrix |
| --- | --- |
| Fig. 4 | GeoLife/TDrive 3M, 8 published fixed queries, r=100/300, budget 5%, DiSMC vs Static-Greedy, 3 trials |
| Fig. 5 | Stage breakdown of the same Fig. 4 runs |
| Fig. 6 | GeoLife 1M / TDrive 3M, external (15,15), r=20/75, Grid/Hilbert/Z profiles and DiSMC |
| Fig. 7 | GeoLife/TDrive 1M, published sparse/medium/dense positions, r=20/75, DiSMC |
| Fig. 8 | GeoLife/TDrive/Porto 100K–1M, external (15,15), r=20/75/20, single ESMC vs DiSMC |
| Fig. 9 | GeoLife/TDrive 3M, medium query, r=60/200, 8/16/24/32/40 cores, 5% |
| Table I | Full GeoLife/TDrive, original published coordinates, r=20/200, budget **10%** |
| Fig. 10 | GeoLife 2M/TDrive 3M, medium query, radii 15/20/30 and 56.25/75/112.5, 5%, Full-parent vs Dependency |
| Fig. 11(a) | GeoLife 2M/TDrive 3M, medium query, r=40/150, 5%, `microLaneParentReplay=false/true` |
| Fig. 12 | GeoLife 2M/TDrive 3M, medium query, r=40/150, 5%, `microCostSignal=unit/static/sampled` |

**Crucial correction for Static-Greedy:** it is not enough to set `microSelector=work_greedy` while keeping `microPlannerPolicy=sampled_peak`: the latter still performs online probing. The script instead sets `microPlannerPolicy=peak`, turns off frontier/reuse/refinement, and uses the static greedy selector.

**Source/paper boundaries:** Fig. 6–7 assembled spatial-operator comparator uses a separate entry point not exposed by `run_profile.sh`, so those entries reproduce the listed launcher profiles, not the operator arm. For several 2M/3M mechanism experiments, the public paper reports the dataset-specific medium location `qM` without exact numeric coordinates. The script uses the *published 1M position-control medium position* as an explicitly representative default; override with `MEDIUM_GEOLIFE_X`, `MEDIUM_GEOLIFE_Y`, `MEDIUM_TDRIVE_X`, `MEDIUM_TDRIVE_Y` to use the original values if available. These runs can execute without those historical values, but must not be described as exact numeric replication.

Fig. 11(b) and Fig. 13 require a common captured frozen state; Fig. 14 reuses Fig. 13 task counts. The source ZIP can export/load frozen state, but its replay path unconditionally restores the completed-ID and witness state, so changing two Boolean switches on replay is **not yet** evidence of the four controlled Fig. 13 combinations. This is one concrete source behavior to validate, not a requirement to recover old logs. This runner never claims it has rerun the original full-scale figures.
