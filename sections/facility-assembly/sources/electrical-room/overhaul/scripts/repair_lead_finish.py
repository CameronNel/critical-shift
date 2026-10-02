"""Apply and measure the lead-storage/trolley correction on a saved source."""
import argparse, hashlib, json, os, sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
import kit as k
from lead_finish import apply
from vision_finish import apply as apply_vision

p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--receipt',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath).resolve();out=Path(a.output).resolve()
assert out!=source
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
before={o.name:signature(o) for o in bpy.context.scene.objects}
def material_signature(mat):
    def value(v):
        try:return list(v)
        except TypeError:return v
    if not mat.use_nodes:return hashlib.sha256(str(list(mat.diffuse_color)).encode()).hexdigest()
    r={'nodes':[(n.name,n.bl_idname,[(s.identifier,value(s.default_value)) for s in n.inputs if hasattr(s,'default_value')])
                for n in mat.node_tree.nodes],
       'links':[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier)
                for l in mat.node_tree.links]}
    return hashlib.sha256(json.dumps(r,sort_keys=True).encode()).hexdigest()
materials_before={mat.name:material_signature(mat) for mat in bpy.data.materials}
m={name:bpy.data.materials[k.PREFIX+name] for name in ['redrubber','rubber','zinc','slate','steel','ochre']}
changes=apply(k,m)
vision=apply_vision()
bpy.context.view_layer.update()
changed=set(changes['changed_existing_mesh_objects'])
expected={k.PREFIX+n+s for n in ['Coiled test lead','Lead reel hook','Test lead hanging tail',
                               'Lead terminal insulated grip','Resting test lead'] for s in ['', '.001']}
assert changed==expected
unchanged={n for n in before if n not in changed}
assert all(bpy.data.objects.get(n) and signature(bpy.data.objects[n])==before[n] for n in unchanged)
assert {mat.name for mat in bpy.data.materials}==set(materials_before)
material_changes=[mat.name for mat in bpy.data.materials if material_signature(mat)!=materials_before[mat.name]]
assert material_changes==['EOH | Wired vision glass'],material_changes
out.parent.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
assert sha(source)==input_sha
report={'repair_kind':'service_lead_and_vision_finish','input_sha256':input_sha,'output_sha256':sha(out),
        'declared_changes':changes,'vision_finish':vision,'unchanged_object_signatures':len(unchanged),
        'changed_material_definitions':material_changes,'all_other_material_definitions_unchanged':True,
        'all_other_matrices_geometry_material_assignments_visibility_lights_unchanged':True,
        'source_bytes_unchanged':True,
        'scope':'Ten cable/hook/boot meshes rebuilt, supported retainers/second ends added and one existing wired-glass roughness profile refined. All other geometry, material definitions, lights, interfaces and cameras preserved.'}
Path(a.receipt).resolve().write_text(json.dumps(report,indent=2)+'\n')
print('LEAD_FINISH_SAVED',out,flush=True)
sys.stdout.flush();sys.stderr.flush();os._exit(0)
