import bpy,bmesh,sys,math,re; sys.path.insert(0,"."); from r2lib import *; from lib import col,port
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w26.blend"); sc=bpy.context.scene; sc.frame_set(1); st=bpy.data.objects["REACTOR_STATE"]
# ---- remove the legacy bank parts (keep the two moving empties and gantry/roof structure)
keep=re.compile(r"^(Gantry|Roof|BANK_A_MOVING|BANK_B_MOVING)")
n=0
for o in list(bpy.data.objects):
    cn=o.users_collection[0].name if o.users_collection else ""
    if cn=="04 BANK MECHANISMS" and o.type in("MESH","FONT","CURVE") and not keep.match(o.name): bpy.data.objects.remove(o,do_unlink=True); n+=1
# merged objects may hold bank stuff under other names: nothing else to do
print("legacy bank objects removed:",n)
# ---- materials
def drvmat(name,strength):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; b=nt.nodes["Principled BSDF"]
    def drv(path,idx,expr):
        fc=nt.driver_add(path,idx) if idx is not None else nt.driver_add(path)
        d=fc.driver; d.type='SCRIPTED'; v=d.variables.new(); v.name='s'; v.type='SINGLE_PROP'; v.targets[0].id=st; v.targets[0].data_path='["stability"]'; d.expression=expr
    for i,e in enumerate(("min(1,2*(1-s)+0.24)","0.03+0.92*s","0.20*s")):
        drv('nodes["Principled BSDF"].inputs["Emission Color"].default_value',i,e); drv('nodes["Principled BSDF"].inputs["Base Color"].default_value',i,e)
    drv('nodes["Principled BSDF"].inputs["Emission Strength"].default_value',None,f"{strength}*(1+0.6*(1-s))*(1+0.18*sin(frame*(0.15+0.5*(1-s))))")
    return m
M={"IRON":bpy.data.materials["R2 iron"],"TRIM":bpy.data.materials["R2 trim rust"],"TEXT":bpy.data.materials["R2 sign text"]}
M["ENAM"]=r2mat("R2 bank enamel",(0.030,0.034,0.070),0.42,edge=(0.55,0.16,0.03),grime=0.4,noise=(2.0,0),metal=0.3,mottle=0.6)
M["GLOW"]=drvmat("R2 state glow",5.0)
class A2(Acc):
    def frustum(s,key,cx,cy,z0,z1,r0,r1,seg=8,rot=math.pi/8):
        bm=s.get(key); r=bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r0,radius2=r1,depth=1.0)
        for v in r['verts']:
            x,y=v.co.x,v.co.y; c,sn=math.cos(rot),math.sin(rot); v.co=Vector((cx+x*c-y*sn,cy+x*sn+y*c,z0+(v.co.z+.5)*(z1-z0)))
for tag,bx in (("A",-1.4),("B",1.4)):
    emp=bpy.data.objects[f"BANK_{tag}_MOVING"]; ez=emp.matrix_world.translation.z
    F=A2(); Mv=A2()
    # fixed housing
    F.frustum((f"BANK_{tag}_FIXED_HOUSING","IRON"),bx,0,9.70,9.95,0.95,0.90); F.frustum((f"BANK_{tag}_FIXED_HOUSING","IRON"),bx,0,9.95,12.30,0.86,0.86)
    F.frustum((f"BANK_{tag}_FIXED_HOUSING","ENAM"),bx,0,10.40,11.90,0.88,0.88)
    for z in (10.15,12.05): F.frustum((f"bank {tag} hazard band","TRIM"),bx,0,z,z+0.14,0.90,0.90)
    F.frustum((f"BANK_{tag}_FIXED_HOUSING","IRON"),bx,0,12.30,12.62,0.86,0.52); F.frustum((f"bank {tag} neck","IRON"),bx,0,12.62,13.72,0.32,0.32); F.frustum((f"bank {tag} neck","IRON"),bx,0,13.52,13.76,0.58,0.58)
    F.frustum((f"bank {tag} state ring","GLOW"),bx,0,10.85,11.00,0.905,0.905)
    for sgn in(-1,1):
        F.box((f"bank {tag} cassette","ENAM"),bx,sgn*1.06,10.30,11.95,1.20,0.30,0,0.03)
        F.box((f"bank {tag} cassette","IRON"),bx,sgn*1.06,10.20,10.30,1.30,0.36,0,0.02); F.box((f"bank {tag} cassette","IRON"),bx,sgn*1.06,11.95,12.05,1.30,0.36,0,0.02)
        F.frustum((f"bank {tag} gauge","IRON"),bx-0.30,sgn*(1.06+0.16),11.35,11.40,0.20,0.20,8,0)
        for pz in(10.6,11.6): F.box((f"bank {tag} clamp","TRIM"),bx,sgn*1.06,pz,pz+0.10,1.24,0.34,0,0.01)
        port(f"PORT_BANK_{tag}_hyd_{'N' if sgn>0 else 'S'}",(bx+0.62,sgn*1.06,11.0),"hydraulic",25,(1,0,0))
    F.box((f"bank {tag} face plate","IRON"),bx,-0.92,11.00,11.90,1.10,0.06,0,0.02)
    # moving assembly (children of the moving empty)
    Mv.box((f"BANK_{tag}_CARRIAGE","ENAM"),bx,0,ez-0.65,ez+0.65,1.45,1.05,0,0.05)
    for sgn in(-1,1): Mv.box((f"bank {tag} guide shoe","IRON"),bx,sgn*0.62,ez-0.45,ez+0.45,0.60,0.16,0,0.02)
    Mv.frustum((f"bank {tag} stem","IRON"),bx,0,ez+0.65,ez+3.10,0.34,0.34)
    Mv.frustum((f"BANK_{tag}_DRIVE_COLUMN","IRON"),bx,0,-5.0,ez-0.65,0.20,0.20)
    z=ez-1.0
    while z>-4.8:
        Mv.frustum((f"bank {tag} rod band","GLOW" if int(round(z))%2==0 else "TRIM"),bx,0,z-0.05,z+0.05,0.225,0.225); z-=1.0
    Mv.frustum((f"bank {tag} rod tip","IRON"),bx,0,-5.25,-5.0,0.32,0.20)
    Mv.box((f"bank {tag} carriage plate","TRIM"),bx,-0.53,ez-0.18,ez+0.18,0.80,0.03,0,0.008)
    fo=F.build("04 BANK MECHANISMS",f"R2 bank {tag} fixed",M); mo=Mv.build("04 BANK MECHANISMS",f"R2 bank {tag} moving",M)
    inv=emp.matrix_world.inverted()
    for o in mo: o.parent=emp; o.matrix_parent_inverse=inv
    # rename gameplay-named parts to their exact identifiers
    for o in fo+mo:
        for nm in (f"BANK_{tag}_FIXED_HOUSING",f"BANK_{tag}_CARRIAGE",f"BANK_{tag}_DRIVE_COLUMN"):
            if nm in o.name and "IRON" in o.name or nm in o.name and "ENAM" in o.name: o.name=nm if nm not in bpy.data.objects else o.name
    # labels on the -y face plate
    for txt,size,zz in ((f"CONTROL BANK {tag}",0.11,11.72),(tag,0.42,11.28)):
        cu=bpy.data.curves.new("R2 bank label",'FONT'); cu.body=txt; cu.size=size; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=0.004
        ob=bpy.data.objects.new(f"R2 bank {tag} label {txt}",cu); ob.location=(bx,-0.96,zz); ob.rotation_euler=(math.pi/2,0,math.pi); bpy.data.collections["04 BANK MECHANISMS"].objects.link(ob); cu.materials.append(M["TEXT"])
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith("R2 bank"):
        for p in o.data.polygons: p.use_smooth=False
bpy.ops.wm.save_as_mainfile(filepath=S+"/w27.blend"); print("ok")
