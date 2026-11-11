import tempfile
import unittest
from pathlib import Path

from scripts.create_subsets import create_nested_subsets


class NestedSubsetTest(unittest.TestCase):
    def test_creates_reproducible_nested_subsets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.txt"
            source.write_text(
                "".join(f"{index}.000 {index + 1}.000\n" for index in range(20)),
                encoding="utf-8",
            )
            first_small = root / "first_5.txt"
            first_large = root / "first_10.txt"
            second_small = root / "second_5.txt"
            second_large = root / "second_10.txt"

            first = create_nested_subsets(
                source, first_small, first_large, 5, 10, seed=20260924
            )
            second = create_nested_subsets(
                source, second_small, second_large, 5, 10, seed=20260924
            )

            small_lines = first_small.read_text(encoding="utf-8").splitlines()
            large_lines = first_large.read_text(encoding="utf-8").splitlines()
            self.assertEqual(5, len(small_lines))
            self.assertEqual(10, len(large_lines))
            self.assertTrue(set(small_lines).issubset(large_lines))
            self.assertEqual(first_small.read_bytes(), second_small.read_bytes())
            self.assertEqual(first_large.read_bytes(), second_large.read_bytes())
            self.assertEqual(first, second)
            self.assertEqual(20, first["source_line_count"])
            self.assertEqual(5, first["small_line_count"])
            self.assertEqual(10, first["large_line_count"])

    def test_rejects_source_smaller_than_requested_subset(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.txt"
            source.write_text("0.000 0.000\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "fewer than 2 lines"):
                create_nested_subsets(
                    source, root / "small.txt", root / "large.txt", 1, 2, seed=7
                )


if __name__ == "__main__":
    unittest.main()
