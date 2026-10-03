import bpy,json,math,collections,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');O=R/'revamp/production/critics/full-c06-technical'
bpy.ops.wm.open_mainfile(filepath=str(R/'module_overhaul_R1.blend'),load_ui=False);s=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=s;dg=bpy.context.evaluated_depsgraph_get();report={'libraries':[],'uv':{},'islands':{},'ray_witnesses':[],'coplanarity':[]}
for lib in bpy.data.libraries:
 options=[Path(bpy.path.abspath(lib.filepath,library=lib.parent)),Path(bpy.path.abspath(lib.filepath))];p=next((x for x in options if x.is_file()),options[0]);raw=p.read_bytes() if p.is_file() else b'';report['libraries'].append({'name':lib.name,'parent':lib.parent.name if lib.parent else None,'raw_path':lib.filepath,'resolved_path':str(p.resolve()),'exists':p.is_file(),'native':raw.startswith((b'BLENDER',b'\x28\xb5\x2f\xfd',b'\x1f\x8b')),'sha256':hashlib.sha256(raw).hexdigest() if raw else None})
g={}
for obj in s.objects:
 if obj.type not in {'MESH','FONT','CURVE','SURFACE','META'}:continue
 e=obj.evaluated_get(dg);m=e.to_mesh(preserve_all_data_layers=True,depsgraph=dg);m.calc_loop_triangles();vs=[obj.matrix_world@v.co for v in m.vertices];ts=[list(t.vertices) for t in m.loop_triangles];uv=m.uv_layers.get('CD_Physical_1m');row={'type':obj.type,'layers':[x.name for x in m.uv_layers],'active':m.uv_layers.active.name if m.uv_layers.active else None,'metric_present':bool(uv),'zero_triangles':0,'zero_area_m2':0.,'surface_area_m2':0.,'max_stretch':0.,'bad_stretch_area_m2':0.,'slots':{}}
 if uv:
  for t in m.loop_triangles:
   p=[vs[i] for i in t.vertices];u=[Vector(uv.data[i].uv) for i in t.loops];wa=(p[1]-p[0]).cross(p[2]-p[0]).length*.5;ua=abs((u[1].x-u[0].x)*(u[2].y-u[0].y)-(u[1].y-u[0].y)*(u[2].x-u[0].x))*.5;row['surface_area_m2']+=wa
   slot=t.material_index;slotrow=row['slots'].setdefault(str(slot),{'material':obj.material_slots[slot].material.name if slot<len(obj.material_slots) and obj.material_slots[slot].material else None,'zero_triangles':0,'zero_area_m2':0.,'bad_stretch_area_m2':0.})
   if wa>1e-10 and ua<1e-12:row['zero_triangles']+=1;row['zero_area_m2']+=wa;slotrow['zero_triangles']+=1;slotrow['zero_area_m2']+=wa
   elif wa>1e-10:
    # solve J using orthonormal world basis; singular values via Frobenius/det.
    a=p[1]-p[0];b=p[2]-p[0];L=a.length;bx=b.dot(a)/L;by=2*wa/L;du=u[1]-u[0];dv=u[2]-u[0];j00=du.x/L;j10=du.y/L;j01=(dv.x-j00*bx)/by;j11=(dv.y-j10*bx)/by;f=j00*j00+j10*j10+j01*j01+j11*j11;det=(j00*j11-j01*j10)**2;disc=math.sqrt(max(0,f*f-4*det));lo=(f-disc)*.5;hi=(f+disc)*.5;stretch=math.sqrt(hi/max(lo,1e-15));row['max_stretch']=max(row['max_stretch'],stretch)
    if stretch>1.1:row['bad_stretch_area_m2']+=wa;slotrow['bad_stretch_area_m2']+=wa
 report['uv'][obj.name]=row
 bvh=BVHTree.FromPolygons(vs,ts,all_triangles=True) if ts else None;g[obj.name]={'obj':obj,'v':vs,'t':ts,'bvh':bvh}
 # connected mesh islands across evaluated triangles, actual world bounds and surface areas
 if obj.name.startswith('CD | Joined'):
  par=list(range(len(vs)))
  def find(x):
   while par[x]!=x:par[x]=par[par[x]];x=par[x]
   return x
  for t in ts:
   for a,b in zip(t,t[1:]):par[find(b)]=find(a)
  comp=collections.defaultdict(list)
  for i in range(len(vs)):comp[find(i)].append(i)
  ct=collections.defaultdict(list)
  for t in ts:ct[find(t[0])].append(t)
  report['islands'][obj.name]=[{'indices':ix,'triangles':ct[k],'bounds':[[min(vs[i][a] for i in ix) for a in range(3)],[max(vs[i][a] for i in ix) for a in range(3)]],'vertices':len(ix)} for k,ix in comp.items() if ct[k]]
 e.to_mesh_clear()
def ray(label,n,p,d,dist=5):
 x=g[n];loc,normal,face,length=x['bvh'].ray_cast(Vector(p),Vector(d),dist);report['ray_witnesses'].append({'label':label,'object':n,'origin':p,'direction':d,'hit':[float(x) for x in loc] if loc is not None else None,'normal':[float(x) for x in normal] if normal is not None else None,'distance_m':length})
# six P2 inherited ribs sample leaf-facing actual solid through low/high contact zone.
for x in [-2.,-1.2,-.4,.4,1.2,2.]:
 for z in [.15,1.75,3.35]:
  rib=f'P2 leaf rib {x}';leaf='P2 blast leaf west' if x<0 else 'P2 blast leaf east';ray('rib back actual surface',rib,[x,15.80,z],[0,-1,0]);ray('leaf front actual surface',leaf,[x,15.70,z],[0,1,0])
# all conveyor bearing rollers and added steel islands support chain
for i in range(29):
 y=5.5+i*.15
 for x,d,side in [(3.97,[1,0,0],'4.0'),(5.33,[-1,0,0],'5.3')]:
  for n in [f'Roller bearing cap {i}_{side}',f'Conveyor roller {i}','CD | Joined Cargo Inspection Conveyor / steel']:
   ray('roller bearing axial support',n,[x,y,.8],d,.2)
# actual slab/floor bearings and roof wall contact
for n in ['Floor slab','Roof deck ceiling slab','West perimeter wall','East perimeter wall']:
 if n in g:
  if n=='Floor slab':ray('floor datum',n,[0,1,.1],[0,0,-1],.5)
for y in [2.2,5.2,8.2,11.2,13.9]:
 for z in [3.65,4.25]:
  n=f'Truss {"bot" if z<4 else "top"} chord {y}';ray('roof chord actual bearing face',n,[-7,y,z],[1,0,0],14);ray('roof chord actual bearing face',n,[7,y,z],[-1,0,0],14)
(O/'surface-independent.json').write_text(json.dumps(report,indent=2));print('SURFACE_PROBE_DONE')
