# Installation and quick validation

## Requirements

- JDK 8.
- Apache Spark 3.2.0 with Scala 2.12.
- Linux or a compatible Bash environment.
- Maven is optional. `build.sh` uses Maven when available and otherwise compiles against the Spark JARs.
- For dataset preprocessing: Python 3, `pyproj`, and GNU `sort`.

## Configure the environment

```bash
export JAVA_HOME=/path/to/jdk8
export PATH="$JAVA_HOME/bin:$PATH"
export SPARK_HOME=/path/to/spark-3.2.0

java -version
javac -version
"$SPARK_HOME/bin/spark-submit" --version
```

Confirm Java 8 and Spark 3.2.0 / Scala 2.12 before building.

## Extract and build

From the repository root:

```bash
unzip artifact/DiSMC-source-release.zip
cd DiSMC-source
bash build.sh
```

The build creates `target/dismc-unified-1.0.0.jar`.

## Run regression checks

```bash
bash scripts/check_selected.sh
```

This runs the 14 selected Java regression-test entry points included in the source archive.

## Run the smoke query

```bash
OUT_DIR="$(mktemp -d)"
bash scripts/run_small_online.sh "$OUT_DIR/five-point-smoke.txt"
```

This runs the bundled five-point example with Spark `local[2]`, a 5% fixture budget, and member export. Use a new output path for every run. This test checks execution and output generation; it is not a reproduction of the paper performance results.

## Run on a Spark cluster

Set `SPARK_MASTER`, `TOTAL_EXECUTOR_CORES`, `EXECUTOR_CORES`, `EXECUTOR_MEMORY`, and `DRIVER_MEMORY` before using `scripts/run_profile.sh`. Set both `QUERY_X` and `QUERY_Y` to the query coordinates. The launcher syntax and paper workload examples are in [`../configs/run-commands.md`](../configs/run-commands.md).
