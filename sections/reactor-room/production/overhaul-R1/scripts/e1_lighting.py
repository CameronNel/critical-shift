import bpy,sys,math; sys.path.insert(0,"."); from lib import *
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w14.blend"); sc=bpy.context.scene
st=bpy.data.objects["REACTOR_STATE"]; LC="25 LIGHTING"
def drv(idt,path,idx,expr):
    fc=idt.driver_add(path,idx) if idx is not None else idt.driver_add(path)
    d=fc.driver; d.type='SCRIPTED'; v=d.variables.new(); v.name='s'; v.type='SINGLE_PROP'; v.targets[0].id=st; v.targets[0].data_path='["stability"]'; d.expression=expr
R="min(1,2*(1-s)+0.24)"; G="0.03+0.92*s"; B="0.20*s"
PULSE="(1+0.6*(1-s))*(1+0.18*sin(frame*(0.15+0.5*(1-s))))"
GATE="max(0,min(1,2.2*(1-s)-0.2))"
def state_color(idt,path):
    for i,e in enumerate((R,G,B)): drv(idt,path,i,e)
def broken(a,b): return f"(1 if sin(frame*{a})*sin(frame*{b})>-0.30 else 0.05)*(0.92+0.08*sin(frame*3.1))"
def hum(p): return f"(0.88+0.12*sin(frame*2.7+{p}))"
def aim(o,tgt): o.rotation_euler=(Vector(tgt)-o.location).to_track_quat('-Z','Y').to_euler()
def light(name,kind,loc,energy,color,tgt=None,size=None,spot=None,energy_expr=None,color_state=False):
    ld=bpy.data.lights.new(name,kind)
    if kind=='AREA': ld.shape='RECTANGLE'; ld.size=size[0] if size else 1.0; ld.size_y=size[1] if size else 1.0
    if kind=='SPOT': ld.spot_size=spot[0]; ld.spot_blend=spot[1]; ld.shadow_soft_size=0.25
    if kind=='POINT': ld.shadow_soft_size=0.3
    ld.energy=energy; ld.color=color
    o=bpy.data.objects.new(name,ld); col(LC).objects.link(o); o.location=loc
    if tgt: aim(o,tgt)
    if color_state: state_color(ld,"color")
    if energy_expr: drv(ld,"energy",None,energy_expr)
    return o
# 0. remove the old drivers on ordinary practicals and rebuild them: alternating sodium amber / cold lavender, some failing, some dead
n=0
for o in bpy.data.objects:
    if o.type!='LIGHT' or o.name.startswith(("LP ","Reactor state key")) : continue
    if any(k in o.name.lower() for k in ("pool","cyan","core")): continue
    L=o.data
    if L.animation_data: L.driver_remove("energy")
    n+=1; base=240 if L.type=='AREA' else (800 if L.type=='SPOT' else 220)
    L.color=(0.68,0.60,1.0) if n%3==0 else (1.0,0.55,0.20)
    if n%4==0: drv(L,"energy",None,f"{base}*{broken(1.9+0.41*n,0.7+0.23*n)}")
    elif n%9==0: L.energy=base*0.03
    else: drv(L,"energy",None,f"{base}*{hum(n)}")
print("practicals rebuilt:",n)
# stronger pool: emission + key + wide fill
bpy.data.materials["pool_glow"].node_tree.animation_data  # keep drivers
for d in bpy.data.materials["pool_glow"].node_tree.animation_data.drivers:
    if "Emission Strength" in d.data_path: d.driver.expression="3.4*"+PULSE
kl=bpy.data.objects["Reactor state key"].data; 
for d in kl.animation_data.drivers:
    if d.data_path=="energy": d.driver.expression="3200*"+PULSE
# 1. reactor beam (state coloured) + wide fill
light("LP reactor beam","SPOT",(0,0,0.8),5500,(0.3,1,0.3),tgt=(0,0,12),spot=(0.62,0.85),energy_expr="5500*"+PULSE,color_state=True)
light("LP reactor fill low","POINT",(0,0,2.2),700,(0.3,1,0.3),energy_expr="700*"+PULSE,color_state=True)
# 2. cold roof shafts
for i,(x,y,tx,ty) in enumerate(((5,4,3.5,2.5),(-4,6,-2.5,4),(4,-6,2.5,-4))):
    light(f"LP roof shaft {i}","SPOT",(x,y,13.6),6500,(0.55,0.58,1.0),tgt=(tx,ty,0),spot=(0.30,0.5),energy_expr=f"6500*{broken(0.31+0.11*i,0.13+0.07*i)}")
# 3. emergency beacons (rotate, wake up as stability drops)
for i,(x,y) in enumerate(((8.4,-8.4),(8.4,8.4),(-8.4,8.4))):
    par=bpy.data.objects.new(f"LP beacon {i} pivot",None); col(LC).objects.link(par); par.location=(x,y,9.0)
    drv(par,"rotation_euler",2,f"frame*0.23+{i*2.1}")
    b=light(f"LP beacon {i}","SPOT",(x,y,9.0),9000,(1.0,0.04,0.02),spot=(0.55,0.4),energy_expr=f"9000*{GATE}*{PULSE}")
    b.parent=par; b.location=(0,0,0); b.rotation_euler=(math.radians(62),0,0)
    box(f"LP beacon {i} lens",x-0.12,x+0.12,y-0.12,y+0.12,8.85,9.05,mat("red"),LC)
# 4. control room: warm lamp, state-coloured screens
light("LP control lamp","AREA",(-1.4,-8.0,8.55),260,(1.0,0.56,0.2),tgt=(-1.4,-8.0,5.4),size=(1.2,0.5),energy_expr=f"260*{broken(1.3,0.47)}")
for i,x in enumerate((-2.4,-1.4,-0.4)): light(f"LP control screen {i}","POINT",(x,-6.9,6.4),35,(0.3,1,0.3),energy_expr=f"35*{hum(i)}",color_state=True)
# 5. elevator
light("LP elevator car lamp","POINT",(-6.8,-6.8,2.3),90,(0.75,0.7,1.0),energy_expr=f"90*{broken(2.3,0.9)}")
light("LP elevator shaft lamp","SPOT",(-6.8,-6.8,10.3),700,(1.0,0.6,0.25),tgt=(-6.8,-6.8,0),spot=(0.5,0.6),energy_expr=f"700*{hum(1.7)}")
# 6. station glows
light("LP EC warning","POINT",(2.55,-8.6,2.7),320,(1.0,0.5,0.1),energy_expr=f"320*{hum(0.4)}")
light("LP turbine heat","POINT",(10.3,-3.3,1.2),420,(1.0,0.32,0.06),energy_expr=f"420*(0.85+0.15*sin(frame*1.3))")
light("LP waste hatch","POINT",(7.6,7.3,1.2),300,(0.75,1.0,0.2),energy_expr=f"300*{hum(2.2)}")
light("LP generator","POINT",(-9.6,-3.6,1.6),300,(1.0,0.58,0.2),energy_expr=f"300*{broken(1.1,0.53)}")
light("LP fuel bay","SPOT",(-4.0,9.2,5.0),1400,(0.68,0.6,1.0),tgt=(-4,9.7,0),spot=(0.9,0.5),energy_expr=f"1400*{broken(0.9,0.37)}")
# 7. rim/fill (cool violet, low) so silhouettes separate from the walls
light("LP rim W","AREA",(-10.2,0,10.5),200,(0.55,0.38,1.0),tgt=(0,0,5),size=(6,3))
light("LP rim E","AREA",(10.2,0,10.5),140,(0.55,0.38,1.0),tgt=(0,0,5),size=(6,3))
# 8. haze box for shafts
vb=box("LP haze volume",-10,10,-10,10,0.1,13.5,None,LC)
vm=bpy.data.materials.new("LP haze"); vm.use_nodes=True; nt=vm.node_tree
for n_ in list(nt.nodes): nt.nodes.remove(n_)
o_=nt.nodes.new("ShaderNodeOutputMaterial"); pv=nt.nodes.new("ShaderNodeVolumePrincipled"); pv.inputs['Density'].default_value=0.0035; pv.inputs['Color'].default_value=(0.8,0.72,0.9,1); pv.inputs['Anisotropy'].default_value=0.4
nt.links.new(pv.outputs['Volume'],o_.inputs['Volume']); vb.data.materials.append(vm); vb.visible_shadow=False
# 9. world + view transform
wn=sc.world.node_tree
for n_ in wn.nodes:
    if n_.type=='BACKGROUND': n_.inputs['Color'].default_value=(0.09,0.04,0.14,1); n_.inputs['Strength'].default_value=0.08
try: sc.view_settings.view_transform='AgX'
except Exception as e: print("vt",e)
try: sc.view_settings.look='AgX - Punchy'
except Exception as e:
    try: sc.view_settings.look='Punchy'
    except Exception as e2: print("look",e2)
sc.view_settings.exposure=-0.4
sc.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=S+"/w15.blend"); print("ok")
