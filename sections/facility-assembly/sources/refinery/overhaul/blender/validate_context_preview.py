"""Read-only comparison of visible candidate placement in its map-context preview."""
import bpy, json, sys, hashlib
from pathlib import Path
from mathutils import Matrix

root = Path(__file__).resolve().parents[1]
repo = root.parents[4]
revision = sys.argv[sys.argv.index('--') + 1]
manifest = json.loads((root / 'production/context' / f'manifest_{revision}.json').read_text())
candidate = repo / manifest['candidate']
context_source = repo / manifest['context_source']
context = bpy.context.scene
path = Path(bpy.data.filepath)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
before = sha(path)
assert before == manifest['sha256']
assert sha(candidate) == manifest['candidate_sha256']
assert sha(context_source) == manifest['context_sha256']
transform = Matrix(manifest['transform'])
original_world = {o.name: o.matrix_world.copy() for o in context.objects}
with bpy.data.libraries.load(str(candidate), link=False) as (source, destination):
    names = list(source.objects)
    destination.objects = list(names)
# Evaluate source parent transforms in a temporary, unsaved scene.
source_scene = bpy.data.scenes.new('CHECK ONLY | Source transforms')
for obj in destination.objects:
    source_scene.collection.objects.link(obj)
bpy.context.window.scene = source_scene
bpy.context.view_layer.update()
errors, skipped, checked = [], [], 0
for name, source in zip(names, destination.objects):
    if source.hide_render:
        skipped.append(name)
        continue
    checked += 1
    if name not in original_world:
        errors.append(dict(name=name, error='missing'))
        continue
    expected = transform @ source.matrix_world
    delta = max(abs(original_world[name][i][j] - expected[i][j]) for i in range(4) for j in range(4))
    if delta > 1e-5:
        errors.append(dict(name=name, delta=delta))
light_count = len([o for o in context.objects if o.type == 'LIGHT'])
world = context.world.node_tree.nodes['Background'].inputs['Strength'].default_value
unchanged = sha(path) == before
passed = not errors and light_count == 21 and world == 0 and unchanged
report = dict(status='PASS' if passed else 'FAIL', source_sha256=before,
              transform_errors=errors, visible_candidate_comparison_count=checked,
              skipped_hidden_state_objects=skipped, light_count=light_count,
              world_strength=world, source_unchanged=unchanged,
              limitations='Visible candidate poses and practical count only. Hidden fault-state poses, exhaustive intersections and whole-map dependency health are not certified.')
(root / 'production/context' / f'validation_{revision}.json').write_text(json.dumps(report, indent=2))
print('CONTEXT_VALIDATION', report['status'], checked, len(errors), flush=True)
if not passed:
    raise RuntimeError('Context comparison failed')
