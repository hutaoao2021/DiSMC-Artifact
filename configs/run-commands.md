# Reproduce DiSMC experiments

All commands below run **from the repository root**, after the source ZIP has been extracted and built, and the datasets prepared as described in the [README](../README.md).

## Requirements

- JDK 8; Spark 3.2.0 / Scala 2.12; Linux/Bash
- For data preparation: Python 3, `pyproj` and GNU `sort`
- Reported cluster configuration: five workers; 40 requested executor cores, 4 cores / 4 GiB per executor, 200 logical owners, and normally an 8 GiB driver
- Each result path must be new; the scripts refuse to overwrite existing results

```bash
export JAVA_HOME=/path/to/jdk8
export PATH="$JAVA_HOME/bin:$PATH"
export SPARK_HOME=/path/to/spark-3.2.0
export SPARK_MASTER=spark://your-master:7077
export DATA_DIR="$PWD/data/historical/reproduction"
export OUT_DIR="$PWD/results/reproduction-$(date +%Y%m%d-%H%M%S)"
export TOTAL_EXECUTOR_CORES=40
export EXECUTOR_CORES=4
export EXECUTOR_MEMORY=4G
export DRIVER_MEMORY=8G
```

The dataset workspace supports `prepared/{dataset}_xy.txt` for full inputs and `subsets/{dataset}_{size}_xy.txt` for sampled inputs. To generate the 100K–800K size-sweep inputs and the 2M prefixes from the existing fixed samples:

```bash
DATA_DIR="$PWD/data/historical/reproduction" bash configs/prepare_paper_subsets.sh
```

## Figure and table commands

Preview an exact command without launching Spark:

```bash
DRY_RUN=1 TRIALS=3 bash configs/run_paper_suite.sh fig4
```

To execute one experiment, replace `fig4` with any entry below:

```bash
TRIALS=3 bash configs/run_paper_suite.sh fig4
TRIALS=3 bash configs/run_paper_suite.sh fig6
TRIALS=3 bash configs/run_paper_suite.sh fig7
TRIALS=3 bash configs/run_paper_suite.sh fig8
TRIALS=3 bash configs/run_paper_suite.sh fig9
TRIALS=3 bash configs/run_paper_suite.sh table1
TRIALS=3 bash configs/run_paper_suite.sh fig10
TRIALS=3 bash configs/run_paper_suite.sh fig11a
TRIALS=3 bash configs/run_paper_suite.sh fig11b
TRIALS=3 bash configs/run_paper_suite.sh fig12
TRIALS=3 bash configs/run_paper_suite.sh fig13
bash configs/run_paper_suite.sh fig14
```

These are **individual alternatives**, not a recommendation to run the full sequence as a short smoke test. Each may require several full-data Spark runs. `fig5` uses Fig. 4 stage records and does not launch a new query.

The exact dataset sizes, query positions, radii, input budgets, resource counts and timing boundaries for each figure are tabulated in [experiment-settings.md](experiment-settings.md). Fixed published queries are in [fixed-query-coordinates.csv](fixed-query-coordinates.csv).

## Method settings

- **DiSMC:** `hilbert_full`, native `sampled_peak` planner and `joint_peak` selector.
- **Static-Greedy (Fig. 4):** `peak` planner, `work_greedy` selector and no online probe/frontier/completion reuse. Merely switching selector with `sampled_peak` active is **not** this baseline.
- **Other distributed baselines:** `grid_d0`, `hilbert_d0`, `z_d0`. Single-machine ESMC uses `single_esmc` (4 GiB JVM heap; 7,200 s timeout in Fig. 8).
- **Fig. 6–7 spatial operator:** `configs/run_spatial_operator.sh` builds a small adapter against the existing `com.SpatialOperatorPipeline`, runs it in Spark and exports full members. It is **not** the original historical streaming operator executable.
- **Fig. 10:** `spatial_full` versus `dependency` input organization.
- **Fig. 11(a):** both candidate refresh and lane refinement must be enabled; private versus paired-parent is selected by `microLaneParentReplay`.
- **Fig. 11(b):** capture once per dataset, then replay Joint and Greedy on the same frozen state for three trials.
- **Fig. 13:** capture once and replay four R/W combinations for three trials; the script bounds acquisition to a maximum of 192 anchors, which is **not** a claim that the historical completed identities are recovered.
- **Fig. 14:** derive check counts from Fig. 13 `*.micro_tasks.csv` via `configs/derive_fig14.py`; no new Spark query.

## Reproduction limits

**Fig. 12:** the available `unit`, `static` and `sampled` commands run independent acquisitions and have **not** been demonstrated to share identical candidates and probe IDs. Their outputs must not be represented as the paper's exact matched-information comparison.

**Dataset-specific medium `qM`:** some original numeric coordinates were not published. The runner exposes `MEDIUM_GEOLIFE_X`, `MEDIUM_GEOLIFE_Y`, `MEDIUM_TDRIVE_X` and `MEDIUM_TDRIVE_Y` overrides, defaulting to documented 1M medium examples rather than invented historical values.

**Timing:** online end-to-end measurements, frozen-state replay and component-only timings cover different operations and are not directly interchangeable. Reported [aggregate CSVs](../results/README.md) predate this repository packaging.
