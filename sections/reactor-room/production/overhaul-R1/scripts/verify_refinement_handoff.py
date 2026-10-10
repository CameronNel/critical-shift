"""Verify the portable reviewed reactor package without Blender or downloads."""
import ast
import hashlib
import json
from pathlib import Path
import struct


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    repo = Path(__file__).resolve().parents[5]
    checkpoint = repo / 'sections/reactor-room/production/checkpoints/refinement-28fc'
    handoff = json.loads((checkpoint / 'handoff.json').read_text())
    assert handoff['files'], 'Missing portable file index'
    for name, expected in handoff['files'].items():
        path = (repo / name).resolve()
        assert path.is_relative_to(repo), name
        assert digest(path) == expected, f'Missing or changed file: {name}; hydrate LFS first'
    source = repo / handoff['source_path']
    with source.open('rb') as stream:
        assert not stream.read(64).startswith(b'version https://git-lfs.github.com/spec/v1'), \
            'The source is an LFS pointer; hydrate it'
    sha = digest(source)
    assert sha == handoff['source_sha256']
    review = repo / handoff['review_path']
    ledger = json.loads((review / 'LUNA_28FC_DISPOSITIONS.json').read_text())
    assert ledger['candidate']['source_sha256'] == sha
    assert set(ledger['accepted_issue_ids']) == set(range(1, 141))
    assert not ledger['pending_ids'] and not ledger['partial_issue_ids']
    assert len(ledger['issues']) == 140
    assert all(row['status'].startswith('accepted') and
               row['evidence']['candidate_sha256'] == sha for row in ledger['issues'])
    assert ledger['score'] == handoff['score'] >= 90
    areas = {'signage', 'machinery', 'props', 'floor', 'pool', 'rods', 'roof', 'walls', 'holistic'}
    assert set(ledger['area_scores']) == areas
    assert ledger['area_scores'] == handoff['area_scores']
    assert min(ledger['area_scores'].values()) >= 85
    for row in ledger['issues']:
        evidence = row['evidence']
        report_name = Path(row['report']).name
        report_path = review / report_name
        if not report_path.exists():
            report_path = review / 'evidence-reports' / report_name
        expected = evidence.get('carry_report_sha256') or evidence['report_sha256']
        assert digest(report_path) == expected, f'Review identity changed for issue {row["id"]}'
    report = (review / 'LUNA_28FC_FINAL_REVIEW.md').read_text()
    assert sha in report
    views = repo / handoff['views_path']
    manifest = json.loads((views / 'render_manifest.json').read_text())
    renderer = Path(__file__).with_name('render_detail_views.py')
    assert digest(renderer) == manifest['renderer_sha256']
    tree = ast.parse(renderer.read_text())
    poses = next(ast.literal_eval(n.value) for n in tree.body
                 if isinstance(n, ast.Assign) and any(
                     isinstance(t, ast.Name) and t.id == 'VIEWS' for t in n.targets))
    poses = {row[0]: row for row in poses}
    assert manifest['source_sha256'] == sha
    assert manifest['resolution'] == [1280, 720] and manifest['color_depth'] == '16'
    assert manifest['samples_max'] == 96 and manifest['adaptive_min_samples'] == 32
    assert manifest['adaptive_threshold'] == struct.unpack('f', struct.pack('f', .015))[0]
    assert not manifest['preview'] and manifest['path_guiding']
    assert manifest['guiding_training_samples'] == 64
    assert manifest['denoiser'] == 'OPENIMAGEDENOISE' and manifest['max_bounces'] == 12
    assert manifest['frame'] == 1 and manifest['stability'] == 1.0
    assert manifest['volume_bounces'] == 1
    assert not manifest['reflective_caustics'] and not manifest['refractive_caustics']
    assert manifest['color_management'] == {
        'transform': 'AgX', 'look': 'AgX - Medium High Contrast', 'exposure': 0.0}
    assert manifest['engine'] == 'CYCLES' and manifest['device'] == 'CPU'
    assert len(manifest['views']) == 10 and set(poses) == {v['name'] for v in manifest['views']}
    for view in manifest['views']:
        raw = views / 'raw-manifests' / view['name'][:2] / 'render_manifest.json'
        original = json.loads(raw.read_text())
        assert original['views'] == [view]
        assert {k: v for k, v in original.items() if k != 'views'} == {
            k: v for k, v in manifest.items() if k != 'views'}
        pose = poses[view['name']]
        assert view['location'] == list(pose[2]) and view['target'] == list(pose[3])
        assert view['lens_mm'] == pose[4] and view['projection'] == 'PERSP'
        image = views / view['file']
        assert digest(image) == view['sha256'] and view['sha256'] in report
        assert struct.unpack('>IIBB', image.read_bytes()[16:26]) == (1280, 720, 16, 2)
    for number, expected_source in [('37', sha), ('82', handoff['historical_fixture_source_sha256'])]:
        folder = views / 'proofs' / number
        proof = json.loads((folder / 'render_manifest.json').read_text())
        assert proof['source_sha256'] == expected_source
        assert proof['resolution'] == [1280, 720] and not proof['preview']
        assert proof['samples_max'] == 96 and proof['adaptive_min_samples'] == 32
        assert proof['path_guiding'] and proof['guiding_training_samples'] == 64
        assert proof['color_depth'] == '16' and len(proof['views']) == 1
        frame = proof['views'][0]
        assert digest(folder / frame['file']) == frame['sha256'] and frame['sha256'] in report
        assert struct.unpack('>IIBB', (folder / frame['file']).read_bytes()[16:26]) == (1280, 720, 16, 2)
    cold_scope = json.loads((checkpoint / 'cold/scope.json').read_text())
    assert cold_scope['pass_check'] and cold_scope['current_source_sha256'] == sha
    assert len(cold_scope['matches']) == handoff['declared_cold_comparisons'] == 124
    assert all(value is True for value in cold_scope['matches'].values())
    for label, expected_source in [('current', sha), ('cold', cold_scope['cold_source_sha256'])]:
        folder = checkpoint / label
        checks = json.loads((folder / 'checks.json').read_text())
        assert checks['source_sha256'] == expected_source and checks['all_pass']
        assert len(checks['checks']) == 14 and all(c['pass'] and c['exit'] == 0 for c in checks['checks'])
        assert 'RESULT: PASS' in (folder / 'control-room-check.log').read_text()
        audit = json.loads((folder / 'audit.json').read_text())
        assert audit['sha256'] == expected_source and audit['protected']['pass_check']
        assert not audit['signage']['failures'] and not audit['support']['failures']
        assert len(audit['signage']['required_camera_sightlines']) == 13
        assert all(r['pass_check'] for r in audit['signage']['required_camera_sightlines'])
    integration = json.loads((checkpoint / 'recipe-integration.json').read_text())
    assert integration['candidate_source_sha256'] == sha
    for item in integration['files']:
        assert digest(renderer.parent / item['name']) == item['sha256']
    dependencies = json.loads((checkpoint / 'current/portable-dependencies.json').read_text())
    assert dependencies['source_sha256'] == sha
    assert all(i['packed'] for i in dependencies['images'] if i['source'] == 'FILE')
    assert all(f['packed'] or f['filepath'] == '<builtin>' for f in dependencies['fonts'])
    assert not dependencies['libraries'] and not dependencies['sounds']
    binary_paths = [repo / n for n in handoff['files'] if Path(n).suffix in {'.blend', '.png'}]
    assert len(binary_paths) == 13
    size = sum(p.stat().st_size for p in binary_paths)
    assert size < 100 * 1024 * 1024, 'Handoff binary size exceeds the declared storage budget'
    print(json.dumps({'status': 'PASS', 'source_sha256': sha, 'accepted': 140,
                      'score': ledger['score'], 'main_views': 10, 'supporting_views': 2,
                      'files_verified': len(handoff['files']), 'binary_bytes': size,
                      'scope': 'Original-file identity, profiles and recorded finite checks only; '
                               'no new render, exhaustive collision, map or runtime validation.'}, indent=2))


if __name__ == '__main__':
    main()
