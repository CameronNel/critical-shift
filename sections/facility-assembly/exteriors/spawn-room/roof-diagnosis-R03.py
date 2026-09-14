import bpy,json
from mathutils import Vector
from pathlib import Path
out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out/'exterior-R03.blend'),load_ui=False)
def val(ob,n):
 try:
  v=getattr(ob,n);return v if isinstance(v,(str,float,bool,int)) else str(v)
 except:return None
lights=[]
for ob in bpy.data.objects:
 if ob.type!='LIGHT':continue
 d=ob.data
 lights.append({'name':ob.name,'location':list(ob.matrix_world.translation),'type':d.type,'energy':d.energy,'properties':{p.identifier:val(d,p.identifier) for p in d.bl_rna.properties if any(t in p.identifier for t in ['shadow','diffuse','specular','volume','spread'])},'cycles':{p.identifier:val(d.cycles,p.identifier) for p in d.cycles.bl_rna.properties},'linking':{'receiver_collection':str(ob.light_linking.receiver_collection),'blocker_collection':str(ob.light_linking.blocker_collection)}})
roofs=[]
for ob in bpy.data.objects:
 if ob.type=='MESH' and any(t in ob.name.lower() for t in ['roof','ceiling','membrane']):
  roofs.append({'name':ob.name,'location':list(ob.matrix_world.translation),'bounds':[list(p) for p in ob.bound_box],'visibility':{n:val(ob,n) for n in ['visible_camera','visible_shadow','visible_diffuse','visible_glossy','visible_transmission','visible_volume_scatter','hide_render']},'materials':[{'name':m.name,'nodes':[{'type':n.type,'name':n.name,'inputs':{i.name:str(i.default_value) for i in n.inputs if hasattr(i,'default_value') and i.name in ['Alpha','Emission Color','Emission Strength','Transmission Weight']}} for n in m.node_tree.nodes] if m.use_nodes else []} for m in ob.data.materials if m]})
blockers=[]
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
for light in bpy.data.objects:
 if light.type!='LIGHT' or light.data.use_shadow:continue
 for roof in bpy.data.objects:
  if roof.type!='MESH' or 'opaque roof membrane' not in roof.name:continue
  eo=roof.evaluated_get(dg);inv=eo.matrix_world.inverted();hit,loc,normal,face=eo.ray_cast(inv@light.matrix_world.translation,inv.to_3x3()@Vector((0,0,1)))
  if hit:blockers.append({'light':light.name,'blocker':roof.name,'upward_ray_hit_world':list(eo.matrix_world@loc),'roof_shadow_visible':roof.visible_shadow,'light_use_shadow':light.data.use_shadow})
r={'blocker_rays':blockers,'lights':lights,'roofs':roofs};(out/'roof-diagnosis-R03.json').write_text(json.dumps(r,indent=2));print(json.dumps(blockers,indent=2))

