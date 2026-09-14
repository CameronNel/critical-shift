"""R08 -> R09: approved warm exterior rock finish and quiet distant backdrop."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'production/spawn-exterior-review'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_spawn_concept02_R08.blend'),load_ui=False)
# The visible upper mountain is exterior context in approved Concept02. Material-only local copy.
m=bpy.data.materials.new('S01 warm broad-plane exterior stone');m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.92
geo=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.65;noise.inputs['Detail'].default_value=.5
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT';ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
for i,(position,color) in enumerate([(0,(.22,.16,.105,1)),(.34,(.31,.23,.145,1)),(.50,(.38,.29,.185,1)),(.66,(.46,.35,.23,1))]):
 e=ramp.color_ramp.elements[0] if i==0 else ramp.color_ramp.elements.new(position);e.position=position;e.color=color
m.node_tree.links.new(geo.outputs['Position'],noise.inputs['Vector']);m.node_tree.links.new(noise.outputs['Fac'],ramp.inputs['Fac']);m.node_tree.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
changed=[]
for c in list(bpy.data.collections):
 if not c.name.startswith('EXT_LIGHTING_'):continue
 for ob in list(c.objects):
  if ob.name=='CSM_Mountain_upper_mass':
   cp=ob.copy();cp.name='S01 exterior upper mountain material override';c.objects.unlink(ob);c.objects.link(cp)
   for sl in cp.material_slots:sl.link='OBJECT';sl.material=m
   changed.append(cp.name)
# A distant haze silhouette has no hard light facets or competing detail.
terrain=bpy.data.objects['Non-walkable distant landscape'];mat=bpy.data.materials.new('S01 distant blue haze');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear();out=nodes.new('ShaderNodeOutputMaterial');em=nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.32,.43,.52,1);em.inputs['Strength'].default_value=.7;mat.node_tree.links.new(em.outputs[0],out.inputs['Surface']);terrain.data.materials.clear();terrain.data.materials.append(mat)
for poly in terrain.data.polygons:poly.material_index=0
s=bpy.context.scene;s.name='FACILITY_SPAWN_CONCEPT02_R09';dest=R/'blender/facility_spawn_concept02_R09.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
b=json.loads((O/'BUILD_R08.json').read_text());b.update(revision='R09',file=str(dest),context_material_only=changed,context_note='Upper exterior mountain material only, as shown in approved concept. Original geometry, footprint and source library preserved; mine interior surfaces untouched.');(O/'BUILD_R09.json').write_text(json.dumps(b,indent=2));print('R09_SAVED',changed,flush=True)
