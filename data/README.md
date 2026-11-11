# Datasets and preprocessing

Download the source datasets from the official third-party providers below.

| Dataset | Official source | Raw input |
| --- | --- | --- |
| GeoLife | [Microsoft GeoLife](https://www.microsoft.com/en-us/download/details.aspx?id=52367) | ZIP containing `.plt` trajectories |
| TDrive | [Microsoft T-Drive](https://www.microsoft.com/en-us/research/publication/t-drive-trajectory-data-sample/) | Directory of taxi-log `.txt` files |
| Porto | [UCI Taxi Trajectory Prediction](https://archive.ics.uci.edu/dataset/339/taxi+service+trajectory+prediction+challenge+ecml+pkdd+2015) | `train.csv` with `POLYLINE` JSON |

Download the original files according to each provider's terms before preprocessing.

## Prepare full datasets and nested samples

Requirements: Python 3, `pyproj` and GNU `sort` on Linux. From the repository root:

```bash
python3 -m pip install pyproj
export GEOLIFE_INPUT="/path/to/Geolife Trajectories 1.3.zip"
export TDRIVE_INPUT="/path/to/tdrive/taxi_log_2008_by_id"
export PORTO_INPUT="/path/to/porto/train.csv"
export WORK_ROOT="$PWD/data/historical/reproduction"

bash data/historical/scripts/prepare_all.sh
bash data/historical/scripts/create_subsets.sh
DATA_DIR="$WORK_ROOT" bash configs/prepare_paper_subsets.sh
```

The outputs are:

| Directory | Contents |
| --- | --- |
| `$WORK_ROOT/prepared/` | Full `geolife_xy.txt`, `tdrive_xy.txt` and `porto_xy.txt` |
| `$WORK_ROOT/subsets/` | Nested 1M/3M samples and additional 100K–800K and 2M paper prefixes |
| `$WORK_ROOT/metadata/` | Newly generated statistics and hashes |

The scripts reject existing output paths. Set a **new** `WORK_ROOT` for a fresh preparation rather than overwriting historical data.

## Processing definition

The released `historical/scripts/prepare_dataset.py` implements trajectory parsing, coordinate validation and region filtering, projection, rounding to three decimals, global `LC_ALL=C sort -u` deduplication, and translation by the minimum projected coordinates. GeoLife and TDrive use **EPSG:32650**, and Porto uses **EPSG:32629**. Final files contain one `x y` pair in meters per line, without a header.

`historical/scripts/create_subsets.py` creates nested 1M/3M reservoir samples. The recorded seeds are **20260925 for GeoLife** and **20260924 for TDrive and Porto**. Use `bash data/historical/scripts/create_subsets.sh --datasets geolife` to sample only GeoLife. Legacy GeoNames remains optional, using `INCLUDE_GEONAMES=1` during preparation and `--datasets geonames` during sampling. `extend_subsets.py` supports the historical 5M/8M extensions.

Historical point counts and SHA-256 hashes are provided in [historical/metadata/](historical/metadata/), with original and distributed script checksums in [historical/file-provenance.json](historical/file-provenance.json). To compare data generated in a different Python/PROJ environment with the reference inputs, use these published SHA-256 hashes.

Optional preprocessing checks:

```bash
(cd data/historical && python3 -m unittest discover -s tests -v)
```
