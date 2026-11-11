import os
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "configs" / "run_paper_suite.sh"
PREFIXER = ROOT / "configs" / "prepare_paper_subsets.sh"


def dry_run(figure, trials=3):
    env = dict(os.environ)
    env.pop("DRIVER_MEMORY", None)
    env.update(DRY_RUN="1", TRIALS=str(trials),
               DATA_DIR="/tmp/fixture-paper-data",
               OUT_DIR="/tmp/paper-results-unexecuted")
    result = subprocess.run(
        ["bash", str(RUNNER), figure], env=env, capture_output=True, text=True
    )
    if result.returncode:
        raise AssertionError("{} failed:\n{}\n{}".format(
            figure, result.stdout, result.stderr
        ))
    records = []
    for line in result.stdout.splitlines():
        if not line.startswith("QUERY_X="):
            continue
        parts = shlex.split(line)
        context = dict(x.split("=", 1) for x in parts[:4])
        assert parts[4] == "bash"
        if parts[5].endswith("configs/run_spatial_operator.sh"):
            records.append((context, parts, {"__operator__": "true"}))
            continue
        assert parts[5].endswith("scripts/run_profile.sh")
        opts = parts[parts.index("--") + 1:] if "--" in parts else []
        assert len(opts) % 2 == 0
        config = dict(x.split("=", 1) for key, x in zip(opts[::2], opts[1::2])
                      if key == "--conf")
        records.append((context, parts, config))
    return records, result.stderr


class PaperCommandMatrixTest(unittest.TestCase):
    def test_fixed_queries_and_no_probe_static_comparator(self):
        rows, _ = dry_run("fig4")
        self.assertEqual(48, len(rows))
        seen = set()
        for env, parts, conf in rows:
            self.assertEqual("8G", env["DRIVER_MEMORY"])
            self.assertEqual("200", parts[9])
            self.assertIn(parts[10], ("100", "300"))
            self.assertEqual("0.05", conf["spark.skyline.shardReadBudget"])
            method = "static" if "_static_" in parts[8] else "dismc"
            seen.add(method)
            if method == "static":
                self.assertEqual("peak", conf["spark.skyline.experiment.microPlannerPolicy"])
                self.assertEqual("work_greedy", conf["spark.skyline.microSelector"])
                self.assertEqual("false", conf["spark.skyline.experiment.microProbeFrontier"])
                self.assertEqual("false", conf["spark.skyline.experiment.microCompletionReuse"])
                self.assertEqual("false", conf["spark.skyline.microCalibratePooledFrontier"])
            else:
                self.assertEqual("sampled_peak", conf["spark.skyline.experiment.microPlannerPolicy"])
                self.assertEqual("joint_peak", conf["spark.skyline.microSelector"])
        self.assertEqual({"dismc", "static"}, seen)

    def test_full_data_ten_percent_and_queries(self):
        rows, _ = dry_run("table1")
        self.assertEqual(6, len(rows))
        self.assertEqual({
            ("124414.676", "106577.117", "20"),
            ("116808.495", "114686.700", "200")
        }, {(env["QUERY_X"], env["QUERY_Y"], parts[10]) for env, parts, _ in rows})
        for _, _, conf in rows:
            self.assertEqual("0.10", conf["spark.skyline.shardReadBudget"])
            self.assertEqual("8", conf["spark.skyline.microProbeCoverageAnchors"])
            self.assertEqual("8", conf["spark.skyline.microLaneProbeMaxOwners"])

    def test_fig11a_refresh_and_refinement_compatible(self):
        rows, _ = dry_run("fig11a")
        self.assertEqual(12, len(rows))
        self.assertEqual(
            {"true", "false"},
            {conf["spark.skyline.microLaneParentReplay"] for _, _, conf in rows}
        )
        for _, _, conf in rows:
            self.assertEqual("true", conf["spark.skyline.microRefreshCandidates"])
            self.assertEqual("true", conf["spark.skyline.microLaneProbeRefinement"])
            self.assertEqual("sampled", conf["spark.skyline.experiment.microCostSignal"])

    def test_fig12_work_signal_modes(self):
        rows, log = dry_run("fig12")
        self.assertEqual(18, len(rows))
        self.assertIn("Fig. 12: Unit / Static / Sampled", log)
        self.assertEqual(
            {"unit", "static", "sampled"},
            {conf["spark.skyline.experiment.microCostSignal"] for _, _, conf in rows}
        )
        for _, _, conf in rows:
            self.assertEqual("false", conf["spark.skyline.microRefreshCandidates"])
            self.assertEqual("false", conf["spark.skyline.microLaneProbeRefinement"])

    def test_input_policy_matrix(self):
        rows, _ = dry_run("fig10")
        self.assertEqual(36, len(rows))
        self.assertEqual(
            {"spatial_full", "dependency"},
            {conf["spark.skyline.experiment.microPartitionMode"] for _, _, conf in rows}
        )
        self.assertEqual(
            {"15", "20", "30", "56.25", "75", "112.5"},
            {parts[10] for _, parts, _ in rows}
        )

    def test_core_scaling(self):
        rows, _ = dry_run("fig9")
        self.assertEqual(30, len(rows))
        self.assertEqual(
            {"8", "16", "24", "32", "40"},
            {env["TOTAL_EXECUTOR_CORES"] for env, _, _ in rows}
        )

    def test_available_baseline_and_size_sweeps(self):
        for fig, count in [("fig6", 30), ("fig7", 36), ("fig8", 108)]:
            with self.subTest(fig=fig):
                rows, message = dry_run(fig)
                self.assertEqual(count, len(rows))
                if fig in ("fig6", "fig7"):
                    operator_rows = [r for r in rows if "__operator__" in r[2]]
                    self.assertEqual(6 if fig == "fig6" else 18, len(operator_rows))

    def test_fig5_is_derived(self):
        rows, message = dry_run("fig5")
        self.assertEqual([], rows)

    def test_prefix_generation_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory() as temp:
            subsets = Path(temp) / "subsets"
            subsets.mkdir()
            # Synthetic 1M/3M streams exercise real paper-size prefix counts.
            for ds in ("geolife", "tdrive", "porto"):
                (subsets / "{}_1m_xy.txt".format(ds)).write_bytes(b"0 0\n" * 1000000)
            for ds in ("geolife", "tdrive"):
                (subsets / "{}_3m_xy.txt".format(ds)).write_bytes(b"1 1\n" * 3000000)
            env = dict(os.environ, DATA_DIR=temp)
            first = subprocess.run(["bash", str(PREFIXER)], env=env, text=True,
                                   capture_output=True)
            self.assertEqual(0, first.returncode, first.stderr)
            for ds in ("geolife", "tdrive", "porto"):
                for count in (100, 200, 400, 600, 800):
                    p = subsets / "{}_{}k_xy.txt".format(ds, count)
                    self.assertEqual(count * 1000, p.read_bytes().count(b"\n"))
            for ds in ("geolife", "tdrive"):
                self.assertEqual(
                    2000000,
                    (subsets / "{}_2m_xy.txt".format(ds)).read_bytes().count(b"\n")
                )
            again = subprocess.run(["bash", str(PREFIXER)], env=env, text=True,
                                   capture_output=True)
            self.assertNotEqual(0, again.returncode)
            self.assertIn("Refusing to overwrite", again.stderr)


if __name__ == "__main__":
    unittest.main()
