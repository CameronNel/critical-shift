import bpy, json
from mathutils import Vector
s=bpy.context.scene; d=bpy.context.evaluated_depsgraph_get()
out=[]
for x,y in [(5.9,2),(5.9,3),(5.9,4),(5.9,5),(5.9,6),(.55,3),(.55,4),(.55,5),(2,5.845),(3,5.845),(4,5.845)]:
    hit,loc,n,idx,o,m=s.ray_cast(d,Vector((x,y,4.23)),Vector((0,0,1)),distance=2.2)
    out.append({'xy':[x,y],'headroom':loc.z-4.205 if hit else None,'object':o.name if hit else None})
print('GALLERY_PROBE',json.dumps(out),flush=True)
for o in s.objects:
    if o.name.startswith(('roof','ceiling beam','gallery hanger','gal rail','gal post','hoist')):
        print(o.name, list(o.location),list(o.dimensions))
