"""Independent evaluated surface contact and stable-volume probe; no Blender writes."""
import bpy, json, hashlib, importlib.util, math, re
from pathlib import Path
from collections import defaultdict, deque
from mathutils import Vector

ROOT=Path('/workspace/critical-shift')
R=ROOT/'sections/facility-assembly/sources/compliance-dock'
OUT=R/'revamp/production/critics/full-c02-technical'
spec=importlib.util.spec_from_file_location('dock_geometry',str(R/'validate_dock.py'))
vd=importlib.util.module_from_spec(spec);spec.loader.exec_module(vd)
bpy.ops.wm.open_mainfile(filepath=str(R/'module_overhaul_R1.blend'),load_ui=False)
scene=bpy.data.scenes.get('COMPLIANCE_EDIT_LOCAL') or bpy.context.scene;bpy.context.window.scene=scene
dep=bpy.context.evaluated_depsgraph_get()
inventory=json.loads((OUT/'native-independent.json').read_text())
targets=set(inventory['summary']['negative_closed_volume_objects'])
roots={'G1 Cart Bypass Gate','Cargo Inspection Conveyor','Covered Trolley H1',
       'CD | Main ventilation supply trunk suspension','CD | Return ventilation trunk suspension','Person Scanner Arch'}
selected={o.name for o in scene.objects if o.type in vd.GEOMETRY_TYPES and
          (any(p.name in roots for p in vd.ancestors(o.parent)) or o.name in targets or o.name in {'Floor slab','Roof deck ceiling slab'})}
shapes={name:vd.Shape(scene.objects[name],dep) for name in selected}

def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def volume(shape,inds):
    refs={i for t in inds for i in shape.triangles[t]};centre=[sum(float(shape.vertices[i][k]) for i in refs)/len(refs) for k in range(3)]
    vol=0
    for i in inds:
        a,b,c=[tuple(float(shape.vertices[n][k])-centre[k] for k in range(3)) for n in shape.triangles[i]]
        vol+=dot(a,cross(b,c))/6
    return vol
normal_results=[]
for name in sorted(targets):
    s=shapes[name];adj=defaultdict(set);uses=defaultdict(list)
    for i,t in enumerate(s.triangles):
        for a,b in zip(t,t[1:]+t[:1]):uses[tuple(sorted((a,b)))].append(i)
    for rows in uses.values():
        for i in rows:adj[i].update(rows)
    unseen=set(range(len(s.triangles)));shells=[]
    while unseen:
        todo=[unseen.pop()];seen=set(todo)
        while todo:
            for i in adj[todo.pop()]:
                if i in unseen:unseen.remove(i);seen.add(i);todo.append(i)
        shell_verts={n for i in seen for n in s.triangles[i]}
        shell_edges=[rows for edge,rows in uses.items() if edge[0] in shell_verts]
        vol=volume(s,seen)
        centre=sum((s.vertices[n] for n in shell_verts),Vector())/len(shell_verts)
        witnesses=[]
        if vol<0:
            for i in sorted(seen)[:3]:
                pts=[s.vertices[k] for k in s.triangles[i]]
                witnesses.append({'triangle':i,'point':vd.vec(sum(pts,Vector())/3),'normal':vd.vec(s.normals[i])})
        shells.append({'triangles':len(seen),'closed':all(len(rows)==2 for rows in shell_edges),'stable_signed_volume_m3':vol,
                       'world_centre':vd.vec(centre),'negative_witnesses':witnesses})
    normal_results.append({'object':name,'stable_signed_volume_m3':volume(s,range(len(s.triangles))),'shells':shells})

def closest(a,b):
    """Actual evaluated triangle surfaces. Bounds only select pairs."""
    crossing=a.bvh.overlap(b.bvh)
    if crossing:
        i,j=crossing[0];pa=sum((a.vertices[k] for k in a.triangles[i]),Vector())/3
        pb,_,jb,d=b.bvh.find_nearest(pa)
        return {'triangle_crossings':len(crossing),'a_triangle':i,'b_triangle':j,'a_normal':vd.vec(a.normals[i]),'b_normal':vd.vec(b.normals[j]),
                'crossing_sample_centroid':vd.vec(pa),'nearest_b_to_centroid':vd.vec(pb),'surface_gap_m':0.0}
    best=None
    for first,second in ((a,b),(b,a)):
        for p in first.vertices:
            q,n,i,d=second.bvh.find_nearest(p)
            if q is not None and (best is None or d<best[0]):best=(d,p,q,i,first,second)
    d,p,q,i,first,second=best
    return {'surface_gap_m':float(d),'sample_object':first.name,'sample_point':vd.vec(p),'nearest_object':second.name,
            'nearest_point':vd.vec(q),'nearest_triangle':i,'nearest_normal':vd.vec(second.normals[i])}

graphs=[]
for rootname in sorted(roots):
    root=scene.objects[rootname];members=[s for s in shapes.values() if rootname in [p.name for p in vd.ancestors(s.obj.parent)]]
    support=shapes[root.get('support_target','Floor slab')];nodes=members+[support];edges=[];graph=defaultdict(set)
    for i,a in enumerate(nodes):
        for b in nodes[i+1:]:
            if not vd.overlaps(a.bounds,b.bounds,.005):continue
            w=closest(a,b)
            if w['surface_gap_m']<=.005001:
                edges.append({'a':a.name,'b':b.name,**w});graph[a.name].add(b.name);graph[b.name].add(a.name)
    connected={support.name};todo=[support.name]
    while todo:
        for n in graph[todo.pop()]:
            if n not in connected:connected.add(n);todo.append(n)
    isolated=[s.name for s in members if s.name not in connected]
    graphs.append({'root':rootname,'support':support.name,'tested_geometry_members':len(members),'actual_surface_connections':edges,
                   'disconnected_from_support_at_5mm_contact_allowance':isolated,
                   'method_limit':'Crossing/nearest surfaces form a geometric connectivity screen. Named oriented ray witnesses below determine bearings; no load capacity or moving mechanism engineering certification.'})

# Directed physical witnesses: point is on the source's real lower/back/contact surface.
requests=[
 ('conveyor motor to mounting plate','Drive motor housing','Drive motor mounting plate',(5.68,9.2,.535),(0,0,-1),.1),
 ('conveyor mounting plate to side frame','Drive motor mounting plate',None,(5.44,9.2,.52),(-1,0,0),.3),
 ('control panel underside to mount','Conveyor control panel',None,(3.42,7.65,.93),(0,0,-1),.5),
 ('gate motor into guide tower','G1 motor drive housing','G1 guide tower east',(3.02,6.9,1.85),(0,1,0),.3),
 ('gate pedestal head to column','G1 pedestal head','G1 pedestal column',(.65,6.75,1.0),(0,0,-1),.1),
 ('gate beam into east guide tower','G1 overhead slide beam','G1 guide tower east',(3.02,7.,1.62),(1,0,0),.2),
 ('gate beam into west latch post','G1 overhead slide beam','G1 latch post west',(.95,7.,1.62),(-1,0,0),.2),
 ('supply trunk suspension bearing','Main ventilation supply trunk','CD | Joined CD | Main ventilation supply trunk suspension / steel',(3.2,1.,4.175),(0,0,1),.3),
 ('return trunk suspension bearing','Return ventilation trunk','CD | Joined CD | Return ventilation trunk suspension / steel',(-3.8,1.,4.125),(0,0,1),.3),
 ('trolley drape on bed','Covered Trolley Draped Tarp','Trolley bed perimeter',(-6.20,12.20,.808),(0,0,-1),.4),
]
rows=[]
for label,source,target,point,direction,distance in requests:
    a=shapes[source];pt=Vector(point);di=Vector(direction).normalized()
    pa,na,ia,da=a.bvh.find_nearest(pt)
    candidates=[shapes[target]] if target else [s for s in shapes.values() if s.name!=source]
    hits=[]
    # Start 10 mm opposite to direction so the two real surfaces and normal are observable.
    for s in candidates:
        hit=s.ray(pt-di*.01,di,distance+.01)
        if hit:hits.append({'object':s.name,'point':vd.vec(hit['point']),'normal':vd.vec(hit['normal']),
                            'triangle':hit['face'],'signed_gap_from_witness_m':(hit['point']-pt).dot(di)})
    rows.append({'label':label,'source':source,'requested_target':target,'witness_world':list(point),'direction_world':list(direction),
                 'source_nearest_surface':{'point':vd.vec(pa),'triangle':ia,'normal':vd.vec(a.normals[ia]),'distance_from_witness_m':da},
                 'target_surface_hits':sorted(hits,key=lambda x:abs(x['signed_gap_from_witness_m']))[:6]})

# Straps: cross-sections sampled across each webbing, excluding buried end loops.
straps=[];tarp=shapes['Covered Trolley Draped Tarp']
for name in sorted(s for s in shapes if s.startswith('Trolley strap ')):
    s=shapes[name];samples=[]
    for x in [-6.1,-5.85,-5.6]:
        y=(s.bounds[0][1]+s.bounds[1][1])/2
        top=s.ray(Vector((x,y,1.3)),Vector((0,0,-1)),1)
        skin=tarp.ray(Vector((x,y,1.3)),Vector((0,0,-1)),1)
        if top and skin:samples.append({'world_x':x,'y':y,'strap_point':vd.vec(top['point']),'tarp_point':vd.vec(skin['point']),
                                        'strap_top_minus_tarp_m':top['point'].z-skin['point'].z,'strap_normal':vd.vec(top['normal']),'tarp_normal':vd.vec(skin['normal'])})
    straps.append({'object':name,'samples':samples})
result={'source_sha256':hashlib.sha256((R/'module_overhaul_R1.blend').read_bytes()).hexdigest(),'stable_normals':normal_results,
        'surface_connectivity':graphs,'oriented_bearing_witnesses':rows,'webbing_to_drape':straps,'saved':False}
(OUT/'bearing-and-normals.json').write_text(json.dumps(result,indent=2)+'\n')
print('STABLE_VOLUME',[(x['object'],x['stable_signed_volume_m3']) for x in normal_results],flush=True)
print('DISCONNECTED',[(g['root'],g['disconnected_from_support_at_5mm_contact_allowance']) for g in graphs],flush=True)
print('FROZEN_SOURCE_RELEASED without save',flush=True)
