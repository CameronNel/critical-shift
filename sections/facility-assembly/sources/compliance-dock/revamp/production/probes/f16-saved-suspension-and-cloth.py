"""Read-only actual finished-surface and consumed cloth measurements."""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[3];P=R/'revamp/production';S=R/'module_overhaul_R1.blend'
state=json.loads((P/'build-state.json').read_text());assert state['revision']=='f16'
H=state['source_sha256'];sha=lambda:hashlib.sha256(S.read_bytes()).hexdigest();assert sha()==H
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False)
sc=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=sc;bpy.context.view_layer.update()
def shape(objects):
 v=[];f=[]
 for o in objects:
  start=len(v);v.extend(o.matrix_world@p.co for p in o.data.vertices);f.extend([start+i for i in face.vertices] for face in o.data.polygons)
 return BVHTree.FromPolygons(v,f,all_triangles=False)
def children(root):return [o for o in sc.objects if o.type=='MESH' and o.parent==root and any(m and m.name=='CD | steel' for m in o.data.materials)]
trayroot=sc.objects['CD | Longitudinal tray suspended assembly'];signroot=sc.objects['CD | P1 deep sign suspended assembly']
assert trayroot['support_class']=='supported_assembly' and signroot['support_class']=='supported_assembly'
trayparts=children(trayroot);signparts=children(signroot);assert trayparts and signparts
traysteel=shape(trayparts);signsteel=shape(signparts);checks=[]
def pair(label,a,b,p):
 p=Vector(p);d=Vector((0,0,1));ha=a.ray_cast(p+d*.02,-d,.04);hb=b.ray_cast(p-d*.02,d,.04)
 assert ha[0] is not None and hb[0] is not None,label
 gap=(hb[0]-ha[0]).z;assert abs(gap)<.000025,(label,gap)
 checks.append(dict(interface=label,source_surface=list(ha[0]),target_surface=list(hb[0]),actual_gap_m=gap))
tray=shape([sc.objects['Cable tray longitudinal -1.5']])
for y in [2.2,5.2,8.2,11.2,13.9]:
 for x in [-1.645,-1.355]:
  pair('saved tray lower suspension bearing',tray,traysteel,(x,y,3.51))
  pair('saved suspension upper truss bearing',traysteel,shape([sc.objects['Truss bot chord '+str(y)]]),(x,y,3.60))
for x in [-.52,.52]:
 pair('saved sign lower suspension bearing',shape([sc.objects['P1 corridor overhead sign']]),signsteel,(x,-1.85,2.45))
 pair('saved sign upper ceiling bearing',signsteel,shape([sc.objects['P1 corridor ceiling']]),(x,-1.85,2.60))
assert len(checks)==24
cloth=[]
for name in ['Chair seat cushion','Chair back lumbar','Chair back upper','CD | Joined Covered Trolley H1 / cotton']:
 o=sc.objects[name];me=o.data;me.calc_loop_triangles();layer=me.uv_layers['CD_Fabric_Cut_1m'];measures=[]
 for t in me.loop_triangles:
  a,b,c=[o.matrix_world@me.vertices[i].co for i in t.vertices];e1=b-a;e2=c-a;l1=e1.length;area=e1.cross(e2).length/2
  if area<1e-12:continue
  height=2*area/l1;along=e1.dot(e2)/l1;u0,u1,u2=[layer.data[i].uv.copy() for i in t.loops];d1=u1-u0;d2=u2-u0
  j00=d1.x/l1;j10=d1.y/l1;j01=(d2.x-j00*along)/height;j11=(d2.y-j10*along)/height
  aa=j00*j00+j10*j10;bb=j01*j01+j11*j11;ab=j00*j01+j10*j11;disc=math.sqrt((aa-bb)**2+4*ab*ab)
  smax=math.sqrt(max(0,(aa+bb+disc)/2));smin=math.sqrt(max(0,(aa+bb-disc)/2));measures.append((area,smax/max(smin,1e-20),smin,smax))
 total=sum(v[0] for v in measures)
 def percentile(index,f):
  acc=0
  for v in sorted(measures,key=lambda v:v[index]):
   acc+=v[0]
   if acc>=total*f:return v[index]
 record=dict(object=name,consumed_uv='CD_Fabric_Cut_1m',actual_materials=[m.name for m in me.materials],area_m2=total,area_fraction_anisotropy_gt_1_25=sum(a for a,r,*_ in measures if r>1.25)/total,area_weighted_anisotropy_p95=percentile(1,.95),maximum_anisotropy=max(v[1] for v in measures))
 cloth.append(record)
 # Write every actual result before failing the diagnostic gate.
assert sha()==H
out=dict(source_sha256=H,source_unchanged=True,native_written=False,scene_mutated=False,scope='Actual saved suspension bearing and targeted consumed cloth Jacobians; not exhaustive support strength or visual acceptance',finished_surface_checks=checks,consumed_cloth=cloth)
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
assert all(v['area_fraction_anisotropy_gt_1_25']<.0001 for v in cloth),cloth
print('F16_SAVED_24_BEARINGS_AND_TARGETED_CONSUMED_CLOTH_PASS',flush=True)
