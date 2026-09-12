"""Independent read-only evaluated wall fits and new mounting checks, eng07."""
from pathlib import Path
import runpy,json,hashlib,time
HERE=Path(__file__).resolve().parent
ctx=runpy.run_path(str(HERE/'astra-eng07-mesh-core.py'))
globals().update({k:ctx[k] for k in ['bpy','Vector','Mesh','scene','ancestors','intersection','bounds','overlap_bounds','SAVED','EXPECTED']})
names=['Service_air_station','East_distribution','Bypass_isolation','Bypass_first_aid','Bypass_work_permit',
       'Plant_work_permit','Clean_distribution','Reactor_turn_key','Refinery_approach_key','Reactor_left_key','Reactor_right_key',
       'Clean_branch_blade_sign','Plant_branch_blade_sign','Recess_task_light','East_wall_key']
names += ['Route_guide_%02d'%i for i in range(11)]
roots=[scene.objects[n] for n in names]
meshes={}
for obj in scene.objects:
    if obj.type not in {'MESH','CURVE'} or obj.get('surface_decal'):continue
    if obj.type=='CURVE' and obj.data.bevel_depth==0:continue
    meshes[obj.name]=Mesh(obj)
print('ALL_PHYSICAL_EVALUATED',len(meshes),flush=True)
architecture=[m for m in meshes.values() if any(c.name=='01_Architecture' for c in m.obj.users_collection)]

def nearest_ray(mesh_list,start,direction,max_distance):
    hits=[]
    for mesh in mesh_list:
        p,n,tri,d=mesh.bvh.ray_cast(start,direction,max_distance)
        if p is not None:hits.append({'object':mesh.obj.name,'point':list(p),'normal':list(n),'distance':d})
    return min(hits,key=lambda h:h['distance']) if hits else None

results=[]
for root in roots:
    members=[m for m in meshes.values() if root in list(ancestors(m.obj))]
    bb=bounds([p for m in members for p in m.bounds])
    outside=[m for m in meshes.values() if root not in list(ancestors(m.obj)) and overlap_bounds(m.bounds,bb,pad=.002)]
    positive=[];contacts=[]
    for m in members:
        for fixed in outside:
            hit=intersection(m,fixed)
            if hit:
                (contacts if hit['aabb_contact_only_within_1um'] else positive).append({'a':m.obj.name,'b':fixed.obj.name,**hit})
    anchor_results=[]
    anchors=json.loads(root.get('support_anchors','[]'))
    targets=json.loads(root.get('support_targets','[]'))
    direction=Vector(root.get('support_direction',[0,0,0]))
    if direction.length:direction.normalize()
    for i,xyz in enumerate(anchors):
        anchor=Vector(xyz)
        wall=nearest_ray(outside,anchor-direction*.10,direction,.50)
        own=nearest_ray(members,anchor+direction*.012,-direction,.35)
        if wall:wall['signed_anchor_gap_m']=(Vector(wall['point'])-anchor).dot(direction)
        if own:own['signed_back_face_to_anchor_m']=(Vector(own['point'])-anchor).dot(direction)
        anchor_results.append({'anchor':xyz,'direction':list(direction),'declared_target':targets[i] if i<len(targets) else None,
                               'actual_outside_ray':wall,'actual_assembly_back_ray':own})
    # Inspect every newly built spacer/foot and primary mounting back, not only the root's anchor.
    mount_results=[]
    tokens=('mounting_spacer','spacer_wall_foot','clamp_wall_spacer','termination_spacer','wall_spacer','ceiling_foot','Recess_light_pan')
    for m in members:
        if not any(t in m.obj.name for t in tokens):continue
        extreme=max(p.dot(direction) for p in m.points)
        pp=[p for p in m.points if extreme-p.dot(direction)<1e-5]
        center=sum(pp,Vector())/len(pp)
        wall=nearest_ray(outside,center-direction*.10,direction,.50)
        if wall:wall['signed_mount_back_gap_m']=(Vector(wall['point'])-center).dot(direction)
        others=[v for v in members if v.obj!=m.obj]
        internal=[]
        for other in others:
            hit=intersection(m,other)
            if hit:internal.append({'object':other.obj.name,'contact_within_1um':hit['aabb_contact_only_within_1um'],'overlap_xyz_m':hit['aabb_overlap_xyz_m'],'method':hit['method']})
        mount_results.append({'object':m.obj.name,'world_bounds_m':[list(p) for p in m.bounds],
                              'wall_facing_extreme_center':list(center),'actual_outside_ray':wall,'internal_contacts':internal})
    results.append({'assembly':root.name,'members':len(members),'world_bounds_m':[list(p) for p in bb],
                    'positive_outside_intersections':positive,'zero_thickness_outside_contacts':contacts,
                    'support_anchors':anchor_results,'physical_mount_checks':mount_results})
    print('ASSEMBLY_CHECKED',root.name,len(members),'POSITIVE',len(positive),flush=True)

def pair_audit(a,b):
    hits=[]
    for m in a:
        for f in b:
            if m.obj==f.obj:continue
            hit=intersection(m,f)
            if hit:hits.append({'a':m.obj.name,'b':f.obj.name,**hit})
    return {'pairs_tested':len(a)*len(b),'intersections':hits}
station_pipe=meshes['Service_air_station_service_pipe'];branch=meshes['Recess_air_branch']
union=meshes['Service_branch_union']
def curve_points(name):
    obj=scene.objects[name]
    return [obj.matrix_world@Vector(p.co[:3]) for p in obj.data.splines[0].points]
def segment_distance(p,a,b):
    d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared))
    return (p-(a+t*d)).length
bp=curve_points('Recess_air_branch');sp=curve_points('Service_air_station_service_pipe');lp=curve_points('Service_air_loop')
service={'branch_to_architecture':pair_audit([branch,union],architecture),
         'station_pipe_to_architecture':pair_audit([station_pipe],architecture),
         'branch_to_station_endpoint_gap_m':(bp[-1]-sp[0]).length,
         'branch_to_loop_centerline_gap_m':min(segment_distance(bp[0],a,b) for a,b in zip(lp,lp[1:])),
         'branch_to_station_surfaces':intersection(branch,station_pipe),
         'branch_to_loop_surfaces':intersection(branch,meshes['Service_air_loop']),
         'union_to_branch_surfaces':intersection(union,branch),
         'branch_world_centerline':[list(p) for p in bp],'station_world_centerline':[list(p) for p in sp]}
frozen=SAVED.parent
manifest=json.loads((frozen/'build_manifest.json').read_text())
hashes={n:hashlib.sha256((frozen/n).read_bytes()).hexdigest() for n in ['build.py','valorant_details.py','interface.json','handoff.json','Fuel_Corridor.blend']}
report={'revision':'eng07','blend':str(SAVED),'blend_sha256':EXPECTED,'object_count':len(scene.objects),
        'evaluated_physical_meshes':len(meshes),'frozen_file_hashes':hashes,
        'scene_hashes':{k:scene.get(k) for k in ['source_sha256','detail_source_sha256','interface_sha256']},
        'method':'Actual evaluated world meshes against all other local physical meshes; independent support rays plus each new physical spacer/foot contact.',
        'limits':['Positive surface intersections and bounded containment need mechanical interpretation, especially fasteners and intended mounting feet.',
                  'Support rays and pair contacts do not prove structural load capacity or internal attachment of every small part.',
                  'No continuous motion, live neighbors, runtime controllers, render or visual-quality inference.'],
        'assemblies':results,'service_feed':service,'no_save_render_or_scene_transform_mutation':True}
assert hashlib.sha256(SAVED.read_bytes()).hexdigest()==EXPECTED
(HERE/'astra-eng07-details-evidence.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'assemblies':[{'assembly':r['assembly'],'positive_pairs':[(p['a'],p['b']) for p in r['positive_outside_intersections']],
                  'anchor_readings':[{'target':p['declared_target'],'wall_gap':p['actual_outside_ray']['signed_anchor_gap_m'] if p['actual_outside_ray'] else None,
                                      'back_gap':p['actual_assembly_back_ray']['signed_back_face_to_anchor_m'] if p['actual_assembly_back_ray'] else None} for p in r['support_anchors']],
                  'mounts':[{'object':p['object'],'back_gap':p['actual_outside_ray']['signed_mount_back_gap_m'] if p['actual_outside_ray'] else None,'internal_contacts':len(p['internal_contacts'])} for p in r['physical_mount_checks']]} for r in results],
                  'service_hits':[(p['a'],p['b']) for p in service['branch_to_architecture']['intersections']],
                  'feed_gaps':[service['branch_to_station_endpoint_gap_m'],service['branch_to_loop_centerline_gap_m']]},indent=2))


