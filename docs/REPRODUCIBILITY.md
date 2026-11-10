# DiSMC reproducibility guide

This guide is grounded in the **2026-11-02 integrated source release**, including its portable packaging fix. The integrated release is **not** claimed to be the exact historical binary of every experiment reported in the manuscript.

## 1. Entry points and their scope

| Entry point | Purpose |
| --- | --- |
| `bash build.sh` | Compile the source to `target/dismc-unified-1.0.0.jar` and produce build provenance |
| `bash scripts/check_selected.sh` | Run 14 selected regression classes |
| `bash scripts/run_small_online.sh NEW_OUTPUT_PATH` | Five-point Spark `local[2]` smoke query with member export |
| `bash scripts/run_profile.sh ...` | Launch a named method profile with explicitly supplied experiment inputs |

Read [the installation guide](INSTALL.md) first.

## 2. Profile launcher syntax

From `DiSMC-source/`:

```text
bash scripts/run_profile.sh PROFILE INPUT OUTPUT PARTITIONS RADIUS DENSITY CELL_FACTOR [-- spark-submit-options]
```

The optional `--` delimiter is mandatory if extra Spark options are given. Examples of recognized profiles include `hilbert_full`, `hilbert_wo_planner`, `hilbert_wo_engine`, `z_d0`, `hilbert_d0`, `grid_d0`, and `single_esmc`; inspect the `case "$PROFILE"` statement for the authoritative accepted set.

The launcher dispatches distributed profiles through `spark-submit` and the `single_esmc` comparator through a Java process using the Spark runtime classpath.

## 3. Required execution configuration

The source launcher reads:

- `SPARK_HOME` — required.
- `SPARK_MASTER` — required for distributed profiles, **not** for `single_esmc`.
- `TOTAL_EXECUTOR_CORES`, `EXECUTOR_CORES`, `EXECUTOR_MEMORY`, `DRIVER_MEMORY` — specify explicitly to match an experiment rather than relying on portable fallback values.
- `QUERY_X` and `QUERY_Y` — set **both** to reproduce a paper query. If omitted, the Java program uses (15.0, 15.0); do not assume this matches an arbitrary benchmark row.

Supply `INPUT` as a location accessible from the corresponding execution mode. In a multi-node Spark run, a driver-only local file path is not a substitute for data accessible to executors.

A *parameterized template*, **not** a complete manuscript experiment command:

```bash
export SPARK_HOME=/path/to/spark-3.2.0
export SPARK_MASTER=spark://your-master-host:7077
export TOTAL_EXECUTOR_CORES=40
export EXECUTOR_CORES=4
export EXECUTOR_MEMORY=4G
export DRIVER_MEMORY=4G
export QUERY_X=15
export QUERY_Y=15

bash scripts/run_profile.sh hilbert_full \
  "$INPUT_URI" "$NEW_OUTPUT_PATH" "$PARTITIONS" "$RADIUS_METERS" \
  "$DENSITY" "$CELL_FACTOR" \
  -- --conf spark.skyline.shardReadBudget=0.05
```

Replace every placeholder and resource choice with the appropriate experiment values. The script rejects preexisting main or selected sidecar output paths; always use a fresh output prefix. For `single_esmc`, only extra options in the form `--conf spark.KEY=VALUE` are accepted and translated to JVM system properties.

## 4. A necessary 5% budget distinction

Do not blindly reuse one budget configuration across execution modes.

- The bundled five-point smoke script requests `spark.skyline.shardReadBudget=0.05` and does **not** enable the Micro-Partition experimental path.
- In `ExperimentConfig.java`, the Micro-Partition path defaults to `0.01`. Requesting `0.05` **also requires** `spark.skyline.budgetDiagnostic=true` and compatible Micro-Partition experiment settings.
- These budget flags alone do **not** reconstruct the paper's acquisition, planner, replay or execution configuration. Exact figure-by-figure commands and configuration files will be published in the separate experiment-config stage.

The main-paper full-input 10% experiment and the ordinary 5% experiments must remain distinct.

## 5. Output and provenance

After a successful `run_profile.sh` invocation, a `.manifest` sidecar reports method/profile, input/output paths, query settings, resources, JAR SHA-256 and selected result fields. Some experimental configurations additionally generate JSON, observation, member-export or task-details files.

The source archive includes:

- `SOURCE_MANIFEST.json`: file inventory and integrated source checksums.
- `VERIFICATION.json`: prior build/regression/smoke verification record.
- `PUBLIC_PACKAGING_NOTES.md`: portability changes made to shell scripts and documentation.

**Validation scope:** the packaging audit checked archive integrity and shell interfaces; it did **not** perform a new JDK 8/Spark 3.2.0 end-to-end run or rerun the paper's entire performance suite. Do not relabel historical timings as new measurements of this integrated release.

## 6. Interpreting experiments

The manuscript separates **complete online E2E**, **frozen-state replay**, and **component-only diagnostics**. Use consistent data subsets, query locations, budgets, profiles, timing boundaries and aggregation rules. See [the experiment index](EXPERIMENT_INDEX.md), the [dataset notes](../data/README.md) and the final supplementary PDF. A five-point smoke result does not validate large-scale performance claims.
