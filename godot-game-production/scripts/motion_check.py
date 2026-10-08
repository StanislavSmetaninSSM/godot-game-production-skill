"""Check declared motion telemetry and coverage; never certify game acceptance.

Standard library only. Input: godot-motion-capture/v1 (references/quality-tools.md).
Exit: 0 checks passed, 1 unverified, 2 measured failure, 3 invalid input/output.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

KINDS = {'contact_drift', 'pose_acceleration', 'anchor_distance', 'event_offset'}
CODES = {'CHECKS_PASSED': 0, 'UNVERIFIED': 1, 'FAILED': 2, 'INVALID': 3}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def number(value):
    """Accept finite JSON numbers, excluding booleans."""
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError('expected finite numeric value, not a boolean')
    return float(value)


def finite_max(values):
    """Reject every invalid observation before reduction can conceal a NaN."""
    return max(number(value) for value in values)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f'non-finite JSON constant: {value}')


def validate_source(source):
    """Validate caller-declared context; this does not authenticate provenance."""
    if not isinstance(source, dict):
        raise ValueError('source context is required')
    for key in ('build_id', 'coordinate_space', 'scenario'):
        if not nonempty(source.get(key)):
            raise ValueError(f'source.{key} must be nonempty')
    if source.get('kind') not in ('godot_runtime', 'synthetic'):
        raise ValueError('source.kind must be godot_runtime or synthetic')
    if source.get('dimension') not in ('2d', '2.5d', '3d'):
        raise ValueError('invalid source.dimension')
    if type(source.get('vector_size')) is not int or source['vector_size'] not in (2, 3):
        raise ValueError('source.vector_size must be 2 or 3')
    if source.get('unit') not in ('px', 'm', 'world_unit'):
        raise ValueError('source.unit must be px, m or world_unit')
    evidence = source.get('evidence')
    if not isinstance(evidence, list) or not evidence or not all(nonempty(e) for e in evidence):
        raise ValueError('source.evidence must name the captures or synthetic fixture')


def relative_samples(samples, size):
    """Read timestamped points relative to their supplied support/root anchor."""
    points, times = [], []
    for sample in samples:
        if not isinstance(sample, dict):
            raise ValueError('each sample must be an object')
        t = number(sample.get('t'))
        if times and t <= times[-1]:
            raise ValueError('sample times must strictly increase')
        if times:
            number(t - times[-1])
        vectors = []
        for key in ('point', 'reference'):
            value = sample.get(key)
            if not isinstance(value, list) or len(value) != size:
                raise ValueError(f'{key} must contain {size} coordinates')
            vectors.append([number(v) for v in value])
        times.append(t)
        points.append([number(a - b) for a, b in zip(*vectors)])
    return times, points


def measure(kind, samples, size):
    """Return measured maximum or None when the declared observations are absent."""
    if kind == 'event_offset':
        values = []
        for sample in samples:
            if not isinstance(sample, dict):
                raise ValueError('event samples must be objects')
            values.append(abs(number(sample.get('visible_time')) - number(sample.get('event_time'))))
        return finite_max(values)
    times, points = relative_samples(samples, size)
    if kind == 'anchor_distance':
        return finite_max(math.hypot(*p) for p in points)
    if kind == 'contact_drift':
        if any(type(sample.get('contact')) is not bool for sample in samples):
            raise ValueError('contact must be boolean on every contact sample')
        values = [math.dist(points[i], points[i - 1]) / (times[i] - times[i - 1])
                  for i in range(1, len(times)) if samples[i]['contact'] and samples[i - 1]['contact']]
        return finite_max(values) if values else None
    if len(times) < 3:
        return None
    intervals = [times[i] - times[i - 1] for i in range(1, len(times))]
    velocities = [[number((a - b) / dt) for a, b in zip(points[i], points[i - 1])]
                  for i, dt in enumerate(intervals, start=1)]
    means = [intervals[i - 1] + (intervals[i] - intervals[i - 1]) / 2
             for i in range(1, len(intervals))]
    return finite_max(math.dist(velocities[i], velocities[i - 1]) / means[i - 1]
                      for i in range(1, len(velocities)))


def evaluate_check(row, source):
    """Assess one planned check without substituting missing data with defaults."""
    result = {'id': row['id'], 'kind': row.get('kind')}
    try:
        kind = row.get('kind')
        if kind not in KINDS or type(row.get('applies')) is not bool:
            raise ValueError('known kind and boolean applies are required')
        if not row['applies']:
            if not nonempty(row.get('reason')):
                raise ValueError('not-applicable check requires a reviewable reason')
            return {**result, 'status': 'NOT_APPLICABLE', 'reason': row['reason']}
        limit = number(row.get('max_value'))
        if limit < 0 or not nonempty(row.get('threshold_reason')):
            raise ValueError('nonnegative threshold and threshold_reason are required')
        unit = {'contact_drift': source['unit'] + '/s', 'pose_acceleration': source['unit'] + '/s^2',
                'anchor_distance': source['unit'], 'event_offset': 's'}[kind]
        result.update(limit=limit, unit=unit, threshold_reason=row['threshold_reason'])
        samples = row.get('samples', [])
        if not isinstance(samples, list):
            raise ValueError('samples must be an array')
        if not samples:
            return {**result, 'status': 'UNVERIFIED', 'reason': 'No samples supplied'}
        value = measure(kind, samples, source['vector_size'])
        if value is None:
            return {**result, 'status': 'UNVERIFIED', 'reason': 'Insufficient applicable intervals'}
        if not math.isfinite(value):
            raise ValueError('measurement overflowed; check coordinate and time scale')
        result.update(measured=value, sample_count=len(samples), status='CHECK_PASSED' if value <= limit else 'FAILED')
    except (ValueError, TypeError, OverflowError, ZeroDivisionError) as error:
        result.update(status='INVALID', reason=str(error))
    return result


def evaluate(data):
    """Resolve declared coverage and aggregate diagnostics, not product acceptance."""
    if not isinstance(data, dict) or data.get('schema') != 'godot-motion-capture/v1':
        raise ValueError('expected godot-motion-capture/v1 object')
    source = data.get('source')
    validate_source(source)
    required = data.get('required_checks')
    if not isinstance(required, list) or not required or not all(nonempty(v) for v in required):
        raise ValueError('required_checks must be a nonempty list of IDs')
    if len(required) != len(set(required)):
        raise ValueError('required_checks contains duplicate IDs')
    rows = data.get('checks')
    if not isinstance(rows, list):
        raise ValueError('checks must be an array')
    by_id = {}
    for row in rows:
        if not isinstance(row, dict) or not nonempty(row.get('id')):
            raise ValueError('each result must have a nonempty id')
        if row['id'] not in required or row['id'] in by_id:
            raise ValueError(f'unplanned or duplicate check ID: {row["id"]}')
        by_id[row['id']] = row
    results = [evaluate_check(by_id[key], source) if key in by_id else
               {'id': key, 'status': 'UNVERIFIED', 'reason': 'Expected check is absent'} for key in required]
    states = {row['status'] for row in results}
    status = next((s for s in ('INVALID', 'FAILED', 'UNVERIFIED') if s in states), 'CHECKS_PASSED')
    if states == {'NOT_APPLICABLE'}:
        status = 'UNVERIFIED'
    return {'status': status, 'source': source, 'checks': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--report', required=True, help='new JSON report; existing files are preserved')
    args = parser.parse_args()
    output = Path(args.report)
    if output.exists():
        print('INVALID: report already exists; use a new path', file=sys.stderr)
        return 3
    report = {'schema': 'godot-motion-report/v1', 'diagnostic_only': True,
              'limitations': 'Caller-declared provenance and applicability require independent review; this is not build acceptance.'}
    try:
        raw = Path(args.input).read_bytes()
        report['input_sha256'] = hashlib.sha256(raw).hexdigest()
        data = json.loads(raw.decode('utf-8-sig'), object_pairs_hook=unique_object, parse_constant=reject_constant)
        report.update(evaluate(data))
    except (ValueError, TypeError, OverflowError, OSError) as error:
        report.update(status='INVALID', error=str(error))
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    except (ValueError, OSError) as error:
        print(f'INVALID: cannot write report: {error}', file=sys.stderr)
        return 3
    print(f'{report["status"]} (diagnostic only): {output}')
    return CODES[report['status']]


if __name__ == '__main__':
    sys.exit(main())
