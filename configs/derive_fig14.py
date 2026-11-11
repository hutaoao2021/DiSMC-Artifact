#!/usr/bin/env python3
"""Derive Fig. 14's formal check counters from the SAME Fig. 13 Spark task rows.

Never rerun Spark or reuse recorded paper aggregates. All four R/W combinations
must be present for each dataset; source rows and derived CSV remain separate.
"""
import csv
import re
import statistics
import sys
from pathlib import Path

FILENAME = re.compile(
    r"^(geolife|tdrive)_(2m|3m)_R([01])W([01])_dismc_trial([1-9][0-9]*)"
    r"\.txt\.micro_tasks\.csv$"
)
COLUMNS = ("candidate_count", "z_window_checks", "distance_checks")


def read_trial(path):
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        mandatory = set(COLUMNS) | {"stage_id", "partition_id", "owner", "lane"}
        if not mandatory.issubset(reader.fieldnames or ()):
            raise ValueError("Missing task counters in {}".format(path))
        totals = dict.fromkeys(COLUMNS, 0)
        identity = set()
        seen = 0
        for record in reader:
            key = (record["stage_id"], record["partition_id"], record["owner"], record["lane"])
            if key in identity:
                raise ValueError("Duplicate Spark task attempt in {}; refuse double count".format(path))
            identity.add(key)
            for column in COLUMNS:
                totals[column] += int(record[column])
            seen += 1
        if seen == 0:
            raise ValueError("No formal task rows in {}".format(path))
        return seen, totals


def derive(directory, output):
    matches = []
    observed = set()
    for path in sorted(directory.glob("*.micro_tasks.csv")):
        match = FILENAME.match(path.name)
        if not match:
            continue  # Exclude the frozen CAPTURE from Fig. 14 formal results.
        dataset, size, r, w, trial = match.groups()
        key = (dataset, r, w, int(trial))
        if key in observed:
            raise ValueError("Duplicate R/W trial: {}".format(key))
        observed.add(key)
        tasks, totals = read_trial(path)
        matches.append({
            "dataset": dataset, "points": size, "R": r, "W": w,
            "trial": int(trial), "formal_tasks": tasks,
            "candidate_count": totals["candidate_count"],
            "generation_z_window_checks": totals["z_window_checks"],
            "counting_distance_checks": totals["distance_checks"],
            "generation_plus_counting_checks":
                totals["z_window_checks"] + totals["distance_checks"],
            "source_task_file": str(path),
        })
    if not matches:
        raise ValueError("No Fig. 13 R/W task files found in {}".format(directory))
    datasets = {row["dataset"] for row in matches}
    for ds in datasets:
        have = {(r["R"], r["W"]) for r in matches if r["dataset"] == ds}
        if have != {("0","0"), ("0","1"), ("1","0"), ("1","1")}:
            raise ValueError("{} missing Fig. 13 combinations: {}".format(ds, have))
    if output.exists():
        raise FileExistsError("Refusing to overwrite: {}".format(output))
    mean_path = output.with_name(output.stem + "_means.csv")
    if mean_path.exists():
        raise FileExistsError("Refusing to overwrite: {}".format(mean_path))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(matches[0]))
        writer.writeheader()
        writer.writerows(matches)
    with mean_path.open("x", newline="", encoding="utf-8") as stream:
        columns = ("dataset","R","W","trials","candidate_count_mean",
                   "generation_z_window_checks_mean",
                   "counting_distance_checks_mean",
                   "generation_plus_counting_checks_mean")
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for ds in sorted(datasets):
            for r in ("0","1"):
                for w in ("0","1"):
                    rows = [x for x in matches if
                            x["dataset"]==ds and x["R"]==r and x["W"]==w]
                    writer.writerow({
                        "dataset":ds,"R":r,"W":w,"trials":len(rows),
                        "candidate_count_mean":statistics.mean(
                            x["candidate_count"] for x in rows),
                        "generation_z_window_checks_mean":statistics.mean(
                            x["generation_z_window_checks"] for x in rows),
                        "counting_distance_checks_mean":statistics.mean(
                            x["counting_distance_checks"] for x in rows),
                        "generation_plus_counting_checks_mean":statistics.mean(
                            x["generation_plus_counting_checks"] for x in rows),
                    })
    return len(matches)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: derive_fig14.py INPUT_FIG13_DIR NEW_FIG14_CSV")
    count = derive(Path(sys.argv[1]), Path(sys.argv[2]))
    print("Derived formal-task checks from {} Fig. 13 runs".format(count))
