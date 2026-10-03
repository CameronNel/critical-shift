import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).parent;R=P.parents[3]
source=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock/module_overhaul_R1.blend')
with bpy.data.libraries.load(str(source),link=False) as (lib,loaded):loaded.scenes=['COMPLIANCE_EDIT_LOCAL']
s=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=s;dg=bpy.context.evaluated_depsgraph_get();rows={};materials={}
used={slot.material for o in s.objects for slot in o.material_slots if slot.material}
for mat in used:
 nodes=mat.node_tree.nodes if mat.node_tree else [];materials[mat.name]={'uv_names':[n.uv_map for n in nodes if n.type=='UVMAP'],'attribute_names':[n.attribute_name for n in nodes if n.type=='ATTRIBUTE'],'image_nodes':[n.image.name if n.image else None for n in nodes if n.type=='TEX_IMAGE'],'coordinates':[{'node':n.name,'outputs_used':[x.name for x in n.outputs if x.is_linked]} for n in nodes if n.type=='TEX_COORD'],'mapping':[{'vector_type':n.vector_type,'scale':list(n.inputs['Scale'].default_value)} for n in nodes if n.type=='MAPPING'],'shader_links':[{'from_node':x.from_node.name,'from_socket':x.from_socket.name,'to_node':x.to_node.name,'to_socket':x.to_socket.name} for x in mat.node_tree.links] if mat.node_tree else []}
for o in s.objects:
 if o.type!='MESH' or not o.data.uv_layers.get('CD_Fabric_Cut_1m'):continue
 e=o.evaluated_get(dg);m=e.to_mesh(preserve_all_data_layers=True,depsgraph=dg);m.calc_loop_triangles();uv=m.uv_layers.get('CD_Fabric_Cut_1m');vs=[o.matrix_world@v.co for v in m.vertices];row={'triangles':len(m.loop_triangles),'surface_area_m2':0.,'zero_uv_area_m2':0.,'max_anisotropy':0.,'stretch_over_1_25_area_m2':0.,'stretch_over_2_area_m2':0.,'material_names':[slot.material.name for slot in o.material_slots if slot.material]}
 for t in m.loop_triangles:
  p=[vs[i] for i in t.vertices];u=[Vector(uv.data[i].uv) for i in t.loops];a=p[1]-p[0];b=p[2]-p[0];wa=a.cross(b).length*.5;row['surface_area_m2']+=wa;du=u[1]-u[0];dv=u[2]-u[0];ua=abs(du.x*dv.y-du.y*dv.x)*.5
  if wa<1e-12:continue
  if ua<1e-12:row['zero_uv_area_m2']+=wa;continue
  L=a.length;bx=b.dot(a)/L;by=2*wa/L;j00=du.x/L;j10=du.y/L;j01=(dv.x-j00*bx)/by;j11=(dv.y-j10*bx)/by;f=j00*j00+j10*j10+j01*j01+j11*j11;det=(j00*j11-j01*j10)**2;disc=math.sqrt(max(0,f*f-4*det));lo=(f-disc)*.5;hi=(f+disc)*.5;anis=math.sqrt(hi/max(lo,1e-15));row['max_anisotropy']=max(row['max_anisotropy'],anis)
  if anis>1.25:row['stretch_over_1_25_area_m2']+=wa
  if anis>2:row['stretch_over_2_area_m2']+=wa
 rows[o.name]=row;e.to_mesh_clear()
(P/'material-uv-consumption.json').write_text(json.dumps({'materials':materials,'fabric_cut_layers':rows},indent=2));print('MATERIALS',len(materials));print('FABRIC',rows)
