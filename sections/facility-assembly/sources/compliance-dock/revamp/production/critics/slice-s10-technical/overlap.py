"""Fresh s10 read-only coplanar triangle intersections and classified envelope witnesses."""
import ast, bpy, json, hashlib, math
from pathlib import Path
from collections import defaultdict
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
tree=ast.parse((OUT/'probe.py').read_text())
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,(ast.Import,ast.ImportFrom,ast.ClassDef,ast.FunctionDef))],type_ignores=[]),str(OUT/'probe.py'),'exec'),globals())
bpy.context.window.scene=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];S=bpy.context.scene
G=collect(S,lambda o:o.type=='MESH' and (o.name.startswith('CD |') or o.name.startswith('Office front') or o.name.startswith('Hatch wall') or o.parent and o.parent.name in {'D1 Staff Front Door','Checkin Counter Hatch'}))
OG={**G,**collect(S,lambda o:o.type=='MESH' and o.name not in G and o.get('support_class')=='architectural')}
def inside(g,p):
    if not g.closed or not all(g.bounds[0][i]<p[i]<g.bounds[1][i] for i in range(3)):return False
    votes=[]
    for d in [Vector((1,.3713907,.529173)).normalized(),Vector((.219471,1,.681703)).normalized()]:
        h=g.ray(p,d,100.)
        votes.append(bool(h and h['normal'].dot(d)>1e-5))
    return all(votes)

def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def clip(subject,clipper):
    if cross(*clipper)<0:clipper=list(reversed(clipper))
    pts=subject
    for a,b in zip(clipper,clipper[1:]+clipper[:1]):
        old=pts;pts=[]
        if not old:break
        prev=old[-1];dp=cross(a,b,prev)
        for cur in old:
            dc=cross(a,b,cur)
            if (dc>=-1e-11)!=(dp>=-1e-11):
                t=dp/(dp-dc);pts.append((prev[0]+t*(cur[0]-prev[0]),prev[1]+t*(cur[1]-prev[1])))
            if dc>=-1e-11:pts.append(cur)
            prev=cur;dp=dc
    return pts
def area(poly):return abs(sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(poly,poly[1:]+poly[:1])))*.5
def overlapbox(a,b):return all(a[0][i]<=b[1][i]+1e-6 and b[0][i]<=a[1][i]+1e-6 for i in range(len(a[0])))
planes=defaultdict(list)
for n,g in G.items():
    for i,t in enumerate(g.tris):
        normal=g.normals[i]
        if g.areas[i]<1e-10:continue
        axis=max(range(3),key=lambda k:abs(normal[k]));other=[k for k in range(3) if k!=axis]
        vv=[g.vertices[k] for k in t];d=normal.dot(vv[0]);poly=[(v[other[0]],v[other[1]]) for v in vv]
        key=tuple(round(float(v),4) for v in normal)+(round(d,5),)
        bounds=([min(v[k] for v in poly) for k in range(2)],[max(v[k] for v in poly) for k in range(2)])
        planes[key].append({'name':n,'triangle':i,'normal':normal,'d':d,'axis':axis,'other':other,'poly':poly,'bounds':bounds,'verts':vv})
pairs=defaultdict(lambda:{'area_m2':0.,'pieces':0,'exposed_samples':0,'covered_samples':0,'witnesses':[]})
for key,rows in planes.items():
    for i,a in enumerate(rows):
        for b in rows[i+1:]:
            if a['normal'].dot(b['normal'])<.999999 or abs(a['d']-b['d'])>1e-6 or not overlapbox(a['bounds'],b['bounds']):continue
            intersection=clip(a['poly'],b['poly'])
            if len(intersection)<3:continue
            ar=area(intersection)
            if ar<1e-9:continue
            p=Vector((0,0,0));p[a['other'][0]]=sum(v[0] for v in intersection)/len(intersection);p[a['other'][1]]=sum(v[1] for v in intersection)/len(intersection)
            p[a['axis']]=(a['d']-sum(a['normal'][j]*p[j] for j in a['other']))/a['normal'][a['axis']]
            occluders=[]
            for gn,g in OG.items():
                if gn in {a['name'],b['name']}:continue
                start=p+a['normal']*.00002
                if inside(g,start):
                    occluders.append({'object':gn,'inside_closed_volume':True});continue
                hit=g.ray(start,a['normal'],.03)
                if hit:occluders.append(hit)
            exposed=not occluders;k=tuple(sorted((a['name'],b['name'])));r=pairs[k]
            r['area_m2']+=ar;r['pieces']+=1;r['exposed_samples' if exposed else 'covered_samples']+=1
            if len(r['witnesses'])<6:r['witnesses'].append({'triangle_a':a['triangle'],'triangle_b':b['triangle'],'point':p,'normal':a['normal'],'area_m2':ar,'exposed_outward_30mm':exposed,'occluders':occluders[:2]})

# Verify normals after translation into a local numerical frame. Open-ended
# converted curves and editable fonts are not asserted to be closed solids.
normal_summary=[{'object':n,'closed':g.closed,'signed_volume_m3':g.volume,'inconsistent_edges':g.inconsistent_winding,'zero_area':g.zero,'boundary_edges':g.boundaries} for n,g in G.items()]

# Primary shell datum and usable D1/hatch occupancy: sample actual triangles,
# separately disclose edge-bevel differences and the added 50mm head closure.
def structural_names(geom):return [n for n in geom if n.startswith('Office front') or n.startswith('Hatch wall') or n.startswith('D1 frame') or n.startswith('Hatch counter leg') or n=='CD | D1 transom closure']
CG={n:g for n,g in G.items() if n in structural_names(G)}
current_cuts=[]
samples=[(-6.3,.5),(-6.3,1.5),(-6.3,2.7),(-4.6,.5),(-4.6,1.5),(-4.6,2.7),(-2.53,.5),(-2.53,1.5),(-2.53,2.7),(-3.5,.5),(-3.5,1.5),(-3.5,2.7),(-5.4,2.32)]
def cut(geom,x,z,y):
    d=(0,1,0) if y<3.6 else (0,-1,0);hits=[g.ray((x,y,z),d,.8) for g in geom.values()];return min([h for h in hits if h],key=lambda h:h['distance']) if any(hits) else None
for x,z in samples:current_cuts.append({'x':x,'z':z,'front':cut(CG,x,z,3.25),'back':cut(CG,x,z,3.95)})
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'module.blend'),load_ui=False)
BG=collect(bpy.context.scene,lambda o:o.type=='MESH' and (o.name.startswith('Office front') or o.name.startswith('Hatch wall') or o.name.startswith('D1 frame') or o.name.startswith('Hatch counter leg')))
cutrows=[]
for r in current_cuts:
    cutrows.append({**r,'baseline_front':cut(BG,r['x'],r['z'],3.25),'baseline_back':cut(BG,r['x'],r['z'],3.95)})
apertures=[]
for label,xr,zr in [('D1 usable aperture',[-5.90,-5.7,-5.4,-5.1,-4.9],[.05,.3,.9,1.5,2.15]),('hatch above worktop',[-4.32,-4.1,-3.8,-3.5,-3.2,-2.9,-2.70],[1.07,1.2,1.6,2.0,2.3])]:
    b_occ=0;c_occ=0;diff=[]
    for x in xr:
        for z in zr:
            b=cut(BG,x,z,3.25);c=cut(CG,x,z,3.25);b_occ+=bool(b);c_occ+=bool(c)
            if bool(b)!=bool(c):diff.append({'x':x,'z':z,'baseline':b,'current':c})
    apertures.append({'label':label,'samples':len(xr)*len(zr),'baseline_shell_occupied':b_occ,'overhaul_shell_occupied':c_occ,'differences':diff,'movable_door_leaf_omitted':True})
report={'native_saved':False,'source_sha256':sha(ROOT/'module_overhaul_R1.blend'),'coplanar_comparison':'Actual coplanar same-outward-facing triangle polygon intersections; opposed butt joints excluded. Exposure uses a 30mm outward ray from intersection witness.','coplanar_pairs':[{'objects':list(k),**r} for k,r in pairs.items()],'normal_summary':normal_summary,'primary_shell_surface_rays':cutrows,'usable_aperture_samples':apertures,'unverified':['Coplanar exposure is sampled; distant external occlusion and arbitrary self-intersections are not an exhaustive proof.','Edge profile refinements mean exact old evaluated surface identity is not claimed.','Native source was reopened, never saved.']}
(OUT/'overlap.json').write_text(json.dumps(safe(report),indent=2)+'\n')
print('OVERLAP_COMPLETE',len(pairs),sum(r['exposed_samples'] for r in pairs.values()),flush=True)
