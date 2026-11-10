# Installation and minimal validation

This guide describes the actual build and script interfaces in the packaged `DiSMC-source/` tree. It does not claim that this documentation update reran Spark.

## 1. Required software

- **JDK 8** (the source-release verification used JDK 1.8.0_211).
- **Apache Spark 3.2.0**, with **Scala 2.12** runtime JARs.
- A Linux or compatible Bash shell, plus common tools (`find`, `sha256sum`, `jar` and `unzip`).
- **Maven** is optional: `build.sh` uses `mvn` if found, otherwise `javac` and Spark's bundled JARs.

The scripts assume a POSIX-like filesystem and shell. Cluster deployment additionally requires an accessible Spark master and shared/distributed data locations.

## 2. Check your environment

```bash
export JAVA_HOME=/path/to/jdk8
export PATH="$JAVA_HOME/bin:$PATH"
export SPARK_HOME=/path/to/spark-3.2.0

java -version
javac -version
"$SPARK_HOME/bin/spark-submit" --version
```

Confirm that Java reports 1.8 and Spark reports 3.2.0 with Scala 2.12. Make sure `$SPARK_HOME/jars` exists. Resolve setup failures before using the artifact scripts.

## 3. Extract and build

Once the release archive is present at the documented repository path:

```bash
unzip artifact/DiSMC-source-20261102-release.zip
cd DiSMC-source
bash build.sh
```

The expected JAR is `target/dismc-unified-1.0.0.jar`. Successful compilation also creates `target/build/provenance.json` containing JAR and Java-source SHA-256 values.

The optional Maven path may need access to a Maven repository to download dependencies. The non-Maven path instead uses `$SPARK_HOME/jars/*`.

## 4. Run the selected regression checks

```bash
bash scripts/check_selected.sh
```

This script compiles test sources and invokes **14 selected Java test classes** with assertions enabled. It covers planner/dependency safety, probe costs, candidate geometry, numerical boundaries and Spark member export. It is not a substitute for end-to-end workload validation.

The bundled `VERIFICATION.json` documents a previous successful verification in the source-release environment; those results must not be misrepresented as independently rerun by this documentation step.

## 5. Run the five-point smoke query

```bash
OUT_DIR="$(mktemp -d)"
bash scripts/run_small_online.sh "$OUT_DIR/smoke.txt"
```

This script launches `com.DistributedSMC` with `hilbert_full` on Spark `local[2]` and reads `examples/five_points.txt`. It enables member export and observation output. Its query settings and 5% budget are fixture settings, not the paper's full benchmark.

The output path and associated sidecar paths must not already exist. Inspect the main output and any generated `.json`, `.observation.json`, or `.members` outputs. The launcher must finish successfully before interpreting these files.

## 6. Next steps

For cluster execution, supported profiles and argument order, use [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md). For individual manuscript figures and tables, consult the [experimental settings and figure index](../configs/experiment-settings.md) and the [supplementary document](../supplementary/DiSMC-supplementary-20261110.pdf). Large performance measurements require their recorded input subsets, configurations and resources.
