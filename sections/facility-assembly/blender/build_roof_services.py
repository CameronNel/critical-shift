"""A13 roof service construction: supported local ventilation, no facility-loop claims."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'connections/roof-services';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A12_complete.blend'),load_ui=False)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();scene=bpy.context.scene
ext=bpy.data.collections.new('20_ROOF_SERVICE_GEOMETRY');scene.collection.children.link(ext)
helpers=(R/'blender/build_exteriors.py').read_text();exec(helpers[helpers.index('def mat('):helpers.index('def build_compliance():')],globals())
olive=mat('Roof services olive painted steel',(.21,.25,.16),.62,.3)
L=json.loads((R/'production/LAYOUT_A12.json').read_text());report=[]
def ray(x,y):return scene.ray_cast(dg,Vector((x,y,40)),Vector((0,0,-1)),distance=40)
for sid in L['placements']:
 if sid in ['mine','condenser-bay']:continue
 ob=bpy.data.objects.get('WALK_PROXY_'+sid)
 if not ob:continue
 pts=[ob.matrix_world@Vector(v) for v in ob.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];chosen=None
 for fx,fy in [(.65,.65),(.35,.65),(.65,.35),(.5,.5),(.35,.35)]:
  x=lo[0]+(hi[0]-lo[0])*fx;y=lo[1]+(hi[1]-lo[1])*fy
  samples=[ray(x+dx,y+dy) for dx,dy in [(0,0),(-1.8,-1.1),(-1.8,1.1),(1.8,-1.1),(1.8,1.1)]]
  if not all(h[0] and h[2].z>.95 and h[1].z>3 for h in samples):continue
  if not all(sid in h[4].name for h in samples):continue
  heights=[h[1].z for h in samples]
  if max(heights)-min(heights)>.04:continue
  chosen=(x,y,max(heights));break
 if not chosen:report.append({'section':sid,'status':'NO_CLEAR_SUPPORTED_PATCH'});continue
 x,y,z=chosen
 box(sid+' service membrane pad',(x,y,z+.018),(3.65,2.25,.035),rubber,.002)
 for yy in [-.72,.72]:
  box(sid+' equipment load spreader',(x,y+yy,z+.095),(2.75,.18,.12),steel,.01)
  for xx in [-1.16,1.16]:rod(sid+' foot anchor',(x+xx,y+yy,z+.15),(x+xx,y+yy,z+.17),.035,ivory)
 box(sid+' rooftop air handling casing',(x,y,z+.62),(2.5,1.65,.94),olive,.04)
 box(sid+' folded weather hood',(x,y,z+1.12),(2.64,1.79,.1),steel,.025)
 # Louver openings and pitched blades, mounted on both long faces.
 for side in [-1,1]:
  yy=y+side*.832
  box(sid+' ventilation dark recess',(x,yy,z+.62),(2.12,.022,.63),rubber,.004)
  for j in range(7):
   blade=box(sid+' rain shedding louver',(x,yy+side*.035,z+.36+j*.085),(2.13,.12,.038),steel,.005);blade.rotation_euler.x=side*.3
  for xx in [-1.12,1.12]:box(sid+' louver frame',(x+xx,yy,z+.62),(.055,.05,.69),olive,.004)
 box(sid+' local isolator enclosure',(x+1.31,y,z+.63),(.12,.38,.43),ivory,.015)
 rod(sid+' roof power conduit',(x+1.4,y,z+.42),(x+1.4,y,z+.1),.023,steel)
 box(sid+' sealed conduit curb',(x+1.4,y,z+.065),(.23,.23,.13),steel,.01)
 # Adjacent roof access cover, independently supported on the tested patch.
 box(sid+' inspection cover curb',(x,y+.97,z+.08),(1.05,.28,.14),steel,.009)
 box(sid+' inspection cover lid',(x,y+.97,z+.16),(1.14,.34,.04),ivory,.008)
 report.append({'section':sid,'status':'BUILT','anchor':[x,y,z],'support_height_spread':max(heights)-min(heights),'support_objects':sorted(set(h[4].name for h in samples))})
cache=bpy.data.collections.new('21_ROOF_SERVICE_VIEWPORT_CACHE');scene.collection.children.link(cache)
bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in list(ext.objects):
 cp=o.copy();cp.data=o.data.copy();cache.objects.link(cp);cp.select_set(True);copies.append(cp)
assert copies
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();bpy.context.object.name='WALK_PROXY_ROOF_SERVICES';cache.hide_render=True;ext.hide_viewport=True
scene.name='FACILITY_A13_ROOF_SERVICES'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_walkthrough_A13_roof_services.blend'),compress=True)
for n in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE','18_REACTOR_FINISH_VIEWPORT_CACHE','21_ROOF_SERVICE_VIEWPORT_CACHE']:bpy.data.collections[n].hide_viewport=True
for n in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD','13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY','17_REACTOR_EXTERIOR_FINISH','20_ROOF_SERVICE_GEOMETRY']:bpy.data.collections[n].hide_viewport=False
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_master_A13_roof_services.blend'),compress=True)
(O/'BUILD.json').write_text(json.dumps({'sections':report,'authoring_objects':len(ext.objects),'viewport_objects':1},indent=2));print('ROOF_SERVICES_BUILT',report,flush=True)
