"""Small end-to-end preprocessing smoke tests using the three real raw adapters."""
import csv
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


class ThreeDatasetEntryPointTest(unittest.TestCase):
    @staticmethod
    def raw_inputs(root):
        geolife = root / "Geolife Trajectories 1.3.zip"
        hdr = "Geolife trajectory\nWGS 84\nAltitude is in Feet\nReserved 3\n0\n0\n"
        rows = "".join(
            "{:.6f},{:.6f},0,1,2,2008-01-01,00:00:00\n".format(
                39.900 + i * .002, 116.400 + i * .002
            ) for i in range(6)
        )
        with zipfile.ZipFile(geolife, "w") as z:
            z.writestr("Data/000/Trajectory/a.plt", hdr + rows)
        tdrive = root / "tdrive"
        tdrive.mkdir()
        (tdrive / "taxi.txt").write_text("".join(
            "1,2008-02-02 15:36:08,{:.6f},{:.6f}\n".format(
                116.500 + i * .002, 39.920 + i * .002
            ) for i in range(6)
        ), encoding="utf-8")
        porto = root / "train.csv"
        with porto.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["TRIP_ID", "POLYLINE"])
            w.writeheader()
            w.writerow({"TRIP_ID": "1", "POLYLINE": json.dumps([
                [-8.620 + i * .002, 41.150 + i * .002] for i in range(6)
            ])})
        return geolife, tdrive, porto

    @staticmethod
    def call(script, env, *args):
        return subprocess.run(["bash", str(SCRIPTS / script), *args],
                              env=env, capture_output=True, text=True)

    def test_all_datasets_seeds_nested_output_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            geo, td, po = self.raw_inputs(root)
            work = root / "work"
            env = dict(os.environ)
            env.update(GEOLIFE_INPUT=str(geo), TDRIVE_INPUT=str(td),
                       PORTO_INPUT=str(po), WORK_ROOT=str(work),
                       SORT_MEMORY="16M", SORT_PARALLELISM="1")
            p = self.call("prepare_all.sh", env)
            self.assertEqual(0, p.returncode, p.stderr)
            for ds in ("geolife", "tdrive", "porto"):
                output = work / "prepared" / "{}_xy.txt".format(ds)
                self.assertGreaterEqual(len(output.read_text().splitlines()), 3)
                meta = json.loads((work / "metadata" / "{}_stats.json".format(ds)).read_text())
                self.assertEqual(ds, meta["dataset"])
            p = self.call("create_subsets.sh", env,
                          "--small-size", "2", "--large-size", "3")
            self.assertEqual(0, p.returncode, p.stderr)
            meta = json.loads((work / "metadata" / "subsets_stats.json").read_text())
            self.assertEqual({"geolife", "tdrive", "porto"}, set(meta["datasets"]))
            for ds in ("geolife", "tdrive", "porto"):
                small = work / "subsets" / "{}_1m_xy.txt".format(ds)
                large = work / "subsets" / "{}_3m_xy.txt".format(ds)
                self.assertEqual(2, len(small.read_text().splitlines()))
                self.assertEqual(3, len(large.read_text().splitlines()))
                self.assertTrue(set(small.read_text().splitlines()).issubset(large.read_text().splitlines()))
                expected_seed = 20260925 if ds == "geolife" else 20260924
                self.assertEqual(expected_seed, meta["datasets"][ds]["seed"])
                self.assertEqual(hashlib.sha256(large.read_bytes()).hexdigest(),
                                 meta["datasets"][ds]["large_sha256"])
            p = self.call("create_subsets.sh", env,
                          "--small-size", "2", "--large-size", "3")
            self.assertNotEqual(0, p.returncode)
            self.assertIn("refusing to overwrite", p.stderr)
            p = self.call("prepare_all.sh", env)
            self.assertNotEqual(0, p.returncode)
            self.assertIn("Refusing to overwrite", p.stderr)

    def test_missing_last_input_fails_before_creating_any_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            geo, td, _ = self.raw_inputs(root)
            env = dict(os.environ)
            env.update(GEOLIFE_INPUT=str(geo), TDRIVE_INPUT=str(td),
                       PORTO_INPUT=str(root / "missing.csv"),
                       WORK_ROOT=str(root / "work"))
            p = self.call("prepare_all.sh", env)
            self.assertNotEqual(0, p.returncode)
            self.assertIn("Missing porto", p.stderr)
            self.assertFalse((root / "work" / "prepared").exists())


if __name__ == "__main__":
    unittest.main()
