"""Compare registered opaque frames; produce diagnostics, never aesthetic acceptance.

Requires Pillow and NumPy. Run with --help. Inputs are read-only; output must be new.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def unique_object(pairs):
    """Reject duplicate JSON keys instead of silently losing a requested region."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def regions_for(size, path):
    """Resolve explicit pixel rectangles or a nonempty grid at the input size."""
    width, height = size
    if path:
        regions = json.loads(Path(path).read_text(encoding='utf-8-sig'), object_pairs_hook=unique_object)
    else:
        regions = {'frame': [0, 0, width, height]}
        nx, ny = min(4, width), min(4, height)
        for y in range(ny):
            for x in range(nx):
                regions[f'cell-{y}-{x}'] = [x * width // nx, y * height // ny,
                                            (x + 1) * width // nx, (y + 1) * height // ny]
    if not isinstance(regions, dict) or not regions:
        raise ValueError('regions must be a nonempty object')
    for name, box in regions.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError('region names must be nonempty')
        if not isinstance(box, list) or len(box) != 4 or any(type(v) is not int for v in box):
            raise ValueError(f'{name}: expected four integer pixel bounds')
        left, top, right, bottom = box
        if not (0 <= left < right <= width and 0 <= top < bottom <= height):
            raise ValueError(f'{name}: rectangle is empty or outside the image')
    return regions


def compare(reference, capture, output, regions_path=None):
    """Write diagnostic images and metrics without resampling or altering sources."""
    import numpy as np
    from PIL import Image

    output = Path(output)
    if output.exists():
        raise ValueError('output directory already exists; use a new report directory')
    paths = [Path(reference), Path(capture)]
    images = []
    for path in paths:
        with Image.open(path) as image:
            image.load()
            if image.mode not in ('RGB', 'RGBA'):
                raise ValueError(f'{path.name}: explicitly convert the image to sRGB RGB/RGBA first')
            rgba = image.convert('RGBA')
            if rgba.getchannel('A').getextrema() != (255, 255):
                raise ValueError(f'{path.name}: composite transparency explicitly before comparison')
            images.append(image.convert('RGB'))
    if images[0].size != images[1].size:
        raise ValueError('image sizes differ; establish comparable captures before measuring')
    width, height = images[0].size
    if min(width, height) < 2:
        raise ValueError('images must be at least 2x2')
    regions = regions_for((width, height), regions_path)
    arrays = [np.asarray(image, dtype=np.float64) / 255.0 for image in images]

    def luminance(rgb):
        linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
        return linear @ np.array([0.2126, 0.7152, 0.0722])

    def palette(rgb):
        bins = np.minimum((rgb * 4).astype(int), 3)
        indices = bins[..., 0] * 16 + bins[..., 1] * 4 + bins[..., 2]
        return np.bincount(indices.ravel(), minlength=64) / indices.size

    def edge_density(luma):
        edges = [np.abs(np.diff(luma, axis=axis)).ravel() for axis in (0, 1)]
        values = np.concatenate(edges)
        return float(values.mean()) if values.size else 0.0

    metrics = {}
    for name, (left, top, right, bottom) in regions.items():
        ref, cap = [array[top:bottom, left:right] for array in arrays]
        lr, lc = luminance(ref), luminance(cap)
        metrics[name] = {
            'bounds': regions[name],
            'rgb_mae': float(np.abs(ref - cap).mean()),
            'luminance_delta': float((lc - lr).mean()),
            'palette_overlap': float(np.minimum(palette(ref), palette(cap)).sum()),
            'edge_density_delta': edge_density(lc) - edge_density(lr),
        }
    full_bounds = [0, 0, width, height]
    subregions = [name for name in metrics if metrics[name]['bounds'] != full_bounds]
    ranked = subregions or list(metrics)
    ranked.sort(key=lambda name: (-metrics[name]['rgb_mae'], name))
    report = {
        'schema': 'godot-frame-comparison/v1', 'status': 'DIAGNOSTIC_ONLY',
        'reference': {'path': str(paths[0].resolve()), 'sha256': hashlib.sha256(paths[0].read_bytes()).hexdigest()},
        'capture': {'path': str(paths[1].resolve()), 'sha256': hashlib.sha256(paths[1].read_bytes()).hexdigest()},
        'size': [width, height], 'regions': metrics, 'ranked_regions': ranked,
        'definitions': {'rgb_mae': 'mean absolute sRGB channel difference, 0..1',
                        'luminance_delta': 'capture minus reference mean linear-sRGB relative luminance',
                        'palette_overlap': 'histogram intersection, 4 bins per sRGB channel, 0..1',
                        'edge_density_delta': 'capture minus reference mean adjacent-pixel luminance difference'},
        'limitations': 'No camera, exposure, provenance or aesthetic acceptance is inferred. Verify capture context independently.',
    }
    side = Image.new('RGB', (width * 2, height))
    side.paste(images[0], (0, 0))
    side.paste(images[1], (width, 0))
    difference = Image.fromarray(np.rint(np.abs(arrays[0] - arrays[1]) * 255).astype('uint8'))
    output.mkdir(parents=True, exist_ok=False)
    side.save(output / 'side-by-side.png')
    difference.save(output / 'difference.png')
    (output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', required=True)
    parser.add_argument('--capture', required=True)
    parser.add_argument('--out', required=True, help='new output directory; never overwrites a report')
    parser.add_argument('--regions', help='JSON object of named [left,top,right,bottom] pixel rectangles')
    args = parser.parse_args()
    try:
        compare(args.reference, args.capture, args.out, args.regions)
    except (OSError, ValueError, ImportError) as error:
        print(f'INVALID: {error}', file=sys.stderr)
        return 3
    print(f'DIAGNOSTIC_ONLY: {Path(args.out) / "report.json"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
