"""Native connected-island topology and real journal/bore witnesses."""
import argparse,hashlib,json,math,sys
from collections import defaultdict
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--expected-sha',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
native=Path(bpy.data.filepath);assert sha(native)==a.expected_sha
S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];deps=bpy.context.evaluated_depsgraph_get()
records=[];islands=[]
for obj in S.objects:
    ancestor=obj;focus=False
    while ancestor:
        focus=focus or ancestor.name in {'Arrival Gate P2','CD | Office key cabinet'};ancestor=ancestor.parent
    if not focus or obj.type!='MESH':continue
    ev=obj.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles()
    world=[obj.matrix_world@v.co for v in me.vertices];adj=[set() for _ in world]
    for e in me.edges:i,j=e.vertices;adj[i].add(j);adj[j].add(i)
    remaining=set(range(len(world)))
    while remaining:
        i=next(iter(remaining));component={i};remaining.remove(i);queue=[i]
        while queue:
            for j in adj[queue.pop()]:
                if j in remaining:remaining.remove(j);component.add(j);queue.append(j)
        indices=sorted(component);mapping={old:new for new,old in enumerate(indices)}
        vs=[world[i] for i in indices];fs=[[mapping[i] for i in f.vertices] for f in me.polygons if f.vertices[0] in component]
        edge_faces=defaultdict(list)
        for fi,f in enumerate(fs):
            for x,y in zip(f,f[1:]+f[:1]):edge_faces[tuple(sorted((x,y)))].append((fi,x,y))
        nonmanifold=sum(len(v)!=2 for v in edge_faces.values())
        same_direction=sum(len(v)==2 and v[0][1:]==v[1][1:] for v in edge_faces.values())
        bounds=[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]]
        center=sum(vs,Vector())/len(vs)
        volume=sum((world[t.vertices[0]]-center).dot((world[t.vertices[1]]-center).cross(world[t.vertices[2]]-center))/6 for t in me.loop_triangles if t.vertices[0] in component)
        rec={'object':obj.name,'index':len(islands),'bounds':bounds,'vertices':len(vs),'faces':len(fs),
             'nonmanifold_edges':nonmanifold,'same_direction_adjacent_faces':same_direction,'signed_volume_m3':volume}
        tree=BVHTree.FromPolygons(vs,fs,all_triangles=False)
        records.append(rec);islands.append((rec,tree,vs))
    ev.to_mesh_clear()
P2=[];cabinet=[]
for xx in [-1.75,-.65,.65,1.75]:
    selected={}
    for rec,tree,vs in islands:
        lo,hi=rec['bounds'];cx=(lo[0]+hi[0])/2
        if abs(cx-xx)>.0002:continue
        if abs(lo[2]-3.48)<.0002 and abs(hi[2]-3.579)<.0002:selected['hanger']=(rec,tree,vs)
        elif abs(lo[2]-3.52)<.0002 and abs(hi[2]-3.60)<.0002:selected['roller']=(rec,tree,vs)
        elif abs(lo[1]-15.842)<.0002 and abs(hi[1]-15.983)<.0002:selected['axle']=(rec,tree,vs)
        elif abs(lo[1]-15.970)<.0002 and abs(hi[1]-15.972)<.0002:selected['clip']=(rec,tree,vs)
    row={'x_m':xx,'selected_islands':{k:v[0] for k,v in selected.items()},'bore_samples':[]}
    assert set(selected)=={'hanger','roller','axle','clip'},'Required mechanical island not identified'
    for name,yy in [('hanger',15.86),('roller',15.94),('clip',15.971)]:
        rec,tree,vs=selected[name];gaps=[];missing=0
        for j in range(192):
            angle=2*math.pi*j/192;direction=Vector((math.sin(angle),0,math.cos(angle)))
            point=Vector((xx,yy,3.56));inner=tree.ray_cast(point,direction,.05)
            shaft=selected['axle'][1].ray_cast(point,direction,.05)
            # The clip has a deliberate assembly split; its empty angular
            # sector must be recorded, not treated as absent bore coverage.
            if inner[0] is None or shaft[0] is None:missing+=1;continue
            gaps.append(inner[3]-shaft[3])
        row['bore_samples'].append({'part':name,'y_m':yy,'sampled_directions':192,
            'missing_directions':missing,'minimum_gap_m':min(gaps),'maximum_gap_m':max(gaps),
            'positive_running_clearance':min(gaps)>0})
    row['head_to_hanger_front_gap_m']=selected['hanger'][0]['bounds'][0][1]-15.847
    row['roller_rear_to_clip_front_gap_m']=selected['clip'][0]['bounds'][0][1]-selected['roller'][0]['bounds'][1][1]
    P2.append(row)
for rec,tree,vs in islands:
    if rec['object']=='Office key box cabinet':shell=(rec,tree,vs)
    elif rec['object']=='Key box glass':glass=(rec,tree,vs)
    if rec['object'].startswith('CD | Joined CD | Office key cabinet / brass'):
        lo,hi=rec['bounds']
        cabinet.append({'island':rec['index'],'glass_rear_to_key_front_gap_m':lo[1]-9.475})
report={'native_sha256':a.expected_sha,'probe_sha256':sha(__file__),'islands':records,'P2_bearing_witnesses':P2,
        'key_glass_separation':cabinet,'interpretation':'All data comes from current evaluated connected islands. A spring split is intentional; all its cut ends still require closed topology.'}
assert sha(native)==a.expected_sha
(HERE/'mechanical-native.json').write_text(json.dumps(report,indent=2)+'\n')
print('MECHANICAL_NATIVE',json.dumps({'P2':P2,'key_glass_separation':cabinet}))
