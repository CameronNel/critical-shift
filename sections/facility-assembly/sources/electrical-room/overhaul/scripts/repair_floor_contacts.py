"""Repair four new coating-loss pieces without changing the reviewed room."""
import argparse,hashlib,json,os,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
import kit as k
from floor_contacts import correct
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--receipt',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath).resolve();out=Path(a.output).resolve();assert source!=out
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
input_sha=sha(source)
assert not bpy.context.scene.get('electrical_floor_contact_revision')
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
before={o.name:signature(o) for o in bpy.context.scene.objects}
materials={m.name:m.node_tree.as_pointer() for m in bpy.data.materials if m.use_nodes}
changes=correct(k);moved={v['object'] for v in changes['moved_contacts']}
bpy.context.view_layer.update()
assert all(signature(bpy.data.objects[n])==sig for n,sig in before.items() if n not in moved)
assert materials=={m.name:m.node_tree.as_pointer() for m in bpy.data.materials if m.use_nodes}
out.parent.mkdir(parents=True,exist_ok=True);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
assert sha(source)==input_sha
r={'repair_kind':'service_floor_contact_exposure_repair','input_sha256':input_sha,'output_sha256':sha(out),
   'declared_changes':changes,'checked_unchanged_objects':len(before)-len(moved),
   'all_other_matrices_geometry_material_assignments_visibility_lights_unchanged':True,
   'source_bytes_unchanged':True,'scope':'Move exactly four new contact contours to exposed service-epoxy edges outside insulating mats, raise by measured1.3mm panel height and register actual panels. Every contour corner/center checks its first surface. Original room/cameras, shader nodes and practicals unchanged.'}
Path(a.receipt).resolve().write_text(json.dumps(r,indent=2)+'\n')
print('FLOOR_CONTACTS_SAVED',out,flush=True)
sys.stdout.flush();sys.stderr.flush();os._exit(0)
