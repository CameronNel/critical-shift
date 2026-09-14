import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'connections/map-finish'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A08_access.blend'),load_ui=False)
with bpy.data.libraries.load(str(O/'access-finish-A09.blend'),link=False) as (src,dst):dst.collections=['13_FINISHED_ACCESS_SCENERY','14_ACCESS_FINISH_VIEWPORT_CACHE']
for c in dst.collections:bpy.context.scene.collection.children.link(c)
bpy.data.collections['13_FINISHED_ACCESS_SCENERY'].hide_viewport=True
material=bpy.data.materials['EXT mineral painted concrete'].copy();material.name='ACCESS FINISH walking concrete';material.diffuse_color=(.34,.32,.265,1)
p=material.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.9;p.inputs['Metallic'].default_value=0
for n in material.node_tree.nodes:
 if n.type=='VALTORGB':
  for i,e in enumerate(n.color_ramp.elements):e.color=(*[v*(.88 if i==0 else 1.02) for v in (.34,.32,.265)],1)
for name in ['Condenser passage','Lower landing','Lift lower passage','Lift branch']:
 o=bpy.data.objects[name];o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(material)
bpy.context.scene.name='FACILITY_A09_ACCESS_FINISH'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_walkthrough_A09_access_finish.blend'),compress=True)
for name in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE']:bpy.data.collections[name].hide_viewport=True
for name in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD','13_FINISHED_ACCESS_SCENERY']:bpy.data.collections[name].hide_viewport=False
bpy.context.scene.name='FACILITY_A09_ACCESS_FINISH_MASTER'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_master_A09_access_finish.blend'),compress=True)
print('A09_ACCESS_FINISH_SAVED',flush=True)
