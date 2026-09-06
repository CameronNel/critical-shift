#!/usr/bin/env python3
"""Fresh-process checks of the actual saved Blender scene, not object doubles.
Run: blender -b output_pbr/CriticalShift_Gullet_PBR.blend --python-exit-code 1
     --python pbr/validate_blender.py -- --output validation/blender
"""
from pathlib import Path
import argparse, json, math, runpy, sys
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
api=runpy.run_path(str(HERE/'build_textured_mine.py'),run_name='gullet_validation_import')
B=api['load_builder']()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=ROOT/'validation'/'blender')
p.add_argument('--render',default='')
p.add_argument('--width',type=int,default=896)
p.add_argument('--samples',type=int,default=16)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
a.output.mkdir(parents=True,exist_ok=True)
scene=next((s for s in bpy.data.scenes if s.get('csm_material_revision')),None)
if scene is None:raise RuntimeError('Open the generated PBR .blend in a fresh process first.')
if bpy.context.window:bpy.context.window.scene=scene
report={'blender':bpy.app.version_string,'file':Path(bpy.data.filepath).name,'fresh_process':True,
        'renderer':'Cycles','status':'RUNNING','assertions':0,'issues':[],
        'scope':'Blender file, images, actual bpy state/gate controls and sampled route clearance. Not Unity or final art acceptance.'}

def check(value,message):
    report['assertions']+=1
    if not value:report['issues'].append(message)

B.install_api(scene);B.register_controls()
meshes=[o for o in scene.objects if o.type=='MESH']
check(len({o.get('csm_id',o.name) for o in meshes})==len(meshes),'Duplicate semantic mesh IDs')
keys={o.get('csm_camera_key') for o in scene.objects if o.type=='CAMERA'}
check({'entry','main_route','bay_overview','dispatch','charge_issue','reverse_route','dry_cut','sump','wet_cut','collapse'}<=keys,'Missing fixed cameras')
used={s.material for o in meshes for s in o.material_slots if s.material}
images={n.image for mat in used if mat.use_nodes for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
report['images']=[{'name':im.name,'packed':bool(im.packed_file),'size':list(im.size)} for im in images]
for im in images:check(bool(im.packed_file),'Scene-used image is not packed: '+im.name)
for obj in meshes:
    check(len(obj.data.polygons)>0,'Empty geometry: '+obj.name)
    check(bool(obj.data.uv_layers),'Missing UV coordinates: '+obj.name)
    check(all(math.isfinite(c) for v in obj.data.vertices for c in v.co),'Non-finite geometry: '+obj.name)
state_json=scene['csm_states_json']
control=B.find_owned(scene,B.PREFIX+'CTRL_BLAST_GATE')
gate_value=control.get('csm_open_fraction',1.0)
apply_event=next((getattr(B,n) for n in ['apply_excavation_event','apply_game_blast','apply_game_cut'] if hasattr(B,n)),None)
if apply_event is None:raise RuntimeError('State authoring API is missing.')
try:
    for sector in B.SECTORS:
        B.reset_states(scene)
        for value,stage in [(1,1),(3,2),(1,2),(5,3)]:
            check(apply_event(scene,sector,value)['state']==stage,'Incorrect progressive state '+sector)
        check(apply_event(scene,sector,7)['remaining_rubble']==22,'Collapse count '+sector)
        for value in [1,5,12]:
            blocked=False
            try:apply_event(scene,sector,value)
            except ValueError:blocked=True
            check(blocked,'Uncleared collapse bypassed '+sector)
        for i in range(22):
            st=B.clear_next_rubble(scene,sector)
            check(st['remaining_rubble']==21-i,'Rubble removal '+sector)
            check(st['state']==(3 if i==21 else 4),'Premature reopening '+sector)
        for other in B.SECTORS:
            if other!=sector:check(B.read_states(scene)[other]['state']==0,'State leaked to '+other)
    leaves=[B.find_owned(scene,B.PREFIX+'Blast_leaf_'+s) for s in ('L','R')]
    for fraction in [0.,.25,1.]:
        B.set_gate(scene,fraction)
        for leaf in leaves:
            check(abs(leaf.location.x-(leaf['csm_closed_x']+leaf['csm_travel']*fraction))<1e-5,'Gate root transform incorrect')
finally:
    scene['csm_states_json']=state_json;B.apply_visibility(scene);B.set_gate(scene,gate_value)

# Cast through the actual visible mesh along a standing worker's main walkway.
verts=[];faces=[]
for obj in meshes:
    if obj.hide_render or obj.get('csm_collision_only'):continue
    offset=len(verts)
    verts.extend(obj.matrix_world@v.co for v in obj.data.vertices)
    faces.extend(tuple(offset+i for i in poly.vertices) for poly in obj.data.polygons)
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=False)
route=[]
for i in range(61):
    y=1.8+i*.55; floor=-.025*max(y,0)
    point=Vector((2.02,y,floor+.28))
    location,normal,index,distance=bvh.ray_cast(point,Vector((0,0,1)),1.60)
    clear=location is None
    route.append({'x':2.02,'y':round(y,2),'standing_clear':clear})
    check(clear,'Standing-path obstruction at y='+str(round(y,2)))
report['standing_path_probes']=route
report['mesh_objects']=len(meshes);report['status']='FAIL' if report['issues'] else 'PASS'
if a.render and not report['issues']:
    B.configure_device(bpy,scene,'cpu')
    report['cold_start_renders']=api['render'](scene,a.output/'renders',a.render,a.samples,a.width)
(a.output/'cold_start_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['images','standing_path_probes']},indent=2),flush=True)
if report['issues']:raise RuntimeError('Cold-start checks failed; inspect the JSON report.')
