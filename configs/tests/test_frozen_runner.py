import unittest

from test_paper_runner import dry_run


class FrozenPaperCommandsTest(unittest.TestCase):
    def test_joint_vs_greedy_uses_one_snapshot(self):
        rows, _ = dry_run("fig11b")
        self.assertEqual(14, len(rows))
        snapshots = [x for x in rows if x[2].get("spark.skyline.microFrozenStateExport") == "true"]
        self.assertEqual(2, len(snapshots))
        replays = [x for x in rows if "spark.skyline.microFrozenStateLoad" in x[2]]
        self.assertEqual(12, len(replays))
        self.assertEqual({"joint_peak", "work_greedy"},
                         {x[2]["spark.skyline.microSelector"] for x in replays})
        for ds in ("geolife", "tdrive"):
            batch = [x for x in replays if "/" + ds + "_2m_" in x[1][8]]
            self.assertEqual(6, len(batch))
            self.assertEqual(1, len({
                x[2]["spark.skyline.microFrozenStateLoad"] for x in batch
            }))
            self.assertTrue(all(x[2]["spark.skyline.inputSha256"] == "DRY_RUN_INPUT_SHA256"
                                for x in batch))

    def test_four_R_W_combinations_share_frozen_input(self):
        rows, _ = dry_run("fig13")
        self.assertEqual(26, len(rows))
        captures = [x for x in rows if x[2].get("spark.skyline.microFrozenStateExport") == "true"]
        self.assertEqual(2, len(captures))
        for ds in ("geolife", "tdrive"):
            batch = [x for x in rows if "spark.skyline.microFrozenStateLoad" in x[2]
                     and "/" + ds + "_" in x[1][8]]
            self.assertEqual(12, len(batch))
            self.assertEqual(1, len({
                x[2]["spark.skyline.microFrozenStateLoad"] for x in batch
            }))
            settings = {
                (x[2]["spark.skyline.experiment.microCompletionReuse"],
                 x[2]["spark.skyline.experiment.microProbeFrontier"])
                for x in batch
            }
            self.assertEqual({
                ("false","false"),("false","true"),("true","false"),("true","true")
            }, settings)

    def test_fig14_does_not_start_spark(self):
        rows, _ = dry_run("fig14")
        self.assertEqual([], rows)


if __name__ == "__main__":
    unittest.main()
