import bpy,sys,math; sys.path.insert(0,"."); import palette5; from r2lib import *; from lib import col
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w23.blend"); sc=bpy.context.scene
print("palette5:",palette5.apply())
# thinner edge wear everywhere
n=0
for m in bpy.data.materials:
    if not m.use_nodes: continue
    for nd in m.node_tree.nodes:
        if nd.type=='MAP_RANGE' and abs(nd.inputs['From Min'].default_value-0.998)<0.01 and abs(nd.inputs['From Max'].default_value-0.93)<0.02: nd.inputs['From Max'].default_value=0.88; n+=1
        if nd.type=='MAP_RANGE' and abs(nd.inputs['From Min'].default_value-0.995)<0.01 and abs(nd.inputs['From Max'].default_value-0.90)<0.02: nd.inputs['From Max'].default_value=0.86; n+=1
print("edge masks thinned:",n)
# station task lamps: modelled caged lamp + spot
iron=bpy.data.materials["R2 iron"]
AMB=bpy.data.materials["R2 lamp amber"]; LAV=bpy.data.materials["R2 lamp lavender"]
st=bpy.data.objects["REACTOR_STATE"]
def drv(idt,path,expr):
    fc=idt.driver_add(path); d=fc.driver; d.type='SCRIPTED'; v=d.variables.new(); v.name='s'; v.type='SINGLE_PROP'; v.targets[0].id=st; v.targets[0].data_path='["stability"]'; d.expression=expr
A=Acc(); k=0
def lamp(x,y,z,tx,ty,tz,amber=True,energy=700,flick=False,name="station"):
    global k; k+=1; energy=energy*5.5
    A.box(("task lamp hood","R2 iron"),x,y,z,z+0.16,0.42,0.30,math.atan2(ty-y,tx-x),0.02)
    ang=math.atan2(ty-y,tx-x)
    A.box(("task lamp face "+("amber" if amber else "lav"),"AMB" if amber else "LAV"),x+math.cos(ang)*0.13,y+math.sin(ang)*0.13,z+0.02,z+0.13,0.02,0.34,ang,0.004)
    ld=bpy.data.lights.new(f"LP task {name} {k}",'SPOT'); ld.spot_size=math.radians(62); ld.spot_blend=0.55; ld.shadow_soft_size=0.15
    ld.color=(1.0,0.55,0.20) if amber else (0.65,0.55,1.0); ld.energy=energy
    o=bpy.data.objects.new(f"LP task {name} {k}",ld); col("25 LIGHTING").objects.link(o); o.location=(x,y,z+0.05)
    o.rotation_euler=(Vector((tx,ty,tz))-o.location).to_track_quat('-Z','Y').to_euler()
    if flick: drv(ld,"energy",f"{energy}*(1 if sin(frame*{1.3+0.3*k})*sin(frame*{0.5+0.17*k})>-0.3 else 0.05)")
# generator / reserve power (west wall)
lamp(-9.5,-4.6,3.4,-9.9,-3.6,1.0,True,700,name="generator"); lamp(-9.5,2.4,3.4,-9.8,0.5,0.9,False,600,True,name="reserve power")
# grid cabinets + turbine (east wall)
lamp(9.4,-0.6,3.3,10.2,-1.0,1.1,False,650,name="grid"); lamp(9.3,-4.9,3.6,9.6,-3.8,1.2,True,700,True,name="turbine")
# fuel bay and racks (north-west)
lamp(-3.4,8.3,3.5,-4.2,9.9,0.9,False,650,True,name="fuel"); lamp(-6.4,8.8,3.4,-5.0,9.9,1.0,True,500,name="fuel rack")
# waste cask
lamp(5.8,6.6,3.6,7.6,8.2,1.2,True,700,name="waste")
# pool-side console
lamp(-1.6,-2.4,3.0,-1.0,-3.8,0.9,False,350,True,name="console")
A.build("23 R2 FLOOR AND DRESSING","R2 lamps",{"R2 iron":iron,"AMB":AMB,"LAV":LAV})
bpy.ops.wm.save_as_mainfile(filepath=S+"/w24.blend"); print("ok")
