#!/usr/bin/env python3
"""
Outfit test: hazmat suit for the crew worker (Blender 5.2 / bpy). Design test, not final art.

Built as pieces that each list the skin regions they cover (`cs_covers`), so `equip()` hides the skin underneath:
  SUIT_BODY   fabric coverall over torso/arms/legs (soft volume, broad folds, waist gather, hem bunching)
  SUIT_GLOVES chunky gloves with cuffs                 SUIT_BOOTS  boots with soles and shafts
  SUIT_HOOD   hood with an open face and a glass visor (head and face decals stay visible through the glass)
  SUIT_KIT    belt, zipper, collar, seams, shoulder straps, pack + tank, hose, rescue handle, dosimeter, ID patch
Read design/ART_DIRECTION.md section 14 first: protective clothing, believable fabric volume, seams, visor thickness,
glove/boot construction, harness/pack, dosimeter, rescue handle; no armour plates, toy proportions or glossy plastic.
"""

import math

import bmesh
import bpy
from mathutils import Vector

import character_regions as CR
import character_scout as SC
import character_worker as CW
import cozy_geo
from cozy_geo import B, mat, tri_count

DEFAULT_COLORS = dict(suit="#E3A22F", gloves="#30323C", boots="#30323C", accent="#E0654A", pack="#2B3350",
                      visor=(0.75, 0.85, 0.95))


def _m(color, rough=0.85, metal=0.0, emit=0.0):
    """mat() accepts palette names or any '#RRGGBB' string (custom colours)."""
    if isinstance(color, str) and color.startswith("#"):
        cozy_geo.HEX[color] = color
    return mat(color, rough, metal, emit)

BODY_REGIONS = ["TORSO", "ARM_L", "ARM_R", "LEG_L", "LEG_R"]
HAND_REGIONS = ["HAND_L", "HAND_R"]
FOOT_REGIONS = ["FOOT_L", "FOOT_R"]


def _smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def _join_regions(root, names):
    bm = bmesh.new()
    for o in root.children:
        if o.get("cs_region") in names:
            bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    return bm


def _to_object(bm, name, material, coll, root, covers):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(material)
    o = bpy.data.objects.new(name, me)
    o["cs_covers"] = list(covers)
    o["cs_outfit"] = "hazmat"
    coll.objects.link(o)
    o.parent = root
    return o


def _fabric_body(root, coll, fabric):
    bm = _join_regions(root, BODY_REGIONS)
    bm.normal_update()
    zs = CW.T(0.94)
    for v in bm.verts:
        x, y, z = v.co
        ax = abs(x)
        leg = 1.0 - _smoothstep(0.55, 0.78, z)
        arm = _smoothstep(0.20, 0.27, ax) * _smoothstep(0.62, 0.72, z)
        d = 0.020 + 0.006 * leg + 0.002 * arm
        # broad folds: knee, elbow, waist gather, hem bunching above the boots (diagonal creases)
        fold = 0.0
        fold += 0.012 * math.exp(-((z - 0.40) / 0.09) ** 2) * (0.5 + 0.5 * math.sin(38 * z + 7 * x + 3 * y)) * leg
        fold += 0.010 * math.exp(-((z - (zs - 0.20)) / 0.08) ** 2) * (0.5 + 0.5 * math.sin(34 * z + 5 * y)) * arm
        fold += 0.009 * math.exp(-((z - 0.72) / 0.05) ** 2) * (0.5 + 0.5 * math.sin(30 * math.atan2(y, x) * 0.5 + 24 * z)) * (1 - arm)
        fold += 0.008 * math.exp(-((z - 0.26) / 0.05) ** 2) * (0.5 + 0.5 * math.sin(44 * z + 9 * x)) * leg
        v.co += v.normal * (d + fold)
    return _to_object(bm, "SUIT_BODY", fabric, coll, root, BODY_REGIONS)


def _shell(root, coll, names, name, material, covers, offset):
    bm = _join_regions(root, names)
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * offset
    return _to_object(bm, name, material, coll, root, covers)


def _cast(obj, origin, direction, dist=4.0):
    ok, loc, nrm, _ = obj.ray_cast(Vector(origin), Vector(direction), distance=dist)
    return (loc, nrm) if ok else (None, None)


def _ring(obj, centre, n=40, max_r=0.6):
    """Points hugging the surface of obj around the vertical axis through `centre` (cast outward from inside, so the
    arms beside the body are never hit)."""
    pts = []
    for i in range(n + 1):
        a = i / n * 2 * math.pi
        d = Vector((math.cos(a), math.sin(a), 0.0))
        loc, nrm = _cast(obj, Vector(centre), d, max_r)
        if loc is not None and abs(loc.x) <= CR.ARM_X:
            pts.append(loc + nrm * 0.004)
    return pts


def _line(obj, pts, off=0.005):
    """pts: (a, b, mode) - 'F' front cast at (x=a, z=b), 'B' back cast, 'S' side cast at (y=a, z=b), 'T' down at (x, y)"""
    out = []
    for a, b, m in pts:
        if m == "F":
            loc, nrm = _cast(obj, (a, 3, b), (0, -1, 0))
        elif m == "B":
            loc, nrm = _cast(obj, (a, -3, b), (0, 1, 0))
        elif m == "SR":
            loc, nrm = _cast(obj, (3, a, b), (-1, 0, 0))
        elif m == "SL":
            loc, nrm = _cast(obj, (-3, a, b), (1, 0, 0))
        else:  # 'T'
            loc, nrm = _cast(obj, (a, b, 3), (0, 0, -1))
        if loc is not None:
            out.append(loc + nrm * off)
    return out


def _hood(root, pivot, coll, fabric, glass, rim_mat):
    """Hood shell with a big open face; a clear glass patch over the opening lets the face decals shine through."""
    rx, ry, rz = SC.HRX * 1.10, SC.HRY * 1.10, SC.HRZ * 1.10
    ox, oz0, oh = 0.245, SC.HZ + 0.015, 0.215          # opening: half-width, centre height, half-height
    made = []
    b = B()
    b.sph(1.0, (0, 0, SC.HZ), fabric, scale=(rx, ry, rz), seg=28, ring=18)
    def rho(v):
        return math.hypot(v.x / ox, (v.z - oz0) / oh)

    def surf_y(x, z):
        return SC._fy(x / 1.10, (z - SC.HZ) / 1.10) * 1.10

    drop = [f for f in b.bm.faces if any(v.co.y > 0.0 and rho(v.co) < 1.0 for v in f.verts)]
    bmesh.ops.delete(b.bm, geom=drop, context="FACES")
    bmesh.ops.delete(b.bm, geom=[v for v in b.bm.verts if not v.link_faces], context="VERTS")
    # snap the hole's boundary vertices onto the ellipse so the outline is smooth, not stair-stepped
    for e in b.bm.edges:
        if e.is_boundary:
            for v in e.verts:
                if v.co.y > 0.0:
                    r = rho(v.co)
                    if r > 1e-6:
                        v.co.x /= r
                        v.co.z = oz0 + (v.co.z - oz0) / r
                        v.co.y = surf_y(v.co.x, v.co.z)
    o = b.build("SUIT_HOOD", floor_normalize=False)
    made.append(o)
    # glass: polar grid over the opening (smooth outline), slightly larger than the hole so it tucks under the hood edge
    g = B()
    nr, na = 5, 32
    rows = []
    for i in range(nr + 1):
        rr = 1.06 * i / nr
        ring = []
        for j in range(na):
            a = j / na * 2 * math.pi
            x, z = ox * rr * math.cos(a), oz0 + oh * rr * math.sin(a)
            y = surf_y(x, z) + 0.010
            ring.append(g.bm.verts.new((x, y, z)))
        rows.append(ring)
    centre = g.bm.verts.new((0, surf_y(0, oz0) + 0.010, oz0))
    for j in range(na):
        g.bm.faces.new((centre, rows[1][j], rows[1][(j + 1) % na]))
    for i in range(1, nr):
        for j in range(na):
            g.bm.faces.new((rows[i][j], rows[i + 1][j], rows[i + 1][(j + 1) % na], rows[i][(j + 1) % na]))
    g.mats = [glass]
    for f in g.bm.faces:
        f.material_index = 0
        f.smooth = True
    o = g.build("SUIT_VISOR", floor_normalize=False)
    made.append(o)
    # rim tube hides the hole edge and gives the visor visible thickness
    rim = B()
    pts = []
    for i in range(49):
        a = i / 48 * 2 * math.pi
        x, z = ox * 1.0 * math.cos(a), oz0 + oh * 1.0 * math.sin(a)
        pts.append((x, surf_y(x, z) + 0.006, z))
    rim.tube(pts, 0.016, rim_mat, seg=8)
    o = rim.build("SUIT_VISOR_RIM", floor_normalize=False)
    made.append(o)
    for o in made:
        coll.objects.link(o)
        o.parent = pivot
        o["cs_covers"] = []
        o["cs_outfit"] = "hazmat"
    return made


def build_hazmat(root, coll=None, colors=None):
    """Add the hazmat suit pieces to a crew worker built with regions=True. Returns (pieces, triangles)."""
    coll = coll or bpy.context.scene.collection
    pivot = next(c for c in root.children if c.name.endswith("_HEAD_PIVOT"))
    c = dict(DEFAULT_COLORS)
    c.update(colors or {})
    fabric = _m(c["suit"], 0.9)
    dark = _m(c["gloves"], 0.85)
    boot_m = _m(c["boots"], 0.85)
    navy = _m(c["pack"], 0.85)
    accent = _m(c["accent"], 0.7)
    trim = _m("#30323C", 0.6)
    white = mat("white", 0.6)
    pieces = []

    body = _fabric_body(root, coll, fabric)
    pieces.append(body)
    gloves = _shell(root, coll, HAND_REGIONS, "SUIT_GLOVES", dark, HAND_REGIONS, 0.022)
    boots = _shell(root, coll, FOOT_REGIONS, "SUIT_BOOTS", boot_m, FOOT_REGIONS, 0.026)
    pieces += [gloves, boots]

    kit = B()
    zs = CW.T(0.94)
    for s in (-1, 1):
        x = s * 0.098 * 1.06
        # boot shaft, sole and hem ring over the suit trouser
        kit.cyl(0.098, 0.15, (x, 0.016, 0.175), boot_m, r2=0.094, seg=16)
        kit.tube([(x + 0.122 * math.cos(a), 0.016 + 0.122 * math.sin(a), 0.205) for a in [i / 20 * 2 * math.pi for i in range(21)]],
                 0.014, fabric, seg=6)
        kit.box((0.19, 0.34, 0.03), (x, 0.06, 0.016), boot_m, bevel=0.012, seg=3)
        # glove cuff
        hx = s * 0.345
        kit.cyl(0.094, 0.10, (hx, 0.065, zs - 0.355), dark, r2=0.098, seg=18)
        kit.tube([(hx + 0.10 * math.cos(a), 0.065 + 0.10 * math.sin(a), zs - 0.305) for a in [i / 20 * 2 * math.pi for i in range(21)]],
                 0.011, fabric, seg=6)
    # belt and buckle
    ring = _ring(body, (0, 0, CW.T(0.63)))
    kit.tube(ring, 0.017, trim, seg=6)
    loc, nrm = _cast(body, (0, 3, CW.T(0.63)), (0, -1, 0))
    if loc is not None:
        kit.box((0.05, 0.02, 0.04), (loc.x, loc.y + 0.012, loc.z), mat("brass", 0.4, 0.8), bevel=0.004)
    # zipper, collar
    zip_pts = _line(body, [(0, z, "F") for z in [CW.T(0.63) + 0.03 + i * 0.03 for i in range(11)]], 0.006)
    if len(zip_pts) > 2:
        kit.tube(zip_pts, 0.006, trim, seg=4)
        kit.box((0.016, 0.01, 0.04), (zip_pts[-1].x, zip_pts[-1].y + 0.004, zip_pts[-1].z - 0.02), mat("brass", 0.4, 0.8), bevel=0.002)
    # leg outer seams (side casts at hip height clear of the arms) and ankle hems
    for s, m in ((1, "SR"), (-1, "SL")):
        seam = _line(body, [(0.012, 0.19 + i * 0.045, m) for i in range(9)], 0.004)
        if len(seam) > 2:
            kit.tube(seam, 0.005, mat("mustard", 0.9), seg=5)
    # shoulder straps, snapped to the suit surface
    for s in (-1, 1):
        x = s * 0.105
        strap = (_line(body, [(x, CW.T(0.63) + 0.05, "B"), (x, 0.98, "B")], 0.012)
                 + _line(body, [(x, 0.0, "T")], 0.012)
                 + _line(body, [(x, 1.02, "F"), (x, 0.90, "F"), (x, CW.T(0.63) + 0.03, "F")], 0.012))
        if len(strap) > 3:
            kit.tube(strap, 0.014, navy, seg=5)
    # ID patch on the wearer's left upper arm, dosimeter on the chest
    loc, nrm = _cast(body, (3, 0.0, zs - 0.10), (-1, 0, 0))
    if loc is not None:
        kit.box((0.012, 0.075, 0.075), (loc.x + 0.005, loc.y, loc.z), accent, bevel=0.003)
    loc, nrm = _cast(body, (0.11, 3, 0.95), (0, -1, 0))
    if loc is not None:
        kit.box((0.075, 0.03, 0.10), (loc.x, loc.y + 0.012, loc.z), dark, bevel=0.006)
        kit.box((0.05, 0.008, 0.035), (loc.x, loc.y + 0.03, loc.z + 0.018), mat("olive", 0.4, 0.0, 1.5), bevel=0.002)
    # pack, tank, hose, rescue handle on the back
    kit.box((0.30, 0.13, 0.36), (0, -0.265, 0.90), navy, bevel=0.03, seg=3)
    kit.box((0.20, 0.03, 0.14), (0, -0.345, 0.86), dark, bevel=0.01)
    kit.cyl(0.055, 0.26, (0.20, -0.27, 0.86), white, seg=14)
    kit.sph(0.055, (0.20, -0.27, 0.99), white, seg=14, ring=6)
    kit.cyl(0.02, 0.04, (0.20, -0.27, 1.03), mat("brass", 0.4, 0.8), seg=8)
    kit.tube([(0.20, -0.27, 1.05), (0.17, -0.22, 1.10), (0.11, -0.16, 1.12), (0.10, -0.10, 1.10)], 0.011, trim, seg=5)
    kit.tube([(-0.08 + 0.16 * i / 12, -0.235 - 0.02 * math.sin(math.pi * i / 12), 1.09 + 0.09 * math.sin(math.pi * i / 12))
              for i in range(13)], 0.011, accent, seg=5)
    o = kit.build("SUIT_KIT", floor_normalize=False)
    coll.objects.link(o)
    o.parent = root
    o["cs_covers"] = []
    o["cs_outfit"] = "hazmat"
    pieces.append(o)

    pieces += _hood(root, pivot, coll, fabric, _glass(c["visor"]), trim)
    tris = sum(tri_count(p) for p in pieces)
    return pieces, tris


def _glass(tint=(0.75, 0.85, 0.95)):
    m = bpy.data.materials.new("SUIT_glass")
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*tint, 1)
    b.inputs["Alpha"].default_value = 0.10
    b.inputs["Roughness"].default_value = 0.05
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = "BLENDED"
    return m


def equip(root):
    """Hide every skin region covered by the outfit pieces on this character."""
    covered = set()
    for o in root.children_recursive:
        covered.update(o.get("cs_covers", []))
    CR.set_hidden(root, covered)
    return covered
