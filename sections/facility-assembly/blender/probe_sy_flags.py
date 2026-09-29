import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[3];out=root/'runtime/out/spawn-integration'
targets=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('SY |') and not o.hide_render]
def ray(p,d):
    p=Vector(p);d=Vector(d);hits=[]
    for o in targets:
        inv=o.matrix_world.inverted()
        try:hit,loc,n,face=o.ray_cast(inv@p,inv.to_3x3()@d,distance=2)
        except RuntimeError:continue
        if hit:hits.append(((o.matrix_world@loc-p).length,o.name,list(o.matrix_world@loc)))
    return sorted(hits)[:4]
r={}
for name in ['SY | Canopy wall anchor','SY | Canopy wall anchor.001']:
    o=bpy.data.objects[name];p=o.matrix_world.translation;r[name]=ray((p.x,13,p.z),(0,-1,0))
for name in ['SY | Dimensional courtyard slab.058','SY | Dimensional courtyard slab.059','SY | Cliff-foot boulder 0']:
    o=bpy.data.objects[name];pts=[o.matrix_world@Vector(p) for p in o.bound_box];x=(min(p.x for p in pts)+max(p.x for p in pts))/2;y=(min(p.y for p in pts)+max(p.y for p in pts))/2;r[name]=ray((x,y,1),(0,0,-1))
(out/'flag-probes.json').write_text(json.dumps(r,indent=2));print('FLAG_PROBES',r,flush=True)
