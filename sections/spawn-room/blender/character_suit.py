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


LODF = 1                                   # 1 = full detail, 2 = medium (smooth, lighter kit), 3 = far (coarse, distance only)


def _ktube(kit, path, r, m, seg=8, caps=True):
    path = list(path)
    if LODF >= 3 and len(path) > 6:
        path = path[::2] + ([path[-1]] if (len(path) - 1) % 2 else [])
        seg = max(3, seg - 2)
    elif LODF == 2:
        seg = max(4, seg - 1)
    kit.tube(path, r, m, seg=seg, caps=caps)


def _kbox(kit, size, pos, m, bevel=0.004, rot=None, seg=2, taper_top=0.0):
    if LODF >= 3:
        bevel, seg = (0.0 if min(size) < 0.03 else min(bevel, 0.006)), 1
    elif LODF == 2:
        bevel, seg = (bevel if min(size) >= 0.02 else 0.0), 1
    kit.box(size, pos, m, bevel=bevel, rot=rot, seg=seg, taper_top=taper_top)


def _kcyl(kit, r, h, pos, m, r2=None, seg=16, axis="Z"):
    kit.cyl(r, h, pos, m, r2=r2, seg=(max(6, seg // 2) if LODF >= 3 else max(8, seg * 3 // 4) if LODF == 2 else seg), axis=axis)


def _ksph(kit, r, pos, m, scale=(1, 1, 1), seg=12, ring=8):
    if LODF >= 3:
        seg, ring = max(6, seg // 2), max(4, ring // 2)
    elif LODF == 2:
        seg, ring = max(8, seg * 3 // 4), max(5, ring * 3 // 4)
    kit.sph(r, pos, m, scale=scale, seg=seg, ring=ring)


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
        d = 0.020 + 0.006 * leg + 0.002 * arm + (0.007 if LODF >= 3 else 0.0)   # coarser body: sit a bit further out
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


def _ring(obj, centre, n=40, max_r=0.6, arm=False):
    """Points hugging the surface of obj around the vertical axis through `centre` (cast outward from inside, so the
    arms beside the body are never hit)."""
    pts = []
    for i in range(n + 1):
        a = i / n * 2 * math.pi
        d = Vector((math.cos(a), math.sin(a), 0.0))
        loc, nrm = _cast(obj, Vector(centre), d, max_r)
        if loc is not None and (arm or abs(loc.x) <= CR.ARM_X):
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
    b.sph(1.0, (0, 0, SC.HZ), fabric, scale=(rx, ry, rz), seg=28 if LODF < 3 else 20, ring=18 if LODF < 3 else 13)
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
    nr, na = (5, 32) if LODF < 3 else (3, 20)
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
    for i in range(49 if LODF < 3 else 33):
        a = i / (48 if LODF < 3 else 32) * 2 * math.pi
        x, z = ox * 1.0 * math.cos(a), oz0 + oh * 1.0 * math.sin(a)
        pts.append((x, surf_y(x, z) + 0.006, z))
    _ktube(rim, pts, 0.016, rim_mat, seg=8)
    o = rim.build("SUIT_VISOR_RIM", floor_normalize=False)
    made.append(o)
    for o in made:
        coll.objects.link(o)
        o.parent = pivot
        o["cs_covers"] = []
        o["cs_outfit"] = "hazmat"
    return made


def _flat_poly(kit, pts_xz, y, thick, m):
    """Thin flat shape in the XZ plane at depth y, extruded by `thick` along y (used for patches and the trefoil)."""
    bm = kit.bm
    front = [bm.verts.new((x, y, z)) for x, z in pts_xz]
    back = [bm.verts.new((x, y + thick, z)) for x, z in pts_xz]
    faces = [bm.faces.new(front[::-1]), bm.faces.new(back)]
    n = len(pts_xz)
    for i in range(n):
        faces.append(bm.faces.new((front[i], front[(i + 1) % n], back[(i + 1) % n], back[i])))
    i = kit._idx(m)
    for f in faces:
        f.material_index = i
        f.smooth = False


def _trefoil(kit, cx, y, cz, r_out, r_in, thick, m, face=-1):
    """Radiation trefoil: three 60-degree wedges plus a hub. face=-1 means it faces -y (the back)."""
    for k in range(3):
        a0 = math.radians(90 + k * 120 - 30)
        a1 = a0 + math.radians(60)
        arc = [a0 + (a1 - a0) * i / 6 for i in range(7)]
        pts = [(cx + r_out * math.cos(a), cz + r_out * math.sin(a)) for a in arc]
        pts += [(cx + r_in * math.cos(a), cz + r_in * math.sin(a)) for a in arc[::-1]]
        _flat_poly(kit, pts, y, thick * face, m)
    hub = [(cx + r_in * 0.55 * math.cos(a), cz + r_in * 0.55 * math.sin(a)) for a in [i / 10 * 2 * math.pi for i in range(10)]]
    _flat_poly(kit, hub, y, thick * face, m)


def _details(kit, body, zs, fabric, trim, accent, boot_m, dark, navy):
    """Small readable extras: patches, pockets, tape, radio, torch, gauges, straps. Kept low-poly on purpose."""
    tape = mat("white", 0.35)
    brass = mat("brass", 0.4, 0.8)
    lens = mat("mustard", 0.3, 0.0, 2.0)
    for sgn in (-1, 1):
        lx = sgn * 0.098 * 1.06
        # soft knee patch
        loc, nrm = _cast(body, (lx, 3, 0.40), (0, -1, 0))
        if loc is not None:
            _kbox(kit, (0.085, 0.016, 0.10), (loc.x, loc.y + 0.006, loc.z), trim, bevel=0.006)
        # reflective safety tape on the shin and upper arm
        ring = _ring(body, (lx, 0.012, 0.31), n=20, max_r=0.3)
        if len(ring) > 6:
            _ktube(kit, ring, 0.011, tape, seg=4)
        arm_c = (sgn * 0.335, 0.045, zs - 0.235)
        ring = _ring(body, arm_c, n=20, max_r=0.3, arm=True)
        if len(ring) > 6:
            _ktube(kit, ring, 0.010, tape, seg=4)
        # elbow patch on the outside of the arm
        loc, nrm = _cast(body, (sgn * 3, 0.02, zs - 0.18), (-sgn, 0, 0))
        if loc is not None:
            _kbox(kit, (0.014, 0.075, 0.085), (loc.x + nrm.x * 0.005, loc.y, loc.z), trim, bevel=0.005)
        # velcro tab on the glove cuff and a strap across the boot
        _kbox(kit, (0.055, 0.016, 0.04), (sgn * 0.345, 0.16, zs - 0.335), accent, bevel=0.005)
        _ktube(kit, [(lx + 0.103 * math.cos(a), 0.016 + 0.103 * math.sin(a), 0.125) for a in [i / 18 * 2 * math.pi for i in range(19)]],
                 0.011, accent, seg=4)
        _kbox(kit, (0.03, 0.016, 0.03), (lx, 0.016 + 0.108, 0.125), brass, bevel=0.003)
    # chest pocket with a flap and button, name tag above it (wearer's right = -x)
    loc, nrm = _cast(body, (-0.11, 3, 0.86), (0, -1, 0))
    if loc is not None:
        _kbox(kit, (0.09, 0.016, 0.075), (loc.x, loc.y + 0.006, loc.z), fabric, bevel=0.006)
        _kbox(kit, (0.094, 0.02, 0.03), (loc.x, loc.y + 0.01, loc.z + 0.03), trim, bevel=0.005)
        _kcyl(kit, 0.008, 0.008, (loc.x, loc.y + 0.02, loc.z + 0.03 - 0.004), brass, seg=8, axis="Y")
    loc, nrm = _cast(body, (-0.11, 3, 1.0), (0, -1, 0))
    if loc is not None:
        _kbox(kit, (0.085, 0.012, 0.03), (loc.x, loc.y + 0.006, loc.z), mat("white", 0.6), bevel=0.003)
        _kbox(kit, (0.06, 0.006, 0.006), (loc.x, loc.y + 0.013, loc.z), dark, bevel=0.0)
    # thigh pocket with flap on the wearer's right leg
    loc, nrm = _cast(body, (-0.104, 3, 0.53), (0, -1, 0))
    if loc is not None:
        _kbox(kit, (0.085, 0.018, 0.09), (loc.x, loc.y + 0.007, loc.z), fabric, bevel=0.006)
        _kbox(kit, (0.09, 0.022, 0.032), (loc.x, loc.y + 0.011, loc.z + 0.03), trim, bevel=0.005)
        _kcyl(kit, 0.008, 0.008, (loc.x, loc.y + 0.022, loc.z + 0.026), brass, seg=8, axis="Y")
    # radio on the right strap, with a stubby antenna; torch clipped on the belt
    _kbox(kit, (0.05, 0.03, 0.075), (-0.105, 0.20, 0.95), dark, bevel=0.006)
    _kcyl(kit, 0.006, 0.09, (-0.115, 0.20, 0.985), dark, seg=6)
    _ksph(kit, 0.008, (-0.095, 0.218, 0.965), mat("olive", 0.4, 0.0, 1.5), seg=6, ring=4)
    loc, nrm = _cast(body, (-0.17, 3, 0.735), (0, -1, 0))
    if loc is not None:
        _kcyl(kit, 0.02, 0.11, (loc.x, loc.y + 0.025, loc.z - 0.11), dark, seg=10)
        _kcyl(kit, 0.026, 0.03, (loc.x, loc.y + 0.025, loc.z - 0.03), accent, seg=10)
        _ksph(kit, 0.02, (loc.x, loc.y + 0.025, loc.z - 0.115), lens, scale=(1, 1, 0.5), seg=8, ring=5)
    # pack extras: strap and buckle, side pouch, gauge, beacon, trefoil warning patch
    _kbox(kit, (0.31, 0.142, 0.022), (0, -0.265, 0.80), trim, bevel=0.004)
    _kbox(kit, (0.04, 0.02, 0.035), (0.0, -0.335, 0.80), brass, bevel=0.004)
    _kbox(kit, (0.06, 0.09, 0.13), (-0.185, -0.265, 0.82), dark, bevel=0.012)
    _ksph(kit, 0.032, (0.20, -0.328, 0.95), mat("white", 0.5), scale=(1, 0.3, 1), seg=12, ring=6)
    _ksph(kit, 0.02, (0.20, -0.336, 0.95), mat("charcoal", 0.5), scale=(1, 0.3, 1), seg=8, ring=5)
    _ksph(kit, 0.02, (0.09, -0.265, 1.09), accent, scale=(1, 1, 0.8), seg=8, ring=5)
    _trefoil(kit, 0.0, -0.361, 0.93, 0.055, 0.02, 0.004, mat("mustard", 0.5))
    # shoulder ID/loop tab
    _kbox(kit, (0.035, 0.05, 0.012), (0.19, 0.0, zs + 0.075), accent, bevel=0.004)


def _hood_details(pivot, coll, trim, accent, dark):
    """Headlamp on the hood, a filter canister on the cheek, and two drawcord toggles under the visor."""
    b = B()
    hz = SC.HZ
    lens = mat("mustard", 0.3, 0.0, 2.5)
    _kbox(b, (0.06, 0.045, 0.04), (0.10, 0.10, hz + SC.HRZ * 1.10 - 0.012), dark, bevel=0.008, rot=None)
    _ksph(b, 0.016, (0.10, 0.128, hz + SC.HRZ * 1.10 - 0.012), lens, scale=(1, 0.5, 1), seg=8, ring=5)
    _kcyl(b, 0.036, 0.05, (-(SC.HRX * 1.10) + 0.005, 0.02, hz - 0.13), dark, seg=12, axis="X")
    _kcyl(b, 0.038, 0.012, (-(SC.HRX * 1.10) - 0.022, 0.02, hz - 0.13), mat("brass", 0.4, 0.8), seg=12, axis="X")
    for s in (-1, 1):
        x = s * 0.075
        y = SC._fy(x / 1.10, (hz - 0.21 - hz) / 1.10) * 1.10 + 0.02
        _ktube(b, [(x, y, hz - 0.205), (x + s * 0.005, y + 0.006, hz - 0.255), (x + s * 0.01, y + 0.004, hz - 0.29)], 0.004, dark, seg=4)
        _ksph(b, 0.013, (x + s * 0.01, y + 0.004, hz - 0.30), accent, seg=8, ring=5)
    o = b.build("SUIT_HOOD_KIT", floor_normalize=False)
    coll.objects.link(o)
    o.parent = pivot
    o["cs_covers"] = []
    o["cs_outfit"] = "hazmat"
    return o


def build_hazmat(root, coll=None, colors=None, lod=0, style="reference"):
    """Add the owner-reference suit; style='legacy' retains the prior design test.

    Both styles use the same worker, hidden-region/equip contract and HERO_SUIT
    library entrypoint. The reference style is hero authoring geometry, not a
    replacement for the parked rig's engine delivery or animation validation.
    """
    if style == "reference":
        from hazmat_reference import build_reference
        return build_reference(root, coll or bpy.context.scene.collection, colors, lod)
    if style != "legacy":
        raise ValueError("Unknown hazmat style: " + style)
    global LODF
    LODF = 1 + int(lod)
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
        _kcyl(kit, 0.098 if LODF < 3 else 0.086, 0.15, (x, 0.016, 0.175), boot_m, r2=0.094 if LODF < 3 else 0.082, seg=16)
        _ktube(kit, [(x + 0.122 * math.cos(a), 0.016 + 0.122 * math.sin(a), 0.205) for a in [i / 20 * 2 * math.pi for i in range(21)]],
                 0.014, fabric, seg=6)
        _kbox(kit, (0.19, 0.34, 0.03), (x, 0.06, 0.016), boot_m, bevel=0.012, seg=3)
        # glove cuff
        hx = s * 0.345
        _kcyl(kit, 0.094 if LODF < 3 else 0.086, 0.10, (hx, 0.065, zs - 0.355), dark, r2=0.098 if LODF < 3 else 0.090, seg=18)
        _ktube(kit, [(hx + 0.10 * math.cos(a), 0.065 + 0.10 * math.sin(a), zs - 0.305) for a in [i / 20 * 2 * math.pi for i in range(21)]],
                 0.011, fabric, seg=6)
    # belt and buckle
    ring = _ring(body, (0, 0, CW.T(0.63)))
    _ktube(kit, ring, 0.017, trim, seg=6)
    loc, nrm = _cast(body, (0, 3, CW.T(0.63)), (0, -1, 0))
    if loc is not None:
        _kbox(kit, (0.05, 0.02, 0.04), (loc.x, loc.y + 0.012, loc.z), mat("brass", 0.4, 0.8), bevel=0.004)
    # zipper, collar
    zip_pts = _line(body, [(0, z, "F") for z in [CW.T(0.63) + 0.03 + i * 0.03 for i in range(11)]], 0.006)
    if len(zip_pts) > 2:
        _ktube(kit, zip_pts, 0.006, trim, seg=4)
        _kbox(kit, (0.016, 0.01, 0.04), (zip_pts[-1].x, zip_pts[-1].y + 0.004, zip_pts[-1].z - 0.02), mat("brass", 0.4, 0.8), bevel=0.002)
    # leg outer seams (side casts at hip height clear of the arms) and ankle hems
    for s, m in ((1, "SR"), (-1, "SL")):
        seam = _line(body, [(0.012, 0.19 + i * 0.045, m) for i in range(9)], 0.004)
        if len(seam) > 2:
            _ktube(kit, seam, 0.005, mat("mustard", 0.9), seg=5)
    # shoulder straps, snapped to the suit surface
    for s in (-1, 1):
        x = s * 0.105
        strap = (_line(body, [(x, CW.T(0.63) + 0.05, "B"), (x, 0.98, "B")], 0.012)
                 + _line(body, [(x, 0.0, "T")], 0.012)
                 + _line(body, [(x, 1.02, "F"), (x, 0.90, "F"), (x, CW.T(0.63) + 0.03, "F")], 0.012))
        if len(strap) > 3:
            _ktube(kit, strap, 0.014, navy, seg=5)
    # ID patch on the wearer's left upper arm, dosimeter on the chest
    loc, nrm = _cast(body, (3, 0.0, zs - 0.10), (-1, 0, 0))
    if loc is not None:
        _kbox(kit, (0.012, 0.075, 0.075), (loc.x + 0.005, loc.y, loc.z), accent, bevel=0.003)
    loc, nrm = _cast(body, (0.11, 3, 0.95), (0, -1, 0))
    if loc is not None:
        _kbox(kit, (0.075, 0.03, 0.10), (loc.x, loc.y + 0.012, loc.z), dark, bevel=0.006)
        _kbox(kit, (0.05, 0.008, 0.035), (loc.x, loc.y + 0.03, loc.z + 0.018), mat("olive", 0.4, 0.0, 1.5), bevel=0.002)
    # pack, tank, hose, rescue handle on the back
    _kbox(kit, (0.30, 0.13, 0.36), (0, -0.265, 0.90), navy, bevel=0.03, seg=3)
    _kbox(kit, (0.20, 0.03, 0.14), (0, -0.345, 0.86), dark, bevel=0.01)
    _kcyl(kit, 0.055, 0.26, (0.20, -0.27, 0.86), white, seg=14)
    _ksph(kit, 0.055, (0.20, -0.27, 0.99), white, seg=14, ring=6)
    _kcyl(kit, 0.02, 0.04, (0.20, -0.27, 1.03), mat("brass", 0.4, 0.8), seg=8)
    _ktube(kit, [(0.20, -0.27, 1.05), (0.17, -0.22, 1.10), (0.11, -0.16, 1.12), (0.10, -0.10, 1.10)], 0.011, trim, seg=5)
    _ktube(kit, [(-0.08 + 0.16 * i / 12, -0.235 - 0.02 * math.sin(math.pi * i / 12), 1.09 + 0.09 * math.sin(math.pi * i / 12))
              for i in range(13)], 0.011, accent, seg=5)
    _details(kit, body, zs, fabric, trim, accent, boot_m, dark, navy)
    o = kit.build("SUIT_KIT", floor_normalize=False)
    coll.objects.link(o)
    o.parent = root
    o["cs_covers"] = []
    o["cs_outfit"] = "hazmat"
    pieces.append(o)

    pieces += _hood(root, pivot, coll, fabric, _glass(c["visor"]), trim)
    pieces.append(_hood_details(pivot, coll, trim, accent, dark))
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
