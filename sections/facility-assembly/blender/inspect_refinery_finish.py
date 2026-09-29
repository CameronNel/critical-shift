import bpy,json,hashlib,ctypes
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3]; out=root/'runtime/out/environment/refinery-finish';out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
rows=[]
for x,y in [(x,y) for x in (3.4,4.5,6,8) for y in (-25,-22,-19,-16,-13,-10)]+[(x,-25.6) for x in (-9,-6,-3,0,2)]+[(-12,y) for y in (-23,-19,-15,-11)]:
 p=Vector((x,y,.45)); hits=[]
 for i in range(12):
  hit,co,n,fi,o,m=s.ray_cast(dg,p,Vector((0,0,-1)),distance=1)
  if not hit:break
  hits.append(dict(name=o.name,z=co.z,normal=list(n),material=o.data.materials[o.data.polygons[fi].material_index].name if o.type=='MESH' and fi<len(o.data.polygons) and len(o.data.materials) else ''))
  p=co-Vector((0,0,.002))
 rows.append(dict(xy=[x,y],hits=hits))
objects=[]
for o in s.objects:
 if o.name.startswith('RFX |'):
  bb=[o.matrix_world@Vector(v) for v in o.bound_box];objects.append(dict(name=o.name,lo=[min(v[i] for v in bb) for i in range(3)],hi=[max(v[i] for v in bb) for i in range(3)],materials=[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []))
data=dict(source=str(Path(bpy.data.filepath)),sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),ground=rows,objects=objects,mine_materials=[dict(name=m.name,nodes=len(m.node_tree.nodes) if m.node_tree else 0) for m in bpy.data.materials if any(k in m.name.lower() for k in ('r39','gullet','mine','mud','asphalt'))])
(out/'inspection.json').write_text(json.dumps(data,indent=2));print('FINISH_INSPECTED',len(objects),flush=True)
