# DiSMC Research Artifact

**DiSMC: Dependency-Complete Planning for Distributed Skyline Micro-Cluster Queries**

This repository provides the Java/Spark implementation, build and run instructions, dataset preparation scripts, experiment settings, reported result tables, and supplementary material for the DiSMC paper.

## Contents

| Path | Contents |
| --- | --- |
| [`artifact/DiSMC-source-release.zip`](artifact/DiSMC-source-release.zip) | Integrated Java/Spark source, tests, launch scripts, and the validated 10% Micro-Partition budget compatibility fix |
| [`docs/INSTALL.md`](docs/INSTALL.md) | Software requirements, build, tests, and smoke run |
| [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) | Execution profiles and reproduction scope |
| [`configs/experiment-settings.md`](configs/experiment-settings.md) | Dataset sizes, queries, radii, budgets, and experiment protocols |
| [`configs/run-commands.md`](configs/run-commands.md) | Copyable commands for build, smoke, distributed execution, baselines, and ablations |
| [`configs/fixed-query-coordinates.csv`](configs/fixed-query-coordinates.csv) | Fixed query coordinates used by the evaluation |
| [`data/README.md`](data/README.md) | Dataset sources, historical preprocessing scripts, and input format |
| [`results/README.md`](results/README.md) | Result CSV descriptions and metric definitions |
| [`supplementary/DiSMC-supplementary-20261110.pdf`](supplementary/DiSMC-supplementary-20261110.pdf) | Supplementary proofs, protocols, and additional experiments |

## Quick start

Requirements: JDK 8, Apache Spark 3.2.0 with Scala 2.12, and Bash. From the repository root:

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

The five-point smoke run checks that the packaged application launches and exports members. It is a functionality check, not a paper-scale performance benchmark.

## Run the paper methods

Start with [`configs/run-commands.md`](configs/run-commands.md). It documents the distributed launcher, query and data parameters, the `joint_peak` and `work_greedy` selector settings, baseline profiles, and the 5%/10% budget options. Use [`configs/experiment-settings.md`](configs/experiment-settings.md) for the dataset and query settings associated with each figure and table.

For the Micro-Partition path, the default additional-input budget is 1%. The release supports explicit 5% and 10% diagnostic budgets with `spark.skyline.budgetDiagnostic=true` and `spark.skyline.shardReadBudget=0.05` or `0.10`.

## Data and results

Raw third-party datasets are not redistributed. Their official sources, preparation steps, and historical processing scripts are described in [`data/README.md`](data/README.md). The CSV files in `results/` contain the reported aggregate values used by the paper; see [`results/README.md`](results/README.md) for their scope.

## Reproduction scope

The source archive includes build scripts, selected regression tests, and a small end-to-end example. Large-scale paper timings were collected with their recorded data, configuration, and execution environment; the release does not claim that the entire performance suite has been rerun with this packaged source. The run instructions explain how to execute the methods and how to configure the reported workloads.
