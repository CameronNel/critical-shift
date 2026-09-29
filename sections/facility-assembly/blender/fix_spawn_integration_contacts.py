"""Bounded correction of measured SY support gaps and existing airlock binding."""
import bpy,json,hashlib,ctypes
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3];src=Path(bpy.data.filepath);out=root/'runtime/out/spawn-integration'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(src)
assert before==json.loads((out/'integration.json').read_text())['after']
libs={bpy.path.abspath(l.filepath):sha(bpy.path.abspath(l.filepath)) for l in bpy.data.libraries}
changed=[]
def remap_extent(name,axis,low=None,high=None):
    o=bpy.data.objects[name];assert o.library is None
    pts=[o.matrix_world@v.co for v in o.data.vertices];a=min(p[axis] for p in pts);b=max(p[axis] for p in pts);aa=a if low is None else low;bb=b if high is None else high;inv=o.matrix_world.inverted()
    o.data=o.data.copy()
    for v,p in zip(o.data.vertices,pts):p[axis]=aa+(p[axis]-a)/(b-a)*(bb-aa);v.co=inv@p
    o.data.update();changed.append(dict(name=name,axis=axis,before=[a,b],after=[aa,bb]))
# The probe found an 80 mm air gap behind both entrance canopy anchor plates.
for name in ('SY | Canopy wall anchor','SY | Canopy wall anchor.001'):remap_extent(name,1,low=12.489)
# Four fixtures were 15 mm below their canopy's underside, with no mount.
for o in bpy.data.objects:
    if o.name.startswith(('SY | Canopy light housing','SY | Canopy warm light diffuser')):
        o.location.z+=.015;changed.append(dict(name=o.name,translation=[0,0,.015]))
# These anchor ends stopped 9 mm short of their support plates.
for o in bpy.data.objects:
    if o.name.startswith('SY | Medical support seated anchor'):
        o.location.y+=.010;changed.append(dict(name=o.name,translation=[0,.010,0]))
# Keep walking elevations unchanged; extend only slab undersides to the probed bed.
remap_extent('SY | Dimensional courtyard slab.058',2,low=-.026)
remap_extent('SY | Dimensional courtyard slab.059',2,low=-.016)
# Keep every new linked art object, but retain the assembly's established open-door
# membership filter. No source object, collection or file is modified.
inst=bpy.data.objects['INSTANCE | spawn-room main PR48'];module=inst.instance_collection
bindings=json.loads((root/'sections/facility-assembly/connections/access/DOOR_BINDINGS.json').read_text())
excluded=set(n for d in bindings if d['sid']=='spawn-room' for n in d['exclude_names'])
wrapper=bpy.data.collections.new('INTEGRATION | Spawn linked art with existing airlock override')
for o in module.all_objects:
    if o.name not in excluded:wrapper.objects.link(o)
assert excluded<={o.name for o in module.all_objects}
inst.instance_collection=wrapper
inst['linked_source_collection']='MODULE_spawn-room';inst['existing_airlock_exclusions']=json.dumps(sorted(excluded))
# Restore two exterior entry pools accidentally included in the spatial interior-
# light retirement screen. Only INTERIOR_ light copies should have been retired.
baseline=root.parent/'main-integration-20260914/sections/facility-assembly/blender/facility_environment.blend'
assert sha(baseline)=='964d81807cd3cc6c43f86a1de5c5a33cba8c13aceb32c44fccc93372cc28d763'
names=['VC | Restored Shift entry pool.002','VC | Restored Shift entry pool.003']
names=[n for n in names if bpy.data.objects.get(n) is None]
with bpy.data.libraries.load(str(baseline),link=False) as (a,b):b.objects=list(names)
for o in b.objects:
    assert o is not None;bpy.data.collections['VC | 08 Restored authored lighting'].objects.link(o)
assert sum(o.name.startswith('COZY_') for o in wrapper.all_objects)==73
assert sha(src)==before and all(sha(p)==h for p,h in libs.items())
bpy.context.view_layer.update();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(src),check_existing=False)
report=dict(before=before,after=sha(src),changed=changed,airlock_excluded=sorted(excluded),restored_exterior_lights=names,linked_objects=len(wrapper.all_objects),r17_unchanged=True)
(out/'corrections.json').write_text(json.dumps(report,indent=2));print('CORRECTED',len(changed),report['after'],flush=True)
