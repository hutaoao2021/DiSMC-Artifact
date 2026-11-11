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
export DRIVER_MEMORY=8G # heavy online/full-data driver size reported in paper
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

**Data paths.** Set `DATA_DIR` to the dataset workspace produced by `data/historical/scripts/prepare_all.sh` and `create_subsets.sh`, e.g. `$PWD/data/historical/reproduction`. The runner accepts the resulting `prepared/` and `subsets/` directories, or flat files in `DATA_DIR`.

To generate the 100K–800K Fig. 8 prefixes and GeoLife/TDrive 2M prefixes from existing frozen 1M/3M inputs, run:

```bash
DATA_DIR="$PWD/data/historical/reproduction" bash configs/prepare_paper_subsets.sh
```

This does not rerandomize the samples or overwrite existing outputs. The supplement explicitly defines GeoLife 2M as the first 2M records of its frozen 3M sample.

**Fig. 11(a) validity:** `microLaneProbeRefinement=true` requires native candidate refresh. Accordingly `run_paper_suite.sh fig11a` uses both `microRefreshCandidates=true` and `microLaneProbeRefinement=true`, varying only `microLaneParentReplay=false/true` between the calibration modes.

**Fig. 12 limitation:** `run_paper_suite.sh fig12` currently launches three independent native signal experiments. The paper's Fig. 12 instead **fixes acquired candidates, observed probes, and other information across the three arms**. Holding just probe limits constant is insufficient. Treat those commands as a runnable signal diagnostic, not an exact matched-information reproduction.
**Crucial correction for Static-Greedy:** it is not enough to set `microSelector=work_greedy` while keeping `microPlannerPolicy=sampled_peak`: the latter still performs online probing. The script instead sets `microPlannerPolicy=peak`, turns off frontier/reuse/refinement, and uses the static greedy selector.

**Paper parameters and actual execution:** Fig. 6 and Fig. 7 now include the assembled operator arm through the existing SpatialOperatorPipeline and its standalone adapter. See `configs/operator-baseline.md` (source ZIP unchanged). Unlike the historical streaming operator variant, this adapter runs the released source's pipeline with complete exported members. Its new timing must be labeled accordingly.

**Medium coordinate qM:** The paper reports the dataset-specific medium point for some 2M/3M controls but does not disclose all those numeric qM values. The runner intentionally defaults to the published 1M medium position (`MEDIUM_GEOLIFE_X/Y`, `MEDIUM_TDRIVE_X/Y`); replace these with measured coordinates if exact correspondence is required. No historical number is fabricated.

**Matched information:** Fig. 12's Unit/Static/Sampled commands run the corresponding code switches with fixed acquisition limits. They are valid controlled runs, but identical candidate/probe IDs have not yet been empirically demonstrated. Do not treat differences as the paper's exact matched-information measurements without comparing their actual identities.

**Frozen controls:** Fig. 11(b) captures one set of inputs/candidate/work/probe information per dataset, then replays it three times each with Joint and Greedy. Fig. 13 likewise captures once and runs all four R/W combinations three times. The source ZIP honors independent R/W controls (JDK 8 regression passed). Fig. 14 is derived from Fig. 13's `*.micro_tasks.csv` (candidate, z-window and distance-check counters) without rerunning Spark.

```bash
TRIALS=3 bash configs/run_paper_suite.sh fig6
TRIALS=3 bash configs/run_paper_suite.sh fig7
TRIALS=3 bash configs/run_paper_suite.sh fig11b
TRIALS=3 bash configs/run_paper_suite.sh fig12
TRIALS=3 bash configs/run_paper_suite.sh fig13
bash configs/run_paper_suite.sh fig14
```

Use a fresh `OUT_DIR` for any new execution; captures and all replay variants are written with distinct names and SHA-256-guarded state identities. `fig14_checks.csv` and `fig14_checks_means.csv` are derived task-level results (not additional experimental trials).

Fig. 11(b) and Fig. 13 now have capture-once-and-replay script entries; these share SHA-256-protected snapshots and distinguish capture from timed replay runs. Fig. 14 reads those same formal task rows. The published 192 completed-ID count and new source-specific timings are not assumed identical without checking the actual generated output. This is a full runnable *new experiment protocol*, not a claim that the exact historical executable or its timings have been recreated.
