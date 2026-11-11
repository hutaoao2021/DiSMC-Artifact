# DiSMC — Research Artifact

**DiSMC: Dependency-Complete Planning for Distributed Skyline Micro-Cluster Queries**

This repository contains the Java/Spark implementation, data-preparation scripts, experiment commands, reported aggregate results, and supplementary material.

## Repository contents

| Path | Purpose |
| --- | --- |
| [Source release](artifact/DiSMC-source-release.zip) | Complete Java source, build scripts and selected tests |
| [Data preparation](data/README.md) | Official GeoLife, TDrive and Porto sources; preprocessing and fixed-seed sampling |
| [Run instructions](configs/run-commands.md) | Shell commands for the paper's figures and Table I |
| [Experiment settings](configs/experiment-settings.md) | Exact reported datasets, query parameters, budgets, resource configuration and measurement scope |
| [Fixed queries](configs/fixed-query-coordinates.csv) | Recorded query positions |
| [Reported results](results/README.md) | CSV aggregates and metric definitions |
| [Supplement](supplementary/DiSMC-supplementary-20261110.pdf) | Additional protocols, results and proofs |

GeoLife, TDrive and Porto are obtained from the original providers listed in the [data guide](data/README.md).

## 1. Build and run a small query

Requirements: **Linux/Bash, JDK 8, Apache Spark 3.2.0 (Scala 2.12)**. Maven is supported; the source build script can otherwise use Spark's JARs.

From the repository root:

```bash
export JAVA_HOME=/path/to/jdk8
export PATH="$JAVA_HOME/bin:$PATH"
export SPARK_HOME=/path/to/spark-3.2.0

unzip artifact/DiSMC-source-release.zip
(cd DiSMC-source && bash build.sh && bash scripts/check_selected.sh)

OUT="$(mktemp -d)"
(cd DiSMC-source && bash scripts/run_small_online.sh "$OUT/smoke.txt")
```

The last command runs the included five-point functional example on Spark `local[2]` and checks result and member export.

## 2. Prepare the datasets

Install Python 3, `pyproj` and GNU `sort`. Follow [data/README.md](data/README.md) for official downloads, and set the paths to the downloaded files:

```bash
export GEOLIFE_INPUT="/path/to/Geolife Trajectories 1.3.zip"
export TDRIVE_INPUT="/path/to/tdrive/taxi_log_2008_by_id"
export PORTO_INPUT="/path/to/porto/train.csv"
export WORK_ROOT="$PWD/data/historical/reproduction"

bash data/historical/scripts/prepare_all.sh
bash data/historical/scripts/create_subsets.sh
DATA_DIR="$WORK_ROOT" bash configs/prepare_paper_subsets.sh
```

Outputs are created under `$WORK_ROOT/prepared/`, `subsets/` and `metadata/`. The scripts reject existing output paths and preserve the supplied historical metadata. GeoLife uses seed `20260925`; TDrive and Porto use `20260924`.

## 3. Run the paper experiment configurations

From the repository root after the build and data preparation:

```bash
export SPARK_MASTER=spark://your-master:7077
export DATA_DIR="$PWD/data/historical/reproduction"
export OUT_DIR="$PWD/results/reproduction-$(date +%Y%m%d-%H%M%S)"
export TOTAL_EXECUTOR_CORES=40
export EXECUTOR_CORES=4
export EXECUTOR_MEMORY=4G
export DRIVER_MEMORY=8G

DRY_RUN=1 TRIALS=3 bash configs/run_paper_suite.sh fig4
TRIALS=3 bash configs/run_paper_suite.sh fig4
TRIALS=3 bash configs/run_paper_suite.sh table1
```

Replace `fig4` with `fig6`, `fig7`, `fig8`, `fig9`, `fig10`, `fig11a`, `fig11b`, `fig12` or `fig13`. `fig5` uses Fig. 4 stage metrics rather than a new query; `fig14` summarizes Fig. 13 formal-task counters. Use **fresh output paths**. See [the command guide](configs/run-commands.md) and [experiment matrix](configs/experiment-settings.md) for the specific controls.

## Evaluation protocols

- Online experiments use a **5% additional-input budget**; Table I full-data experiments use **10%**.
- Fig. 11(b) and Fig. 13 run on shared frozen states. Fig. 14 summarizes the formal-task counters from Fig. 13.
- Fig. 6–7 invoke the included `SpatialOperatorPipeline` through a Spark adapter. This is the released assembled-operator implementation.
- Fig. 12 offers independent Unit/Static/Sampled signal runs. The paper's matched-information control additionally fixes acquired candidate and probe identities; the distinction is documented in the [run guide](configs/run-commands.md).
- For dataset-specific medium positions, the runner exposes `qM` coordinate overrides. The [experiment settings](configs/experiment-settings.md) identify the representative defaults.

[Result CSVs](results/README.md) report the paper's aggregate measurements. Runtime is expected to vary with cluster resources, data preparation and experimental configuration.
