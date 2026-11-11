import tempfile
import unittest
from pathlib import Path

from scripts.extend_subsets import extend_nested_subsets


class ExtendSubsetTest(unittest.TestCase):
    def test_extends_existing_base_and_is_reproducible(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.txt"
            base = root / "base.txt"
            source.write_bytes(b"".join(
                "{:03d} 0\n".format(index).encode("ascii")
                for index in range(20)
            ))
            base.write_bytes(source.read_bytes()[:5 * len(b"000 0\n")])
            first_medium = root / "first_8.txt"
            first_large = root / "first_12.txt"
            second_medium = root / "second_8.txt"
            second_large = root / "second_12.txt"

            first = extend_nested_subsets(
                source, base, first_medium, first_large,
                base_size=5, medium_size=8, large_size=12, seed=7,
            )
            second = extend_nested_subsets(
                source, base, second_medium, second_large,
                base_size=5, medium_size=8, large_size=12, seed=7,
            )

            self.assertEqual(first, second)
            self.assertEqual(first_medium.read_bytes(), second_medium.read_bytes())
            self.assertEqual(first_large.read_bytes(), second_large.read_bytes())
            medium = set(first_medium.read_bytes().splitlines())
            large = set(first_large.read_bytes().splitlines())
            self.assertEqual(8, len(medium))
            self.assertEqual(12, len(large))
            self.assertTrue(set(base.read_bytes().splitlines()).issubset(medium))
            self.assertTrue(medium.issubset(large))


if __name__ == "__main__":
    unittest.main()
