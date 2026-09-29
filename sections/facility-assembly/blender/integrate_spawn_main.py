"""Replace only the obsolete spawn cache with PR48's directly linked module."""
import bpy,json,hashlib,ctypes,sys
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3];src=Path(bpy.data.filepath)
out=root/'runtime/out/spawn-integration';out.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
before=sha(src);assert before=='964d81807cd3cc6c43f86a1de5c5a33cba8c13aceb32c44fccc93372cc28d763'
module=src.parent.parent/'sources/spawn-room/module.blend'
assert sha(module)=='9635f41aec585768285317399af9d6a3943411a66e20e2e3d96b05ad86dcfa40'
libraries={bpy.path.abspath(l.filepath):sha(bpy.path.abspath(l.filepath)) for l in bpy.data.libraries}
old=bpy.data.objects['MATERIAL_PREVIEW_spawn-room'];assert old.library and 'R17' in old.library.filepath
old_bounds=[list(old.matrix_world@Vector(p)) for p in old.bound_box]
# Removing a linked datablock from this assembly does not write its library.
bpy.data.objects.remove(old,do_unlink=True)
with bpy.data.libraries.load(str(module),link=True,relative=True) as (a,b):
    assert 'MODULE_spawn-room' in a.collections;b.collections=['MODULE_spawn-room']
linked=b.collections[0]
coll=bpy.data.collections.new('INTEGRATION | Current spawn module');bpy.context.scene.collection.children.link(coll)
inst=bpy.data.objects.new('INSTANCE | spawn-room main PR48',None);coll.objects.link(inst)
inst.instance_type='COLLECTION';inst.instance_collection=linked;inst.location=(-28,0,0)
inst['source_merge']='47b7eec8';inst['source_sha256']=sha(module)
bpy.context.view_layer.update()
assert any(o.name=='FACILITY_floor_slab' for o in linked.all_objects)
assert any(o.name.startswith('COZY_') for o in linked.all_objects)
# Old merged-room light copies must not double-light the directly linked room.
# Restrict removal to the old spawn interior footprint and explicit restored lights.
retired=[]
for o in list(bpy.data.objects):
    if o.library or o.type!='LIGHT' or not o.name.startswith('VC | Restored INTERIOR_'):continue
    x,y,z=o.matrix_world.translation
    if -35.47<x<-19.73 and -.71<y<12.41 and -.18<z<3.97:
        retired.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
# Save cameras for actual exterior and threshold checks without changing lighting.
for name,pos,target,lens in [('SI | Spawn threshold',(-28,15.7,1.65),(-28,9.3,1.3),24),('SI | Spawn east attachments',(-16,10.2,1.7),(-22,7.6,1.6),28),('SI | Medical attachments',(-26,29,1.7),(-20,33,1.8),28)]:
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);coll.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();data.lens=lens
assert sha(src)==before
assert all(sha(p)==h for p,h in libraries.items())
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(src),check_existing=False)
report=dict(before=before,after=sha(src),module_sha256=sha(module),module_objects=len(linked.all_objects),cozy_objects=sum(o.name.startswith('COZY_') for o in linked.all_objects),retired_cached_lights=retired,libraries=libraries,old_spawn_bounds=old_bounds,r17_regenerated=False)
(out/'integration.json').write_text(json.dumps(report,indent=2));print('DIRECT_SPAWN_LINKED',report,flush=True)
