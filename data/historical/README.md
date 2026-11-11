# Dataset preprocessing details

The scripts in this directory implement preprocessing and fixed-seed subset generation for GeoLife, TDrive, and Porto. For data downloads and an end-to-end command sequence, follow [the dataset guide](../README.md).

## Processing pipeline

1. Parse trajectories from GeoLife ZIP `.plt` files, TDrive taxi-log text files, or Porto `POLYLINE` entries.
2. Validate WGS84 coordinates, apply the dataset study-area filters, and project GeoLife/TDrive to EPSG:32650 or Porto to EPSG:32629.
3. Round projected coordinates to three decimals, globally deduplicate with `LC_ALL=C sort -u`, subtract per-dataset coordinate minima, and write one `x y` pair per line.
4. Generate fixed-seed nested subsets using the included reservoir sampler. Use seed `20260925` for GeoLife and `20260924` for TDrive and Porto.

Run `prepare_all.sh` to prepare GeoLife, TDrive, and Porto from the configured input paths. Run `create_subsets.sh` to generate the nested subsets. See [the dataset guide](../README.md) for the complete sequence and environment variables. Existing outputs are protected against accidental overwriting.

## Reference prepared datasets

| Dataset | Points | SHA-256 |
| --- | ---: | --- |
| GeoLife | 18,355,282 | `44f2e5dee84b14bfd1a59a56226717137da355d057c81913522e93e197d755c4` |
| TDrive | 11,274,655 | `92b15d34e40b5c87b799db29220e45c0d4fd448f92d53555082fc639af5834f2` |
| Porto | 17,565,472 | `6dcd783e15070483319ea3809cfcd19eeb0c47190e9433f9953e9d52ba3bd574` |

Additional reference statistics, sample sizes, and checksums are available in [metadata/](metadata/).

## Preprocessing tests

```bash
python3 -m unittest discover -s data/historical/tests -v
```
