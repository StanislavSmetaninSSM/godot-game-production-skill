"""Known telemetry counterexamples and coverage failures, through the real CLI."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'motion_check.py'


def sample(t, point, reference=None, contact=True):
    return {'t': t, 'point': point, 'reference': reference or [0] * len(point), 'contact': contact}


def check(kind='contact_drift', samples=None, limit=0.1):
    return {'id': 'hero', 'kind': kind, 'applies': True, 'max_value': limit,
            'threshold_reason': 'Fixture requirement',
            'samples': samples if samples is not None else [sample(0, [0, 0]), sample(1, [0, 0])]}


def capture(row=None, size=2):
    return {'schema': 'godot-motion-capture/v1',
            'source': {'kind': 'synthetic', 'build_id': 'fixture-v1',
                       'dimension': '3d' if size == 3 else '2d', 'vector_size': size,
                       'coordinate_space': 'world', 'unit': 'm' if size == 3 else 'px',
                       'scenario': 'controlled-test', 'evidence': ['synthetic fixture']},
            'required_checks': ['hero'], 'checks': [row if row is not None else check()]}


class MotionCheckTests(unittest.TestCase):
    def run_tool(self, data, raw=None):
        self.assertTrue(SCRIPT.exists(), 'Motion diagnostic capability is absent')
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            source, out = root / 'input.json', root / 'report.json'
            content = raw if raw is not None else json.dumps(data)
            source.write_text(content, encoding='utf-8')
            before = source.read_bytes()
            result = subprocess.run([sys.executable, str(SCRIPT), '--input', str(source),
                                     '--report', str(out)], capture_output=True, text=True)
            report = json.loads(out.read_text(encoding='utf-8')) if out.exists() else None
            self.assertEqual(before, source.read_bytes())
            if report:
                self.assertTrue(report['diagnostic_only'])
                self.assertEqual(hashlib.sha256(before).hexdigest(), report['input_sha256'])
            return result.returncode, report

    def test_stationary_contact_passes_and_retains_synthetic_provenance(self):
        code, report = self.run_tool(capture())
        self.assertEqual(0, code)
        self.assertEqual('CHECKS_PASSED', report['status'])
        self.assertEqual('synthetic', report['source']['kind'])
        self.assertEqual(0, report['checks'][0]['measured'])

    def test_drifting_contact_fails_in_2d_and_3d(self):
        for size in (2, 3):
            with self.subTest(size=size):
                rows = [sample(0, [0] * size), sample(1, [1] + [0] * (size - 1))]
                code, report = self.run_tool(capture(check(samples=rows), size))
                self.assertEqual(2, code)
                self.assertEqual(1, report['checks'][0]['measured'])

    def test_moving_support_does_not_count_as_sliding(self):
        rows = [sample(0, [0, 2, 0], [0, 0, 0]), sample(1, [3, 2, 0], [3, 0, 0])]
        code, report = self.run_tool(capture(check(samples=rows), 3))
        self.assertEqual(0, code)
        self.assertEqual(0, report['checks'][0]['measured'])

    def test_swing_separates_stance_intervals(self):
        rows = [sample(0, [0, 0]), sample(1, [0, 0]), sample(2, [5, 2], contact=False),
                sample(3, [10, 0]), sample(4, [10, 0])]
        self.assertEqual(0, self.run_tool(capture(check(samples=rows)))[0])

    def test_without_stance_interval_contact_is_unverified(self):
        rows = [sample(0, [0, 0], contact=False), sample(1, [1, 0])]
        self.assertEqual(1, self.run_tool(capture(check(samples=rows)))[0])

    def test_pose_acceleration_detects_jump_but_not_constant_velocity(self):
        for positions, expected in (([0, 1, 2], 0), ([0, 0, 3], 2)):
            rows = [sample(t, [p, 0]) for t, p in enumerate(positions)]
            self.assertEqual(expected, self.run_tool(capture(check('pose_acceleration', rows, 1)))[0])

    def test_pose_relative_to_root_ignores_translation(self):
        rows = [sample(0, [0, 2], [0, 0]), sample(1, [0, 2], [0, 0]), sample(2, [4, 2], [4, 0])]
        self.assertEqual(0, self.run_tool(capture(check('pose_acceleration', rows, 0)))[0])

    def test_overflowing_time_interval_is_invalid(self):
        rows = [sample(-1e308, [0, 0]), sample(1e308, [1, 0])]
        code, report = self.run_tool(capture(check(samples=rows, limit=0)))
        self.assertEqual(3, code)
        self.assertEqual('INVALID', report['checks'][0]['status'])

    def test_large_finite_mean_interval_does_not_hide_acceleration(self):
        rows = [sample(-1e308, [0, 0]), sample(0, [0, 0]), sample(1e308, [1e308, 0])]
        code, report = self.run_tool(capture(check('pose_acceleration', rows, 0)))
        self.assertEqual(2, code)
        self.assertEqual(1e-308, report['checks'][0]['measured'])

    def test_later_overflow_cannot_hide_behind_a_valid_stance(self):
        rows = [sample(0, [0, 0]), sample(1, [0, 0]), sample(2, [0, 0], contact=False),
                sample(3, [1e308, 0], [-1e308, 0]), sample(4, [1e308, 0], [-1e308, 0])]
        code, report = self.run_tool(capture(check(samples=rows, limit=0)))
        self.assertEqual(3, code)
        self.assertEqual('INVALID', report['checks'][0]['status'])

    def test_anchor_distance_uses_euclidean_norm_and_inclusive_threshold(self):
        row = check('anchor_distance', [sample(0, [3, 4])], 5)
        code, report = self.run_tool(capture(row))
        self.assertEqual(0, code)
        self.assertEqual(5, report['checks'][0]['measured'])
        row['max_value'] = 4.99
        self.assertEqual(2, self.run_tool(capture(row))[0])

    def test_event_offset_is_seconds(self):
        row = check('event_offset', [{'event_time': 10, 'visible_time': 10.25}], 0.2)
        code, report = self.run_tool(capture(row))
        self.assertEqual(2, code)
        self.assertEqual(0.25, report['checks'][0]['measured'])
        self.assertEqual('s', report['checks'][0]['unit'])

    def test_missing_result_and_empty_samples_are_unverified(self):
        data = capture()
        for mutation in ('missing', 'empty', 'no_samples'):
            item = copy.deepcopy(data)
            if mutation == 'missing':
                item['checks'] = []
            elif mutation == 'empty':
                item['checks'][0]['samples'] = []
            else:
                del item['checks'][0]['samples']
            code, report = self.run_tool(item)
            self.assertEqual(1, code, mutation)
            self.assertEqual('UNVERIFIED', report['status'])

    def test_empty_plan_duplicates_and_unknown_results_are_invalid(self):
        for mutation in ('empty', 'duplicate_plan', 'duplicate_result', 'extra'):
            data = capture()
            if mutation == 'empty': data['required_checks'] = []
            if mutation == 'duplicate_plan': data['required_checks'] *= 2
            if mutation == 'duplicate_result': data['checks'] *= 2
            if mutation == 'extra': data['checks'][0]['id'] = 'unplanned'
            self.assertEqual(3, self.run_tool(data)[0], mutation)

    def test_all_not_applicable_is_not_success(self):
        row = {'id': 'hero', 'kind': 'contact_drift', 'applies': False, 'reason': 'Actor flies'}
        self.assertEqual(1, self.run_tool(capture(row))[0])
        del row['reason']
        self.assertEqual(3, self.run_tool(capture(row))[0])

    def test_bad_times_vectors_and_numeric_types_are_invalid(self):
        for field, value in (('t', 0), ('t', True), ('t', float('nan')),
                             ('point', [0]), ('point', [0, False]), ('point', [float('inf'), 0]),
                             ('contact', 'yes')):
            data = capture()
            data['checks'][0]['samples'][1][field] = value
            self.assertEqual(3, self.run_tool(data)[0], (field, value))

    def test_threshold_must_be_explicit_finite_and_justified(self):
        for value in (-1, True, float('inf'), '0.1'):
            data = capture()
            data['checks'][0]['max_value'] = value
            self.assertEqual(3, self.run_tool(data)[0])
        data = capture()
        data['checks'][0]['threshold_reason'] = ''
        self.assertEqual(3, self.run_tool(data)[0])

    def test_duplicate_json_keys_are_rejected(self):
        self.assertEqual(3, self.run_tool(None, raw='{"schema":"a","schema":"b"}')[0])

    def test_existing_report_and_input_path_are_not_overwritten(self):
        self.assertTrue(SCRIPT.exists(), 'Motion diagnostic capability is absent')
        with tempfile.TemporaryDirectory() as name:
            source = Path(name) / 'input.json'
            source.write_text(json.dumps(capture()), encoding='utf-8')
            before = source.read_bytes()
            result = subprocess.run([sys.executable, str(SCRIPT), '--input', str(source),
                                     '--report', str(source)], capture_output=True)
            self.assertEqual(3, result.returncode)
            self.assertEqual(before, source.read_bytes())


if __name__ == '__main__':
    unittest.main()
