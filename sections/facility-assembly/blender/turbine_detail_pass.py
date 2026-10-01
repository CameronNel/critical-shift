"""Turbine room detail pass (additive derivative).

Usage:
  blender --background --disable-autoexec --python-exit-code 1 \
    --python sections/facility-assembly/blender/turbine_detail_pass.py -- OUT.blend [--render DIR]

Opens sources/turbine-room/module.blend, adds ~20 families of small props/wear in
a new collection '10 Detail pass', reusing the room's existing materials, and saves
to OUT.blend. It never writes the source module. Every family is built as ONE joined
mesh (low draw-call/object count) with sharp, flat-shaded Valorant-style facets.
Placement avoids existing geometry with an AABB test.
"""
import sys, math, random, os
import bpy, bmesh
from mathutils import Vector, Matrix

SRC = os.path.join(os.path.dirname(__file__), '..', 'sources', 'turbine-room', 'module.blend')
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = argv[0] if argv else '/tmp/turbine_detail.blend'
RENDER = argv[argv.index('--render') + 1] if '--render' in argv else None
rnd = random.Random(7)

bpy.ops.wm.open_mainfile(filepath=os.path.abspath(SRC))
M = {m.name: m for m in bpy.data.materials}
CONC, OIL, STEEL = M['Dense cast concrete'], M['Dry mineral oil residue'], M['Machined steel']
YEL, ORG, RED = M['Service ochre enamel'], M['Oxide orange enamel'], M['Emergency red enamel']
RUB, PAINT, IRON = M['Matte vulcanized rubber'], M['Maintenance enamel touchup'], M['Oiled iron']
WOOD, GLASS, PAPER = M['Worn beech work surface'], M['Warm diffusing glass'], M['Offwhite shift paper']
SLATE, JACKET, TERR = M['Old slate primer exposed at impacts'], M['Thermal jacket warm grey'], M['Dry worn terrazzo concrete']
PRIMER = M['Exposed old primer']

# ---- existing-geometry AABBs for collision rejection --------------------------
taken = []
for o in bpy.data.objects:
    if o.type != 'MESH' or max(o.dimensions) > 8 or not o.visible_get():
        continue
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    taken.append((Vector((min(v[i] for v in bb) for i in range(3))), Vector((max(v[i] for v in bb) for i in range(3)))))

def free(lo, hi, pad=0.12):
    for a, b in taken:
        if all(lo[i] - pad < b[i] and hi[i] + pad > a[i] for i in range(3)):
            return False
    return True

def claim(lo, hi):
    taken.append((Vector(lo), Vector(hi)))

# ---- family builders ---------------------------------------------------------
class Fam:
    def __init__(self, name):
        self.name, self.bm, self.mats = name, bmesh.new(), []
    def mi(self, mat):
        if mat not in self.mats: self.mats.append(mat)
        return self.mats.index(mat)
    def box(self, c, s, mat, rz=0.0, rx=0.0):
        m = bmesh.ops.create_cube(self.bm, size=1.0)
        vs = m['verts']
        mx = Matrix.Translation(c) @ Matrix.Rotation(rz, 4, 'Z') @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Diagonal((s[0], s[1], s[2], 1))
        bmesh.ops.transform(self.bm, matrix=mx, verts=vs)
        i = self.mi(mat)
        for f in {f for v in vs for f in v.link_faces}: f.material_index = i
    def cyl(self, c, r, h, mat, axis='Z', seg=8, r2=None):
        m = bmesh.ops.create_cone(self.bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
        vs = m['verts']
        rot = {'Z': Matrix.Identity(4), 'X': Matrix.Rotation(math.pi / 2, 4, 'Y'), 'Y': Matrix.Rotation(math.pi / 2, 4, 'X')}[axis]
        bmesh.ops.transform(self.bm, matrix=Matrix.Translation(c) @ rot, verts=vs)
        i = self.mi(mat)
        for f in {f for v in vs for f in v.link_faces}: f.material_index = i
    def tube(self, a, b, r, mat, seg=4):
        a, b = Vector(a), Vector(b); d = b - a
        m = bmesh.ops.create_cone(self.bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length)
        vs = m['verts']
        rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
        bmesh.ops.transform(self.bm, matrix=Matrix.Translation((a + b) / 2) @ rot, verts=vs)
        i = self.mi(mat)
        for f in {f for v in vs for f in v.link_faces}: f.material_index = i
    def decal(self, c, sx, sy, mat, rz=0.0, z=0.004):
        self.box((c[0], c[1], z), (sx, sy, 0.004), mat, rz)
    def finish(self, coll):
        bm = self.bm
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        me = bpy.data.meshes.new(self.name)
        bm.to_mesh(me); bm.free()
        for f in me.polygons: f.use_smooth = False   # sharp, flat-shaded
        for m in self.mats: me.materials.append(m)
        # simple box-projected UVs so the room's procedural/bake workflow has a layer
        uv = me.uv_layers.new(name='UVMap')
        for l in me.loops:
            n = me.polygons[l.index // 1 if False else 0].normal  # placeholder, replaced below
        for p in me.polygons:
            n = p.normal; ax = max(range(3), key=lambda i: abs(n[i])); u, v = [i for i in range(3) if i != ax]
            for li in p.loop_indices:
                co = me.vertices[me.loops[li].vertex_index].co
                uv.data[li].uv = (co[u], co[v])
        ob = bpy.data.objects.new(self.name, me)
        coll.objects.link(ob)
        return len(me.polygons)

coll = bpy.data.collections.new('10 Detail pass')
bpy.context.scene.collection.children.link(coll)
tri_budget = {}

# floor free-spot finder: returns (x,y) with an unoccupied footprint
def spot(sx, sy, h=0.6, region=((-3.6, 9.6), (0.8, 23.2)), tries=400):
    for _ in range(tries):
        x, y = rnd.uniform(*region[0]), rnd.uniform(*region[1])
        lo, hi = (x - sx / 2, y - sy / 2, 0.0), (x + sx / 2, y + sy / 2, h)
        if free(lo, hi):
            claim(lo, hi); return x, y
    return None

# 1. worn-floor scuff / oil decals ------------------------------------------
f = Fam('Detail floor wear')
for _ in range(70):
    x, y = rnd.uniform(-3.8, 9.8), rnd.uniform(0.3, 23.7)
    f.decal((x, y), rnd.uniform(.3, 1.4), rnd.uniform(.2, .9), rnd.choice([OIL, SLATE, PRIMER, CONC]), rnd.uniform(0, 3.1), z=0.003 + rnd.random() * .002)
# 2. broken / chipped floor tiles -------------------------------------------
for _ in range(14):
    x, y = rnd.uniform(-3.6, 9.6), rnd.uniform(0.6, 23.4)
    f.box((x, y, 0.004), (0.5, 0.5, 0.008), PRIMER, rnd.uniform(0, 3.1))           # exposed substrate
    for k in range(3):
        f.box((x + rnd.uniform(-.2, .2), y + rnd.uniform(-.2, .2), 0.02), (rnd.uniform(.08, .2), rnd.uniform(.08, .2), 0.03), TERR, rnd.uniform(0, 3.1), rnd.uniform(-.25, .25))  # raised broken shards
# 14. hazard-stripe edging along walkways -----------------------------------
for y0 in (1.6, 22.2):
    for i in range(10):
        f.box((-3.4 + i * 0.5, y0, 0.005), (0.25, 0.14, 0.006), YEL, 0.5)
        f.box((-3.4 + i * 0.5 + .25, y0, 0.005), (0.25, 0.14, 0.006), SLATE, 0.5)
tri_budget[f.name] = f.finish(coll)

# 3. floor cable runs with yellow ramp protectors ---------------------------
f = Fam('Detail floor cables')
def cable_path(pts, r=0.035):
    for a, b in zip(pts, pts[1:]):
        f.tube((a[0], a[1], r), (b[0], b[1], r), r, RUB, 6)
for _ in range(6):
    x0, y0 = rnd.uniform(-3.5, 9), rnd.uniform(1, 22)
    pts = [(x0, y0), (x0 + rnd.uniform(-2, 2), y0 + rnd.uniform(1, 4)), (x0 + rnd.uniform(-2, 2), y0 + rnd.uniform(4, 7))]
    if all(free((p[0] - .1, p[1] - .1, 0), (p[0] + .1, p[1] + .1, .1), .05) for p in pts):
        cable_path(pts)
        for a, b in zip(pts, pts[1:]):
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); ang = math.atan2(b[1] - a[1], b[0] - a[0])
            f.box((m[0], m[1], 0.03), (0.35, 0.22, 0.05), YEL, ang)
tri_budget[f.name] = f.finish(coll)

# 4. hanging, drooping ceiling cable bundles --------------------------------
f = Fam('Detail hanging cables')
for _ in range(9):
    x, y = rnd.uniform(-3, 9), rnd.uniform(1, 23)
    z = 7.1; n = 7; sag = rnd.uniform(.5, 1.1); dx, dy = rnd.uniform(-2.5, 2.5), rnd.uniform(1.5, 3.5)
    prev = None
    for i in range(n + 1):
        t = i / n; p = (x + dx * t, y + dy * t, z - sag * 4 * t * (1 - t) - 0.5 * t)
        if prev:
            f.tube(prev, p, 0.03, RUB, 5)
            if i % 3 == 0: f.box(p, (.1, .1, .05), STEEL)
        prev = p
tri_budget[f.name] = f.finish(coll)

# 5/19/15. wall furniture: sockets, junction boxes, extinguishers, signs, pegboards, hose reels
f = Fam('Detail wall fittings')
def wall_spot(sx, sz, z, tries=300):
    for _ in range(tries):
        side = rnd.choice(['W', 'E', 'S', 'N'])
        if side in 'WE':
            y = rnd.uniform(1.0, 23.0); x = -3.97 if side == 'W' else 9.97; lo, hi = (x - .15, y - sx / 2, z - sz / 2), (x + .15, y + sx / 2, z + sz / 2)
        else:
            x = rnd.uniform(-3.4, 9.4); y = 0.03 if side == 'S' else 23.97
            if abs(x) < 1.8: continue
            lo, hi = (x - sx / 2, y - .15, z - sz / 2), (x + sx / 2, y + .15, z + sz / 2)
        if free(lo, hi, 0.08):
            claim(lo, hi); return side, (x, y)
    return None
def place(side, p, depth, lx, ly, lz):
    # local x along wall, y out of wall, z up -> world
    if side == 'W': return (p[0] + ly, p[1] + lx, lz)
    if side == 'E': return (p[0] - ly, p[1] - lx, lz)
    if side == 'S': return (p[0] + lx, p[1] + ly, lz)
    return (p[0] - lx, p[1] - ly, lz)
def rot(side): return {'W': math.pi / 2, 'E': math.pi / 2, 'S': 0, 'N': 0}[side]
def wbox(side, p, lx, ly, lz, s, mat):  # s=(along wall, depth, height)
    sw = (s[1], s[0], s[2]) if side in 'WE' else s
    f.box(place(side, p, 0, lx, ly, lz), sw, mat)
for _ in range(14):    # 5. power sockets / plugs with plugged leads
    w = wall_spot(.3, .3, 0.5)
    if not w: continue
    s, p = w
    wbox(s, p, 0, .02, .5, (.16, .05, .16), PAINT); wbox(s, p, 0, .06, .5, (.1, .03, .1), STEEL)
    wbox(s, p, -.025, .08, .5, (.02, .02, .03), STEEL); wbox(s, p, .025, .08, .5, (.02, .02, .03), STEEL)
    if rnd.random() < .5:
        wbox(s, p, 0, .12, .5, (.07, .07, .09), RED); f.tube(place(s, p, 0, 0, .15, .5), place(s, p, 0, rnd.uniform(-.4, .4), .4, .05), .02, RUB, 5)
for _ in range(8):    # junction boxes with conduit drops
    w = wall_spot(.5, .7, 1.7)
    if not w: continue
    s, p = w
    wbox(s, p, 0, .08, 1.7, (.4, .15, .5), IRON); wbox(s, p, 0, .17, 1.7, (.3, .03, .4), PAINT)
    f.tube(place(s, p, 0, .1, .1, 1.45), place(s, p, 0, .1, .1, .0), .025, STEEL, 6)
for _ in range(3):    # 15. fire extinguishers + brackets
    w = wall_spot(.35, .8, 1.1)
    if not w: continue
    s, p = w
    wbox(s, p, 0, .06, 1.1, (.1, .02, .5), STEEL)
    c = place(s, p, 0, 0, .12, 1.0); f.cyl(c, .09, .5, RED, 'Z', 8); f.cyl((c[0], c[1], 1.3), .035, .08, STEEL, 'Z', 6)
for _ in range(6):    # 19. warning / info signs
    w = wall_spot(.6, .45, 2.4)
    if not w: continue
    s, p = w
    wbox(s, p, 0, .03, 2.4, (.5, .02, .35), YEL); wbox(s, p, 0, .045, 2.4, (.42, .01, .05), SLATE); wbox(s, p, 0, .045, 2.3, (.3, .01, .04), SLATE)
for _ in range(2):    # 9. tool pegboard + hanging tools
    w = wall_spot(1.2, 1.0, 1.5)
    if not w: continue
    s, p = w
    wbox(s, p, 0, .04, 1.5, (1.1, .04, .9), WOOD)
    for i in range(5):
        lx = -.45 + i * .22
        wbox(s, p, lx, .09, 1.6, (.035, .03, .4), STEEL); wbox(s, p, lx, .09, 1.35, (.07, .03, .08), STEEL)   # wrench
        wbox(s, p, lx, .09, 1.15, (.045, .04, .22), ORG if i % 2 else YEL)                                      # screwdriver
for _ in range(2):    # 16. hose reel
    w = wall_spot(.8, .8, 1.2)
    if not w: continue
    s, p = w
    c = place(s, p, 0, 0, .25, 1.2)
    if s in 'WE': f.cyl(c, .35, .22, RED, 'X', 8); f.cyl(c, .12, .3, STEEL, 'X', 6)
    else: f.cyl(c, .35, .22, RED, 'Y', 8); f.cyl(c, .12, .3, STEEL, 'Y', 6)
tri_budget[f.name] = f.finish(coll)

# 6. scaffolding bay ----------------------------------------------------------
f = Fam('Detail scaffolding')
sc = spot(2.6, 1.4, 3.0, region=((-3.6, -1.5), (2.5, 21.5)))
if sc:
    x, y = sc; w, d, h = 2.4, 1.2, 3.0
    for ix in (-w / 2, w / 2):
        for iy in (-d / 2, d / 2):
            f.tube((x + ix, y + iy, 0), (x + ix, y + iy, h), .032, STEEL, 6)
    for z in (0.4, 1.5, 2.6):
        for iy in (-d / 2, d / 2): f.tube((x - w / 2, y + iy, z), (x + w / 2, y + iy, z), .028, STEEL, 6)
        for ix in (-w / 2, w / 2): f.tube((x + ix, y - d / 2, z), (x + ix, y + d / 2, z), .028, STEEL, 6)
    for z in (1.5, 2.6):
        f.box((x, y, z + .04), (w, d, .05), WOOD)
    for iy in (-d / 2, d / 2): f.tube((x - w / 2, y + iy, .4), (x + w / 2, y + iy, 2.6), .02, STEEL, 4)   # diagonal brace
    f.box((x + .5, y, 1.58), (.5, .3, .2), ORG); f.tube((x - .4, y + .3, 2.65), (x - 1.1, y + .8, .05), .02, RUB, 5)  # bucket + dangling rope
tri_budget[f.name] = f.finish(coll)

# 7. desks with chairs, papers, lamps ---------------------------------------
f = Fam('Detail desks')
for _ in range(3):
    sp = spot(1.6, .9, 1.0)
    if not sp: continue
    x, y = sp; a = rnd.choice([0, math.pi / 2])
    def L(lx, ly): return (x + lx * math.cos(a) - ly * math.sin(a), y + lx * math.sin(a) + ly * math.cos(a))
    f.box((x, y, .74), (1.4, .7, .05), WOOD, a)
    for lx, ly in ((-.65, -.3), (.65, -.3), (-.65, .3), (.65, .3)):
        p = L(lx, ly); f.box((p[0], p[1], .36), (.05, .05, .72), STEEL)
    p = L(.3, 0); f.box((p[0], p[1], .77), (.3, .22, .01), PAPER, a + rnd.uniform(-.4, .4))
    p = L(-.5, .2); f.cyl((p[0], p[1], .8), .05, .04, STEEL, 'Z', 6); f.tube((p[0], p[1], .8), (p[0] + .1, p[1], 1.1), .01, STEEL, 4); f.box((p[0] + .13, p[1], 1.12), (.12, .06, .04), YEL)
    p = L(0, -.65); f.box((p[0], p[1], .45), (.4, .4, .05), RUB, a); f.box((p[0], p[1] - .17 * math.cos(a), .72), (.4, .05, .4), RUB, a)  # chair
    f.cyl((p[0], p[1], .22), .04, .45, STEEL, 'Z', 6)
tri_budget[f.name] = f.finish(coll)

# 8. ceiling strip light fixtures (mesh only; existing area lights keep the lighting) --
f = Fam('Detail ceiling fixtures')
for y in (3, 8, 13, 18, 22):
    for x in (-1.5, 5, 8.5):
        if free((x - .6, y - .1, 6.4), (x + .6, y + .1, 7.0), .05):
            f.box((x, y, 6.9), (1.2, .18, .08), STEEL); f.box((x, y, 6.84), (1.1, .12, .02), GLASS)
            f.tube((x - .5, y, 6.95), (x - .5, y, 7.15), .01, STEEL, 4); f.tube((x + .5, y, 6.95), (x + .5, y, 7.15), .01, STEEL, 4)
# 17. roof damage: sagging / missing panels, stains and exposed purlins
for _ in range(6):
    x, y = rnd.uniform(-3, 9), rnd.uniform(1, 23)
    f.box((x, y, 7.17), (rnd.uniform(.8, 1.4), rnd.uniform(.6, 1.1), .02), SLATE, rnd.uniform(0, 3))          # stain patch on ceiling
    f.box((x + .3, y, 6.95), (.9, .5, .02), IRON, rnd.uniform(-.3, .3), rnd.uniform(.35, .6))                  # hanging loose panel
    f.tube((x - .3, y - .3, 7.15), (x + .6, y + .4, 7.15), .035, STEEL, 4)                                      # exposed purlin through gap
tri_budget[f.name] = f.finish(coll)

# 10/11/12/13/18/20 floor props ----------------------------------------------
f = Fam('Detail floor props')
def pallet(x, y, rz=0):
    for dx in (-.4, 0, .4): f.box((x + dx, y, .06), (.1, .8, .1), WOOD, rz)
    for dy in (-.3, 0, .3): f.box((x, y + dy, .13), (1.0, .12, .03), WOOD, rz)
for _ in range(4):   # 12. pallets with crates
    sp = spot(1.1, 0.9, 1.4)
    if not sp: continue
    x, y = sp; pallet(x, y)
    for k in range(rnd.randint(1, 3)):
        f.box((x + rnd.uniform(-.1, .1), y, .3 + .32 * k), (.7, .6, .3), rnd.choice([WOOD, ORG, IRON]), rnd.uniform(-.1, .1))
for _ in range(7):   # 11. oil drums (some tipped, some leaking)
    sp = spot(.6, .6, .9)
    if not sp: continue
    x, y = sp; c = rnd.choice([RED, YEL, STEEL, ORG])
    if rnd.random() < .25:
        f.cyl((x, y, .27), .27, .85, c, 'X', 8); f.decal((x + .7, y), .9, .7, OIL, 0, z=.005)
    else:
        f.cyl((x, y, .45), .27, .9, c, 'Z', 8); f.cyl((x, y, .91), .27, .03, STEEL, 'Z', 8); f.box((x, y, .6), (.56, .56, .04), STEEL)
for _ in range(3):   # 20. gas cylinders in a rack + trolley
    sp = spot(.9, .5, 1.5)
    if not sp: continue
    x, y = sp
    for k in range(2):
        f.cyl((x - .2 + .4 * k, y, .7), .1, 1.3, [ORG, STEEL][k], 'Z', 8); f.cyl((x - .2 + .4 * k, y, 1.4), .05, .1, STEEL, 'Z', 6)
    f.box((x, y, .04), (.9, .4, .04), IRON); f.box((x, y, .6), (.85, .03, .05), YEL)
for _ in range(3):   # 10. loose tools on the floor
    sp = spot(.8, .5, .2)
    if not sp: continue
    x, y = sp; a = rnd.uniform(0, 3.1)
    f.box((x, y, .02), (.5, .04, .03), STEEL, a); f.box((x + .25 * math.cos(a), y + .25 * math.sin(a), .02), (.1, .1, .03), STEEL, a)   # wrench
    f.box((x + .2, y + .2, .03), (.3, .05, .05), WOOD, a + 1); f.box((x + .2 + .15 * math.cos(a + 1), y + .2 + .15 * math.sin(a + 1), .04), (.1, .06, .06), STEEL, a + 1)  # hammer
f.tube((0, 0, 0), (0, 0, 0), .001, STEEL, 3)
# 18. ladder leaning on the east wall
lx = spot(.5, 1.0, 2.8, region=((8.3, 9.4), (2, 22)))
if lx:
    x, y = lx
    for dy in (-.25, .25): f.tube((x + .1, y + dy, 0), (x + .75, y + dy, 2.6), .022, ORG, 4)
    for k in range(8): z = .3 + k * .3; f.tube((x + .1 + .65 * z / 2.6, y - .25, z), (x + .1 + .65 * z / 2.6, y + .25, z), .015, STEEL, 4)
# 13. broken pipe: dangling flanged stub with puddle
sp = spot(1.2, 1.2, 4.0, region=((-3.6, 9.6), (1, 23)))
if sp:
    x, y = sp
    f.cyl((x, y, 3.7), .14, 1.0, JACKET, 'Z', 8); f.cyl((x, y, 3.2), .2, .05, IRON, 'Z', 8)
    f.tube((x, y, 3.2), (x + .5, y + .2, 2.6), .12, JACKET, 6); f.box((x + .55, y + .22, 2.55), (.35, .1, .3), PRIMER, .4, .5)
    f.decal((x + .5, y + .2), 1.1, .8, OIL, 0.3, z=.006)
tri_budget[f.name] = f.finish(coll)

# ---- bookkeeping --------------------------------------------------------------
bpy.context.scene['detail_pass_tris'] = int(sum(tri_budget.values()))
print('FAMILY_FACES', tri_budget)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(OUT), compress=True)

if RENDER:
    os.makedirs(RENDER, exist_ok=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'MATERIAL'
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    for name in ('C01', 'C03', 'C05', 'W02'):
        cam = next((o for o in bpy.data.objects if o.type == 'CAMERA' and o.name.startswith(name)), None)
        if cam:
            sc.camera = cam; sc.render.filepath = os.path.join(RENDER, name + '.png'); bpy.ops.render.render(write_still=True)
