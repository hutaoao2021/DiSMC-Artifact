# Datasets and preprocessing

Raw GeoLife, TDrive, and Porto data are not redistributed in this repository. Download them from the official sources and follow their dataset terms:

| Dataset | Source | Input format |
| --- | --- | --- |
| GeoLife | [Microsoft GeoLife](https://www.microsoft.com/en-us/download/details.aspx?id=52367) | ZIP archive containing trajectory `.plt` files |
| TDrive | [Microsoft T-Drive](https://www.microsoft.com/en-us/research/publication/t-drive-trajectory-data-sample/) | Directory of taxi `.txt` files |
| Porto | [UCI Taxi Service Trajectory Prediction](https://archive.ics.uci.edu/dataset/339/taxi+service+trajectory+prediction+challenge+ecml+pkdd+2015) | `train.csv` with JSON `POLYLINE` coordinates |

## One-step entry points for all three datasets

Install Python 3 and `pyproj`; GNU `sort` must be available on Linux. After downloading the official archives, run the following commands from the **repository root**:

```bash
python3 -m pip install pyproj
export GEOLIFE_INPUT="/path/to/Geolife Trajectories 1.3.zip"
export TDRIVE_INPUT="/path/to/tdrive/taxi_log_2008_by_id"
export PORTO_INPUT="/path/to/porto/train.csv"
export WORK_ROOT="$PWD/data/historical/reproduction"

bash data/historical/scripts/prepare_all.sh
bash data/historical/scripts/create_subsets.sh
```

The first command processes GeoLife, TDrive and Porto with the recovered historical parser. Full prepared point sets are written to `$WORK_ROOT/prepared/`; nested 1M/3M subsets are written to `$WORK_ROOT/subsets/`; new statistics are written to `$WORK_ROOT/metadata/`. **Checked-in historical metadata is never replaced.**

GeoLife uses the independently recorded sampling seed **20260925**; TDrive and Porto retain **20260924**. The 1M sample is nested in the 3M sample. For a single dataset, use `bash data/historical/scripts/create_subsets.sh --datasets geolife`. Legacy GeoNames is still optional: `INCLUDE_GEONAMES=1` while preparing and `--datasets geonames` while sampling.

Both scripts refuse to overwrite existing outputs. For a new run, use a fresh `WORK_ROOT`. Run `bash data/historical/scripts/prepare_all.sh --help` and `python3 data/historical/scripts/create_subsets.py --help` for options. The paper batch launcher can consume this nested layout with `DATA_DIR="$WORK_ROOT"`. For figures requiring 2M or other sizes, generate those additional subsets from the prepared 3M file according to `configs/run-commands.md`.

## Historical preprocessing

The scripts in [`historical/scripts/`](historical/scripts/) were recovered from the experiment data-preparation directory. They are the historical parser and preparation pipeline, not the later reference converter.

Install Python 3, `pyproj`, and GNU `sort`. Example GeoLife command:

```bash
python3 -m pip install pyproj
python3 data/historical/scripts/prepare_dataset.py \
  --dataset geolife \
  --input /path/to/Geolife-Trajectories.zip \
  --output /path/to/prepared/geolife_xy.txt \
  --stats /path/to/metadata/geolife_stats.json \
  --temp-root /path/to/prepared/tmp \
  --sort-memory 4G --sort-parallelism 4
```

For TDrive, set `--dataset tdrive` and point `--input` to the extracted taxi-log directory. For Porto, set `--dataset porto` and point `--input` to `train.csv`. Use new output and stats paths.

The processing order is parsing, coordinate validation and study-area filtering, projection, three-decimal formatting, global `LC_ALL=C sort -u` deduplication, and translation by the global coordinate minima. GeoLife and TDrive use EPSG:32650; Porto uses EPSG:32629. Prepared files contain one projected and translated `x y` pair per line, in meters, with no header.

## Subsets

`create_subsets.py` now processes GeoLife, TDrive and Porto by default with their respective recorded seeds. `extend_subsets.py` extends an existing 3M base subset to 5M and 8M. The recovered GeoLife hashes are in `historical/metadata/geolife_scale_stats.json`; do not call newly produced samples byte-identical without confirming their SHA-256.

Historical processing counts, seeds, output hashes, and source-file hashes are in [`historical/metadata/`](historical/metadata/) and [`historical/file-provenance.json`](historical/file-provenance.json). Historical Python, pyproj, PROJ, and GNU sort versions were not fully recorded; the repository does not claim byte-identical regeneration under arbitrary current versions.

## Test the preprocessing scripts

```bash
(cd data/historical && python3 -m unittest discover -s tests -v)
```
