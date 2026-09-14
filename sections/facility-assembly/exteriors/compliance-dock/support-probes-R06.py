import bpy,json
from pathlib import Path
from mathutils import Vector
out=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(out/'exterior-R06.blend'),load_ui=False)
dg=bpy.context.evaluated_depsgraph_get()
def bound(name):
 ob=bpy.data.objects[name];eo=ob.evaluated_get(dg);pts=[eo.matrix_world@Vector(p) for p in eo.bound_box]
 return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
rows=[]
for prop,support,axis in [('Marker holder attachment','Inspection station backing',1),('Marker holder attachment.001','Inspection station backing',1),('Marker holder','Marker holder attachment',1),('Marker holder','Inspection station backing',1),('Clipboard fibre board','Inspection station backing',1),('Inspection sheet','Clipboard fibre board',1),('Stamp rubber base','Permit stamp shelf',2),('Permit stamp shelf','Inspection station backing',1)]:
 a,b=bound(prop),bound(support);rows.append({'prop':prop,'presumed_support':support,'axis':axis,'signed_aabb_gap_m':a[0][axis]-b[1][axis],'scope':'Presumed support; axis AABB gap only, not full raycast/anchor/contact validation'})
(out/'support-probes-R06.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))


