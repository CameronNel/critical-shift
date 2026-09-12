"""Independent support-neighborhood follow-up, unchanged frozen eng12."""
from pathlib import Path
import runpy,json,hashlib
HERE=Path(__file__).resolve().parent
c=runpy.run_path(str(HERE/'astra-eng12-mesh-core.py'))
globals().update({k:c[k] for k in ['bpy','Vector','Mesh','scene','ancestors','intersection','bounds','overlap_bounds','SAVED','EXPECTED']})
meshes={}
for o in scene.objects:
    if o.type not in {'MESH','CURVE'} or o.get('surface_decal'):continue
    if o.type=='CURVE' and o.data.bevel_depth==0:continue
    meshes[o.name]=Mesh(o)
out=[]
for name in ['Gate_crown_infill','Gate_crown_beam','Tray_penetration_lower_ledge']:
    a=meshes[name];neighbors=[]
    for b in meshes.values():
        if a==b or not overlap_bounds(a.bounds,b.bounds,pad=.04):continue
        hit=intersection(a,b)
        gaps=[max(0,a.bounds[0][i]-b.bounds[1][i],b.bounds[0][i]-a.bounds[1][i]) for i in range(3)]
        neighbors.append({'object':b.obj.name,'bounds_m':[list(p) for p in b.bounds],
                          'aabb_axis_gaps_m':gaps,'intersection':hit})
    out.append({'object':name,'bounds_m':[list(p) for p in a.bounds],
                'root_chain':[o.name for o in ancestors(a.obj)],'properties':{k:a.obj[k] for k in a.obj.keys()},
                'nearby_objects':neighbors})
root=scene.objects['Freight_gate_crown'];anchor=Vector(json.loads(root['support_anchors'])[0]);direction=Vector(root['support_direction']).normalized()
anchor_hits=[]
for m in meshes.values():
    if root in list(ancestors(m.obj)):continue
    p,n,t,d=m.bvh.ray_cast(anchor-direction*.1,direction,.5)
    if p is not None:anchor_hits.append({'object':m.obj.name,'point':list(p),'distance_m':d,'signed_anchor_gap_m':(p-anchor).dot(direction)})
root_info={'name':root.name,'properties':{k:root[k] for k in root.keys()},
           'anchor_ray':min(anchor_hits,key=lambda r:r['distance_m']) if anchor_hits else None}
root_info['anchor_surface_witnesses']=[]
for name in ['Gate_crown_beam','Ceiling_crossmember.010']:
    m=meshes[name];p,n,t,d=m.bvh.find_nearest(anchor)
    root_info['anchor_surface_witnesses'].append({'object':name,'nearest':list(p),'distance_m':d,'normal':list(n)})
report={'revision':'eng12','blend_sha256':EXPECTED,'objects':len(scene.objects),'crown_root':root_info,'crown_neighborhood':out,'saved':False,
        'limits':'Evaluated contacts and axis gaps within40mm AABB neighborhoods. Not structural analysis or load simulation.'}
assert hashlib.sha256(SAVED.read_bytes()).hexdigest()==EXPECTED
(HERE/'astra-eng12-crown-evidence.json').write_text(json.dumps(report,indent=2,default=lambda v:list(v)))
for r in out:print(r['object'],[(n['object'],n['aabb_axis_gaps_m'],bool(n['intersection'])) for n in r['nearby_objects']],flush=True)


