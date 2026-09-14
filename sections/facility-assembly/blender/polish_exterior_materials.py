"""Assembly-local exterior material overrides and coherent daylight."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'connections/exterior-final'
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/facility_walkthrough_A14_exterior.blend'),load_ui=False)
cache={};count=0

def material(m):
 if m is None:return None
 if m.as_pointer() in cache:return cache[m.as_pointer()]
 n=m.copy();n.name='A14 Exterior '+m.name;cache[m.as_pointer()]=n
 low=m.name.lower()
 if n.use_nodes:
  p=n.node_tree.nodes.get('Principled BSDF')
  if p:
   if any(k in low for k in ['concrete','mineral','plaster','panel','plinth']):
    p.inputs['Roughness'].default_value=.86
    for node in n.node_tree.nodes:
     if node.type=='VALTORGB':
      for el in node.color_ramp.elements:
       col=el.color;el.color=(col[0]*1.03,col[1]*1.01,col[2]*.97,col[3])
   elif 'steel' in low:p.inputs['Roughness'].default_value=.57
 return n

def clone(c):
 global count
 new=bpy.data.collections.new('A14_'+c.name)
 for ob in c.objects:
  cp=ob.copy();new.objects.link(cp)
  if cp.type=='MESH':
   for slot in cp.material_slots:
    m=slot.material;slot.link='OBJECT';slot.material=material(m)
   count+=1
 for ch in c.children:new.children.link(clone(ch))
 return new
for inst in bpy.data.collections['06_LINKED_EXTERIORS'].objects:
 if inst.instance_collection:inst.instance_collection=clone(inst.instance_collection)
for ob in bpy.data.collections['07_FAST_WALKTHROUGH_PROXIES'].objects:
 if 'EXTERIOR_INSTANCE' in ob.name:
  for i,m in enumerate(ob.data.materials):ob.data.materials[i]=material(m)
# A physical sky replaces the flat backdrop; one matched sun supplies direction.
w=bpy.data.worlds.new('A14 coherent outdoor daylight');w.use_nodes=True;scene=bpy.context.scene;scene.world=w;nodes=w.node_tree.nodes;bg=nodes.get('Background');sky=nodes.new('ShaderNodeTexSky');sky.sky_type='MULTIPLE_SCATTERING';sky.sun_elevation=.65;sky.sun_rotation=2.4;sky.sun_disc=False;sky.altitude=.2;sky.air_density=1.;sky.aerosol_density=.55;bg.inputs['Strength'].default_value=.20;w.node_tree.links.new(sky.outputs['Color'],bg.inputs['Color'])
for ob in bpy.data.objects:
 if ob.type=='LIGHT' and ob.data.type=='SUN':ob.data.energy=3.2;ob.data.color=(1,.91,.78);ob.data.angle=.08
scene.view_settings.exposure=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_walkthrough_A14_exterior.blend'),compress=True)
for name in ['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE','18_REACTOR_FINISH_VIEWPORT_CACHE','21_ROOF_SERVICE_VIEWPORT_CACHE','23_EXTERIOR_FINISH_VIEWPORT_CACHE']:bpy.data.collections[name].hide_viewport=True
for name in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','09_FINISHED_HORIZONTAL_CONNECTIONS','CONNECTION_C01_RESCUE_COURTYARD','13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY','17_REACTOR_EXTERIOR_FINISH','20_ROOF_SERVICE_GEOMETRY','22_EXTERIOR_FINISH_GEOMETRY']:bpy.data.collections[name].hide_viewport=False
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/facility_master_A14_exterior.blend'),compress=True)
(O/'MATERIALS.json').write_text(json.dumps({'assembly_exterior_objects':count,'local_material_overrides':len(cache),'source_files_modified':False,'sky':'Multiple-scattering physical sky, matched warm sun'},indent=2));print('A14_MATERIALS_SAVED',count,len(cache),flush=True)

