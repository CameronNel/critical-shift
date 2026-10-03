import ast,bpy,bmesh,hashlib,json,math
from pathlib import Path
from mathutils import Vector
from math import sqrt
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');P=R/'revamp/production/probes/f13-retry-preflight';source=R/'module_overhaul_R1.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before=sha(source)
with bpy.data.libraries.load(str(source),link=False) as (lib,loaded):loaded.scenes=['COMPLIANCE_EDIT_LOCAL']
S=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=S;bpy.context.view_layer.update()
for script,name in [('full_detail.py','octagon'),('full_repairs.py','developed_upholstery_chart')]:
 tree=ast.parse((R/script).read_text());function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
 exec(compile(ast.Module(body=[function],type_ignores=[]),str(R/script),'exec'),globals())
def clone(o,name):
 q=o.copy();q.data=o.data.copy();world=o.matrix_world.copy();q.parent=None;S.collection.objects.link(q);q.matrix_world=world;q.name=name;bpy.context.view_layer.update();return q
def material_count(o):return {'slots':[m.name for m in o.data.materials if m],'used_indices':sorted({f.material_index for f in o.data.polygons}),'vertices':len(o.data.vertices)}
material_cases=[]
for key in ['navy','wear']:
 leaf=clone(S.objects['P2 blast leaf east'],'TEMP '+key+' leaf');leaf.data.materials.clear();leaf.data.materials.append(bpy.data.materials['CD | wear'])
 pts=octagon(1.56002,.66002,.10);vs=[(1.15+x,y,1.+z) for y in [15.7419,15.792] for x,z in pts];fs=[tuple(range(7,-1,-1)),tuple(range(8,16))]+[(k,(k+1)%8,8+(k+1)%8,8+k) for k in range(8)]
 me=bpy.data.meshes.new('TEMP cut');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials['CD | '+key]);cut=bpy.data.objects.new('TEMP '+key+' cutter',me);S.collection.objects.link(cut)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 bpy.context.view_layer.objects.active=leaf;mod=leaf.modifiers.new('Actual material transfer probe','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name)
 material_cases.append({'cutter_material':key,**material_count(leaf)});bpy.data.objects.remove(cut,do_unlink=True);bpy.data.objects.remove(leaf,do_unlink=True)
def metric(o):
 o.data.calc_loop_triangles();uv=o.data.uv_layers['CD_Fabric_Cut_1m'];vs=[o.matrix_world@v.co for v in o.data.vertices];row={'triangles':len(o.data.loop_triangles),'max_anisotropy':0.,'surface_area_m2':0.,'zero_uv_area_m2':0.,'over_2_area_m2':0.}
 for t in o.data.loop_triangles:
  p=[vs[v] for v in t.vertices];u=[uv.data[i].uv.copy() for i in t.loops];a=p[1]-p[0];b=p[2]-p[0];du=u[1]-u[0];dv=u[2]-u[0];wa=a.cross(b).length/2;row['surface_area_m2']+=wa
  if wa<1e-12:continue
  ua=abs(du.x*dv.y-du.y*dv.x)/2
  if ua<1e-12:row['zero_uv_area_m2']+=wa;continue
  L=a.length;bx=b.dot(a)/L;by=2*wa/L;j00=du.x/L;j10=du.y/L;j01=(dv.x-j00*bx)/by;j11=(dv.y-j10*bx)/by;f=j00*j00+j10*j10+j01*j01+j11*j11;det=(j00*j11-j01*j10)**2;disc=math.sqrt(max(0,f*f-4*det));lo=(f-disc)*.5;hi=(f+disc)*.5;anis=math.sqrt(hi/max(lo,1e-15));row['max_anisotropy']=max(row['max_anisotropy'],anis)
  if anis>2:row['over_2_area_m2']+=wa
 return row
charts={}
for name in ['Chair seat cushion','Chair back lumbar','Chair back upper']:
 q=clone(S.objects[name],name+' temporary chart');old=metric(q);S.objects[name].name=name+' probe original';q.name=name;developed_upholstery_chart(q,q.data.uv_layers['CD_Fabric_Cut_1m']);new=metric(q);charts[name]={'before':old,'after':new};bpy.data.objects.remove(q,do_unlink=True)
report={'source_sha256':before,'source_unchanged':sha(source)==before,'native_saved':False,'method':'Corrected source/clone dependency-graph updates and exact upholstery names; read-only f12 append; isolated cloned leaf Boolean material test and three upholstery charts using only extracted named root helper functions. No full builder.','boolean_material_cases':material_cases,'upholstery':charts,'recipe_sha256':{n:sha(R/n) for n in ['overhaul_dock.py','full_detail.py','full_repairs.py','render_dock.py']},'formal_review':False}
(P/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
