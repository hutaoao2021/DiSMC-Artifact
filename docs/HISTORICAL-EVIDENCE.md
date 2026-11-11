# Historical experiment command archive (optional reference)

The [command index](../configs/historical-command-index.csv) links **119 archived command files** to execution arguments, recorded environment/configuration, input/build hashes, and available result-manifest fields. These records are supplementary provenance for earlier runs and development checks. To reproduce the paper, follow the current [experiment commands](../configs/run-commands.md) and [parameter matrix](../configs/experiment-settings.md).

Original commands, logs and source files were not changed. Storage roots, account-specific installation paths and network endpoints are substituted in distributed records. Original file SHA-256 values identify the unredacted private originals; distributed JSON/file hashes identify the redacted copies separately. No raw trajectories or member-coordinate output are published here.

## Coverage of requested figures and table

| Target | Recovery status | Evidence and remaining boundary |
|---|---|---|
| **Fig. 4** | **Recorded argv + environment + results: 48/48** | `large_radius_three_rounds_20261018`: GeoLife/TDrive 3M, r=100/300, 4 fixed queries, DiSMC/Static-Greedy, 3 trials, 5% cap. Per-trial CSV is recomputed against existing reported aggregates. Input and recorded JAR hashes retained. |
| **Fig. 10** | **Partial: historical input-policy commands recovered; final 5% series not bound** | Earlier input-policy and TDrive mechanism runs contain recorded **1%** commands. They are antecedents, not proof of the final 5% figure, its radius sweep or final aggregate values. The 2026-11-10 5% fixed-responsibility accounting experiment is a separate supplement table and must not be substituted. |
| **Fig. 11a** | **Reported settings/measurements; historical executed commands not located** | Local manuscript-update records contain author-supplied paired-calibration repetitions. These do not establish the exact executed argv, environment, input hash or build for each trial. Existing command templates remain templates. |
| **Fig. 11b** | **Partial: 5% frozen-state antecedent commands recovered** | `accept_validation_5pct_20261023/attempt3`, medium-query capture and three replays/arm, preserve frozen-state hashes and common control settings. Their actual timings differ from the final figure, and TDrive uses **3M** rather than the reported **2M, r=40** replacement batch. They are not relabelled as the replacement runs. |
| **Fig. 12** | **Partial: matched-information antecedents recovered** | GeoLife/TDrive unit/static/sampled command records and responsibility replay references located; recovered commands use **1%**. A final 5% run-to-figure binding is not established. Shared runs may also support earlier input-policy diagnostics; the index states this overlap. |
| **Fig. 13** | **Partial: 24 historical factorial commands recovered** | Fixed-plan Completion/Witness commands, replay references and result manifests recovered. They explicitly use **1%**. Final 5% replacements, if used for the published figure, still require their own records. |
| **Table I — TDrive** | **Recorded argv + environment + results: 3/3** | `tdrive_full_r200_budget10_once_20261018` and `...repeat23_20261019`; 11,274,655 points, r=200, q=(116808.495,114686.700), k=2, 200 owners, 40 cores, 10%. Recorded input/JAR identities and three E2E values retained. |
| **Table I — GeoLife** | **Profiled trial recovered; full three-trial binding incomplete** | `geolife_tail_budget10_20261015/full`: 18,355,282 points, r=20, q=(124414.676,106577.117), k=2, 200 owners, 40 cores, 10%; E2E **2758.206 s**, 259 tasks. Its historical JAR differs from the TDrive build. Two additional reported E2Es (**2682.821**, **2893.186 s**) lack recovered per-trial commands/logs. Other GeoLife full-data commands in the index produce different E2Es and are not substituted. |

“Not located” describes this bounded recovery pass, not proof that a file never existed. It is possible to close these entries with the original files; changing the old records' budget labels would not close them.

## What the records mean

- **Recorded command:** the recovered original JSON argv, together with its original SHA-256. Where stored, its original environment is included. A `status=prepared` or `running` field is not treated as completion evidence; an available result manifest supplies a separate completion observation.
- **Partial environment / reconstruction:** some old files store an argv list only. The wrapper and result manifest help describe settings, but absent environment variables remain unknown. The current wrapper hash is distinguished from the historically recorded JAR hash.
- **Paper-reported only:** the experiment registry and plotted CSVs describe reported protocols; they do not supply missing historical commands or trial logs. No argv is synthesized from a result value.
- **Current rehash:** a file hash computed during this recovery pass is not silently presented as a hash captured when the old run started. Recorded hashes and current rehashes are separate fields.
- **Timing:** Fig. 4 and Table I are complete-query E2E records. Frozen-state replays exclude acquisition/capture. Do not mix these measurements.

The JSON preserves explicit Spark flags (master redacted), resources, query environment, radius, k, budget, probe/cache switches, replay/frozen-state paths and hashes when available. Installation-specific paths can be mapped to your own workspace, but historical wrappers/JARs are separate from the integrated-source candidate.

## Data and source identities

See [recovered historical preprocessing](../data/historical/README.md) for actual ordering, seed/RNG details and raw/prepared/subset hashes. The later reference converter remains available and distinctly labelled.

Historical large-radius/TDrive full-data JAR: `fa03bf111aaca953d8cb78c3d185292a1f60b56c2dbfbc6d4022fa11645da5df`.

GeoLife Table I profiled JAR: `6b0759cfc6103db6165fac85e6ba8b569ce3488ae7e6ccf819a016b544e41b21`.

Frozen-state antecedent JAR: `ca5e66e04b9aa1172dcafbe3a36f2bca1a22a4596504276a0457c87278ceeb1d`.

The repository's 2026-11-02 integrated code includes subsequent numerical changes. The [validated 10% candidate](BUDGET10-VALIDATION.md) demonstrates a narrowly scoped compatible budget allowance and a synthetic Micro-Partition query. Neither file is asserted to reproduce the historical JAR byte-for-byte or all Table I timings.

## Recheck distributed evidence

```bash
python3 tools/check_recovered_evidence.py
```

This verifies original-release preservation, candidate source-file hashes, preprocessing distributed-file hashes, Fig. 4 repetition counts/aggregate arithmetic, recorded-vs-current Fig. 4 input/JAR hashes and the TDrive Table I mean/SD. It does not execute the full historical workloads.
