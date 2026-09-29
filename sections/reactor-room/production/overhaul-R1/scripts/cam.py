import bpy,sys,time,math
from mathutils import Vector
def shoot(name,loc,target,out,lens=22,res=(960,540),samples=12):
    sc=bpy.context.scene
    cd=bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=200
    co=bpy.data.objects.new(name,cd); sc.collection.objects.link(co)
    co.location=loc; co.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
    sc.camera=co; sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=samples; sc.cycles.use_denoising=True
    sc.render.resolution_x,sc.render.resolution_y=res; sc.render.resolution_percentage=100
    sc.render.filepath=out; t=time.time(); bpy.ops.render.render(write_still=True); print("done",name,round(time.time()-t),flush=True)
    bpy.data.objects.remove(co)
