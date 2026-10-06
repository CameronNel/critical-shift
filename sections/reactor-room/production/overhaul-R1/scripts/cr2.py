"""Control room: increase window-to-back-wall depth by 50% (3.94 m -> 5.91 m) by moving the BACK wall back 1.97 m,
through an opening cut in the hall's south wall.  The window, desk group, west door and elevator landing do not move.
usage: python cr2.py -- <src.blend> <dst.blend>
Steps
 1. cut an opening in the hall south wall (slab, bands, insets, pilasters) behind the control room: x -5.0..2.2, z 5.16..9.0
 2. back group (back wall, back furniture, east storage run, cot, shelves, back lamps/readouts/screens) moves -Y as rigid pieces
 3. long structure (floor, soffit, roof, side walls, long beams) is stretched: vertices behind the split move -Y
 4. one extra ceiling light for the new rear area
"""
import bpy,bmesh,sys
from mathutils import Vector
A=sys.argv[sys.argv.index("--")+1:]; SRC,DST=A[0],A[1]
D=1.97; S=-8.85
OPEN=(-5.0,2.2,5.16,9.0)                        # x0,x1,z0,z1  (all y: the opening goes through the wall)
bpy.ops.wm.open_mainfile(filepath=SRC)
def ext(o):
    p=[o.matrix_world@Vector(v) for v in o.bound_box]
    return (min(q.x for q in p),max(q.x for q in p),min(q.y for q in p),max(q.y for q in p),min(q.z for q in p),max(q.z for q in p))
def separate(objs):
    for o in objs:
        bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active=o; o.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.separate(type='LOOSE'); bpy.ops.object.mode_set(mode='OBJECT')
# ---------- 1. wall opening
arch=[o for o in bpy.data.collections["22 R2 ARCHITECTURE"].objects if o.type=="MESH"]
def near_wall(e): return e[3]<-10.2 and e[2]>-11.3 and e[1]>OPEN[0] and e[0]<OPEN[1] and e[5]>OPEN[2] and e[4]<OPEN[3]
cand=[o for o in arch if near_wall(ext(o))]
separate([o for o in cand if o.name.startswith(("MERGED","R2 w0"))])
def boxes_minus(b):
    x0,x1,y0,y1,z0,z1=b; ox0,ox1,oz0,oz1=OPEN; out=[]
    if x0<ox0: out.append((x0,min(x1,ox0),y0,y1,z0,z1))
    if x1>ox1: out.append((max(x0,ox1),x1,y0,y1,z0,z1))
    mx0,mx1=max(x0,ox0),min(x1,ox1)
    if mx1>mx0:
        if z0<oz0: out.append((mx0,mx1,y0,y1,z0,min(z1,oz0)))
        if z1>oz1: out.append((mx0,mx1,y0,y1,max(z0,oz1),z1))
    return [q for q in out if q[1]-q[0]>1e-4 and q[5]-q[4]>1e-4]
cut=deleted=0
for o in list(bpy.data.collections["22 R2 ARCHITECTURE"].objects):
    if o.type!="MESH": continue
    e=ext(o)
    if not near_wall(e): continue
    if (e[1]-e[0])>13 or o.parent: continue                       # skip whole-room merged meshes (corners etc.)
    pieces=boxes_minus(e)
    if len(pieces)==1 and pieces[0]==tuple(e): continue
    if not pieces: bpy.data.objects.remove(o,do_unlink=True); deleted+=1; continue
    mw=o.matrix_world; inv=mw.inverted(); bm=bmesh.new()
    for (x0,x1,y0,y1,z0,z1) in pieces:
        r=bmesh.ops.create_cube(bm,size=1.0)
        for v in r['verts']:
            w=Vector((x0+(v.co.x+.5)*(x1-x0),y0+(v.co.y+.5)*(y1-y0),z0+(v.co.z+.5)*(z1-z0))); v.co=inv@w
    bm.to_mesh(o.data); bm.free(); o.data.update(); cut+=1
print("CR2 wall opening: pieces re-cut",cut,"removed",deleted)
# ---------- 2/3. back extension
cols=[bpy.data.collections["20 CONTROL MEZZANINE"],bpy.data.collections["26 R2 CONTROL ROOM"]]
separate([o for c in cols for o in c.objects if o.type=="MESH" and o.name.startswith("MERGED")])
def classify(o,e):
    cx=(e[0]+e[1])/2; cy=(e[2]+e[3])/2; ylen=e[3]-e[2]
    if cx<=-4.75 and not (o.name.startswith("MERGED 20 CONTROL M CF gunmetal") and ylen>2.5): return "stay"      # elevator landing, rails, door frames (west wall A island is long -> stretched)
    if ylen>2.5: return "stretch"
    if cx>=1.4 and e[2]>=-9.75 and e[3]<=-7.3 and (e[5]-e[4])<3: return "move"                                    # east storage run travels with the back wall
    return "move" if cy<S else "stay"
def stretch_back(o):
    mw=o.matrix_world; inv=mw.inverted()
    for v in o.data.vertices:
        w=mw@v.co
        if w.y<S: w.y-=D; v.co=inv@w
    o.data.update()
st={"stay":0,"move":0,"stretch":0}
for c in cols:
    for o in list(c.objects):
        if o.type not in("MESH","CURVE","FONT") or o.name.startswith(("East wall patch","MZ landing")): continue
        r=classify(o,ext(o))
        if r=="move":
            if o.parent: raise SystemExit("parented object: "+o.name)
            o.location.y-=D
        elif r=="stretch":
            if o.type!="MESH": raise SystemExit("cannot stretch non-mesh: "+o.name)
            stretch_back(o)
        st[r]+=1
moved=0
for l in bpy.data.objects:
    if l.type=="LIGHT":
        p=l.matrix_world.translation
        if -4.8<=p.x<=2.2 and 5.0<=p.z<=9.6 and -10.6<=p.y<S: l.location.y-=D; moved+=1
print("CR2 control room:",st,"lights moved",moved)
# ---------- 4. light for the new rear area (copy of the existing desk lamp, placed over the extension)
src=bpy.data.objects.get("LP control lamp")
if src:
    n=src.copy(); n.data=src.data.copy(); n.name="LP control lamp rear"; n.location=(-1.4,-10.6,8.55); src.users_collection[0].objects.link(n)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=DST)
