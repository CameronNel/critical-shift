"""Save the strictly additive reserve lighting stage and its measured receipt."""
import argparse, hashlib, json, os, sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
import kit as k
from reserve_finish import apply
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--receipt',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath).resolve();out=Path(a.output).resolve();assert source!=out
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
input_sha=sha(source)
def signature(o):
    r={'matrix':sum((list(row) for row in o.matrix_world),[]),'type':o.type,
       'hidden':[o.hide_render,o.hide_viewport],
       'materials':[slot.material.name if slot.material else None for slot in o.material_slots]}
    if o.type=='MESH':
        r['vertices']=[list(v.co) for v in o.data.vertices]
        r['polygons']=[(list(f.vertices),f.material_index,f.use_smooth) for f in o.data.polygons]
    elif o.type=='FONT':r['body']=o.data.body
    elif o.type=='LIGHT':r['light']=[o.data.energy,list(o.data.color)]
    elif o.type=='CAMERA':r['lens']=o.data.lens
    return hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest()
def material_signature(mat):
    def value(v):
        try:return list(v)
        except TypeError:return v
    r={'nodes':[(n.name,n.bl_idname,[(s.identifier,value(s.default_value)) for s in n.inputs if hasattr(s,'default_value')])
                for n in mat.node_tree.nodes] if mat.use_nodes else [],
       'links':[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier)
                for l in mat.node_tree.links] if mat.use_nodes else [],'diffuse_color':list(mat.diffuse_color)}
    return hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest()
before={o.name:signature(o) for o in bpy.context.scene.objects}
materials={mat.name:material_signature(mat) for mat in bpy.data.materials}
m={name:bpy.data.materials[k.PREFIX+name] for name in ['ceramic','slate','steel','replacement','zinc','rubber']}
changes=apply(k,m)
assert all(bpy.data.objects.get(n) and signature(bpy.data.objects[n])==v for n,v in before.items())
assert all(bpy.data.materials.get(n) and material_signature(bpy.data.materials[n])==v for n,v in materials.items())
out.parent.mkdir(parents=True,exist_ok=True);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
assert sha(source)==input_sha
report={'repair_kind':'additive_reserve_service_lighting','input_sha256':input_sha,'output_sha256':sha(out),
        'declared_changes':changes,'unchanged_object_signatures':len(before),
        'all_existing_object_signatures_unchanged':True,'all_existing_material_definitions_unchanged':True,
        'source_bytes_unchanged':True,
        'scope':'Nine supported low-voltage strips, raceways and supplies added to three existing reserve racks. No existing mesh, transform, light, material, interface or camera changed.'}
Path(a.receipt).resolve().write_text(json.dumps(report,indent=2)+'\n')
print('RESERVE_FINISH_SAVED',out,flush=True)
sys.stdout.flush();sys.stderr.flush();os._exit(0)
