import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
f='/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock/revamp/production/checkpoints/full-f12-interrupted.blend'
with bpy.data.libraries.load(f,link=False) as (src,dst):dst.scenes=[n for n in src.scenes if n=='COMPLIANCE_EDIT_LOCAL']
s=next(x for x in bpy.data.scenes if x.name.startswith('COMPLIANCE_EDIT_LOCAL'))
if bpy.context.window:bpy.context.window.scene=s
bpy.context.view_layer.update()
def tree(o):
 v=[o.matrix_world@x.co for x in o.data.vertices];f=[list(x.vertices) for x in o.data.polygons]
 return BVHTree.FromPolygons(v,f,all_triangles=False)
body=tree(s.objects['Lead tunnel main body']); out=[]
for nm in ['Tunnel stiffener 5.42_6.8','Tunnel stiffener 3.88_6.8']:
 rib=tree(s.objects[nm]);east='5.42_' in nm;sign=1 if east else -1;xout=6 if east else 3
 for z in [.90,1.20,1.50,1.80,1.95,1.98,2.00,2.01,2.03,2.06]:
  y=6.8
  hb=body.ray_cast(Vector((xout,y,z)),Vector((-sign,0,0)),3)
  hr=rib.ray_cast(Vector((xout,y,z)),Vector((-sign,0,0)),3)
  out.append({'rib':nm,'z':z,'body_hit_x':round(hb[0].x,6) if hb[0] else None,'rib_outer_hit_x':round(hr[0].x,6) if hr[0] else None,'body_minus_rib_outer_abs_m':round(abs(hb[0].x-hr[0].x),6) if hb[0] and hr[0] else None})
Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock/revamp/production/probes/f12-luna-preflight/failed_rib_ray_measurements.json').write_text(json.dumps(out,indent=2))
for r in out:print(r)
