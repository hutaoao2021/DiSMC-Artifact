# Dataset preparation

## Data sources

The DiSMC experiments use several spatial datasets. GeoLife and TDrive are trajectory collections, while the main manuscript and supplementary material also describe their other experimental inputs. Obtain third-party data from the relevant original providers in accordance with applicable access and redistribution terms.

## GeoLife and TDrive preprocessing

The supplementary protocol specifies the following preparation convention for these two trajectory datasets:

1. Parse WGS84 coordinate records.
2. Retain valid records in the longitude interval [115, 118] degrees E and latitude interval [39, 42] degrees N.
3. Project coordinates to EPSG:32650 (meter units).
4. Round each projected coordinate to three decimal places.
5. Deduplicate coordinate pairs globally.
6. Subtract the minimum coordinate values to translate the prepared point set.

The supplementary report distinguishes raw record counts from prepared unique points. It also describes fixed-seed sampling and nested subsets; these are necessary to reproduce the specific benchmark workloads.

## Parameters and provenance

Use the exact query coordinates and experimental radii listed in the supplementary tables, not arbitrary example queries. Retain a record of input version, preparation program version, number of raw records, number of prepared points, and a content hash of the prepared input whenever available.

The source archive contains a five-point synthetic fixture at `examples/five_points.txt`. It is a convenient environment and correctness example; it is not a replacement for the full experimental datasets.
