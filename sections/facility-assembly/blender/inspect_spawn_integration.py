"""Read-only saved-scene inventory for PR48 integration; no .blend writes."""
import bpy,json,ctypes
from pathlib import Path
from mathutils import Vector
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
root=Path(__file__).resolve().parents[3]
out=root/'runtime/out/spawn-integration';out.mkdir(parents=True,exist_ok=True)
def row(o):
    pts=[o.matrix_world@Vector(p) for p in o.bound_box]
    return dict(name=o.name,type=o.type,library=o.library.filepath if o.library else None,
        collections=[c.name for c in o.users_collection],parent=o.parent.name if o.parent else None,
        instance=o.instance_collection.name if o.instance_collection else None,
        matrix=[list(v) for v in o.matrix_world],hide_render=o.hide_render,hide_viewport=o.hide_viewport,
        lo=[min(p[i] for p in pts) for i in range(3)],hi=[max(p[i] for p in pts) for i in range(3)],
        mats=[s.material.name if s.material else None for s in o.material_slots])
module=Path(bpy.data.filepath).name=='module.blend'
objs=[row(o) for o in bpy.data.objects if module or o.name.startswith('SY |') or any(k in o.name.lower() for k in ('spawn','reactor','connection','stair','access','medical'))]
data=dict(file=bpy.data.filepath,objects=objs,collections=[dict(name=c.name,library=c.library.filepath if c.library else None,children=[x.name for x in c.children],objects=len(c.objects),hide_render=c.hide_render,hide_viewport=c.hide_viewport) for c in bpy.data.collections],libraries=[l.filepath for l in bpy.data.libraries])
dest=out/('module-inspection.json' if module else 'environment-inspection.json');dest.write_text(json.dumps(data,indent=2));print('INSPECTION',dest,len(objs),flush=True)
