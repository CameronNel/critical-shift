import bpy,json
s=bpy.context.scene
for name in ['Floor','Continuous inner vessel','Terminal rear casing','Connected filter plenum']:
 o=bpy.data.objects.get(name)
 if not o:continue
 print('DIAG',name,[(m.name,list(m.diffuse_color),[(n.type,list(n.inputs['Base Color'].default_value)) for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED']) for m in o.data.materials])
for m in [bpy.data.materials['Dry charcoal ground concrete'],bpy.data.materials['Structural warm graphite']]:
 print('LINKS',m.name,[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links])
print('SCENE',s.view_settings.exposure,s.view_settings.view_transform,s.world.node_tree.nodes['Background'].inputs[1].default_value)
