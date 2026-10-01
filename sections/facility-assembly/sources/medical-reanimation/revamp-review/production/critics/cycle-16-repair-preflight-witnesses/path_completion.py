import bpy,json,hashlib,math
from pathlib import Path
from mathutils.bvhtree import BVHTree
ROOT=Path('/workspace/critical-shift/sections/facility-assembly/sources/medical-reanimation');OUT=Path('/tmp/medical16-repair-technical');expected='39007192eef36f87c5299933e3a2a4f3462791871144c349a580ba2d9d322487'
with bpy.data.libraries.load(str(ROOT/'module_overhaul_R2.blend'),link=False) as (a,b):b.scenes=['REANIMATION_EDIT_LOCAL']
s=bpy.data.scenes['REANIMATION_EDIT_LOCAL'];bpy.context.window.scene=s;bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();g={};bounds={}
for o in s.objects:
 if o.type not in {'MESH','CURVE','FONT'}:continue
 ev=o.evaluated_get(deps);me=ev.to_mesh();me.calc_loop_triangles();v=[o.matrix_world@x.co for x in me.vertices];f=[tuple(x.vertices) for x in me.loop_triangles]
 if v and f:g[o.name]=(v,f,BVHTree.FromPolygons(v,f,all_triangles=True));bounds[o.name]=[[min(x[i] for x in v) for i in range(3)],[max(x[i] for x in v) for i in range(3)]]
 ev.to_mesh_clear()
source=(OUT/'audit_repair.py').read_text();exec(compile(source[source.index('def contact('):source.index('\nstock=[]')],str(OUT/'audit_repair.py'),'exec'))
rows=[]
for a,b in [('Serviceable inner access panel','Inner service panel rear support'),('Serviceable inner access panel.001','Inner service panel rear support.001'),('Inner service panel rear support','Rear machine skin'),('Inner service panel rear support.001','Rear machine skin'),('Chassis longitudinal channel','Fabricated chamber foot'),('Fabricated chamber foot','Chamber sole shoe'),('Chamber sole shoe','Floor'),('Reserve removable door','MED_R2 | Reserve fixed front crosschannel 1.28'),('MED_R2 | Reserve fixed front crosschannel 1.28','Reserve folded side'),('MED_R2 | Reserve fixed front crosschannel 0.14','Reserve folded side'),('Reserve folded side','Reserve folded cap')]:rows.append(contact(a,b))
for i in range(12):
 seal='Cartridge bottom seal'+('' if i==0 else '.'+str(i).zfill(3));shelves=[n for n in bounds if n.startswith('Folded storage shelf')];bottom=bounds[seal][0][2];shelf=min(shelves,key=lambda n:abs(bounds[n][1][2]-bottom));r=contact(seal,shelf);r['selection']='Nearest actual shelf crown by seal bottom Z; corrected shelf indexing from discovery.';rows.append(r)
 for host in ['Cartridge bank formed upright','Cartridge bank formed upright.001']:
  if not any(r['a']==shelf and r['b']==host for r in rows):rows.append(contact(shelf,host))
for a,b in [('Cartridge bank formed upright','Floor'),('Cartridge bank formed upright.001','Floor')]:rows.append(contact(a,b))
(OUT/'load-path-completion-witnesses.json').write_text(json.dumps(rows,indent=2));assert hashlib.sha256((ROOT/'module_overhaul_R2.blend').read_bytes()).hexdigest()==expected
print('LOAD_PATH_COMPLETION',[(r['a'],r['b'],r['sampled_surface_distance_m'],r['triangle_intersections']) for r in rows],flush=True)
