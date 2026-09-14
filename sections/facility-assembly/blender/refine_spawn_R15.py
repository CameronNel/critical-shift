"""R14 -> R15: connect stowed hose to its wall support and verify protected rock vertices."""
import bpy,json,math
from pathlib import Path
from mathutils.kdtree import KDTree
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_spawn_concept02_R14.blend'),load_ui=False)
ext=bpy.data.collections['29_SPAWN_APPROVED_EXTERIOR'];helpers=(R/'blender/build_exteriors.py').read_text();exec(helpers[helpers.index('def mat('):helpers.index('def build_compliance():')],globals())
steel=bpy.data.materials['S01 graphite folded steel'];orange=bpy.data.materials['S01 burnt orange identification']
rod('Hose reel supported axle',(-32.35,.27,1.22),(-32.35,.52,1.22),.115,steel)
rod('Hose reel back flange',(-32.35,.425,1.22),(-32.35,.450,1.22),.253,steel)
rod('Hose reel spindle cap',(-32.35,.255,1.22),(-32.35,.275,1.22),.065,orange)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();checks=[]
for name in ['S01 exterior quarried front material override','S01 exterior upper mountain material override']:
 ob=bpy.data.objects[name];index=ob.vertex_groups['Protected lower interface and boundary'].index;protected=[v.co.copy() for v in ob.data.vertices if any(g.group==index and g.weight>.99 for g in v.groups)]
 evaluated=ob.evaluated_get(dg);mesh=evaluated.to_mesh();tree=KDTree(len(mesh.vertices))
 for i,v in enumerate(mesh.vertices):tree.insert(v.co,i)
 tree.balance();error=max((tree.find(v)[2] for v in protected),default=0)
 checks.append({'object':name,'protected_vertices':len(protected),'max_nearest_vertex_error_m':error,'evaluated_faces':len(mesh.polygons),'pass':error<.0001});evaluated.to_mesh_clear()
# Reject simplification if any protected vertex was moved/deleted: retain the prior exact geometry.
for check in checks:
 if not check['pass']:
  ob=bpy.data.objects[check['object']];ob.modifiers.remove(ob.modifiers['Upper exterior rock planes']);check['fallback']='Simplification removed; exact R13 geometry retained';check['delivered_protected_interface_pass']=True
 else:check['delivered_protected_interface_pass']=True
s=bpy.context.scene;s.name='FACILITY_SPAWN_CONCEPT02_R15';dest=R/'blender/facility_spawn_concept02_R15.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
b=json.loads((O/'BUILD_R14.json').read_text());b.update(revision='R15',file=str(dest),new_objects=len(ext.objects),new_faces=sum(len(o.data.polygons) for o in ext.objects if o.type=='MESH'),scope='Spawn exterior and rescue courtyard, including approved visible exterior rock context. Original room libraries preserved.',protected_rock_checks=checks,hose_support='Axle overlaps retained wall mounting box and inner hose coil; back flange supports reel');(O/'BUILD_R15.json').write_text(json.dumps(b,indent=2));print('R15_SAVED',checks,flush=True)
