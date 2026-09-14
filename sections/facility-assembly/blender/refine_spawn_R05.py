"""R04 -> R05: restrained background and stronger warm directional exterior light."""
import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_spawn_concept02_R04.blend'),load_ui=False)
s=bpy.context.scene
sun=next(o for o in s.objects if o.type=='LIGHT' and o.data.type=='SUN' and not o.library)
sun.rotation_euler=(.95,0,2.4);sun.data.color=(1,.90,.72);sun.data.energy=3.2
bpy.data.lights['S01 broad exterior skylight'].energy=5000
w=s.world;bg=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND')
for link in list(bg.inputs['Color'].links):w.node_tree.links.remove(link)
bg.inputs['Color'].default_value=(.25,.48,.78,1);bg.inputs['Strength'].default_value=.8
terrain=bpy.data.objects['Non-walkable distant landscape']
for v in terrain.data.vertices:
 if v.co.z>0:v.co.z=3+v.co.z*.22
for i in range(4):
 m=bpy.data.materials['S01 distant terrain '+str(i)];m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.22+i*.012,.31+i*.012,.36+i*.012,1)
# Broader low planting, still confined to approved beds.
ob=bpy.data.objects['S01 curved planted grasses']
for v in ob.data.vertices:
 if v.co.z<.69:v.co.z=.22+(v.co.z-.22)*1.5
# Roof membrane: warmer manufactured surface rather than neutral gray slab.
for collection in bpy.data.collections:
 if not collection.name.startswith('S01_'):continue
 for ob in collection.objects:
  if ob.type!='MESH':continue
  for slot in ob.material_slots:
   if slot.material and 'roof' in slot.material.name.lower():
    m=slot.material.copy();m.name='S01 warm roof membrane';slot.link='OBJECT';slot.material=m
    p=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
    if p and not p.inputs['Base Color'].is_linked:p.inputs['Base Color'].default_value=(.43,.39,.30,1)
s.name='FACILITY_SPAWN_CONCEPT02_R05';dest=R/'blender/facility_spawn_concept02_R05.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
b=json.loads((O/'BUILD_R04.json').read_text());b.update(revision='R05',file=str(dest),lighting_note='Warm diagonal sun, restrained broad fill, blue sky and lowered background silhouettes');(O/'BUILD_R05.json').write_text(json.dumps(b,indent=2));print('R05_SAVED',flush=True)
