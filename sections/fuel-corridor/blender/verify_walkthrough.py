"""CPU-only saved-file comparison of original floors/doors and corrected signs."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[1]
checkpoint=root/'production/checkpoints/walkthrough'
def signature(o):
    return hashlib.sha256(repr((list(map(list,o.matrix_world)),[list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])).encode()).hexdigest()
prefixes=('REFINERY_BOUNDARY','REACTOR_BOUNDARY','PLANT_PORT','CLEAN_PORT','WASTE_PORT','FREIGHT_GATE','Floor_')
def geometry():return {o.name:signature(o) for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(prefixes)}
bpy.ops.wm.open_mainfile(filepath=str(checkpoint/'corrected.blend'))
corrected=geometry();s=bpy.context.scene
doors=[{'name':o.name,'port':o['port_id'],'position':list(o.matrix_world.translation)} for o in s.objects if o.get('port_id')]
leaves=[o.name for o in s.objects if o.get('component_role')=='sliding_leaf_carriage']
panels=[{'name':o.name,'code':o.get('wayfinding_code')} for o in s.objects if o.get('component_role')=='wall_wayfinding_panel']
text_sizes={role:sorted(set(round(o.data.size,5) for o in s.objects if o.type=='FONT' and o.parent and o.parent.get('component_role')=='wall_wayfinding_panel' and o.name.endswith('_'+role))) for role in ['number','title','subtitle']}
# Check a wall/post exists behind each physical mounting foot, excluding all signs.
dg=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];owners=[]
for o in s.objects:
    if o.type!='MESH' or o.get('surface_decal') or (o.parent and o.parent.get('component_role')=='wall_wayfinding_panel'):continue
    ev=o.evaluated_get(dg);me=ev.to_mesh();offset=len(verts)
    verts.extend(ev.matrix_world@v.co for v in me.vertices);faces.extend(tuple(offset+i for i in p.vertices) for p in me.polygons);owners.extend([o.name]*len(me.polygons));ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts,faces);mounts=[]
for o in s.objects:
    if '_mount_foot' not in o.name or not(o.parent and o.parent.get('component_role')=='wall_wayfinding_panel'):continue
    center=sum((o.matrix_world@Vector(c) for c in o.bound_box),Vector())/8;n=Vector(o['wayfinding_normal'])
    hit,normal,index,distance=bvh.ray_cast(center+n*.5,-n,.515)
    mounts.append({'name':o.name,'support':owners[index] if hit is not None else None,'front_to_support_m':distance})
bpy.ops.wm.open_mainfile(filepath=str(checkpoint/'live-before.blend'))
before=geometry();changed=sorted(k for k in before.keys()&corrected.keys() if before[k]!=corrected[k]);missing=sorted(before.keys()-corrected.keys())
report={'base':'live-before.blend','corrected':'corrected.blend','geometry_compared':len(before),'changed_original_floor_or_door_meshes':changed,'missing_original_floor_or_door_meshes':missing,'doors':doors,'sliding_leaves':leaves,'panels':panels,'consistent_font_sizes_m':text_sizes,'mounts':mounts,'pass':not changed and not missing and len(doors)==6 and len(leaves)==12 and all(x['support'] for x in mounts)}
(root/'production/evidence/walkthrough/saved-geometry-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['doors','sliding_leaves','panels','mounts']}))
assert report['pass'], 'Walkthrough geometry verification failed'
