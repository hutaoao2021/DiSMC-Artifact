# Release checklist — DiSMC research artifact

**Status (2026-11-11):** Markdown documentation and result CSVs are in the private repository; the three binary artifacts below are **prepared locally but not yet uploaded to GitHub**. Do **not** publicize or submit the GitHub URL as an accessible artifact before these steps finish.

## Required uploads, exact repository paths

| Repository path | Size in bytes | SHA-256 |
| --- | ---: | --- |
| `artifact/DiSMC-source-20261102-release.zip` | 317963 | `40171c00e8c1d92c543560e084e9646897336ec7bff2c3d856f57a57d2e7c92e` |
| `supplementary/DiSMC-supplementary-20261110.pdf` | 356472 | `a4f92431326f58ddcebf7d4097c66b6923ab7268c3c809246f697ae6b7fc5c6f` |
| `results/table_ix_5pct/DiSMC_TableIX_5pct_public_records.zip` | 217767 | `8382d80aad038d81075c5e986fac0f1ada8d9ba0ae8b8b10a1e7a03494cf2a89` |

These hashes correspond to the author-prepared final binaries. Uploading to GitHub must not change their bytes.

## Validate the repository **before** making it public

1. Download each uploaded artifact and compute SHA-256 locally; compare with the hashes above.
2. Check the source ZIP opens and contains `DiSMC-source/build.sh`, `pom.xml`, and `scripts/run_small_online.sh`.
3. Open the supplementary PDF and confirm **18 pages**, latest Table IX (5% diagnostic), and main-paper terminology.
4. Extract the **public** Table IX ZIP, then run `python tableIX_formal5_20261110/verify_records.py` from the extraction directory; expect `geolife PASS` and `tdrive PASS`.
5. Confirm GitHub Markdown links in `README.md`, `docs/INSTALL.md`, `docs/REPRODUCIBILITY.md`, `data/README.md`, `configs/`, and `results/` work.
6. Review sensitive information. The sanitized Table IX ZIP excludes internal commands, logs, IPs and run manifests. Do not upload the original unredacted `DiSMC_TableIX_5pct_raw_records_20261110.zip`.
7. The source's small smoke and regression tests require JDK 8 and Spark 3.2.0. A static/script audit is **not** equivalent to a successful independent Spark execution. Record any remaining real-environment test limitations transparently.
8. Consider adding a source license **only if all rights holders agree**; a license is not automatically granted by repository visibility.
9. Authorize the public release with all coauthors, and then change repository visibility to **Public**.
10. Test a raw file URL in a browser where you are **not logged into GitHub**; make sure an anonymous reader can download each binary.
11. Only after the above: put `https://github.com/hutaoao2021/DiSMC-Artifact` in the CMT Availability field and replace any text saying the package is still being finalized.

## Distinctions important to paper accuracy

- Main paper CMT upload remains the separate `DiSMC.pdf` file; the supplementary PDF is in this artifact repo.
- Main Table I full-data experiments report a 10% extra-input cap; current integrated Micro-Partition config rejects a direct 10% flag substitution.
- `results/*.csv` stores final **paper-reported aggregates**, not freshly regenerated raw Spark trials.
- A five-point smoke query is a functionality check, not proof of all reported performance.
- ESMC rows censored at 7200 s are lower bounds, not measured completion times.
