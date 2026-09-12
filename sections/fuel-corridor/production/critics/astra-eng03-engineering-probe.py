"""Independent evaluated eng03 checks. CPU only, no render or scene save.
Moving states are mathematical translations of evaluated vertex copies; scene state stays unchanged.
"""
from pathlib import Path
import bpy, hashlib, json, math, time
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE=Path(__file__).resolve().parent
SECTION=HERE.parents[1]
SAVED=SECTION/'production/checkpoints/eng03/Fuel_Corridor.blend'
EXPECTED='bf22ed9f5ef31b52a4cb7031c7055080d111396a515cd145c160126c1d85e31a'
assert hashlib.sha256(SAVED.read_bytes()).hexdigest()==EXPECTED
assert not bpy.data.filepath
bpy.ops.wm.open_mainfile(filepath=str(SAVED),load_ui=False)
scene=bpy.context.scene
assert scene.get('stage')=='full' and scene.get('revision')=='eng03'
bpy.context.view_layer.update()
deps=bpy.context.evaluated_depsgraph_get()
start=time.perf_counter()

def ancestors(o):
    while o:
        yield o
        o=o.parent

def bounds(points):
    return tuple(Vector([fn(p[a] for p in points) for a in range(3)]) for fn in [min,max])

def overlap_bounds(a,b,pad=0):
    return all(a[0][i]<=b[1][i]+pad and b[0][i]<=a[1][i]+pad for i in range(3))

def gap_bounds(a,b):
    return math.sqrt(sum(max(0,a[0][i]-b[1][i],b[0][i]-a[1][i])**2 for i in range(3)))

class Mesh:
    def __init__(self,obj,offset=None,base=None):
        self.obj=obj
        if base is not None:
            self.points=[p+offset for p in base.points]
            self.tris=base.tris
        else:
            ev=obj.evaluated_get(deps)
            me=ev.to_mesh()
            self.points=[ev.matrix_world@v.co for v in me.vertices]
            me.calc_loop_triangles()
            self.tris=[tuple(t.vertices) for t in me.loop_triangles]
            ev.to_mesh_clear()
        self.bounds=bounds(self.points)
        self.bvh=BVHTree.FromPolygons(self.points,self.tris,all_triangles=True,epsilon=0)

def inside(mesh,point):
    """Parity containment supplement; two deterministic non-axis rays agree."""
    votes=[]
    for xyz in [(0.911,.313,.269),(-.237,.927,.289)]:
        direction=Vector(xyz).normalized();origin=point.copy();count=0
        for _ in range(32):
            loc,normal,index,distance=mesh.bvh.ray_cast(origin,direction,100)
            if loc is None:break
            if distance<1e-6:return False
            count+=1;origin=loc+direction*1e-5
        votes.append(count%2==1)
    return all(votes)

def intersection(a,b):
    if not overlap_bounds(a.bounds,b.bounds):return None
    overlap_xyz=[min(a.bounds[1][i],b.bounds[1][i])-max(a.bounds[0][i],b.bounds[0][i]) for i in range(3)]
    diagnostic={'aabb_overlap_xyz_m':overlap_xyz,'a_bounds_world_m':[list(p) for p in a.bounds],
                'b_bounds_world_m':[list(p) for p in b.bounds],
                'aabb_contact_only_within_1um':min(overlap_xyz)<=1e-6}
    pairs=a.bvh.overlap(b.bvh)
    if pairs:
        ia,ib=pairs[0]
        return {'method':'evaluated_triangle_surface_overlap','triangle_pairs':len(pairs),**diagnostic,
                'first_triangle_a':[list(a.points[k]) for k in a.tris[ia]],
                'first_triangle_b':[list(b.points[k]) for k in b.tris[ib]]}
    # Surface tests miss a fully contained closed part. Sample a bounded vertex set.
    for test,container in [(a,b),(b,a)]:
        for p in test.points[::max(1,len(test.points)//8)][:9]:
            if inside(container,p):return {'method':'two_ray_containment_sample','contained_object':test.obj.name,'point':list(p),**diagnostic}
    return None

gate_region=(Vector((5.65,5.9,-.05)),Vector((7.1,14.1,4.7)))
service_region=(Vector((-1.9,13.05,.65)),Vector((1.2,15.9,3.25)))
meshes={}
for obj in scene.objects:
    if obj.type not in {'MESH','CURVE'} or obj.get('surface_decal'):continue
    if obj.type=='CURVE' and obj.data.bevel_depth==0:continue
    bb=bounds([obj.matrix_world@Vector(p) for p in obj.bound_box])
    chain=list(ancestors(obj))
    if (overlap_bounds(bb,gate_region) or overlap_bounds(bb,service_region)
        or obj.name.startswith(('Ceiling_','Recessed_ceiling','Height_step'))
        or any(p.name in {'FREIGHT_GATE','Service_pipework','Service_air_station','Longitudinal_tray','Freight_bulkhead',
                          'REFINERY_BOUNDARY','REACTOR_BOUNDARY','PLANT_PORT','CLEAN_PORT','WASTE_PORT'} for p in chain)):
        meshes[obj.name]=Mesh(obj)
print('SELECTED_EVALUATED_MESHES',len(meshes),flush=True)

carriages=[o for o in scene.objects if o.get('component_role')=='sliding_leaf_carriage' and o.parent and o.parent.name=='FREIGHT_GATE']
assert len(carriages)==2
moving_names={o.name for o in scene.objects if any(p in carriages for p in ancestors(o))}
moving={c.name:[m for n,m in meshes.items() if n in moving_names and c in list(ancestors(m.obj))] for c in carriages}
fixed=[m for n,m in meshes.items() if n not in moving_names and overlap_bounds(m.bounds,gate_region)]
motion_pairs={}
roller_contacts={}
gate_rails=[m for m in meshes.values() if m.obj.name.startswith('FREIGHT_GATE_running_rail')]
assert len(gate_rails)==2
count=38
for step in range(count+1):
    f=step/count
    states=[]
    for c in carriages:
        translation=Vector(c['closed_to_open_translation_m'])*(f-1)
        current=[Mesh(m.obj,translation,m) for m in moving[c.name]]
        states.append(current)
        for m in current:
            if m.obj.name.startswith('FREIGHT_GATE_leaf_carriage_roller'):
                bottom=m.bounds[0].z
                bottom_points=[p for p in m.points if p.z<=bottom+2e-6]
                rail_samples=[]
                for rail in gate_rails:
                    distances=[rail.bvh.find_nearest(p)[3] for p in bottom_points]
                    distance=min(d for d in distances if d is not None)
                    support_rays=[]
                    for p in bottom_points:
                        hit=rail.bvh.ray_cast(p+Vector((0,0,.001)),Vector((0,0,-1)),.01)
                        if hit[0] is not None:support_rays.append(hit[3]-.001)
                    rail_samples.append({'rail':rail.obj.name,'minimum_bottom_vertex_to_rail_surface_m':distance,
                                         'roller_bottom_minus_rail_top_m':bottom-rail.bounds[1].z,
                                         'vertical_support_ray_signed_gap_m':min(support_rays,key=abs) if support_rays else None,
                                         'bottom_vertex_count':len(bottom_points)})
                witness=min(rail_samples,key=lambda v:v['minimum_bottom_vertex_to_rail_surface_m'])
                roller_contacts.setdefault(m.obj.name,[]).append({'fraction':round(f,6),**witness})
            for other in fixed:
                hit=intersection(m,other)
                if not hit:continue
                key=(m.obj.name,other.obj.name)
                if key not in motion_pairs:motion_pairs[key]={'moving':key[0],'fixed':key[1],'states':[],'first_evidence':hit}
                motion_pairs[key]['states'].append(round(f,6))
    for a in states[0]:
        for b in states[1]:
            hit=intersection(a,b)
            if hit:
                key=(a.obj.name,b.obj.name)
                if key not in motion_pairs:motion_pairs[key]={'moving':key[0],'opposite_moving':key[1],'states':[],'first_evidence':hit}
                motion_pairs[key]['states'].append(round(f,6))
    if step%10==0:print('GATE_SAMPLED_STATE',step,count,flush=True)

near_closed=[]
for fraction in [0,.001,.002,.004,.005,.0055,.006,.01]:
    states=[]
    for c in carriages:
        translation=Vector(c['closed_to_open_translation_m'])*(fraction-1)
        states.append([Mesh(m.obj,translation,m) for m in moving[c.name] if 'carriage_roller' in m.obj.name])
    hits=[]
    for a in states[0]:
        for b in states[1]:
            hit=intersection(a,b)
            if hit:hits.append({'a':a.obj.name,'b':b.obj.name,**hit})
    near_closed.append({'fraction':fraction,'opposing_roller_intersections':hits})

def assembly_meshes(root_name):
    return [m for m in meshes.values() if any(o.name==root_name for o in ancestors(m.obj))]

def pair_audit(group_a,group_b):
    hits=[];closest=None
    for a in group_a:
        for b in group_b:
            if a.obj==b.obj:continue
            gap=gap_bounds(a.bounds,b.bounds)
            if closest is None or gap<closest['aabb_lower_bound_m']:closest={'a':a.obj.name,'b':b.obj.name,'aabb_lower_bound_m':gap}
            hit=intersection(a,b)
            if hit:hits.append({'a':a.obj.name,'b':b.obj.name,**hit})
    return {'pairs_tested':len(group_a)*len(group_b),'intersections':hits,'minimum_aabb_gap':closest}

crown=[m for n,m in meshes.items() if n.startswith(('Gate_crown','Tray_penetration'))]
overhead=[m for n,m in meshes.items() if n.startswith('FREIGHT_GATE_') and ('motor' in n or 'lintel' in n or 'drive_' in n or 'running_rail' in n)]
tray=assembly_meshes('Longitudinal_tray')
fixed_checks={'crown_to_gate_overhead':pair_audit(crown,overhead),
              'tray_to_gate_overhead':pair_audit(tray,overhead),
              'tray_to_crown':pair_audit(tray,crown)}
print('FIXED_GATE_CHECKED',flush=True)

all_ceilings=[m for m in meshes.values() if m.obj.name.startswith(('Ceiling_','Recessed_ceiling','Height_step'))]
external_heads={}
external_saved_roller_pairs={}
for name in ['REFINERY_BOUNDARY','REACTOR_BOUNDARY','PLANT_PORT','CLEAN_PORT','WASTE_PORT']:
    members=assembly_meshes(name)
    assert members,name
    external_heads[name]=pair_audit(members,all_ceilings)
    roots=[o for o in scene.objects if o.get('component_role')=='sliding_leaf_carriage' and o.parent and o.parent.name==name]
    assert len(roots)==2
    groups=[[m for m in members if 'carriage_roller' in m.obj.name and root in list(ancestors(m.obj))] for root in roots]
    external_saved_roller_pairs[name]=pair_audit(*groups)

pipe=meshes['Service_air_station_service_pipe']
branch=meshes['Recess_air_branch']
architecture=[m for m in meshes.values() if any(c.name=='01_Architecture' for c in m.obj.users_collection) and overlap_bounds(m.bounds,service_region)]
ceiling=[m for m in architecture if m.obj.name.startswith(('Ceiling_','Recessed_ceiling','Height_step'))]
service_checks={'station_pipe_to_architecture':pair_audit([pipe],architecture),
                'branch_to_architecture':pair_audit([branch],architecture),
                'station_pipe_to_ceiling':pair_audit([pipe],ceiling)}

def curve_points(name):
    obj=scene.objects[name]
    return [obj.matrix_world@Vector(p.co[:3]) for p in obj.data.splines[0].points]
def segment_distance(p,a,b):
    d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared))
    return (p-(a+t*d)).length
branch_points=curve_points('Recess_air_branch')
station_points=curve_points('Service_air_station_service_pipe')
loop_points=curve_points('Service_air_loop')
feed={'branch_world_centerline':[list(p) for p in branch_points],
      'station_inlet_world':list(station_points[0]),
      'branch_to_station_endpoint_gap_m':(branch_points[-1]-station_points[0]).length,
      'branch_to_loop_centerline_gap_m':min(segment_distance(branch_points[0],a,b) for a,b in zip(loop_points,loop_points[1:])),
      'branch_to_station_surfaces':intersection(branch,pipe),
      'branch_to_loop_surfaces':intersection(branch,meshes['Service_air_loop']),
      'reserved_supply_caps':[n for n in meshes if n.startswith('Air_supply_reserved')]}

report={'blend':str(SAVED),'blend_sha256':EXPECTED,'revision':scene['revision'],'stage':scene['stage'],
        'blender_version':bpy.app.version_string,'object_count':len(scene.objects),'evaluated_selected_mesh_count':len(meshes),
        'source_sha256':scene.get('source_sha256'),'detail_source_sha256':scene.get('detail_source_sha256'),'interface_sha256':scene.get('interface_sha256'),
        'gate_motion':{'samples':count+1,'fraction_semantics':'0=CLOSED, 1=authored OPEN','maximum_translation_step_m':1.85/count,
                       'moving_members':{k:[m.obj.name for m in v] for k,v in moving.items()},'fixed_member_count':len(fixed),
                       'intersecting_pairs':list(motion_pairs.values()),
                       'near_closed_opposing_roller_diagnostic':near_closed,
                       'roller_support_contacts':roller_contacts,
                       'roller_contact_method':'Closest evaluated rail surface to minimum-Z roller vertices in all39 translated states; positive roller-to-fixed triangle overlaps checked separately.'},
        'gate_fixed_clearances':fixed_checks,'external_door_ceiling_clearances':external_heads,
        'external_saved_opposing_roller_pairs':external_saved_roller_pairs,'recess_clearance':service_checks,'feed_continuity':feed,
        'limits':['Finite 48.7 mm translation samples are not a continuous collision sweep or engine test.',
                  'Surface overlap plus bounded parity containment; no mechanical intent exceptions silently suppressed.',
                  'AABB separation is a conservative lower bound, not exact closest-triangle distance.',
                  'Only selected gate/service regions and external door-versus-ceiling pairs audited; neighbor scenes not imported.'],
        'no_render_no_save_no_scene_transform_mutation':True,'elapsed_seconds':time.perf_counter()-start}
assert hashlib.sha256(SAVED.read_bytes()).hexdigest()==EXPECTED
(HERE/'astra-eng03-engineering-probe.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'gate_pairs':[{'a':v['moving'],'b':v.get('fixed',v.get('opposite_moving')),'samples':len(v['states']),'first':v['states'][0],'last':v['states'][-1]} for v in motion_pairs.values()],
                  'fixed_gate_hits':{k:len(v['intersections']) for k,v in fixed_checks.items()},
                  'external_door_ceiling_hits':{k:[(h['a'],h['b']) for h in v['intersections']] for k,v in external_heads.items()},
                  'recess_hits':{k:[(h['a'],h['b']) for h in v['intersections']] for k,v in service_checks.items()},
                  'feed_endpoint_gap':feed['branch_to_station_endpoint_gap_m'],'feed_loop_gap':feed['branch_to_loop_centerline_gap_m'],
                  'elapsed':report['elapsed_seconds']},indent=2),flush=True)


