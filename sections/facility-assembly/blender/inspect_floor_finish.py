import bpy,json,hashlib,ctypes
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3];out=root/'runtime/out/environment/floor-finish';out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();rows=[];mats=set()
for o in s.objects:
 if o.type!='MESH' or not o.name.startswith(('CY |','RFX |')):continue
 bb=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(v[i] for v in bb) for i in range(3)];hi=[max(v[i] for v in bb) for i in range(3)]
 if hi[2]>.32 or lo[2]<-.5:continue
 rows.append(dict(name=o.name,lo=lo,hi=hi,location=list(o.location),scale=list(o.scale),materials=[m.name for m in o.data.materials],verts=len(o.data.vertices),faces=len(o.data.polygons),overlay=bool(o.get('intentional_surface_overlay'))))
 mats.update(m.name for m in o.data.materials)
materials={}
for name in mats:
 m=bpy.data.materials[name];materials[name]=dict(colour=list(m.diffuse_color),nodes=[dict(name=n.name,type=n.type,parent=n.parent.name if n.parent else None,inputs={i.name:list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value for i in n.inputs if hasattr(i,'default_value') and i.name in ('Roughness','Metallic','Base Color','Scale','Distance','Strength','To Min','To Max')},ramp=[list(e.color) for e in n.color_ramp.elements] if n.type=='VALTORGB' else None) for n in m.node_tree.nodes] if m.use_nodes else [])
(out/'inspection.json').write_text(json.dumps(dict(source=bpy.data.filepath,sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),objects=rows,materials=materials),indent=2));print('FLOORS_INSPECTED',len(rows),flush=True)
