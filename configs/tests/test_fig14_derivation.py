import csv
import tempfile
import unittest
from pathlib import Path

from configs.derive_fig14 import derive


class Fig14DerivationTest(unittest.TestCase):
    def test_four_combinations_same_task_sources(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            data = root / "fig13"
            data.mkdir()
            for ds, size in (("geolife", "2m"), ("tdrive", "3m")):
                for r in ("0","1"):
                    for w in ("0","1"):
                        for trial in (1,2,3):
                            path = data / (
                                "{}_{}_R{}W{}_dismc_trial{}.txt.micro_tasks.csv".format(
                                    ds,size,r,w,trial)
                            )
                            with path.open("w",newline="") as f:
                                writer = csv.writer(f)
                                writer.writerow(["stage_id","partition_id",
                                                 "candidate_count","z_window_checks",
                                                 "distance_checks"])
                                writer.writerow([1,0,4,10,30])
                                writer.writerow([1,1,3,5,50])
            dest = root / "fig14.csv"
            self.assertEqual(24, derive(data,dest))
            with dest.open(newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(24,len(rows))
            self.assertEqual("95",rows[0]["generation_plus_counting_checks"])
            mean_path = root / "fig14_means.csv"
            with mean_path.open(newline="") as f:
                means = list(csv.DictReader(f))
            self.assertEqual(8,len(means))
            with self.assertRaises(FileExistsError):
                derive(data,dest)


if __name__ == "__main__":
    unittest.main()
