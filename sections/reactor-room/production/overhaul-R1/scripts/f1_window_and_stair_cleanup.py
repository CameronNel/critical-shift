import bpy,sys,math; sys.path.insert(0,"."); from lib import *
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w15b.blend")
n=0
for o in list(bpy.data.objects):
    if 'stair' in o.name.lower(): bpy.data.objects.remove(o,do_unlink=True); n+=1
print("stair leftovers removed:",n)
old=[o for o in bpy.data.objects if o.name.startswith(("MZ front sill wall","MZ front pier","MZ window","MZ front deep sill"))]
sg=bpy.data.objects["MZ front head wall"].data.materials[0]; dk=bpy.data.materials["hall_steel"]; gl=bpy.data.materials["observation_glass"]
for o in old: bpy.data.objects.remove(o,do_unlink=True)
MZ="20 CONTROL MEZZANINE"; YF=-5.9; XW,XE=-4.8,2.0; WX0,WX1=-4.6,1.8; Z0,Z1=5.65,8.5
box("MZ front kick wall",XW,XE,YF-0.2,YF,5.4,Z0,sg,MZ)
box("MZ front pier W",XW,WX0,YF-0.2,YF,Z0,Z1,sg,MZ); box("MZ front pier E",WX1,XE,YF-0.2,YF,Z0,Z1,sg,MZ)
box("MZ window glass",WX0,WX1,YF-0.13,YF-0.09,Z0,Z1,gl,MZ)
for i,x in enumerate((WX0,WX1)): box(f"MZ window jamb {i}",x-0.05,x+0.05,YF-0.24,YF+0.02,Z0-0.05,Z1+0.05,dk,MZ)
for i,z in enumerate((Z0,Z1)): box(f"MZ window rail {i}",WX0-0.05,WX1+0.05,YF-0.24,YF+0.02,z-0.05,z+0.05,dk,MZ)
for i in range(1,4):
    x=WX0+(WX1-WX0)*i/4; box(f"MZ window mullion {i}",x-0.03,x+0.03,YF-0.2,YF-0.02,Z0,Z1,dk,MZ)
bpy.ops.wm.save_as_mainfile(filepath=S+"/w16.blend"); print("ok")
