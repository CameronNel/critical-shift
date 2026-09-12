"""Saved full04 walkthrough inventory; no live Blender, render, mutation or save."""
import bpy,json,hashlib,math,re
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent
SAVED=HERE.parent/'checkpoints/full04/Fuel_Corridor.blend'
EXPECTED='e2bcb2ddb4e2d6dda969520b2bbbaa7eab4e7f537d52e7b48537404091c24b35'
assert hashlib.sha256(SAVED.read_bytes()).hexdigest()==EXPECTED
assert not bpy.data.filepath
bpy.ops.wm.open_mainfile(filepath=str(SAVED),load_ui=False)
scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
contract=json.loads((SAVED.parent/'interface.json').read_text())
def ancestors(o):
    while o:
        yield o;o=o.parent
def bbox(points):return [[f(p[i] for p in points) for i in range(3)] for f in [min,max]]
def evaluated(o):
    ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles()
    points=[ev.matrix_world@v.co for v in me.vertices];tris=[tuple(t.vertices) for t in me.loop_triangles]
    ev.to_mesh_clear();return points,tris
def convert(v):
    if isinstance(v,(str,int,float,bool)) or v is None:return v
    if hasattr(v,'items'):return {k:convert(x) for k,x in v.items()}
    return [convert(x) for x in v]
physical=[]
for o in scene.objects:
    if o.type not in {'MESH','CURVE'} or o.get('surface_decal'):continue
    if o.type=='CURVE' and not o.data.bevel_depth:continue
    pp,tt=evaluated(o)
    physical.append({'obj':o,'bounds':bbox(pp),'bvh':BVHTree.FromPolygons(pp,tt,all_triangles=True)})
print('PHYSICAL',len(physical),flush=True)
floors=[]
for c in contract['floor_cells']:
    o=scene.objects.get('Floor_'+c['id']);pp,tt=evaluated(o);bb=bbox(pp)
    floors.append({'id':c['id'],'object':o.name,'actual_bounds_m':bb,'contract_xy':c['bounds'],
                   'contract_ceiling_height_m':c['height'],'floor_top_m':bb[1][2]})
doors=[]
for o in scene.objects:
    if 'port_id' not in o:continue
    descendants=[x for x in scene.objects if o in list(ancestors(x))]
    leaves=[x for x in descendants if re.fullmatch(re.escape(o.name)+r'_sliding_leaf(?:\.\d+)?',x.name)]
    carriages=[x for x in descendants if x.get('component_role')=='sliding_leaf_carriage']
    doors.append({'root':o.name,'properties':convert(dict(o.items())),
                   'carriages':[{'name':x.name,'properties':convert(dict(x.items()))} for x in carriages],
                   'leaves':[{'name':x.name,'bounds_m':bbox(evaluated(x)[0]),'properties':convert(dict(x.items()))} for x in leaves],
                   'texts':[{'name':x.name,'text':x.data.body} for x in descendants if x.type=='FONT']})
fonts=[]
for o in scene.objects:
    if o.type!='FONT':continue
    pp,tt=evaluated(o)
    if not pp:continue
    bb=bbox(pp);center=Vector([(bb[0][i]+bb[1][i])/2 for i in range(3)])
    normal=(o.matrix_world.to_3x3()@Vector((0,0,1))).normalized();direction=-normal
    end=center+direction*1.2;segment=bbox([center,end]);hits=[]
    for m in physical:
        b=m['bounds']
        if not all(segment[0][i]<=b[1][i]+.001 and b[0][i]<=segment[1][i]+.001 for i in range(3)):continue
        p,n,t,d=m['bvh'].ray_cast(center,direction,1.2)
        if p is not None:hits.append({'object':m['obj'].name,'distance_m':d,'point':list(p),'normal':list(n)})
    fonts.append({'name':o.name,'text':o.data.body,'font_size_m':o.data.size,'align':o.data.align_x,
                   'center_world_m':list(center),'bounds_m':bb,'front_normal':list(normal),
                   'ancestors':[a.name for a in ancestors(o)],'backing_center_ray':min(hits,key=lambda h:h['distance_m']) if hits else None})
routes={k:{'points':p,'length_m':sum(math.dist(a,b) for a,b in zip(p,p[1:]))} for k,p in contract['route_centerlines'].items()}
allfloor=[Vector(p) for r in floors for p in r['actual_bounds_m']]
report={'saved_blend':str(SAVED),'blend_sha256':EXPECTED,'revision':scene.get('revision'),'object_count':len(scene.objects),
        'source_hashes':{k:scene.get(k) for k in ['source_sha256','detail_source_sha256','interface_sha256']},
        'doors':doors,'door_count':len(doors),'leaf_count':sum(len(d['leaves']) for d in doors),
        'contract_port_count':len(contract['ports']),'contract_ports':contract['ports'],
        'floors':floors,'overall_floor_bounds_m':bbox(allfloor),'route_centerlines':routes,
        'texts':fonts,'method':'Actual saved object/leaf inventory, evaluated floor meshes, contract route lengths and font center backing rays against physical evaluated surfaces.',
        'limits':['Portals are not certified safe exits or live-neighbor passage.','Contract route lengths are planning centerlines, not timed player movement.','A center backing ray does not prove glyph extents fit their support or rendered readability.','No live instance, render, source edit, neighbor access or scene save.'],'saved':False}
assert hashlib.sha256(SAVED.read_bytes()).hexdigest()==EXPECTED
(HERE/'astra-walkthrough-full04-evidence.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'door_roots':[(d['root'],len(d['leaves']),d['properties']['port_id']) for d in doors],
                  'floor_bounds':report['overall_floor_bounds_m'],'routes':routes,'text_count':len(fonts)},indent=2))
