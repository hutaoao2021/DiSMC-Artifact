#!/usr/bin/env python3
import argparse
import csv
import datetime
import hashlib
import json
import math
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from pyproj import Transformer


DATASET_CONFIGS = {
    "geonames": {
        "target_crs": "EPSG:6933",
        "projection_area": (-180.0, 180.0, -86.0, 86.0),
    },
    "tdrive": {
        "target_crs": "EPSG:32650",
        "projection_area": (114.0, 120.0, 0.0, 84.0),
        "dataset_area": (115.0, 118.0, 39.0, 42.0),
    },
    "porto": {
        "target_crs": "EPSG:32629",
        "projection_area": (-12.0, -6.0, 0.0, 84.0),
        "dataset_area": (-9.5, -7.5, 40.5, 42.5),
    },
    "geolife": {
        "target_crs": "EPSG:32650",
        "projection_area": (114.0, 120.0, 0.0, 84.0),
        "dataset_area": (115.0, 118.0, 39.0, 42.0),
    },
}

MAX_ERROR_RATE = 0.0001


COUNTER_NAMES = (
    "source_records",
    "coordinate_pairs_seen",
    "valid_projected_points",
    "malformed_records",
    "invalid_coordinates",
    "outside_projection_area",
    "outside_dataset_area",
    "empty_trajectories",
    "parse_errors",
    "malformed_coordinate_pairs",
)


def new_counters():
    return {name: 0 for name in COUNTER_NAMES}


def _valid_wgs84(longitude, latitude):
    return (
        math.isfinite(longitude)
        and math.isfinite(latitude)
        and -180.0 <= longitude <= 180.0
        and -90.0 <= latitude <= 90.0
    )


def _validated_pair(longitude, latitude, counters):
    counters["coordinate_pairs_seen"] += 1
    if not _valid_wgs84(longitude, latitude):
        counters["invalid_coordinates"] += 1
        return None
    return longitude, latitude


def iter_geonames(path, counters):
    with Path(path).open("r", encoding="utf-8") as source:
        for line in source:
            counters["source_records"] += 1
            fields = line.rstrip("\r\n").split("\t")
            if len(fields) < 6:
                counters["malformed_records"] += 1
                continue
            try:
                latitude = float(fields[4])
                longitude = float(fields[5])
            except ValueError:
                counters["malformed_records"] += 1
                continue
            point = _validated_pair(longitude, latitude, counters)
            if point is not None:
                yield point


def iter_tdrive(path, counters):
    root = Path(path)
    files = [root] if root.is_file() else sorted(root.rglob("*.txt"))
    for input_path in files:
        with input_path.open("r", encoding="utf-8") as source:
            for line in source:
                counters["source_records"] += 1
                fields = line.rstrip("\r\n").split(",")
                if len(fields) != 4:
                    counters["malformed_records"] += 1
                    continue
                try:
                    longitude = float(fields[2])
                    latitude = float(fields[3])
                except ValueError:
                    counters["malformed_records"] += 1
                    continue
                point = _validated_pair(longitude, latitude, counters)
                if point is not None:
                    yield point


def iter_geolife(path, counters):
    with zipfile.ZipFile(path) as archive:
        names = sorted(
            name for name in archive.namelist()
            if name.lower().endswith(".plt") and not name.endswith("/")
        )
        for name in names:
            with archive.open(name) as binary_source:
                for line_number, encoded in enumerate(binary_source):
                    if line_number < 6:
                        continue
                    counters["source_records"] += 1
                    fields = encoded.decode("utf-8", errors="replace").rstrip("\r\n").split(",")
                    if len(fields) < 2:
                        counters["malformed_records"] += 1
                        continue
                    try:
                        latitude = float(fields[0])
                        longitude = float(fields[1])
                    except ValueError:
                        counters["malformed_records"] += 1
                        continue
                    point = _validated_pair(longitude, latitude, counters)
                    if point is not None:
                        yield point


def iter_porto(path, counters):
    with Path(path).open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        for row in reader:
            counters["source_records"] += 1
            encoded = row.get("POLYLINE")
            if encoded is None:
                counters["malformed_records"] += 1
                continue
            try:
                polyline = json.loads(encoded)
            except (TypeError, ValueError):
                counters["parse_errors"] += 1
                continue
            if not isinstance(polyline, list):
                counters["parse_errors"] += 1
                continue
            if not polyline:
                counters["empty_trajectories"] += 1
                continue
            for coordinate in polyline:
                if not isinstance(coordinate, list) or len(coordinate) != 2:
                    counters["malformed_coordinate_pairs"] += 1
                    continue
                try:
                    longitude = float(coordinate[0])
                    latitude = float(coordinate[1])
                except (TypeError, ValueError):
                    counters["malformed_coordinate_pairs"] += 1
                    continue
                point = _validated_pair(longitude, latitude, counters)
                if point is not None:
                    yield point


def format_coordinate(value):
    formatted = "{:.3f}".format(value)
    return "0.000" if formatted == "-0.000" else formatted


def project_points(points, dataset, output, counters):
    config = DATASET_CONFIGS[dataset]
    west, east, south, north = config["projection_area"]
    dataset_area = config.get("dataset_area")
    transformer = Transformer.from_crs(
        "EPSG:4326", config["target_crs"], always_xy=True
    )
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as destination:
        for longitude, latitude in points:
            if dataset_area is not None:
                dataset_west, dataset_east, dataset_south, dataset_north = dataset_area
                if not (
                    dataset_west <= longitude <= dataset_east
                    and dataset_south <= latitude <= dataset_north
                ):
                    counters["outside_dataset_area"] += 1
                    continue
            if not (west <= longitude <= east and south <= latitude <= north):
                counters["outside_projection_area"] += 1
                continue
            x, y = transformer.transform(longitude, latitude)
            if not math.isfinite(x) or not math.isfinite(y):
                counters["invalid_coordinates"] += 1
                continue
            destination.write(
                "{} {}\n".format(format_coordinate(x), format_coordinate(y))
            )
            counters["valid_projected_points"] += 1


def external_unique(source, destination, memory, parallelism, temporary_directory):
    source_path = Path(source)
    destination_path = Path(destination)
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment["LC_ALL"] = "C"
    command = [
        "sort",
        "-u",
        "-S",
        str(memory),
        "--parallel={}".format(int(parallelism)),
        "-T",
        str(temporary_directory),
        str(source_path),
    ]
    with destination_path.open("wb") as output:
        subprocess.run(command, check=True, stdout=output, env=environment)


def _parse_xy(line, line_number, path):
    fields = line.split()
    if len(fields) != 2:
        raise ValueError("invalid x y line {} in {}".format(line_number, path))
    try:
        x = float(fields[0])
        y = float(fields[1])
    except ValueError as exc:
        raise ValueError("invalid number on line {} in {}".format(line_number, path)) from exc
    if not math.isfinite(x) or not math.isfinite(y):
        raise ValueError("non-finite coordinate on line {} in {}".format(line_number, path))
    return x, y


def translate_unique(source, destination):
    source_path = Path(source)
    destination_path = Path(destination)
    count = 0
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    with source_path.open("r", encoding="utf-8") as input_file:
        for line_number, line in enumerate(input_file, 1):
            x, y = _parse_xy(line, line_number, source_path)
            count += 1
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
    if count == 0:
        raise ValueError("no valid points in {}".format(source_path))

    offset_x = -min_x
    offset_y = -min_y
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=destination_path.name + ".", suffix=".tmp", dir=str(destination_path.parent)
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as output_file:
            with source_path.open("r", encoding="utf-8") as input_file:
                for line_number, line in enumerate(input_file, 1):
                    x, y = _parse_xy(line, line_number, source_path)
                    output_file.write(
                        "{} {}\n".format(
                            format_coordinate(x + offset_x),
                            format_coordinate(y + offset_y),
                        )
                    )
        os.replace(temporary_name, destination_path)
    except BaseException:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)
        raise

    return {
        "unique_points": count,
        "translation_offset_x": offset_x,
        "translation_offset_y": offset_y,
        "projected_min_x": min_x,
        "projected_max_x": max_x,
        "projected_min_y": min_y,
        "projected_max_y": max_y,
        "min_x": 0.0,
        "max_x": max_x + offset_x,
        "min_y": 0.0,
        "max_y": max_y + offset_y,
    }


def validate_output(path, expected_count):
    input_path = Path(path)
    count = 0
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    with input_path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            x, y = _parse_xy(line, line_number, input_path)
            if x < 0 or y < 0:
                raise ValueError("negative coordinate on line {} in {}".format(line_number, input_path))
            count += 1
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
    if count != expected_count:
        raise ValueError("line count {} does not match expected {}".format(count, expected_count))
    if count == 0:
        raise ValueError("output is empty: {}".format(input_path))
    return {
        "line_count": count,
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y,
    }


def _adapter(dataset):
    return {
        "geonames": iter_geonames,
        "tdrive": iter_tdrive,
        "porto": iter_porto,
        "geolife": iter_geolife,
    }[dataset]


def _sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_source(path):
    source_path = Path(path)
    if source_path.is_file():
        return _sha256_file(source_path)
    digest = hashlib.sha256()
    for input_path in sorted(item for item in source_path.rglob("*") if item.is_file()):
        relative = str(input_path.relative_to(source_path)).encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        with input_path.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def _error_count(counters):
    return sum(counters[name] for name in (
        "malformed_records",
        "invalid_coordinates",
        "parse_errors",
        "malformed_coordinate_pairs",
    ))


def _parse_arguments(arguments):
    parser = argparse.ArgumentParser(description="Prepare a canonical DiSMC point dataset")
    parser.add_argument("--dataset", required=True, choices=sorted(DATASET_CONFIGS))
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--stats", required=True)
    parser.add_argument("--temp-root")
    parser.add_argument("--sort-memory", default="4G")
    parser.add_argument("--sort-parallelism", type=int, default=4)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args(arguments)


def run_pipeline(options, command):
    input_path = Path(options.input).resolve()
    output_path = Path(options.output).resolve()
    stats_path = Path(options.stats).resolve()
    if not input_path.exists():
        raise ValueError("input does not exist: {}".format(input_path))
    if options.sort_parallelism < 1:
        raise ValueError("sort parallelism must be positive")
    if not options.overwrite:
        for existing in (output_path, stats_path):
            if existing.exists():
                raise ValueError("output already exists: {}".format(existing))

    temporary_root = Path(options.temp_root).resolve() if options.temp_root else output_path.parent
    temporary_root.mkdir(parents=True, exist_ok=True)
    work_directory = Path(tempfile.mkdtemp(
        prefix="prepare-{}-".format(options.dataset), dir=str(temporary_root)
    ))
    projected_path = work_directory / "projected.txt"
    unique_path = work_directory / "unique.txt"
    prepared_path = work_directory / "prepared.txt"
    staged_stats_path = work_directory / "stats.json"
    counters = new_counters()
    try:
        points = _adapter(options.dataset)(input_path, counters)
        project_points(points, options.dataset, projected_path, counters)
        observed = max(1, counters["source_records"])
        error_count = _error_count(counters)
        error_rate = error_count / float(observed)
        if error_rate > MAX_ERROR_RATE:
            raise ValueError(
                "input error rate {:.6%} exceeds {:.4%}".format(error_rate, MAX_ERROR_RATE)
            )
        external_unique(
            projected_path,
            unique_path,
            options.sort_memory,
            options.sort_parallelism,
            work_directory,
        )
        translation = translate_unique(unique_path, prepared_path)
        validation = validate_output(prepared_path, translation["unique_points"])
        valid_points = counters["valid_projected_points"]
        duplicate_rate = (
            (valid_points - translation["unique_points"]) / float(valid_points)
            if valid_points else 0.0
        )
        metadata = dict(counters)
        metadata.update(translation)
        metadata.update({
            "dataset": options.dataset,
            "source_path": str(input_path),
            "source_sha256": _sha256_source(input_path),
            "source_crs": "EPSG:4326",
            "target_crs": DATASET_CONFIGS[options.dataset]["target_crs"],
            "projection_area": DATASET_CONFIGS[options.dataset]["projection_area"],
            "dataset_area": DATASET_CONFIGS[options.dataset].get("dataset_area"),
            "coordinate_decimals": 3,
            "error_count": error_count,
            "error_rate": error_rate,
            "maximum_error_rate": MAX_ERROR_RATE,
            "duplicate_rate": duplicate_rate,
            "output_path": str(output_path),
            "output_line_count": validation["line_count"],
            "output_bytes": prepared_path.stat().st_size,
            "output_sha256": _sha256_file(prepared_path),
            "command": shlex.join(command),
            "completed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        })
        with staged_stats_path.open("w", encoding="utf-8") as destination:
            json.dump(metadata, destination, ensure_ascii=False, indent=2, sort_keys=True)
            destination.write("\n")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        stats_path.parent.mkdir(parents=True, exist_ok=True)
        os.replace(prepared_path, output_path)
        os.replace(staged_stats_path, stats_path)
        shutil.rmtree(str(work_directory))
        return metadata
    except BaseException:
        print("preprocessing workspace preserved at {}".format(work_directory), file=sys.stderr)
        raise


def main(arguments=None):
    raw_arguments = sys.argv[1:] if arguments is None else list(arguments)
    options = _parse_arguments(raw_arguments)
    command = [sys.executable, str(Path(__file__).resolve())] + raw_arguments
    try:
        metadata = run_pipeline(options, command)
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 2
    print("dataset={}".format(metadata["dataset"]))
    print("unique_points={}".format(metadata["unique_points"]))
    print("duplicate_rate={:.6f}".format(metadata["duplicate_rate"]))
    print("output={}".format(metadata["output_path"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
