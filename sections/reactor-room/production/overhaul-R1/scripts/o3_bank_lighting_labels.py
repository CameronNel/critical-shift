import bpy,sys,math; sys.path.insert(0,"."); from lib import col; from mathutils import Vector
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w27.blend")
for o in bpy.data.objects:
    if o.type=='FONT' and o.name.startswith("R2 bank") and "label" in o.name: o.rotation_euler=(math.pi/2,0,0)
    if o.type=='MESH' and "state ring" in o.name:
        bx=-1.4 if " A " in o.name else 1.4
        for v in o.data.vertices: v.co.x=bx+(v.co.x-bx)*1.05; v.co.y*=1.05
st=bpy.data.objects["REACTOR_STATE"]
def spot(name,loc,tgt,energy,color,size,blend=0.5,flick=None):
    ld=bpy.data.lights.new(name,'SPOT'); ld.spot_size=size; ld.spot_blend=blend; ld.energy=energy; ld.color=color; ld.shadow_soft_size=0.2
    o=bpy.data.objects.new(name,ld); col("25 LIGHTING").objects.link(o); o.location=loc; o.rotation_euler=(Vector(tgt)-o.location).to_track_quat('-Z','Y').to_euler()
    if flick:
        fc=ld.driver_add("energy"); d=fc.driver; d.type='SCRIPTED'; d.expression=f"{energy}*(1 if sin(frame*{flick})*sin(frame*{flick*0.37})>-0.3 else 0.05)"
    return o
for tag,bx,c in (("A",-1.4,(1.0,0.55,0.20)),("B",1.4,(0.62,0.5,1.0))):
    spot(f"LP bank {tag} uplight",(bx,-3.75,1.3),(bx,-0.4,11.2),22000,c,math.radians(20))
    spot(f"LP bank {tag} gantry lamp",(bx,2.6,13.35),(bx,0,10.4),4500,(0.9,0.85,1.0),math.radians(55),0.6,flick=1.9+0.6*(bx>0))
bpy.ops.wm.save_as_mainfile(filepath=S+"/w27.blend"); print("ok")
