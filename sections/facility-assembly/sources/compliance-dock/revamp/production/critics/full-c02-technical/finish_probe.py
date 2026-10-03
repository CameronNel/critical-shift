"""Backing-gap and actually consumed fabric material inspection; no source save."""
import bpy, json, hashlib, importlib.util, math
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock')
OUT=R/'revamp/production/critics/full-c02-technical'
spec=importlib.util.spec_from_file_location('dock_geometry',str(R/'validate_dock.py'));vd=importlib.util.module_from_spec(spec);spec.loader.exec_module(vd)
bpy.ops.wm.open_mainfile(filepath=str(R/'module_overhaul_R1.blend'),load_ui=False)
scene=bpy.data.scenes.get('COMPLIANCE_EDIT_LOCAL') or bpy.context.scene;bpy.context.window.scene=scene;dep=bpy.context.evaluated_depsgraph_get()
prior=json.loads((OUT/'bearing-and-normals.json').read_text())
graphs={g['root']:g for g in prior['surface_connectivity']}
cache={}
def get(name):
    if name not in cache:cache[name]=vd.Shape(scene.objects[name],dep)
    return cache[name]
def bb_distance(a,b):return math.sqrt(sum(max(0,a[0][i]-b[1][i],b[0][i]-a[1][i])**2 for i in range(3)))
def closest(a,b):
    best=None
    for first,second in ((a,b),(b,a)):
        for p in first.vertices:
            q,n,i,d=second.bvh.find_nearest(p)
            if q is not None and (best is None or d<best[0]):best=(d,p,q,i,first,second)
    d,p,q,i,first,second=best
    _,_,j,_=first.bvh.find_nearest(p)
    return {'distance_m':float(d),'source_object':first.name,'source_point':vd.vec(p),'source_normal':vd.vec(first.normals[j]),
            'other_object':second.name,'other_point':vd.vec(q),'other_normal':vd.vec(second.normals[i]),'other_triangle':i}
names={'Cargo Inspection Conveyor':['Conveyor return belt'],
       'Person Scanner Arch':['Scanner column inset -1','Scanner column inset 1','Scanner status light 0','Scanner status light 1','Scanner status light 2','Scanner status light 3']}
rows=[]
for root,targets in names.items():
    g=graphs[root];isolated=set(g['disconnected_from_support_at_5mm_contact_allowance'])
    connected=[o.name for o in scene.objects if o.type in vd.GEOMETRY_TYPES and root in [p.name for p in vd.ancestors(o.parent)] and o.name not in isolated]
    for name in targets:
        a=get(name);ordered=sorted(connected,key=lambda n:bb_distance(a.bounds,get(n).bounds));nearest=[]
        for other in ordered:
            b=get(other)
            if len(nearest)>=5 and bb_distance(a.bounds,b.bounds)>nearest[-1]['distance_m']:continue
            nearest.append(closest(a,b));nearest.sort(key=lambda x:x['distance_m']);nearest=nearest[:5]
        direction=Vector((0,0,-1)) if root=='Cargo Inspection Conveyor' else Vector((0,1,0))
        centre=(Vector(a.bounds[0])+Vector(a.bounds[1]))*.5
        hits=[]
        for n in connected:
            b=get(n);hit=b.ray(centre-direction*.05,direction,1)
            if hit:hits.append({'object':n,'point':vd.vec(hit['point']),'normal':vd.vec(hit['normal']),
                                'signed_distance_from_component_centre_m':(hit['point']-centre).dot(direction)})
        containment=[]
        for other in ordered[:5]:
            b=get(other)
            containment.append({'object':other,'component_centre_inside_closed_mesh':b.contains(centre),
                                'component_sample_vertices_inside':sum(b.contains(p) for p in a.vertices[::max(1,len(a.vertices)//12)]),
                                'tested_vertex_count':len(a.vertices[::max(1,len(a.vertices)//12)])})
        rows.append({'object':name,'root':root,'nearest_connected_surfaces':nearest,'closed_surface_containment_screen':containment,'oriented_ray_direction':vd.vec(direction),
                     'ray_from_world':vd.vec(centre-direction*.05),'oriented_ray_hits':sorted(hits,key=lambda h:h['signed_distance_from_component_centre_m'])[:5]})
nodes=[];m=bpy.data.materials['CD | cotton']
for n in m.node_tree.nodes:
    inputs=[]
    for p in n.inputs:
        try:d=p.default_value;value=list(d) if hasattr(d,'__len__') and not isinstance(d,str) else d
        except:value=None
        inputs.append({'name':p.name,'default':value,'linked_from':[{'node':l.from_node.name,'socket':l.from_socket.name} for l in p.links]})
    nodes.append({'name':n.name,'type':n.type,'uv_map':getattr(n,'uv_map',None),'inputs':inputs})
result={'source_sha256':hashlib.sha256((R/'module_overhaul_R1.blend').read_bytes()).hexdigest(),
        'backing_gap_witnesses':rows,'actual_cotton_shader_nodes':nodes,'saved':False}
(OUT/'backing-and-consumed-fabric.json').write_text(json.dumps(result,indent=2)+'\n')
print('BACKING_GAPS',[(r['object'],r['nearest_connected_surfaces'][0]) for r in rows],flush=True)
print('FROZEN_SOURCE_RELEASED without save',flush=True)
