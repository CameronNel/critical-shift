"""Cold-load delivery inventory and new-geometry interface reservation evidence."""
import bpy,json,os,time,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review';rev=os.environ.get('SPAWN_REV','R06');path=R/'blender'/('facility_spawn_concept02_'+rev+'.blend')
t=time.perf_counter();bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);load=time.perf_counter()-t;bpy.context.view_layer.update()
L=json.loads((R/'production/LAYOUT_A12.json').read_text());hits=[];inventory=[]
for ob in bpy.data.collections['29_SPAWN_APPROVED_EXTERIOR'].objects:
 if ob.type not in {'MESH','CURVE','FONT'}:continue
 pts=[ob.matrix_world@Vector(p) for p in ob.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 inventory.append({'name':ob.name,'bounds':[lo,hi],'materials':[slot.material.name if slot.material else None for slot in ob.material_slots]})
 for reservation in L['reserved_volumes']:
  low=[c-s/2 for c,s in zip(reservation['center'],reservation['size'])];high=[c+s/2 for c,s in zip(reservation['center'],reservation['size'])]
  if all(min(hi[i],high[i])-max(lo[i],low[i])>.001 for i in range(3)):hits.append({'object':ob.name,'reservation':reservation['id']})
libs=[{'path':bpy.path.abspath(lib.filepath,library=lib.parent),'exists':Path(bpy.path.abspath(lib.filepath,library=lib.parent)).exists()} for lib in bpy.data.libraries]
visibility=[{'collection':c.name,'hide_render':c.hide_render,'hide_viewport':c.hide_viewport} for c in bpy.context.scene.collection.children]
report={'revision':rev,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'cold_load_seconds':load,'library_dependencies':libs,'new_object_inventory':inventory,'reserved_volume_intersections':hits,'reservation_check_pass':not hits,'visibility':visibility,'lighting_mode':bpy.context.scene.get('lighting_mode'),'blender_version':bpy.app.version_string,'runtime_scope':'Cold Blender assembly load benchmark only. No FPS, collision, navmesh or Unity readiness claim.','interior_lights':{'retained':True,'hide_render':bpy.data.collections['30_RETAINED_INTERIOR_LIGHTING'].hide_render,'hide_viewport':bpy.data.collections['30_RETAINED_INTERIOR_LIGHTING'].hide_viewport,'review_renderer':'Temporarily disables collection30 without saving.'},'interface_scope':'New exterior geometry vs all named reservation boxes. Existing apertures unchanged by build scripts; traversal geometry is separately tested by route audit.'}
(O/('DELIVERY_'+rev+'.json')).write_text(json.dumps(report,indent=2));print('DELIVERY',load,'seconds',len(hits),'reservation hits',sum(not x['exists'] for x in libs),'missing libraries',flush=True)

