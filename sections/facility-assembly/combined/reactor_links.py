"""Reactor hall doors and connector tubes for the combined map (helpers imported by build_combined_map.py).

Everything here is local to the combined scene: the reactor module is never edited. Hall wall openings are cut into
local copies of the linked meshes; connectors are plain placeholder concrete tubes drawn along the plan v7 links.
Status: unreviewed, not accepted.
"""
import bpy, bmesh, math
from mathutils import Vector

# Openings cut through the hall wall, module frame (the reactor is placed with rotation 0, so module frame = plan frame).
# angle: direction the opening faces (outwards), c: centre of the door on the hall axis, hw: half clear width, along a0..a1: the wall
# layer measured along the opening axis from the hall centre, z0..z1: clear height.
HALL_CUTS = {
    'south_door': dict(ang=-math.pi / 2, hw=2.5, a0=10.0, a1=12.2, z0=0.0, z1=5.0, clear_a0=7.8, rooms=('reactor-room',)),
    'label_turbine': dict(ang=math.pi / 2, hw=2.3, a0=10.2, a1=10.5, z0=5.5, z1=6.1, only=('RH walls text WHITE',), islands=True, rooms=('turbine-room',)),
    'label_cooling': dict(ang=math.pi, hw=2.3, a0=10.2, a1=10.5, z0=5.5, z1=6.1, only=('RH walls text WHITE',), islands=True, rooms=('cooling-plant',)),
    'label_waste': dict(ang=-math.pi / 4, hw=2.6, a0=11.2, a1=11.8, z0=5.5, z1=6.1, only=('RH walls text WHITE',), islands=True, rooms=('waste-storage',)),
    'northeast_door': dict(ang=math.pi / 4, hw=2.5, a0=9.8, a1=13.6, z0=0.0, z1=5.0, rooms=('electrical-room',)),
}


def _inside(cut, p, grow=0.0):
    c, s = math.cos(cut['ang']), math.sin(cut['ang'])
    al = p[0] * c + p[1] * s; pe = -p[0] * s + p[1] * c
    return cut['a0'] - grow <= al <= cut['a1'] + grow and abs(pe) <= cut['hw'] + grow and cut['z0'] - grow <= p[2] <= cut['z1'] + grow


def _islands(bm):
    seen = set(); out = []
    for f in bm.faces:
        if f.index in seen: continue
        st = [f]; seen.add(f.index); cur = []
        while st:
            a = st.pop(); cur.append(a)
            for e in a.edges:
                for b in e.link_faces:
                    if b.index not in seen: seen.add(b.index); st.append(b)
        out.append(cur)
    return out


def cut_hall(wrap, omit, objects, wm, active):
    """Cut the listed HALL_CUTS (those whose rooms are all included) out of the linked hall. Wall layers are clipped by bisecting the planes of the opening
    and deleting the faces inside; free-standing dressing (pipes, stations, signs) is removed island by island when its centre falls in the opening,
    text and curve objects when their centre does. Objects with modifiers are kept or omitted whole. Returns {cut name: objects touched}."""
    report = {}
    cuts = {k: v for k, v in HALL_CUTS.items() if all(r in active for r in v['rooms'])}
    if not cuts: return report
    done = {}
    for o in objects:
        if o.type not in ('MESH', 'CURVE', 'FONT') or o.name in omit: continue
        m = wm(o)
        bbc = [m @ Vector(c) for c in o.bound_box]
        touched = [k for k, ct in cuts.items() if ('only' not in ct or o.name in ct['only']) and (any(_inside(ct, p, 0.4) for p in bbc) or _bbox_overlaps(dict(ct, a0=ct.get('clear_a0', ct['a0'])), bbc))]
        if not touched: continue
        if o.type != 'MESH' or o.modifiers:
            centre = sum(bbc, Vector()) / 8
            if any(_inside(dict(cuts[k], a0=cuts[k].get('clear_a0', cuts[k]['a0'])), centre) for k in touched):
                omit.add(o.name); report.setdefault(touched[0], []).append(o.name + ' (omitted)')
            continue
        me = o.data.copy(); me.transform(m)
        bm = bmesh.new(); bm.from_mesh(me)
        changed = False
        big = o.name.startswith(('RH walls', 'R2 floor'))
        for k in touched:
            ct = cuts[k]; c, s = math.cos(ct['ang']), math.sin(ct['ang'])
            if big and not ct.get('islands'):
                for co, no in (((c * ct['a0'], s * ct['a0'], 0), (c, s, 0)), ((c * ct['a1'], s * ct['a1'], 0), (c, s, 0)),
                               ((-s * ct['hw'], c * ct['hw'], 0), (-s, c, 0)), ((s * ct['hw'], -c * ct['hw'], 0), (-s, c, 0)),
                               ((0, 0, ct['z1']), (0, 0, 1))):
                    geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
                    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no, dist=1e-5)
                dead = [f for f in bm.faces if _inside(ct, f.calc_center_median())]
                if dead: bmesh.ops.delete(bm, geom=dead, context='FACES'); changed = True
            else:
                bm.faces.index_update(); dead = []
                cl = dict(ct, a0=ct.get('clear_a0', ct['a0']))      # free-standing dressing is cleared in front of the door as well
                for isl in _islands(bm):
                    pts = [v.co for f in isl for v in f.verts]
                    ctr = sum(pts, Vector()) / len(pts)
                    n_in = sum(1 for p in pts if _inside(cl, p))
                    if _inside(cl, ctr) or n_in > 0.5 * len(pts): dead.extend(isl)
                if dead: bmesh.ops.delete(bm, geom=dead, context='FACES'); changed = True
            if changed: report.setdefault(k, []).append(o.name)
        if not changed:
            bm.free(); bpy.data.meshes.remove(me); continue
        bm.to_mesh(me); bm.free()
        if not me.polygons:
            bpy.data.meshes.remove(me); omit.add(o.name); continue
        n = bpy.data.objects.new(o.name, me); wrap.objects.link(n); omit.add(o.name)
    for k, v in report.items(): print('HALL CUT', k, len(v), 'objects changed')
    return report


def _bbox_overlaps(ct, pts):
    c, s = math.cos(ct['ang']), math.sin(ct['ang'])
    al = [p[0] * c + p[1] * s for p in pts]; pe = [-p[0] * s + p[1] * c for p in pts]; z = [p[2] for p in pts]
    return min(al) <= ct['a1'] and max(al) >= ct['a0'] and min(pe) <= ct['hw'] and max(pe) >= -ct['hw'] and min(z) <= ct['z1'] and max(z) >= ct['z0']


def _ring_solid(bm, ring, z0, z1):
    vs = [bm.verts.new((p[0], p[1], z0)) for p in ring]
    f = bm.faces.new(vs)
    ex = bmesh.ops.extrude_face_region(bm, geom=[f])
    top = [e for e in ex['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, 0, z1 - z0))


def tube(coll, name, pts, w, h, mat_wall, mat_floor, t=0.3, slab=0.25):
    """Open-ended rectangular tube along the plan polyline pts (clear width w, clear height h, wall thickness t, floor top z 0). Corners are mitred."""
    P = [Vector((p[0], p[1])) for p in pts]; n = len(P)
    D = [(P[i + 1] - P[i]).normalized() for i in range(n - 1)]; N = [Vector((-d.y, d.x)) for d in D]
    off = []
    for i in range(n):
        if i == 0: off.append(N[0].copy())
        elif i == n - 1: off.append(N[-1].copy())
        else:
            m = (N[i - 1] + N[i]).normalized(); s = min(1.0 / max(m.dot(N[i]), 0.35), 3.0); off.append(m * s)
    L = lambda d: [P[i] + off[i] * d for i in range(n)]
    R = lambda d: [P[i] - off[i] * d for i in range(n)]
    ring_out = L(w / 2 + t) + R(w / 2 + t)[::-1]
    parts = {'floor': (ring_out, -slab, 0.0, mat_floor), 'roof': (ring_out, h, h + slab, mat_wall),
             'wall L': (L(w / 2 + t) + L(w / 2)[::-1], 0.0, h, mat_wall), 'wall R': (R(w / 2) + R(w / 2 + t)[::-1], 0.0, h, mat_wall)}
    objs = []
    for key, (ring, z0, z1, mat) in parts.items():
        bm = bmesh.new(); _ring_solid(bm, ring, z0, z1)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        me = bpy.data.meshes.new(f'{name} {key}'); bm.to_mesh(me); bm.free(); me.materials.append(mat)
        o = bpy.data.objects.new(f'{name} {key}', me); coll.objects.link(o); objs.append(o)
    return objs


def tube_lights(coll, name, pts, h, every=7.0, energy=120.0):
    """Area lights along the centre line at roof height."""
    P = [Vector((p[0], p[1])) for p in pts]; total = sum((P[i + 1] - P[i]).length for i in range(len(P) - 1))
    k = max(1, int(total // every)); n = 0
    for j in range(k):
        d = (j + 0.5) * total / k; acc = 0.0
        for i in range(len(P) - 1):
            seg = (P[i + 1] - P[i]).length
            if acc + seg >= d:
                q = P[i] + (P[i + 1] - P[i]).normalized() * (d - acc); break
            acc += seg
        ld = bpy.data.lights.new(f'{name} light {j}', 'AREA'); ld.energy = energy; ld.size = 1.6; ld.size_y = 0.4; ld.color = (1.0, 0.92, 0.8)
        lo = bpy.data.objects.new(f'{name} light {j}', ld); lo.location = (q.x, q.y, h - 0.12); coll.objects.link(lo); n += 1
    return n


# ---------------------------------------------------------------------------------------------------------------------------------
# Finished halls: smooth centre lines, spawn-room materials, trim, and spawn airlock doors copied into the connectors.
# ---------------------------------------------------------------------------------------------------------------------------------
import os

SPAWN_MATS = {'wall': 'V13_HALL_wall', 'dado': 'V13_HALL_dado', 'ceiling': 'V_ceiling_mineral', 'floor': 'CS_hall_floor', 'skirt': 'V_graphite',
              'steel': 'steel', 'darksteel': 'darksteel', 'yellow': 'yellow', 'slab': 'CS_slab_concrete'}
AIRLOCK_PREFIXES = ('AIRLOCK', 'LIFE_airlock')
AIRLOCK_ORIGIN = Vector((0.0, 9.32, 0.0))       # door centre in spawn-room module coordinates (measured from the AIRLOCK_* objects)


def load_spawn_assets(spawn_path, fallback):
    """Link the spawn room's wall, dado, ceiling, floor, trim materials and its airlock door objects (the module the combined map already links). Missing ones fall back."""
    with bpy.data.libraries.load(spawn_path, link=True, relative=True) as (src, dst):
        dst.materials = [n for n in SPAWN_MATS.values() if n in src.materials]
        dst.objects = [n for n in src.objects if n.startswith(AIRLOCK_PREFIXES)]
    mats = {}
    for k, n in SPAWN_MATS.items():
        m = next((x for x in dst.materials if x is not None and x.name == n), None)
        mats[k] = m or fallback
    mats['lamp'] = _emissive('HALL lamp panel', (1.0, 0.93, 0.8), 5.0)
    return mats, [o for o in dst.objects if o is not None]


def _emissive(name, col, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = col + (1,); b.inputs['Emission Color'].default_value = col + (1,); b.inputs['Emission Strength'].default_value = strength
    return m


def fillet(pts, r, step=1.0):
    """Centre line through plan points pts with every interior corner replaced by a true circular arc of radius r (reduced where the legs are short), sampled finely; straight legs get points every `step` m."""
    P = [Vector(p) for p in pts]; out = [P[0].copy()]
    for i in range(1, len(P) - 1):
        a, b, c = P[i - 1], P[i], P[i + 1]
        v1 = (a - b).normalized(); v2 = (c - b).normalized()
        ang = math.acos(max(-1.0, min(1.0, v1.dot(v2))))          # interior angle
        turn = math.pi - ang
        if turn < 1e-3: out.append(b.copy()); continue
        t = r * math.tan(turn / 2)
        t = min(t, 0.46 * (a - b).length, 0.46 * (c - b).length)
        reff = t / math.tan(turn / 2)
        t1 = b + v1 * t; t2 = b + v2 * t
        bis = (v1 + v2).normalized(); cen = b + bis * (reff / math.sin(ang / 2))
        a1 = math.atan2(t1.y - cen.y, t1.x - cen.x); a2 = math.atan2(t2.y - cen.y, t2.x - cen.x)
        d = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        n = max(6, int(abs(d) / math.radians(3)))
        for k in range(n + 1):
            ak = a1 + d * k / n; out.append(Vector((cen.x + reff * math.cos(ak), cen.y + reff * math.sin(ak))))
    out.append(P[-1].copy())
    dense = [out[0]]
    for q in out[1:]:
        base = dense[-1]; seg = q - base; L = seg.length
        if L < 1e-6: continue
        for j in range(1, int(L // step) + 1): dense.append(base + seg.normalized() * step * j)
        if (q - dense[-1]).length > 1e-4: dense.append(q)
    return dense


class Path:
    def __init__(self, pts):
        self.P = [Vector(p) for p in pts]; self.n = len(self.P)
        self.cum = [0.0]
        for i in range(1, self.n): self.cum.append(self.cum[-1] + (self.P[i] - self.P[i - 1]).length)
        self.length = self.cum[-1]
        D = [(self.P[i + 1] - self.P[i]).normalized() for i in range(self.n - 1)]; N = [Vector((-d.y, d.x)) for d in D]
        self.off = []
        for i in range(self.n):
            if i == 0: self.off.append(N[0].copy())
            elif i == self.n - 1: self.off.append(N[-1].copy())
            else:
                m = (N[i - 1] + N[i]).normalized(); s = min(1.0 / max(m.dot(N[i]), 0.35), 3.0); self.off.append(m * s)
        self.D, self.N = D, N

    def at(self, s):
        s = max(0.0, min(self.length, s))
        for i in range(self.n - 1):
            if s <= self.cum[i + 1] + 1e-9:
                f = (s - self.cum[i]) / max(self.cum[i + 1] - self.cum[i], 1e-9)
                return self.P[i] + (self.P[i + 1] - self.P[i]) * f, self.D[i], self.N[i]
        return self.P[-1], self.D[-1], self.N[-1]

    def lat(self, d): return [self.P[i] + self.off[i] * d for i in range(self.n)]

    def nearest(self, p):
        """Arclength of the centre-line point closest to plan point p."""
        best = (1e9, 0.0); p = Vector(p)
        for i in range(self.n - 1):
            a, b = self.P[i], self.P[i + 1]; ab = b - a; f = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
            dd = (a + ab * f - p).length
            if dd < best[0]: best = (dd, self.cum[i] + f * ab.length)
        return best[1]


def _uv(bm, scale=2.0):
    layer = bm.loops.layers.uv.verify()
    for f in bm.faces:
        nx, ny, nz = abs(f.normal.x), abs(f.normal.y), abs(f.normal.z)
        for l in f.loops:
            c = l.vert.co
            u, v = ((c.x, c.y) if nz >= max(nx, ny) else ((c.y, c.z) if nx >= ny else (c.x, c.z)))
            l[layer].uv = (u / scale, v / scale)


def solid(coll, name, ring, z0, z1, mat, uv_scale=2.0):
    bm = bmesh.new(); _ring_solid(bm, ring, z0, z1); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); _uv(bm, uv_scale)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = bpy.data.objects.new(name, me); coll.objects.link(o); return o


def obox(coll, name, c, tang, length, width, z0, z1, mat):
    """Box centred on plan point c, long side along tang."""
    t = Vector(tang).normalized(); n = Vector((-t.y, t.x)); c = Vector(c)
    ring = [c - t * length / 2 - n * width / 2, c + t * length / 2 - n * width / 2, c + t * length / 2 + n * width / 2, c - t * length / 2 + n * width / 2]
    return solid(coll, name, ring, z0, z1, mat)


def pipe(coll, name, P, z, r, mat, sides=8):
    bm = bmesh.new(); rings = []
    for i, p in enumerate(P):
        d = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized(); n = Vector((-d.y, d.x))
        rings.append([bm.verts.new((p.x + n.x * r * math.cos(a), p.y + n.y * r * math.cos(a), z + r * math.sin(a))) for a in [2 * math.pi * k / sides for k in range(sides)]])
    for i in range(len(rings) - 1):
        for k in range(sides): bm.faces.new((rings[i][k], rings[i][(k + 1) % sides], rings[i + 1][(k + 1) % sides], rings[i + 1][k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = bpy.data.objects.new(name, me); coll.objects.link(o); return o


def spans(L, openings, sg, pad=0.0):
    """Intervals of arclength [0, L] on side sg that are not inside a wall opening of that side. openings: list of (s0, s1, side)."""
    cuts = sorted((a - pad, b + pad) for a, b, sd in openings if sd == sg)
    out = []; cur = 0.0
    for a, b in cuts:
        if a > cur + 1e-6: out.append((cur, a))
        cur = max(cur, b)
    if cur < L - 1e-6: out.append((cur, L))
    return out


def in_opening(s, openings, margin=0.0, sg=None):
    return any(a - margin <= s <= b + margin and (sg is None or sd == sg) for a, b, sd in openings)


def hall(coll, name, centre, w, h, mats, openings=(), t=0.3, slab=0.25, rib_every=4.0, step_lights=True):
    """A finished hall along the smooth centre line (list of plan points): spawn plaster walls over a washable dado with skirt and cap, spawn mineral ceiling with steel ribs and lamp panels,
    spawn floor with painted lane lines, two conduits. Returns the Path."""
    path = Path(centre); W2 = w / 2; sk = 0.04      # sk: thickness of the finished inner skin over the concrete shell
    ring_out = path.lat(W2 + t) + path.lat(-(W2 + t))[::-1]
    ring_in = path.lat(W2) + path.lat(-W2)[::-1]
    solid(coll, f'{name} floor slab', ring_out, -slab, -sk, mats['slab'])
    solid(coll, f'{name} floor', ring_in, -sk, 0.0, mats['floor'])
    solid(coll, f'{name} roof slab', ring_out, h, h + slab, mats['slab'])
    solid(coll, f'{name} ceiling', ring_in, h - sk, h, mats['ceiling'])
    for side, sg in (('L', 1), ('R', -1)):
        for i, (a, b) in enumerate(spans(path.length, openings, sg)):
            ribbon = lambda d0, d1: patch_ring(path, a, b, sg * d0, sg * d1)
            tag = f'{side}{i}'
            solid(coll, f'{name} wall shell {tag}', ribbon(W2 + t, W2), 0.0, h, mats['slab'])
            solid(coll, f'{name} wall {tag}', ribbon(W2, W2 - sk), sk, h - sk, mats['wall'])
            solid(coll, f'{name} dado {tag}', ribbon(W2 - sk, W2 - sk - 0.05), 0.1, 1.15, mats['dado'])
            solid(coll, f'{name} dado cap {tag}', ribbon(W2 - sk, W2 - sk - 0.07), 1.15, 1.2, mats['skirt'])
            solid(coll, f'{name} skirt {tag}', ribbon(W2 - sk, W2 - sk - 0.09), 0.0, 0.1, mats['skirt'])
            solid(coll, f'{name} lane line {tag}', ribbon(W2 - 0.55, W2 - 0.43), 0.0, 0.012, mats['yellow'])
        pipe(coll, f'{name} conduit {side}', path.lat(sg * (W2 - 0.3)), h - 0.55, 0.07, mats['steel'])
    s = rib_every / 2
    while s < path.length - 0.5:
        c, d, n = path.at(s)
        obox(coll, f'{name} rib', c, d, 0.26, w, h - 0.34, h - 0.02, mats['steel'])
        if step_lights and s + rib_every / 2 < path.length - 0.3:
            c2, d2, n2 = path.at(s + rib_every / 2)
            obox(coll, f'{name} lamp', c2, d2, 1.8, 0.4, h - 0.07, h - 0.02, mats['lamp'])
        s += rib_every
    return path


def airlock(coll, assets, pos, tang, w, h, mats, name='airlock', open_by=1.12):
    """Bulkhead across the hall at plan point pos (hall direction tang) with a copy of the spawn room's airlock double door, leaves parked open into the bulkhead. The copied objects share the
    spawn module's mesh data, so nothing in the source is edited."""
    t = Vector(tang).normalized(); n = Vector((-t.y, t.x)); pos = Vector(pos); W2 = w / 2
    # bulkhead panels beside and above the door frame (frame ring +-1.44 m, top 2.87 m), 0.5 m thick
    for sg in (1, -1):
        c = pos + n * sg * (W2 + 1.44) / 2; obox(coll, f'{name} bulkhead {sg}', c, t, 0.5, W2 - 1.44, 0.0, h, mats['wall'])
    obox(coll, f'{name} bulkhead head', pos, t, 0.5, 2.9, 2.87, h, mats['wall'])
    ang = math.atan2(t.y, t.x)
    # the spawn door faces +y; rotating by (hall direction - 90 degrees) turns that normal along the hall
    M = Matrix.Translation(Vector((pos.x, pos.y, 0.0))) @ Matrix.Rotation(ang - math.pi / 2, 4, 'Z') @ Matrix.Translation(-AIRLOCK_ORIGIN)
    def side(o):
        while o is not None:
            if o.name == 'AIRLOCK_leaf_L': return -1
            if o.name == 'AIRLOCK_leaf_R': return 1
            o = o.parent
        return 0
    count = 0
    for o in assets:
        if o.type == 'EMPTY': continue
        base = _wm(o)
        sd = side(o)
        if sd: base = Matrix.Translation(Vector((sd * open_by, 0.0, 0.0))) @ base
        no = bpy.data.objects.new(f'{name} {o.name}', o.data); no.matrix_basis = M @ base; coll.objects.link(no); count += 1
    return count


def _wm(o):
    m = o.matrix_basis.copy()
    return (_wm(o.parent) @ o.matrix_parent_inverse @ m) if o.parent else m


from mathutils import Matrix  # noqa: E402


# ---------------------------------------------------------------------------------------------------------------------------------
# Hall dressing pass ("umph"): zone colours, accent lighting, coves, pilasters, services, signage, spawn props, haze.
# ---------------------------------------------------------------------------------------------------------------------------------
import random as _random

ZONES = {
    'turbine-room':    dict(accent=(1.0, 0.45, 0.08), tint=(0.78, 0.72, 0.68), name='TURBINE HALL'),
    'electrical-room': dict(accent=(0.12, 0.5, 1.0), tint=(0.62, 0.72, 0.9), name='ELECTRICAL'),
    'waste-storage':   dict(accent=(1.0, 0.72, 0.08), tint=(0.8, 0.78, 0.6), name='WASTE STORAGE'),
    'cooling-plant':   dict(accent=(0.08, 0.9, 0.85), tint=(0.58, 0.82, 0.84), name='COOLING PLANT'),
    'bridge':          dict(accent=(1.0, 0.5, 0.12), tint=(0.78, 0.74, 0.74), name='TURBINE - ELECTRICAL'),
    'service':         dict(accent=(0.3, 0.95, 0.9), tint=(0.7, 0.78, 0.8), name='PLANT SERVICE'),
    'tunnel':          dict(accent=(0.85, 0.92, 1.0), tint=(0.82, 0.82, 0.86), name='REACTOR CONCOURSE'),
}
SPAWN_PROPS = {   # prefix of object names in the spawn module: (mount origin in spawn coordinates, direction the prop faces in degrees)
    'V_HALL_extinguisher': ((-1.70, 7.135, 0.0), 0.0),
    'V_HALL_first_aid': ((-1.70, 7.10, 0.0), 0.0),
    'LIFE_shift_clock': ((1.70, 0.95, 0.0), 180.0),
    'V_HALL_shift_board': ((1.70, 6.0, 0.0), 180.0),
    'HALL_notice': ((1.70, 0.95, 0.0), 180.0),
    'V_HALL_culture_poster': ((1.70, 7.59, 0.0), 180.0),
    'HALL_waiting_bench': ((-2.13, 1.55, 0.0), 0.0),
    'COZY_L_ficus': ((2.37, 5.83, 0.0), 0.0),
    'V_HALL_plant_shelf': ((-2.0, 2.04, 0.0), 0.0),
}


def load_spawn_props(spawn_path):
    """Link the spawn module's objects, then keep those whose root ancestor starts with one of SPAWN_PROPS (the props are parented hierarchies, so the child names differ from the root)."""
    with bpy.data.libraries.load(spawn_path, link=True, relative=True) as (src, dst):
        dst.objects = list(src.objects)
    objs = [o for o in dst.objects if o is not None]
    def root(o):
        while o.parent is not None: o = o.parent
        return o
    keep = []
    for o in objs:
        r = root(o)
        if r.name.startswith(tuple(SPAWN_PROPS)): o['prop_root'] = r.name; keep.append(o)
    return keep


def tinted_copy(mat, tint, name):
    """Local copy of a linked material with its base colour multiplied by tint (inserted between the colour source and the shader), the way the cliff rock is matched elsewhere in the build."""
    m = mat.copy(); m.name = name
    if not m.use_nodes: return m
    nt = m.node_tree; bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None: return m
    link = next((l for l in nt.links if l.to_node == bsdf and l.to_socket.name == 'Base Color'), None)
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = 1.0; mix.inputs[7].default_value = tuple(tint) + (1.0,)
    if link:
        nt.links.new(link.from_socket, mix.inputs[6]); nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])
    else:
        mix.inputs[6].default_value = bsdf.inputs['Base Color'].default_value; nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])
    return m


class MB:
    """Collects many solids of one material into one object."""
    def __init__(self, coll, name, mat):
        self.coll, self.name, self.mat = coll, name, mat; self.bm = bmesh.new(); self.n = 0
    def ring(self, ring, z0, z1):
        _ring_solid(self.bm, ring, z0, z1); self.n += 1
    def box(self, c, t, length, width, z0, z1):
        t = Vector(t).normalized(); nn = Vector((-t.y, t.x)); c = Vector(c)
        self.ring([c - t * length / 2 - nn * width / 2, c + t * length / 2 - nn * width / 2, c + t * length / 2 + nn * width / 2, c - t * length / 2 + nn * width / 2], z0, z1)
    def done(self):
        if not self.n: self.bm.free(); return None
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces); _uv(self.bm)
        me = bpy.data.meshes.new(self.name); self.bm.to_mesh(me); self.bm.free(); me.materials.append(self.mat)
        o = bpy.data.objects.new(self.name, me); self.coll.objects.link(o); return o


def patch_ring(path, s0, s1, d0, d1):
    n = max(2, int(abs(s1 - s0) / 0.4) + 2)
    A = []; B = []
    for i in range(n):
        s = s0 + (s1 - s0) * i / (n - 1); pos, d, nn = path.at(s)
        A.append(pos + nn * d0); B.append(pos + nn * d1)
    return A + B[::-1]


def loft(coll, name, path, section, mat, side=1):
    """Extrude a (lateral d, z) section along the whole path. side -1 mirrors it to the right wall."""
    bm = bmesh.new(); rings = []
    sec = [(side * d, z) for d, z in section]
    for i in range(path.n):
        rings.append([bm.verts.new((path.P[i].x + path.off[i].x * d, path.P[i].y + path.off[i].y * d, z)) for d, z in sec])
    k = len(sec)
    for i in range(path.n - 1):
        for j in range(k): bm.faces.new((rings[i][j], rings[i][(j + 1) % k], rings[i + 1][(j + 1) % k], rings[i + 1][j]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); _uv(bm)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = bpy.data.objects.new(name, me); coll.objects.link(o); return o


def text_obj(coll, body, loc, rot, size, mat, extrude=0.006, align='CENTER'):
    cu = bpy.data.curves.new('HALL sign ' + body, 'FONT'); cu.body = body; cu.size = size; cu.align_x = align; cu.extrude = extrude; cu.resolution_u = 2; cu.materials.append(mat)
    o = bpy.data.objects.new('HALL sign ' + body, cu); o.location = loc; o.rotation_euler = rot; coll.objects.link(o); return o


def place_prop(coll, props, prefix, path, s, sg, W2, sk=0.04, offset=0.0):
    """Copy a spawn-room prop onto the hall wall (sg +1 left, -1 right) at arclength s, facing into the hall."""
    pos, t, nn = path.at(s)
    origin, face = SPAWN_PROPS[prefix]
    P = pos + nn * sg * (W2 - sk + offset); face_dir = -nn * sg
    phi = math.atan2(face_dir.y, face_dir.x) - math.radians(face)
    M = Matrix.Translation(Vector((P.x, P.y, 0.0))) @ Matrix.Rotation(phi, 4, 'Z') @ Matrix.Translation(-Vector(origin))
    n = 0
    for o in props:
        if o.type == 'EMPTY' or o.get('prop_root', '') != prefix: continue
        no = bpy.data.objects.new(f'HALL prop {o.name}', o.data); no.matrix_basis = M @ _wm(o); coll.objects.link(no); n += 1
    return n


def straight_at(path, s, half=1.2, tol_deg=1.5):
    a = path.at(max(s - half, 0))[1]; b = path.at(min(s + half, path.length))[1]
    return math.degrees(math.acos(max(-1.0, min(1.0, a.dot(b))))) < tol_deg


def dress_hall(coll, path, zone_key, mats, props, h=5.0, w=5.0, airlock_s=(), haze=True, seed=0, openings=()):
    """Add the dressing to a hall made by hall(): accent lines, coves, pilasters, wall insets, ceiling ribs and light bars, cable tray, duct, floor runner and LED dashes, signs, props, lights and haze."""
    Z = ZONES[zone_key]; rnd = _random.Random(seed); W2 = w / 2; sk = 0.04; L = path.length
    acc = _emissive(f'HALL accent {zone_key}', Z['accent'], 7.0); acc_dim = _emissive(f'HALL accent dim {zone_key}', Z['accent'], 2.6)
    sign = _emissive('HALL sign ivory', (0.95, 0.92, 0.82), 2.2)
    runner = _runner_mat(); runner_edge = _emissive('HALL runner edge', (0.8, 0.8, 0.82), 0.25)
    wall = mats['wall_t']; compact = w < 3.0; op = openings
    mb = {k: MB(coll, f'{zone_key} {k}', m) for k, m in (('acc', acc), ('accd', acc_dim), ('steel', mats['steel']), ('dark', mats['darksteel']), ('wall', wall), ('lamp', mats['lamp']),
                                                           ('yellow', mats['yellow']), ('sign', sign), ('runner', runner), ('runner_edge', runner_edge), ('ext', mats['darksteel']), ('extacc', acc_dim))}
    # 1. accent lines and baseboard glow (wall sides skip the branch openings)
    for sg in (1, -1):
        for a, b in spans(L, op, sg):
            mb['acc'].ring(patch_ring(path, a, b, sg * (W2 - sk), sg * (W2 - sk - 0.035)), 1.21, 1.26)
            mb['accd'].ring(patch_ring(path, a, b, sg * (W2 - sk), sg * (W2 - sk - 0.1)), 0.1, 0.13)
        lc = min(1.25, W2 - 0.4)
        mb['acc'].ring(patch_ring(path, 0, L, sg * lc, sg * (lc + 0.06)), h - 0.05, h - 0.02)      # ceiling light lines
    # 2. pilasters, insets, ribs, lamps
    s = 1.5
    bay = 0
    screens = []
    while s < L - 1.0:
        if in_opening(s, op, 0.9):
            s += 3.0; bay += 1; continue
        for sg in (1, -1):
            mb['dark'].ring(patch_ring(path, s - 0.2, s + 0.2, sg * (W2 - sk - 0.14), sg * (W2 - sk)), 0.0, h - 0.7)
            if bay % 2 == 0: mb['acc'].ring(patch_ring(path, s - 0.03, s + 0.03, sg * (W2 - sk - 0.16), sg * (W2 - sk - 0.14)), 0.5, 3.7)
        if s + 3.0 < L - 1.0 and not any(abs(s + 1.5 - a) < 1.8 for a in airlock_s) and straight_at(path, s + 1.5, 1.4) and not any(in_opening(x, op, 0.5) for x in (s + 0.4, s + 1.5, s + 2.6)) and not compact:
            for sg in (1, -1):
                if bay % 2 == 1 or sg == -1: mb['steel'].ring(patch_ring(path, s + 0.4, s + 2.6, sg * (W2 - sk - 0.02), sg * (W2 - sk)), 1.43, 2.87)
                mb['dark'].ring(patch_ring(path, s + 0.46, s + 2.54, sg * (W2 - sk - 0.05), sg * (W2 - sk - 0.02)), 1.49, 2.81)
                screens.append((s + 0.5, s + 2.5, sg))
        s += 3.0; bay += 1
    s = 2.0
    while s < L - 1.0:
        c, d, n = path.at(s)
        mb['steel'].box(c, d, 0.3, w, h - 0.5, h - 0.02)
        s += 4.0
    s = 4.0
    while s < L - 1.0:
        c, d, n = path.at(s); mb['lamp'].box(c, d, 2.4, 0.5, h - 0.54, h - 0.5); s += 4.0
    # 3. services: cable tray, duct with flanges and hangers (full-width halls only)
    if not compact:
        mb['dark'].ring(patch_ring(path, 0.5, L - 0.5, 0.5, 1.1), h - 0.75, h - 0.68)
        mb['steel'].ring(patch_ring(path, 0.5, L - 0.5, -1.9, -1.25), h - 0.95, h - 0.5)
        s = 3.0
        while s < L - 1.0:
            mb['dark'].ring(patch_ring(path, s - 0.06, s + 0.06, -1.96, -1.19), h - 1.0, h - 0.45)
            mb['dark'].ring(patch_ring(path, s - 0.02, s + 0.02, 0.5, 1.1), h - 0.68, h)
            s += 3.0
    # 4. floor runner and LED dashes
    rw = 0.85 if not compact else 0.45
    mb['runner'].ring(patch_ring(path, 0, L, -rw, rw), 0.0, 0.01)
    for sg in (1, -1): mb['runner_edge'].ring(patch_ring(path, 0, L, sg * rw, sg * (rw + 0.06)), 0.0, 0.012)
    s = 0.5
    while s < L - 0.4:
        for sg in (1, -1):
            mb['acc'].ring(patch_ring(path, s, s + 0.45, sg * (rw + 0.15), sg * (rw + 0.23)), 0.0, 0.014)
        s += 1.0
    for a in airlock_s:
        mb['yellow'].ring(patch_ring(path, a - 1.05, a - 0.75, -W2 + 0.1, W2 - 0.1), 0.0, 0.012)
        mb['yellow'].ring(patch_ring(path, a + 0.75, a + 1.05, -W2 + 0.1, W2 - 0.1), 0.0, 0.012)
    # exterior: plinth, buttress ribs, roof cap and a dim zone stripe on both outer faces
    for sg in (1, -1):
        for a, b in spans(L, op, sg):
            mb['ext'].ring(patch_ring(path, a, b, sg * (W2 + 0.3), sg * (W2 + 0.42)), 0.0, 0.35)
            mb['ext'].ring(patch_ring(path, a, b, sg * (W2 + 0.3), sg * (W2 + 0.38)), h + 0.05, h + 0.3)
            mb['extacc'].ring(patch_ring(path, a, b, sg * (W2 + 0.3), sg * (W2 + 0.34)), min(3.9, h - 0.2), min(3.98, h - 0.12))
        e = 2.0
        while e < L - 1.0:
            if not in_opening(e, op, 0.6, sg): mb['ext'].ring(patch_ring(path, e - 0.18, e + 0.18, sg * (W2 + 0.3), sg * (W2 + 0.62)), 0.0, h + 0.25)
            e += 5.0
    for m in mb.values(): m.done()
    add_screens(coll, path, zone_key, screens, W2, sk, h)
    # 5. coves (plaster wedge in each wall/ceiling corner) with a glowing strip
    cw = min(0.75, W2 * 0.45)
    for sg in (1, -1):
        for i, (a, b) in enumerate(spans(L, op, sg)):
            sub = Path([path.at(a + (b - a) * k / max(2, int((b - a) / 0.5)))[0] for k in range(max(2, int((b - a) / 0.5)) + 1)]) if op else path
            loft(coll, f'{zone_key} cove {sg}{i}', sub, [(W2 - sk, h - cw), (W2 - sk, h - sk), (W2 - sk - cw, h - sk)], wall, side=sg)
            loft(coll, f'{zone_key} cove glow {sg}{i}', sub, [(W2 - sk - 0.2, h - cw + 0.2), (W2 - sk - 0.26, h - cw + 0.26), (W2 - sk - 0.36, h - cw + 0.16), (W2 - sk - 0.3, h - cw + 0.1)], acc_dim, side=sg)
    # 6. signs
    n0 = path.at(3.2); 
    def wall_sign(s, sg, body, z, size):
        pos, t, nn = path.at(s); alpha = math.atan2(t.y, t.x)
        loc = pos + nn * sg * (W2 - sk - 0.012)
        rot = (math.pi / 2, 0, alpha) if sg == 1 else (math.pi / 2, 0, alpha + math.pi)
        text_obj(coll, body, (loc.x, loc.y, z), rot, size, sign)
    if L > 8:
        wall_sign(3.5, 1, 'REACTOR HALL  <' if not compact else 'SERVICE  <', min(3.05, h - 0.5), 0.2); wall_sign(L - 3.5, -1, Z['name'] + '  >', min(3.05, h - 0.5), 0.2)
        mid = L / 2
        if straight_at(path, mid, 1.0) and not in_opening(mid, op, 1.5, 1): wall_sign(mid, 1, Z['name'], 3.05, 0.2)
    for a in airlock_s:
        pos, t, nn = path.at(a); th = math.atan2(-t.x, t.y)
        text_obj(coll, f'AIRLOCK  {Z["name"]}', (pos.x - t.x * 0.28, pos.y - t.y * 0.28, 3.6), (math.pi / 2, 0, th), 0.22, sign)
        # red beacon above the bulkhead
        b = MB(coll, f'{zone_key} beacon', _emissive('HALL beacon red', (1.0, 0.08, 0.05), 9.0)); b.box(pos - t * 0.3 + nn * 0.0, t, 0.14, 0.14, 4.3, 4.45); b.done()
    # 7. spawn props on straight wall sections
    placed = 0
    if props and L > 8 and not compact:
        spots = []
        s = 6.0
        while s < L - 6.0:
            if straight_at(path, s, 0.5, 14.0) and not any(abs(s - a) < 2.5 for a in airlock_s) and not in_opening(s, op, 2.0): spots.append(s)
            s += 1.0
        rnd.shuffle(spots)
        picks = [('V_HALL_extinguisher', -1), ('V_HALL_first_aid', 1), ('LIFE_shift_clock', 1), ('V_HALL_shift_board', -1), ('V_HALL_culture_poster', 1), ('HALL_waiting_bench', -1)]
        used = []
        for pref, sg in picks:
            for sp in spots:
                if pref == 'HALL_waiting_bench' and not straight_at(path, sp, 1.0, 2.0): continue
                if all(abs(sp - u) > 3.2 for u in used):
                    placed += place_prop(coll, props, pref, path, sp, sg, W2, offset=(0.0 if pref != 'HALL_waiting_bench' else -0.05)); used.append(sp); print('PROP', zone_key, pref, 'side', sg, 'at', tuple(round(v, 1) for v in path.at(sp)[0])); break
    for a in airlock_s:   # a plant either side of every airlock approach
        for sg in (1, -1):
            if straight_at(path, a - 2.2, 1.0): placed += place_prop(coll, props, 'COZY_L_ficus', path, a - 1.9, sg, W2, offset=-0.45)
    # 8. lights: ceiling warm panels, accent cove up-lights
    k = 0; s = 4.0
    while s < L - 1.0:
        c, d, n = path.at(s)
        ld = bpy.data.lights.new(f'{zone_key} bay light {k}', 'AREA'); ld.energy = 60; ld.size = 2.2; ld.size_y = 0.45; ld.color = (1.0, 0.9, 0.78)
        lo = bpy.data.objects.new(f'{zone_key} bay light {k}', ld); lo.location = (c.x, c.y, h - 0.58); lo.rotation_euler = (0, 0, math.atan2(d.y, d.x) + 0.0); coll.objects.link(lo)
        for sg in (1, -1):
            c2 = c + n * sg * (W2 - 0.5)
            ud = bpy.data.lights.new(f'{zone_key} cove light {k}{sg}', 'AREA'); ud.energy = 28; ud.size = 1.2; ud.size_y = 0.3; ud.color = Z['accent']
            uo = bpy.data.objects.new(ud.name, ud); uo.location = (c2.x, c2.y, h - 0.62); uo.rotation_euler = (math.pi, 0, math.atan2(d.y, d.x)); coll.objects.link(uo)
        k += 1; s += 4.0
    # 9. haze
    if haze:
        hm = bpy.data.materials.new(f'{zone_key} haze'); hm.use_nodes = True; nt = hm.node_tree
        for n_ in list(nt.nodes):
            if n_.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n_)
        vs = nt.nodes.new('ShaderNodeVolumeScatter'); vs.inputs['Density'].default_value = 0.014; vs.inputs['Anisotropy'].default_value = 0.55
        out = next(n_ for n_ in nt.nodes if n_.type == 'OUTPUT_MATERIAL'); nt.links.new(vs.outputs['Volume'], out.inputs['Volume'])
        ring_in = path.lat(W2 - sk) + path.lat(-(W2 - sk))[::-1]
        solid(coll, f'{zone_key} haze volume', ring_in, 0.02, h - 0.55, hm)
    return placed


def add_stub_labels(wrap, active, mat):
    """New door labels for the hall's three stubs and two new doors (the old header letters are removed by the label cuts)."""
    labels = [('turbine-room', 'TURBINE HALL', (0.0, 10.36, 5.8), (math.pi / 2, 0, 0.0)),
              ('cooling-plant', 'COOLING PLANT', (-10.36, 0.0, 5.8), (math.pi / 2, 0, math.pi / 2)),
              ('waste-storage', 'WASTE STORAGE', (8.09, -8.09, 5.8), (math.pi / 2, 0, math.radians(225))),
              ('electrical-room', 'ELECTRICAL', (7.95, 7.95, 5.35), (math.pi / 2, 0, math.radians(315))),
              ('reactor-room', 'CONCOURSE', (0.0, -10.72, 5.1), (math.pi / 2, 0, math.pi))]
    for room, body, loc, rot in labels:
        if room in active:
            cu = bpy.data.curves.new('HALL door label ' + body, 'FONT'); cu.body = body; cu.size = 0.2; cu.align_x = 'CENTER'; cu.extrude = 0.006; cu.resolution_u = 2; cu.materials.append(mat)
            o = bpy.data.objects.new('HALL door label ' + body, cu); o.location = loc; o.rotation_euler = rot; wrap.objects.link(o)


SCREEN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'textures')


def screen_material(zone_key, k):
    name = f'HALL screen {zone_key} {k}'
    if name in bpy.data.materials: return bpy.data.materials[name]
    path = os.path.join(SCREEN_DIR, f'hall_screen_{zone_key}_{k}.png')
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled'); tex = nt.nodes.new('ShaderNodeTexImage')
    if os.path.exists(path):
        tex.image = bpy.data.images.load(path, check_existing=True); tex.image.colorspace_settings.name = 'sRGB'
    tex.extension = 'CLIP'
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color']); nt.links.new(tex.outputs['Color'], bsdf.inputs['Emission Color'])
    bsdf.inputs['Emission Strength'].default_value = 2.2; bsdf.inputs['Roughness'].default_value = 0.12; bsdf.inputs['Metallic'].default_value = 0.0
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m


def add_screens(coll, path, zone_key, screens, W2, sk, h=5.0):
    """One lit display quad per recessed wall panel, UV 0..1 over the panel, one of four designs per panel (schematic, status, route map, trace)."""
    groups = {}
    for i, (s0, s1, sg) in enumerate(screens):
        groups.setdefault(i % 4, []).append((s0, s1, sg))
    for k, items in groups.items():
        bm = bmesh.new(); uv = bm.loops.layers.uv.verify()
        for s0, s1, sg in items:
            a, ta, na = path.at(s0); b, tb, nb = path.at(s1); d = W2 - sk - 0.058
            pa = a + na * sg * d; pb = b + nb * sg * d; z0, z1 = 1.55, min(2.75, h - 0.5)
            vs = [bm.verts.new((pa.x, pa.y, z0)), bm.verts.new((pb.x, pb.y, z0)), bm.verts.new((pb.x, pb.y, z1)), bm.verts.new((pa.x, pa.y, z1))]
            ua, ub = (0.0, 1.0)       # checked in renders: this reads correctly on both walls
            uvs = {vs[0]: (ua, 0), vs[1]: (ub, 0), vs[2]: (ub, 1), vs[3]: (ua, 1)}
            f = bm.faces.new(vs if sg == -1 else vs[::-1])
            for l in f.loops: l[uv].uv = uvs[l.vert]
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        me = bpy.data.meshes.new(f'{zone_key} screens {k}'); bm.to_mesh(me); bm.free(); me.materials.append(screen_material(zone_key, k))
        o = bpy.data.objects.new(f'{zone_key} screens {k}', me); coll.objects.link(o)


def _runner_mat():
    if 'HALL runner' in bpy.data.materials: return bpy.data.materials['HALL runner']
    m = bpy.data.materials.new('HALL runner'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.045, 0.05, 0.058, 1); b.inputs['Roughness'].default_value = 0.38; b.inputs['Metallic'].default_value = 0.0
    return m


def lintel(coll, name, path, a, b, sg, W2, z0, z1, mats, t=0.3, sk=0.04):
    """Fill the part of a wall opening above a lower branch hall (concrete shell and plaster skin)."""
    solid(coll, f'{name} shell', patch_ring(path, a, b, sg * (W2 + t), sg * W2), z0, z1, mats['slab'])
    solid(coll, f'{name} skin', patch_ring(path, a, b, sg * W2, sg * (W2 - sk)), z0, z1 - sk, mats['wall'])
