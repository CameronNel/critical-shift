"""Cold-open, preservation, source-link, route and reactor-interface checks."""
import bpy,json,hashlib,ctypes
import numpy as np
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3];src=Path(bpy.data.filepath);out=root/'runtime/out/spawn-integration'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(src)
def sig(o):
    h=hashlib.sha256();h.update(str((o.type,[list(r) for r in o.matrix_world],o.hide_render,o.hide_viewport)).encode())
    if o.type=='MESH':
        for seq,field,dtype,n in [(o.data.vertices,'co','f',3),(o.data.loops,'vertex_index','i',1),(o.data.polygons,'material_index','i',1)]:
            a=np.empty(len(seq)*n,dtype=dtype);seq.foreach_get(field,a);h.update(a.tobytes())
        h.update(str([m.name if m else None for m in o.data.materials]).encode())
    elif o.type=='LIGHT':h.update(str((o.data.type,o.data.energy,list(o.data.color))).encode())
    elif o.type=='FONT':h.update(o.data.body.encode())
    return h.hexdigest()
final={o.name:sig(o) for o in bpy.data.objects if not o.library}
sy=[o for o in bpy.data.objects if o.name.startswith('SY |')]
inst=bpy.data.objects['INSTANCE | spawn-room main PR48'];linked=list(inst.instance_collection.all_objects)
assert all(o.library and o.library.filepath.startswith('//') and 'sources' in o.library.filepath for o in linked)
assert len([o for o in linked if o.name.startswith('COZY_')])==73
assert not any(o.name=='AIRLOCK_leaf_body' for o in linked)
assert len(linked)==1958
assert not any(o.name in ('SERVICE_end','SERVICE_end_washable_dado','SERVICE_end_coved_skirt','SERVICE_end_dado_cap') for o in linked)
assert not bpy.data.objects.get('MATERIAL_PREVIEW_spawn-room')
slab=next(o for o in linked if o.name=='FACILITY_floor_slab');coords=[slab.matrix_world@Vector(p) for p in slab.bound_box]
slab_z=[min(p.z for p in coords),max(p.z for p in coords)];assert abs(slab_z[0]+.17)<.00001
integration=json.loads((out/'integration.json').read_text())
assert all(sha(p)==h for p,h in integration['libraries'].items())
missing=[(x.name,x.filepath) for x in bpy.data.images if x.users and x.source=='FILE' and not x.packed_file and not Path(bpy.path.abspath(x.filepath,library=x.library)).exists()]
missing_ids=[x.name for seq in (bpy.data.objects,bpy.data.meshes,bpy.data.materials,bpy.data.collections) for x in seq if x.is_missing and x.users]
# All added yard parts must stay clear of the restored walking floor, apart from
# intended shallow bedding of paving and exterior panel plinths.
sy_rows=[]
for o in sy:
    pts=[o.matrix_world@Vector(p) for p in o.bound_box]
    sy_rows.append(dict(name=o.name,type=o.type,bounds=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],materials=[a.material.name for a in o.material_slots if a.material]))
baseline=root.parent/'main-integration-20260914/sections/facility-assembly/blender/facility_environment.blend'
assert sha(baseline)=='964d81807cd3cc6c43f86a1de5c5a33cba8c13aceb32c44fccc93372cc28d763'
bpy.ops.wm.open_mainfile(filepath=str(baseline),load_ui=False)
original={o.name:sig(o) for o in bpy.data.objects if not o.library}
changed=[n for n in original.keys()&final.keys() if original[n]!=final[n]]
removed=sorted(original.keys()-final.keys());added=sorted(final.keys()-original.keys())
assert all(n.startswith('SY |') for n in changed),changed
assert len(removed)==17 and all(n.startswith('VC | Restored INTERIOR_') for n in removed),removed
assert all(n.startswith(('INSTANCE | spawn-room','SI |')) for n in added),added
assert sha(src)==before
report=dict(source_sha256=before,source_main_merge='47b7eec8',module_sha256=sha(root/'sections/facility-assembly/sources/spawn-room/module.blend'),linked_objects=len(linked),cozy_objects=73,slab_z=slab_z,sy_objects=sy_rows,changed_original_local_objects=changed,removed_old_spawn_interior_lights=removed,added=added,missing_images=missing,missing_used_ids=missing_ids,r17_unchanged=True,unchanged_original_local_objects=len(original)-len(changed)-len(removed),runtime_verified=False)
(out/'verification.json').write_text(json.dumps(report,indent=2));print('COLD_VERIFY',len(changed),len(sy_rows),'missing',missing,missing_ids,flush=True)
