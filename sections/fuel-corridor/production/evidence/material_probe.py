import bpy
for name in ['cotton','glove']:
 m=bpy.data.materials[name]
 print(name)
 for node in m.node_tree.nodes:
  if node.type=='VALTORGB':print([(e.position,list(e.color)) for e in node.color_ramp.elements])
 print([(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links])
 p=m.node_tree.nodes.get('Principled BSDF');print([(i.name,str(i.default_value)) for i in p.inputs if i.name in ['Weight','Emission Color','Emission Strength','Base Color','Roughness','Metallic','Specular IOR Level']])
