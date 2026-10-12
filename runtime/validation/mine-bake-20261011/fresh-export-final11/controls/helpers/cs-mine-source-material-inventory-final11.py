import bpy,json
from pathlib import Path
objects=[]
for obj in bpy.data.objects:
 if obj.type!='MESH' or not any(x in obj.name.lower() for x in ['floor','beam','timber','plank']):continue
 objects.append({'name':obj.name,'library':str(obj.library.filepath) if obj.library else None,'meshLibrary':str(obj.data.library.filepath) if obj.data.library else None,'materials':[{'name':s.material.name,'library':str(s.material.library.filepath) if s.material.library else None,'nodes':[n.type for n in s.material.node_tree.nodes]} for s in obj.material_slots if s.material and s.material.use_nodes]})
Path('/tmp/cs-mine-source-material-inventory-final11.json').write_text(json.dumps({'objects':objects,'materials': [{'name':m.name,'users':m.users,'library':str(m.library.filepath) if m.library else None,'nodes':[n.type for n in m.node_tree.nodes] if m.use_nodes else []} for m in bpy.data.materials]},indent=2));print('CS_INVENTORY',len(objects))
