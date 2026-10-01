"""Read-only fresh s07 critic measurements. Never saves source or renders."""
import bpy, bmesh, hashlib, importlib.util, json, math
from pathlib import Path
from collections import defaultdict
from mathutils import Vector

ROOT=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock')
OUT=ROOT/'revamp/production/critics/slice-s07-technical-probe.json'
spec=importlib.util.spec_from_file_location('dock_validator',ROOT/'validate_dock.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
scene=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
shapes={o.name:v.Shape(o,dg) for o in scene.objects if o.type in v.GEOMETRY_TYPES}
report={'source':bpy.data.filepath,'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'blender':bpy.app.version_string,'scene':scene.name,'revision':scene.get('revision'),'methods':{},'unverified':[]}
vec=lambda q:[float(x) for x in q]
baseline=json.loads((ROOT/'revamp/production/baseline.json').read_text())
base={o['name']:o for o in baseline['objects']}
changes=[];missing=[];max_delta=0
for name,rec in base.items():
    o=scene.objects.get(name)
    if o is None:missing.append(name);continue
    delta=max(abs(o.matrix_world[i][j]-rec['matrix'][i][j]) for i in range(4) for j in range(4));max_delta=max(max_delta,delta)
    if delta>1e-6:changes.append({'name':name,'max_matrix_delta':delta})
report['inherited_world_matrices']={'baseline_sha256':baseline['source_sha256'],'count':len(base),'missing':missing,'changes':changes,'max_delta':max_delta}
local=[o for o in scene.objects if o.type in v.GEOMETRY_TYPES]
report['inventory']={'object_count':len(scene.objects),'evaluated_triangles':sum(len(s.triangles) for s in shapes.values()),'evaluated_material_submeshes':0,'used_materials':sorted({m.name for o in local for m in o.data.materials if m})}
scope=[]
for o in local:
    if o.get('overhaul_surface') or o.name.startswith('CD |') or (o.parent and o.parent.name in {'D1 Staff Front Door','Checkin Counter Hatch'}):scope.append(o)
report['scope_inventory']=[]
uvrows=[];missing_uv=[];normalrows=[]
for o in scope:
    s=shapes[o.name]
    report['scope_inventory'].append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'bounds':s.bounds,'closed':s.closed,'triangles':len(s.triangles),'materials':[m.name if m else None for m in o.data.materials],'modifiers':[m.type for m in o.modifiers]})
    ev=o.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles()
    report['inventory']['evaluated_material_submeshes']+=len({p.material_index for p in me.polygons})
    layer=me.uv_layers.get('CD_Physical_1m')
    consumed=any(m and m.use_nodes and any(n.type=='UVMAP' and n.uv_map=='CD_Physical_1m' for n in m.node_tree.nodes) for m in me.materials)
    if consumed and layer is None:missing_uv.append({'object':o.name,'type':o.type,'available_uv_layers':[l.name for l in me.uv_layers]})
    if layer:
        ratios=[];slopes=[];degenerate=[];nonfinite=[];area_ratios=[];useful=[];violation_witnesses=[]
        for t in me.loop_triangles:
            pts=[o.matrix_world@me.vertices[i].co for i in t.vertices];uvs=[layer.data[i].uv.copy() for i in t.loops]
            ar=(pts[1]-pts[0]).cross(pts[2]-pts[0]).length*.5
            au=abs((uvs[1].x-uvs[0].x)*(uvs[2].y-uvs[0].y)-(uvs[1].y-uvs[0].y)*(uvs[2].x-uvs[0].x))*.5
            if not all(math.isfinite(x) for u in uvs for x in u):nonfinite.append(t.index)
            if ar>1e-11 and au<1e-12:degenerate.append(t.index)
            if ar>1e-11:area_ratios.append(au/ar)
            n=(pts[1]-pts[0]).cross(pts[2]-pts[0]).normalized()
            sloped=all(abs(abs(n[i])-1)>1e-5 for i in range(3))
            for i in range(3):
                dist=(pts[(i+1)%3]-pts[i]).length
                if dist>1e-8:
                    ratio=(uvs[(i+1)%3]-uvs[i]).length/dist;ratios.append(ratio)
                    if dist>.0001:
                        useful.append(ratio)
                        if abs(ratio-1)>.01 and len(violation_witnesses)<5:violation_witnesses.append({'triangle':t.index,'edge_length_m':dist,'uv_edge_length':(uvs[(i+1)%3]-uvs[i]).length,'ratio':ratio,'point_a':vec(pts[i]),'point_b':vec(pts[(i+1)%3]),'uv_a':vec(uvs[i]),'uv_b':vec(uvs[(i+1)%3])})
                    if sloped:slopes.append(ratio)
        uvrows.append({'object':o.name,'triangle_count':len(me.loop_triangles),'edge_ratio_min':min(ratios) if ratios else None,'edge_ratio_max':max(ratios) if ratios else None,'edges_above_100um_ratio_min':min(useful) if useful else None,'edges_above_100um_ratio_max':max(useful) if useful else None,'metric_violations_above_100um':violation_witnesses,'area_ratio_min':min(area_ratios) if area_ratios else None,'area_ratio_max':max(area_ratios) if area_ratios else None,'sloped_edge_count':len(slopes),'sloped_edge_ratio_min':min(slopes) if slopes else None,'sloped_edge_ratio_max':max(slopes) if slopes else None,'degenerate_uv_triangles':degenerate,'nonfinite_uv_triangles':nonfinite})
    bm=bmesh.new();bm.from_mesh(me)
    normalrows.append({'object':o.name,'closed':s.closed,'signed_volume_m3':bm.calc_volume(signed=True),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'negative_world_determinant':o.matrix_world.determinant()<0})
    bm.free();ev.to_mesh_clear()
report['uv']={'metric_rows':uvrows,'consumers_missing_named_layer':missing_uv,'method':'Evaluated triangle edges and areas: UV unit/world metre ratio. Includes triangulated sloped caps and actual applied bevels. Repeats/seams intentional.'}
report['normals']=normalrows

def near_pair(a,b):
    A=shapes[a];B=shapes[b];witness=[]
    for X,Y in [(A,B),(B,A)]:
        for p in X.vertices:
            q,n,f,d=Y.bvh.find_nearest(p)
            if q is not None:witness.append((d,X.name,Y.name,p,q,f))
        for t in X.triangles:
            p=sum((X.vertices[i] for i in t),Vector())/3
            q,n,f,d=Y.bvh.find_nearest(p)
            if q is not None:witness.append((d,X.name,Y.name,p,q,f))
    d,x,y,p,q,f=min(witness,key=lambda k:k[0]);overlap=A.bvh.overlap(B.bvh)
    return {'a':a,'b':b,'surface_distance_upper_bound_m':d,'witness_from':x,'witness_to':y,'point_a':vec(p),'point_b':vec(q),'target_triangle':f,'intersecting_triangle_pairs':len(overlap),'method':'Actual evaluated vertex and triangle-centroid nearest surface witnesses plus BVH triangle intersections; distance is upper bound, not bounding-box inference.'}

pairs=[
('Hatch speaking aperture plate','CD | Speaking glazing clamp'),('Hatch speaking aperture plate','CD | Speaking glazing clamp.001'),
('Speaking baffle ring','CD | Speaking grille isolation pad'),('CD | Speaking grille isolation pad','Hatch speaking aperture plate'),
('CD | Speaking glazing clamp','CD | Speaking load-bearing stanchion'),('CD | Speaking glazing clamp.001','CD | Speaking load-bearing stanchion.001'),
('CD | Speaking load-bearing stanchion','CD | Speaking stanchion foot'),('CD | Speaking load-bearing stanchion.001','CD | Speaking stanchion foot.001'),
('CD | Speaking stanchion foot','CD | Counter linoleum inset'),('CD | Speaking stanchion foot.001','CD | Counter linoleum inset'),
('Transaction counter slab','Hatch counter leg west'),('Transaction counter slab','Hatch counter leg east'),('Transaction counter slab','CD | Counter gusset'),('CD | Counter gusset','Hatch wall sill base'),('Hatch counter leg west','Floor slab'),
('CD | Counter linoleum inset','Transaction counter slab'),('CD | Molded stamping pad','CD | Counter linoleum inset'),
('Authority stamp rubber base','CD | Molded stamping pad'),('Ink pad tin base','CD | Molded stamping pad'),('Ink pad felt cushion','Ink pad tin base'),('Ink pad lid open','CD | Ink pad pin hinge'),('Ink pad lid open','CD | Ink pad pin hinge.001'),('CD | Ink pad pin hinge','Ink pad tin base'),
('CD | Used cotton wipe','CD | Folded wipe lower ply'),('CD | Folded wipe lower ply','CD | Counter linoleum inset'),
('D1 keycard reader','Office front wall mid'),('CD | Reader molded face','D1 keycard reader'),('CD | D1 service mounting back','Office front wall mid'),('CD | Door armored conduit','CD | D1 service mounting back'),('CD | Door armored conduit','D1 keycard reader'),
('CD | Service saddle fixing','CD | Door armored conduit'),('CD | Service saddle fixing','Office front wall mid'),
('CD | Task wall bracket','Office front head lintel'),('CD | Task wall bracket','CD | Task folded shade'),('CD | Task frosted lens','CD | Task folded shade'),
('CD | D1 captive hinge','D1 door leaf'),('CD | D1 captive hinge','D1 frame jamb -1'),('CD | D1 hinge strap','D1 door leaf'),('CD | D1 hinge strap','CD | D1 captive hinge'),
('Authority stamp brass collar','Authority stamp rubber base'),('Authority stamp ferrule','Authority stamp brass collar'),('Authority stamp wood shaft','Authority stamp ferrule'),('Authority stamp wood knob','Authority stamp wood shaft'),
('CD | Door armored conduit','CD | D1 service lid'),('CD | Door armored conduit','CD | D1 service lid recessed stamping')
]
report['load_path_pairs']=[near_pair(a,b) if a in shapes and b in shapes else {'a':a,'b':b,'missing':[n for n in [a,b] if n not in shapes]} for a,b in pairs]
report['counter_lip_scars']=[near_pair(o.name,'Transaction counter slab') for o in scope if o.name.startswith('CD | Counter lip rubbed spot')]

def ray_at(target,point,direction):
    d=Vector(direction).normalized();p=Vector(point);h=shapes[target].ray(p-d*.04,d,.12)
    return {'target':target,'requested_surface_point':point,'direction':direction,'hit':{'point':vec(h['point']),'normal':vec(h['normal']),'signed_gap_m':h['distance']-.04,'triangle':h['face']} if h else None}
report['bearing_rays']=[ray_at('CD | Counter linoleum inset',[-2.915,3.43,1.042],[0,0,-1]),ray_at('CD | Molded stamping pad',[-2.95,3.43,1.048],[0,0,-1]),ray_at('CD | Molded stamping pad',[-2.8,3.42,1.048],[0,0,-1]),ray_at('Ink pad tin base',[-2.8,3.42,1.0695],[0,0,-1]),ray_at('CD | Folded wipe lower ply',[-4.11,3.39,1.044],[0,0,-1]),ray_at('CD | Counter linoleum inset',[-4.11,3.39,1.042],[0,0,-1])]

# Exact planar, partial same-facing overlaps with actual triangle clipping.
def clip(poly,tri):
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    orient=1 if cross(tri[0],tri[1],tri[2])>=0 else -1
    for a,b in zip(tri,tri[1:]+tri[:1]):
        new=[]
        for p,q in zip(poly,poly[1:]+poly[:1]):
            fp=orient*cross(a,b,p);fq=orient*cross(a,b,q);inp=fp>=-1e-10;inq=fq>=-1e-10
            if inp:new.append(p)
            if inp!=inq:
                t=fp/(fp-fq);new.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
        poly=new
        if not poly:break
    return poly
planes=defaultdict(list)
for o in scope:
    if o.type=='FONT':continue
    s=shapes[o.name]
    for ti,t in enumerate(s.triangles):
        P=[s.vertices[i] for i in t];n=(P[1]-P[0]).cross(P[2]-P[0]);area=n.length*.5
        if area<1e-10:continue
        n.normalize();d=n.dot(P[0]);axis=max(range(3),key=lambda i:abs(n[i]));other=[i for i in range(3) if i!=axis]
        key=tuple(round(n[i],5) for i in range(3))+(round(d,5),)
        planes[key].append((o.name,ti,P,n,axis,other))
overlaps=defaultdict(lambda:{'area_m2':0,'triangle_pairs':0,'witnesses':[]})
for group in planes.values():
    for i,A in enumerate(group):
        for B in group[i+1:]:
            if A[0]==B[0]:continue
            if abs(A[3].dot(A[2][0]-B[2][0]))>2e-6:continue
            other=A[5];pa=[tuple(p[k] for k in other) for p in A[2]];pb=[tuple(p[k] for k in other) for p in B[2]]
            if any(max(p[j] for p in pa)<min(p[j] for p in pb)-1e-9 or max(p[j] for p in pb)<min(p[j] for p in pa)-1e-9 for j in range(2)):continue
            poly=clip(pa,pb)
            if len(poly)<3:continue
            area=abs(sum(p[0]*q[1]-p[1]*q[0] for p,q in zip(poly,poly[1:]+poly[:1])))*.5/abs(A[3][A[4]])
            if area<1e-9:continue
            row=overlaps[tuple(sorted((A[0],B[0])))];row['area_m2']+=area;row['triangle_pairs']+=1
            if len(row['witnesses'])<3:
                c=[sum(p[j] for p in poly)/len(poly) for j in range(2)];q=Vector();q[other[0]]=c[0];q[other[1]]=c[1];q[A[4]]=(A[3].dot(A[2][0])-sum(A[3][k]*q[k] for k in other))/A[3][A[4]]
                hit=v.nearest_ray(list(shapes.values()),q+A[3]*.00001,A[3],.10,exclude=(A[0],B[0]))
                row['witnesses'].append({'point':vec(q),'normal':vec(A[3]),'face_a':A[1],'face_b':B[1],'cover_within_100mm':hit['shape'].name if hit else None,'cover_distance_m':hit['distance'] if hit else None})
report['partial_same_facing_coplanar_faces']=[{'objects':list(k),**r} for k,r in sorted(overlaps.items(),key=lambda k:-k[1]['area_m2'])]
report['methods']['partial_coplanar']='Actual evaluated triangle normals/planes, 2D polygon clipping for positive overlap area, then outward surface rays. Covers scoped geometry only. Different planes and general edge crossings are outside this coplanarity test.'

# Measure architectural envelope and portal side/head landmarks, then cold-load protected original to compare.
names=[o.name for o in scene.objects if o.get('support_class')=='architectural' and o.type in v.GEOMETRY_TYPES]
report['architecture_current']={'names':names,'union_bounds':v.bounds([p for n in names for p in shapes[n].vertices])}
office_names=[n for n in names if n.startswith('Office front') or n=='Hatch wall sill base']
office_names+=['D1 frame jamb -1','D1 frame jamb 1','D1 frame head','CD | D1 transom closure']
samples=[]
for z in [.3,1.5,2.34,2.36,2.8,3.0]:
    for x in [-6.7,-6.03,-6.00,-5.95,-4.80,-4.76,-4.7,-4.43,-4.3,-2.8,-2.45]:
        p=Vector((x,3.2,z));h=v.nearest_ray([shapes[n] for n in office_names],p,Vector((0,1,0)),1)
        samples.append({'point':vec(p),'front_y':float(h['point'].y) if h else None,'object':h['shape'].name if h else None})
report['office_front_current_samples']=samples
currentmat={o.name:[list(r) for r in o.matrix_world] for o in scene.objects if o.name in base}
currentarch={n:shapes[n].bounds for n in names}
def geom_hash(s):return hashlib.sha256(json.dumps({'vertices':[[round(x,5) for x in p] for p in s.vertices],'triangles':s.triangles},separators=(',',':')).encode()).hexdigest()
currentgeometry={n:geom_hash(s) for n,s in shapes.items() if n in base}
# Required portal geometry was preserved by exact original matrix/geometry comparisons
# outside repair names; measure wall rays to substantiate the repaired D1 pocket.
landmarks=[]
for x,z,dir in [(-5.4,1.5,(-1,0,0)),(-5.4,1.5,(1,0,0)),(-5.4,2.0,(0,0,1)),(-3.51,1.5,(-1,0,0)),(-3.51,1.5,(1,0,0)),(-3.51,1.5,(0,0,1)),(-3.51,1.5,(0,0,-1))]:
    h=v.nearest_ray([shapes[n] for n in office_names],Vector((x,3.6,z)),Vector(dir),5)
    landmarks.append({'origin':[x,3.6,z],'direction':dir,'hit':vec(h['point']) if h else None,'object':h['shape'].name if h else None})
report['repaired_architecture_current_landmarks']=landmarks
report['libraries']=[{'filepath':l.filepath,'relative':l.filepath.startswith('//'),'parent':l.parent.filepath if l.parent else None,'resolved':bpy.path.abspath(l.filepath),'exists':Path(bpy.path.abspath(l.filepath)).is_file()} for l in bpy.data.libraries]
report['unverified']=['Surface contacts do not establish engineering strength, mass distribution or moving hinge swept collision.','Scoped coplanar detection is not a complete arbitrary self-intersection audit.','Local slice review does not approve full-room art, all routes, restroom or runtime integration.']
OUT.write_text(json.dumps(report,indent=2,allow_nan=False));print('CURRENT_PROBE_WRITTEN',OUT,flush=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'module.blend'),load_ui=False)
oldscene=bpy.context.scene;olddg=bpy.context.evaluated_depsgraph_get();oldshapes={o.name:v.Shape(o,olddg) for o in oldscene.objects if o.type in v.GEOMETRY_TYPES}
oldarch=[o.name for o in oldscene.objects if o.get('support_class')=='architectural' and o.type in v.GEOMETRY_TYPES]
report['architecture_original']={'union_bounds':v.bounds([p for n in oldarch for p in oldshapes[n].vertices]),'count':len(oldarch)}
matrixchanges=[];dimchanges=[];geometrychanges=[]
for o in oldscene.objects:
    if o.name not in currentmat:continue
    d=max(abs(o.matrix_world[i][j]-currentmat[o.name][i][j]) for i in range(4) for j in range(4))
    if d>1e-6:matrixchanges.append({'name':o.name,'max_delta':d})
    if o.name in currentarch:
        dif=max(abs(currentarch[o.name][j][i]-oldshapes[o.name].bounds[j][i]) for j in range(2) for i in range(3))
        if dif>1e-5:dimchanges.append({'name':o.name,'max_bound_delta':dif,'old':oldshapes[o.name].bounds,'current':currentarch[o.name]})
oldoffice=[n for n in oldarch if n.startswith('Office front') or n=='Hatch wall sill base']
oldoffice+=['D1 frame jamb -1','D1 frame jamb 1','D1 frame head']
oldsamples=[]
for row in samples:
    h=v.nearest_ray([oldshapes[n] for n in oldoffice],Vector(row['point']),Vector((0,1,0)),1)
    oldy=float(h['point'].y) if h else None
    oldsamples.append({'point':row['point'],'old_front_y':oldy,'current_front_y':row['front_y'],'delta':row['front_y']-oldy if row['front_y'] is not None and oldy is not None else None,'old_object':h['shape'].name if h else None,'current_object':row['object']})
oldlandmarks=[]
for row in landmarks:
    h=v.nearest_ray([oldshapes[n] for n in oldoffice],Vector(row['origin']),Vector(row['direction']),5)
    oldlandmarks.append({'origin':row['origin'],'direction':row['direction'],'original_hit':vec(h['point']) if h else None,'current_hit':row['hit'],'original_object':h['shape'].name if h else None,'current_object':row['object']})
changedgeometry=[n for n,s in oldshapes.items() if n in currentgeometry and currentgeometry[n]!=geom_hash(s)]
report['direct_original_comparison']={'source_sha256':hashlib.sha256((ROOT/'module.blend').read_bytes()).hexdigest(),'matrix_changes':matrixchanges,'inherited_geometry_fingerprint_changes':changedgeometry,'geometry_method':'Ordered evaluated world vertices rounded to 10um plus ordered triangles; fingerprint differences can include numeric reorder and are not automatically geometric defects.','architectural_bound_changes':dimchanges,'office_front_samples':oldsamples,'office_aperture_landmarks':oldlandmarks}
OUT.write_text(json.dumps(report,indent=2,allow_nan=False));print('FINAL_PROBE_WRITTEN',OUT,flush=True)
