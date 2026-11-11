# Experimental settings and scope registry

Dataset settings, query parameters and evaluation protocols below follow the DiSMC paper and supplementary experiment registry.

## Common environment and interpretation

- Spark **3.2.0** / Scala **2.12** and Java **1.8.0_211**.
- Five KVM workers, each 12 vCPUs and 19.61–23.47 GiB of guest memory. Four expose an Intel Xeon E5-2420 (1.90 GHz), one a generic QEMU CPU model.
- Unless varied: **40 requested executor cores**, **4 cores / 4 GiB per executor**, **200 logical owners**, **k = 2**, with locality waiting disabled. The online planner and full-data runs use an **8 GiB driver**; component controls may use a **4 GiB driver**.
- GeoLife and TDrive prepared coordinates are projected to EPSG:32650, rounded to 0.001 m, globally deduplicated, and translated by subtracting dataset minima. Fixed nested reservoir seeds: **GeoLife 20260925**, **TDrive 20260924**.
- **Complete online E2E** measures acquisition, probing, planning, routing, formal execution, reduction and member output. **Frozen-state replay** measures replay after capture; **component diagnostics** report individual stages. Each timing is interpreted within its designated boundary.
- The budget represents **additional task-input record assignments relative to the initial owner input population** (`B = floor(fraction × R0)`), rather than transmitted bytes or peak memory.
- The standard online configuration uses **5%**; full-data runs use **10%**; frozen-state comparisons use the captured plan.

## Main-paper figure/table matrix

| Paper | Dataset / prepared points | Query and radius | Budget | Measurement / extra control | Command status |
| --- | --- | --- | --- | --- | --- |
| Fig. 4 | GeoLife 3M; TDrive 3M | Four fixed q20/q40/q60/q80 positions; r=100/300 | 5% | DiSMC vs Static-Greedy; 3 online trials each arm; mean ± sample SD; 40 cores | DiSMC uses sampled_peak/joint_peak; Static-Greedy uses peak/work_greedy and disables online probes and reuse; coordinates are in `fixed-query-coordinates.csv` |
| Fig. 5 | Same as Fig. 4 | Same 8 queries | Same | Stage decomposition of the **same 48 runs**, not new trials | Derive from Fig. 4 run-stage records |
| Fig. 6 | GeoLife 1M; TDrive 3M | External q=(15,15), r=20/75 | 5% for DiSMC | Grid/Hilbert/Z-order, assembled spatial operators and DiSMC; complete E2E median of 3 | Run `fig6` for Grid/Hilbert/Z, DiSMC and assembled operator via separate released-source adapter; compare current implementation outputs |
| Fig. 7 | GeoLife 1M; TDrive 1M | Sparse/medium/dense coordinates; r=20/75 | As original system protocol | DiSMC vs assembled spatial operators; median of 3 | Run `fig7` with both DiSMC and assembled spatial operator; fixed positions from `fixed-query-coordinates.csv` |
| Fig. 8 | GeoLife/TDrive/Porto 100K–1M | External q=(15,15); r=20/75/20 | Profile-specific | Single-threaded ESMC (4 GiB JVM heap, 7200 s timeout) vs 40-core DiSMC; 3-run median | `single_esmc` and `hilbert_full` represent the paper's single-thread versus 40-core scale-out comparison |
| Fig. 9 | GeoLife 3M; TDrive 3M | Dataset-specific medium q; r=60/200 | 5% | 8/16/24/32/40 executor cores; mean ± sample SD, 3 trials | Runner exposes dataset-specific medium-coordinate overrides and acquisition settings for matching the recorded configuration |
| Table I | GeoLife 18,355,282; TDrive 11,274,655 | GeoLife q=(124414.676,106577.117), r=20; TDrive q=(116808.495,114686.700), r=200 | **10%** | Full-data E2E, 3 serial trials, 40 cores, complete output | Use the default `artifact/dismc-source.zip` with `spark.skyline.shardReadBudget=0.10` and `spark.skyline.budgetDiagnostic=true`; budget allowance covered by the included validation checks |
| Fig. 10 | GeoLife 2M; TDrive 3M | Medium positions, base r0=20/75; multiples 0.75/1/1.5 | 5% | Full-parent vs Dependency; matched acquisition/work/Engine; three-run E2E medians | Matched-information comparison toggles `microPartitionMode=spatial_full/dependency` with shared acquired inputs and work observations |
| Fig. 11a | GeoLife 2M; TDrive 3M | Medium positions, r=40/150 | 5% | Private-only vs paired-parent calibration; three online runs; mean ± SD | Use both refresh and lane refinement; `microLaneParentReplay=false/true` toggles private-only/paired-parent |
| Fig. 11b | GeoLife 2M; TDrive 2M | Medium positions, r=40/40 | 5% | Joint vs Greedy *fixed owner/task-order replay*; 3 replays; capture excluded | Run `fig11b`: capture one state per dataset, then three replay trials for both selectors (acquisition outside replay) |
| Fig. 12 | GeoLife 2M; TDrive 3M | Matched work-signal control | 5% | Unit/Static/Sampled with identical acquired information; E2E median and longest formal task | Use `fig12` for Unit/Static/Sampled modes; matched-information comparisons use a common acquired candidate/probe state |
| Fig. 13 | Frozen GeoLife/TDrive inputs | q=(15,15), fixed query | Frozen | Four (R,W) reuse combinations; three-run E2E means | Run `fig13`: capture one state, then four R/W combinations over three replay trials per dataset |
| Fig. 14 | Same frozen inputs as Fig. 13 | Same query | Frozen | Task-summed formal generation/counting checks from Fig. 13's runs | **No new execution**; `fig14` sums Fig. 13 `.micro_tasks.csv` checks |

The [supplementary PDF](../supplementary/dismc-supplementary.pdf) additionally reports input policy, query-position robustness, counting resolution (λ=0.5/1/2/4), parameter sensitivity, selector diagnostics, and original ESMC datasets.

## Parameter matching notes

The recorded datasets, sample hashes, query coordinates and frozen-state identities identify individual experimental runs. Where a paper workload is specified by a symbolic medium position or a fixed acquired state, use the corresponding recorded input or state to match that run. The provided command matrix documents the published values and exposes overrides for these controls.

See the [run instructions](run-commands.md) for commands and the distinction between native online and fixed-information comparisons.
