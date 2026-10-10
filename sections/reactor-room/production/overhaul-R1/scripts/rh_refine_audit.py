"""Evidence checks for the hall candidate. Findings remain failures until fixed.
Run through rh_stage_runner.py -- rh_refine_audit.py CANDIDATE REPORT BASELINE.
This does not substitute for the independent visual review.
"""
import bpy, sys, json, math, hashlib, ast
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=sys.argv[sys.argv.index('--')+1:]
source,output,baseline=map(Path,A[:3])
def protected(o):
    return o.name.startswith(('CR ','CR_','COL ')) or any(c.name in
        ('31 CR CONTROL ROOM REDO','32 CR COLLISION','20 CONTROL MEZZANINE') for c in o.users_collection)
def material_state(m):
    if not m: return None
    nt=m.node_tree
    if not nt: return (m.name,list(m.diffuse_color))
    nodes=[]
    for n in sorted(nt.nodes,key=lambda n:n.name):
        sockets=[]
        for s in n.inputs:
            if not hasattr(s,'default_value'): continue
            v=s.default_value
            if isinstance(v,(str,int,float,bool)): value=v
            elif hasattr(v,'name'): value=v.name
            else:
                try: value=list(v)
                except TypeError: value=str(type(v))
            sockets.append((s.identifier,value))
        nodes.append((n.name,n.bl_idname,sockets))
    links=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in nt.links)
    drivers=[]
    if nt.animation_data:
        for f in nt.animation_data.drivers:
            drivers.append((f.data_path,f.array_index,f.driver.expression,
                [(v.name,v.type,[(t.id.name if t.id else None,t.data_path) for t in v.targets]) for v in f.driver.variables]))
    return (m.name,nodes,links,sorted(drivers))
def digest(o):
    vals=[o.name,o.type,o.parent.name if o.parent else None,list(o.matrix_world),
        [material_state(m) for m in getattr(o.data,'materials',[])]]
    if o.type=='MESH':
        vals.extend([[list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons]])
    return hashlib.sha256(repr(vals).encode()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(baseline)); bpy.context.scene.frame_set(1)
old={o.name:digest(o) for o in bpy.data.objects if protected(o)}
bpy.ops.wm.open_mainfile(filepath=str(source)); sc=bpy.context.scene; sc.frame_set(1)
dg=bpy.context.evaluated_depsgraph_get()
changed=[n for n,h in old.items() if n not in bpy.data.objects or digest(bpy.data.objects[n])!=h]
new_protected=[o.name for o in bpy.data.objects if protected(o) and o.name not in old]
records=[]
for o in bpy.data.objects:
    if protected(o): continue
    lettering=any(m and any(k in m.name.lower() for k in ('white','signal','legend','letter','paint')) for m in getattr(o.data,'materials',[]))
    legacy_gfx=o.type=='MESH' and o.name.startswith('R2 gfx')
    if o.type=='FONT' or legacy_gfx or (o.type=='MESH' and 'legend' in o.name.lower() and lettering):
        ev=o.evaluated_get(dg); mesh=ev.to_mesh(); mesh.calc_loop_triangles()
        normal=(o.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
        if legacy_gfx:
            # Converted legacy glyphs have world coordinates, including the
            # diagonal walls. A cardinal thin-axis guess loses their fronts.
            from r2lib import WALLS
            centre=sum((o.matrix_world@Vector(v) for v in o.bound_box),Vector())/8
            candidates=[]
            for w in WALLS:
                xy=Vector((centre.x,centre.y))-w.P
                u=xy.dot(w.t)
                if -.1<=u<=w.L+.1:candidates.append((abs(xy.dot(w.n)),w))
            wall=min(candidates,key=lambda x:x[0])[1]
            normal=Vector((wall.n.x,wall.n.y,0))
        if o.name=='Emergency cooling legend': normal=Vector((0,1,0))
        # Mesh legends sometimes retain world coordinates. Choose their visible
        # thin-axis front explicitly, rather than assuming a conversion matrix.
        if o.type=='MESH' and abs(normal.z)>.5:
            q=[o.matrix_world@Vector(v) for v in o.bound_box]
            spans=[max(v[i] for v in q)-min(v[i] for v in q) for i in range(3)]
            axis=min(range(3),key=spans.__getitem__)
            if axis<2:
                normal=Vector((0,0,0)); normal[axis]=-1 if sum(v[axis] for v in q)>0 else 1
        tris=[t for t in mesh.loop_triangles if (o.matrix_world.to_3x3()@t.normal).normalized().dot(normal)>.85]
        step=max(1,len(tris)//100)
        samples=[list(o.matrix_world@(sum((mesh.vertices[i].co for i in t.vertices),Vector())/3)) for t in tris[::step]]
        records.append(dict(name=o.name,body=o.data.body if o.type=='FONT' else o.name,normal=list(normal),samples=samples))
        ev.to_mesh_clear()
records.extend(json.loads(sc.get('rh_wall_text_records','[]')))
for o in bpy.data.objects:
    if o.type!='MESH' or not o.name.startswith('RH refine board ') or not o.name.endswith(' PANEL'): continue
    q=[o.matrix_world@Vector(v) for v in o.bound_box]
    centre=sum(q,Vector())/8
    n=Vector((-centre.x,-centre.y,0)).normalized()
    # These three boards occupy the straight north/east/west walls.
    axis=max(range(2),key=lambda i:abs(n[i]));n=Vector((0,0,0));n[axis]=-1 if centre[axis]>0 else 1
    horizontal=Vector((0,0,1)).cross(n)
    lo=min(p.dot(horizontal) for p in q);hi=max(p.dot(horizontal) for p in q)
    z0=min(p.z for p in q);z1=max(p.z for p in q);front=max(p.dot(n) for p in q)+.024
    samples=[list(horizontal*(lo+(hi-lo)*(i+.5)/9)+n*front+Vector((0,0,z0+(z1-z0)*(j+.5)/5))) for i in range(9) for j in range(5)]
    records.append(dict(name=o.name+' entire face',body='Board panel and indicators',normal=list(n),samples=samples))
# Generator lettering and its complete plate must clear the actual wall approach.
# A frontal-only check missed conduit parallax in main10.
generator_plate=bpy.data.objects['RH refine sign STANDBY GENERATOR PANEL']
generator_text=bpy.data.objects['RH refine STANDBY GENERATOR']
q=[generator_plate.matrix_world@v.co for v in generator_plate.data.vertices]
y0,y1=min(p.y for p in q),max(p.y for p in q)
z0,z1=min(p.z for p in q),max(p.z for p in q)
records.append(dict(name='RH refine STANDBY GENERATOR entire plate',body='Generator plaque whole face',normal=[1,0,0],samples=[[generator_text.location.x,y0+(y1-y0)*(i+.5)/17,z0+(z1-z0)*(j+.5)/5] for i in range(17) for j in range(5)]))
def transparent_object(o):
    if not o.data.materials: return False
    for m in o.data.materials:
        if not m or not m.use_nodes: return False
        out=next((n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output),None)
        if out and not out.inputs['Surface'].is_linked: continue
        b=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if b and (b.inputs['Alpha'].default_value<.3 or b.inputs['Transmission Weight'].default_value>.95): continue
        if any(n.type in ('BSDF_TRANSPARENT','BSDF_GLASS','BSDF_REFRACTION') for n in m.node_tree.nodes): continue
        return False
    return True
signs=[]
for r in records:
    n=Vector(r['normal']); blocked=[]; samples=r['samples']
    for p in samples:
        p=Vector(p); origin=p+n*1.20; remaining=1.205
        for _ in range(12):
            hit,loc,normal,idx,obj,mw=sc.ray_cast(dg,origin,-n,distance=remaining)
            if not hit or not transparent_object(obj): break
            remaining-=(origin-loc).length+.0001; origin=loc-n*.0001
            if remaining<=0: hit=False; break
        if hit and (loc-p).dot(n)>.003:
            blocked.append(dict(object=obj.name,point=list(p),depth=round((loc-p).dot(n),5)))
    signs.append(dict(name=r.get('name',r['body']),body=r['body'],samples=len(samples),
        blocked=len(blocked),occluders=blocked[:10],pass_check=bool(samples) and not blocked))
cameras=[]
for node in ast.parse(Path(__file__).with_name('render_detail_views.py').read_text()).body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('VIEWS','INSPECTION_VIEWS') for t in node.targets):
        cameras.extend(ast.literal_eval(node.value))
camera_signs=[]
for name,label,position,target,lens in cameras:
    if name=='37_generator_plaque':
        distance=(Vector(position)-Vector(target)).length
        target=tuple(generator_text.matrix_world.translation)
        position=tuple(Vector(target)+Vector((1,0,0))*distance)
    position=Vector(position);forward=(Vector(target)-position).normalized()
    right=forward.cross(Vector((0,0,1))).normalized();up=right.cross(forward)
    for r in records:
        n=Vector(r['normal']);in_frame=0;clear=0;blockers={}
        for point in r['samples']:
            p=Vector(point);delta=p-position;depth=delta.dot(forward)
            if depth<=0 or n.dot(-delta.normalized())<=.1: continue
            if abs(delta.dot(right))>depth*18/lens or abs(delta.dot(up))>depth*10.125/lens:continue
            in_frame+=1;direction=delta.normalized();origin=position;remaining=delta.length-.003
            for _ in range(24):
                hit,loc,normal,idx,obj,mw=sc.ray_cast(dg,origin,direction,distance=remaining)
                if not hit or not transparent_object(obj):break
                remaining-=(loc-origin).length+.0001;origin=loc+direction*.0001
                if remaining<=0:hit=False;break
            if hit:blockers[obj.name]=blockers.get(obj.name,0)+1
            else:clear+=1
        if in_frame:camera_signs.append(dict(camera=name,sign=r.get('name',r['body']),samples_in_frame=in_frame,clear=clear,occluders=blockers))
# Explicit contact anchors. These measure named targets, never a broad bbox.
contacts=[]; cache={}
def tree(o):
    if o.name not in cache:
        ev=o.evaluated_get(dg); mesh=ev.to_mesh()
        cache[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in mesh.vertices],
            [p.vertices[:] for p in mesh.polygons],all_triangles=False)
        ev.to_mesh_clear()
    return cache[o.name]
def contact(name,subject,target_prefix,p,d=(0,0,-1),gap=.005,penetration=.002,angle=12):
    targets=[o for o in bpy.data.objects if o.type=='MESH' and (o.name==target_prefix or o.name.startswith(target_prefix+' '))]
    prefixes=[subject] if isinstance(subject,str) else subject
    subjects=[o.name for o in bpy.data.objects if any(o.name.startswith(q) for q in prefixes)]
    p=Vector(p); d=Vector(d).normalized(); hits=[]
    for o in targets:
        loc,n,idx,dist=tree(o).ray_cast(p-d*.025,d,.10)
        if loc is not None: hits.append((dist-.025,math.degrees(math.acos(max(-1,min(1,n.dot(-d))))),o.name,list(loc)))
    hit=min(hits,key=lambda h:abs(h[0])) if hits else None
    subject_distances=[tree(bpy.data.objects[n]).find_nearest(p)[3] for n in subjects if bpy.data.objects[n].type=='MESH']
    surface_distance=min((v for v in subject_distances if v is not None),default=None)
    ok=bool(subjects and surface_distance is not None and surface_distance<=.0021 and hit and -penetration-1e-5<=hit[0]<=gap+1e-5 and hit[1]<=angle)
    contacts.append(dict(name=name,subjects=subjects,target=target_prefix,anchor=list(p),direction=list(d),
        max_gap=gap,max_penetration=penetration,max_angle=angle,subject_surface_distance=surface_distance,result=hit,pass_check=ok))
registry=json.loads(sc.get('rh_support_registry','[]'))
empty_registry=[r['id'] for r in registry if not r['anchors']]
for r in registry:
    for i,p in enumerate(r['anchors']):
        contact(r['id']+'-'+str(i),r['subject'],r['target'],p,r['direction'],r['gap'],r['penetration'],r['angle'])
for i,(x,y,z) in enumerate([(5.2,9.5,0),(5.9,9.9,0),(5.5,8.9,0),(-9.2,-7.1,0),(-8.5,-7.8,0),
    (-3.84,4.93,.135),(-3.14,4.93,.135),(-3.84,5.67,.135),(-3.14,5.67,.135),
    (6.52,-3.7,.135),(7.18,-3.7,.135),(6.52,-2.98,.135),(7.18,-2.98,.135)]):
    if any(r['owner']=='refinement props' and r['name'].startswith('drum ') for r in registry):continue
    subject='RH refine legacy drums' if i<5 else 'RH stations props'
    target='RH stations spill pallets' if z else 'R2 floor'
    if z:
        pallet_x=-3.49 if i<9 else 6.85
        bars=[pallet_x-.615+k*.1025 for k in range(13)]
        anchors=[(min(bars,key=lambda bx:abs(bx-(x+side*.18))),y,z) for side in (-1,1)]
    else: anchors=[(x+.20*math.cos(a),y+.20*math.sin(a),z) for a in (0,math.pi/2,math.pi,3*math.pi/2)]
    for j,p in enumerate(anchors): contact('drum-%02d-foot-%d'%(i+1,j),subject,target,p)
for x,y in ((-3.49,5.30),(6.85,-3.34)):
    for dx in (-1,1): contact('spill pallet foot','RH stations spill pallets','R2 floor',(x+dx*1.34*.37,y,0))
for x,y in ((-9.95,5.6),(-7.6,5.6)):
    for sx in (-1,1):
        for sy in (-1,1):contact('case foot','RH refine transport cases','R2 floor',(x+sx*.38,y+sy*.30,0))
for x in (1.8,3.3):
    for dy in (-.30,.30):contact('vessel seat to frame','RH refine vessel seat','RH stations south',(x,-9.65+dy,.52))
    contact('vessel bottom to seat','RH stations south','RH refine vessel seat',(x,-9.65,.60),penetration=.002)
for y in (.88,1.26):contact('gantry ladder floor','RH refine ladder feet','R2 floor',(7.17,y,0))
for y in (.88,1.26):
    contact('gantry ladder head tie','RH refine ladder head ties','RH pool platform STEEL',(7.006,y,13.82),(-1,0,0))
contact('gantry landing seam','RH refine ladder top step','RH pool platform TREAD',(7.,1.07,13.8575),(-1,0,0))
for x in (-10.,10.):
    for y in (4.25,4.95):contact('crane wheel rail','RH refine crane bridge running gear','R2 crane rails crane TRIM',(x,y,14.42))
if bpy.data.objects.get('RH refine main hook sheave IRON'):
    tx=bpy.data.objects['R2 crane trolley crane IRON'].matrix_world.translation.x
    c=Vector((tx+.30,4.40,10.405));n=(Vector((tx+.05,4.6,10.19))-c).normalized()
    # Sample the four lens seating quadrants, clear of the protective crossbars.
    u=n.cross(Vector((0,0,1))).normalized();v=n.cross(u)
    for a,b in ((-1,-1),(-1,1),(1,-1),(1,1)):
        contact('retained hook inspection lens mount '+str((a,b)),'R2 crane trolley crane LAMPA','R2 crane trolley crane IRON',c+n*.026+(u*a+v*b)*.018,-n)
required_sightlines=[('01_machinery_turbine_grid','ZONE C'),('02_machinery_coolant_eccs','ZONE A'),('02_machinery_coolant_eccs','R2 gfx DANGER AUTHORISED PERSONNEL ONLY'),('02_machinery_coolant_eccs','RH refine EMERGENCY COOLING'),('07_roof_crane','RH refine crane identity')]
required_sightlines += [(c,s) for c in ('02_machinery_coolant_eccs','06_control_rods_pool','10_walls_west_access','37_generator_plaque') for s in ('RH refine STANDBY GENERATOR','RH refine STANDBY GENERATOR entire plate')]
required_camera_records=[dict(camera=c,sign=s,records=[r for r in camera_signs if r['camera']==c and r['sign']==s]) for c,s in required_sightlines]
for row in required_camera_records:row['pass_check']=bool(row['records']) and all(r['clear']==r['samples_in_frame'] for r in row['records'])
zone_c_views=[r for r in camera_signs if r['camera']=='01_machinery_turbine_grid' and r['sign']=='ZONE C']
zone_c_pass=bool(zone_c_views) and all(r['clear']==r['samples_in_frame'] for r in zone_c_views)
report=dict(source=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    protected=dict(count=len(old),changed=changed,added=new_protected,pass_check=not changed and not new_protected),
    signage=dict(records=signs,failures=sum(not r['pass_check'] for r in signs)+sum(not r['pass_check'] for r in required_camera_records),
        zone_c_machinery_camera=dict(pass_check=zone_c_pass,records=zone_c_views),
        camera_visibility=camera_signs,
        required_camera_sightlines=required_camera_records,
        scope='Hall lettering and whole board faces, frontal obstruction plus all defined review camera sightlines. Camera obstruction is evidence for review, not an automatic global failure. Readability remains visual.'),
    support=dict(records=contacts,failures=sum(not r['pass_check'] for r in contacts),
        registered_assemblies=len(registry),
        covered_owners=sorted({r['owner'] for r in registry}),
        empty_registrations=empty_registry,
        scope='Sampled registered pipe supports, wall utilities, service fixtures, signage mounts, station equipment/props, floor bearings, roof bearings, pool rails/suspension, and refinement interfaces. Integral floor seats and finite assembly coverage also require the independent saved-scene inventory; this is not an exhaustive all-vertex or all-pair collision test.'))
output.write_text(json.dumps(report,indent=2)+'\n')
print('AUDIT',output,'sign failures',report['signage']['failures'],'contact failures',report['support']['failures'],
    'protected',report['protected']['pass_check'],flush=True)
