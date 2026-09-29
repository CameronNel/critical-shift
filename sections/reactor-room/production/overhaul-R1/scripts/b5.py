import bpy,sys; sys.path.insert(0,"."); from lib import *
S=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=S+"/w4.blend")
DK=mat("hall_steel"); SG=mat("hall_steel_light"); FL=mat("hall_floor"); MZ="20 CONTROL MEZZANINE"
pan=bpy.data.objects["Shell 3 field.014"].data.materials[0]
# 0. rest of old east window opening
box("East wall patch window low B",10.8,11.08,1.6,2.7,8.0,10.2,pan,MZ); box("East wall patch window high B",10.8,11.08,1.6,2.7,10.2,12.9,pan,MZ)
# 1. move elevator to SW corner zone
dx,dy=-10.2,2.0
for o in bpy.data.objects:
    if o.name.startswith("EL ") and o.parent is None:
        o.location.x+=dx; o.location.y+=dy
# 2. rebuild landing / doors
rm=[o for o in bpy.data.objects if o.name.startswith(("MZ landing","MZ column 3","MZ column base 3","MZ east wall","MZ door"))]
for o in rm: bpy.data.objects.remove(o,do_unlink=True)
west=None
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith("Control south wall"): west=o
print("west wall obj:",west.name if west else None, bbw(west) if west else None)
wm=west.data.materials[0] if west and west.data.materials else SG
if west: bpy.data.objects.remove(west,do_unlink=True)
XW,XE,YB,YF,ZF=-4.8,2.0,-10.06,-5.9,5.4
box("MZ west wall back",XW-0.2,XW,YB,-7.3,ZF-0.2,8.8,wm,MZ); box("MZ west wall front",XW-0.2,XW,-6.3,YF,ZF-0.2,8.8,wm,MZ)
box("MZ west wall header",XW-0.2,XW,-7.3,-6.3,7.6,8.8,wm,MZ)
for i,y in enumerate([-7.3,-6.3]): box(f"MZ door jamb {i}",XW-0.23,XW+0.03,y-0.04,y+0.04,ZF,7.6,DK,MZ)
box("MZ door head",XW-0.23,XW+0.03,-7.34,-6.26,7.56,7.64,DK,MZ)
box("MZ east wall",XE,XE+0.2,YB,YF,ZF-0.2,8.8,SG,MZ)
# landing: front deck + strip
box("MZ landing deck",-8.0,-4.8,-5.6,-4.6,ZF-0.2,ZF,FL,MZ); box("MZ landing strip",-5.6,-4.8,-8.0,-5.6,ZF-0.2,ZF,FL,MZ)
box("MZ landing deck edge",-8.0,-4.8,-4.65,-4.55,ZF-0.3,ZF-0.2,DK,MZ)
for i,(x,y) in enumerate([(-7.85,-4.75),(-4.95,-4.75)]):
    box(f"MZ landing column {i}",x-0.14,x+0.14,y-0.14,y+0.14,0,ZF-0.2,DK,MZ); box(f"MZ landing column base {i}",x-0.26,x+0.26,y-0.26,y+0.26,0,0.05,DK,MZ)
box("MZ landing beam",-8.0,-4.8,-4.85,-4.65,ZF-0.55,ZF-0.2,DK,MZ)
for i,x in enumerate([-7.4,-6.4,-5.4]): box(f"MZ landing joist {i}",x-0.04,x+0.04,-5.6,-4.85,ZF-0.5,ZF-0.2,DK,MZ)
def rail(name,p0,p1):
    for k,(h,r) in enumerate(((1.05,0.025),(0.55,0.018))): cyl_between(f"{name} rail {k}",(p0[0],p0[1],ZF+h),(p1[0],p1[1],ZF+h),r,DK,MZ)
    L=((p1[0]-p0[0])**2+(p1[1]-p0[1])**2)**.5; n=max(2,int(L/1.0)+1)
    for j in range(n+1):
        t=j/n; cyl(f"{name} post {j}",p0[0]+(p1[0]-p0[0])*t,p0[1]+(p1[1]-p0[1])*t,ZF,ZF+1.05,0.028,DK,MZ,8)
rail("MZ landing front",(-8.0,-4.66),(-4.86,-4.66)); rail("MZ landing west",(-7.94,-5.6),(-7.94,-4.66)); rail("MZ landing east",(-4.86,-5.9),(-4.86,-4.66))
bpy.ops.wm.save_as_mainfile(filepath=S+"/w5.blend"); print("ok")
