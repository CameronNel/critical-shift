"""Read-only all-mesh actual shader-consumed cut-layer Jacobian diagnostic."""
import bpy,hashlib,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[3];F=R/'module_overhaul_R1.blend';H='6838d604ac4586da057a652e98e9c694f754a84e9f38ba70b83f1046e9ae6e9a';sha=lambda:hashlib.sha256(F.read_bytes()).hexdigest();assert sha()==H
bpy.ops.wm.open_mainfile(filepath=str(F),load_ui=False);S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S
records=[]
def active_cut(m):
 if not m or not m.node_tree:return False
 seen=set();queue=[n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and getattr(n,'is_active_output',True)]
 while queue:
  n=queue.pop()
  if n.as_pointer() in seen:continue
  seen.add(n.as_pointer())
  if n.type=='UVMAP' and n.uv_map=='CD_Fabric_Cut_1m':return True
  queue.extend(link.from_node for inp in n.inputs for link in inp.links)
 return False
for o in S.objects:
 if o.type!='MESH':continue
 used={p.material_index for p in o.data.polygons};mats=[o.data.materials[i] for i in used];active=[m.name for m in mats if active_cut(m)]
 if not active:continue
 me=o.data;layer=me.uv_layers.get('CD_Fabric_Cut_1m');assert layer,o.name;me.calc_loop_triangles();measures=[]
 for t in me.loop_triangles:
  if me.materials[t.material_index].name not in active:continue
  a,b,c=[o.matrix_world@me.vertices[i].co for i in t.vertices];e1=b-a;e2=c-a;l1=e1.length;area=e1.cross(e2).length/2
  if area<1e-12:continue
  height=2*area/l1;along=e1.dot(e2)/l1;u0,u1,u2=[layer.data[i].uv.copy() for i in t.loops];d1=u1-u0;d2=u2-u0
  j00=d1.x/l1;j10=d1.y/l1;j01=(d2.x-j00*along)/height;j11=(d2.y-j10*along)/height
  aa=j00*j00+j10*j10;bb=j01*j01+j11*j11;ab=j00*j01+j10*j11;disc=math.sqrt((aa-bb)**2+4*ab*ab)
  smax=math.sqrt(max(0,(aa+bb+disc)/2));smin=math.sqrt(max(0,(aa+bb-disc)/2));measures.append((area,smax/max(smin,1e-20),smin,smax,t.index))
 total=sum(v[0] for v in measures)
 def weighted(k,p):
  acc=0
  for v in sorted(measures,key=lambda v:v[k]):
   acc+=v[0]
   if acc>=total*p:return v[k]
 records.append(dict(object=o.name,actual_active_materials=active,consumed_uv='CD_Fabric_Cut_1m',area_m2=total,area_fraction_anisotropy_gt_1_25=sum(a for a,r,*_ in measures if r>1.25)/total,area_weighted_anisotropy_p95=weighted(1,.95),maximum_anisotropy=max(v[1] for v in measures),maximum_witness=max(measures,key=lambda v:v[1])))
assert sha()==H
Path(__file__).with_suffix('.json').write_text(json.dumps(dict(source_sha256=H,source_unchanged=True,native_written=False,scope='All actual output-connected shader cut UVs, not unconsumed physical audit layers; numerical diagnosis only, no independent visual score',results=records),indent=2)+'\n')
print('ALL_SHADER_CONSUMED_CLOTH_DIAGNOSTIC',records,flush=True)
