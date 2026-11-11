# Experimental settings and scope registry

**Source of this registry:** the final 2026-11-10 DiSMC main paper and its 18-page supplement (especially the *Unified workload and acquisition registry*), cross-checked with the 2026-11-02 integrated Java/Spark source. These are **reported experimental conditions**, not a claim that every historical large-scale run has been reproduced with this source release.

## Common environment and interpretation

- Spark **3.2.0** / Scala **2.12** and Java **1.8.0_211**.
- Five KVM workers, each 12 vCPUs and 19.61–23.47 GiB of guest memory. Four expose an Intel Xeon E5-2420 (1.90 GHz), one a generic QEMU CPU model.
- Unless varied: **40 requested executor cores**, **4 cores / 4 GiB per executor**, **200 logical owners**, **k = 2**, with locality waiting disabled. The online planner and full-data runs use an **8 GiB driver**; component controls may use a **4 GiB driver**.
- GeoLife and TDrive prepared coordinates are projected to EPSG:32650, rounded to 0.001 m, globally deduplicated, and translated by subtracting dataset minima. Fixed nested reservoir seeds: **GeoLife 20260925**, **TDrive 20260924**.
- **Complete online E2E** includes acquisition/probing/planning/routing/formal execution/reduction/member output according to the paper protocol. **Frozen-state replay** excludes capture/reconstruction; **component diagnostics** are not whole-query E2E. These timings should never be pooled.
- The budget counts **additional task-input record assignments relative to the initial owner input population** (`B = floor(fraction × R0)`). It is not a network-byte or peak-RAM budget.
- Do **not** assume all runs used 5%: full-data runs used **10%**, while selected frozen-state controls use a fixed acquired plan.

## Reading this experiment index

The matrix below also serves as the manuscript's figure/table navigation index. **Overall efficiency:** Fig. 4 (same-resource DiSMC vs Static-Greedy), Fig. 5 (stage decomposition of those same runs), and Fig. 6–8 (distributed comparators, spatial-position robustness, and single-threaded ESMC scale-out). **Scalability and full data:** Fig. 9 and Table I. **Mechanism studies:** Fig. 10 (input organization), Fig. 11 (calibration and frozen-state selector replay), Fig. 12 (matched work signals), and Fig. 13–14 (probe-reuse E2E and task-level computation). This index describes *reported measurements*, not fresh reruns.

**Interpretation:** complete online E2E, fixed-state replay, and component-only measurements use different accounting boundaries; additional task-input record assignments are not network bytes or time. Budget fractions must be read from each experiment, not assumed to be globally 5%.

## Main-paper figure/table matrix

| Paper | Dataset / prepared points | Query and radius | Budget | Measurement / extra control | Command status |
| --- | --- | --- | --- | --- | --- |
| Fig. 4 | GeoLife 3M; TDrive 3M | Four fixed q20/q40/q60/q80 positions; r=100/300 | 5% | DiSMC vs Static-Greedy; 3 online trials each arm; mean ± sample SD; 40 cores | Use `hilbert_full` with `microSelector=joint_peak` (DiSMC) or `work_greedy` (greedy); coordinates are in `fixed-query-coordinates.csv` |
| Fig. 5 | Same as Fig. 4 | Same 8 queries | Same | Stage decomposition of the **same 48 runs**, not new trials | Derive from Fig. 4 run-stage records |
| Fig. 6 | GeoLife 1M; TDrive 3M | External q=(15,15), r=20/75 | 5% for DiSMC | Grid/Hilbert/Z-order, assembled spatial operators and DiSMC; complete E2E median of 3 | Legacy routing profiles have launcher names; assembled operator path must be separately identified |
| Fig. 7 | GeoLife 1M; TDrive 1M | Sparse/medium/dense coordinates; r=20/75 | As original system protocol | DiSMC vs assembled spatial operators; median of 3 | Coordinates in `fixed-query-coordinates.csv`; separate from 3M fixed online cohort |
| Fig. 8 | GeoLife/TDrive/Porto 100K–1M | External q=(15,15); r=20/75/20 | Profile-specific | Single-threaded ESMC (4 GiB JVM heap, 7200 s timeout) vs 40-core DiSMC; 3-run median | `single_esmc` and `hilbert_full` launch entries exist; do not interpret as same-resource speedup |
| Fig. 9 | GeoLife 3M; TDrive 3M | Dataset-specific medium q; r=60/200 | 5% | 8/16/24/32/40 executor cores; mean ± sample SD, 3 trials | Exact medium coordinates and fully matched acquisition flags must be supplied before exact rerun |
| Table I | GeoLife 18,355,282; TDrive 11,274,655 | GeoLife q=(124414.676,106577.117), r=20; TDrive q=(116808.495,114686.700), r=200 | **10%** | Full-data E2E, 3 serial trials, 40 cores, complete output | Supported by the release source; set `spark.skyline.shardReadBudget=0.10` and `spark.skyline.budgetDiagnostic=true` |
| Fig. 10 | GeoLife 2M; TDrive 3M | Medium positions, base r0=20/75; multiples 0.75/1/1.5 | 5% | Full-parent vs Dependency; matched acquisition/work/Engine; three-run E2E medians | Needs matched input-policy configuration; cannot be reproduced by changing only budget |
| Fig. 11a | GeoLife 2M; TDrive 3M | Medium positions, r=40/150 | 5% | Private-only vs paired-parent calibration; three online runs; mean ± SD | Dedicated paired-calibration settings required |
| Fig. 11b | GeoLife 2M; TDrive 2M | Medium positions, r=40/40 | 5% | Joint vs Greedy *fixed owner/task-order replay*; 3 replays; capture excluded | Requires frozen acquired state; do not present as online comparison |
| Fig. 12 | GeoLife 2M; TDrive 3M | Matched work-signal control | 5% | Unit/Static/Sampled with identical acquired information; E2E median and longest formal task | `microCostSignal` accepts `unit`/`static`/`sampled` only in compatible sampled-peak micro mode |
| Fig. 13 | Frozen GeoLife/TDrive inputs | q=(15,15), fixed query | Frozen | Four (R,W) reuse combinations; three-run E2E means | Requires identical responsibility/input/probe IDs across arms |
| Fig. 14 | Same frozen inputs as Fig. 13 | Same query | Frozen | Task-summed formal generation/counting checks from Fig. 13's runs | **No new execution**; derive from Fig. 13 task records |

The [supplementary PDF](../supplementary/DiSMC-supplementary-20261110.pdf) additionally reports input policy, query-position robustness, counting resolution (λ=0.5/1/2/4), parameter sensitivity, selector diagnostics, and original ESMC datasets.

## Limits of this registry

The supplement does not expose every frozen state, hash, medium-position query coordinate, or exact Spark option for every experiment in a single public machine-readable manifest. **Do not invent missing values**. A command template with known query/dataset parameters is useful for exercising the code, but it is not an independently verified reproduction of the paper's timing until its acquisition flags, build ID, data preparation and state inputs have also been matched.

For source-supported launcher options and examples, see [run commands](run-commands.md).
