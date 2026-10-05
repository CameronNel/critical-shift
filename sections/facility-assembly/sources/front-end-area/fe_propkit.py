"""Small shared helpers for the hand-modelled yard props: studs/rivets/bolts, weld seams, angular rocks, and a position-based
vertex-colour weathering pass (ground dirt, rain streaks, low-frequency blotches) so props are not flat single-colour parts."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler
from fe_kit import *

FACE = {'+x': (0, math.pi / 2, 0), '-x': (0, -math.pi / 2, 0), '+y': (-math.pi / 2, 0, 0), '-y': (math.pi / 2, 0, 0), '+z': (0, 0, 0), '-z': (math.pi, 0, 0)}

def p_stud(r=0.014, h=0.012, seg=5, taper=0.55):
    """Domed rivet/bolt head: a frustum with a top cap only (no hidden bottom), axis +z, base at z=0."""
    pb = bmesh.new(); b = [pb.verts.new(Vector((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), 0))) for i in range(seg)]
    t = [pb.verts.new(Vector((r * taper * math.cos(2 * math.pi * i / seg), r * taper * math.sin(2 * math.pi * i / seg), h))) for i in range(seg)]
    for i in range(seg): pb.faces.new((b[i], b[(i + 1) % seg], t[(i + 1) % seg], t[i]))
    pb.faces.new(t[::-1] if False else t)
    bmesh.ops.recalc_face_normals(pb, faces=pb.faces[:])
    return pb

def studs(m, pts, face='+y', r=0.014, h=0.012, seg=5, mi=None, rgba=None):
    """Rivet heads at the given points, facing +-x/y/z."""
    for p in pts: m.add(p_stud(r, h, seg), p, FACE[face], (1, 1, 1), mi, rgba)

def stud_row(m, a, b, n, face='+y', **kw):
    a = Vector(a); b = Vector(b)
    studs(m, [a.lerp(b, i / max(n - 1, 1)) for i in range(n)], face, **kw)

def hex_bolt(m, p, face='+y', r=0.02, h=0.016, mi=None, rgba=None):
    m.add(p_cyl(r, h, 6), Vector(p), FACE[face], (1, 1, 1), mi, rgba)

def add_var(m, pb, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), mi=None, rgba=None, var=0.2, rnd=None, flat=True):
    """m.add, then multiply each new face's colour by a random factor (per-face tonal variation, good for flat-shaded rock)."""
    rnd = rnd or random
    n0 = len(m.bm.faces); m.add(pb, loc, rot, scale, mi, rgba)
    m.bm.faces.ensure_lookup_table()
    for f in m.bm.faces[n0:]:
        k = 1.0 + rnd.uniform(-var, var)
        if flat: f.smooth = False
        for l in f.loops:
            c = l[m.layer]; l[m.layer] = (min(c[0] * k, 1), min(c[1] * k, 1), min(c[2] * k, 1), 1)

def p_rock(rnd, size=0.2, squash=0.75, jag=0.28, sub=1):
    """Angular lump: jittered icosphere, flat-bottomed."""
    pb = bmesh.new(); res = bmesh.ops.create_icosphere(pb, subdivisions=sub, radius=1.0)
    ax = Vector((rnd.uniform(0.8, 1.25), rnd.uniform(0.8, 1.25), squash * rnd.uniform(0.8, 1.15)))
    for v in res['verts']:
        k = 1.0 + rnd.uniform(-jag, jag)
        v.co = Vector((v.co.x * ax.x, v.co.y * ax.y, max(v.co.z * ax.z, -0.35 * ax.z))) * (size * k)
    for f in pb.faces: f.smooth = False
    return pb

def _hash(x, y, z, s):
    return math.sin(x * 12.9898 + y * 78.233 + z * 37.719 + s * 11.1) * 43758.5453 % 1.0

def _noise(x, y, z, s):
    """Smooth-ish low-frequency noise in [-1,1] built from a few sines."""
    return (math.sin(x * 2.3 + s) * math.cos(y * 1.9 - s * 0.7) + math.sin(z * 3.1 + x * 1.3 + s * 1.7) * 0.6 + math.sin((x + y) * 5.3 + z * 2.1 + s * 0.3) * 0.35) / 1.95

def crisp(m, angle=40.0):
    """Smooth-by-angle: edges sharper than `angle` shade flat, so unbevelled boxes stay crisp while cylinders and lathes stay round."""
    lim = math.radians(angle)
    for e in m.bm.edges:
        if len(e.link_faces) == 2:
            a = e.calc_face_angle(None)
            e.smooth = a is None or a < lim

def weather(m, seed=0, dirt=0.5, dirt_h=0.3, streak=0.25, blotch=0.16, top=0.0, mud=(0.16, 0.11, 0.07), zmax=None, skip_emissive=True, angle=40.0):
    """Position based wear on the vertex colours: ground-splash dirt (dark mud at the foot), vertical rain streaks, low-frequency blotches, and dust on top-facing faces."""
    bm = m.bm; lay = m.layer; emi = None
    for mi_, mat in enumerate(m.mats):
        if mat is not None and mat.name == 'emissive': emi = mi_
    zmax = zmax or max((v.co.z for v in bm.verts), default=1.0) or 1.0
    for f in bm.faces:
        if skip_emissive and f.material_index == emi: continue
        up = max(f.normal.z, 0.0)
        for l in f.loops:
            co = l.vert.co; c = l[lay]
            k = 1.0 + blotch * _noise(co.x, co.y, co.z, seed)
            w = dirt * math.exp(-max(co.z, 0.0) / dirt_h) + streak * max(0.0, math.sin(co.x * 31.0 + co.y * 23.0 + seed * 3.0)) ** 6 * (0.3 + co.z / zmax)
            w = min(w, 0.85); t = top * up
            r, g, b = c[0] * k, c[1] * k, c[2] * k
            r, g, b = r * (1 - w) + mud[0] * w, g * (1 - w) + mud[1] * w, b * (1 - w) + mud[2] * w
            if t: r, g, b = r + (0.34 - r) * t * 0.5, g + (0.31 - g) * t * 0.5, b + (0.26 - b) * t * 0.5
            l[lay] = (min(r, 1.0), min(g, 1.0), min(b, 1.0), c[3])
    crisp(m, angle)

def ring_pts(cx, cy, R, n, a0=0.0):
    return [(cx + R * math.cos(a0 + 2 * math.pi * i / n), cy + R * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]

def cable(m, pts, r=0.012, seg=5, mi=None, rgba=None):
    """Polyline hose/cable of thin cylinders with no joints (cheap)."""
    for a, b in zip(pts[:-1], pts[1:]): m.between(a, b, r, seg=seg, mi=mi, rgba=rgba)

def bez(p0, p1, p2, n=6):
    out = []
    for i in range(n + 1):
        t = i / n; out.append(tuple((1 - t) ** 2 * a + 2 * (1 - t) * t * b + t * t * c for a, b, c in zip(p0, p1, p2)))
    return out

def p_frustum(bl, bw, tl, tw, h, r=0.02, seg=1, shift=(0.0, 0.0)):
    """Box that tapers from a (bl x bw) base at z=0 to a (tl x tw) top at z=h, chamfered; shift moves the top in x,y."""
    pb = bmesh.new(); bmesh.ops.create_cube(pb, size=1.0)
    for v in pb.verts:
        if v.co.z < 0: v.co = Vector((v.co.x * bl, v.co.y * bw, 0.0))
        else: v.co = Vector((v.co.x * tl + shift[0], v.co.y * tw + shift[1], h))
    if r > 0: bmesh.ops.bevel(pb, geom=pb.edges[:], offset=r, segments=seg, affect='EDGES')
    for f in pb.faces: f.smooth = False
    return pb

def p_wheel_spoked(R=0.21, w=0.05, spokes=5, seg=16):
    """Iron railway wheel about the z axis: flanged rim, hub, thin spokes."""
    pb = p_lathe([(R - 0.03, -w / 2), (R, -w / 2 + 0.006), (R, w / 2 - 0.012), (R + 0.016, w / 2 - 0.006), (R + 0.016, w / 2 + 0.01), (R - 0.03, w / 2)], seg, close=False)
    hub = p_cyl(0.045, w * 1.5, 10); xf(hub, (0, 0, 0.004))
    bmesh.ops.recalc_face_normals(pb, faces=pb.faces[:])
    me = bpy.data.meshes.new('t'); hub.to_mesh(me); hub.free(); pb.from_mesh(me); bpy.data.meshes.remove(me)
    for k in range(spokes):
        a = k * 2 * math.pi / spokes
        sp = p_rbox(R - 0.06, 0.022, w * 0.7, 0.004, 1); xf(sp, (math.cos(a) * (R - 0.02) / 2 + 0.0, math.sin(a) * (R - 0.02) / 2, 0), (0, 0, a))
        me = bpy.data.meshes.new('t'); sp.to_mesh(me); sp.free(); pb.from_mesh(me); bpy.data.meshes.remove(me)
    return pb

def p_arc_band(R, z0, z1, a0, a1, seg=10, t=0.004):
    """Raised curved label patch on a cylinder of radius R (about z), from angle a0 to a1."""
    pb = bmesh.new(); rows = []
    for i in range(seg + 1):
        a = a0 + (a1 - a0) * i / seg
        rows.append([pb.verts.new(Vector(((R + t * k) * math.cos(a), (R + t * k) * math.sin(a), z))) for k, z in ((0, z0), (0, z1), (1, z1), (1, z0))])
    for i in range(seg):
        A, B = rows[i], rows[i + 1]
        pb.faces.new((A[3], B[3], B[2], A[2])); pb.faces.new((A[1], A[2], B[2], B[1])); pb.faces.new((A[0], A[3], B[3], B[0]))
    pb.faces.new(rows[0][::-1] if False else rows[0]); pb.faces.new(rows[-1][::-1])
    bmesh.ops.recalc_face_normals(pb, faces=pb.faces[:])
    return pb

def dent(bm, center_ang, center_z, depth=0.012, size=0.07, R=0.29):
    """Push body vertices inward around a point on a cylinder of radius R (about z)."""
    for v in bm.verts:
        r = math.hypot(v.co.x, v.co.y)
        if r < R * 0.8: continue
        a = math.atan2(v.co.y, v.co.x); da = math.atan2(math.sin(a - center_ang), math.cos(a - center_ang)) * R; dz = v.co.z - center_z
        w = math.exp(-(da * da + dz * dz) / (2 * size * size))
        if w > 0.02:
            k = (r - depth * w) / r; v.co.x *= k; v.co.y *= k
