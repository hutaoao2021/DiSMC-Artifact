# DiSMC — Research Artifact

**DiSMC: Dependency-Complete Planning for Distributed Skyline Micro-Cluster Queries**

This repository is being prepared for the DiSMC research-paper artifact. The implementation is a Java/Spark system for distributed skyline micro-cluster queries with dependency-complete task inputs, joint physical planning, and safe reuse of completed probe work.

> **Release status (2026-11-10):** The source ZIP and supplementary PDF listed below have **not yet been uploaded to this repository**. The repository is currently private and should not be presented as a complete, publicly accessible artifact. The documentation below describes the intended release layout.

## Package index

| Path | Purpose |
| --- | --- |
| `artifact/DiSMC-source-20261102-release.zip` | Integrated Java/Spark source, tests, launch scripts, and five-point fixture (**pending upload**) |
| `supplementary/DiSMC-supplementary-20261110.pdf` | Final supplementary technical document (**pending upload**) |
| [`docs/INSTALL.md`](docs/INSTALL.md) | Software requirements, compilation, selected regression checks, and smoke test |
| [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) | Execution modes, configuration boundaries, provenance and validation scope |
| [`docs/EXPERIMENT_INDEX.md`](docs/EXPERIMENT_INDEX.md) | Navigation from paper figures and tables to experiment categories |
| [`configs/experiment-settings.md`](configs/experiment-settings.md) | Paper-specific workload, budget, query and measurement registry |
| [`configs/run-commands.md`](configs/run-commands.md) | Source-backed launcher syntax, templates and known configuration limitations |
| [`configs/fixed-query-coordinates.csv`](configs/fixed-query-coordinates.csv) | Eight fixed online queries, positional controls and full-data coordinates |
| [`results/README.md`](results/README.md) | Paper-reported aggregate results and their interpretation limits |
| [`docs/RELEASE_CHECKLIST.md`](docs/RELEASE_CHECKLIST.md) | Two required binary upload paths, checksums and public-access verification checklist |
| [`data/README.md`](data/README.md) | Dataset sources, input preparation and redistribution limitations |

## Quick start

The packaged source archive extracts into a `DiSMC-source/` directory. On Linux or a compatible Bash environment with **JDK 8** and **Apache Spark 3.2.0 (Scala 2.12)**:

```bash
unzip artifact/DiSMC-source-20261102-release.zip
cd DiSMC-source
export JAVA_HOME=/path/to/jdk8
export PATH="$JAVA_HOME/bin:$PATH"
export SPARK_HOME=/path/to/spark-3.2.0

bash build.sh
bash scripts/check_selected.sh

OUT_DIR="$(mktemp -d)"
bash scripts/run_small_online.sh "$OUT_DIR/smoke.txt"
```

The last command uses the bundled five-point example, Spark `local[2]`, a 5% additional-input-record budget, and member export. It is a **small functionality check**, not a reproduction of the paper's large-scale performance results. Use a new output path for each run.

If Maven is installed, `build.sh` uses Maven; otherwise it compiles the Java sources with JDK tools and the Spark runtime JARs. The selected-check script requires `SPARK_HOME` in either case.

## Reproducing paper experiments

Use [the reproducibility guide](docs/REPRODUCIBILITY.md), [the experiment index](docs/EXPERIMENT_INDEX.md), and the [experiment settings](configs/experiment-settings.md) / [command templates](configs/run-commands.md), and the [published result tables](results/README.md) together. The paper distinguishes complete online end-to-end measurements, frozen-state replay, and component-only measurements. These scopes must not be mixed.

For clustered runs, set `SPARK_MASTER` and the executor/driver resources deliberately. The source launcher is `scripts/run_profile.sh`. Paper-scale parameters, data subset definitions and fully specified commands are being organized separately; the five-point smoke command is not an exact paper benchmark command.

The source is a **2026-11-02 integrated release** including the recorded numerical correction and portable shell packaging, not the byte-identical historical executable used for every published timing. Its bundled `VERIFICATION.json` reports earlier checks; the full paper performance suite has not been rerun with this integrated release.

## Data and supplementary materials

The repository does not redistribute third-party GeoLife or TDrive raw datasets. See [data preparation notes](data/README.md) for provenance and preprocessing conventions. The supplementary PDF supplies additional protocols, result tables, figures and correctness arguments.

## Citation

*DiSMC: Dependency-Complete Planning for Distributed Skyline Micro-Cluster Queries.*
