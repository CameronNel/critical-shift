"""Control-room optimiser (visual-neutral dev tricks), run on a BUILT blend.
usage: python cr_optimize.py -- <in.blend> <out.blend> [--no-merge]
 1. hidden-face removal: a face whose centre and corners all lie flush (<= 1.5 mm) against other surfaces facing it can never be seen (box bottoms on the floor,
    legs on desk tops, panels against walls); the pair is removed from both meshes.  Decals/glass/emissive/screen objects are skipped.
 2. coplanar dissolve (0.5 deg) with UV/material/sharp delimits, then loose-vertex clean-up.
 3. static merge: single-material dressing objects of the same material are joined (fewer draw calls).  Interactive/animated groups
    (chair, crt, rack, desk, tv, beacon, text, decals) keep their own objects.
Bevel segments (crk.BEVSEG) and cylinder side counts (crk.prism_seg) are reduced at build time, not here.
Prints a before/after table (triangles, objects, materials in use)."""
import bpy,bmesh,sys,re,collections
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A[0],A[1]; MERGE="--no-merge" not in A
bpy.ops.wm.open_mainfile(filepath=SRC)
C=bpy.data.collections["31 CR CONTROL ROOM REDO"]
SKIP_GROUP=("grime","marks","glassnote","glass","tv","text","beacon","haze","COL","decal","note","poster")
def group(o): m=re.match(r"CR (\w+)",o.name); return m.group(1) if m else ""
def tris(objs): return sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objs if o.type=='MESH')
meshes=[o for o in C.all_objects if o.type=='MESH' and not o.name.startswith(("COL ","CR haze"))]
b_tris,b_obj=tris(meshes),len(meshes); b_mats=len({m.name for o in meshes for m in o.data.materials if m})
# ---- 1. hidden faces against every other surface of the control room + the structural shell
shell=[o for o in bpy.data.collections["26 R2 CONTROL ROOM"].objects if o.type=='MESH']
dg=bpy.context.evaluated_depsgraph_get()
def bvh(objs):
    vs=[];fs=[]
    for o in objs:
        base=len(vs); vs+= [o.matrix_world@v.co for v in o.data.vertices]; fs+=[tuple(base+i for i in p.vertices) for p in o.data.polygons]
    return BVHTree.FromPolygons(vs,fs)
eligible=[o for o in meshes if group(o) not in SKIP_GROUP and not any(m and (m.name.startswith(("CR tv","CR glass")) or "emissive" in m.name) for m in o.data.materials)]
T=bvh(meshes+shell); removed=0
for o in eligible:
    me=o.data; bm=bmesh.new(); bm.from_mesh(me); mw=o.matrix_world; nm=mw.to_3x3()
    kill=[]
    for f in bm.faces:
        n=(nm@f.normal).normalized(); c=mw@f.calc_center_median()
        pts=[c]+[c+(mw@v.co-c)*0.85 for v in f.verts]          # centre + every corner pulled in 15%: the WHOLE face must be covered
        ok=True
        for p in pts:
            h=T.ray_cast(p+n*0.0003,n,0.0015)
            if h[0] is None or h[1].dot(n)>=-0.5: ok=False; break
        if ok: kill.append(f)
    if kill: bmesh.ops.delete(bm,geom=kill,context='FACES_ONLY'); removed+=len(kill)
    # ---- 2. coplanar dissolve
    bmesh.ops.dissolve_limit(bm,angle_limit=0.0087,verts=bm.verts[:],edges=bm.edges[:],delimit={'UV','MATERIAL','SHARP'})
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
    bm.to_mesh(me); bm.free(); me.update()
print("hidden faces removed:",removed)
# ---- 3. static merge by material
if MERGE:
    by=collections.defaultdict(list)
    for o in [o for o in C.all_objects if o.type=='MESH' and not o.name.startswith(("COL ","CR haze"))]:
        if group(o) in ("ceil","wall","deco","clutter","shelf","break","wtable","floor","door") and len(o.data.materials)==1 and o.data.materials[0] and not o.animation_data and not o.data.shape_keys:
            if len(o.data.uv_layers)!=1: continue
            o.data.uv_layers[0].name="UVMap"                         # joins match UV layers by NAME: unify first or the loops of a mismatched layer land at (0,0)
            by[o.data.materials[0].name].append(o)
    for mn,lst in by.items():
        if len(lst)<2: continue
        for o in bpy.context.view_layer.objects: o.select_set(False)
        for o in lst: o.select_set(True)
        bpy.context.view_layer.objects.active=lst[0]; bpy.ops.object.join(); lst[0].name="CR static "+mn[3:] if mn.startswith("CR ") else "CR static "+mn
after=[o for o in C.all_objects if o.type=='MESH' and not o.name.startswith(("COL ","CR haze"))]
a_tris,a_obj=tris(after),len(after); a_mats=len({m.name for o in after for m in o.data.materials if m})
print("OPT  triangles %d -> %d (%.1f%%)   objects %d -> %d   materials in use %d -> %d"%(b_tris,a_tris,100*(a_tris-b_tris)/b_tris,b_obj,a_obj,b_mats,a_mats))
bpy.ops.wm.save_as_mainfile(filepath=DST)
