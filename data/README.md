# Datasets and preprocessing

Raw GeoLife, TDrive, and Porto data are not redistributed in this repository. Download them from the official sources and follow their dataset terms:

| Dataset | Source | Input format |
| --- | --- | --- |
| GeoLife | [Microsoft GeoLife](https://www.microsoft.com/en-us/download/details.aspx?id=52367) | ZIP archive containing trajectory `.plt` files |
| TDrive | [Microsoft T-Drive](https://www.microsoft.com/en-us/research/publication/t-drive-trajectory-data-sample/) | Directory of taxi `.txt` files |
| Porto | [UCI Taxi Service Trajectory Prediction](https://archive.ics.uci.edu/dataset/339/taxi+service+trajectory+prediction+challenge+ecml+pkdd+2015) | `train.csv` with JSON `POLYLINE` coordinates |

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

`create_subsets.py` implements fixed-seed reservoir sampling for the datasets listed in its `DATASETS` constant. `extend_subsets.py` extends an existing 3M base subset to 5M and 8M. Their arguments and required directory layout are available with `--help`. The recovered GeoLife 1M/3M sampling seed and output hashes are recorded in `historical/metadata/geolife_scale_stats.json`; the exact original GeoLife subset-generation invocation was not recovered, so do not treat a newly generated sample as byte-identical without checking its SHA-256.

Historical processing counts, seeds, output hashes, and source-file hashes are in [`historical/metadata/`](historical/metadata/) and [`historical/file-provenance.json`](historical/file-provenance.json). Historical Python, pyproj, PROJ, and GNU sort versions were not fully recorded; the repository does not claim byte-identical regeneration under arbitrary current versions.

## Test the preprocessing scripts

```bash
python3 -m unittest discover -s data/historical/tests -v
```
