"""R07 -> R08: authored roof membrane fields; restore interior light availability."""
import bpy,json,random,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_spawn_concept02_R07.blend'),load_ui=False)
s=bpy.context.scene;ext=bpy.data.collections['29_SPAWN_APPROVED_EXTERIOR'];random.seed(908)
helpers=(R/'blender/build_exteriors.py').read_text();exec(helpers[helpers.index('def mat('):helpers.index('def build_compliance():')],globals())
roof=[]
for i,color in enumerate([(.37,.32,.24),(.40,.35,.27),(.43,.38,.30),(.35,.31,.24)]):
 m=mat('S01 mineral coated membrane '+str(i),color,.88)
 for n in list(m.node_tree.nodes):
  if n.type=='BUMP':m.node_tree.nodes.remove(n)
 roof.append(m)
for c in bpy.data.collections:
 if not c.name.startswith('S01_'):continue
 for ob in c.objects:
  if ob.type=='MESH' and 'exterior opaque roof membrane' in ob.name:
   for sl in ob.material_slots:sl.link='OBJECT';sl.material=roof[1]
fields=[('Hall',(-29.78,-.575),(-26.22,9.375),3.568),('Briefing',(-35.38,.84),(-29.78,6.26),3.568),('Locker',(-26.30,.54),(-19.74,7.46),3.968),('Service',(-29.75,9.4),(-26.25,12.4),3.568)]
for name,a,b,z in fields:
 nx=math.ceil((b[0]-a[0])/1.55);ny=math.ceil((b[1]-a[1])/1.75);sx=(b[0]-a[0])/nx;sy=(b[1]-a[1])/ny
 for ix in range(nx):
  for iy in range(ny):
   ob=box(name+' laid membrane field',(a[0]+(ix+.5)*sx,a[1]+(iy+.5)*sy,z+.001),(sx-.012,sy-.012,.002),random.choice(roof),.001)
   ob['support']='retained exterior roof membrane';ob['purpose']='manufactured membrane course with restrained tonal variation'
# Interior source lights remain available in normal saved assembly state.
s['lighting_mode']='ASSEMBLY_INTERIOR_LIGHTS_AVAILABLE';bpy.data.collections['30_RETAINED_INTERIOR_LIGHTING'].hide_viewport=False;bpy.data.collections['30_RETAINED_INTERIOR_LIGHTING'].hide_render=False
s['interior_lighting_note']='Original lights retained and enabled. Exterior locked-view renderer temporarily disables collection30 for light-isolated exterior comparison.'
s.name='FACILITY_SPAWN_CONCEPT02_R08';dest=R/'blender/facility_spawn_concept02_R08.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
b=json.loads((O/'BUILD_R07.json').read_text());b.update(revision='R08',file=str(dest),roof_fields=len([o for o in ext.objects if 'laid membrane field' in o.name]),lighting_mode=s['lighting_mode']);(O/'BUILD_R08.json').write_text(json.dumps(b,indent=2));print('R08_SAVED',flush=True)
