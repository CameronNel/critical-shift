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
