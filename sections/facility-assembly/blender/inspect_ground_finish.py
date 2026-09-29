"""Read-only inventory for the roof-excluded finish correction."""
import bpy,json,hashlib,ctypes
from pathlib import Path
from mathutils import Vector
from collections import Counter
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3];out=root/'runtime/out/environment/ground-finish';out.mkdir(parents=True,exist_ok=True)
src=Path(bpy.data.filepath);s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box];return [[round(f(v[i] for v in p),4) for i in range(3)] for f in (min,max)]
objects=[];used=set()
for o in s.objects:
 if o.type not in {'MESH','FONT','LIGHT'}:continue
 b=bounds(o)
 if not (o.name.startswith(('FLR |','MEX |')) or (b[1][0]>-50 and b[0][0]<-19 and b[1][1]>-48 and b[0][1]<-23 and b[0][2]<8)):continue
 if o.type=='MESH':
  mats=[m.name_full if m else '' for m in o.data.materials];counts=Counter(p.material_index for p in o.data.polygons)
  used.update(mats);q=dict(name=o.name_full,bounds=b,library=str(o.library.filepath) if o.library else None,collections=[c.name for c in o.users_collection],verts=len(o.data.vertices),faces=len(o.data.polygons),materials={mats[i]:n for i,n in counts.items() if i<len(mats)})
 elif o.type=='FONT':q=dict(name=o.name,bounds=b,text=o.data.body,materials=[m.name for m in o.data.materials]);used.update(q['materials'])
 else:q=dict(name=o.name,position=list(o.matrix_world.translation),energy=o.data.energy,color=list(o.data.color),kind=o.data.type)
 objects.append(q)
materials={}
for m in bpy.data.materials:
 if m.name_full not in used:continue
 materials[m.name_full]=dict(users=m.users,nodes=[dict(name=n.name,type=n.bl_idname,parent=n.parent.name if n.parent else None,location=list(n.location),inputs={i.name:(list(i.default_value) if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else i.default_value) for i in n.inputs if hasattr(i,'default_value') and i.type in {'VALUE','RGBA','VECTOR','STRING'}},ramp=[(e.position,list(e.color)) for e in n.color_ramp.elements] if n.type=='VALTORGB' else None,image=n.image.name if n.type=='TEX_IMAGE' and n.image else None) for n in m.node_tree.nodes] if m.use_nodes else [],links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links] if m.use_nodes else [])
r=dict(source=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),objects=objects,materials=materials)
(out/'inspection.json').write_text(json.dumps(r,indent=2));print('INSPECTION_COMPLETE',len(objects),len(materials),flush=True)
