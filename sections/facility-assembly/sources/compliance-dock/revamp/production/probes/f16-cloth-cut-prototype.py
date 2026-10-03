"""Isolated root-owned seam-chart experiment; no builder or native save."""
import bpy,ast,hashlib,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];SOURCE=R/'module_overhaul_R1.blend';H='d2514e668ea2b24e8b4ede6bde870e12f10c1afd6d6e1892b12c016266bd7b35'
sha=lambda:hashlib.sha256(SOURCE.read_bytes()).hexdigest();assert sha()==H
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False);scene=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=scene
code=ast.parse((R/'full_repairs.py').read_text());fn=next(n for n in code.body if isinstance(n,ast.FunctionDef) and n.name=='sewn_cushion_charts');exec(compile(ast.Module(body=[fn],type_ignores=[]),str(R/'full_repairs.py'),'exec'))
records=[]
for name in ['Chair seat cushion','Chair back lumbar','Chair back upper']:
 o=scene.objects[name];cut=o.data.uv_layers['CD_Fabric_Cut_1m'];sewn_cushion_charts(o,cut);o.data.calc_loop_triangles();measures=[]
 for t in o.data.loop_triangles:
  a,b,c=[o.matrix_world@o.data.vertices[i].co for i in t.vertices];e1=b-a;e2=c-a;l1=e1.length;area=e1.cross(e2).length/2
  if area<1e-12:continue
  height=2*area/l1;along=e1.dot(e2)/l1;u0,u1,u2=[cut.data[i].uv.copy() for i in t.loops];d1=u1-u0;d2=u2-u0
  j00=d1.x/l1;j10=d1.y/l1;j01=(d2.x-j00*along)/height;j11=(d2.y-j10*along)/height
  aa=j00*j00+j10*j10;bb=j01*j01+j11*j11;ab=j00*j01+j10*j11;disc=math.sqrt((aa-bb)**2+4*ab*ab)
  smax=math.sqrt(max(0,(aa+bb+disc)/2));smin=math.sqrt(max(0,(aa+bb-disc)/2));measures.append((area,smax/max(smin,1e-20)))
 total=sum(v[0] for v in measures);record=dict(object=name,area_fraction_gt_1_25=sum(a for a,r in measures if r>1.25)/total,maximum_anisotropy=max(v[1] for v in measures));records.append(record);assert record['area_fraction_gt_1_25']<.0001,record
assert sha()==H
Path(__file__).with_suffix('.json').write_text(json.dumps(dict(source_sha256=H,source_unchanged=True,native_written=False,only_in_memory_cloth_layer_modified=True,full_builder_executed=False,scope='Prototype only, saved F16 verification still required',results=records),indent=2)+'\n')
print('ISOLATED_F16_CLOTH_SEAM_CHART_PASS',records,flush=True)
