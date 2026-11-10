# DiSMC — Research Artifact

**DiSMC: Dependency-Complete Planning for Distributed Skyline Micro-Cluster Queries**

This repository organizes the DiSMC implementation, its supplementary technical document, and instructions for running the provided checks and experiments. DiSMC targets distributed skyline micro-cluster queries with dependency-complete task inputs, coordinated physical planning, and safe reuse of probe computations.

## Repository layout

| Location | Contents |
| --- | --- |
| `artifact/DiSMC-source-20261102.zip` | Java/Spark implementation, build and launch scripts, regression tests, and five-point example (source archive) |
| `supplementary/supplementary.pdf` | Supplementary experimental protocols, detailed measurements, and correctness arguments |
| `docs/REPRODUCIBILITY.md` | Environment requirements, building, checks, and execution notes |
| `docs/EXPERIMENT_INDEX.md` | Guide to the main-paper experimental results |
| `data/README.md` | Dataset provenance and preparation protocol |

The archive and PDF paths above are the intended locations for the corresponding release files. See the repository file list to confirm which files are currently available.

## Quick start

The supplied source archive is structured as a Maven-compatible Java project. After extracting it into `DiSMC-source/`, use a Linux or compatible Bash environment with **JDK 8** and **Apache Spark 3.2.0 (Scala 2.12)**.

```bash
cd DiSMC-source
export JAVA_HOME=/path/to/jdk8
export SPARK_HOME=/path/to/spark-3.2.0
bash build.sh
bash scripts/check_selected.sh
bash scripts/run_small_online.sh /absolute/new/output/diSMC-small.txt
```

The synthetic example is a local `local[2]` test and requests a 5% additional-input record budget. Use a new output path for each run.

For cluster execution, set `SPARK_HOME`, `SPARK_MASTER`, resource limits, and the query coordinates explicitly. Consult the source archive's launcher README and `docs/REPRODUCIBILITY.md` for the available method profiles.

## Evaluation guide

The main paper presents full-query comparisons, distributed baselines, scalability experiments, dependency-input controls, planner controls, and probe-reuse controls. `docs/EXPERIMENT_INDEX.md` maps these groups to the manuscript figures. The supplementary PDF records the detailed measurement protocols and associated tables.

## Data

GeoLife and TDrive use prepared two-dimensional coordinates derived from their respective trajectory collections. The preparation convention and reproducibility notes are documented in `data/README.md`. Raw third-party datasets are not redistributed through this repository unless their distribution terms permit it.

## Version identification

The source archive is identified by its 2026-11-02 release label and contains `SOURCE_MANIFEST.json` and `VERIFICATION.json`. The main paper's experimental conditions and any source-release regression checks should be interpreted according to their stated protocols.

## Citation

If you use this artifact, please cite:

*DiSMC: Dependency-Complete Planning for Distributed Skyline Micro-Cluster Queries.*

