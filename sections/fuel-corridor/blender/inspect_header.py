import bpy,json
s=bpy.context.scene
for name in ['REACTOR_BOUNDARY_type','REACTOR_BOUNDARY_direction_panel']:
 o=s.objects[name]
 print(json.dumps({'name':name,'type':o.type,'materials':[m.name for m in o.data.materials],'slots':[(m.link,m.material.name if m.material else None) for m in o.material_slots],'matrix':[list(r) for r in o.matrix_world],'format':sorted(set(x.material_index for x in o.data.body_format)) if o.type=='FONT' else []}))
 for m in o.data.materials:
  n=m.node_tree.nodes.get('Principled BSDF')
  print(m.name,list(n.inputs['Base Color'].default_value),n.inputs['Emission Strength'].default_value)
