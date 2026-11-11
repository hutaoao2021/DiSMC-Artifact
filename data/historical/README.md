# Recovered historical preprocessing

These scripts were recovered from the original experiment filesystem, together with processing metadata and input/output SHA-256 values. They are distinct from the later reference converter `data/prepare_trajectories.py`; byte equivalence between those two pipelines is not asserted.

[file-provenance.json](file-provenance.json) gives each original relative path, original file hash, distributed file hash, dataset scope and evidence source. Storage/network strings are redacted where present; target-dataset metadata excerpts are explicitly identified. No raw trajectories are distributed.

## Actual historical order

1. Parse raw records. GeoLife: sorted ZIP `.plt` entries, six header lines skipped, latitude/longitude fields 0/1. TDrive: sorted recursive `.txt` files, four-field rows, longitude/latitude fields 2/3. Porto: CSV `POLYLINE` JSON `[longitude, latitude]` entries.
2. Reject malformed/nonfinite or invalid WGS84 coordinates, then apply dataset study-area and projection-area filters.
3. Project `EPSG:4326` using `always_xy=True`: GeoLife/TDrive to **EPSG:32650**; Porto to **EPSG:32629**.
4. Format projected coordinates to **three decimal places**; normalize negative zero.
5. Perform global line deduplication using external **`LC_ALL=C sort -u`**, with recorded `-S 4G --parallel=4`. The ordering is lexicographic line ordering, not numeric coordinate sorting or SQLite ordering.
6. Find coordinate minima, subtract them from the deduplicated rounded coordinates, and format to three decimals again.
7. Generate subsets separately from the prepared file. Recovered `create_subsets.py` uses Python `random.Random(seed)` (MT19937), reservoir Algorithm R using `randrange`, then shuffles with the **same generator stream**; the 1M subset is a prefix of the 3M output. TDrive/Porto metadata records seed **20260924**. GeoLife metadata records seed **20260925**, but the exact GeoLife-specific generation invocation/launcher has not been recovered. Do not silently substitute the TDrive/Porto launcher as its historical command.
8. `extend_subsets.py` preserves the existing 3M set, samples additional records from its complement, and shuffles the resulting 5M/8M sets. See code for RNG draw order. This is a separate process from a prefix subset.

`prepare_all.sh` is the recovered multi-dataset launcher; it does not invoke GeoLife. GeoLife's actual CLI is retained in `metadata/geolife_stats.json`. The historical scripts also support other datasets; that does not mean all of them are used by this artifact's targeted experiments.

## Files and historical identity

| Dataset | Prepared points | Prepared SHA-256 |
|---|---:|---|
| GeoLife | 18,355,282 | `44f2e5dee84b14bfd1a59a56226717137da355d057c81913522e93e197d755c4` |
| TDrive | 11,274,655 | `92b15d34e40b5c87b799db29220e45c0d4fd448f92d53555082fc639af5834f2` |
| Porto | 17,565,472 | `6dcd783e15070483319ea3809cfcd19eeb0c47190e9433f9953e9d52ba3bd574` |

Raw input hashes, bbox settings, translation offsets, recorded CLI, counts and completion times are in `metadata/*_stats.json`. TDrive's source hash is a directory-tree digest whose serialization is defined by the recovered script, not a tarball hash. Subset hashes and seed records are supplied separately. Hashes are provided without redistributing the source datasets.

## Environment and verification

Historical metadata does not pin Python/pyproj/PROJ/coreutils versions. These remain **unknown for the historical execution**. The current verification environment is Python 3.8.8, pyproj 3.5.0, PROJ 9.2.0 and GNU sort 8.32; it is not retroactively assigned to past runs. The recovered 19 small preprocessing tests pass in that environment; this does not constitute a full raw-dataset regeneration.

Use the recovered parser directly for a fresh conversion with your own legally acquired input:

```bash
python3 data/historical/scripts/prepare_dataset.py --help
python3 data/historical/scripts/create_subsets.py --help
python3 data/historical/scripts/extend_subsets.py --help
python3 -m unittest discover -s data/historical/tests -v
```

The launchers expect their own `raw/`, `prepared/`, `metadata/` and `scale_subsets/` layout. They refuse overwriting existing outputs unless explicitly allowed. Follow the existing [dataset acquisition instructions](../README.md); file names and hashes must be checked before claiming historical byte identity.
