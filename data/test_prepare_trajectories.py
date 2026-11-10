import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('prepare_trajectories.py')


class TrajectoryPreparationTest(unittest.TestCase):
    def call(self, dataset, source, output, *opts):
        return subprocess.run([sys.executable, str(SCRIPT), '--dataset', dataset,
                               '--input', str(source), '--output', str(output), *opts],
                              capture_output=True, text=True, check=True)

    def check_output(self, output, expected):
        lines = output.read_text().strip().splitlines()
        self.assertEqual(len(lines), expected)
        self.assertEqual(len(set(lines)), expected)
        points = [tuple(float(v) for v in line.split()) for line in lines]
        self.assertEqual(min(x for x, _ in points), 0.0)
        self.assertEqual(min(y for _, y in points), 0.0)
        self.assertTrue(all(len(line.split()) == 2 for line in lines))
        self.assertTrue(all(len(c.split('.')[1]) == 3 for line in lines for c in line.split()))
        return json.loads(Path(str(output) + '.meta.json').read_text())

    def test_geolife(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            src = d / 'geo'
            src.mkdir()
            header = 'Geolife trajectory\nWGS 84\nAltitude is in Feet\nReserved 3\n0,2,255,My Track,0,0,2,8421376\n0\n'
            (src/'a.plt').write_text(header + '39.9,116.4,0,0,0,2008-01-01,00:00\n39.9,116.4,0,0,0,2008-01-01,00:00\n39.91,116.41,0,0,0,2008-01-01,00:01\n30,100,0,0,0,0,0\n')
            out = d / 'geo.txt'
            self.call('geolife', src, out, '--sample-sizes', '1,2', '--seed', '20260925')
            meta = self.check_output(out, 2)
            self.assertEqual(meta['counts']['outside_bbox'], 1)
            self.assertEqual(len(Path(str(out)+'.sample_1.txt').read_text().splitlines()), 1)

    def test_tdrive(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            src = d/'1.txt'
            src.write_text('102,2008-02-02 13:34:27,116.30826,39.94702\n102,2008-02-02 13:34:28,116.30826,39.94702\n103,2008-02-02 13:35:00,116.32000,39.94800\n')
            out = d/'t.txt'
            self.call('tdrive', src, out)
            self.check_output(out, 2)

    def test_porto(self):
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            src = d/'train.csv'
            src.write_text('TRIP_ID,POLYLINE\nabc,"[[-8.62,41.14],[-8.63,41.15],[-8.62,41.14]]"\n')
            out = d/'p.txt'
            self.call('porto', src, out)
            self.check_output(out, 2)


if __name__ == '__main__':
    unittest.main()
