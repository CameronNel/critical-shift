"""Prune explicitly scoped historical review images after native dependency checks."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = Path.cwd().resolve()
WORK = ROOT / 'image-cleanup-work'
WORK.mkdir(exist_ok=True)
RASTER = {'.png', '.jpg', '.jpeg', '.webp', '.tga', '.tif', '.tiff', '.exr', '.hdr', '.bmp', '.gif'}
BASE_COMMIT = 'a82c7d9b80456153a0c65ca4897044a7f62c7d1c'
BRANCH = 'chore/prune-generated-images-20260914'
REPORT_DIR = ROOT / 'maintenance' / 'image-cleanup-20260914'

def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()

def digest_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def inventory():
    rows = []
    entries = subprocess.check_output(['git', 'ls-files', '-s', '-z']).decode().split('\0')
    for entry in filter(None, entries):
        metadata, name = entry.split('\t', 1)
        mode, blob, stage = metadata.split()
        if stage != '0' or mode not in {'100644', '100755'}:
            raise RuntimeError('Unexpected index entry: ' + name)
        path = ROOT / name
        with path.open('rb') as f:
            head = f.read(1024)
        match = re.search(rb'^size (\d+)$', head, re.M) if head.startswith(b'version https://git-lfs.github.com/spec/v1') else None
        oid = re.search(rb'^oid sha256:([0-9a-f]+)$', head, re.M) if match else None
        rows.append({'path': name, 'blob': blob, 'bytes': int(match.group(1)) if match else path.stat().st_size, 'lfs': bool(match), 'oid': oid.group(1).decode() if oid else None})
    return rows

def prepare():
    rows = inventory()
    images = [r for r in rows if Path(r['path']).suffix.lower() in RASTER]
    max_exterior = defaultdict(int)
    for r in images:
        m = re.match(r'^sections/facility-assembly/exteriors/([^/]+)/review-R(\d+)/[^/]+$', r['path'])
        if m:
            max_exterior[m.group(1)] = max(max_exterior[m.group(1)], int(m.group(2)))
    candidates = []
    for row in images:
        path = row['path']
        reason = None
        m = re.match(r'^sections/condenser-bay/production/renders/review/([^/]+)/[^/]+$', path)
        if m and not re.search(r'(?:^|-)R34(?:-|$)', m.group(1)):
            reason = 'Historical condenser-bay review output before accepted R34'
        m = re.match(r'^sections/facility-assembly/production/spawn-exterior-review/(renders|player)-R(\d+)/[^/]+$', path)
        if m and int(m.group(2)) < 17:
            reason = 'Historical spawn exterior review output before current R17'
        m = re.match(r'^sections/facility-assembly/exteriors/([^/]+)/review-R(\d+)/[^/]+$', path)
        if m and int(m.group(2)) < max_exterior[m.group(1)]:
            reason = 'Superseded exterior review output; latest section review retained'
        if reason:
            if re.search(r'(?:^|/)(?:assets?|textures?|posters?|decals?|signage|references?|sources?|art|concepts?)(?:/|$)', path, re.I):
                raise RuntimeError('Protected artwork unexpectedly selected: ' + path)
            candidates.append(dict(row, reason=reason))
    manifest = json.loads((ROOT / 'MAP.json').read_text())
    scenes = [manifest['authoring_scene'], manifest['inspection_scene']]
    keep_blends = [r for r in rows if r['path'] in scenes or re.match(r'^sections/facility-assembly/sources/[^/]+/module\.blend$', r['path']) or (r['path'].startswith('sections/facility-assembly/exteriors/') and r['path'].endswith('.blend'))]
    if len([r for r in keep_blends if r['path'].endswith('/module.blend')]) != len(manifest['sections']):
        raise RuntimeError('Missing canonical room module')
    inputs = [r for r in images if '/assets/' in r['path'] or '/textures/' in r['path']]
    hydrate = [r['path'] for r in keep_blends + inputs if r['lfs']]
    if not hydrate or not candidates:
        raise RuntimeError('Empty hydration set or deletion set')
    state = {'base_commit': BASE_COMMIT, 'audit_commit': git('rev-parse', 'HEAD'), 'inventory': rows, 'images': images, 'candidates': candidates, 'scenes': scenes, 'hydrate': hydrate}
    (WORK / 'state.json').write_text(json.dumps(state, indent=2))
    print('PREPARE', json.dumps({'candidate_files': len(candidates), 'candidate_bytes': sum(r['bytes'] for r in candidates), 'hydrate_files': len(hydrate), 'hydrate_bytes': sum(r['bytes'] for r in keep_blends + inputs if r['lfs'])}), flush=True)
    subprocess.run(['git', 'lfs', 'install', '--local', '--skip-smudge'], check=True)
    subprocess.run(['git', 'lfs', 'pull', '--include=' + ','.join(hydrate), '--exclude='], check=True)
    by_path = {r['path']: r for r in rows}
    for name in hydrate:
        if digest_file(ROOT / name) != by_path[name]['oid']:
            raise RuntimeError('Hydrated LFS hash mismatch: ' + name)
    (WORK / 'scenes.txt').write_text('\n'.join(scenes) + '\n')

def collect_protection(reports):
    protected_paths, protected_names, protected_oids, protected_dirs = set(), set(), set(), set()
    def add(value, sequence=False):
        if not value:
            return
        value = str(value).replace('\\', '/')
        protected_names.add(Path(value).name.lower())
        resolved = os.path.normpath(value)
        try:
            relative = Path(resolved).relative_to(ROOT).as_posix()
            protected_paths.add(relative.lower())
        except ValueError:
            if 'sections/' in value:
                relative = os.path.normpath('sections/' + value.split('sections/', 1)[1]).replace('\\', '/')
                protected_paths.add(relative.lower())
        if sequence or '<UDIM>' in value or '<UVTILE>' in value or '#' in value:
            protected_dirs.add(Path(value).parent.name.lower())
    for report in reports:
        if any(lib['missing'] for lib in report['libraries']):
            raise RuntimeError('Incomplete dependency scan')
        for path in report['all_paths']:
            add(path)
        for image in report['images']:
            multi = image['source'] in {'SEQUENCE', 'TILED', 'MOVIE'}
            add(image['path'], multi)
            add(image['absolute'], multi)
            for item in image['packed']:
                add(item['path'], multi)
                protected_oids.add(item['sha256'])
    return protected_paths, protected_names, protected_oids, protected_dirs

def apply():
    if git('branch', '--show-current') != BRANCH:
        raise RuntimeError('Refuse cleanup outside task branch')
    state = json.loads((WORK / 'state.json').read_text())
    before = [json.loads((WORK / f'before-{i}.json').read_text()) for i in range(len(state['scenes']))]
    for report, scene in zip(before, state['scenes']):
        if report['scene'] != scene or report['object_count'] < 1:
            raise RuntimeError('Invalid scene audit')
    paths, names, oids, directories = collect_protection(before)
    removed, protected = [], []
    for row in state['candidates']:
        p = Path(row['path'])
        used = row['path'].lower() in paths or p.name.lower() in names or row['oid'] in oids or p.parent.name.lower() in directories
        (protected if used else removed).append(row)
    if not removed:
        raise RuntimeError('No independently unreferenced review images to remove')
    state['removed'] = removed
    state['protected_candidates'] = protected
    protected_files = set(state['hydrate'])
    for report in before:
        for lib in report['libraries']:
            protected_files.add(Path(lib['path']).relative_to(ROOT).as_posix())
    state['protected_file_hashes'] = {name: digest_file(ROOT / name) for name in sorted(protected_files)}
    (WORK / 'remove-paths').write_bytes(b''.join(r['path'].encode() + b'\0' for r in removed))
    subprocess.run(['git', 'rm', '--quiet', '--pathspec-from-file=' + str(WORK / 'remove-paths'), '--pathspec-file-nul'], check=True)
    (WORK / 'state.json').write_text(json.dumps(state, indent=2))
    print('REMOVED_FROM_TASK_WORKTREE', json.dumps({'files':len(removed),'bytes':sum(r['bytes'] for r in removed),'protected_candidates':len(protected)}), flush=True)

def verify():
    state = json.loads((WORK / 'state.json').read_text())
    before = [json.loads((WORK / f'before-{i}.json').read_text()) for i in range(len(state['scenes']))]
    after = [json.loads((WORK / f'after-{i}.json').read_text()) for i in range(len(state['scenes']))]
    if before != after:
        raise RuntimeError('Before/after native Blender inventories differ; no commit permitted')
    for name, expected in state['protected_file_hashes'].items():
        if digest_file(ROOT / name) != expected:
            raise RuntimeError('Protected input changed: ' + name)
    removed = {r['path'] for r in state['removed']}
    staged = subprocess.check_output(['git', 'diff', '--cached', '--name-status', '-z']).decode().split('\0')
    pairs = list(zip(staged[0::2], staged[1::2]))
    if set(pairs) != {('D', name) for name in removed}:
        raise RuntimeError('Unexpected staged edits')
    nondeleted = [r for r in state['inventory'] if r['path'] not in removed]
    for row in nondeleted:
        if not (ROOT / row['path']).is_file():
            raise RuntimeError('Unapproved file missing: ' + row['path'])
    ignore = ROOT / '.gitignore'
    old_ignore = ignore.read_text() if ignore.exists() else ''
    rules = sorted('/' + path for path in removed)
    ignore.write_text(old_ignore.rstrip() + '\n\n# Historical review images pruned 2026-09-14; see maintenance/image-cleanup-20260914.\n' + '\n'.join(rules) + '\n')
    summary = {'base_commit': state['base_commit'], 'audit_commit': state['audit_commit'], 'branch': BRANCH, 'image_files_before': len(state['images']), 'image_bytes_before': sum(r['bytes'] for r in state['images']), 'removed_image_files': len(removed), 'removed_image_bytes': sum(r['bytes'] for r in state['removed']), 'image_files_after': len(state['images']) - len(removed), 'image_bytes_after': sum(r['bytes'] for r in state['images']) - sum(r['bytes'] for r in state['removed']), 'blend_files_changed': 0, 'map_manifest_changed': False, 'native_before_after_match': True, 'protected_input_hashes_match': True, 'protected_input_files': len(state['protected_file_hashes']), 'protected_candidates': state['protected_candidates'], 'scenes': [{'path':x['scene'],'sha256':x['scene_sha256'],'objects':x['object_count'],'image_datablocks':len(x['images']),'packed_image_payloads':sum(len(im['packed']) for im in x['images']),'linked_libraries':len(x['libraries']),'missing_libraries':sum(y['missing'] for y in x['libraries'])} for x in before], 'limitations': ['Dependency and file-integrity audit, not a rendered visual or Unity runtime test.', 'Removed images remain recoverable in Git history; remote Git LFS quota is not reclaimed.', 'Main branch remains unchanged pending independent review.']}
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / 'SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
    (REPORT_DIR / 'REMOVED_IMAGES.json').write_text(json.dumps(state['removed'], indent=2) + '\n')
    (REPORT_DIR / 'DEPENDENCIES_BEFORE.json').write_text(json.dumps(before, indent=2) + '\n')
    (REPORT_DIR / 'DEPENDENCIES_AFTER.json').write_text(json.dumps(after, indent=2) + '\n')
    (REPORT_DIR / 'README.md').write_text('# Image cleanup, 14 September 2026\n\nRemoved ' + str(summary['removed_image_files']) + ' historical review images (' + str(summary['removed_image_bytes']) + ' bytes of hydrated payload) on the task branch only.\n\nBoth canonical MAP.json scenes were opened in separate, read-only Blender processes before and after deletion. Their complete recorded dependency inventories, geometry digests, packed-image hashes, source-file hashes and object counts match exactly. All linked libraries resolved. No Blender file, material, poster, texture, geometry, source module, MAP.json or existing script was edited. No scene was saved or rendered.\n\n## Retention\n\nRetained every native image/path dependency, all source artwork, concepts, textures, PBR packs, posters, references and baseline comparison inputs. Kept all accepted condenser R34 review sets, the current spawn R17 images, and the latest review for every exterior section. All existing Markdown reports and JSON evidence remain. Only the removed historical output filenames are ignored, not arbitrary images or future revisions.\n\n## Historical references and recovery\n\nSome old review reports reference images deliberately pruned by this cleanup. Those references are historical, not missing map dependencies. The full path, Git blob, LFS object ID and hydrated byte size are in REMOVED_IMAGES.json. Restore an individual old image from commit `' + BASE_COMMIT + '` using `git restore --source=' + BASE_COMMIT + ' -- path/to/image.png`, then `git lfs pull --include=path/to/image.png`.\n\n## Scope of verification\n\nThis is a native dependency and byte-integrity audit, not a Unity test, FPS benchmark, visual render approval or independent human review. Nothing is merged into main by this task.\n\nDeleting pointers from a branch does not purge old LFS objects or reclaim GitHub LFS quota. No history rewrite, force push, LFS remote purge, repository recreation or asset recompression was performed.\n', encoding='utf-8')
    print('VERIFIED_SUMMARY', json.dumps(summary), flush=True)
    subprocess.run(['git', 'add', '--', '.gitignore', str(REPORT_DIR.relative_to(ROOT))], check=True)

if __name__ == '__main__':
    {'prepare':prepare, 'apply':apply, 'verify':verify}[sys.argv[1]]()
