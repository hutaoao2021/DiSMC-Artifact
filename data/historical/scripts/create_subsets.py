#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import random
import tempfile
from pathlib import Path


DEFAULT_SEED = 20260924
GEOLIFE_SEED = 20260925
DATASETS = ("geolife", "tdrive", "porto")
AVAILABLE_DATASETS = ("geolife", "geonames", "tdrive", "porto")


def _write_lines_atomic(path, lines):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    digest = hashlib.sha256()
    try:
        with os.fdopen(descriptor, "wb") as output:
            for line in lines:
                encoded = line.encode("utf-8")
                output.write(encoded)
                digest.update(encoded)
        os.replace(temporary_name, path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise
    return digest.hexdigest()


def create_nested_subsets(source, small_output, large_output, small_size, large_size, seed):
    if not 0 < small_size <= large_size:
        raise ValueError("subset sizes must satisfy 0 < small <= large")

    generator = random.Random(seed)
    reservoir = []
    source_digest = hashlib.sha256()
    source_line_count = 0
    with Path(source).open("rb") as input_file:
        for source_line_count, encoded in enumerate(input_file, start=1):
            source_digest.update(encoded)
            line = encoded.decode("utf-8")
            if source_line_count <= large_size:
                reservoir.append(line)
            else:
                replacement = generator.randrange(source_line_count)
                if replacement < large_size:
                    reservoir[replacement] = line

    if source_line_count < large_size:
        raise ValueError(
            "source has fewer than {} lines: {}".format(large_size, source_line_count)
        )

    generator.shuffle(reservoir)
    large_lines = reservoir
    small_lines = reservoir[:small_size]
    small_sha256 = _write_lines_atomic(small_output, small_lines)
    large_sha256 = _write_lines_atomic(large_output, large_lines)
    return {
        "seed": seed,
        "source_line_count": source_line_count,
        "source_sha256": source_digest.hexdigest(),
        "small_line_count": small_size,
        "small_sha256": small_sha256,
        "large_line_count": large_size,
        "large_sha256": large_sha256,
    }


def main():
    parser = argparse.ArgumentParser(description="Create reproducible nested point subsets")
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1] / "reproduction", type=Path)
    parser.add_argument("--datasets", nargs="+", choices=AVAILABLE_DATASETS, default=list(DATASETS))
    parser.add_argument("--small-size", default=1_000_000, type=int)
    parser.add_argument("--large-size", default=3_000_000, type=int)
    parser.add_argument("--seed", default=DEFAULT_SEED, type=int)
    parser.add_argument("--geolife-seed", default=GEOLIFE_SEED, type=int)
    options = parser.parse_args()
    if not 0 < options.small_size <= options.large_size:
        parser.error("subset sizes must satisfy 0 < small <= large")
    if len(set(options.datasets)) != len(options.datasets):
        parser.error("duplicate dataset names are not allowed")

    root = options.root.resolve()
    subset_directory = root / "subsets"
    stats_path = root / "metadata" / "subsets_stats.json"
    expected_outputs = [stats_path]
    for dataset in options.datasets:
        expected_outputs.extend([
            subset_directory / "{}_1m_xy.txt".format(dataset),
            subset_directory / "{}_3m_xy.txt".format(dataset),
        ])
    existing = [str(path) for path in expected_outputs if path.exists()]
    if existing:
        parser.error("refusing to overwrite existing files: " + ", ".join(existing))

    missing = [
        str(root / "prepared" / "{}_xy.txt".format(dataset))
        for dataset in options.datasets
        if not (root / "prepared" / "{}_xy.txt".format(dataset)).is_file()
    ]
    if missing:
        parser.error("missing prepared inputs: " + ", ".join(missing))

    statistics = {
        "method": "fixed-seed reservoir sampling; 1M is nested within 3M",
        "seed": options.seed,
        "geolife_seed": options.geolife_seed,
        "datasets": {},
    }
    for dataset in options.datasets:
        dataset_seed = options.geolife_seed if dataset == "geolife" else options.seed
        print("sampling dataset={} seed={}".format(dataset, dataset_seed), flush=True)
        statistics["datasets"][dataset] = create_nested_subsets(
            root / "prepared" / "{}_xy.txt".format(dataset),
            subset_directory / "{}_1m_xy.txt".format(dataset),
            subset_directory / "{}_3m_xy.txt".format(dataset),
            options.small_size,
            options.large_size,
            dataset_seed,
        )

    stats_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=stats_path.name + ".", suffix=".tmp", dir=str(stats_path.parent)
    )
    with os.fdopen(descriptor, "w", encoding="utf-8") as output:
        json.dump(statistics, output, ensure_ascii=False, indent=2, sort_keys=True)
        output.write("\n")
    os.replace(temporary_name, stats_path)
    print("stats={}".format(stats_path), flush=True)


if __name__ == "__main__":
    main()
