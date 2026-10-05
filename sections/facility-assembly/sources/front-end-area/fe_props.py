"""Prop prototypes. Each returns a mesh object built in a bmesh; instances are linked duplicates sharing mesh data."""
from fe_common import *
import mathutils.noise as mnoise

def bm_box(bm, cx, cy, cz, sx, sy, sz, rz=0.0, bevel=0.0, seg=1):
    r = bmesh.ops.create_cube(bm, size=1.0)
    verts = r['verts']
    rot = Matrix.Rotation(rz, 4, 'Z')
    for v in verts:
        p = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz)); p = rot @ p
        v.co = Vector((cx + p.x, cy + p.y, cz + p.z))
    if bevel > 0:
        edges = {e for v in verts for e in v.link_edges}
        bmesh.ops.bevel(bm, geom=list(edges), offset=min(bevel, 0.45 * min(sx, sy, sz)), segments=seg, affect='EDGES')
    return verts

def bm_cyl(bm, cx, cy, z0, z1, r, seg=16, r2=None, axis='z', rz=0.0):
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=(r if r2 is None else r2), depth=(z1 - z0))
    for v in res['verts']:
        p = v.co.copy(); p.z += (z0 + z1) / 2
        if axis == 'x': p = Vector((p.z - (z0 + z1) / 2 + 0, p.y, p.x)) if False else p
        v.co = Vector((cx + p.x, cy + p.y, p.z))
    return res['verts']

def bm_cyl_h(bm, cx, cy, cz, length, r, seg=16, rz=0.0):
    """Horizontal cylinder along X rotated by rz about Z, centre (cx,cy,cz)."""
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r, depth=length)
    rot = Matrix.Rotation(rz, 4, 'Z'); rx = Matrix.Rotation(math.pi / 2, 4, 'Y')
    for v in res['verts']:
        p = rot @ (rx @ v.co); v.co = Vector((cx + p.x, cy + p.y, cz + p.z))
    return res['verts']

def bm_torus(bm, cx, cy, cz, R, r, ns=18, nt=10, tilt=True):
    rings = []
    for i in range(ns):
        a = 2 * math.pi * i / ns; ring = []
        for j in range(nt):
            b = 2 * math.pi * j / nt
            x = (R + r * math.cos(b)) * math.cos(a); y = (R + r * math.cos(b)) * math.sin(a); z = r * math.sin(b)
            p = Vector((x, z, y)) if tilt else Vector((x, y, z))
            ring.append(bm.verts.new(Vector((cx + p.x, cy + p.y, cz + p.z))))
        rings.append(ring)
    for i in range(ns):
        for j in range(nt):
            a, b = rings[i][j], rings[i][(j + 1) % nt]; c, d = rings[(i + 1) % ns][(j + 1) % nt], rings[(i + 1) % ns][j]
            try: bm.faces.new((a, b, c, d))
            except ValueError: pass

def bm_blob(bm, cx, cy, cz, rx, ry, rz, sub=2, jitter=0.12, seed=0):
    res = bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    rnd = random.Random(seed)
    for v in res['verts']:
        k = 1.0 + rnd.uniform(-jitter, jitter)
        v.co = Vector((cx + v.co.x * rx * k, cy + v.co.y * ry * k, cz + v.co.z * rz * k))
    return res['verts']

def finish(name, bm, mat, coll, rgba, smooth=False):
    o = mesh_obj(name, bm, mat, coll, rgba, smooth=smooth); o.hide_viewport = False; return o

# --------------------------------------------------------------------- prototypes
def proto_crate(F, coll, variant):
    bm = bmesh.new(); w = 1.0; h = 1.0
    cols = [(0.52, 0.38, 0.22, 1), (0.40, 0.46, 0.34, 1), (0.60, 0.50, 0.30, 1), (0.30, 0.34, 0.38, 1)]
    bm_box(bm, 0, 0, h / 2, 0.92, 0.92, 0.92)               # core
    for sx in (-1, 1):
        for sy in (-1, 1): bm_box(bm, sx * 0.46, sy * 0.46, h / 2, 0.08, 0.08, h, bevel=0.008)
    for z in (0.04, h - 0.04):
        bm_box(bm, 0, 0, z, 1.0, 1.0, 0.08, bevel=0.008)
    for i in range(3):
        z = 0.28 + i * 0.22
        for sx in (-1, 1): bm_box(bm, sx * 0.48, 0, z, 0.03, 0.88, 0.14, bevel=0.004)
        for sy in (-1, 1): bm_box(bm, 0, sy * 0.48, z, 0.88, 0.03, 0.14, bevel=0.004)
    return finish(f'proto_crate_{variant}', bm, F['props'], coll, cols[variant % 4])

def proto_pallet(F, coll):
    bm = bmesh.new()
    for i in range(5): bm_box(bm, 0, -0.45 + i * 0.225, 0.14, 1.2, 0.1, 0.022, bevel=0.003)
    for i in range(3):
        bm_box(bm, -0.55 + i * 0.55, 0, 0.075, 0.1, 1.0, 0.09, bevel=0.004)
        bm_box(bm, -0.55 + i * 0.55, 0, 0.005, 0.1, 0.9, 0.02)
    for i in range(3): bm_box(bm, 0, -0.45 + i * 0.45, 0.025, 1.2, 0.1, 0.02, bevel=0.003)
    return finish('proto_pallet', bm, F['timber'], coll, None)

def proto_barrel(F, coll, rgba):
    bm = bmesh.new()
    bm_cyl(bm, 0, 0, 0.0, 0.9, 0.3, seg=24)
    for z in (0.15, 0.45, 0.75): bm_cyl(bm, 0, 0, z - 0.02, z + 0.02, 0.312, seg=24)
    bm_cyl(bm, 0, 0, 0.9, 0.93, 0.27, seg=24)
    bm_cyl(bm, 0.12, 0.08, 0.93, 0.96, 0.04, seg=10)
    return finish('proto_barrel', bm, F['props'], coll, rgba)

def proto_drum(F, coll):
    bm = bmesh.new()
    bm_cyl(bm, 0, 0, 0, 0.9, 0.55, seg=28)
    for z in (0.12, 0.45, 0.78): bm_cyl(bm, 0, 0, z - 0.03, z + 0.03, 0.575, seg=28)
    bm_cyl(bm, 0, 0, 0.9, 0.93, 0.5, seg=28)
    return finish('proto_drum', bm, F['props'], coll, (0.32, 0.34, 0.36, 1))

def proto_cable_drum(F, coll):
    bm = bmesh.new()
    for z in (0.02, 0.88): bm_cyl(bm, 0, 0, z, z + 0.1, 0.55, seg=24)
    bm_cyl(bm, 0, 0, 0.12, 0.88, 0.25, seg=20)
    bm_cyl(bm, 0, 0, 0.12, 0.88, 0.36, seg=20)
    bm_cyl(bm, 0, 0, 0.0, 1.0, 0.04, seg=8)
    return finish('proto_cable_drum', bm, F['timber'], coll, None)

def proto_tyre(F, coll):
    bm = bmesh.new(); bm_torus(bm, 0, 0, 0.17, 0.33, 0.17, ns=20, nt=10, tilt=False)
    return finish('proto_tyre', bm, F['rubber'], coll, None)

def proto_cone(F, coll):
    bm = bmesh.new(); bm_box(bm, 0, 0, 0.015, 0.34, 0.34, 0.03, bevel=0.004); bm_cyl(bm, 0, 0, 0.03, 0.66, 0.13, seg=16, r2=0.02)
    bm_cyl(bm, 0, 0, 0.3, 0.38, 0.086, seg=16, r2=0.075)
    return finish('proto_cone', bm, F['plastic'], coll, (0.95, 0.4, 0.05, 1))

def proto_bollard(F, coll):
    bm = bmesh.new(); bm_cyl(bm, 0, 0, 0, 0.9, 0.09, seg=14); bm_cyl(bm, 0, 0, 0.82, 0.88, 0.1, seg=14)
    bm_cyl(bm, 0, 0, 0.55, 0.6, 0.095, seg=14)
    return finish('proto_bollard', bm, F['plastic'], coll, (0.9, 0.7, 0.05, 1))

def proto_bench(F, coll):
    bm = bmesh.new()
    for i in range(5): bm_box(bm, 0, -0.18 + i * 0.09, 0.45, 1.6, 0.07, 0.035, bevel=0.004)
    for i in range(3): bm_box(bm, 0, 0.2 + i * 0.1, 0.62 + i * 0.12, 1.6, 0.03, 0.08, bevel=0.004)
    for sx in (-0.7, 0.7):
        bm_box(bm, sx, 0, 0.22, 0.06, 0.5, 0.44, bevel=0.005); bm_box(bm, sx, 0.22, 0.65, 0.06, 0.05, 0.6, bevel=0.005)
    return finish('proto_bench', bm, F['timber'], coll, None)

def proto_shrub(F, coll, seed):
    bm = bmesh.new(); rnd = random.Random(seed)
    for i in range(3):
        bm_blob(bm, rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), 0.35 + rnd.uniform(0, 0.25), rnd.uniform(0.35, 0.55), rnd.uniform(0.35, 0.55), rnd.uniform(0.3, 0.5), sub=3, jitter=0.18, seed=seed * 7 + i)
    return finish(f'proto_shrub_{seed}', bm, F['foliage'], coll, (0.30 + 0.03 * seed, 0.25, 0.09, 1), smooth=True)

def proto_tree(F, coll, seed):
    bm = bmesh.new(); rnd = random.Random(seed)
    bm_cyl(bm, 0, 0, 0, 3.2, 0.14, seg=10, r2=0.09); bm_cyl(bm, 0.2, 0, 2.2, 3.6, 0.07, seg=8, r2=0.05)
    for i in range(5):
        bm_blob(bm, rnd.uniform(-0.8, 0.8), rnd.uniform(-0.8, 0.8), 3.4 + rnd.uniform(0, 1.3), rnd.uniform(0.9, 1.4), rnd.uniform(0.9, 1.4), rnd.uniform(0.8, 1.1), sub=3, jitter=0.22, seed=seed * 11 + i)
    return finish(f'proto_tree_{seed}', bm, F['foliage'], coll, (0.20, 0.16, 0.08, 1), smooth=True)

def proto_pole(F, coll):
    bm = bmesh.new()
    bm_cyl(bm, 0, 0, 0, 0.25, 0.14, seg=12, r2=0.1); bm_cyl(bm, 0, 0, 0.25, 5.0, 0.08, seg=12, r2=0.06)
    bm_box(bm, 0.45, 0, 5.0, 1.0, 0.1, 0.08, bevel=0.01); bm_box(bm, 0.85, 0, 4.92, 0.4, 0.22, 0.1, bevel=0.015)
    return finish('proto_pole', bm, F['steel_charcoal'], coll, None)

def proto_lamp_glow(F, coll):
    bm = bmesh.new(); bm_box(bm, 0.88, 0, 4.86, 0.3, 0.16, 0.03)
    return finish('proto_lamp_glow', bm, F['emissive'], coll, (1.0, 0.85, 0.6, 1))

def proto_scrap(F, coll, seed):
    bm = bmesh.new(); rnd = random.Random(seed)
    for i in range(26):
        kind = rnd.choice(('beam', 'plate', 'pipe', 'beam'))
        x, y = rnd.uniform(-0.9, 0.9), rnd.uniform(-0.6, 0.6); z = rnd.uniform(0.05, 0.7); rz = rnd.uniform(0, math.pi)
        if kind == 'beam': bm_box(bm, x, y, z, rnd.uniform(1.0, 2.0), 0.12, 0.2, rz=rz, bevel=0.01)
        elif kind == 'plate': bm_box(bm, x, y, z, rnd.uniform(0.6, 1.2), rnd.uniform(0.5, 0.9), 0.03, rz=rz, bevel=0.004)
        else: bm_cyl_h(bm, x, y, z, rnd.uniform(0.8, 1.6), 0.07, seg=10, rz=rz)
    return finish(f'proto_scrap_{seed}', bm, F['steel_rust'], coll, None)

def proto_tarp(F, coll, seed):
    bm = bmesh.new(); res = bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0); rnd = random.Random(seed)
    for v in res['verts']:
        z = max(v.co.z, 0.0)
        n = mnoise.noise(Vector((v.co.x * 2.2 + seed, v.co.y * 2.2, z * 2.2)))
        v.co = Vector((v.co.x * 1.0, v.co.y * 0.8, z * 0.8 * (1.0 + 0.2 * n)))
    return finish(f'proto_tarp_{seed}', bm, F['props'], coll, (0.25, 0.42, 0.28, 1), smooth=True)

def proto_cart(F, coll):
    bm = bmesh.new()
    bm_box(bm, 0, 0, 0.62, 2.3, 1.2, 0.07, bevel=0.01)                     # floor
    for sy in (-1, 1): bm_box(bm, 0, sy * 0.6, 0.95, 2.3, 0.06, 0.7, bevel=0.01)
    for sx in (-1, 1): bm_box(bm, sx * 1.15, 0, 0.95, 0.06, 1.2, 0.7, bevel=0.01)
    for z in (0.62 + 0.3, 0.62 + 0.62): bm_box(bm, 0, 0, z + 0.04, 2.4, 1.3, 0.05, bevel=0.01) if False else None
    bm_box(bm, 0, 0, 1.32, 2.4, 1.3, 0.05, bevel=0.01)
    for sx in (-0.75, 0.75):
        for sy in (-0.66, 0.66): bm_cyl_h(bm, sx, sy, 0.3, 0.07, 0.3, seg=18, rz=math.pi / 2)
        bm_cyl_h(bm, sx, 0, 0.3, 1.3, 0.035, seg=8, rz=math.pi / 2)
    bm_box(bm, 1.5, 0, 0.5, 0.5, 0.06, 0.05); bm_box(bm, -1.5, 0, 0.5, 0.5, 0.06, 0.05)
    for sy in (-1, 1): bm_box(bm, 0, sy * 0.35, 0.62 - 0.1, 2.0, 0.08, 0.14)
    return finish('proto_cart', bm, F['steel_rust'], coll, None)

def proto_generator(F, coll):
    bm = bmesh.new()
    bm_box(bm, 0, 0, 0.9, 3.0, 1.6, 1.5, bevel=0.03)
    for i in range(12): bm_box(bm, -1.35 + i * 0.25, 0.805, 0.95, 0.1, 0.02, 0.9)
    for sx in (-1, 1): bm_box(bm, sx * 1.2, 0, 0.08, 0.2, 1.7, 0.16, bevel=0.01)
    bm_cyl(bm, 1.1, -0.5, 1.65, 2.4, 0.09, seg=12); bm_cyl(bm, 1.1, -0.5, 2.4, 2.45, 0.14, seg=12)
    bm_box(bm, -0.8, 0.8, 1.55, 0.5, 0.05, 0.3, bevel=0.01)
    return finish('proto_generator', bm, F['steel_accent'], coll, None)

def proto_tank_v(F, coll, h=2.4, r=1.0):
    bm = bmesh.new()
    bm_cyl(bm, 0, 0, 0.3, h, r, seg=28); bm_cyl(bm, 0, 0, h, h + 0.12, r * 0.8, seg=28, r2=r * 0.5)
    for a in range(4): bm_box(bm, math.cos(a * math.pi / 2) * r * 0.8, math.sin(a * math.pi / 2) * r * 0.8, 0.15, 0.12, 0.12, 0.3)
    for z in (0.8, 1.5): bm_cyl(bm, 0, 0, z, z + 0.05, r * 1.02, seg=28)
    bm_box(bm, r + 0.05, 0, h * 0.5, 0.05, 0.5, h * 0.9)    # ladder rail
    for i in range(8): bm_box(bm, r + 0.06, 0, 0.5 + i * 0.28, 0.04, 0.4, 0.03)
    return finish('proto_tank_v', bm, F['steel_charcoal'], coll, None)

def proto_planter(F, coll):
    bm = bmesh.new()
    bm_box(bm, 0, 0, 0.3, 1.2, 1.2, 0.6, bevel=0.03)
    bm_box(bm, 0, 0, 0.58, 1.0, 1.0, 0.06)
    return finish('proto_planter', bm, F['concrete_slab'], coll, None)

def proto_soil(F, coll):
    bm = bmesh.new(); bm_box(bm, 0, 0, 0.6, 1.02, 1.02, 0.03)
    return finish('proto_soil', bm, F['props'], coll, (0.18, 0.12, 0.08, 1))


class MB:
    """Multi-material single-mesh builder: each part gets a material slot index and a vertex colour."""
    def __init__(self, mats):
        self.bm = bmesh.new(); self.mats = list(mats); self.layer = self.bm.loops.layers.float_color.new('Col'); self.mi = 0; self.rgba = (1, 1, 1, 1)
    def use(self, mi, rgba=(1, 1, 1, 1)): self.mi = mi; self.rgba = rgba; return self
    def _tag(self, before):
        for f in self.bm.faces:
            if f in before: continue
            f.material_index = self.mi
            for l in f.loops: l[self.layer] = self.rgba
    def _wrap(self, fn, *a, **k):
        before = set(self.bm.faces); r = fn(self.bm, *a, **k); self._tag(before); return r
    def box(self, *a, **k): return self._wrap(bm_box, *a, **k)
    def cyl(self, *a, **k): return self._wrap(bm_cyl, *a, **k)
    def cyl_h(self, *a, **k): return self._wrap(bm_cyl_h, *a, **k)
    def blob(self, *a, **k): return self._wrap(bm_blob, *a, **k)
    def torus(self, *a, **k): return self._wrap(bm_torus, *a, **k)
    def finish(self, name, coll, smooth=False):
        me = bpy.data.meshes.new(name); self.bm.to_mesh(me); self.bm.free()
        for m in self.mats: me.materials.append(m)
        if smooth:
            for p in me.polygons: p.use_smooth = True
        o = bpy.data.objects.new(name, me); coll.objects.link(o); return o
