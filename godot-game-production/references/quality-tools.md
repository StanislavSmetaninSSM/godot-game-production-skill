# Offline quality diagnostics

These helpers consume project captures. They do not launch Godot, export
telemetry, decide artistic quality or replace the evidence ledger. Keep reports,
source captures and capture context together in the existing evidence run. Record
their exact hashes and candidate identity under the existing evidence rules.

## Image comparison

Requires Python 3.10+, Pillow and NumPy. Use an available project/bundled runtime;
if unavailable, declare the missing dependencies and prepare a local environment
within existing authorization. Do not silently modify system Python.

```text
python scripts/frame_compare.py --reference approved-srgb.png --capture godot-srgb.png --out diagnostics/frame-01 --regions regions.json
```

`regions.json` is optional. Example: `{"player":[80,30,150,170]}` specifies
left/top/right/bottom pixel edges. Without it, the tool checks the whole frame
and up to a 4x4 grid. Names and bounds must be valid, nonempty and unique.
Both images must be same-sized opaque RGB/RGBA, at least 2x2, explicitly prepared
as sRGB. No implicit resizing, exposure correction or image registration occurs.

The new output directory contains side-by-side.png, difference.png and report.json.
The report binds source SHA-256 and gives region bounds, RGB mean absolute error
(0..1), signed mean linear-sRGB luminance difference, coarse palette overlap
(4 bins/channel, 0..1) and edge-density difference. Regions rank by RGB error;
the whole frame is excluded when subregions exist. Inspect results visually:
coarse palette agreement and low error cannot establish design or motion quality.
Exit 0 means diagnostic files were created; status is always DIAGNOSTIC_ONLY.
Exit 3 means invalid input/dependency/output. Existing output is preserved.

## Motion capture contract

The motion checker uses Python's standard library. Export a JSON object with:

- `schema`: `godot-motion-capture/v1`.
- `source`: kind (`godot_runtime` or `synthetic`), build_id, dimension (`2d`,
  `2.5d`, `3d`), vector_size (2 or 3), coordinate_space, unit (`px`, `m`,
  `world_unit`), scenario, evidence (nonempty list of capture/trace identities).
- `required_checks`: nonempty unique IDs copied from the predeclared matrix.
- `checks`: supplied result rows. An absent planned row is UNVERIFIED; extra or
  duplicate IDs are INVALID. Every row has id, kind and boolean applies.
- Applicable rows require finite nonnegative max_value, nonempty threshold_reason,
  and samples. Non-applicable rows require a reviewable reason; missing telemetry
  cannot be declared inapplicable. An all-inapplicable run remains UNVERIFIED.

| kind | samples and measurement | minimum data |
| --- | --- | --- |
| contact_drift | `{t,point,reference,contact}`; maximum support-relative speed over adjacent stance samples, unit/s | Two consecutive contact=true samples |
| pose_acceleration | `{t,point,reference}`; change of adjacent relative velocities divided by their mean timestep, unit/s² | Three samples |
| anchor_distance | `{t,point,reference}`; maximum point/reference distance, unit | One sample; matrix covers other relevant poses |
| event_offset | `{event_time,visible_time}`; maximum absolute offset, seconds | One paired event |

Times are finite seconds and strictly increase within each spatial check; vectors
have vector_size finite coordinates. Booleans are not numbers. Threshold equality
passes. Empty/missing samples and missing stance intervals are UNVERIFIED; invalid
types/times, duplicate JSON keys and NaN/Infinity are INVALID.
Non-finite derived intervals, coordinates or measurements are also INVALID.

This complete **synthetic** example tests a foot transported with an elevator.
The zero tolerance is a mathematical fixture expectation, not a game budget:

```json
{
  "schema": "godot-motion-capture/v1",
  "source": {
    "kind": "synthetic", "build_id": "elevator-fixture-v1",
    "dimension": "3d", "vector_size": 3, "coordinate_space": "world",
    "unit": "m", "scenario": "transported contact",
    "evidence": ["synthetic example; not a Godot capture"]
  },
  "required_checks": ["left-foot"],
  "checks": [{
    "id": "left-foot", "kind": "contact_drift", "applies": true,
    "max_value": 0, "threshold_reason": "Exact synthetic transported anchor",
    "samples": [
      {"t": 0, "point": [0, 2, 0], "reference": [0, 0, 0], "contact": true},
      {"t": 1, "point": [3, 2, 0], "reference": [3, 0, 0], "contact": true}
    ]
  }]
}
```

```text
python scripts/motion_check.py --input capture.json --report diagnostics/motion-01.json
```

Report includes the input hash, caller-declared source, per-check measurements,
units, limits, reasons and states. Overall precedence and exit codes:
INVALID=3, FAILED=2, UNVERIFIED=1, CHECKS_PASSED=0. Existing reports are preserved.
Every report has diagnostic_only=true. No state means milestone PASS.

For real capture, the owning Godot systems export the required points/events and
identify the actual build and supporting video/frames. Record transforms, sample
clock and mapping in the project capture notes. The supplied source.kind and
evidence strings are declarations; a reviewer verifies their actual artifacts.
The checker cannot validate an omitted inventory row, unseen inter-frame motion,
incorrectly exported point, fabricated provenance or a poorly justified threshold.
