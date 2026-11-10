# DiSMC Artifact — release checklist

**Status (2026-11-11):** Source and supplementary documents have been prepared locally, but the binary files are **not yet uploaded**. The repository remains **Private**.

## Required file uploads

| Repository path | Size (bytes) | SHA-256 |
| --- | ---: | --- |
| `artifact/DiSMC-source-20261102-release.zip` | 317963 | `40171c00e8c1d92c543560e084e9646897336ec7bff2c3d856f57a57d2e7c92e` |
| `supplementary/DiSMC-supplementary-20261110.pdf` | 356472 | `a4f92431326f58ddcebf7d4097c66b6923ab7268c3c809246f697ae6b7fc5c6f` |

**No separate Table IX ZIP is required for this release.** Its reported results already appear in the supplementary PDF and the aggregate result CSV. The raw records were supplied for manuscript verification, not as a third compulsory publication artifact.

## Other repository content (already organized)

- `README.md`, `docs/INSTALL.md`, `docs/REPRODUCIBILITY.md`: overview, environment, build, smoke and selected tests.
- `configs/`: experiment settings, command templates and coordinates.
- `data/`: dataset sources, reference preprocessing and test code.
- `results/`: paper-reported aggregates, their scope and limits.
- `docs/EXPERIMENT_INDEX.md`: figure/table navigation.

## Validate before release

1. Upload only the **two required binaries**, without replacing existing documentation or results.
2. Download each file from GitHub and verify its SHA-256 against this checklist.
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
