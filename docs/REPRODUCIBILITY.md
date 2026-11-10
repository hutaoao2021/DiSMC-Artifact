# DiSMC reproducibility guide

## 1. Software requirements

The 2026-11-02 source package targets:

- Java Development Kit 8
- Apache Spark 3.2.0 and Scala 2.12 runtime JARs
- Bash and either Maven or the JDK compilation tools

Set `JAVA_HOME` and `SPARK_HOME` to existing installations.

## 2. Compile and run the supplied checks

Extract `artifact/DiSMC-source-20261102.zip`, then:

```bash
cd DiSMC-source
export JAVA_HOME=/path/to/jdk8
export SPARK_HOME=/path/to/spark-3.2.0
bash build.sh
bash scripts/check_selected.sh
bash scripts/run_small_online.sh /absolute/new/output/dismc-smoke.txt
```

The smoke test uses `examples/five_points.txt`, Spark `local[2]`, a 5% additional-input record budget, and member export. The output path must not already exist.

## 3. Cluster launcher

The launcher is `scripts/run_profile.sh` and has the following calling convention:

```bash
bash scripts/run_profile.sh PROFILE INPUT OUTPUT PARTITIONS RADIUS DENSITY CELL_FACTOR \
  -- --conf spark.skyline.shardReadBudget=0.05
```

Before a cluster run, explicitly configure `SPARK_HOME`, `SPARK_MASTER`, `TOTAL_EXECUTOR_CORES`, `EXECUTOR_CORES`, `EXECUTOR_MEMORY`, `DRIVER_MEMORY`, and where applicable `QUERY_X` and `QUERY_Y`. The launcher accepts several method profiles; inspect the `case "$PROFILE"` list in the script for recognized values.

Use unique output paths. The launcher writes a `.manifest` beside the output, recording method, dataset path, selected parameters, resource requests and JAR SHA-256.

## 4. Understanding the measurement scopes

The manuscript distinguishes complete online end-to-end time from frozen-state replay measurements and component-only diagnostics. When reproducing a figure, use the exact dataset subset, query location, radius, plan budget, acquisition policy, execution profile and timing scope recorded for that experiment. Do not combine measurements from different protocols into the same statistics.

The source release contains its own build and regression verification record (`VERIFICATION.json`). Its `SOURCE_MANIFEST.json` identifies the integrated source tree. Experimental result provenance is recorded separately from build checks.

## 5. Output and comparisons

For correctness tests, compare objective frontiers under the documented finite-candidate numerical semantics and check complete members when the experiment supports that validation. For timing comparisons, report repeated-run statistics with the aggregation rule specified by each paper figure or table.

See `docs/EXPERIMENT_INDEX.md` for the figure groups and `supplementary/supplementary.pdf` for additional protocols.
