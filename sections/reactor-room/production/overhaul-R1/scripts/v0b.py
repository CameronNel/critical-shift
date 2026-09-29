import bpy,re,sys,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath="w36.blend")
R={"grid":(9.0,10.9,-2.5,1.5),"turb":(8.4,10.9,-5.6,-2.1),"gen":(-10.9,-8.1,-4.7,-2.7),"resA":(-10.9,-8.7,2.9,4.3),"resB":(-10.9,-8.7,-5.8,-4.6),
"fuel":(-5.6,-2.6,8.7,10.9),"cart":(-10.0,-7.9,6.4,8.4),"bank":(2.5,4.8,9.5,10.9),"spares":(4.5,5.6,9.5,10.9),"vent":(8.6,10.4,5.8,7.8),
"waste":(6.3,8.3,7.4,9.6),"ec":(1.0,4.2,-10.6,-8.0),"pump":(-4.7,-2.3,-10.3,-7.9),"samp":(1.0,2.3,-4.3,-3.1),"bench":(-10.8,-9.6,3.8,5.4),"coolwall":(-5.6,5.4,-10.7,-9.95)}
KEEP2=re.compile(r"(THROTTLE|VENT CONTROL|COOLANT_|EMERGENCY_COOLING|WASTE_TRANSFER|SAMPLE_DRAW|MF13|MF14 RES|MF01 FUEL|MF02 FUEL|MF19 FUEL|dial|toggle|spoke|handwheel|\\bkey\\b|selector|CRT|phosphor|\\blive|MERGED|seal edge|ECCS|Pump discharge|Pump suction|Manifold|riser|valve|gauge|Sample bottle|Sampling pressure|screen|legend|identity|identif|sign|label|tag|wall plum|clip|sleeve|pipe|Containment|guard|collar|grip|pivot|hub|stem|bonnet|bezel|crystal)",re.I)
cols=[c for c in bpy.data.collections if c.name.startswith(("05 PER","MF W","W"))]
dele=[];keep=[]
for c in cols:
    for o in c.objects:
        if o.type!="MESH": continue
        p=o.matrix_world.translation; bb=[o.matrix_world@Vector(v) for v in o.bound_box]; cx=sum(v.x for v in bb)/8; cy=sum(v.y for v in bb)/8
        reg=[k for k,(x0,x1,y0,y1) in R.items() if x0<=cx<=x1 and y0<=cy<=y1]
        if not reg: continue
        if not KEEP2.search(o.name): dele.append((o,reg[0]))
        else: keep.append((o,reg[0]))
import collections
d=collections.defaultdict(list)
for o,r in dele:
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]; d[r].append(bb)
for r,l in d.items():
    pts=[p for bb in l for p in bb]; print("DEL",r,len(l),"x%.2f..%.2f y%.2f..%.2f z%.2f..%.2f"%(min(p.x for p in pts),max(p.x for p in pts),min(p.y for p in pts),max(p.y for p in pts),min(p.z for p in pts),max(p.z for p in pts)))
k=collections.defaultdict(list)
for o,r in keep: k[r].append(o.name[:30])
for r,l in k.items(): print("KEEP",r,len(l),sorted(set(l))[:14])

import json
for o,r in dele: bpy.data.objects.remove(o,do_unlink=True)
# orphan-clean
for me in [m for m in bpy.data.meshes if m.users==0]: bpy.data.meshes.remove(me)
print("DELETED",len(dele))
bpy.ops.wm.save_as_mainfile(filepath="w37.blend")
