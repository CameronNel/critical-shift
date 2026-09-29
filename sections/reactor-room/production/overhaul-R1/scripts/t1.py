import bpy,bmesh,sys,math,collections; sys.path.insert(0,"."); from r2lib import *
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w34.blend")
# ---- new machine paints (legacy enamel groups collapse into these)
r2mat("R2 machine enamel",(0.16,0.045,0.04),0.42,edge=(0.75,0.25,0.07),grime=0.45,noise=(2.4,0),metal=0.25,mottle=0.6)
r2mat("R2 machine olive",(0.085,0.095,0.05),0.5,edge=(0.55,0.35,0.10),grime=0.5,noise=(2.4,0),metal=0.2,mottle=0.6)
MAP={"hall_ink":"R2 ink","hall_steel_light":"R2 dado navy","hall_paint_chip":"R2 wall plum lower","hall_white":"R2 wall plum lower","WP white mineral":"R2 wall plum lower","hall_rim_stone":"R2 wall inset",
"hall_steel":"R2 iron","RF dark":"R2 iron","RF gunmetal":"R2 iron","RF edge":"R2 iron","RF white":"R2 wall plum upper","RF orange":"R2 trim rust",
"hall_teal_dark":"R2 machine enamel","hall_teal":"R2 machine enamel","hall_cast_iron":"R2 machine enamel","hall_teal_service":"R2 machine olive","hall_teal_light":"R2 machine olive",
"hall_rubber":"R2 cable","hall_yellow":"R2 trim rust","hall_orange":"R2 trim rust","hall_floor_yellow":"R2 floor tile","hall_floor":"R2 floor tile",
"hall_pipe":"R2 pipe lagging","hall_shaft":"R2 pipe lagging","MF inexpensive instrument glazing":"observation_glass","glass":"observation_glass","wood":"R2 desk","paper":"R2 paper",
"R2 binder b":"R2 binder a","R2 blanket":"R2 fabric","R2 pipe vent":"R2 pipe hydraulic","R2 cable tray":"R2 conduit","R2 pool grout":"R2 backing","R2 door panel":"R2 door steel",
"R2 ceiling panel":"R2 lamp lavender","R2 readout amber":"R2 lamp amber","amber":"R2 lamp amber","red":"R2 status lamp","R2 drum blue":"R2 drum red","R2 mug":"R2 cone"}
n=0
for o in bpy.data.objects:
    if o.type not in('MESH','CURVE','FONT'): continue
    for s in o.material_slots:
        if s.material and s.material.name in MAP and MAP[s.material.name] in bpy.data.materials: s.material=bpy.data.materials[MAP[s.material.name]]; n+=1
used=set(s.material.name for o in bpy.data.objects if o.type in('MESH','CURVE','FONT') for s in o.material_slots if s.material)
print("slots remapped:",n,"| materials on objects now:",len(used))
# ---- world-scale box-projected UVs (1 UV unit = 2 m) so tileable textures apply directly
nu=0; TILE=2.0
for o in bpy.data.objects:
    if o.type!='MESH' or o.name.startswith(("LP haze",)) or not o.data.polygons: continue
    me=o.data; mw=o.matrix_world
    bm=bmesh.new(); bm.from_mesh(me); uv=bm.loops.layers.uv.verify()
    for f in bm.faces:
        nrm=(mw.to_3x3()@f.normal); ax=max(range(3),key=lambda i:abs(nrm[i]))
        for l in f.loops:
            p=mw@l.vert.co
            l[uv].uv=((p.y,p.z) if ax==0 else (p.x,p.z) if ax==1 else (p.x,p.y))
            l[uv].uv=(l[uv].uv[0]/TILE,l[uv].uv[1]/TILE)
    bm.to_mesh(me); bm.free(); nu+=1
print("meshes UV-mapped:",nu)
bpy.ops.wm.save_as_mainfile(filepath=S+"/w35.blend"); print("ok")
