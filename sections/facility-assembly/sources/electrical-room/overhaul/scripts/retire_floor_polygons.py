"""Retire a rejected new detail layer; preserve the entire reviewed room."""
import argparse,hashlib,json,os,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
import kit as k
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--receipt',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath).resolve();out=Path(a.output).resolve();assert source!=out
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
input_sha=sha(source)
assert not bpy.context.scene.get('electrical_floor_contact_revision')
root=bpy.data.objects[k.PREFIX+'Localized service plinth contacts']
pieces=[bpy.data.objects[k.PREFIX+'Individual service floor contact '+str(i)] for i in range(6)]
assert all(o.type=='MESH' and o.get('cs_assembly')==root.name for o in pieces)
removed=[o.name for o in pieces]+[root.name]
def signature(o):
    d={'matrix':sum((list(r) for r in o.matrix_world),[]),'type':o.type,
       'hidden':[o.hide_render,o.hide_viewport],
       'materials':[s.material.name if s.material else None for s in o.material_slots]}
    if o.type=='MESH':
        d['verts']=[list(v.co) for v in o.data.vertices]
        d['faces']=[(list(p.vertices),p.material_index,p.use_smooth) for p in o.data.polygons]
    elif o.type=='LIGHT':d['light']=[o.data.energy,list(o.data.color)]
    elif o.type=='CAMERA':d['lens']=o.data.lens
    elif o.type=='FONT':d['body']=o.data.body
    return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
before={o.name:signature(o) for o in bpy.context.scene.objects if o.name not in removed}
for o in pieces:
    mesh=o.data;bpy.data.objects.remove(o,do_unlink=True)
    assert mesh.users==0;bpy.data.meshes.remove(mesh)
bpy.data.objects.remove(root,do_unlink=True)
mat=bpy.data.materials[k.PREFIX+'Service plinth abrasion'];assert mat.users==0
bpy.data.materials.remove(mat)
bpy.context.scene['electrical_floor_contact_resolution']='Rejected new polygon-patch layer removed; existing floor history and finish retained.'
bpy.context.view_layer.update()
assert all(signature(bpy.data.objects[n])==sig for n,sig in before.items())
out.parent.mkdir(parents=True,exist_ok=True);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
assert sha(source)==input_sha
r={'repair_kind':'retire_new_floor_polygons','input_sha256':input_sha,'output_sha256':sha(out),
   'removed_new_object_names':removed,'removed_new_meshes':6,'removed_support_roots':1,
   'unused_new_material_removed':True,'checked_unchanged_objects':len(before),
   'all_other_matrices_geometry_material_assignments_visibility_lights_unchanged':True,
   'source_bytes_unchanged':True,'scope':'Remove only the rejected six new polygon floor patches and their support root/material. All original assets, existing floor wear, door history, shader response, cameras and practicals retained.'}
Path(a.receipt).resolve().write_text(json.dumps(r,indent=2)+'\n')
print('FLOOR_POLYGONS_RETIRED',out,flush=True)
sys.stdout.flush();sys.stderr.flush();os._exit(0)
