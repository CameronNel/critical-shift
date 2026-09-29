import bpy,sys,re,math
from mathutils import Vector
f=sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.open_mainfile(filepath=f); sc=bpy.context.scene
print("FILE",f); print("UNITS",sc.unit_settings.system,sc.unit_settings.scale_length)
print("CURSOR",tuple(sc.cursor.location))
def bb(o):
    return [o.matrix_world@Vector(v) for v in o.bound_box]
def ext(pts): return (min(p.x for p in pts),max(p.x for p in pts),min(p.y for p in pts),max(p.y for p in pts),min(p.z for p in pts),max(p.z for p in pts))
allp=[];bycol={}
for o in sc.objects:
    if o.type in("MESH","CURVE","FONT") and not o.name.startswith("LP haze"):
        b=bb(o); allp+=b; c=o.users_collection[0].name if o.users_collection else "?"; bycol.setdefault(c,[]).extend(b)
e=ext(allp); print("ALL_EXT x%.2f..%.2f y%.2f..%.2f z%.2f..%.2f"%e, "size %.2f x %.2f x %.2f"%(e[1]-e[0],e[3]-e[2],e[5]-e[4]))
for c,p in sorted(bycol.items()):
    e=ext(p); print("COL %-40s x%.2f..%.2f y%.2f..%.2f z%.2f..%.2f"%(c[:40],*e))
print("EMPTIES")
for o in sorted(sc.objects,key=lambda o:o.name):
    if o.type=="EMPTY": print("  E",o.name,tuple(round(x,3) for x in o.matrix_world.translation),tuple(round(math.degrees(a),1) for a in o.matrix_world.to_euler()),dict((k,o[k]) for k in o.keys() if not k.startswith("_"))) 
pat=re.compile(r"door|port|anchor|connect|access|gate|threshold|portal|vestib|entry|exit",re.I)
print("DOORISH")
for o in sorted(sc.objects,key=lambda o:o.name):
    if o.type!="EMPTY" and pat.search(o.name):
        b=bb(o); e=ext(b); print("  D",o.name[:52],o.type,"x%.2f..%.2f y%.2f..%.2f z%.2f..%.2f"%e)
