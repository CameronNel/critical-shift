import bpy, json, importlib.util, hashlib, math
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
ROOT=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock')
spec=importlib.util.spec_from_file_location('dock_v',ROOT/'validate_dock.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
dg=bpy.context.evaluated_depsgraph_get();scene=bpy.context.scene
names=[o.name for o in scene.objects if o.type in v.GEOMETRY_TYPES and (o.get('overhaul_surface') or o.name.startswith('CD |') or o.name=='Floor slab')]
S={n:v.Shape(scene.objects[n],dg) for n in names}
R={'source_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'source_saved':False,'reader_seating':[],'coplanar_plane_witnesses':[],'zero_area_triangles':[],'bearing_penetration_rays':[]}
for x,z in [(-4.70,1.25),(-4.67,1.30),(-4.73,1.19)]:
    p=Vector((x,3.54,z));h=S['Office front wall mid'].ray(p-Vector((0,.04,0)),Vector((0,1,0)),.08)
    R['reader_seating'].append({'reader_back_point':list(p),'wall_hit':list(h['point']) if h else None,'signed_gap_m':h['distance']-.04 if h else None,'wall_front_normal':list(h['normal']) if h else None,'reader_back_to_wall_penetration_m':.04-h['distance'] if h else None})
# Face witnesses are taken per actual plane, not combined across six box faces.
def clip(poly,tri):
    def c(a,b,p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
    o=1 if c(tri[0],tri[1],tri[2])>=0 else -1
    for a,b in zip(tri,tri[1:]+tri[:1]):
        new=[]
        for p,q in zip(poly,poly[1:]+poly[:1]):
            fp=o*c(a,b,p);fq=o*c(a,b,q);inside=fp>=-1e-10
            if inside:new.append(p)
            if inside!=(fq>=-1e-10):
                t=fp/(fp-fq);new.append(tuple(p[k]+t*(q[k]-p[k]) for k in range(2)))
        poly=new
        if not poly:break
    return poly
for a,b in [('Hatch counter leg west','Hatch wall sill base'),('Hatch counter leg east','Hatch wall sill base'),('Office front dado west','Office front wainscot west'),('Office front dado mid','Office front wainscot mid'),('CD | Counter lip rubbed spot','CD | Counter lip rubbed spot.001'),('CD | Counter lip rubbed spot.001','CD | Counter lip rubbed spot.002')]:
    A=S[a];B=S[b];rows=defaultdict(lambda:{'area_m2':0,'witness':None})
    for ia,ta in enumerate(A.triangles):
        pa=[A.vertices[i] for i in ta];na=(pa[1]-pa[0]).cross(pa[2]-pa[0]);aa=na.length*.5
        if aa<1e-10:continue
        na.normalize();axis=max(range(3),key=lambda i:abs(na[i]));other=[i for i in range(3) if i!=axis]
        for ib,tb in enumerate(B.triangles):
            pb=[B.vertices[i] for i in tb];nb=(pb[1]-pb[0]).cross(pb[2]-pb[0]);ba=nb.length*.5
            if ba<1e-10:continue
            nb.normalize()
            if na.dot(nb)<.999999 or abs(na.dot(pa[0]-pb[0]))>1e-6:continue
            p2=[tuple(p[k] for k in other) for p in pa];q2=[tuple(p[k] for k in other) for p in pb]
            if any(max(p[j] for p in p2)<min(p[j] for p in q2)-1e-9 or max(p[j] for p in q2)<min(p[j] for p in p2)-1e-9 for j in range(2)):continue
            poly=clip(p2,q2)
            if len(poly)<3:continue
            ar=abs(sum(p[0]*q[1]-p[1]*q[0] for p,q in zip(poly,poly[1:]+poly[:1])))*.5/abs(na[axis])
            if ar<1e-9:continue
            key=tuple(round(x,5) for x in na)+(round(na.dot(pa[0]),5),);row=rows[key];row['area_m2']+=ar
            if row['witness'] is None:
                q=Vector();q[other[0]]=sum(p[0] for p in poly)/len(poly);q[other[1]]=sum(p[1] for p in poly)/len(poly);q[axis]=(na.dot(pa[0])-sum(na[k]*q[k] for k in other))/na[axis]
                blockers=[s.name for n,s in S.items() if n not in (a,b) and s.contains(q+na*.0001)]
                h=v.nearest_ray(list(S.values()),q+na*.00001,na,.1,exclude=(a,b))
                row['witness']={'point':list(q),'normal':list(na),'tri_a':ia,'tri_b':ib,'outward_probe_contained_by':blockers,'outward_cover':h['shape'].name if h else None,'cover_distance_m':h['distance'] if h else None}
    R['coplanar_plane_witnesses'].extend({'objects':[a,b],'plane':list(key),**row} for key,row in rows.items())
for n,s in S.items():
    zero=[];tiny=[]
    for i,t in enumerate(s.triangles):
        p=[s.vertices[j] for j in t];a=(p[1]-p[0]).cross(p[2]-p[0]).length*.5
        if a==0:zero.append(i)
        elif a<1e-12:tiny.append(i)
    if zero or tiny:R['zero_area_triangles'].append({'object':n,'exact_zero_area_triangle_count':len(zero),'tiny_nonzero_triangle_count':len(tiny),'zero_triangle_indices':zero[:20]})
for a,b,point,direction in [('D1 keycard reader','Office front wall mid',[-4.7,3.54,1.25],[0,1,0]),('Ink pad felt cushion','Ink pad tin base',[-2.8,3.42,1.0695],[0,0,-1]),('CD | Used cotton wipe','CD | Folded wipe lower ply',[-4.11,3.323,1.044],[0,0,-1]),('CD | D1 hinge strap','D1 door leaf',[-5.86,3.599,0.32],[0,1,0])]:
    d=Vector(direction);p=Vector(point);h=S[b].ray(p-d*.03,d,.08)
    R['bearing_penetration_rays'].append({'a':a,'b':b,'surface_point':point,'hit':list(h['point']) if h else None,'signed_gap_m':h['distance']-.03 if h else None})
out=ROOT/'revamp/production/critics/slice-s07-technical-surface-witness.json';out.write_text(json.dumps(R,indent=2));print('WITNESS_WRITTEN',out,flush=True)
