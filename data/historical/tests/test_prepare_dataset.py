import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from pyproj import Transformer

from scripts.prepare_dataset import (
    DATASET_CONFIGS,
    format_coordinate,
    external_unique,
    iter_geonames,
    iter_porto,
    iter_tdrive,
    iter_geolife,
    new_counters,
    project_points,
    translate_unique,
    validate_output,
)


class AdapterTest(unittest.TestCase):
    def test_geolife_reads_plt_points_after_four_header_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "geolife.zip"
            with zipfile.ZipFile(archive, "w") as output:
                output.writestr(
                    "Data/000/Trajectory/a.plt",
                    "Geolife trajectory\nWGS 84\nAltitude is in Feet\n"
                    "Reserved 3\n0\n0\n39.9,116.4,0,1,2,date,time\n",
                )
            counters = new_counters()
            points = list(iter_geolife(archive, counters))

        self.assertEqual([(116.4, 39.9)], points)
        self.assertEqual(1, counters["coordinate_pairs_seen"])

    def test_geonames_reads_longitude_then_latitude_and_counts_invalid_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "allCountries.txt"
            source.write_text(
                "1\tname\tascii\taliases\t42.58765\t1.7418\tT\tPK\n"
                "broken\n"
                "2\tname\tascii\taliases\t95\t1.0\tT\tPK\n",
                encoding="utf-8",
            )
            counters = new_counters()

            points = list(iter_geonames(source, counters))

        self.assertEqual([(1.7418, 42.58765)], points)
        self.assertEqual(3, counters["source_records"])
        self.assertEqual(1, counters["malformed_records"])
        self.assertEqual(1, counters["invalid_coordinates"])


class ProjectionTest(unittest.TestCase):
    def test_format_coordinate_rounds_and_normalizes_negative_zero(self):
        self.assertEqual("0.000", format_coordinate(-0.0004))
        self.assertEqual("12.346", format_coordinate(12.3456))

    def test_geonames_projection_uses_longitude_as_x(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "projected.txt"
            counters = new_counters()
            project_points([(10.0, 0.0)], "geonames", output, counters)
            x_text, y_text = output.read_text(encoding="utf-8").split()

        self.assertAlmostEqual(964862.803, float(x_text), delta=1.0)
        self.assertEqual(0.0, float(y_text))
        self.assertEqual(1, counters["valid_projected_points"])

    def test_projection_rejects_points_outside_target_crs_area(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "projected.txt"
            counters = new_counters()

            project_points([(10.0, 45.0), (0.0, 89.0)], "geonames", output, counters)

            self.assertEqual(1, len(output.read_text(encoding="utf-8").splitlines()))
            self.assertEqual(1, counters["valid_projected_points"])
            self.assertEqual(1, counters["outside_projection_area"])

    def test_projection_rejects_points_outside_dataset_study_area(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "projected.txt"
            counters = new_counters()

            project_points([(116.4, 39.9), (119.0, 60.0)], "tdrive", output, counters)

            self.assertEqual(1, len(output.read_text(encoding="utf-8").splitlines()))
            self.assertEqual(1, counters["valid_projected_points"])
            self.assertEqual(1, counters["outside_dataset_area"])

    def test_each_projection_round_trips_representative_coordinate(self):
        examples = {
            "geonames": (10.0, 45.0),
            "tdrive": (116.4, 39.9),
            "porto": (-8.62, 41.15),
        }
        for dataset, (longitude, latitude) in examples.items():
            target_crs = DATASET_CONFIGS[dataset]["target_crs"]
            forward = Transformer.from_crs("EPSG:4326", target_crs, always_xy=True)
            inverse = Transformer.from_crs(target_crs, "EPSG:4326", always_xy=True)
            x, y = forward.transform(longitude, latitude)
            actual_longitude, actual_latitude = inverse.transform(x, y)
            self.assertAlmostEqual(longitude, actual_longitude, places=7)
            self.assertAlmostEqual(latitude, actual_latitude, places=7)

    def test_tdrive_recurses_in_stable_order_and_counts_bad_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "b.txt").write_text(
                "2,2008-02-02 15:36:08,116.6,39.9\n",
                encoding="utf-8",
            )
            (root / "a.txt").write_text(
                "1,2008-02-02 15:36:08,116.51172,39.92123\n"
                "malformed\n",
                encoding="utf-8",
            )
            counters = new_counters()

            points = list(iter_tdrive(root, counters))

        self.assertEqual([(116.51172, 39.92123), (116.6, 39.9)], points)
        self.assertEqual(3, counters["source_records"])
        self.assertEqual(1, counters["malformed_records"])

    def test_porto_streams_polylines_and_accepts_empty_trajectory(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "train.csv"
            with source.open("w", encoding="utf-8", newline="") as output:
                writer = csv.DictWriter(output, fieldnames=["TRIP_ID", "POLYLINE"])
                writer.writeheader()
                writer.writerow({
                    "TRIP_ID": "1",
                    "POLYLINE": json.dumps([
                        [-8.618643, 41.141412],
                        [-8.618499, 41.141376],
                    ]),
                })
                writer.writerow({"TRIP_ID": "2", "POLYLINE": "[]"})
            counters = new_counters()

            points = list(iter_porto(source, counters))

        self.assertEqual(
            [(-8.618643, 41.141412), (-8.618499, 41.141376)],
            points,
        )
        self.assertEqual(2, counters["source_records"])
        self.assertEqual(1, counters["empty_trajectories"])

    def test_porto_counts_malformed_json_and_coordinate_pairs(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "train.csv"
            with source.open("w", encoding="utf-8", newline="") as output:
                writer = csv.DictWriter(output, fieldnames=["TRIP_ID", "POLYLINE"])
                writer.writeheader()
                writer.writerow({"TRIP_ID": "1", "POLYLINE": "not-json"})
                writer.writerow({"TRIP_ID": "2", "POLYLINE": "[[1]]"})
                writer.writerow({"TRIP_ID": "3", "POLYLINE": "[[181,0]]"})
            counters = new_counters()

            points = list(iter_porto(source, counters))

        self.assertEqual([], points)
        self.assertEqual(1, counters["parse_errors"])
        self.assertEqual(1, counters["malformed_coordinate_pairs"])
        self.assertEqual(1, counters["invalid_coordinates"])


class PipelineTest(unittest.TestCase):
    def test_external_unique_removes_duplicate_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "projected.txt"
            unique = root / "unique.txt"
            source.write_text("2.000 3.000\n1.000 1.000\n2.000 3.000\n", encoding="utf-8")

            external_unique(source, unique, "16M", 1, root)

            self.assertEqual(
                ["1.000 1.000", "2.000 3.000"],
                unique.read_text(encoding="utf-8").splitlines(),
            )

    def test_translation_preserves_distance_and_makes_minima_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "unique.txt"
            output = root / "prepared.txt"
            source.write_text("-100.000 -200.000\n-90.000 -195.000\n", encoding="utf-8")

            stats = translate_unique(source, output)

            lines = output.read_text(encoding="utf-8").splitlines()
            self.assertEqual(["0.000 0.000", "10.000 5.000"], lines)
            self.assertEqual(2, stats["unique_points"])
            self.assertEqual(100.0, stats["translation_offset_x"])
            self.assertEqual(200.0, stats["translation_offset_y"])
            before_distance = ((10.0 ** 2) + (5.0 ** 2)) ** 0.5
            after = [tuple(map(float, line.split())) for line in lines]
            after_distance = (
                (after[1][0] - after[0][0]) ** 2
                + (after[1][1] - after[0][1]) ** 2
            ) ** 0.5
            self.assertAlmostEqual(before_distance, after_distance)

    def test_malformed_unique_input_does_not_replace_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "unique.txt"
            output = root / "prepared.txt"
            source.write_text("1.000 2.000\nbroken\n", encoding="utf-8")
            output.write_text("sentinel\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                translate_unique(source, output)

            self.assertEqual("sentinel\n", output.read_text(encoding="utf-8"))

    def test_validate_output_checks_count_shape_and_nonnegative_values(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "prepared.txt"
            output.write_text("0.000 0.000\n10.000 5.000\n", encoding="utf-8")

            stats = validate_output(output, 2)

            self.assertEqual(2, stats["line_count"])
            self.assertEqual(0.0, stats["min_x"])
            self.assertEqual(10.0, stats["max_x"])
            self.assertEqual(0.0, stats["min_y"])
            self.assertEqual(5.0, stats["max_y"])


class CliTest(unittest.TestCase):
    def _command(self, source, output, stats, temporary_root):
        return [
            sys.executable,
            "scripts/prepare_dataset.py",
            "--dataset",
            "geonames",
            "--input",
            str(source),
            "--output",
            str(output),
            "--stats",
            str(stats),
            "--temp-root",
            str(temporary_root),
            "--sort-memory",
            "16M",
            "--sort-parallelism",
            "1",
        ]

    def test_cli_publishes_output_and_auditable_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "geonames.txt"
            output = root / "prepared.txt"
            stats_path = root / "stats.json"
            source.write_text(
                "1\tn\ta\tb\t0\t10\tT\tPK\n"
                "2\tn\ta\tb\t0\t10\tT\tPK\n"
                "3\tn\ta\tb\t1\t11\tT\tPK\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                self._command(source, output, stats_path, root),
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            stats = json.loads(stats_path.read_text(encoding="utf-8"))
            digest = hashlib.sha256(output.read_bytes()).hexdigest()
            self.assertEqual(2, stats["unique_points"])
            self.assertEqual(3, stats["valid_projected_points"])
            self.assertEqual(digest, stats["output_sha256"])
            self.assertEqual(2, stats["output_line_count"])
            self.assertEqual("EPSG:6933", stats["target_crs"])
            self.assertEqual("geonames", stats["dataset"])
            self.assertIn("scripts/prepare_dataset.py", stats["command"])

            original = output.read_bytes()
            second = subprocess.run(
                self._command(source, output, stats_path, root),
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(0, second.returncode)
            self.assertEqual(original, output.read_bytes())

    def test_cli_rejects_error_rate_above_threshold_without_publishing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "geonames.txt"
            output = root / "prepared.txt"
            stats_path = root / "stats.json"
            source.write_text(
                "1\tn\ta\tb\t0\t10\tT\tPK\nmalformed\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                self._command(source, output, stats_path, root),
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertFalse(output.exists())
            self.assertFalse(stats_path.exists())
            self.assertIn("error rate", result.stderr)


if __name__ == "__main__":
    unittest.main()
