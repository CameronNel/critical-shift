import bpy,sys,math; sys.path.insert(0,"."); from r2lib import *; from lib import col,box
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w21.blend"); sc=bpy.context.scene
st=bpy.data.objects["REACTOR_STATE"]; LC="25 LIGHTING"
def drv(idt,path,idx,expr):
    fc=idt.driver_add(path,idx) if idx is not None else idt.driver_add(path)
    d=fc.driver; d.type='SCRIPTED'; v=d.variables.new(); v.name='s'; v.type='SINGLE_PROP'; v.targets[0].id=st; v.targets[0].data_path='["stability"]'; d.expression=expr
def broken(a,b): return f"(1 if sin(frame*{a})*sin(frame*{b})>-0.30 else 0.04)*(0.92+0.08*sin(frame*3.1))"
def hum(p): return f"(0.9+0.1*sin(frame*2.7+{p}))"
# 1. remove the old ordinary practicals (keep pool/state/LP rig)
rm=0
for o in list(bpy.data.objects):
    if o.type=='LIGHT' and not o.name.startswith(("LP ","Reactor state key")) and not any(k in o.name.lower() for k in ("pool","cyan","core")):
        bpy.data.objects.remove(o,do_unlink=True); rm+=1
print("old practicals removed:",rm)
# 2. wall-washer fixtures on the cornice
AMB=bpy.data.materials.new("R2 lamp amber"); AMB.use_nodes=True; b=AMB.node_tree.nodes["Principled BSDF"]; b.inputs['Base Color'].default_value=(0.6,0.3,0.05,1); b.inputs['Emission Color'].default_value=(1.0,0.5,0.15,1); b.inputs['Emission Strength'].default_value=5
LAV=bpy.data.materials.new("R2 lamp lavender"); LAV.use_nodes=True; b=LAV.node_tree.nodes["Principled BSDF"]; b.inputs['Base Color'].default_value=(0.3,0.25,0.6,1); b.inputs['Emission Color'].default_value=(0.6,0.5,1.0,1); b.inputs['Emission Strength'].default_value=5
iron=bpy.data.materials["R2 iron"]; k=0; A=Acc()
for w in WALLS:
    us=[3.0,9.0] if w.L>10 else [w.L/2]
    if w.i==6: us=[1.5,10.5]           # west wall: flank the main door
    if w.i==4: us=[1.5,10.5]           # north wall: flank the fuel door
    if w.i==1: us=[0.9,w.L-0.9]        # SE diagonal: flank the cooling door
    for u in us:
        k+=1; amber=(k%3!=0); p=w.pt(u,0.55)
        A.box(("fixtures","R2 iron"),p.x,p.y,13.85,14.25,0.5,0.34,w.angle,0.03)
        q=w.pt(u,0.55+0.19)
        A.box(("fix lamp "+("amber" if amber else "lavender"),"AMB" if amber else "LAV"),q.x,q.y,13.9,14.15,0.42,0.02,w.angle,0.005)
        tgt=w.pt(u,0.0); z0=6.0
        ld=bpy.data.lights.new(f"LP wash {w.i}_{k}",'SPOT'); ld.spot_size=math.radians(70); ld.spot_blend=0.6; ld.shadow_soft_size=0.3
        ld.color=(1.0,0.52,0.18) if amber else (0.62,0.5,1.0)
        base=3000 if amber else 2200; ld.energy=base
        o=bpy.data.objects.new(f"LP wash {w.i}_{k}",ld); col(LC).objects.link(o); o.location=(p.x,p.y,14.0)
        o.rotation_euler=(Vector((tgt.x,tgt.y,z0))-o.location).to_track_quat('-Z','Y').to_euler()
        if k%5==0: drv(ld,"energy",None,f"{base}*{broken(1.7+0.43*k,0.6+0.21*k)}")
        elif k%7==0: ld.energy=base*0.03
        else: drv(ld,"energy",None,f"{base}*{hum(k)}")
mats={"R2 iron":iron,"AMB":AMB,"LAV":LAV}
# Acc.build wants a mats dict keyed by the second key element
A.build("22 R2 ARCHITECTURE","R2 lights",mats)
# 3. state light balance: reactor should glow, not flood
for o in bpy.data.objects:
    if o.type!='LIGHT': continue
    if o.name=="Reactor state key":
        for d in o.data.animation_data.drivers:
            if d.data_path=="energy": d.driver.expression="1800*(1+0.6*(1-s))*(1+0.18*sin(frame*(0.15+0.5*(1-s))))"
    if o.name=="LP reactor fill low":
        for d in o.data.animation_data.drivers:
            if d.data_path=="energy": d.driver.expression="300*(1+0.6*(1-s))*(1+0.18*sin(frame*(0.15+0.5*(1-s))))"
sc.view_settings.exposure=0.0
bpy.ops.wm.save_as_mainfile(filepath=S+"/w22.blend"); print("ok")
