#!/usr/bin/env python3
"""DiSMC reference trajectory conversion; not an exact historical data build."""
import argparse
import csv
import hashlib
import json
import math
import random
import sqlite3
import tempfile
from pathlib import Path

from pyproj import Transformer, __version__ as pyproj_version, proj_version_str

SPECS = {
    "geolife": (115.0, 118.0, 39.0, 42.0, "EPSG:32650"),
    "tdrive": (115.0, 118.0, 39.0, 42.0, "EPSG:32650"),
    "porto": (-9.5, -7.5, 40.5, 42.5, "EPSG:32629"),
}


def files_for(dataset, root):
    if dataset == "geolife":
        files = sorted(root.rglob("*.plt")) if root.is_dir() else [root]
    elif dataset == "tdrive":
        files = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in (".txt", ".csv")) if root.is_dir() else [root]
    else:
        files = [root]
    if not files or not all(p.is_file() for p in files):
        raise ValueError("No recognized input files found")
    return files


def source_points(dataset, files):
    for path in files:
        if dataset == "geolife":
            with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
                for _ in range(6):
                    next(handle, None)  # Official GeoLife PLT header
                for line in handle:
                    fields = line.strip().split(",")
                    if len(fields) < 2:
                        yield None
                        continue
                    try:
                        yield float(fields[1]), float(fields[0])  # longitude, latitude
                    except ValueError:
                        yield None
        elif dataset == "tdrive":
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                for row in csv.reader(handle):
                    if not row:
                        continue
                    if len(row) < 4:
                        yield None
                        continue
                    try:
                        yield float(row[2]), float(row[3])  # id,time,longitude,latitude
                    except ValueError:
                        yield None
        else:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                if not reader.fieldnames or "POLYLINE" not in reader.fieldnames:
                    raise ValueError("Porto CSV must have a POLYLINE field")
                for row in reader:
                    try:
                        points = json.loads(row["POLYLINE"] or "[]")
                    except (json.JSONDecodeError, TypeError):
                        yield None
                        continue
                    for point in points:
                        if not isinstance(point, list) or len(point) < 2:
                            yield None
                            continue
                        try:
                            yield float(point[0]), float(point[1])
                        except (TypeError, ValueError):
                            yield None


def hash_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def xy_line(xmm, ymm, minx, miny):
    return f"{(xmm-minx)/1000:.3f} {(ymm-miny)/1000:.3f}\n"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset", choices=sorted(SPECS), required=True)
    p.add_argument("--input", type=Path, required=True, help="Raw data directory, PLT, or Porto train.csv")
    p.add_argument("--output", type=Path, required=True, help="New output x/y text file")
    p.add_argument("--sample-sizes", default="", help="Optional nested prefix sizes, comma-separated")
    p.add_argument("--seed", type=int, default=None, help="Random seed for illustrative samples")
    args = p.parse_args()
    lo_lon, hi_lon, lo_lat, hi_lat, epsg = SPECS[args.dataset]
    sizes = sorted(set(int(s) for s in args.sample_sizes.split(",") if s.strip()))
    if any(s <= 0 for s in sizes) or (sizes and args.seed is None):
        p.error("sample sizes must be positive and require --seed")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    meta_path = Path(str(args.output) + ".meta.json")
    sample_paths = {n: Path(str(args.output) + f".sample_{n}.txt") for n in sizes}
    if any(path.exists() for path in [args.output, meta_path, *sample_paths.values()]):
        p.error("An output already exists; use a fresh output path")
    files = files_for(args.dataset, args.input)
    project = Transformer.from_crs("EPSG:4326", epsg, always_xy=True)
    counts = {"raw_point_records": 0, "invalid_or_unparseable": 0, "outside_bbox": 0, "kept_before_dedup": 0}
    with tempfile.TemporaryDirectory(prefix="dismc-prep-") as work:
        connection = sqlite3.connect(str(Path(work) / "unique.sqlite"))
        connection.execute("CREATE TABLE xy (xmm INTEGER NOT NULL, ymm INTEGER NOT NULL, PRIMARY KEY(xmm, ymm)) WITHOUT ROWID")
        batch = []
        for pair in source_points(args.dataset, files):
            counts["raw_point_records"] += 1
            if pair is None or not all(math.isfinite(x) for x in pair):
                counts["invalid_or_unparseable"] += 1
                continue
            lon, lat = pair
            if not (lo_lon <= lon <= hi_lon and lo_lat <= lat <= hi_lat):
                counts["outside_bbox"] += 1
                continue
            x, y = project.transform(lon, lat)
            if not (math.isfinite(x) and math.isfinite(y)):
                counts["invalid_or_unparseable"] += 1
                continue
            batch.append((round(x * 1000), round(y * 1000)))
            counts["kept_before_dedup"] += 1
            if len(batch) >= 10000:
                connection.executemany("INSERT OR IGNORE INTO xy VALUES (?, ?)", batch)
                connection.commit()
                batch.clear()
        if batch:
            connection.executemany("INSERT OR IGNORE INTO xy VALUES (?, ?)", batch)
            connection.commit()
        count, minx, miny = connection.execute("SELECT count(*),min(xmm),min(ymm) FROM xy").fetchone()
        if count == 0:
            raise ValueError("No valid unique points remain after filtering")
        if sizes and sizes[-1] > count:
            raise ValueError(f"Requested sample size {sizes[-1]} exceeds {count} prepared points")
        counts["prepared_unique_points"] = count
        rng = random.Random(args.seed)
        reservoir = []
        query = "SELECT xmm,ymm FROM xy ORDER BY xmm,ymm"
        with args.output.open("w", encoding="utf-8", newline="\n") as out:
            for index, (xmm, ymm) in enumerate(connection.execute(query)):
                xy = xy_line(xmm, ymm, minx, miny)
                out.write(xy)
                if sizes:
                    if index < sizes[-1]:
                        reservoir.append(xy)
                    else:
                        j = rng.randrange(index + 1)
                        if j < sizes[-1]:
                            reservoir[j] = xy
        if sizes:
            rng.shuffle(reservoir)
            for n, path in sample_paths.items():
                with path.open("w", encoding="utf-8", newline="\n") as out:
                    out.writelines(reservoir[:n])
        connection.close()
    meta = {
        "dataset": args.dataset,
        "input_file_count": len(files),
        "bbox_lon_lat": [lo_lon, hi_lon, lo_lat, hi_lat],
        "source_crs": "EPSG:4326", "target_crs": epsg,
        "rounding": "nearest integer millimeter using Python round(x*1000)",
        "deduplication": "global equality of rounded projected coordinate pairs",
        "translation": "subtract global minima of rounded x and y before output",
        "ordering": "sorted x then y by integer millimeters; not the historical ingestion order",
        "python_reference_not_original_experiment_pipeline": True,
        "pyproj_version": pyproj_version, "proj_version": proj_version_str,
        "counts": counts, "output_sha256": hash_file(args.output),
        "samples": {str(n): {"sha256": hash_file(path), "path": path.name} for n, path in sample_paths.items()},
        "sample_seed": args.seed,
        "sample_caveat": "reservoir over sorted unique points; seeds do not prove matching historical frozen sample IDs"
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "meta": str(meta_path), "counts": counts, "sha256": meta["output_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
