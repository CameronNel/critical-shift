"""Create clearly labeled QA sheets and compare untouched camera renders.

Uses Pillow and NumPy in the bundled Python runtime, not Blender.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_batch(path):
    root = Path(path).resolve()
    data = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    if not data['completed']:
        raise RuntimeError(f'Batch incomplete: {root}')
    for camera in data['cameras']:
        actual = digest(root / camera['image'])
        if actual != camera['sha256']:
            raise RuntimeError(f'Pixel artifact hash differs: {camera["image"]}')
    return root, data


def sheet(path):
    root, batch = read_batch(path)
    cameras = batch['cameras']
    cell_w, cell_h = 640, 435
    canvas = Image.new('RGB', (1280, 70 + ((len(cameras) + 1) // 2) * cell_h), '#e9e4d9')
    draw = ImageDraw.Draw(canvas)
    font_path = Path('C:/Windows/Fonts/arial.ttf')
    font = ImageFont.truetype(str(font_path), 19) if font_path.exists() else ImageFont.load_default()
    title = ImageFont.truetype(str(font_path), 27) if font_path.exists() else font
    draw.text((18, 18), f'WASTE STORAGE / {batch["revision"]} / QA thumbnails', fill='#193c40', font=title)
    for index, camera in enumerate(cameras):
        image = Image.open(root / camera['image']).convert('RGB')
        image.thumbnail((cell_w - 12, cell_h - 36))
        x = (index % 2) * cell_w + 6
        y = 70 + (index // 2) * cell_h
        canvas.paste(image, (x, y))
        draw.text((x + 5, y + cell_h - 29), camera['name'], fill='#193c40', font=font)
    result = root / 'contact-sheet.jpg'
    canvas.save(result, quality=94)
    print(result)


def compare(before, after, output):
    old_root, old = read_batch(before)
    new_root, new = read_batch(after)
    old_cameras = {item['name']: item for item in old['cameras']}
    new_cameras = {item['name']: item for item in new['cameras']}
    result = {'before_revision': old['revision'], 'after_revision': new['revision'],
              'source_identical': old['source_sha256'] == new['source_sha256'],
              'settings_identical': old['settings'] == new['settings'],
              'camera_set_identical': set(old_cameras) == set(new_cameras), 'cameras': []}
    for name in sorted(set(old_cameras) & set(new_cameras)):
        first, second = old_cameras[name], new_cameras[name]
        a = np.asarray(Image.open(old_root / first['image']).convert('RGB'), dtype=np.float32)
        b = np.asarray(Image.open(new_root / second['image']).convert('RGB'), dtype=np.float32)
        compatible = a.shape == b.shape
        delta = np.abs(a - b) if compatible else None
        result['cameras'].append({
            'camera': name, 'framing_identical': all(first[k] == second[k] for k in ['matrix_world', 'lens_mm', 'sensor_width_mm']),
            'pixel_dimensions_identical': compatible, 'file_identical': first['sha256'] == second['sha256'],
            'mean_absolute_channel_difference_255': float(delta.mean()) if compatible else None,
            'max_channel_difference_255': float(delta.max()) if compatible else None,
            'fraction_pixels_any_channel_difference_gt_2': float((delta.max(axis=2) > 2).mean()) if compatible else None,
            'before_image': f'{old_root.name}/{first["image"]}',
            'after_image': f'{new_root.name}/{second["image"]}'
        })
    result['all_pixels_identical'] = result['camera_set_identical'] and all(cam['file_identical'] for cam in result['cameras'])
    result['interpretation'] = 'Numeric comparison only; visual improvement or regression requires independent pixel review.'
    dest = Path(output).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='action', required=True)
s = subparsers.add_parser('sheet')
s.add_argument('batch')
c = subparsers.add_parser('compare')
c.add_argument('before')
c.add_argument('after')
c.add_argument('--output', required=True)
args = parser.parse_args()
if args.action == 'sheet':
    sheet(args.batch)
else:
    compare(args.before, args.after, args.output)
