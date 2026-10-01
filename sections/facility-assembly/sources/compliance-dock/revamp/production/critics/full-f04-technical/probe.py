import bpy, json, hashlib, math, importlib.util
from pathlib import Path
from collections import defaultdict
from mathutils import Vector
import numpy as np
ROOT=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');OUT=ROOT/'revamp/production/critics/full-f04-technical'
S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S;DG=bpy.context.evaluated_depsgraph_get();DG.update()
spec=importlib.util.spec_from_file_location('dv',ROOT/'validate_dock.py');dv=importlib.util.module_from_spec(spec);spec.loader.exec_module(dv)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'source_sha256':sha(bpy.data.filepath),'scene':S.name,'blender':bpy.app.version_string,'scope':'Read-only targeted native technical diagnosis, not acceptance or full cycle','contacts':[]}
base=json.loads((ROOT/'revamp/production/baseline.json').read_text())['objects'];r['matrices']={'count':len(base),'missing':[],'changed':[],'max_delta':0}
for rec in base:
 o=S.objects.get(rec['name'])
 if o is None:r['matrices']['missing'].append(rec['name']);continue
 delta=max(abs(o.matrix_world[i][j]-rec['matrix'][i][j]) for i in range(4) for j in range(4));r['matrices']['max_delta']=max(delta,r['matrices']['max_delta'])
 if delta>1e-6:r['matrices']['changed'].append({'object':o.name,'delta':delta})
protected=json.loads((ROOT/'revamp/production/protected-inputs.json').read_text());r['protected']=[dict(path=rel,expected=exp,actual=sha(ROOT.parents[3]/rel),unchanged=sha(ROOT.parents[3]/rel)==exp) for rel,exp in protected.items()]
r['libraries']=[]
for lib in bpy.data.libraries:
 p=Path(bpy.path.abspath(lib.filepath,library=lib.parent))
 if not p.is_file():p=Path(bpy.path.abspath(lib.filepath))
 r['libraries'].append({'raw':lib.filepath,'relative':lib.filepath.startswith('//'),'exists':p.is_file(),'resolved':str(p),'native_payload':p.read_bytes()[:8].startswith((b'BLENDER',b'\x28\xb5\x2f\xfd',b'\x1f\x8b')) if p.is_file() else False})
shapes={};meshes={};r['topology']=[];r['fabric_uv']=[]
for o in S.objects:
 if o.type!='MESH':continue
 E=o.evaluated_get(DG);m=E.to_mesh();m.calc_loop_triangles();points=[o.matrix_world@v.co for v in m.vertices];tris=[tuple(t.vertices) for t in m.loop_triangles]
 edgefaces=defaultdict(list)
 for ti,t in enumerate(tris):
  for a,b in zip(t,t[1:]+t[:1]):edgefaces[tuple(sorted((a,b)))].append((ti,1 if a<b else -1))
 boundary=[e for e,fs in edgefaces.items() if len(fs)==1];nonmanifold=[e for e,fs in edgefaces.items() if len(fs)>2];winding=[e for e,fs in edgefaces.items() if len(fs)==2 and fs[0][1]==fs[1][1]]
 zero=[i for i,t in enumerate(tris) if (points[t[1]]-points[t[0]]).cross(points[t[2]]-points[t[0]]).length<1e-15]
 adjacency=defaultdict(list)
 for fs in edgefaces.values():
  if len(fs)==2:
   a,b=fs[0][0],fs[1][0];adjacency[a].append(b);adjacency[b].append(a)
 negative=[];seen=set();count=0
 for ti in range(len(tris)):
  if ti in seen:continue
  todo=[ti];seen.add(ti);component=[]
  while todo:
   f=todo.pop();component.append(f)
   for n in adjacency[f]:
    if n not in seen:seen.add(n);todo.append(n)
  count+=1
  closed=all(len(edgefaces[tuple(sorted((a,b)))])==2 for f in component for a,b in zip(tris[f],tris[f][1:]+tris[f][:1]))
  if closed:
   volume=sum(points[t[0]].dot(points[t[1]].cross(points[t[2]])) for f in component for t in [tris[f]])/6
   if volume<-1e-9:negative.append({'triangle':ti,'volume_m3':volume})
 if boundary or nonmanifold or winding or zero or negative:r['topology'].append(dict(object=o.name,boundary_edges=len(boundary),overused_edges=len(nonmanifold),inconsistent_winding=len(winding),collapsed=len(zero),negative_closed_components=negative,connected_components=count))
 if 'CD_Fabric_Cut_1m' in m.uv_layers:
  layer=m.uv_layers['CD_Fabric_Cut_1m'];finite=all(math.isfinite(float(v)) for uv in layer.data for v in uv.uv);seams=[];edges=defaultdict(list);sing=[];edge_ratios=[];collapseduv=0
  for t in m.loop_triangles:
   p=[points[i] for i in t.vertices];u=[layer.data[i].uv.copy() for i in t.loops]
   for j in range(3):
    k=(j+1)%3;length=(p[k]-p[j]).length
    if length>.0001:edge_ratios.append((u[k]-u[j]).length/length)
    a,b=t.vertices[j],t.vertices[k];edges[tuple(sorted((a,b)))].append([list(u[j]),list(u[k])] if a<b else [list(u[k]),list(u[j])])
   u0=np.array(u[1])-np.array(u[0]);u1=np.array(u[2])-np.array(u[0]);q0=p[1]-p[0];q1=p[2]-p[0]
   if q0.length<1e-12:continue
   e=q0.normalized();g=np.array([[q0.length,q1.dot(e)],[0,max(0,q1.length_squared-q1.dot(e)**2)**.5]])
   if abs(np.linalg.det(g))<1e-12:continue
   J=np.column_stack((u0,u1))@np.linalg.inv(g);sv=np.linalg.svd(J,compute_uv=False)
   if min(sv)<1e-6:collapseduv+=1
   else:sing.append((min(sv),max(sv),int(t.index)))
  for e,uvs in edges.items():
   if len(uvs)==2 and max(abs(uvs[0][i][j]-uvs[1][i][j]) for i in range(2) for j in range(2))>1e-5:seams.append(e)
  r['fabric_uv'].append(dict(object=o.name,finite=finite,consumed_by=[mat.name for mat in m.materials if mat and mat.node_tree and any(n.type=='UVMAP' and n.uv_map=='CD_Fabric_Cut_1m' for n in mat.node_tree.nodes)],shared_edge_seams=len(seams),collapsed_uv_triangles=collapseduv,edge_ratio_range=[min(edge_ratios),max(edge_ratios)] if edge_ratios else [],singular_value_range=[min(a for a,b,i in sing),max(b for a,b,i in sing)] if sing else [],max_stretch_witness=max(sing,key=lambda v:v[1]) if sing else None))
 E.to_mesh_clear()
print('BASE_FINISHED',flush=True)
def shape(n):
 if n not in shapes:shapes[n]=dv.Shape(S.objects[n],DG)
 return shapes[n]
def rayhits(n,p,d,span):
 sh=shape(n);p=Vector(p);d=Vector(d).normalized();origin=p-d*span;hits=[]
 for k in range(100):
  h=sh.ray(origin,d,span*2)
  if h is None or (h['point']-p).dot(d)>span+1e-6:break
  hits.append({'point':list(h['point']),'normal':list(h['normal']),'triangle':h['face'],'signed':(h['point']-p).dot(d)})
  origin=h['point']+d*1e-6
 return hits
def contact(label,A,B,p,d,span=.025,engagement=None):
 ha=rayhits(A,p,d,span);hb=rayhits(B,p,d,span);row={'label':label,'a':A,'b':B,'point':p,'direction':d,'intentional_mechanical_engagement':engagement}
 if not ha or not hb:row.update(status='ray_miss',a_hits=ha,b_hits=hb)
 else:
  a=max(ha,key=lambda h:h['signed']);b=min(hb,key=lambda h:h['signed']);gap=b['signed']-a['signed'];D=Vector(d).normalized();angle=max(math.degrees(math.acos(max(-1,min(1,Vector(a['normal']).dot(D))))),math.degrees(math.acos(max(-1,min(1,Vector(b['normal']).dot(-D))))))
  row.update(signed_gap_m=gap,angle_error_deg=angle,a_surface=a,b_surface=b,status='within_default' if -.002001<=gap<=.005001 and angle<=12.001 else ('engagement_measured' if engagement and gap<=.005001 else 'outside_default'))
 r['contacts'].append(row)
# Utility enclosure rear stand-offs and backboard, all 12 real fastening stations.
U='CD | Joined Wall Utilities Rack / steel';B='Utility backer panel'
for n in ['Transformer box 1','Transformer box 2','Main breaker disconnect']:
 rec=next(x for x in base if x['name']==n);x,y,z=rec['location'];depth,w,h=rec['dimensions']
 for yy in [y-w*.34,y+w*.34]:
  for zz in [z-h*.35,z+h*.35]:
   contact('utility enclosure to stand-off',n,U,[6.76,yy,zz],[1,0,0],.012)
   contact('utility stand-off to backboard',U,B,[6.78,yy,zz],[1,0,0],.012)
 contact('utility separate door to rim','CD | Joined Wall Utilities Rack / blue',n,[x-depth/2,y+w*.42,z],[1,0,0],.01)
# Drawer pull studs + holder seats; sample actual U-pull ends.
for k,y in enumerate([8.3,9.1]):
 studs=f'CD | Joined CD | Office file cabinet {k} / steel'
 for j in range(4):
  z=.22+.30*j
  for yy in [y-.1,y+.1]:
   contact('drawer pull to captive stud',f'Drawer pull {k}_{j}',studs,[-6.,yy,z],[-1,0,0],.013,'Curve pull and stud use a deliberately engaged mechanical joint')
   contact('drawer stud to drawer face',studs,f'Drawer face {k}_{j}',[-6.01,yy,z],[-1,0,0],.004)
  contact('drawer cardholder seat',f'Drawer cardholder {k}_{j}',f'Drawer face {k}_{j}',[-6.01,y,z+.03],[-1,0,0],.006)
# Beacon mounting and cap separation.
for x in [-1.5,1.5]:
 contact('arrival beacon to wall bracket',f'P2 beacon base {x}','CD | Joined Arrival Gate P2 / charcoal',[x,15.77,3.9],[0,1,0],.02)
 contact('arrival bracket to actual wall','CD | Joined Arrival Gate P2 / charcoal','North lintel P2',[x,15.8,3.9],[0,1,0],.02)
 contact('beacon lens to base',f'P2 beacon amber {x}',f'P2 beacon base {x}',[x,15.68,3.93],[0,0,-1],.02)
contact('G1 beacon seat','G1 warning strobe beacon','CD | G1 beacon captive seat',[3.02,7,2.51],[0,0,-1],.015)
# All 58 roller journals, matched axial bearing cap/roller endpoints.
steel='CD | Joined Cargo Inspection Conveyor / steel'
for i in range(29):
 y=5.5+.15*i
 for x,sign in [(4.02,-1),(5.28,1)]:
  contact('roller axial journal',f'Conveyor roller {i}',steel,[x,y,.80],[sign,0,0],.008,'1mm axial journal insertion into roller')
  cap=f'Roller bearing cap {i}_{4.0 if sign<0 else 5.3}'
  contact('journal to bearing cap',steel,cap,[4.010 if sign<0 else 5.290,y,.80],[sign,0,0],.006,'1mm axial journal insertion into bearing cap')
# All eyes: roof to flange, flange/stem and stem/forged eye.
for x,y in [(4.05,6.65),(4.05,8.65),(5.25,6.65),(5.25,8.65)]:
 contact('lifting-eye flange roof seat',steel,'Lead tunnel main body',[x,y,2.15],[0,0,-1],.006)
 contact('lifting eye stem root',f'Lifting eyebolt stem {x}_{y}',steel,[x,y,2.15],[0,0,-1],.006,'Stem is deliberately seated within 8mm flange bore')
 contact('vertical eye to stem',f'Lifting eyebolt ring {x}_{y}',f'Lifting eyebolt stem {x}_{y}',[x,y,2.162],[0,0,-1],.004)
# Motor chassis transfer, control cantilever transfer.
contact('motor body to mounting plate','Drive motor housing','Drive motor mounting plate',[5.68,9.2,.53],[0,0,-1],.04)
for y in [9.04,9.36]:
 contact('motor plate to welded saddle','Drive motor mounting plate',steel,[5.60,y,.505],[0,0,-1],.01)
 # saddle root meets chassis tie via its vertical tongue
 contact('motor saddle to chassis',steel,'CD | Joined Cargo Inspection Conveyor / navy',[5.345,y,.615],[-1,0,0],.009,'Saddle tongue welded through chassis face')
for y in [7.35,7.95]:
 contact('operator desk arm to cantilever','Conveyor operator desk arm',steel,[3.625,y,.92],[1,0,0],.025)
 contact('operator cantilever to cargo shell',steel,'Lead tunnel main body',[3.9,y,1.15],[1,0,0],.025,'Cantilever root welded to housing wall')
 contact('monitor pedestal to actual desk','CD | Joined Cargo Inspection Conveyor / charcoal','Conveyor operator desk arm',[3.35,y,.94],[0,0,-1],.006)
# Original suspension rods connect an actual end cap and roof plate.
for rec in base:
 if not rec['name'].endswith(' Fixture Housing'):continue
 prefix=rec['name'].removesuffix(' Fixture Housing');x,y,z=rec['location'];f='CD | Joined CD | '+prefix+' suspended fixture / steel';cap='CD | Joined CD | '+prefix+' suspended fixture / charcoal'
 for yy in [y-.46,y+.46]:
  contact('fixture rod to end-cap',f,cap,[x,yy,z+.042],[0,0,-1],.012)
  contact('fixture roof plate actual seat',f,'Roof deck ceiling slab',[x,yy,4.4],[0,0,1],.012)
for name,(x,y,z) in [('Inspection face',(2.3,4.4,3.25)),('Custody transfer',(-4.8,11.3,3.15))]:
 f='CD | Joined CD | '+name+' luminaire / steel';lamp='CD | Fitted angled lamp'+('' if name=='Inspection face' else '.001')
 contact('new luminaire fork to lamp',f,lamp,[x,y,z+.05],[0,0,-1],.015)
 contact('new luminaire stem roof',f,'Roof deck ceiling slab',[x,y,4.4],[0,0,1],.01)
# All webbing vertices on lower surface, sample actual downward garment support.
for j in range(4):
 name='Trolley strap '+str(j);sh=shape(name)
 gaps=[];witness=[]
 for p in sh.vertices[:50]:
  h=shape('Covered Trolley Draped Tarp').ray(p+Vector((0,0,.015)),Vector((0,0,-1)),.04)
  if h:
   gap=p.z-h['point'].z;gaps.append(gap);witness.append(dict(strap=list(p),cloth=list(h['point']),gap=gap))
 r.setdefault('webbing',[]).append(dict(object=name,samples=len(gaps),gap_range=[min(gaps),max(gaps)] if gaps else [],max_gap_witness=max(witness,key=lambda x:x['gap']) if witness else None))
for x in [-6.20,-5.50]:
 for y in [12.3,13.25,14.2]:
  # Actual cloth perimeter bearing; not bounding box evidence.
  contact('cloth to trolley perimeter','Covered Trolley Draped Tarp','Trolley bed perimeter',[x,y,.81],[0,0,-1],.06)
(OUT/'probe.json').write_text(json.dumps(dv.json_safe(r),indent=2,allow_nan=False))
print('PROBE_FINISHED',len(r['contacts']),flush=True)
