from pathlib import Path
s=Path('/tmp/cs-mine-aov-linked-context-final11.py').read_text().replace('/tmp/cs-mine-aov-linked-context-final11','/tmp/cs-mine-source-geometry-position-final11')
s=s.replace("for name,(eye,target,lens) in views.items():", """m=next(m for m in bpy.data.materials if m.name=='R39 | Riveted duct iron');nt=m.node_tree
translation=scene.objects['ROOM_mine'].matrix_world.translation
for node in list(nt.nodes):
 if node.type=='NEW_GEOMETRY' and node.outputs['Position'].is_linked:
  links=list(node.outputs['Position'].links);offset=nt.nodes.new('ShaderNodeVectorMath');offset.operation='ADD';offset.inputs[1].default_value=-translation;nt.links.new(node.outputs['Position'],offset.inputs[0])
  for link in links:nt.links.new(offset.outputs[0],link.to_socket)
records['diagnosticWorldPositionOffset']=list(-translation)
for name,(eye,target,lens) in views.items():
 if name!='R39_02_TUNNEL':continue""")
Path('/tmp/cs-mine-source-geometry-position-render-final11.py').write_text(s)
