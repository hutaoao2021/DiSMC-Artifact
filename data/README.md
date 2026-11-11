# Datasets and preparation for DiSMC

This document records the dataset sources and preparation rules in the **final DiSMC supplementary material**, and offers a **new reference converter**. It distinguishes documented historical settings from what the published source package can currently reproduce. The repository **does not redistribute raw trajectory data**.

## 1. Official sources

| Dataset | Provider and original form | Official access |
| --- | --- | --- |
| **GeoLife** | Microsoft Research Asia; user folders with GPS trajectory `.plt` files (latitude, longitude and other fields after six header lines) | [Microsoft GeoLife download](https://www.microsoft.com/en-us/download/details.aspx?id=52367) |
| **TDrive** | Microsoft Research Asia; taxi ID, timestamp, longitude, latitude in comma-separated files | [Microsoft T-Drive dataset page](https://www.microsoft.com/en-us/research/publication/t-drive-trajectory-data-sample/) |
| **Porto** | ECML/PKDD 2015 taxi trajectory challenge; `train.csv` containing a JSON-array `POLYLINE` field with `[longitude,latitude]` pairs | [UCI repository, dataset 339](https://archive.ics.uci.edu/dataset/339/taxi+service+trajectory+prediction+challenge+ecml+pkdd+2015) |
| **NE / CAS / TS** | Original ESMC benchmark two-dimensional point inputs, used without GeoLife/TDrive/Porto projection | Specific provider URLs and original input hashes **not established from the supplied source archive**; do not fabricate download links |

Download data from the providers under their terms. The download packages, versions, raw counts and upstream content can change. The T-Drive public page describes *approximately 15 million* sample points, whereas DiSMC's historical Table I reports **17,662,984 raw records**. These figures must **not** be treated as proof of a matching raw dataset; the upstream release/version and the historical file hash remain to be reconciled before claiming exact input reproduction.

## 2. Source-to-prepared conventions (from the supplementary paper)

| Dataset | Longitude filter | Latitude filter | Target CRS | Frozen sampling seed |
| --- | --- | --- | --- | ---: |
| GeoLife | 115–118° E | 39–42° N | EPSG:32650 (UTM zone 50N) | 20260925 |
| TDrive | 115–118° E | 39–42° N | EPSG:32650 (UTM zone 50N) | 20260924 |
| Porto | −9.5 to −7.5° | 40.5–42.5° N | EPSG:32629 (UTM zone 29N) | 20260924 |

The historical protocol:

1. Parse original WGS84 coordinates in **longitude/latitude order** after handling each format's source columns.
2. Keep valid coordinates within the indicated bounding box.
3. Project to the dataset-specific EPSG coordinate reference system (meters).
4. Round projected coordinates to **three decimals** (millimeters).
5. Globally deduplicate coordinate pairs.
6. Translate every point by subtracting the **global minima** of the respective X and Y coordinates.
7. Make fixed-seed **shuffled, nested reservoir subsets**; a smaller size is a prefix of the larger frozen sample (e.g. GeoLife 2M and 1M are prefixes of its 3M set).

For the manuscript's full-input rows, the supplement reports GeoLife **24,876,978 raw → 18,355,282 prepared** and TDrive **17,662,984 raw → 11,274,655 prepared**. The ESMC benchmark inputs are reported as NE **123,593 → 118,620**, CAS **196,902 → 124,514**, TS **389,942 → 383,852**. Porto is reported with **17,565,472 prepared** coordinates. These are **reported experimental counts**, not independently rebuilt numbers.

## 3. Required DiSMC program input

The integrated Java source's input readers (e.g. `DistributedSMCGridbaseRebuilt.readAndProcessData`) expect **plain UTF-8 text, one whitespace-separated `x y` pair per line, no header**. Coordinates are in projected-and-translated **meters**, not raw longitude/latitude, and do not carry per-trajectory IDs or timestamps.

Example:

```text
0.200 0.000
0.300 0.000
3.000 0.000
```

The Java implementation also deduplicates coordinates globally, but that does not replace the offline projection and sampling protocol. For a true multi-node run, put the prepared input at a URI all Spark executors can access.

## 4. Executable **reference** converter

The 2026-11-02 Java release does **not** include the historical trajectory-preparation program. To help readers produce valid `x y` inputs, this repository includes a separate, small reference implementation:

- [`prepare_trajectories.py`](prepare_trajectories.py): GeoLife PLT, TDrive CSV/TXT and Porto `train.csv` parsing; bounding box, CRS, rounding, global deduplication, minima translation, manifest and optional nested sample prefixes.
- [`test_prepare_trajectories.py`](test_prepare_trajectories.py): synthetic parsing/projection/deduplication tests.
- [`requirements.txt`](requirements.txt): tested `pyproj` dependency.

**Requirements:** Python 3.10+ (reference script tested using Python 3 and `pyproj 3.7.2`), disk space for a temporary on-disk SQLite deduplication database, and enough RAM for the *largest requested* reservoir sample. Example commands are run from the **repository root**, after extracting provider data:

```bash
python -m pip install -r data/requirements.txt
python -m unittest discover -s data -p 'test_prepare_trajectories.py' -v

python data/prepare_trajectories.py --dataset geolife \
  --input /path/to/extracted/Geolife/Data \
  --output /new/output/geolife-prepared.txt \
  --seed 20260925 --sample-sizes 100000,200000,400000,600000,800000,1000000,2000000,3000000

python data/prepare_trajectories.py --dataset tdrive \
  --input /path/to/extracted/TDrive \
  --output /new/output/tdrive-prepared.txt \
  --seed 20260924 --sample-sizes 100000,200000,400000,600000,800000,1000000,2000000,3000000

python data/prepare_trajectories.py --dataset porto \
  --input /path/to/extracted/Porto/train.csv \
  --output /new/output/porto-prepared.txt \
  --seed 20260924 --sample-sizes 100000,200000,400000,600000,800000,1000000
```

Use **fresh output paths**; the converter refuses overwriting the output, manifest or sample files. It produces:

- `<output>.txt` (the specified main file itself, if its suffix is `.txt`) containing unique X/Y meter coordinates;
- `<output>.meta.json` containing file counts, data CRS, preprocessing parameters, versions, prepared record counts and SHA-256;
- `<output>.sample_N.txt` for any requested nested sample sizes.

The reference implementation uses **SQLite global deduplication and lexicographic ordering of millimeter coordinates** before a seeded reservoir and shuffle. It uses Python `round(x*1000)` in integer millimeters. This yields deterministic *reference* outputs under the recorded environment, but the historical ingestion ordering, projection library and rounding tie behavior are **not known**. Consequently the reference samples **are not claimed to have the exact historical IDs, hashes, or counts**. A provided seed does not establish that identity. To reproduce a **published timing number**, the actual prepared data hash and experiment state must also match.

## 5. Coordinate and provenance check

Before running a benchmark, record:

- Upstream dataset name, official source URL, downloaded archive name/version and SHA-256;
- exact parser/CRS/projection library and its version, coordinate filter, rounding/deduplication behavior;
- total records before and after preparation, and prepared file SHA-256;
- sampler implementation/seed, largest sample size, sample hashes, and whether subsets are prefixes;
- query coordinates (which must use the same projected/translated frame), radii, k, and acquisition budget.

Paper query coordinates are listed in [`configs/fixed-query-coordinates.csv`](../configs/fixed-query-coordinates.csv); they are **not raw GPS longitude/latitude** and should not be reused with a differently translated dataset without checking coordinate-system alignment.

## 6. What remains unverified

- The publicly obtainable upstream files have **not been downloaded and processed as part of this documentation task**.
- The released integrated Java source lacks the historical dataset preprocessing scripts, raw input hashes and fixed historical reservoir ordering. Therefore, newly generated files are **valid inputs**, not byte-identical copies of the paper's historical inputs.
- Original source/download links and prepared-input hashes for **NE/CAS/TS** are not established from the provided material. If the original ESMC inputs are already available, use their existing whitespace-separated planar `x y` files; do not run the Beijing/Porto geographic projection.
- No private trajectory logs, usernames, server paths or third-party raw data should be committed to the repository.

## Recovered historical pipeline

The original experiment parser/subset scripts and processing metadata have now been recovered: see [historical preprocessing](historical/README.md). `prepare_trajectories.py` above remains a later reference converter; it is not substituted for those scripts or claimed byte-identical.
