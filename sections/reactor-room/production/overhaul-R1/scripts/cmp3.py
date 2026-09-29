import bpy,sys,math
from mathutils import Vector
f=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=f); sc=bpy.context.scene
for o in sc.objects:
    if o.name.startswith("LP haze"): o.hide_viewport=True; o.hide_render=True
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
print("FILE",f.split("/")[-1])
# inner shell planes at z=11 (above stations, below roof, through hall centre column avoided by starting at r=8)
for z in (11.0,):
  for k in range(8):
    a=k*math.pi/4; o=Vector((8*math.cos(a),8*math.sin(a),z)); d=Vector((math.cos(a),math.sin(a),0))
    hit,loc,n,idx,ob,mat=sc.ray_cast(dg,o,d)
    print("  z=%.0f dir %3d -> hit r=%s  %s"%(z,round(math.degrees(a)),("%.2f"%math.hypot(loc.x,loc.y)) if hit else "none",ob.name[:36] if hit else ""))
for pt in ((6.5,6.5,1.0),(-6.5,6.5,1.0)):
    hit,loc,n,idx,ob,mat=sc.ray_cast(dg,Vector(pt),Vector((0,0,1))); print("  UP from",pt,"-> z=%.2f"%loc.z if hit else "none", ob.name[:34] if hit else "")
