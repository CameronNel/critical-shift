#!/usr/bin/env python3
"""Fetch four specifically selected CC0 material sets; never download executable code.
Original files are retained. Blender controls scale, colour and detail strength.
"""
from pathlib import Path
import argparse, hashlib, io, json, time, urllib.request, zipfile
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
DEFAULT = PACKAGE.parents[1]/'assets'/'pbr' if PACKAGE.parent.name == 'blender' else HERE/'materials'
AGENT = 'CriticalShift-Gullet-MaterialBuild/1.1 (single-project CC0 asset download)'

def fetch(url, limit=180_000_000):
    error = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': AGENT})
            with urllib.request.urlopen(req, timeout=90) as response:
                data = response.read(limit + 1)
            if len(data) > limit:
                raise ValueError('Download exceeds the declared safety limit: ' + url)
            if not data:
                raise ValueError('Empty download: ' + url)
            return data
        except Exception as exc:
            error = exc
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise RuntimeError('Could not download ' + url) from error

def store(dest, asset, role, data, extension, url):
    folder = dest/asset
    folder.mkdir(parents=True, exist_ok=True)
    path = folder/(role + extension)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_bytes(data)
    temporary.replace(path)
    return {'path': path.relative_to(dest).as_posix(), 'url': url,
            'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}

def polyhaven(dest, asset, tile):
    api = 'https://api.polyhaven.com/files/' + asset
    files = json.loads(fetch(api, 8_000_000))
    entry = {'provider': 'Poly Haven', 'asset': asset,
             'source': 'https://polyhaven.com/a/' + asset,
             'license': 'CC0-1.0', 'license_url': 'https://polyhaven.com/license',
             'tile_m': tile, 'maps': {}}
    keys = {'color': ['Diffuse', 'diff'], 'roughness': ['Rough', 'rough'],
            'normal': ['nor_gl'], 'height': ['Displacement', 'disp']}
    for role, candidates in keys.items():
        key = next((k for k in candidates if k in files), None)
        if key is None:
            if role == 'height':
                continue
            raise RuntimeError('Missing required Poly Haven map: ' + asset + '/' + role)
        formats = files[key].get('2k', {})
        fmt = 'jpg' if 'jpg' in formats else 'png'
        remote = formats[fmt]
        print('Downloading', asset, role, remote['url'], flush=True)
        data = fetch(remote['url'])
        if remote.get('md5') and hashlib.md5(data).hexdigest() != remote['md5']:
            raise RuntimeError('Provider MD5 mismatch: ' + remote['url'])
        entry['maps'][role] = store(dest, asset, role, data, '.' + fmt, remote['url'])
    return entry

def ambientcg(dest, asset, tile):
    url = 'https://ambientcg.com/get?file=' + asset + '_2K-JPG.zip'
    print('Downloading', asset, url, flush=True)
    data = fetch(url)
    entry = {'provider': 'ambientCG', 'asset': asset,
             'source': 'https://ambientcg.com/view?id=' + asset,
             'license': 'CC0-1.0', 'license_url': 'https://docs.ambientcg.com/license/',
             'tile_m': tile, 'archive_url': url,
             'archive_sha256': hashlib.sha256(data).hexdigest(), 'maps': {}}
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for role, suffix in [('color', '_Color'), ('roughness', '_Roughness'),
                             ('normal', '_NormalGL'), ('height', '_Displacement')]:
            matches = [i for i in archive.infolist()
                       if suffix in Path(i.filename).stem and Path(i.filename).suffix.lower() in ('.jpg', '.png')]
            if not matches:
                if role == 'height':
                    continue
                raise RuntimeError('Missing map in archive: ' + asset + '/' + role)
            item = sorted(matches, key=lambda i: i.filename)[0]
            if item.file_size > 100_000_000:
                raise RuntimeError('Unexpected map size: ' + item.filename)
            entry['maps'][role] = store(dest, asset, role, archive.read(item), Path(item.filename).suffix.lower(), url)
    return entry

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', type=Path, default=DEFAULT)
    args = parser.parse_args()
    dest = args.dest.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    entries = []
    # No moss, green concrete, artificial glowing ore or generic grunge pack.
    for asset, tile in [('rock_surface', 2.0), ('gravel_ground_01', 2.0)]:
        entries.append(polyhaven(dest, asset, tile))
    for asset, tile in [('Concrete046', 2.4), ('Metal046B', 1.0)]:
        entries.append(ambientcg(dest, asset, tile))
    manifest = {'schema': 1, 'downloaded_at_utc': datetime.now(timezone.utc).isoformat(),
                'resolution': '2K', 'assets': entries}
    (dest/'download_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    notes = ['# Downloaded material provenance', '', 'All four sets are CC0-1.0. Original map pixels are retained.',
             'Shader adjustments are made in Blender, not represented as original source material.', '',
             'The JSON manifest records each source URL, file size and SHA-256 hash.', '']
    for entry in entries:
        notes += [f"## {entry['asset']} ({entry['provider']})", entry['source'], entry['license_url'], '']
    (dest/'PROVENANCE.md').write_text('\n'.join(notes), encoding='utf-8')
    print('Verified downloaded maps:', sum(len(x['maps']) for x in entries), flush=True)
    print('Manifest:', dest/'download_manifest.json', flush=True)

if __name__ == '__main__':
    main()
