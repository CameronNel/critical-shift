import bpy,sys,math,random; sys.path.insert(0,"."); import palette2; from lib import *
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w10.blend"); sc=bpy.context.scene
print("materials recoloured:",palette2.apply())
# --- reactor state control (game will drive 'stability': 1 stable ... 0 critical)
st=bpy.data.objects.new("REACTOR_STATE",None); st.empty_display_type='SPHERE'; st.empty_display_size=0.3; st.location=(0,0,-0.6); col("24 REACTOR STATE").objects.link(st)
st["stability"]=1.0; st.id_properties_ui("stability").update(min=0.0,max=1.0,description="1 = stable (sickly green), 0.5 = warning (amber), 0 = critical (blood red)")
def drv(idtarget,path,idx,expr):
    fc=idtarget.driver_add(path,idx) if idx is not None else idtarget.driver_add(path)
    d=fc.driver; d.type='SCRIPTED'; v=d.variables.new(); v.name='s'; v.type='SINGLE_PROP'; v.targets[0].id=st; v.targets[0].data_path='["stability"]'; d.expression=expr
R="min(1,2*(1-s)+0.24)"; G="0.03+0.92*s"; B="0.20*s"
PULSE="(1+0.6*(1-s))*(1+0.18*sin(frame*(0.15+0.5*(1-s))))"
def state_color(idtarget,path):
    for i,e in enumerate((R,G,B)): drv(idtarget,path,i,e)
# pool emission materials
for name,strength in (("pool_glow",2.4),("hall_cyan_indicator",1.2),("hall_screen_line",1.2)):
    m=bpy.data.materials[name]; nt=m.node_tree; b=nt.nodes["Principled BSDF"]
    state_color(nt,'nodes["Principled BSDF"].inputs["Emission Color"].default_value'); state_color(nt,'nodes["Principled BSDF"].inputs["Base Color"].default_value')
    drv(nt,'nodes["Principled BSDF"].inputs["Emission Strength"].default_value',None,f"{strength}*{PULSE}")
# animation on old pool_glow strength keyframes would fight the driver: clear
pm=bpy.data.materials["pool_glow"].node_tree
if pm.animation_data and pm.animation_data.action: pm.animation_data.action=None
# volumes
for n in bpy.data.materials["pool_medium"].node_tree.nodes:
    if n.type=='VOLUME_ABSORPTION': state_color(bpy.data.materials["pool_medium"].node_tree,f'nodes["{n.name}"].inputs["Color"].default_value')
    if n.type=='VOLUME_SCATTER': state_color(bpy.data.materials["pool_medium"].node_tree,f'nodes["{n.name}"].inputs["Color"].default_value')
# --- lights: pool lights follow state; everything else dim, some flicker, some dead
random.seed(4); k=0
for o in bpy.data.objects:
    if o.type!='LIGHT': continue
    L=o.data
    if "pool" in o.name.lower() or "cyan" in o.name.lower() or "core" in o.name.lower():
        base=L.energy*1.1; state_color(L,"color"); drv(L,"energy",None,f"{base}*{PULSE}")
    else:
        base=L.energy*0.14; L.color=(1.0,0.60,0.28); k+=1
        if k%5==0: drv(L,"energy",None,f"{base*0.6}*(1 if sin(frame*{2.1+0.37*k})>-0.55 else 0.05)")   # failing fluorescent
        elif k%7==0: L.energy=base*0.02                                                                   # dead
        else: L.energy=base
# a stronger pool light so the reactor is the main source
pl=bpy.data.lights.new("Reactor state key","AREA"); pl.shape='DISK'; pl.size=5.5; pl.energy=1.0
po=bpy.data.objects.new("Reactor state key",pl); col("24 REACTOR STATE").objects.link(po); po.location=(0,0,1.2)
state_color(pl,"color"); drv(pl,"energy",None,f"3800*{PULSE}")
# --- world: near black + thin haze
w=sc.world; nt=w.node_tree
for n in nt.nodes:
    if n.type=='BACKGROUND': n.inputs['Color'].default_value=(0.006,0.006,0.010,1); n.inputs['Strength'].default_value=0.4
out=next(n for n in nt.nodes if n.type=='OUTPUT_WORLD'); vs=nt.nodes.new("ShaderNodeVolumeScatter"); vs.inputs['Density'].default_value=0.003; vs.inputs['Anisotropy'].default_value=0.35; vs.inputs['Color'].default_value=(0.75,0.72,0.72,1)
nt.links.new(vs.outputs['Volume'],out.inputs['Volume'])
sc.frame_set(1); bpy.ops.wm.save_as_mainfile(filepath=S+"/w14.blend"); print("ok")
