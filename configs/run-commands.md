# Source-backed execution entry points and commands

**Purpose:** runnable *interfaces* for the **2026-11-02 integrated source**, with manuscript-specific parameters shown separately. Exact historical timing reproduction additionally requires the same source build, prepared input hash, Spark settings, acquisition state and timing scope. Commands with placeholders **must be filled in before execution**.

## 0. Prepare environment and source

The release ZIP is already available in this repository. Extract it from the top-level repository directory:

```bash
unzip artifact/DiSMC-source-20261102-release.zip
cd DiSMC-source

export JAVA_HOME=/path/to/jdk8
export PATH="$JAVA_HOME/bin:$PATH"
export SPARK_HOME=/path/to/spark-3.2.0

bash build.sh
bash scripts/check_selected.sh
```

## 1. Verified launcher interface

```text
bash scripts/run_profile.sh PROFILE INPUT OUTPUT PARTITIONS RADIUS DENSITY CELL_FACTOR [-- spark-submit-options]
```

Recognized profiles in the integrated launcher are:

- `single_esmc` — single-JVM ESMC comparator;
- `z_d0` / `hilbert_d0` / `grid_d0` — distributed local-kernel routing comparators;
- `hilbert_full` and `full` — complete configurations;
- `hilbert_wo_planner` / `hilbert_wo_engine` — principal ablations;
- `wo_planner`, `wo_engine`, `wo_dependency_partition`, `wo_sharing`, `wo_refinement`, `wo_new_bounds` and `wo_prepared_reuse` — further built-in toggles.

These are code-supported profile identifiers. **They do not by themselves reconstruct the paper's online acquisition, fixed-state controls or external spatial-operator assembly.**

`INPUT` must be a prepared data location accessible to the execution engine; `OUTPUT` must be new. `QUERY_X` and `QUERY_Y` must be set together or both omitted (the omitted default is 15,15). Extra Spark options must follow `--`. For `single_esmc`, only `--conf spark.KEY=VALUE` extras are accepted, translated to JVM system properties.

## 2. Small functionality check (directly runnable after installation)

```bash
OUT_DIR="$(mktemp -d)"
bash scripts/run_small_online.sh "$OUT_DIR/five-point-smoke.txt"
```

This runs Spark `local[2]` and the bundled five-point input; it is **not** a paper-scale benchmark.

## 3. Single-threaded ESMC example

The following is a *parameterized invocation*, not a full Fig. 8 reproduction. The single-machine process needs an input readable locally and enough heap for the chosen dataset.

```bash
export SPARK_HOME=/path/to/spark-3.2.0
export QUERY_X=15
export QUERY_Y=15
export JAVA_TOOL_OPTIONS="-Xmx4g"

bash scripts/run_profile.sh single_esmc \
  /absolute/path/to/prepared-geolife-100k.txt \
  /absolute/new/output/esmc-100k.txt \
  200 20 2 1
```

`JAVA_TOOL_OPTIONS` is a standard JVM mechanism; the launcher itself has no ESMC heap-size argument. Run with a prepared data input, not the raw GeoLife trajectory CSV. Keep the 7200-s timeout and three-repetition protocol separately when reproducing the paper's censored series.

## 4. Distributed routing comparison — command *template*

```bash
export SPARK_HOME=/path/to/spark-3.2.0
export SPARK_MASTER=spark://your-master:7077
export TOTAL_EXECUTOR_CORES=40
export EXECUTOR_CORES=4
export EXECUTOR_MEMORY=4G
export DRIVER_MEMORY=4G
export QUERY_X=15
export QUERY_Y=15

# GeoLife 1M external query example; choose a fresh output path:
bash scripts/run_profile.sh hilbert_d0 \
  "$PREPARED_GEOLIFE_1M_URI" "$NEW_OUTPUT_PATH" \
  200 20 2 1 \
  -- --conf spark.locality.wait=0s
```

For `z_d0`/`grid_d0` replace only the profile **when the comparator protocol permits the same settings**. For the assembled spatial-operator comparator, the correct operator implementation/driver path must be supplied separately; there is **no** launcher profile literally named `spatial_operators`.

## 5. Table IX 5% micro-mode configuration — source-checked core flags

These settings correspond to the key Micro-Partition conditions in the captured 2026-11-10 Table IX commands and satisfy the *configuration constraints checked in* `ExperimentConfig.java`. **This is a selected flag fragment, not the full 77-option historical command** (which also has Spark tuning, acquisition controls, observation and provenance paths). It has not been rerun on the new integrated binary.

```bash
export QUERY_X=15
export QUERY_Y=15
# Additionally set SPARK_HOME, SPARK_MASTER, cores, executor/driver memory
# and the prepared input and new output paths.

bash scripts/run_profile.sh hilbert_full \
  "$PREPARED_INPUT_URI" "$NEW_OUTPUT_PATH" \
  200 "$RADIUS_METERS" 2 1 \
  -- \
  --conf spark.skyline.experiment.enabled=true \
  --conf spark.skyline.experiment.partitionStrategy=workload \
  --conf spark.skyline.experiment.organization=independent_owner \
  --conf spark.skyline.experiment.shardStrategy=none \
  --conf spark.skyline.experiment.transportEncoding=deduplicated_union \
  --conf spark.skyline.experiment.ownerThreads=1 \
  --conf spark.skyline.experiment.maxPieces=4 \
  --conf spark.skyline.experiment.microPartition=true \
  --conf spark.skyline.experiment.microPartitionMode=dependency \
  --conf spark.skyline.experiment.microCostModel=cell_quadratic \
  --conf spark.skyline.experiment.microTaskOrder=cost \
  --conf spark.skyline.experiment.microPlannerPolicy=sampled_peak \
  --conf spark.skyline.experiment.microRefinedCounting=true \
  --conf spark.skyline.experiment.microCountingCellMultiplier=2.0 \
  --conf spark.skyline.experiment.geometricBounds=true \
  --conf spark.skyline.experiment.microProbeFrontier=true \
  --conf spark.skyline.shardReadBudget=0.05 \
  --conf spark.skyline.budgetDiagnostic=true \
  --conf spark.skyline.stableInputIds=true \
  --conf spark.skyline.materializeMembers=true \
  --conf spark.locality.wait=0s
```

Run with GeoLife 2M, radius **20**, or TDrive 3M, radius **75**, both q=(15,15), to match the visible *workload description* for Table IX. **Matching the measured charge numbers also requires the full original acquisition/refinement parameters and prepared inputs.** Do not interpret this fragment alone as an exact Table IX reproduction. The original per-owner records were used for manuscript verification, but are not required as a standalone public bundle.

## 6. Other mechanism settings

Examples of code-recognized options, **not full runnable protocols**:

- `spark.skyline.experiment.microCostSignal=unit|static|sampled` for the matched work-signal control. Non-`sampled` settings require eligible sampled-peak Micro-Partition execution.
- `spark.skyline.experiment.microCountingCellMultiplier=0.5|1|2|4` with `microPartition=true` and `microRefinedCounting=true` for the counting-resolution control.
- `spark.skyline.experiment.microCompletionReuse=true|false` for one reuse switch. Witness transfer and frozen responsibilities require additional matching state/control flags; this setting alone cannot recreate Fig. 13.
- `spark.skyline.microFrozenStateLoad=...` and matching provenance checks for the fixed-state selector, **not** an arbitrary online run.

## 7. Important 10% full-data limitation

Main Table I and supplementary full-data protocols used **10%** extra-input assignment caps. The current `ExperimentConfig.java`, when `microPartition=true`, permits the 1% default or only 2%, 3%, 5% with `spark.skyline.budgetDiagnostic=true`. A simple `--conf spark.skyline.shardReadBudget=0.10` therefore fails early in that Micro-Partition path. **No Table I "copy/paste exact command" is claimed for the integrated source until the historical runtime path or a separately verified release-specific configuration is established.** Do not silently substitute 5%.

## 8. Recording each new run

Use distinct outputs and record: dataset name and *prepared input hash*, subset seed/count, code/JAR SHA-256, profile, q, r, k, partitions/owners, all `--conf` options, core/memory requests, run ID, E2E definition and trial repetitions. The launcher writes an adjacent `.manifest` only after successful return. Do not treat a generated manifest as proof of result correctness.

See [experiment settings](experiment-settings.md), [query coordinates](fixed-query-coordinates.csv), and the supplementary PDF for the original measurement definitions.
