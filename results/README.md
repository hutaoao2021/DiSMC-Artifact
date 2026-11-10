# DiSMC experimental results

This directory publishes **machine-readable paper-reported aggregate results** across the main evaluation. The CSVs are transcriptions of the final manuscript/supplementary numerical arrays and plotting data. **They are not newly rerun Spark results**, nor do they replace full raw per-trial logs.

## Data files and measurement meaning

| File | Paper location | Meaning |
| --- | --- | --- |
| [`online_fixed_queries.csv`](online_fixed_queries.csv) | Main Fig. 4 | DiSMC vs **same-resource** Static-Greedy: 8 fixed queries × 2 methods; 3-run **mean and sample SD**, complete online E2E |
| [`esmc_scaleout.csv`](esmc_scaleout.csv) | Main Fig. 8 | DiSMC (40 executor cores) vs **single-threaded** ESMC; 3-run E2E medians, with 7200-s censored timeouts |
| [`core_scaling.csv`](core_scaling.csv) | Main Fig. 9 | GeoLife/TDrive executor-core sweep; 3-run **mean and sample SD**, complete online E2E |
| [`input_policy.csv`](input_policy.csv) | Main Fig. 10 / Supplement input-policy table | Full-parent vs Dependency at *matched acquisition/work/Engine*, 3-run **medians**. Different selected plans are allowed. |
| [`full_data.csv`](full_data.csv) | Main Table I | Complete-output GeoLife/TDrive **10% cap** runs, 3-run **mean and sample SD** |
| [`table_ix_5pct.csv`](table_ix_5pct.csv) | Supplement **Table IX** | Distinct **5% fixed-responsibility budget-feasibility diagnostic** from raw records, not the Fig. 10 E2E comparison |
| [`table_ix_5pct/README.md`](table_ix_5pct/README.md) | Supplement Table IX | Optional verification note for the supplementary budget diagnostic; no standalone evidence ZIP is required |

For the complete experiment matrix, see [`configs/experiment-settings.md`](../configs/experiment-settings.md) and the [experiment index](../docs/EXPERIMENT_INDEX.md). The final 18-page supplementary PDF has additional tables and the definitions of controls not transcribed as separate CSVs here. **Not every figure is represented by a standalone numeric CSV**, and CSV presence must not be interpreted as full raw-log availability.

## Strict interpretation notes

1. **Measured vs reported:** Main-figure CSV numbers were read from the final paper's plotting arrays/tables. They are published **aggregates** with the stated protocol and are not outputs of a new run using the 2026-11-02 integrated source.
2. **Timeouts are censored:** For rows with `esmc_censored_timeout=true`, the `esmc_value_s=7200` value is a **lower bound**. Never treat it as the measured ESMC completion time, compute an exact speedup from it, or include it as an uncensored observation in a mean.
3. **Different resources:** ESMC is single-threaded (4 GiB JVM heap); DiSMC uses 40 requested executor cores. Fig. 8 represents *complete-system scale-out*, not a same-resource algorithmic speedup.
4. **Sampling and statistics:** `mean_e2e_s` and `sample_sd_s` represent three trials where present; `median_e2e_s` values have no implied SD. Stage totals/fixed-state replays use their own timing boundaries and must not be mixed.
5. **Budgets:** Main Table I full-data runs use **10%**. Standard online and mechanism conditions generally use **5%**, but check the per-file scope. Additional input assignment budgets are **not network bytes**.
6. **Table IX Full-parent charge is not Full-parent E2E:** Table IX ran **one complete Dependency query per dataset**. Under matched selected responsibilities, the over-budget Full-parent alternative was accounted for **without running or timing that alternative**.
7. **Historical build boundary:** Paper-reported large-scale results were collected under their historical source/configuration. The 2026-11-02 integrated source includes later numerical corrections and has **not** rerun the entire performance suite. Do not claim byte-identical results without the historical prepared input hashes and complete configuration.

## What is and is not verified

- The numeric values in the CSVs are matched to the **final manuscript/source plotting arrays** and the supplement.
- The reported supplementary Table IX charges were checked separately using author-provided per-owner records during manuscript preparation. A raw-record ZIP is **not** a required release deliverable.
- We have **not** independently executed the entire large-scale Spark experiment suite or acquired all original dataset hashes as part of this release preparation.
- The main source ZIP and final supplementary PDF are uploaded to the **Public** repository. Their recorded Git blobs match locally checked files; independent signed-out download verification remains pending.

## Validation guide

To check the published CSV scopes, compare each row with the figure/table caption and the [configuration registry](../configs/experiment-settings.md). For the supplementary Table IX metric boundary, see [the short verification note](table_ix_5pct/README.md). For launching a fresh run, see [source-backed commands](../configs/run-commands.md); the smoke test is a functionality check, not a performance reproduction.
