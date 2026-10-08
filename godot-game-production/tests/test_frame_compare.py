"""Executable contracts for honest, non-destructive frame diagnostics."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'frame_compare.py'


class FrameComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ref = self.root / 'reference.png'
        self.cap = self.root / 'capture.png'
        self.out = self.root / 'report'
        Image.new('RGB', (8, 8), 'black').save(self.ref)
        Image.new('RGB', (8, 8), 'black').save(self.cap)

    def run_tool(self, regions=None):
        self.assertTrue(SCRIPT.exists(), 'Frame comparison capability is absent')
        cmd = [sys.executable, str(SCRIPT), '--reference', str(self.ref),
               '--capture', str(self.cap), '--out', str(self.out)]
        if regions is not None:
            path = self.root / 'regions.json'
            path.write_text(json.dumps(regions), encoding='utf-8')
            cmd += ['--regions', str(path)]
        return subprocess.run(cmd, capture_output=True, text=True)

    def report(self):
        return json.loads((self.out / 'report.json').read_text(encoding='utf-8'))

    def test_identical_images_are_diagnostic_not_acceptance(self):
        result = self.run_tool()
        self.assertEqual(0, result.returncode, result.stderr)
        report = self.report()
        self.assertEqual('DIAGNOSTIC_ONLY', report['status'])
        self.assertEqual(0, report['regions']['frame']['rgb_mae'])
        self.assertEqual(1, report['regions']['frame']['palette_overlap'])
        self.assertEqual(hashlib.sha256(self.ref.read_bytes()).hexdigest(), report['reference']['sha256'])
        with Image.open(self.out / 'side-by-side.png') as side:
            self.assertEqual((16, 8), side.size)
        with Image.open(self.out / 'difference.png') as difference:
            self.assertEqual((8, 8), difference.size)

    def test_black_white_difference_has_hand_derived_metrics(self):
        Image.new('RGB', (8, 8), 'white').save(self.cap)
        result = self.run_tool({'whole': [0, 0, 8, 8]})
        self.assertEqual(0, result.returncode, result.stderr)
        metrics = self.report()['regions']['whole']
        self.assertEqual(1, metrics['rgb_mae'])
        self.assertAlmostEqual(1, metrics['luminance_delta'], places=6)
        self.assertEqual(0, metrics['palette_overlap'])

    def test_changed_region_ranks_before_unchanged_region(self):
        image = Image.new('RGB', (8, 8), 'black')
        image.paste('white', (4, 0, 8, 8))
        image.save(self.cap)
        result = self.run_tool({'left': [0, 0, 4, 8], 'right': [4, 0, 8, 8]})
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(['right', 'left'], self.report()['ranked_regions'])
        self.assertEqual(0, self.report()['regions']['left']['rgb_mae'])

    def test_mismatched_dimensions_are_not_resized(self):
        Image.new('RGB', (16, 8)).save(self.cap)
        self.assertEqual(3, self.run_tool().returncode)
        self.assertFalse(self.out.exists())

    def test_ranking_uses_region_bounds_instead_of_reserved_names(self):
        image = Image.new('RGB', (8, 8), 'black')
        image.paste('white', (0, 0, 4, 8))
        image.save(self.cap)
        cases = [
            ({'frame': [0, 0, 4, 8], 'quiet': [4, 0, 8, 8]}, ['frame', 'quiet']),
            ({'whole': [0, 0, 8, 8], 'changed': [0, 0, 4, 8], 'quiet': [4, 0, 8, 8]},
             ['changed', 'quiet']),
            ({'frame': [0, 0, 8, 8], 'also_whole': [0, 0, 8, 8]}, ['also_whole', 'frame']),
        ]
        for index, (regions, expected) in enumerate(cases):
            with self.subTest(regions=regions):
                self.out = self.root / f'report-{index}'
                result = self.run_tool(regions)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual(expected, self.report()['ranked_regions'])

    def test_transparent_image_requires_explicit_compositing(self):
        Image.new('RGBA', (8, 8), (0, 0, 0, 0)).save(self.cap)
        self.assertEqual(3, self.run_tool().returncode)
        self.assertFalse(self.out.exists())

    def test_invalid_regions_are_rejected(self):
        for regions in ({}, {'x': [0, 0, 0, 8]}, {'x': [-1, 0, 4, 4]},
                        {'x': [0, 0, 9, 8]}, {'x': [False, 0, 4, 4]}, {'': [0, 0, 4, 4]}):
            with self.subTest(regions=regions):
                self.assertEqual(3, self.run_tool(regions).returncode)
                self.assertFalse(self.out.exists())

    def test_existing_output_is_preserved(self):
        self.out.mkdir()
        marker = self.out / 'report.json'
        marker.write_text('previous report', encoding='utf-8')
        self.assertEqual(3, self.run_tool().returncode)
        self.assertEqual('previous report', marker.read_text(encoding='utf-8'))

    def test_input_bytes_are_unchanged(self):
        before = (self.ref.read_bytes(), self.cap.read_bytes())
        self.assertEqual(0, self.run_tool().returncode)
        self.assertEqual(before, (self.ref.read_bytes(), self.cap.read_bytes()))

    def test_corrupt_image_is_reported_without_outputs(self):
        self.cap.write_bytes(b'not an image')
        self.assertEqual(3, self.run_tool().returncode)
        self.assertFalse(self.out.exists())


if __name__ == '__main__':
    unittest.main()
