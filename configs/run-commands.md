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

Select one figure or table per command. Each entry may invoke multiple Spark trials. `fig5` uses the stage records from Fig. 4.

The exact dataset sizes, query positions, radii, input budgets, resource counts and timing boundaries for each figure are tabulated in [experiment-settings.md](experiment-settings.md). Fixed published queries are in [fixed-query-coordinates.csv](fixed-query-coordinates.csv).

## Method settings

- **DiSMC:** `hilbert_full`, native `sampled_peak` planner and `joint_peak` selector.
- **Static-Greedy (Fig. 4):** `peak` planner and `work_greedy` selector, with online probe, frontier transfer and completion reuse disabled. The static comparator uses a separate planner policy from DiSMC.
- **Other distributed baselines:** `grid_d0`, `hilbert_d0`, `z_d0`. Single-machine ESMC uses `single_esmc` (4 GiB JVM heap; 7,200 s timeout in Fig. 8).
- **Fig. 6–7 spatial operator:** `configs/run_spatial_operator.sh` invokes the released assembled `com.SpatialOperatorPipeline` implementation via a Spark adapter and exports complete members. The paper also reports a separately implemented historical streaming variant.
- **Fig. 10:** `spatial_full` versus `dependency` input organization.
- **Fig. 11(a):** both candidate refresh and lane refinement must be enabled; private versus paired-parent is selected by `microLaneParentReplay`.
- **Fig. 11(b):** capture once per dataset, then replay Joint and Greedy on the same frozen state for three trials.
- **Fig. 13:** capture once and replay four R/W combinations for three trials, using the same captured state. The capture configuration permits up to 192 anchors; the generated state records the actual selection.
- **Fig. 14:** derive check counts from Fig. 13 `*.micro_tasks.csv` via `configs/derive_fig14.py`; no new Spark query.

## Matching the paper's measurement protocols

**Fig. 12 — signal controls.** The supplied `unit`, `static` and `sampled` entries measure their respective native online configurations. The paper's matched-information experiment uses common acquired candidates and probe IDs across signals. For that protocol, retain the same captured information across comparison arms and check candidate/probe identities before interpreting measurements as matched.

**Medium positions (`qM`).** The runner accepts `MEDIUM_GEOLIFE_X`, `MEDIUM_GEOLIFE_Y`, `MEDIUM_TDRIVE_X` and `MEDIUM_TDRIVE_Y`. Defaults are documented representative medium positions; exact reproduction of an original run uses its recorded coordinates.

**Timing.** Complete online E2E, frozen replay and component diagnostics have separate measurement boundaries. The [aggregate CSVs](../results/README.md) record the values reported in the paper.
