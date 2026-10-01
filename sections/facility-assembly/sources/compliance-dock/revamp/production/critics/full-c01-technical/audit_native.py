"""Fresh read-only f02 technical probe. Does not save, build or render."""
import bpy, json, math, hashlib, sys, importlib.util
from pathlib import Path
from collections import defaultdict, Counter
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT=Path(__file__).parent
ROOT=OUT.parents[3]
spec=importlib.util.spec_from_file_location('validator',ROOT/'validate_dock.py')
vd=importlib.util.module_from_spec(spec);spec.loader.exec_module(vd)
S=bpy.context.scene;D=bpy.context.evaluated_depsgraph_get()
assert S.name=='COMPLIANCE_EDIT_LOCAL'
expected='dc608cae0a42303e614f2db3dc0cd9d50e4366dc738ac57c35957c6df34e0331'
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==expected
BASE=json.loads((OUT.parents[1]/'baseline.json').read_text())
records=[];islands=[];shapes=[];byname={};metrics=[];tri_exact=defaultdict(list);planes=defaultdict(list)
material_use=Counter();mapping_use=Counter();submeshes=0
def finite(xs):return all(math.isfinite(float(x)) for x in xs)
def shader_sources(m):
    if not m.use_nodes:return []
    roots=[n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output]
    seen=set();stack=list(roots)
    while stack:
        n=stack.pop()
        if n.name in seen:continue
        seen.add(n.name)
        for i in n.inputs:
            stack.extend(l.from_node for l in i.links)
    return [n for n in m.node_tree.nodes if n.name in seen and n.type in {'UVMAP','TEX_COORD','GROUP'}]
def bounds(vs):return [[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]]
def bboxgap(a,b):return math.sqrt(sum(max(a[0][k]-b[1][k],b[0][k]-a[1][k],0)**2 for k in range(3)))
for index,o in enumerate(S.objects):
    if o.type not in vd.GEOMETRY_TYPES:continue
    shape=vd.Shape(o,D);shapes.append(shape);byname[o.name]=shape
    ev=o.evaluated_get(D);me=ev.to_mesh();me.calc_loop_triangles()
    vs=shape.vertices;ts=shape.triangles
    used={t.material_index for t in me.loop_triangles};submeshes+=len(used)
    for i in used:material_use[me.materials[i].name]+=1
    parent=list(range(len(vs)))
    def find(x):
        while x!=parent[x]:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(x,y):
        x,y=find(x),find(y)
        if x!=y:parent[y]=x
    for t in ts:union(t[0],t[1]);union(t[1],t[2])
    groups=defaultdict(list)
    for ti,t in enumerate(ts):groups[find(t[0])].append(ti)
    zeros=[];tiny=[];nonfinite=[];norms=[];uv_bad=[];uv_missing=[];uv_zero=[];edge_ratios=[];worldarea=0;chartarea=0
    sources={i:shader_sources(me.materials[i]) for i in used}
    for ti,t in enumerate(me.loop_triangles):
        p=[vs[i] for i in t.vertices];cross=(p[1]-p[0]).cross(p[2]-p[0]);area=cross.length*.5;worldarea+=area
        if area==0:zeros.append(ti)
        elif area<1e-14:tiny.append(ti)
        if not all(finite(v) for v in p):nonfinite.append(ti)
        if area>1e-14:
            n=cross.normalized();calc=shape.normals[ti]
            if n.dot(calc)<.999:norms.append({'triangle':ti,'dot':n.dot(calc)})
            key=tuple(sorted(tuple(round(float(x),6) for x in q) for q in p))
            tri_exact[key].append((o.name,ti,n.copy(),area))
            axis=max(range(3),key=lambda k:abs(n[k]))
            if abs(n[axis])>.999999:
                sign=1 if n[axis]>0 else -1;other=[k for k in range(3) if k!=axis]
                if max(q[axis] for q in p)-min(q[axis] for q in p)<.000002:
                    q=[(float(v[other[0]]),float(v[other[1]])) for v in p]
                    planes[(axis,sign,round(sum(v[axis] for v in p)/3,5))].append((o.name,ti,q,area))
        coords=[n for n in sources[t.material_index] if n.type=='UVMAP']
        if not coords:mapping_use['object' if any(n.type=='TEX_COORD' for n in sources[t.material_index]) else 'none']+=1
        for src in coords:
            mapping_use[src.uv_map]+=1
            layer=me.uv_layers.get(src.uv_map)
            if layer is None:uv_missing.append({'triangle':ti,'material':me.materials[t.material_index].name,'layer':src.uv_map});continue
            uv=[layer.data[i].uv.copy() for i in t.loops]
            if not all(finite(x) for x in uv):uv_bad.append({'triangle':ti,'nonfinite':True});continue
            ua=abs((uv[1].x-uv[0].x)*(uv[2].y-uv[0].y)-(uv[1].y-uv[0].y)*(uv[2].x-uv[0].x))*.5;chartarea+=ua
            if ua==0 and area>1e-14:uv_zero.append(ti)
            for k in range(3):
                length=(p[(k+1)%3]-p[k]).length
                if length>.0001:
                    ratio=(uv[(k+1)%3]-uv[k]).length/length;edge_ratios.append(ratio)
                    if abs(ratio-1)>.01 and len(uv_bad)<8:uv_bad.append({'triangle':ti,'edge_m':length,'uv_per_m':ratio})
    topology=[]
    for comp,tids in enumerate(groups.values()):
        vis=sorted({i for ti in tids for i in ts[ti]});renum={v:k for k,v in enumerate(vis)}
        vv=[vs[i] for i in vis];tt=[tuple(renum[i] for i in ts[ti]) for ti in tids]
        edges=defaultdict(list)
        for t in tt:
            for a,b in zip(t,t[1:]+t[:1]):edges[tuple(sorted((a,b)))].append((a,b))
        boundary=sum(len(v)==1 for v in edges.values());nonmanifold=sum(len(v)>2 for v in edges.values());wrong=sum(len(v)==2 and v[0]==v[1] for v in edges.values())
        closed=not boundary and not nonmanifold
        center=sum(vv,Vector())/len(vv);vol=sum((vv[t[0]]-center).dot((vv[t[1]]-center).cross(vv[t[2]]-center))/6 for t in tt)
        rec={'object':o.name,'island':comp,'vertices':len(vv),'triangles':len(tt),'bounds':bounds(vv),'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'inconsistent_oriented_edges':wrong,'closed':closed,'signed_volume_m3':vol if closed else None,'owner':shape.owner.name if shape.owner else None}
        topology.append(rec)
        island={'record':rec,'v':vv,'t':tt,'bvh':BVHTree.FromPolygons(vv,tt,all_triangles=True,epsilon=1e-7),'closed':closed,'obj':o,'index':len(islands)}
        islands.append(island)
    records.append({'object':o.name,'type':o.type,'triangles':len(ts),'islands':len(topology),'exact_zero_triangles':zeros,'tiny_area_triangles':tiny,'nonfinite_triangles':nonfinite,'geometric_normal_disagreements':norms[:8],'uv_missing':uv_missing[:8],'uv_errors':uv_bad,'uv_zero_triangles':uv_zero[:8],'metric_edge_ratio_range':[min(edge_ratios),max(edge_ratios)] if edge_ratios else None,'world_area_m2':worldarea,'chart_area_m2':chartarea,'open_islands':sum(not r['closed'] for r in topology),'negative_closed_islands':[r for r in topology if r['closed'] and r['signed_volume_m3']<-1e-12],'zero_volume_closed_islands':[r for r in topology if r['closed'] and abs(r['signed_volume_m3'])<1e-12]})
    ev.to_mesh_clear()
    if len(records)%200==0:print('EVALUATED',len(records),flush=True)
matrices=[];missing=[];dimchange=[];boundschange=[]
for r in BASE['objects']:
    o=S.objects.get(r['name'])
    if not o:missing.append(r['name']);continue
    delta=max(abs(float(o.matrix_world[i][j])-r['matrix'][i][j]) for i in range(4) for j in range(4))
    matrices.append({'object':o.name,'maximum_element_delta':delta})
    if o.name in byname:
        box=byname[o.name].bounds;old=r['bounds'];diff=max(abs(box[i][k]-old['min' if i==0 else 'max'][k]) for i in range(2) for k in range(3))
        if diff>.00001:boundschange.append({'object':o.name,'max_delta_m':diff,'old':[old['min'],old['max']],'new':box})
    d=max(abs(float(o.dimensions[k])-r['dimensions'][k]) for k in range(3))
    if d>.00001:dimchange.append({'object':o.name,'max_delta_m':d,'dimensions':list(o.dimensions),'old':r['dimensions']})
data={'source_sha256':expected,'scene':S.name,'objects':len(S.objects),'geometry_objects':len(records),'evaluated_triangles':sum(r['triangles'] for r in records),'used_material_submeshes':submeshes,'local_used_material_families':dict(material_use),'shader_mapping_triangle_counts':dict(mapping_use),'inherited_matrix_measurements':matrices,'missing_inherited':missing,'dimension_changes':dimchange,'evaluated_bound_changes':boundschange,'geometry':records,'topology_islands':[i['record'] for i in islands]}
(OUT/'native-mesh-uv.json').write_text(json.dumps(data,indent=2))
print('NATIVE_MESH_UV',len(records),len(islands),submeshes,len(material_use),flush=True)

# Internal load paths use narrow-phase actual triangle surfaces, not only root
# anchors or AABB contact. This reports component islands needing classification.
def surface_gap(a,b,limit=None):
    if a['bvh'].overlap(b['bvh']):return 0.,'triangle_intersection'
    best=1e30;witness=None
    for aa,bb in ((a,b),(b,a)):
        for p in aa['v']:
            q,n,ti,d=bb['bvh'].find_nearest(p)
            if d is not None and d<best:
                best=float(d);witness=[list(p),list(q)]
                if limit is not None and best<=limit:return best,'vertex_to_triangle'
    return best,witness
owners=defaultdict(list)
for island in islands:
    if island['record']['owner']:owners[island['record']['owner']].append(island)
loadpaths=[];all_edges=[]
for owner,parts in owners.items():
    root=S.objects[owner];target=byname[root['support_target']]
    connected=set();adj=defaultdict(list);seed=[]
    targetpart={'v':target.vertices,'t':target.triangles,'bvh':target.bvh}
    for a in parts:
        if bboxgap(a['record']['bounds'],target.bounds)>.005001:continue
        gap,how=surface_gap(a,targetpart,.005001)
        if gap<=.005001:connected.add(a['index']);seed.append({'island':a['index'],'object':a['record']['object'],'gap_m':gap})
    for i,a in enumerate(parts):
        for b in parts[i+1:]:
            if bboxgap(a['record']['bounds'],b['record']['bounds'])>.005001:continue
            gap,how=surface_gap(a,b,.005001)
            if gap<=.005001:
                adj[a['index']].append(b['index']);adj[b['index']].append(a['index'])
                all_edges.append({'a':a['index'],'b':b['index'],'gap_m':gap,'method':how if isinstance(how,str) else 'nearest_surface'})
    stack=list(connected)
    while stack:
        a=stack.pop()
        for b in adj[a]:
            if b not in connected:connected.add(b);stack.append(b)
    disconnected=[]
    for a in parts:
        if a['index'] in connected:continue
        nearest=None
        for b in parts:
            if b['index'] not in connected:continue
            lower=bboxgap(a['record']['bounds'],b['record']['bounds'])
            if nearest and lower>nearest['gap_m']:continue
            gap,witness=surface_gap(a,b)
            if nearest is None or gap<nearest['gap_m']:nearest={'object':b['record']['object'],'island':b['index'],'gap_m':gap,'witness':witness}
        disconnected.append({'island':a['index'],**a['record'],'nearest_connected':nearest})
    row={'assembly':owner,'target':target.name,'islands':len(parts),'supported_islands':len(connected),'seeds':seed,'disconnected':disconnected}
    loadpaths.append(row);print('LOADPATH',owner,len(parts),len(disconnected),flush=True)
    (OUT/'internal-load-paths.json').write_text(json.dumps({'tolerance_m':.005001,'assemblies':loadpaths,'contact_edges':all_edges},indent=2))

# Same-direction axis-planar triangle overlap independent of object topology.
def clip(subject,clipper):
    area=lambda p:sum(p[i][0]*p[(i+1)%len(p)][1]-p[i][1]*p[(i+1)%len(p)][0] for i in range(len(p)))/2
    if area(clipper)<0:clipper=list(reversed(clipper))
    result=subject
    for i,a in enumerate(clipper):
        b=clipper[(i+1)%len(clipper)]
        def cross(p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
        prev=result[-1] if result else None;pv=cross(prev) if prev else 0;new=[]
        for cur in result:
            cv=cross(cur)
            if (cv>=-1e-10)!=(pv>=-1e-10):
                t=pv/(pv-cv);new.append((prev[0]+t*(cur[0]-prev[0]),prev[1]+t*(cur[1]-prev[1])))
            if cv>=-1e-10:new.append(cur)
            prev,pv=cur,cv
        result=new
        if not result:return 0.,[]
    return abs(area(result)),result
coplanar=[];pairs=set()
for plane,items in planes.items():
    grid=defaultdict(list)
    for i,item in enumerate(items):
        q=item[2];mi=[min(p[k] for p in q) for k in range(2)];ma=[max(p[k] for p in q) for k in range(2)]
        for x in range(math.floor(mi[0]*2),math.floor(ma[0]*2)+1):
            for y in range(math.floor(mi[1]*2),math.floor(ma[1]*2)+1):grid[x,y].append(i)
    for bucket in grid.values():
        for pos,i in enumerate(bucket):
            for j in bucket[pos+1:]:
                key=(plane,i,j)
                if key in pairs:continue
                pairs.add(key);a,b=items[i],items[j]
                if a[0]==b[0] and a[1]==b[1]:continue
                area,poly=clip(a[2],b[2])
                if area<1e-7:continue
                axis,sign,d=plane;other=[k for k in range(3) if k!=axis];center=[0.,0.,0.];center[axis]=d
                center[other[0]]=sum(p[0] for p in poly)/len(poly);center[other[1]]=sum(p[1] for p in poly)/len(poly)
                direction=Vector((0,0,0));direction[axis]=sign
                hit=vd.nearest_ray(shapes,Vector(center)+direction*.00003,direction,.03,exclude=[a[0],b[0]])
                coplanar.append({'a':a[0],'a_triangle':a[1],'b':b[0],'b_triangle':b[1],'overlap_area_m2':area,'plane':plane,'witness_world':center,'outward_occluder_within_30mm':hit['shape'].name if hit else None})
    if len(items)>1000:print('PLANE',plane,len(items),len(coplanar),flush=True)
exact=[]
for key,rows in tri_exact.items():
    if len(rows)<2:continue
    exact.append({'triangles':[{'object':r[0],'triangle':r[1],'normal':list(r[2]),'area_m2':r[3]} for r in rows],'world_vertices':key})
(OUT/'coplanar-duplicates.json').write_text(json.dumps({'axis_planar_overlap':coplanar,'exact_world_triangle_duplicates':exact,'scope':'same-direction axis-planar triangles; non-axis exact duplicates; outward 30mm obstruction ray witness, not full visibility'},indent=2))
print('COPLANAR',len(coplanar),'EXACT',len(exact),flush=True)
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()==expected
