#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import random
import tempfile
from pathlib import Path


DEFAULT_SEED = 20260924
DATASETS = ("geolife", "geonames", "tdrive", "porto")
BASE_SIZE = 3_000_000
MEDIUM_SIZE = 5_000_000
LARGE_SIZE = 8_000_000


def write_lines_atomic(path, lines):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=str(path.parent)
    )
    digest = hashlib.sha256()
    try:
        with os.fdopen(descriptor, "wb") as output:
            for line in lines:
                output.write(line)
                digest.update(line)
        os.replace(temporary_name, path)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise
    return digest.hexdigest()


def extend_nested_subsets(
    source, base_path, medium_output, large_output,
    base_size=BASE_SIZE, medium_size=MEDIUM_SIZE, large_size=LARGE_SIZE,
    seed=DEFAULT_SEED,
):
    if not 0 < base_size < medium_size < large_size:
        raise ValueError("subset sizes must be strictly increasing")
    base_lines = Path(base_path).read_bytes().splitlines(keepends=True)
    if len(base_lines) != base_size:
        raise ValueError("base subset has {} lines, expected {}".format(
            len(base_lines), base_size
        ))
    base_set = set(base_lines)
    if len(base_set) != len(base_lines):
        raise ValueError("base subset contains duplicate lines")

    additional_size = large_size - base_size
    reservoir = []
    remaining_count = 0
    source_line_count = 0
    source_digest = hashlib.sha256()
    generator = random.Random(seed)
    with Path(source).open("rb") as input_file:
        for source_line_count, encoded in enumerate(input_file, start=1):
            source_digest.update(encoded)
            if encoded in base_set:
                continue
            if len(reservoir) < additional_size:
                reservoir.append(encoded)
            else:
                replacement = generator.randrange(remaining_count + 1)
                if replacement < additional_size:
                    reservoir[replacement] = encoded
            remaining_count += 1

    if len(reservoir) < additional_size:
        raise ValueError("source has fewer than {} unique remaining lines".format(
            additional_size
        ))
    generator.shuffle(reservoir)
    medium_lines = base_lines + reservoir[:medium_size - base_size]
    large_lines = base_lines + reservoir
    generator.shuffle(medium_lines)
    generator.shuffle(large_lines)
    return {
        "seed": seed,
        "source_line_count": source_line_count,
        "source_sha256": source_digest.hexdigest(),
        "base_line_count": base_size,
        "medium_line_count": len(medium_lines),
        "medium_sha256": write_lines_atomic(medium_output, medium_lines),
        "large_line_count": len(large_lines),
        "large_sha256": write_lines_atomic(large_output, large_lines),
    }


def main():
    parser = argparse.ArgumentParser(description="Extend reproducible nested subsets")
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1], type=Path)
    parser.add_argument("--seed", default=DEFAULT_SEED, type=int)
    options = parser.parse_args()
    root = options.root.resolve()
    subset_directory = root / "scale_subsets"
    stats_path = root / "metadata" / "extended_subsets_stats.json"
    outputs = []
    for dataset in DATASETS:
        outputs.extend([
            subset_directory / "{}_5m_xy.txt".format(dataset),
            subset_directory / "{}_8m_xy.txt".format(dataset),
        ])
    existing = [str(path) for path in outputs if path.exists()]
    if existing:
        parser.error("refusing to overwrite existing files: " + ", ".join(existing))

    statistics = {
        "method": "fixed-seed reservoir extension of the existing 3M subset",
        "seed": options.seed,
        "datasets": {},
    }
    for dataset in DATASETS:
        print("extending dataset={}".format(dataset), flush=True)
        statistics["datasets"][dataset] = extend_nested_subsets(
            root / "prepared" / "{}_xy.txt".format(dataset),
            subset_directory / "{}_3m_xy.txt".format(dataset),
            subset_directory / "{}_5m_xy.txt".format(dataset),
            subset_directory / "{}_8m_xy.txt".format(dataset),
            seed=options.seed,
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
