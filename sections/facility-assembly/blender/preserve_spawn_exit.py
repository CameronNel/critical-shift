"""Preserve the established assembly-only service exit with directly linked art."""
import bpy, hashlib, json
from pathlib import Path

src = Path(bpy.data.filepath)
root = Path(__file__).resolve().parents[3]
out = root / 'runtime/out/spawn-integration'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
before = sha(src)
assert before == 'd647545d0c15d37bd9d6543002b367fb04d3cd6b9787dc5d83c6e9ba958874d7'
libs = {bpy.path.abspath(l.filepath): sha(bpy.path.abspath(l.filepath)) for l in bpy.data.libraries}
inst = bpy.data.objects['INSTANCE | spawn-room main PR48']
wrapper = inst.instance_collection
assert wrapper.library is None
names = ['SERVICE_end', 'SERVICE_end_washable_dado',
         'SERVICE_end_coved_skirt', 'SERVICE_end_dado_cap']
for name in names:
    o = wrapper.objects[name]
    assert o.library is not None
    wrapper.objects.unlink(o)
inst['existing_service_exit_exclusions'] = json.dumps(names)
assert len(wrapper.all_objects) == 1958
assert sum(o.name.startswith('COZY_') for o in wrapper.all_objects) == 73
assert sha(src) == before and all(sha(p) == h for p, h in libs.items())
bpy.context.view_layer.update()
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(src), check_existing=False)
assert all(sha(p) == h for p, h in libs.items())
report = dict(before=before, after=sha(src), excluded=names,
              linked_objects=1958, source_files_unchanged=True)
(out / 'exit-preservation.json').write_text(json.dumps(report, indent=2))
print('SPAWN_EXIT_PRESERVED', report, flush=True)
