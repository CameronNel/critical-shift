"""Recover receiving/press silhouettes with weak existing practicals only."""
# The receiving bay was swallowed from the required reverse camera. Its actual
# overhead fixture limps on; a wall lamp fails instead. Six outages remain, with
# paired shader/source electrical states and unchanged physical fixture poses.
for key,energy in [('Ceiling pendant 0',50),('Wall service lamp 1',0),
                   ('Press task bar',60),('Mine threshold practical',60),('Personnel threshold practical',28)]:
 light=bpy.data.objects['RF1 LIGHT | '+key];light.data.energy=energy
 lens=bpy.data.objects[light['fixture_lens']]
 light['electrical_state']=lens['electrical_state']='weak' if energy else 'failed'
 for material in lens.data.materials:
  for node in material.node_tree.nodes:
   if node.type=='BSDF_PRINCIPLED':
    node.inputs['Base Color'].default_value=(.12,.145,.102,1) if energy else (.043,.055,.044,1)
    node.inputs['Emission Color'].default_value=(*light.data.color,1)
    node.inputs['Emission Strength'].default_value=.30 if energy else 0
outages=[]
for light in s.objects:
 if light.type=='LIGHT' and light.data.energy==0:
  outages.append(dict(light=light.name,lens=light['fixture_lens'],energy=0,shader_emission=0))
assert len(outages)==6
s['failed_fixture_registry']=json.dumps(outages)
bpy.context.view_layer.update()
