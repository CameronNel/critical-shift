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
        touched = [k for k, ct in cuts.items() if any(_inside(ct, p, 0.4) for p in bbc) or _bbox_overlaps(dict(ct, a0=ct.get('clear_a0', ct['a0'])), bbc)]
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
            if big:
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


def hall(coll, name, centre, w, h, mats, t=0.3, slab=0.25, rib_every=4.0, step_lights=True):
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
        ribbon = lambda d0, d1: path.lat(sg * d0) + path.lat(sg * d1)[::-1]
        solid(coll, f'{name} wall shell {side}', ribbon(W2 + t, W2), 0.0, h, mats['slab'])
        solid(coll, f'{name} wall {side}', ribbon(W2, W2 - sk), sk, h - sk, mats['wall'])
        solid(coll, f'{name} dado {side}', ribbon(W2 - sk, W2 - sk - 0.05), 0.1, 1.15, mats['dado'])
        solid(coll, f'{name} dado cap {side}', ribbon(W2 - sk, W2 - sk - 0.07), 1.15, 1.2, mats['skirt'])
        solid(coll, f'{name} skirt {side}', ribbon(W2 - sk, W2 - sk - 0.09), 0.0, 0.1, mats['skirt'])
        solid(coll, f'{name} lane line {side}', ribbon(W2 - 0.55, W2 - 0.43), 0.0, 0.012, mats['yellow'])
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
