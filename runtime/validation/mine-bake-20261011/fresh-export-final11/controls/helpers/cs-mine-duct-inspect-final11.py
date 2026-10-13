import bpy,json
from pathlib import Path
m=next(m for m in bpy.data.materials if m.name=='R39 | Riveted duct iron')
r=[]
for n in m.node_tree.nodes:
 r.append({'name':n.name,'type':n.type,'properties':{k:getattr(n,k) for k in ('noise_dimensions','normalize','operation','vector_type','bump_strength','space') if hasattr(n,k)},'inputs':{i.name:{'default':list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value,'links':[(l.from_node.name,l.from_socket.name) for l in i.links]} for i in n.inputs if hasattr(i,'default_value')},'image':n.image.filepath if n.type=='TEX_IMAGE' and n.image else None})
Path('/tmp/cs-mine-duct-nodes-final11.json').write_text(json.dumps(r,indent=2));print('CS_DUCT_NODES',json.dumps(r))
