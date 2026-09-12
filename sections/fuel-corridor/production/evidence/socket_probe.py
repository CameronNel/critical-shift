import bpy
p=bpy.data.materials['cotton'].node_tree.nodes.get('Principled BSDF')
print([(i,s.name,s.identifier,str(s.default_value)) for i,s in enumerate(p.inputs)])
