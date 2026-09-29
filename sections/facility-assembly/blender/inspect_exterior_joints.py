import bpy,json,hashlib,ctypes,re
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3];out=root/'runtime/out/environment/exterior-joints';out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();rows=[]
names=('ART | Refinery exterior process systems','ART | Refinery authored surface finish','ART | Courtyard mine-to-refinery')
for cn in names:
 c=bpy.data.collections.get(cn);assert c,cn
 for o in c.objects:
  if any(k in o.name for k in ('paint loss','corrosion','runoff','Localized joint oxidation','Localized worn dust','Contained ore','Boulder','boulder','Fieldstone','fieldstone')):continue
  bb=[o.matrix_world@Vector(v) for v in o.bound_box]
  rows.append(dict(name=o.name,collection=cn,type=o.type,location=list(o.location),rotation=list(o.rotation_euler),scale=list(o.scale),lo=[min(v[i] for v in bb) for i in range(3)],hi=[max(v[i] for v in bb) for i in range(3)],materials=[slot.material.name if slot.material else None for slot in o.material_slots],verts=len(o.data.vertices) if o.type=='MESH' else 0,hidden=o.hide_render,overlay=bool(o.get('intentional_surface_overlay'))))
(out/'inspection.json').write_text(json.dumps(dict(source=bpy.data.filepath,sha256=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),objects=rows),indent=2));print('JOINTS_INSPECTED',len(rows),flush=True)
