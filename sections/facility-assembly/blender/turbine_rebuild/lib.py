"""Shared helpers for the turbine room rebuild (v3: bevelled hero assets, smooth curved forms, restrained detail).

Everything is built from primitives whose faces are UV-fitted into one swatch of a single painted atlas (UV0).
Boxes may carry a bevel width; `finalize` welds vertices, applies a weighted Bevel modifier (so only the marked
hard edges get a crisp highlight) and shades by angle so cylinders and pipes are smooth while panels stay flat.
A second atlas (ORM: G=roughness, B=metal) drives material response. No lighting is baked here.
"""
import math, random
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

CELL, GRID, INSET = 128, 16, 9          # atlas 2048^2, 16x16 swatches, 9px safe border
BEV_MAX = 0.05                          # bevel modifier width; per-edge weight = face bev / BEV_MAX

# name: (hex, edge, dirt, noise, emissive)   edge>1 lightens edges (paint chipping), <1 darkens
PALETTE = {
    'wall_slate': ('2E2F33', 1.06, .08, .030, 0),
    'wall_slate_lt': ('393A3E', 1.06, .06, .028, 0),
    'terra_a': ('20252B', .88, .05, .026, 0),
    'terra_b': ('1D2228', .88, .05, .028, 0),
    'terra_c': ('252A31', .88, .04, .024, 0),
    'terra_worn': ('2D3239', .90, .14, .045, 0),
    'casing': ('3D4245', 1.10, .10, .040, 0),
    'casing_dark': ('2C3436', 1.10, .14, .040, 0),
    'hood_orange': ('2F5750', 1.12, .08, .030, 0),
    'sand': ('46423D', 1.06, .08, .030, 0),
    'sand_dark': ('34312E', 1.08, .12, .035, 0),
    'ivory': ('55524D', 1.08, .08, .028, 0),
    'ivory_warm': ('3F3C38', 1.06, .06, .025, 0),
    'slate_blue': ('26282B', 1.14, .10, .030, 0),
    'slate_dark': ('1D1E21', 1.18, .10, .030, 0),
    'trim_black': ('101215', 1.30, .03, .020, 0),
    'charcoal': ('22262B', 1.25, .06, .030, 0),
    'steel_dark': ('34363A', 1.30, .08, .040, 0),
    'steel_mid': ('4D5054', 1.25, .08, .040, 0),
    'steel_light': ('4F5155', 1.15, .06, .035, 0),
    'steel_worn': ('55575B', 1.40, .18, .060, 0),
    'orange': ('B58A32', 1.18, .07, .028, 0),
    'orange_dark': ('8E692A', 1.18, .12, .035, 0),
    'orange_worn': ('A57F36', 1.40, .22, .060, 0),
    'yellow': ('B68A2E', 1.12, .07, .028, 0),
    'yellow_worn': ('8F7030', 1.35, .20, .055, 0),
    'red':          ('C2392B', 1.12, .07, .028, 0),
    'red_dark':     ('8E2A20', 1.12, .10, .032, 0),
    'concrete': ('3A3A3C', 1.04, .10, .045, 0),
    'concrete_dark': ('27272A', 1.04, .12, .050, 0),
    'tile_a':       ('B5AEA1', .88, .04, .022, 0),
    'tile_b':       ('ABA497', .88, .05, .024, 0),
    'tile_c':       ('BDB6A9', .88, .04, .020, 0),
    'tile_worn':    ('9A9488', .90, .14, .045, 0),
    'tile_border': ('202429', .86, .05, .022, 0),
    'tile_border_b': ('1B1F23', .86, .05, .022, 0),
    'tile_oil': ('1A1C1F', .92, .08, .045, 0),
    'tile_crack':   ('7C776E', .92, .12, .045, 0),
    'grout':        ('2A2724', 1., .0, .02, 0),
    'backing':      ('0E1013', 1., .0, .02, 0),
    'primer':       ('6A4B3E', 1.2, .12, .05, 0),
    'rust':         ('8A4D2B', 1.1, .20, .08, 0),
    'rubber':       ('24262A', 1.15, .04, .025, 0),
    'wood':         ('4F4234', 1.12, .10, .040, 0),
    'wood_dark':    ('352C23', 1.12, .12, .040, 0),
    'paper':        ('E7E2D4', 1.0, .04, .025, 0),
    'lagging': ('4D4B47', 1.10, .10, .040, 0),
    'lagging_dark': ('3F3D3A', 1.10, .14, .040, 0),
    'crack':        ('050607', 1.0, .0, .01, 0),
    'damp':         ('191D22', 1.0, .0, .02, 0),
    'floor_grime':  ('0F1114', 1.0, .0, .03, 0),
    'patch':        ('272D34', 1.05, .06, .04, 0),
    'sealant':      ('0B0C0E', 1.0, .0, .02, 0),
    'gold_paint':   ('A98439', 1.12, .10, .035, 0),
    'wet':          ('23272D', 1.0, .0, .02, 0),
    'brass_blade':  ('94722F', 1.15, .10, .03, 0),
    'brass':        ('C79A3C', 1.15, .08, .035, 0),
    'oil': ('0F1113', 1.0, .0, .04, 0),
    'oxide': ('6A3A2F', 1.12, .14, .06, 0),
    'oxide_dark': ('4A2A24', 1.12, .16, .06, 0),
    'teal': ('2F5750', 1.12, .10, .05, 0),
    'teal_dark': ('1F3A36', 1.12, .12, .05, 0),
    'grime_dark': ('151515', 1.0, .0, .04, 0),
    'chalk':        ('F2EFE6', 1.0, .02, .015, 0),
    'green':        ('3E6A5F', 1.12, .06, .028, 0),
    'blue_panel': ('3A3A3D', 1.12, .06, .028, 0),
    'poster_a':     ('2B3C5A', 1.0, .0, .02, 0),
    'poster_b':     ('E8913A', 1.0, .0, .02, 0),
    'poster_c':     ('F0C95A', 1.0, .0, .02, 0),
    'glass':        ('1D2B36', 1.0, .0, .01, 0),
    # emissive swatches
    'lamp': ('FFA84A', 1.0, 0., .01, 1),
    'screen': ('B8641C', 1.0, 0., .02, 1),
    'screen_cool':  ('3F7F78', 1.0, 0., .02, 1),
    'screen_dim':   ('143742', 1.0, 0., .02, 1),
    'led_red':      ('D83A24', 1.0, 0., .01, 1),
    'led_green':    ('2FA553', 1.0, 0., .01, 1),
}
# (roughness, metallic) overrides, default (.62, 0)
PBR = {'crack': (.95, 0),
       'damp': (.11, 0), 'floor_grime': (.78, 0), 'patch': (.55, 0), 'sealant': (.45, 0),
       'gold_paint': (.7, 0), 'wet': (.035, 0), 'brass_blade': (.38, .92),
       'terra_a': (.2, 0), 'terra_b': (.2, 0), 'terra_c': (.2, 0), 'terra_worn': (.32, 0), 'tile_border': (.2, 0), 'tile_border_b': (.2, 0), 'oil': (.04, 0), 'tile_oil': (.06, 0),
       'casing': (.45, .4), 'casing_dark': (.45, .4), 'hood_orange': (.5, .05), 'wall_slate': (.9, 0), 'wall_slate_lt': (.9, 0),
       'steel_dark': (.46, .32), 'steel_mid': (.42, .34), 'steel_light': (.4, .4), 'brass': (.28, .95), 'orange': (.3, .85), 'orange_dark': (.35, .8), 'orange_worn': (.4, .75), 'yellow': (.3, .85), 'yellow_worn': (.4, .75), 'steel_worn': (.55, .55), 'brass': (.32, .9),
       'tile_a': (.34, 0), 'tile_b': (.34, 0), 'tile_c': (.34, 0), 'tile_worn': (.5, 0), 'tile_border': (.34, 0), 'tile_border_b': (.34, 0),
       'tile_oil': (.2, 0), 'oil': (.1, 0), 'tile_crack': (.5, 0), 'concrete': (.85, 0), 'concrete_dark': (.85, 0), 'trim_black': (.4, 0), 'glass': (.08, 0),
       'orange': (.48, .05), 'yellow': (.48, .05), 'red': (.45, .05), 'rubber': (.8, 0), 'lagging': (.85, 0), 'lagging_dark': (.85, 0),
       'sand': (.9, 0), 'sand_dark': (.9, 0), 'ivory': (.7, 0), 'ivory_warm': (.9, 0), 'paper': (.9, 0), 'wood': (.6, 0), 'wood_dark': (.6, 0)}
ORDER = list(PALETTE)
SWATCH = {n: i for i, n in enumerate(ORDER)}
EMISSIVE = {i for i, n in enumerate(ORDER) if PALETTE[n][4]}

def write_png(path, rgb):
    """Minimal 8-bit RGB PNG writer (bpy's Image.pixels.foreach_set is unreliable for 16M-element writes)."""
    import zlib, struct
    h, w, _ = rgb.shape
    raw = np.concatenate([np.zeros((h, 1), np.uint8), rgb.reshape(h, w * 3)], axis=1)[::-1].tobytes()   # row 0 is the bottom in Blender
    def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))

def make_atlas(path):
    """Paint the albedo atlas (gradient + edge wear + dirt + speckle) and the ORM atlas (G rough, B metal). Deterministic."""
    rng = np.random.default_rng(11)
    N = CELL * GRID
    img = np.zeros((N, N, 3), np.float32); orm = np.zeros((N, N, 3), np.float32); orm[..., 0] = 1
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
        base = np.power(np.array([int(hx[k:k + 2], 16) / 255 for k in (0, 2, 4)], np.float32), 2.2)
        if emi:
            col = np.broadcast_to(base, (CELL, CELL, 3)).copy() * (1 + .06 * (v[..., None] - .5))
        else:
            e = np.minimum(np.minimum(u, 1 - u), np.minimum(v, 1 - v)); ef = np.clip(e / 0.10, 0, 1)[..., None]
            mul = (1 - ef) * edge + ef * 1.0
            shade = (1 - dirt * (1 - v[..., None]) ** 2) * (1 + .05 * (v[..., None] - .5))
            grime = 1 + (vnoise(3) - .5) * nz * 9 + (vnoise(9) - .5) * nz * 4
            speck = 1 + (rng.random((CELL, CELL, 1)).astype(np.float32) - .5) * nz
            col = base * mul * shade * grime[..., None] * speck
            sg = rng.random((1, 14)).astype(np.float32); sg = np.repeat(sg, CELL // 14 + 1, axis=1)[:, :CELL]; sg = np.repeat(sg, CELL, axis=0)    # vertical weathering streaks
            streak = np.clip((sg - .45) * 2.2, 0, 1) * np.clip(1 - v, 0, 1) ** .7
            col = col * (1 - .3 * streak[..., None])
        r, m = PBR.get(name, (.62, 0.0))
        rough = np.clip(r + (vnoise(5) - .5) * .18, .05, 1)
        cx, cy = i % GRID, i // GRID
        sl = (slice(cy * CELL, (cy + 1) * CELL), slice(cx * CELL, (cx + 1) * CELL))
        img[sl] = np.clip(col, 0, 1.5)
        orm[sl[0], sl[1], 1] = rough; orm[sl[0], sl[1], 2] = m
    write_png(path, (np.power(np.clip(img, 0, 1), 1 / 2.2) * 255 + .5).astype(np.uint8))
    opath = path.replace('.png', '_orm.png'); write_png(opath, (orm * 255 + .5).astype(np.uint8))
    a = bpy.data.images.load(path); a.name = 'turbine_atlas'; a.colorspace_settings.name = 'sRGB'
    o = bpy.data.images.load(opath); o.name = 'turbine_atlas_orm'; o.colorspace_settings.name = 'Non-Color'
    return a, o

def uv_origin(idx):
    return (idx % GRID) / GRID, (idx // GRID) / GRID

class Builder:
    """Accumulates geometry into named groups (one joined mesh each)."""
    def __init__(self):
        self.g = {}; self.group = 'ARCH'; self.m = Matrix.Identity(4); self.stack = []
        self.reg = []; self.rng = random.Random(5)
    def push(self, loc=(0, 0, 0), rz=0.0):
        self.stack.append(self.m); loc = tuple(loc) + (0.0,) * (3 - len(loc))
        self.m = self.m @ Matrix.Translation(loc) @ Matrix.Rotation(rz, 4, 'Z'); return self
    def push_m(self, M):
        self.stack.append(self.m); self.m = self.m @ M; return self
    def pop(self): self.m = self.stack.pop()
    def __enter__(self): return self
    def __exit__(self, *a): self.pop()
    def use(self, group): self.group = group
    def _g(self): return self.g.setdefault(self.group, dict(v=[], f=[], uv=[], sw=[], swi=[], bev=[]))
    # -- low level --
    def poly(self, pts, sw, flip=False, bev=0.0, fit=True, hint=None):
        g = self._g(); idx = SWATCH[sw] if isinstance(sw, str) else sw
        P = [self.m @ Vector(p) for p in pts]
        if flip: P.reverse()
        if hint is not None:                                              # make the face normal agree with a local-space direction
            nn = Vector((0, 0, 0))
            for i in range(len(P)):
                a_, b_ = P[i], P[(i + 1) % len(P)]
                nn += Vector(((a_.y - b_.y) * (a_.z + b_.z), (a_.z - b_.z) * (a_.x + b_.x), (a_.x - b_.x) * (a_.y + b_.y)))
            if nn.dot(self.m.to_3x3() @ Vector(hint)) < 0: P.reverse()
        n = Vector((0, 0, 0))
        for i in range(len(P)):
            a, b = P[i], P[(i + 1) % len(P)]
            n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
        if n.length < 1e-12: return
        n.normalize()
        ox, oy = uv_origin(idx); s = 1.0 / GRID; ins = INSET / (CELL * GRID); span = s - 2 * ins
        base = len(g['v']); g['v'].extend(tuple(p) for p in P); g['f'].append(tuple(range(base, base + len(P))))
        if not fit:                                                             # curved/smooth surfaces: one flat colour, no stripe artefacts
            g['uv'].append([(ox + s / 2, oy + s / 2)] * len(P))
        else:
            if abs(n.z) < 0.75: va = Vector((0, 0, 1)); ua = va.cross(n)
            else: ua = Vector((1, 0, 0)); va = n.cross(ua)
            ua = (ua - n * ua.dot(n)).normalized(); va = (va - n * va.dot(n)).normalized()
            us = [p.dot(ua) for p in P]; vs = [p.dot(va) for p in P]
            u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
            g['uv'].append([(ox + ins + span * ((u - u0) / (u1 - u0) if u1 - u0 > 1e-9 else .5),
                             oy + ins + span * ((v - v0) / (v1 - v0) if v1 - v0 > 1e-9 else .5)) for u, v in zip(us, vs)])
        g['sw'].append(1 if idx in EMISSIVE else 0); g['swi'].append(idx); g['bev'].append(bev)
    # -- primitives --
    def box(self, c, s, sw, rot=(0, 0, 0), nb=False, nt=False, reg=False, bev=0.0):
        hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
        E = Euler(rot, 'XYZ').to_matrix()
        v = [Vector(c) + E @ Vector((sx * hx, sy * hy, sz * hz)) for sz in (-1, 1) for sy in (-1, 1) for sx in (-1, 1)]
        faces = [(0, 2, 3, 1), (0, 1, 5, 4), (1, 3, 7, 5), (3, 2, 6, 7), (2, 0, 4, 6), (4, 5, 7, 6)]
        names = ['b', 's', 'e', 'n', 'w', 't']
        sws = sw if isinstance(sw, (list, tuple)) and len(sw) == 6 else [sw] * 6
        for f, nm in zip(faces, names):
            if (nb and nm == 'b') or (nt and nm == 't'): continue
            self.poly([v[i] for i in f], sws[names.index(nm)], bev=bev)
        if reg: self.reserve_box(c, s, rot)
    def reserve_box(self, c, s, rot=(0, 0, 0), pad=0.0):
        E = Euler(rot, 'XYZ').to_matrix()
        pts = [self.m @ (Vector(c) + E @ Vector((sx * s[0] / 2, sy * s[1] / 2, sz * s[2] / 2))) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
        self.reg.append((Vector(min(p[i] for p in pts) - pad for i in range(3)), Vector(max(p[i] for p in pts) + pad for i in range(3))))
    def prism(self, ring, h, sw, c=(0, 0, 0), caps=True, axis='Z', bev=0.0, flat=False):
        n = len(ring)
        def P(x, y, z):
            if axis == 'Z': return (c[0] + x, c[1] + y, c[2] + z)
            if axis == 'Y': return (c[0] + x, c[1] + z, c[2] + y)
            return (c[0] + z, c[1] + x, c[2] + y)
        lo = [P(x, y, -h / 2) for x, y in ring]; hi = [P(x, y, h / 2) for x, y in ring]
        sws = sw if isinstance(sw, (list, tuple)) else None
        for i in range(n):
            j = (i + 1) % n
            self.poly([lo[i], lo[j], hi[j], hi[i]], sws[i % len(sws)] if sws else sw, flip=(axis == 'Y'), bev=bev, fit=not flat)
        if caps:
            cs = sws[0] if sws else sw
            self.poly(lo[::-1], cs, flip=(axis == 'Y'), bev=bev); self.poly(hi, cs, flip=(axis == 'Y'), bev=bev)
    def cyl(self, c, r, h, sw, axis='Z', seg=32, r2=None, caps=True, bev=0.0):
        seg = max(8, min(seg, int(10 + r * 56)))                                                   # triangle budget: small radii need fewer segments
        ring = [(r * math.cos(2 * math.pi * i / seg + math.pi / seg), r * math.sin(2 * math.pi * i / seg + math.pi / seg)) for i in range(seg)]
        if r2 is None or abs(r2 - r) < 1e-9: return self.prism(ring, h, sw, c, caps, axis, bev, flat=True)
        k = r2 / r; hi = [(x * k, y * k) for x, y in ring]
        def P(x, y, z):
            if axis == 'Z': return (c[0] + x, c[1] + y, c[2] + z)
            if axis == 'Y': return (c[0] + x, c[1] + z, c[2] + y)
            return (c[0] + z, c[1] + x, c[2] + y)
        fl = (axis == 'Y')
        for i in range(seg):
            j = (i + 1) % seg
            self.poly([P(*ring[i], -h / 2), P(*ring[j], -h / 2), P(*hi[j], h / 2), P(*hi[i], h / 2)], sw, flip=fl, bev=bev, fit=False)
        if caps:
            self.poly([P(*p, -h / 2) for p in ring[::-1]], sw, flip=fl, bev=bev); self.poly([P(*p, h / 2) for p in hi], sw, flip=fl, bev=bev)
    def rod(self, a, b, r, sw, seg=10, caps=True, bev=0.0):
        a, b = Vector(a), Vector(b); d = b - a
        if d.length < 1e-6: return
        q = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
        self.push((a + b) / 2); self.m = self.m @ q
        self.cyl((0, 0, 0), r, d.length, sw, 'Z', seg, caps=caps, bev=bev)
        self.pop()
    def sweep(self, path, r, sw, seg=24, bend=0.3, caps=True, bev=0.0):
        """Smooth tube along a polyline with rounded corners (quadratic arcs of radius ~bend)."""
        pts = [Vector(p) for p in path]; out = [pts[0]]
        for i in range(1, len(pts) - 1):
            A, P, B = pts[i - 1], pts[i], pts[i + 1]
            t = min(bend, (A - P).length * .45, (B - P).length * .45)
            p1 = P + (A - P).normalized() * t; p2 = P + (B - P).normalized() * t
            for k in range(0, 7):
                s = k / 6; out.append((1 - s) ** 2 * p1 + 2 * s * (1 - s) * P + s * s * p2)
        out.append(pts[-1])
        cl = [out[0]]
        for p in out[1:]:
            if (p - cl[-1]).length > 1e-5: cl.append(p)
        out = cl
        T = []
        for i in range(len(out)):
            a = out[max(i - 1, 0)]; b = out[min(i + 1, len(out) - 1)]; T.append((b - a).normalized())
        N = T[0].cross(Vector((0, 0, 1)) if abs(T[0].z) < .9 else Vector((1, 0, 0))).normalized()
        rings = []
        for i, c in enumerate(out):
            if i: N = (N - T[i] * N.dot(T[i])).normalized()
            B = T[i].cross(N)
            rings.append([c + (N * math.cos(2 * math.pi * k / seg) + B * math.sin(2 * math.pi * k / seg)) * r for k in range(seg)])
        for a, b in zip(rings, rings[1:]):
            for k in range(seg):
                j = (k + 1) % seg; self.poly([a[k], a[j], b[j], b[k]], sw, bev=bev, fit=False)
        if caps: self.poly(rings[0][::-1], sw, bev=bev); self.poly(rings[-1], sw, bev=bev)
    def sphere(self, c, r, sw, seg=16):
        c = Vector(c); lat = [(-1.0, 0.0), (-.8, .6), (-.4, .92), (0, 1), (.4, .92), (.8, .6), (1.0, 0.0)]; rings = []
        for z, k in lat:
            if k == 0: rings.append([c + Vector((0, 0, r * z))])
            else: rings.append([c + Vector((r * k * math.cos(2 * math.pi * i / seg), r * k * math.sin(2 * math.pi * i / seg), r * z * .98)) for i in range(seg)])
        for a, b in zip(rings, rings[1:]):
            for i in range(seg):
                j = (i + 1) % seg
                if len(a) == 1: self.poly([a[0], b[j], b[i]], sw, fit=False)
                elif len(b) == 1: self.poly([a[i], a[j], b[0]], sw, fit=False)
                else: self.poly([a[i], a[j], b[j], b[i]], sw, fit=False)
    def arc_shell(self, c, r_out, r_in, length, a0, a1, sw, n=28, bev=0.0):
        """Partial tube along Y (arc a0..a1 in the XZ plane, radians): outer, inner, two rims and two end faces."""
        h = length / 2
        def P(r, t, y): return (c[0] + r * math.cos(t), c[1] + y, c[2] + r * math.sin(t))
        th = [a0 + (a1 - a0) * i / n for i in range(n + 1)]
        for i in range(n):
            t0, t1 = th[i], th[i + 1]; tm = (t0 + t1) / 2; ox, oz = math.cos(tm), math.sin(tm)
            self.poly([P(r_out, t0, -h), P(r_out, t1, -h), P(r_out, t1, h), P(r_out, t0, h)], sw, fit=False, hint=(ox, 0, oz))
            self.poly([P(r_in, t0, -h), P(r_in, t1, -h), P(r_in, t1, h), P(r_in, t0, h)], sw, fit=False, hint=(-ox, 0, -oz))
            for yy, s in ((-h, -1), (h, 1)): self.poly([P(r_in, t0, yy), P(r_in, t1, yy), P(r_out, t1, yy), P(r_out, t0, yy)], sw, fit=False, hint=(0, s, 0), bev=bev)
        for t, s in ((a0, -1), (a1, 1)):
            tx, tz = -math.sin(t) * s, math.cos(t) * s
            self.poly([P(r_in, t, -h), P(r_out, t, -h), P(r_out, t, h), P(r_in, t, h)], sw, hint=(tx, 0, tz), bev=bev)
    def flat(self, c, sx, sy, sw, rz=0.0, z=0.006):
        self.box((c[0], c[1], z), (sx, sy, 0.004), sw, (0, 0, rz), nb=True)
    def text(self, s, loc, size, sw='chalk', rz=0.0, rx=math.pi / 2, align='CENTER', extrude=.004):
        cu = bpy.data.curves.new('t', 'FONT'); cu.body = s; cu.size = size; cu.align_x = align; cu.align_y = 'CENTER'
        cu.extrude = extrude; cu.resolution_u = 3; ob = bpy.data.objects.new('t', cu); bpy.context.scene.collection.objects.link(ob)
        dg = bpy.context.evaluated_depsgraph_get(); me = ob.evaluated_get(dg).to_mesh()
        R = self.m @ Matrix.Translation(loc) @ Matrix.Rotation(rz, 4, 'Z') @ Matrix.Rotation(rx, 4, 'X')
        g = self._g(); idx = SWATCH[sw]; ox, oy = uv_origin(idx); s_ = 1.0 / GRID
        for p in me.polygons:
            P = [R @ me.vertices[i].co for i in p.vertices]; base = len(g['v']); g['v'].extend(tuple(q) for q in P)
            g['f'].append(tuple(range(base, base + len(P)))); g['uv'].append([(ox + s_ / 2, oy + s_ / 2)] * len(P))
            g['sw'].append(0); g['swi'].append(idx); g['bev'].append(0.0)
        ob.evaluated_get(dg).to_mesh_clear(); bpy.data.objects.remove(ob); bpy.data.curves.remove(cu)
    # -- placement registry --
    def free(self, lo, hi, pad=0.1):
        for a, b in self.reg:
            if all(lo[i] - pad < b[i] and hi[i] + pad > a[i] for i in range(3)): return False
        return True
    def claim(self, lo, hi): self.reg.append((Vector(lo), Vector(hi)))
    # -- finalise --
    def build(self, coll, materials):
        out = {}
        for gname, g in self.g.items():
            if gname == 'OCC':
                me = bpy.data.meshes.new('OCCLUDER_MESH'); me.from_pydata(g['v'], [], g['f']); me.update()
                ob = bpy.data.objects.new('OCCLUDER_ONLY', me); coll.objects.link(ob); ob['shipping'] = False; out['OCC'] = ob; continue
            me = bpy.data.meshes.new('MESH_' + gname); me.from_pydata(g['v'], [], g['f']); me.update()
            uv = me.uv_layers.new(name='UVMap'); k = 0
            for fi, f in enumerate(g['f']):
                for j in range(len(f)): uv.data[k].uv = g['uv'][fi][j]; k += 1
            for fi, p in enumerate(me.polygons): p.material_index = g['sw'][fi]; p.use_smooth = False
            at = me.attributes.new('swatch', 'INT', 'FACE'); at.data.foreach_set('value', g['swi'])
            bt = me.attributes.new('bev', 'FLOAT', 'FACE'); bt.data.foreach_set('value', g['bev'])
            for m in materials[gname]: me.materials.append(m)
            ob = bpy.data.objects.new('TURBINE_' + gname, me); coll.objects.link(ob); out[gname] = ob
        return out
    def stats(self):
        return {k: dict(faces=len(g['f']), tris=sum(len(f) - 2 for f in g['f'])) for k, g in self.g.items()}

SHARP = math.radians(48)

def finalize(ob):
    """Weld, bevel the marked hard edges, then shade by angle (flat panels, smooth cylinders/pipes/bevels)."""
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bl = bm.faces.layers.float.get('bev'); bw = bm.edges.layers.float.new('bevel_weight_edge'); n_b = 0
    for e in bm.edges:
        if len(e.link_faces) == 2 and bl is not None:
            a, b = e.link_faces
            w = min(a[bl], b[bl])
            if w > 0 and e.calc_face_angle(0.0) > math.radians(40): e[bw] = min(1.0, w / BEV_MAX); n_b += 1
    bm.to_mesh(me); bm.free(); me.update()
    if n_b:
        md = ob.modifiers.new('bev', 'BEVEL'); md.width = BEV_MAX; md.segments = 2; md.limit_method = 'WEIGHT'; md.harden_normals = True
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier='bev')
    bm = bmesh.new(); bm.from_mesh(ob.data)
    for f in bm.faces: f.smooth = True
    for e in bm.edges:
        if len(e.link_faces) != 2 or e.calc_face_angle(0.0) > SHARP: e.smooth = False
    bm.to_mesh(ob.data); bm.free()
    return n_b
