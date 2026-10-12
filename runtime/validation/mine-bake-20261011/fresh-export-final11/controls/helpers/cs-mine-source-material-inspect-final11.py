import bpy,json
from pathlib import Path
report=[]
for obj in bpy.context.scene.objects:
 if obj.type!='MESH' or not any(x in obj.name.lower() for x in ['floor','beam','timber','plank']):continue
 if not any(s.material and s.material.name.startswith(('R39','R38')) for s in obj.material_slots):continue
 report.append({'name':obj.name,'objectLibrary':str(obj.library.filepath) if obj.library else None,'dataLibrary':str(obj.data.library.filepath) if obj.data.library else None,'materials':[{'name':s.material.name,'slotLink':s.link,'library':str(s.material.library.filepath) if s.material.library else None,'nodes':[(n.type,n.name) for n in s.material.node_tree.nodes if n.type in ['BSDF_PRINCIPLED','BSDF_DIFFUSE','GROUP','OUTPUT_MATERIAL']]} for s in obj.material_slots if s.material]})
Path('/tmp/cs-mine-source-material-inspect-final11.json').write_text(json.dumps(report,indent=2))
print('CS_SOURCE_MATERIAL_INSPECT',len(report))
