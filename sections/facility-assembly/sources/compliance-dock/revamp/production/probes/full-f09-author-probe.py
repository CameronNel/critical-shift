import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
root=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock')
source=root/'module_overhaul_R1.blend'
before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
s=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL'];bpy.context.window.scene=s
rows=[]
for o in s.objects:
    if o.type not in {'MESH','FONT','LIGHT'}:continue
    if not any(t.lower() in o.name.lower() for t in ['scanner','lead tunnel','office side','manifest','floor slab','lead curtain','check-in','checkin','office task','support concealed','office rear','specimen','reassurance','printed']):continue
    points=[o.matrix_world@Vector(p) for p in o.bound_box] if o.type!='LIGHT' else []
    row=dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,bounds=[[min(v[k] for v in points) for k in range(3)],[max(v[k] for v in points) for k in range(3)]] if points else None,materials=[m.name if m else None for m in o.data.materials] if o.type!='LIGHT' else [],matrix=[list(r) for r in o.matrix_world],component_names=o.get('component_names'))
    if o.type=='FONT':row.update(body=o.data.body,size=o.data.size)
    if o.type=='LIGHT':row.update(energy=o.data.energy,size=getattr(o.data,'size',None),spread=getattr(o.data,'spread',None))
    rows.append(row)
after=hashlib.sha256(source.read_bytes()).hexdigest();assert before==after
out=root/'revamp/production/probes/full-f09-author-plan.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(dict(source_sha256=before,source_unchanged=True,rows=rows),indent=2)+'\n')
print('AUTHOR_READ_ONLY_BOUNDS',len(rows),flush=True)
