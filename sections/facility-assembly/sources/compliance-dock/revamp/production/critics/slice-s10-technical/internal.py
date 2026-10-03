"""Fresh native s10 internal load-path and component-normal measurements, no save."""
import ast,bpy,hashlib,json,math
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
tree=ast.parse((OUT/'probe.py').read_text())
exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,(ast.Import,ast.ImportFrom,ast.ClassDef,ast.FunctionDef))],type_ignores=[]),str(OUT/'probe.py'),'exec'),globals())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SOURCE=ROOT/'module_overhaul_R1.blend';EXPECTED='f817b83c4d0bcf1dec88e6f3b7bf39ddc9100da66e74a1a1c5015ebbe52c5265'
assert sha(SOURCE)==EXPECTED
bpy.context.window.scene=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];S=bpy.context.scene
G=collect(S)
def local(o):return o.name.startswith('CD |') or o.name.startswith('Office front') or o.name.startswith('Hatch wall') or o.parent and o.parent.name in {'D1 Staff Front Door','Checkin Counter Hatch'}
component_rows=[];C={};finite_failures=[]
for n,g in G.items():
    if not local(S.objects[n]):continue
    if not all(math.isfinite(c) for p in g.vertices for c in p):finite_failures.append(n)
    parent=list(range(len(g.vertices)))
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def unite(a,b):parent[find(a)]=find(b)
    for tr in g.tris:
        unite(tr[0],tr[1]);unite(tr[1],tr[2])
    buckets=defaultdict(list)
    for i,tr in enumerate(g.tris):buckets[find(tr[0])].append(i)
    comps=[]
    for idx,trids in enumerate(buckets.values()):
        tris=[g.tris[i] for i in trids];ids=sorted({v for t in tris for v in t});pts=[g.vertices[i] for i in ids]
        bounds=([min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)])
        centre=Vector([(bounds[0][i]+bounds[1][i])/2 for i in range(3)])
        volume=sum((g.vertices[a]-centre).dot((g.vertices[b]-centre).cross(g.vertices[c]-centre))/6 for a,b,c in tris)
        counts=defaultdict(int);wind=defaultdict(int)
        for t in tris:
            for a,b in zip(t,t[1:]+t[:1]):k=tuple(sorted((a,b)));counts[k]+=1;wind[k]+=1 if a<b else -1
        boundary=sum(v==1 for v in counts.values());multiple=sum(v>2 for v in counts.values());inconsistent=sum(wind[k]!=0 for k,v in counts.items() if v==2)
        row={'object':n,'component':idx,'triangles':len(tris),'bounds':bounds,'closed':boundary==0 and multiple==0,'signed_volume_centered_m3':volume,'boundary_edges':boundary,'multiface_edges':multiple,'inconsistent_winding_edges':inconsistent,'zero_area_triangles':sum(g.areas[i]==0 for i in trids),'nonfinite_normals':sum(not all(math.isfinite(c) for c in g.normals[i]) for i in trids),'type':g.type}
        component_rows.append(row)
        comps.append({'row':row,'bvh':BVHTree.FromPolygons(g.vertices,tris,all_triangles=True,epsilon=0),'normals':[g.normals[i] for i in trids]})
    C[n]=comps

def raycomp(c,p,d):
    q,n,t,dist=c['bvh'].ray_cast(Vector(p),Vector(d),.5)
    return {'point':q,'normal':c['normals'][t],'distance':dist,'component':c['row']['component']} if q is not None else None
mounts=C['CD | D1 ID captive stand-offs'];ID=[]
for x in [-5.545,-5.255]:
    for z in [1.89,1.95]:
        candidates=[c for c in mounts if c['row']['bounds'][0][0]<x<c['row']['bounds'][1][0] and c['row']['bounds'][0][2]<z<c['row']['bounds'][1][2]]
        spacer=max(candidates,key=lambda c:c['row']['bounds'][1][1]);head=min(candidates,key=lambda c:c['row']['bounds'][1][1])
        pfront=G['CD | D1 ID enamel'].ray((x,3.45,z),(0,1,0),.3)
        pback=G['CD | D1 ID enamel'].ray((x,3.65,z),(0,-1,0),.3)
        sf=raycomp(spacer,(x,3.45,z),(0,1,0));sb=raycomp(spacer,(x,3.65,z),(0,-1,0));hb=raycomp(head,(x,3.65,z),(0,-1,0))
        supports=[G[n].ray((x,3.55,z),(0,1,0),.3) for n in ['D1 door leaf','CD | D1 die-pressed leaf.001']]
        support=min([h for h in supports if h],key=lambda h:h['distance'])
        row={'sample':[x,z],'plate_front':pfront,'plate_back':pback,'spacer_front':sf,'spacer_back':sb,'head_back':hb,'actual_stepped_skin':support,'plate_to_spacer_separation_m':sf['point'].y-pback['point'].y,'spacer_to_skin_separation_m':support['point'].y-sb['point'].y,'head_to_plate_separation_m':pfront['point'].y-hb['point'].y,'spacer_component':spacer['row'],'head_component':head['row']}
        row['load_path_contact_pass']=all(abs(row[k])<=.00002 for k in ['plate_to_spacer_separation_m','spacer_to_skin_separation_m','head_to_plate_separation_m'])
        ID.append(row)
# Datums are compared directly to the frozen module, as native geometry.
current_floor=G['Floor slab'].bounds
arch=[g for n,g in G.items() if S.objects[n].get('support_class')=='architectural']
current_arch_bounds=([min(g.bounds[0][i] for g in arch) for i in range(3)],[max(g.bounds[1][i] for g in arch) for i in range(3)])
current_closure=G['CD | D1 transom closure'].bounds
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'module.blend'),load_ui=False)
B=bpy.context.scene;BG=collect(B,lambda o:o.get('support_class')=='architectural')
base_arch_bounds=([min(g.bounds[0][i] for g in BG.values()) for i in range(3)],[max(g.bounds[1][i] for g in BG.values()) for i in range(3)])
report={'source_sha256':sha(SOURCE),'source_unchanged':sha(SOURCE)==EXPECTED,'native_saved':False,'finite_vertex_failures':finite_failures,'id_rigid_plate_four_standoff_loadpaths':ID,'component_geometry':component_rows,'primary_datums':{'floor_current':current_floor,'floor_baseline':BG['Floor slab'].bounds,'architectural_bounds_current':current_arch_bounds,'architectural_bounds_baseline':base_arch_bounds,'added_unused_frame_headslot_closure_bounds':current_closure,'closure_interpretation':'Adds solid in the former 50mm head slot at z2.30..2.35, above the preserved 2.20m usable D1 doorway. Literal all-solid union identity is not claimed.'},'classification':'Closed solid components require finite, noncollapsed triangles, positive centered signed volume and consistent shared-edge winding. Open-ended curves and evaluated text are classified separately; engaged fastener components may penetrate intentionally.','unverified':['Sampled bearings do not establish every possible internal point.','No runtime, full-room or engine performance approval.']}
(OUT/'internal.json').write_text(json.dumps(safe(report),indent=2)+'\n');print('INTERNAL_COMPLETE',len(component_rows),len(ID),flush=True)
