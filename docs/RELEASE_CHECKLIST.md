# DiSMC Artifact — release checklist

**Status (2026-11-11):** The source ZIP and supplementary PDF have been **uploaded** to the **Private** repository. Their Git blob hashes match the locally checked files. Public/anonymous download testing is still pending.

## Required uploaded files

| Repository path | Size (bytes) | SHA-256 |
| --- | ---: | --- |
| `artifact/DiSMC-source-20261102-release.zip` | 317963 | `40171c00e8c1d92c543560e084e9646897336ec7bff2c3d856f57a57d2e7c92e` |
| `supplementary/DiSMC-supplementary-20261110.pdf` | 356472 | `a4f92431326f58ddcebf7d4097c66b6923ab7268c3c809246f697ae6b7fc5c6f` |

**Table IX is supplementary, not a required principal release artifact.** A sanitized evidence ZIP has also been uploaded by the author at `results/table_ix_5pct/DiSMC_TableIX_5pct_public_records.zip`, with locally checked SHA-256 `8382d80aad038d81075c5e986fac0f1ada8d9ba0ae8b8b10a1e7a03494cf2a89`. Its presence does not change the two core deliverables.

## Other repository content (already organized)

- `README.md`, `docs/INSTALL.md`, `docs/REPRODUCIBILITY.md`: overview, environment, build, smoke and selected tests.
- `configs/`: experiment settings, command templates and coordinates.
- `data/`: dataset sources, reference preprocessing and test code.
- `results/`: paper-reported aggregates, their scope and limits.
- `docs/EXPERIMENT_INDEX.md`: figure/table navigation.

## Validate before release

1. **Completed:** both core binaries are present, and Git blob SHA-1 values match locally verified bytes. For an independent end-to-end check, download each file from GitHub and compare SHA-256 with this checklist.
2. **Completed:** the supplementary Table IX evidence file is also present, but is optional.
3. Verify the source ZIP contains a Maven project, build and smoke scripts; do not claim full Spark benchmarks were rerun by this release process.
4. Open the supplementary PDF and verify it has **18 pages**, including the updated 5% Table IX diagnostic.
5. Confirm README, documentation and result-file links. Check for secrets, credentials and private path disclosures.
6. Confirm coauthor approval and any source distribution rights; decide license separately.
7. Keep the repo Private until both file and documentation checks are complete. Only then, with authorization, change to Public.
8. After publication, confirm the files can be downloaded **without signing in**. Then update the CMT Availability field.

## Interpretation boundaries

- The CMT main paper PDF is separately submitted; it is not one of these two uploads.
- Main Table I full-input runs used a **10%** cap, while many other experiments used **5%**.
- Existing CSVs contain **paper-reported aggregates**, not fresh rerun Spark results.
- ESMC timeouts at 7200 s are censored lower bounds.
- The integrated source release has not been used to rerun every historical large-scale benchmark.
