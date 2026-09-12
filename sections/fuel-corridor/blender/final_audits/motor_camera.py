"""Independent saved eng12 motor, lamp, seam and camera checks. No scene mutations."""
from pathlib import Path
import runpy,json,hashlib,math
HERE=Path(__file__).resolve().parent
c=runpy.run_path(str(HERE/'astra-eng12-mesh-core.py'))
globals().update({k:c[k] for k in ['bpy','Vector','Mesh','scene','ancestors','intersection','bounds','overlap_bounds','SAVED','EXPECTED']})
meshes={}
for o in scene.objects:
    if o.type not in {'MESH','CURVE'} or o.get('surface_decal'):continue
    if o.type=='CURVE' and o.data.bevel_depth==0:continue
    meshes[o.name]=Mesh(o)
print('EVALUATED',len(meshes),flush=True)

def nearest(a,b):
    best=None
    for source,target in [(a,b),(b,a)]:
        for p in source.points:
            q,n,i,d=target.bvh.find_nearest(p)
            if q is not None and (best is None or d<best['distance_m']):
                best={'distance_m':d,'source':source.obj.name,'target':target.obj.name,'point':list(p),'nearest':list(q)}
    return best

groups=[]
for name in ['Freight_gate_drive','Gate_motor_task_lamp']:
    root=scene.objects[name];inv=root.matrix_world.inverted()
    members=[m for m in meshes.values() if root in list(ancestors(m.obj))]
    whole=bounds([p for m in members for p in m.bounds])
    outside=[m for m in meshes.values() if root not in list(ancestors(m.obj)) and overlap_bounds(m.bounds,whole,pad=.003)]
    internal=[];external=[]
    for i,a in enumerate(members):
        for b in members[i+1:]:
            hit=intersection(a,b)
            if hit:internal.append({'a':a.obj.name,'b':b.obj.name,**hit})
        for b in outside:
            hit=intersection(a,b)
            if hit:external.append({'a':a.obj.name,'b':b.obj.name,**hit})
    rows=[]
    for a in members:
        local=bounds([inv@p for p in a.points]);close=[]
        for b in members:
            if a==b or not overlap_bounds(a.bounds,b.bounds,pad=.006):continue
            close.append(nearest(a,b))
        rows.append({'name':a.obj.name,'type':a.obj.type,'world_bounds_m':[list(p) for p in a.bounds],
                     'root_local_bounds_m':[list(p) for p in local],
                     'root_local_dimensions_m':list(local[1]-local[0]),'near_contacts':close})
    # Actual back faces to surrounding physical architecture, one ray through
    # each primary mounting center. Origins are offset in front of the object.
    mounts=[]
    for a in members:
        if a.obj.name not in ['Motor_vertical_mount','Motor_cable_clamp_back','Motor_task_back']:continue
        direction=root.matrix_world.to_3x3()@Vector((0,1,0));direction.normalize()
        depth=max(p.dot(direction) for p in a.points)
        pp=[p for p in a.points if depth-p.dot(direction)<1e-5]
        center=sum(pp,Vector())/len(pp);origin=center-direction*.1;hits=[]
        for b in outside:
            p,n,t,d=b.bvh.ray_cast(origin,direction,.5)
            if p is not None:hits.append({'object':b.obj.name,'point':list(p),'distance_m':d,'signed_back_gap_m':(p-center).dot(direction)})
        mounts.append({'object':a.obj.name,'back_center':list(center),'first_hit':min(hits,key=lambda h:h['distance_m']) if hits else None})
    groups.append({'name':name,'members':rows,'internal_intersections':internal,'outside_intersections':external,'mount_rays':mounts,'bounds_m':[list(p) for p in whole]})
    print('GROUP',name,'MEMBERS',len(members),'OUTSIDE',[(r['a'],r['b']) for r in external],flush=True)

# Dimensions use the root's actual evaluated coordinates, axial X and radial YZ.
root=scene.objects['Freight_gate_drive'];inv=root.matrix_world.inverted()
core=[m for n,m in meshes.items() if n=='Gate_motor' or n=='Motor_end_bell' or n.startswith('Motor_end_bell.')]
fins=[m for n,m in meshes.items() if n=='Motor_cooling_fin' or n.startswith('Motor_cooling_fin.')]
corepts=[inv@p for m in core for p in m.points];finpts=[inv@p for m in fins for p in m.points]
cb=bounds(corepts);fb=bounds(finpts)
axis_mid=(inv@(sum(meshes['Gate_motor'].points,Vector())/len(meshes['Gate_motor'].points)))
dimensions={'core_members':[m.obj.name for m in core],'core_bounds_root_m':[list(p) for p in cb],
            'axial_body_length_m':cb[1].x-cb[0].x,'endbells':[],
            'fin_count':len(fins),'fin_bounds_root_m':[list(p) for p in fb],
            'fin_y_span_m':fb[1].y-fb[0].y,'fin_z_span_m':fb[1].z-fb[0].z,
            'fin_max_radial_diameter_m':2*max(math.hypot(p.y-axis_mid.y,p.z-axis_mid.z) for p in finpts)}
for m in core:
    if m.obj.name=='Gate_motor':continue
    pp=[inv@p for p in m.points]
    dimensions['endbells'].append({'name':m.obj.name,'max_radial_diameter_m':2*max(math.hypot(p.y-axis_mid.y,p.z-axis_mid.z) for p in pp)})

seams=[m for n,m in meshes.items() if n.startswith('REACTOR_BOUNDARY_leaf_panel_seam')]
targets=[meshes[n] for n in ['REACTOR_BOUNDARY_leaf_identity_field','REACTOR_BOUNDARY_leaf_identity_field.001','REACTOR_BOUNDARY_leaf_stiffener.001','REACTOR_BOUNDARY_leaf_stiffener.008']]
seamcheck=[]
for a in seams:
    for b in targets:
        if not overlap_bounds(a.bounds,b.bounds,pad=.12):continue
        seamcheck.append({'seam':a.obj.name,'body':b.obj.name,'seam_z':list(p.z for p in a.bounds),
                          'body_z':list(p.z for p in b.bounds),'z_gap_m':a.bounds[0].z-b.bounds[1].z,
                          'intersection':intersection(a,b)})

deps=bpy.context.evaluated_depsgraph_get();cameras=[]
for cam in [o for o in scene.objects if o.type=='CAMERA']:
    corners=cam.data.view_frame(scene=scene);x0,x1=min(p.x for p in corners),max(p.x for p in corners)
    y0,y1=min(p.y for p in corners),max(p.y for p in corners);z=corners[0].z
    origin=cam.matrix_world.translation;near=[];hist={};center=None
    for j in range(17):
        for i in range(17):
            local=Vector((x0+(x1-x0)*(i+.5)/17,y0+(y1-y0)*(j+.5)/17,z)).normalized()
            direction=(cam.matrix_world.to_3x3()@local).normalized()
            hit,p,n,t,obj,mat=scene.ray_cast(deps,origin,direction,distance=30)
            if not hit:continue
            d=(p-origin).length;row={'grid':[i,j],'object':obj.name,'distance_m':d,'point':list(p)}
            hist[obj.name]=hist.get(obj.name,0)+1
            if d<.12:near.append(row)
            if i==8 and j==8:center=row
    cameras.append({'name':cam.name,'rays':289,'near_hits':near,'center_hit':center,'first_hit_histogram':hist})
hashes={n:hashlib.sha256((SAVED.parent/n).read_bytes()).hexdigest() for n in ['build.py','valorant_details.py','interface.json','build_manifest.json','handoff.json','Fuel_Corridor.blend']}
report={'revision':'final-F04','objects':len(scene.objects),'physical_meshes':len(meshes),'hashes':hashes,
        'scene_hashes':{k:scene.get(k) for k in ['source_sha256','detail_source_sha256','interface_sha256']},
        'groups':groups,'motor_dimensions':dimensions,'reactor_seam_replay':seamcheck,'camera_frustum_rays':cameras,
        'limits':['Closed saved geometry only; no motion or engine execution.','Nearest contact witnesses are vertex-to-surface and finite, not exact global closest distances.','Finite camera lattice cannot certify full-frame visibility or exposure.','Same-assembly intersections require mechanical interpretation.'],'saved':False,'rendered':False}
assert hashlib.sha256(SAVED.read_bytes()).hexdigest()==EXPECTED
(HERE.parents[1]/'production/evidence/final-pass/F04-motor-camera.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'dimensions':dimensions,'seam_hits':[(r['seam'],r['body']) for r in seamcheck if r['intersection']],
                  'camera_near':[(r['name'],len(r['near_hits'])) for r in cameras]},indent=2))



