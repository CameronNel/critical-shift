"""Independent read-only native evidence; never saves or mutates the .blend."""
import bpy, json, math, hashlib, importlib.util
from pathlib import Path
from collections import defaultdict, Counter
from mathutils import Vector

OUT=Path(__file__).parent
DOCK=OUT.parents[3]
PROD=OUT.parents[1]
REPO=DOCK.parents[3]
EXPECTED='dc608cae0a42303e614f2db3dc0cd9d50e4366dc738ac57c35957c6df34e0331'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(bpy.data.filepath)==EXPECTED
spec=importlib.util.spec_from_file_location('vd',DOCK/'validate_dock.py')
vd=importlib.util.module_from_spec(spec);spec.loader.exec_module(vd)
S=bpy.context.scene;D=bpy.context.evaluated_depsgraph_get()
assert S.name=='COMPLIANCE_EDIT_LOCAL'
shapes=[];byname={};counts=Counter();families=Counter();uvstats=Counter();bad=[];planes=defaultdict(list);exact=defaultdict(list)
for o in S.objects:
    if o.type not in vd.GEOMETRY_TYPES:continue
    a=vd.Shape(o,D);shapes.append(a);byname[o.name]=a
    ev=o.evaluated_get(D);me=ev.to_mesh();me.calc_loop_triangles()
    counts['geometry_objects']+=1;counts['triangles']+=len(me.loop_triangles)
    used=set(t.material_index for t in me.loop_triangles);counts['material_submeshes']+=len(used)
    for k in used:families[me.materials[k].name]+=1
    sources={}
    for k in used:
        m=me.materials[k]
        roots=[n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output]
        stack=list(roots);seen=set()
        while stack:
            n=stack.pop()
            if n.name in seen:continue
            seen.add(n.name)
            for pin in n.inputs:stack.extend(l.from_node for l in pin.links)
        sources[k]=[n for n in m.node_tree.nodes if n.name in seen and n.type=='UVMAP']
    for ti,t in enumerate(me.loop_triangles):
        p=[a.vertices[k] for k in t.vertices];cross=(p[1]-p[0]).cross(p[2]-p[0]);area=cross.length*.5
        if area<=1e-14:bad.append({'object':o.name,'triangle':ti,'area_m2':area})
        if area>1e-14:
            n=cross.normalized()
            if n.dot(a.normals[ti])<.999:bad.append({'object':o.name,'triangle':ti,'normal_dot':n.dot(a.normals[ti])})
            key=tuple(sorted(tuple(round(float(v),6) for v in q) for q in p))
            exact[key].append((o.name,ti,tuple(float(x) for x in n),area))
            axis=max(range(3),key=lambda k:abs(n[k]))
            if abs(n[axis])>.999999 and area>1e-7 and max(q[axis] for q in p)-min(q[axis] for q in p)<2e-6:
                other=[k for k in range(3) if k!=axis];q=[tuple(float(v[k]) for k in other) for v in p]
                planes[(axis,1 if n[axis]>0 else -1,round(sum(v[axis] for v in p)/3,5))].append((o.name,ti,q,area))
        for src in sources[t.material_index]:
            layer=me.uv_layers.get(src.uv_map)
            if layer is None:bad.append({'object':o.name,'triangle':ti,'missing_uv':src.uv_map});continue
            uv=[layer.data[k].uv.copy() for k in t.loops];uvstats['mapped_triangles']+=1
            ua=abs((uv[1].x-uv[0].x)*(uv[2].y-uv[0].y)-(uv[1].y-uv[0].y)*(uv[2].x-uv[0].x))*.5
            if ua<=0 and area>1e-14:bad.append({'object':o.name,'triangle':ti,'collapsed_uv':src.uv_map})
            for k in range(3):
                edge=(p[(k+1)%3]-p[k]).length
                if edge>.0001:
                    ratio=(uv[(k+1)%3]-uv[k]).length/edge;uvstats['measured_edges']+=1
                    if not math.isfinite(ratio) or abs(ratio-1)>.01:bad.append({'object':o.name,'triangle':ti,'uv_per_m':ratio})
    ev.to_mesh_clear()
BASE=json.loads((PROD/'baseline.json').read_text())
matrix_deltas=[]
for r in BASE['objects']:
    o=S.objects.get(r['name'])
    matrix_deltas.append({'object':r['name'],'missing':o is None,'max_delta':max(abs(o.matrix_world[i][j]-r['matrix'][i][j]) for i in range(4) for j in range(4)) if o else None})
protected=json.loads((PROD/'protected-inputs.json').read_text())
protected_report=[{'path':p,'expected':v,'actual':sha(REPO/p),'match':sha(REPO/p)==v} for p,v in protected.items()]
libraries=[]
for lib in bpy.data.libraries:
    # Blender normalizes all loaded Library.filepath values relative to the
    # currently opened source. lib.parent records link provenance, not a second
    # path base to apply to that normalized value.
    path=Path(bpy.path.abspath(lib.filepath));libraries.append({'stored_path':lib.filepath,'resolved':str(path),'exists':path.exists(),'sha256':sha(path) if path.exists() else None})
images=[{'name':im.name,'source':im.source,'filepath':im.filepath,'packed':bool(im.packed_file)} for im in bpy.data.images]
summary={'source':bpy.data.filepath,'source_sha256':EXPECTED,'blender':bpy.app.version_string,'scene':S.name,'scenes':[s.name for s in bpy.data.scenes],'counts':dict(counts),'local_material_families':dict(families),'uv_stats':dict(uvstats),'mesh_uv_bad':bad,'max_inherited_matrix_delta':max(r['max_delta'] for r in matrix_deltas if r['max_delta'] is not None),'missing_inherited':[r['object'] for r in matrix_deltas if r['missing']],'protected_inputs':protected_report,'libraries':libraries,'images':images,'linked_scene_reference_only':{'objects_in_local_scene':sum(bool(o.library) for o in S.objects)},'scene_units':{'system':S.unit_settings.system,'scale_length':S.unit_settings.scale_length},'render':{'engine':S.render.engine,'resolution_x':S.render.resolution_x,'resolution_y':S.render.resolution_y,'percentage':S.render.resolution_percentage},'native_not_saved':True}
(OUT/'native-independent.json').write_text(json.dumps(summary,indent=2))
print('INDEPENDENT_NATIVE',dict(counts),len(families),len(bad),flush=True)

def boxgap(a,b):return math.sqrt(sum(max(a.bounds[0][k]-b.bounds[1][k],b.bounds[0][k]-a.bounds[1][k],0)**2 for k in range(3)))
def pair(a,b):
    hits=a.bvh.overlap(b.bvh)
    best=1e30;witness=None
    for aa,bb in ((a,b),(b,a)):
        for p in aa.vertices:
            q,n,ti,d=bb.bvh.find_nearest(p)
            if d is not None and d<best:best=float(d);witness=[list(p),list(q)]
    # Exact contact proof for overlap and containment are kept distinct from
    # the vertex-to-triangle upper bound on the general surface minimum.
    a_inside=[list(p) for p in a.vertices if b.contains(p)][:3]
    b_inside=[list(p) for p in b.vertices if a.contains(p)][:3]
    return {'a':a.name,'b':b.name,'aabb_separation_lower_bound_m':boxgap(a,b),'vertex_triangle_distance_upper_bound_m':best,'nearest_witness':witness,'triangle_overlap_pairs':len(hits),'a_vertices_inside_b':a_inside,'b_vertices_inside_a':b_inside}

pairs=[('Drawer pull 0_0','Drawer face 0_0'),('Drawer cardholder 0_0','Drawer face 0_0'),('Transformer box 1','Utility backer panel'),('Transformer box 2','Utility backer panel'),('Main breaker disconnect','Utility backer panel'),('P2 blast leaf west','P2 frame jamb -1'),('P2 gate sign plate','P2 blast leaf west'),('P2 beacon base -1.5','North lintel P2'),('P2 security console','North wall east'),('G1 warning strobe beacon','G1 side pocket housing'),('Conveyor roller 0','Roller bearing cap 0_4.0'),('Conveyor roller 0','Roller bearing cap 0_5.3'),('Lifting eyebolt ring 4.05_6.65','Lifting eyebolt stem 4.05_6.65'),('Cargo crate base','Conveyor roller 0'),('Scanner column inset -1','Scanner portal column -1'),('Key box glass','Office key box cabinet')]
probe=[]
for a,b in pairs:
    if a in byname and b in byname:probe.append(pair(byname[a],byname[b]))
    else:probe.append({'a':a,'b':b,'missing':[n for n in (a,b) if n not in byname]})
# Search actual surrounding solids for the independently suspicious parts.
nearest=[]
for name in ['Transformer box 1','Main breaker disconnect','Drawer pull 0_0','Drawer cardholder 0_0','P2 beacon base -1.5','P2 gate sign plate','G1 warning strobe beacon','Drive motor mounting plate','Conveyor operator desk arm','Lifting eyebolt ring 4.05_6.65']:
    a=byname[name];candidates=sorted((b for b in shapes if b.name!=name and b.obj.type!='FONT'),key=lambda b:boxgap(a,b))[:16]
    nearest.append({'object':name,'surrounding_meshes':[pair(a,b) for b in candidates if boxgap(a,b)<.30]})
rays=[]
for label,origin,direction,distance in [('utilities_back',(6.760001,12.5,1.6),(1,0,0),.2),('drawer_mount',(-6.000001,8.194,.22),(-1,0,0),.1),('p2_beacon_back',(-1.5,15.770001,3.9),(0,1,0),.2),('p2_sign_back',(-1.5,15.710001,3.3),(0,1,0),.2),('cargo_crate_down',(4.65,5.5,.824999),(0,0,-1),.2)]:
    hit=vd.nearest_ray(shapes,Vector(origin),Vector(direction),distance)
    rays.append({'label':label,'origin':origin,'direction':direction,'hit':{'object':hit['shape'].name,'point':list(hit['point']),'normal':list(hit['normal']),'distance_m':hit['distance']} if hit else None})
(OUT/'contact-witnesses.json').write_text(json.dumps({'tolerance_gap_m':.005,'tolerance_penetration_m':.002,'pair_probes':probe,'surrounding_probes':nearest,'directional_rays':rays,'method_limits':'Surface upper bounds use sampled vertices against exact evaluated triangles. AABB separation is a strict lower bound; triangle overlap and closed-solid containment are engagement witnesses. All candidate solids are read from the native local scene; no root-anchor inference.'},indent=2))
print('CONTACT_WITNESSES_DONE',flush=True)

def clip(subject,clipper):
    area=lambda p:sum(p[i][0]*p[(i+1)%len(p)][1]-p[i][1]*p[(i+1)%len(p)][0] for i in range(len(p)))/2
    if area(clipper)<0:clipper=list(reversed(clipper))
    result=subject
    for i,a in enumerate(clipper):
        b=clipper[(i+1)%len(clipper)]
        cross=lambda p:(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
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
aggregates={};tested=0
for plane,items in planes.items():
    grid=defaultdict(list);seen=set()
    for i,item in enumerate(items):
        q=item[2];mi=[min(p[k] for p in q) for k in range(2)];ma=[max(p[k] for p in q) for k in range(2)]
        for x in range(math.floor(mi[0]*4),math.floor(ma[0]*4)+1):
            for y in range(math.floor(mi[1]*4),math.floor(ma[1]*4)+1):grid[x,y].append(i)
    for bucket in grid.values():
        for pos,i in enumerate(bucket):
            for j in bucket[pos+1:]:
                if (i,j) in seen:continue
                seen.add((i,j));a,b=items[i],items[j]
                if a[0]==b[0] and a[1]==b[1]:continue
                # Coarse boxes cull before polygon clipping.
                if any(max(p[k] for p in a[2])<min(p[k] for p in b[2])-1e-10 or max(p[k] for p in b[2])<min(p[k] for p in a[2])-1e-10 for k in range(2)):continue
                tested+=1;area,poly=clip(a[2],b[2])
                if area<1e-7:continue
                key=(tuple(sorted((a[0],b[0]))),plane)
                row=aggregates.setdefault(key,{'objects':key[0],'plane':plane,'overlap_area_m2':0.,'triangle_pair_count':0,'witnesses':[]})
                row['overlap_area_m2']+=area;row['triangle_pair_count']+=1
                if len(row['witnesses'])<3:
                    axis,sign,d=plane;other=[k for k in range(3) if k!=axis];center=[0.,0.,0.];center[axis]=d
                    center[other[0]]=sum(p[0] for p in poly)/len(poly);center[other[1]]=sum(p[1] for p in poly)/len(poly)
                    direction=Vector((0,0,0));direction[axis]=sign
                    hit=vd.nearest_ray(shapes,Vector(center)+direction*.00003,direction,.03,exclude=[a[0],b[0]])
                    row['witnesses'].append({'point':center,'triangles':[a[1],b[1]],'outward_occluder_within_30mm':hit['shape'].name if hit else None})
    if len(items)>1000:print('COPLANAR_PLANE',plane,len(items),len(aggregates),flush=True)
exactrows=[{'objects':list(dict.fromkeys(r[0] for r in rows)),'triangles':[{'object':r[0],'triangle':r[1],'normal':r[2],'area_m2':r[3]} for r in rows],'vertices':key} for key,rows in exact.items() if len(rows)>1]
(OUT/'coplanar-duplicates.json').write_text(json.dumps({'scope':'same-direction axis-planar overlap at 10 micrometre plane buckets, true polygon clipping above 1e-7 m2; exact world vertices rounded 1 micrometre for all orientations; 30 mm outward ray witness is local exposure evidence, not camera visibility','tested_triangle_pairs':tested,'axis_planar_overlap':sorted(aggregates.values(),key=lambda r:r['overlap_area_m2'],reverse=True),'exact_world_triangle_duplicates':exactrows},indent=2))
print('COPLANAR_DONE',len(aggregates),len(exactrows),flush=True)
assert sha(bpy.data.filepath)==EXPECTED
