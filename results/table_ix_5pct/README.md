# Table IX: fixed-responsibility 5% record-fee diagnostic

This case is **separate from** main-paper Fig. 10's three-run Full-parent/Dependency **online E2E** comparison. The matched-responsibility case reported in supplementary **Table IX** has one complete Dependency execution per dataset and a counterfactual Full-parent record-charge computation on the **same responsibilities**.

## Already supplied original record archive

**Local original from the authors:** `DiSMC_TableIX_5pct_raw_records_20261110.zip`

- SHA-256: `d7479212e63386e68cd4050cf4eb8ca221c13d603a96416b289a400f7f60ebb2`
- Contents: `tableIX_formal5_20261110/` with `geolife/`, `tdrive/`, `summary.json`, `tableIX_5pct.csv`, `verify_records.py`, `protocol.json`, and per-dataset record files.
- **GitHub publication status: pending binary archive upload and privacy/path screening.** The checksum describes the *received original*, not a file already downloadable from this repository.

The original `executed_command.sh` and some logs contain **internal absolute paths and a private-network address**. Those paths are not required to understand the metric and must be parameterized/redacted before public release. If a *sanitized* ZIP is published, its SHA-256 will be different and must be recorded separately.

**Prepared public evidence ZIP (pending upload):** `DiSMC_TableIX_5pct_public_records.zip`, SHA-256 `8382d80aad038d81075c5e986fac0f1ada8d9ba0ae8b8b10a1e7a03494cf2a89`. This derivative preserves original per-owner candidate records, per-task input populations, original selected plans and original accounting data, but **excludes sensitive commands, logs and observation/manifest payloads**. Its two regenerated SHA-256 manifests cover the included files. The supplied original verifier was run on the derivative and passed for both datasets. The prepared file exists as a local artifact; it has **not yet been uploaded to GitHub**.

## Query and outcome

| Parameter | GeoLife | TDrive |
| --- | ---: | ---: |
| Prepared data points | 2,000,000 | 3,000,000 |
| Query (x,y) | (15,15) | (15,15) |
| Radius | 20 m | 75 m |
| k / owners / requested cores | 2 / 200 / 40 | 2 / 200 / 40 |
| Initially assigned owner inputs, `R0` | 3,606,291 | 5,308,365 |
| 5% budget `B=floor(0.05×R0)` | 180,314 | 265,418 |
| Selected physical tasks | 226 | 270 |
| Split owners | 14 | 16 |
| **Full-parent computed extra assignments** | 308,095 | 983,097 |
| **Dependency measured extra assignments** | 174,393 | 259,343 |
| Dependency budget use | 96.72% | 97.71% |
| Saved charge relative to Full-parent | 43.40% | 73.62% |

Only the Dependency plan was executed (one run per dataset). The original summaries additionally record 92.120 s and 83.793 s for these Dependency runs; **there is no Full-parent runtime** for the over-budget alternative. Do not compare these single-run diagnostics to the three-run online Fig. 10 medians.

## Verification with the original ZIP

After making the archive available locally:

```bash
unzip DiSMC_TableIX_5pct_raw_records_20261110.zip -d table_ix_raw
python table_ix_raw/tableIX_formal5_20261110/verify_records.py
```

The script provided *inside that ZIP* checks file SHA-256 values against `raw_record_manifest.json`, checks each selected plan checksum, aggregates exact per-owner charges and cross-checks selected task-input populations. Its key arithmetic definitions are:

```text
R0 = sum_owner(parent_input_records[owner])
B = floor(0.05 * R0)
full_charge = sum_owner((num_tasks[owner]-1) * parent_input_records[owner])
dependency_charge =
    sum_owner(max(0, sum_task(input_records[owner,task])
                     - parent_input_records[owner]))
saved_fraction = 1 - dependency_charge / full_charge
utilization_fraction = dependency_charge / B
```

**Important:** compute `max(0, ·)` *per owner before summing*. The globally subtracted input sum is not generally identical because the accounting charge is clipped by owner.

The original verification script and 200-owner fee CSVs belong to the prepared raw ZIP; the compact [table](../table_ix_5pct.csv) is a verified *summary*, not a replacement for those files.

## Provenance boundary

The raw records reflect a historical Spark execution with specific prepared data hashes, runner settings and a frozen responsibility mapping. The 2026-11-02 integrated source can express the core 5% Micro-Partition flags but a generic command template alone does not recreate the precise selected plan or original run. See [source-checked flags](../../configs/run-commands.md).
