import bpy,bmesh,sys,math; sys.path.insert(0,"."); from r2lib import *; from lib import col,bbw
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w31.blend"); dg=bpy.context.evaluated_depsgraph_get()
old=[o for o in bpy.data.objects if o.name.startswith("MERGED 03 POOL AND") and "hall_pool_tile" in o.name]
tr=0
for o in old:
    e=o.evaluated_get(dg); me=e.to_mesh(); tr+=sum(len(p.vertices)-2 for p in me.polygons); e.to_mesh_clear()
print("old pool tile-course objects:",len(old),"tris",tr)
for o in old: bpy.data.objects.remove(o,do_unlink=True)
M={"TILE":r2mat("R2 pool tile",(0.030,0.075,0.060),0.22,edge=(0.10,0.22,0.18),grime=0.35,noise=(2.0,0),mottle=0.6),"GROUT":r2mat("R2 pool grout",(0.012,0.02,0.022),0.6,edge=None,grime=0.0,noise=(1,0),mottle=0.0)}
A=Acc(); R=3.40; Z0,Z1=-6.55,-0.55; SEG=32
bm=A.get(("pool lining","TILE")); 
top=[bm.verts.new((R*math.cos(2*math.pi*i/SEG),R*math.sin(2*math.pi*i/SEG),Z1)) for i in range(SEG)]; bot=[bm.verts.new((R*math.cos(2*math.pi*i/SEG),R*math.sin(2*math.pi*i/SEG),Z0)) for i in range(SEG)]
for i in range(SEG): bm.faces.new((bot[i],bot[(i+1)%SEG],top[(i+1)%SEG],top[i]))
bmesh.ops.reverse_faces(bm,faces=list(bm.faces))     # inward-facing wall
# modelled tile courses (horizontal ribs) and vertical grout ribs
for k in range(1,10):
    z=Z1-k*0.6; bmc=A.get(("pool course","GROUT"))
    for i in range(SEG):
        a0=2*math.pi*i/SEG; a1=2*math.pi*(i+1)/SEG; am=(a0+a1)/2; L=2*(R-0.01)*math.sin(math.pi/SEG)+0.01
        A.box(("pool course","GROUT"),(R-0.015)*math.cos(am),(R-0.015)*math.sin(am),z-0.012,z+0.012,L,0.02,am+math.pi/2,0.0)
for i in range(SEG):
    am=2*math.pi*(i+0.5)/SEG
    A.box(("pool seam","GROUT"),(R-0.015)*math.cos(am),(R-0.015)*math.sin(am),Z0,Z1,0.024,0.02,am+math.pi/2,0.0)
objs=A.build("03 POOL AND RAIL","R2 pool",M)
for o in objs:
    for p in o.data.polygons: p.use_smooth=False
dg=bpy.context.evaluated_depsgraph_get(); nt=0
for o in objs:
    e=o.evaluated_get(dg); me=e.to_mesh(); nt+=sum(len(p.vertices)-2 for p in me.polygons); e.to_mesh_clear()
print("new pool lining tris:",nt)
bpy.ops.wm.save_as_mainfile(filepath=S+"/w32.blend"); print("ok")
