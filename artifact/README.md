# Implementation archive

Expected file: `DiSMC-source-20261102-release.zip`.

The source archive is based on the 2026-11-02 integrated DiSMC Java/Spark release. It contains the application sources, Maven project, regression tests, build/launch scripts and a five-point synthetic fixture.

The release package leaves Java production and test sources unchanged while making the launcher environment configuration portable. `PUBLIC_PACKAGING_NOTES.md` inside the archive documents the packaging step.

**Reproducible input:** JDK 8; Spark 3.2.0 (Scala 2.12). See [the guide](../docs/REPRODUCIBILITY.md) for test and launch commands.

**Archive SHA-256:** `ac5b75689b3454a9e3c38ca986c311933cad4f5f5e9ff1595c6dfaccb75da047`

Download the ZIP and extract before running the build.
