"""Shared helpers for the turbine room rebuild.

Everything is built from flat-shaded, sharp-edged primitives whose faces are
UV-fitted into one swatch of a single painted atlas (UV0). A second UV layer
(UV1, 'LightmapUV') is generated later for the baked lightmaps.
"""
import math, random
import numpy as np
import bpy
from mathutils import Vector, Matrix, Euler

CELL, GRID, INSET = 128, 16, 9          # atlas 2048^2, 16x16 swatches, 9px safe border

# name: (hex, edge, dirt, noise, emissive)   edge>1 lightens edges (paint chipping), <1 darkens
PALETTE = {
    'ivory':        ('D8CDB6', 1.10, .10, .030, 0),
    'ivory_dirty':  ('BDB19A', 1.06, .20, .045, 0),
    'ivory_warm':   ('E3D2AE', 1.08, .08, .025, 0),
    'wainscot':     ('2F3A45', 1.18, .10, .030, 0),
    'wainscot_blue':('3A5568', 1.15, .10, .030, 0),
    'charcoal':     ('2B2F36', 1.25, .06, .030, 0),
    'black':        ('16181C', 1.35, .04, .020, 0),
    'steel_dark':   ('4A515B', 1.30, .08, .040, 0),
    'steel_mid':    ('7B848F', 1.25, .08, .040, 0),
    'steel_light':  ('A9B2BC', 1.15, .06, .035, 0),
    'steel_worn':   ('8E969E', 1.40, .18, .060, 0),
    'orange':       ('E27227', 1.20, .08, .030, 0),
    'orange_dark':  ('B7511B', 1.20, .14, .040, 0),
    'orange_worn':  ('C96A2E', 1.45, .24, .070, 0),
    'yellow':       ('F2B81C', 1.15, .08, .030, 0),
    'yellow_worn':  ('D6A01E', 1.40, .22, .060, 0),
    'red':          ('C2392B', 1.15, .08, .030, 0),
    'red_dark':     ('8E2A20', 1.15, .12, .035, 0),
    'concrete':     ('8D8B86', 1.05, .10, .050, 0),
    'concrete_dark':('6E6C68', 1.05, .14, .055, 0),
    'tile_a':       ('B4AFA4', .86, .05, .030, 0),
    'tile_b':       ('A7A296', .86, .06, .035, 0),
    'tile_c':       ('BDB8AC', .86, .05, .030, 0),
    'tile_worn':    ('938E83', .90, .20, .070, 0),
    'tile_oil':     ('5E564B', .92, .10, .060, 0),
    'tile_crack':   ('77726A', .92, .16, .060, 0),
    'grout':        ('3A3834', 1., .0, .02, 0),
    'backing':      ('1E2025', 1., .0, .02, 0),
    'primer':       ('6A4B3E', 1.2, .15, .06, 0),
    'rust':         ('8A4D2B', 1.1, .25, .09, 0),
    'rubber':       ('24262A', 1.2, .05, .03, 0),
    'wood':         ('A8794D', 1.15, .12, .05, 0),
    'wood_dark':    ('7A5436', 1.15, .15, .05, 0),
    'paper':        ('E7E2D4', 1.0, .05, .03, 0),
    'lagging':      ('9B968C', 1.12, .14, .05, 0),
    'lagging_dark': ('7D7971', 1.12, .18, .05, 0),
    'brass':        ('C79A3C', 1.2, .10, .04, 0),
    'oil':          ('2A2118', 1.0, .0, .04, 0),
    'chalk':        ('F2EFE6', 1.0, .02, .015, 0),
    'green':        ('5C7A66', 1.15, .08, .03, 0),
    'blue_panel':   ('4C6D8C', 1.15, .08, .03, 0),
    'sky':          ('9FC4D8', 1.0, .0, .02, 0),
    # emissive swatches
    'lamp':         ('FFE6B0', 1.0, 0., .01, 1),
    'screen':       ('FFB43E', 1.0, 0., .02, 1),
    'screen_cool':  ('BFE8FF', 1.0, 0., .02, 1),
    'led_red':      ('FF4A33', 1.0, 0., .01, 1),
    'led_green':    ('7DFF8A', 1.0, 0., .01, 1),
}
ORDER = list(PALETTE)
SWATCH = {n: i for i, n in enumerate(ORDER)}
EMISSIVE = {i for i, n in enumerate(ORDER) if PALETTE[n][4]}

def write_png(path, rgb):
    """Minimal 8-bit RGB PNG writer (bpy's Image.pixels.foreach_set is unreliable for 16M-element writes)."""
    import zlib, struct
    h, w, _ = rgb.shape
    raw = np.concatenate([np.zeros((h, 1), np.uint8), rgb.reshape(h, w * 3)], axis=1)[::-1].tobytes()   # flip: row 0 is the bottom in Blender
    def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))

def make_atlas(path):
    """Paint the atlas: gradient + edge wear + dirt + speckle per swatch (deterministic)."""
    rng = np.random.default_rng(11)
    N = CELL * GRID
    img = np.zeros((N, N, 4), np.float32); img[..., 3] = 1
    yy, xx = np.mgrid[0:CELL, 0:CELL].astype(np.float32)
    u = np.clip((xx - INSET) / (CELL - 2 * INSET - 1), 0, 1)
    v = np.clip((yy - INSET) / (CELL - 2 * INSET - 1), 0, 1)
    def vnoise(scale):
        g = rng.random((scale + 2, scale + 2)).astype(np.float32)
        gx, gy = u * scale, v * scale
        x0, y0 = gx.astype(int), gy.astype(int); fx, fy = gx - x0, gy - y0
        fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        return (g[y0, x0] * (1 - fx) * (1 - fy) + g[y0, x0 + 1] * fx * (1 - fy) + g[y0 + 1, x0] * (1 - fx) * fy + g[y0 + 1, x0 + 1] * fx * fy)
    for i, name in enumerate(ORDER):
        hx, edge, dirt, nz, emi = PALETTE[name]
        base = np.array([int(hx[k:k + 2], 16) / 255 for k in (0, 2, 4)], np.float32)
        base = np.power(base, 2.2)                      # sRGB -> linear authoring
        if emi:
            col = np.broadcast_to(base, (CELL, CELL, 3)).copy(); col *= (1 + .08 * (v[..., None] - .5))
        else:
            e = np.minimum(np.minimum(u, 1 - u), np.minimum(v, 1 - v))
            ef = np.clip(e / 0.10, 0, 1)[..., None]
            mul = (1 - ef) * edge + ef * 1.0                          # edge band (chipped paint / worn corners)
            shade = 1 - dirt * (1 - v[..., None]) ** 2                # dirt gathers low
            shade *= 1 + .05 * (v[..., None] - .5)                   # soft top-light gradient
            grime = 1 + (vnoise(3) - .5) * nz * 6 + (vnoise(9) - .5) * nz * 3
            speck = 1 + (rng.random((CELL, CELL, 1)).astype(np.float32) - .5) * nz
            col = base * mul * shade * grime[..., None] * speck
        cx, cy = i % GRID, i // GRID
        img[cy * CELL:(cy + 1) * CELL, cx * CELL:(cx + 1) * CELL, :3] = np.clip(col, 0, 1.5)
    srgb = np.power(np.clip(img[..., :3], 0, 1), 1 / 2.2)
    write_png(path, (srgb * 255 + .5).astype(np.uint8))
    out = bpy.data.images.load(path); out.name = 'turbine_atlas'; out.colorspace_settings.name = 'sRGB'
    return out

def uv_origin(idx):
    return (idx % GRID) / GRID, (idx // GRID) / GRID

class Builder:
    """Accumulates flat-shaded geometry into named groups (one joined mesh each)."""
    def __init__(self):
        self.g = {}                  # group -> dict(v, f, uv, sw)
        self.group = 'ARCH'
        self.m = Matrix.Identity(4)
        self.stack = []
        self.reg = []                # AABBs (lo, hi) reserved by solids, for scatter placement
        self.rng = random.Random(5)
    # -- transform stack --
    def push(self, loc=(0, 0, 0), rz=0.0):
        self.stack.append(self.m)
        loc = tuple(loc) + (0.0,) * (3 - len(loc))
        self.m = self.m @ Matrix.Translation(loc) @ Matrix.Rotation(rz, 4, 'Z')
        return self
    def pop(self): self.m = self.stack.pop()
    def __enter__(self): return self
    def __exit__(self, *a): self.pop()
    def use(self, group): self.group = group
    # -- low level --
    def _g(self):
        return self.g.setdefault(self.group, dict(v=[], f=[], uv=[], sw=[], swi=[]))
    def poly(self, pts, sw, flip=False):
        g = self._g(); idx = SWATCH[sw] if isinstance(sw, str) else sw
        P = [self.m @ Vector(p) for p in pts]
        if flip: P.reverse()
        n = Vector((0, 0, 0))
        for i in range(len(P)):
            a, b = P[i], P[(i + 1) % len(P)]
            n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
        if n.length < 1e-12: return
        n.normalize()
        if abs(n.z) < 0.75: va = Vector((0, 0, 1)); ua = va.cross(n)
        else: ua = Vector((1, 0, 0)); va = n.cross(ua)
        ua = (ua - n * ua.dot(n)).normalized(); va = (va - n * va.dot(n)).normalized()
        us = [p.dot(ua) for p in P]; vs = [p.dot(va) for p in P]
        u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
        ox, oy = uv_origin(idx); s = 1.0 / GRID; ins = INSET / (CELL * GRID); span = s - 2 * ins
        base = len(g['v']); g['v'].extend(tuple(p) for p in P)
        g['f'].append(tuple(range(base, base + len(P))))
        g['uv'].append([(ox + ins + span * ((u - u0) / (u1 - u0) if u1 - u0 > 1e-9 else .5),
                         oy + ins + span * ((v - v0) / (v1 - v0) if v1 - v0 > 1e-9 else .5)) for u, v in zip(us, vs)])
        g['sw'].append(1 if idx in EMISSIVE else 0); g['swi'].append(idx)
    # -- primitives --
    def box(self, c, s, sw, rot=(0, 0, 0), nb=False, nt=False, reg=False):
        hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
        E = Euler(rot, 'XYZ').to_matrix()
        v = [Vector(c) + E @ Vector((sx * hx, sy * hy, sz * hz)) for sz in (-1, 1) for sy in (-1, 1) for sx in (-1, 1)]
        # v idx: z0:(0..3) z1:(4..7); within: (-,-)(+,-)(-,+)(+,+)
        faces = [(0, 2, 3, 1), (0, 1, 5, 4), (1, 3, 7, 5), (3, 2, 6, 7), (2, 0, 4, 6), (4, 5, 7, 6)]
        if nb: faces = faces[1:]
        if nt: faces = faces[:-1]
        sws = sw if isinstance(sw, (list, tuple)) else [sw] * 6
        names = (['b'] if not nb else []) + ['s', 'e', 'n', 'w'] + (['t'] if not nt else [])
        for f, nm in zip(faces, names):
            col = sws[{'b': 0, 's': 1, 'e': 2, 'n': 3, 'w': 4, 't': 5}[nm]] if len(sws) == 6 else sws[0]
            self.poly([v[i] for i in f], col)
        if reg: self.reserve_box(c, s, rot)
    def reserve_box(self, c, s, rot=(0, 0, 0), pad=0.0):
        E = Euler(rot, 'XYZ').to_matrix()
        pts = [self.m @ (Vector(c) + E @ Vector((sx * s[0] / 2, sy * s[1] / 2, sz * s[2] / 2))) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
        self.reg.append((Vector(min(p[i] for p in pts) - pad for i in range(3)), Vector(max(p[i] for p in pts) + pad for i in range(3))))
    def prism(self, ring, h, sw, c=(0, 0, 0), caps=True, axis='Z'):
        """Extrude a closed 2D ring (list of (x,y)) by h along `axis`, centred at c."""
        n = len(ring)
        def P(x, y, z):
            if axis == 'Z': return (c[0] + x, c[1] + y, c[2] + z)
            if axis == 'Y': return (c[0] + x, c[1] + z, c[2] + y)
            return (c[0] + z, c[1] + x, c[2] + y)                      # 'X'
        lo = [P(x, y, -h / 2) for x, y in ring]; hi = [P(x, y, h / 2) for x, y in ring]
        sws = sw if isinstance(sw, (list, tuple)) else None
        for i in range(n):
            j = (i + 1) % n
            self.poly([lo[i], lo[j], hi[j], hi[i]], sws[i % len(sws)] if sws else sw, flip=(axis == 'Y'))
        if caps:
            cs = sws[0] if sws else sw
            self.poly(lo[::-1], cs, flip=(axis == 'Y')); self.poly(hi, cs, flip=(axis == 'Y'))
    def cyl(self, c, r, h, sw, axis='Z', seg=12, r2=None, caps=True):
        ring = [(r * math.cos(2 * math.pi * i / seg + math.pi / seg), r * math.sin(2 * math.pi * i / seg + math.pi / seg)) for i in range(seg)]
        if r2 is None or abs(r2 - r) < 1e-9: return self.prism(ring, h, sw, c, caps, axis)
        # frustum
        k = r2 / r; hi = [(x * k, y * k) for x, y in ring]
        def P(x, y, z):
            if axis == 'Z': return (c[0] + x, c[1] + y, c[2] + z)
            if axis == 'Y': return (c[0] + x, c[1] + z, c[2] + y)
            return (c[0] + z, c[1] + x, c[2] + y)
        fl = (axis == 'Y')
        for i in range(seg):
            j = (i + 1) % seg
            self.poly([P(*ring[i], -h / 2), P(*ring[j], -h / 2), P(*hi[j], h / 2), P(*hi[i], h / 2)], sw, flip=fl)
        if caps:
            self.poly([P(*p, -h / 2) for p in ring[::-1]], sw, flip=fl); self.poly([P(*p, h / 2) for p in hi], sw, flip=fl)
    def rod(self, a, b, r, sw, seg=4, caps=False):
        a, b = Vector(a), Vector(b); d = b - a
        if d.length < 1e-6: return
        q = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
        self.push((a + b) / 2); self.m = self.m @ q
        self.cyl((0, 0, 0), r, d.length, sw, 'Z', seg, caps=caps)
        self.pop()
    def pipe(self, pts, r, sw, seg=8, flange=None, elbow_sw=None):
        """Polyline pipe with mitred corners (angular elbow caps) and optional flange rings at joints."""
        for a, b in zip(pts, pts[1:]): self.rod(a, b, r, sw, seg, caps=False)
        for p in pts[1:-1]:
            self.cyl(p, r * 1.0, r * 2.0, elbow_sw or sw, 'Z', seg) if False else self.sphere(p, r * 1.02, elbow_sw or sw, 6)
        for p in (pts[0], pts[-1]) if flange else ():
            pass
    def sphere(self, c, r, sw, seg=6):
        c = Vector(c); rings = [(-.9, .45), (-.35, .9), (.35, .9), (.9, .45)]
        pr = []
        for z, k in rings:
            pr.append([c + Vector((r * k * math.cos(2 * math.pi * i / seg), r * k * math.sin(2 * math.pi * i / seg), r * z * .95)) for i in range(seg)])
        for a, b in zip(pr, pr[1:]):
            for i in range(seg): j = (i + 1) % seg; self.poly([a[i], a[j], b[j], b[i]], sw)
        self.poly(pr[-1], sw); self.poly(pr[0][::-1], sw)
    def flat(self, c, sx, sy, sw, rz=0.0, z=0.006):
        self.box((c[0], c[1], z), (sx, sy, 0.004), sw, (0, 0, rz), nb=True)
    def text(self, s, loc, size, sw='chalk', rz=0.0, rx=math.pi / 2, align='CENTER'):
        cu = bpy.data.curves.new('t', 'FONT'); cu.body = s; cu.size = size; cu.align_x = align; cu.align_y = 'CENTER'
        cu.extrude = 0.004; ob = bpy.data.objects.new('t', cu); bpy.context.scene.collection.objects.link(ob)
        dg = bpy.context.evaluated_depsgraph_get(); me = ob.evaluated_get(dg).to_mesh()
        R = Matrix.Translation(loc) @ Matrix.Rotation(rz, 4, 'Z') @ Matrix.Rotation(rx, 4, 'X')
        for p in me.polygons:
            self.poly([R @ me.vertices[i].co for i in p.vertices], sw)
        ob.evaluated_get(dg).to_mesh_clear(); bpy.data.objects.remove(ob); bpy.data.curves.remove(cu)
    # -- placement registry --
    def free(self, lo, hi, pad=0.1):
        for a, b in self.reg:
            if all(lo[i] - pad < b[i] and hi[i] + pad > a[i] for i in range(3)): return False
        return True
    def claim(self, lo, hi): self.reg.append((Vector(lo), Vector(hi)))
    # -- finalise --
    def build(self, coll, materials):
        """materials: dict group -> (atlas_material, emissive_material)."""
        out = {}
        for gname, g in self.g.items():
            if gname == 'OCC':
                me = bpy.data.meshes.new('OCCLUDER_MESH'); me.from_pydata(g['v'], [], g['f']); me.update()
                ob = bpy.data.objects.new('OCCLUDER_ONLY', me); coll.objects.link(ob); ob['shipping'] = False; out['OCC'] = ob; continue
            me = bpy.data.meshes.new('MESH_' + gname)
            me.from_pydata(g['v'], [], g['f']); me.update()
            uv = me.uv_layers.new(name='UVMap')
            k = 0
            for fi, f in enumerate(g['f']):
                for j in range(len(f)): uv.data[k].uv = g['uv'][fi][j]; k += 1
            for fi, p in enumerate(me.polygons): p.material_index = g['sw'][fi]; p.use_smooth = False
            at = me.attributes.new('swatch', 'INT', 'FACE'); at.data.foreach_set('value', g['swi'])
            for m in materials[gname]: me.materials.append(m)
            ob = bpy.data.objects.new('TURBINE_' + gname, me); coll.objects.link(ob); out[gname] = ob
        return out
    def stats(self):
        return {k: dict(faces=len(g['f']), tris=sum(len(f) - 2 for f in g['f'])) for k, g in self.g.items()}
