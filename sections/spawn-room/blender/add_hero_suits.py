#!/usr/bin/env python3
"""
Spawn Room hero suits (spawnroom.md sections 8.3-8.4).

Run headlessly (Blender 5.2):
    blender -b <input.blend> -P add_hero_suits.py -- <output.blend>

Replaces the personal-belongings dressing in the four PPE lockers (PPE_01..PPE_04, one per player)
with one hanging hazmat suit each, a wall-mounted helmet cradle with helmet, and per-player identity
colour. Removed: jacket, wooden hangers, mid shelf and what sat on it, floor work boots.
Everything is built in each locker's local frame, so the two rotated lockers mirror correctly.

Support registration (validate_contacts.py): suit hook rests on the hanger rail, cradle bolts to the
locker side panel, helmet rests on the cradle. Contact points are raycast onto the real geometry.
Re-running removes previous PPE_0n_suit / PPE_0n_helmet objects first.
"""
import math
import sys

import bpy
import bmesh
from mathutils import Matrix, Vector

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else None
ZO = 0.01                      # world z of each locker origin
CX = 0.15                      # suit centre line (local x); leaves the left side free for the helmet cradle
SEG = 22
ID_COLOURS = {1: (0.03, 0.20, 0.55, 1), 2: (0.05, 0.42, 0.12, 1), 3: (0.55, 0.06, 0.28, 1), 4: (0.78, 0.76, 0.68, 1)}
M = bpy.data.materials
scene = bpy.context.scene


def Z(zw):
    return zw - ZO


def make_mat(name, rgba, rough, bump=0.0, metal=0.0, coat=0.0):
    if name in M:
        return M[name]
    m = M.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"][0]
    p.inputs["Base Color"].default_value = rgba
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if coat:
        p.inputs["Coat Weight"].default_value = coat
    if bump:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 900.0
        nz.inputs["Detail"].default_value = 6.0
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = bump
        bp.inputs["Distance"].default_value = 0.002
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


make_mat("SUIT_fabric", (0.50, 0.31, 0.04, 1), 0.92, bump=0.35)
make_mat("SUIT_dark", (0.03, 0.035, 0.035, 1), 0.72)
make_mat("SUIT_visor", (0.015, 0.03, 0.04, 1), 0.06, coat=0.6)
for k, c in ID_COLOURS.items():
    make_mat("SUIT_id_%d" % k, c, 0.8)
STEEL, YELLOW, INK = "steel", "yellow", "ink"


# ---------------------------------------------------------------- geometry helpers
class Bucket:
    def __init__(self):
        self.bms = {}

    def bm(self, mat):
        if mat not in self.bms:
            self.bms[mat] = bmesh.new()
        return self.bms[mat]


def loft(bk, mat, rings, seg=SEG, cap=True):
    """rings: [(cx, cy, z_world, rx, ry)] bottom to top. Elliptical cross sections."""
    bm = bk.bm(mat)
    vr = []
    for (cx, cy, zw, rx, ry) in rings:
        vr.append([bm.verts.new(Vector((cx + rx * math.cos(2 * math.pi * i / seg),
                                        cy + ry * math.sin(2 * math.pi * i / seg), Z(zw)))) for i in range(seg)])
    for a, b in zip(vr, vr[1:]):
        for i in range(seg):
            j = (i + 1) % seg
            bm.faces.new((a[i], a[j], b[j], b[i]))
    if cap:
        bm.faces.new(list(reversed(vr[0])))
        bm.faces.new(vr[-1])


def ellipsoid(bk, mat, c, r, seg=18, rings=10, mtx=None, keep=None):
    bm = bk.bm(mat)
    ret = bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    for v in ret["verts"]:
        v.co = Vector((v.co.x * r[0], v.co.y * r[1], v.co.z * r[2]))
        if mtx is not None:
            v.co = mtx @ v.co
        v.co = v.co + Vector((c[0], c[1], Z(c[2])))
    return ret["verts"]


def box(bk, mat, c, s, bevel=0.0, yaw=0.0):
    bm = bk.bm(mat)
    ret = bmesh.ops.create_cube(bm, size=1.0)
    R = Matrix.Rotation(yaw, 3, "Z")
    for v in ret["verts"]:
        v.co = R @ Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2])) + Vector((c[0], c[1], Z(c[2])))
    if bevel:
        edges = list({e for v in ret["verts"] for e in v.link_edges})
        bmesh.ops.bevel(bm, geom=edges, offset=bevel, segments=2, affect="EDGES")


def cyl(bk, mat, c, r, h, axis="Z", seg=20):
    bm = bk.bm(mat)
    ret = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=h)
    for v in ret["verts"]:
        x, y, z = v.co
        if axis == "X":
            x, y, z = z, y, x
        elif axis == "Y":
            x, y, z = x, z, y
        v.co = Vector((x + c[0], y + c[1], z + Z(c[2])))


def finish(bk, root, name, mats_order=None):
    """One mesh object per material, parented to root, smooth shaded."""
    out = []
    for mat, bm in bk.bms.items():
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        me = bpy.data.meshes.new("%s_%s" % (name, mat))
        bm.to_mesh(me)
        bm.free()
        for p in me.polygons:
            p.use_smooth = True
        me.materials.append(M[mat])
        o = bpy.data.objects.new("%s_%s" % (name, mat.replace("SUIT_", "").lower()), me)
        o.parent = root
        for c in MESH_COLS:
            c.objects.link(o)
        out.append(o)
    return out


# ---------------------------------------------------------------- suit
def build_suit(bk, n, k):
    """k: station number 1..4. Faces local -Y (the open front of the locker)."""
    idm = "SUIT_id_%d" % k
    F, D = "SUIT_fabric", "SUIT_dark"
    s = 1.0 + 0.012 * (k - 2)                       # tiny human difference in build
    ph = k * 1.7
    fold = lambda i, a=0.05: 1.0 + a * math.sin(i * 2.3 + ph)
    # torso (crotch to shoulder yoke) with broad folds at the waist
    tor = [(CX, 0.0, 1.24, .17, .105), (CX, 0.0, 1.30, .19, .115), (CX, 0.0, 1.40, .20, .122),
           (CX, 0.0, 1.50, .185, .115), (CX, 0.0, 1.58, .19, .118), (CX, 0.0, 1.68, .225, .135),
           (CX, 0.0, 1.78, .225, .128), (CX, 0.0, 1.83, .185, .108), (CX, 0.0, 1.862, .13, .09), (CX, 0.0, 1.885, .098, .082)]
    tor = [(a, b, c, rx * s * fold(i), ry * fold(i + 1)) for i, (a, b, c, rx, ry) in enumerate(tor)]
    loft(bk, F, tor, seg=26)
    # collar seal ring + folded hood bundle draped behind the neck
    loft(bk, D, [(CX, 0.0, 1.865, .098, .085), (CX, 0.0, 1.915, .10, .088)], seg=24)
    ellipsoid(bk, F, (CX, 0.04, 1.915), (.125, .105, .05), seg=22, rings=12)
    ellipsoid(bk, F, (CX, 0.115, 1.76), (.13, .055, .115), seg=18, rings=10)
    # waist belt, seal flap on the chest, dosimeter/status module, id patch
    loft(bk, D, [(CX, 0.0, 1.455, .206 * s, .126), (CX, 0.0, 1.495, .206 * s, .126)], seg=26, cap=False)
    box(bk, D, (CX + 0.02, -0.134, 1.66), (.16, .016, .030), bevel=.004, yaw=0.0)           # closure flap
    box(bk, D, (CX - 0.10, -0.137, 1.60), (.075, .02, .095), bevel=.006)                  # dosimeter housing
    box(bk, "ink", (CX - 0.10, -0.1475, 1.615), (.050, .002, .035), bevel=0.0)            # screen
    box(bk, YELLOW, (CX - 0.10, -0.1475, 1.57), (.050, .002, .012), bevel=0.0)            # status stripe
    box(bk, idm, (CX + 0.17, -0.098, 1.75), (.075, .016, .075), bevel=.008)               # shoulder id patch
    # arms (shoulder to wrist), folds at elbow, dark cuffs, mitten gloves
    for sx in (-1, 1):
        arm = [(CX + sx * .225, 0.0, 1.83, .078, .078), (CX + sx * .235, -0.01, 1.72, .072, .070),
               (CX + sx * .245, -0.035, 1.60, .067 * 1.06, .066 * 1.06), (CX + sx * .245, -0.045, 1.55, .066, .066),
               (CX + sx * .245, -0.04, 1.44, .060, .060), (CX + sx * .245, -0.03, 1.33, .050, .050)]
        arm = [(a, b, c, rx * fold(i + sx), ry * fold(i + 2 * sx)) for i, (a, b, c, rx, ry) in enumerate(arm)]
        loft(bk, F, arm, seg=18)
        ellipsoid(bk, F, (CX + sx * .225, 0.0, 1.83), (.08, .08, .06), seg=16, rings=8)                   # rounded shoulder
        loft(bk, D, [(CX + sx * .245, -0.03, 1.335, .058, .058), (CX + sx * .245, -0.03, 1.29, .058, .058)], seg=18)
        ellipsoid(bk, D, (CX + sx * .245, -0.03, 1.205), (.046, .030, .090), seg=14, rings=9)    # glove
        ellipsoid(bk, D, (CX + sx * .245 - sx * .042, -0.052, 1.245), (.018, .020, .045), seg=10, rings=6,
                  mtx=Matrix.Rotation(sx * 0.35, 3, "Y"))                                       # thumb
    # legs with knee folds + pads, ankle cuffs, hanging boots (heel up off the floor)
    for sx in (-1, 1):
        leg = [(CX + sx * .085, 0.0, 1.27, .105, .105), (CX + sx * .095, -0.01, 1.15, .098, .098),
               (CX + sx * .100, -0.02, 1.00, .090, .092), (CX + sx * .102, -0.03, 0.88, .086 * 1.06, .088 * 1.06),
               (CX + sx * .102, -0.03, 0.80, .082, .084), (CX + sx * .102, -0.02, 0.66, .074, .074),
               (CX + sx * .102, -0.02, 0.56, .068, .068)]
        leg = [(a, b, c, rx * fold(i + 3 * sx), ry * fold(i + sx)) for i, (a, b, c, rx, ry) in enumerate(leg)]
        loft(bk, F, leg, seg=18)
        box(bk, D, (CX + sx * .102, -0.136, 0.86), (.10, .028, .12), bevel=.012)              # knee pad
        loft(bk, D, [(CX + sx * .102, -0.02, 0.575, .076, .076), (CX + sx * .102, -0.02, 0.545, .076, .076)], seg=18)
        box(bk, D, (CX + sx * .102, -0.075, 0.49), (.115, .27, .13), bevel=.03)                # boot
        box(bk, STEEL, (CX + sx * .102, -0.075, 0.418), (.12, .275, .024), bevel=.008)         # sole plate
    # integrated pack on the back: body, filter canister, hose to the collar, rescue handle
    box(bk, D, (CX, 0.165, 1.50), (.30, .11, .40), bevel=.02)
    cyl(bk, STEEL, (CX - 0.075, 0.165, 1.36), .045, .12, axis="Z")
    cyl(bk, STEEL, (CX + 0.075, 0.165, 1.36), .045, .12, axis="Z")
    box(bk, idm, (CX, 0.223, 1.62), (.20, .008, .03), bevel=.002)                             # pack id stripe
    loft(bk, D, [(CX + .05, 0.14, 1.70, .012, .012), (CX + .06, 0.11, 1.82, .012, .012), (CX + .035, 0.07, 1.90, .012, .012)],
         seg=8, cap=True)
    box(bk, YELLOW, (CX, 0.16, 1.86), (.12, .012, .03), bevel=.005)                           # rescue handle strap
    # hanger: bar under the yoke, two short straps up to a hook over the rail
    box(bk, STEEL, (CX, 0.15, 1.935), (.34, .014, .014), bevel=.003)
    for sx in (-1, 1):
        box(bk, STEEL, (CX + sx * .11, 0.075, 1.895), (.014, .14, .014), bevel=.002)          # strap forward to the yoke
    return CX


# ---------------------------------------------------------------- helmet
def build_helmet(bk, n, k, base_z):
    """Built around its own origin; returns nothing (caller places and rotates). base_z = ring bottom (world z)."""
    D = "SUIT_dark"
    yaw = (-1) ** k * (0.10 + 0.05 * k)
    R = Matrix.Rotation(yaw, 3, "Z")
    c = (0.0, 0.0)
    cyl(bk, D, (0, 0, base_z + 0.02), .098, .04, axis="Z", seg=24)
    z0 = base_z + 0.17
    verts = ellipsoid(bk, "SUIT_fabric", (0, 0, z0), (.135, .150, .150), seg=36, rings=20)
    # visor: front cap of a slightly larger shell, solidified for thickness
    bm = bk.bm("SUIT_visor")
    ret = bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=28, radius=1.0)
    for v in ret["verts"]:
        v.co = Vector((v.co.x * .141, v.co.y * .156, v.co.z * .156 + Z(z0)))
    keep, drop = [], []
    for f in ret["verts"][0].link_faces[:0]:
        pass
    faces = {f for v in ret["verts"] for f in v.link_faces}
    for f in faces:
        ctr = f.calc_center_median()
        (keep if (ctr.y < -0.04 and (ctr.x / 0.105) ** 2 + ((ctr.z - Z(z0) - 0.01) / 0.075) ** 2 < 1.0) else drop).append(f)
    bmesh.ops.delete(bm, geom=drop, context="FACES")
    bmesh.ops.solidify(bm, geom=[f for f in bm.faces if f in set(keep) and f.is_valid], thickness=-0.012)
    # hard-shell stripe in player colour over the crown
    cyl(bk, "SUIT_id_%d" % k, (0, 0, base_z + 0.047), .1, .012, axis="Z", seg=24)
    # apply yaw about the helmet axis to everything built in this bucket
    for m_, b_ in bk.bms.items():
        for v in b_.verts:
            v.co = R @ v.co
    return yaw


# ---------------------------------------------------------------- scene surgery
def kill(obj):
    for c in list(obj.children_recursive):
        bpy.data.objects.remove(c, do_unlink=True)
    bpy.data.objects.remove(obj, do_unlink=True)


def clear_old(n):
    names = [o.name for o in bpy.data.objects if o.name.startswith(("PPE_0%d_suit" % n, "PPE_0%d_helmet" % n))]
    for pat in ("BELONG_0%d_jacket" % n, "BELONG_0%d_hanger_" % n, "BELONG_0%d_fold_" % n, "BELONG_0%d_bag" % n,
                "BELONG_0%d_mid_shelf" % n, "PPE_0%d_work_boot" % n):
        names += [o.name for o in bpy.data.objects
                  if o.name.startswith(pat) and o.parent and o.parent.name == "PPE_0%d" % n]
    for nm in names:
        o = bpy.data.objects.get(nm)
        if o is not None:
            kill(o)


def cast(parent, local_origin, local_dir, dist=1.0):
    mw = parent.matrix_world
    dg = bpy.context.evaluated_depsgraph_get()
    o = mw @ Vector(local_origin)
    d = (mw.to_3x3() @ Vector(local_dir)).normalized()
    ok, loc, nrm, _i, obj, _m = scene.ray_cast(dg, o, d, distance=dist)
    return (mw.inverted() @ loc, obj) if ok else (None, None)


def anchor(root, name, local, parent_obj):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.01
    e.parent = root
    e.matrix_parent_inverse = Matrix.Identity(4)
    e.location = local                         # roots have identity local transform, so this is the locker frame
    e["cs_support_anchor"] = True
    for c in ROOT_COLS:
        pass
    c0 = bpy.data.collections.get("MODULE_spawn-room")
    (c0 or scene.collection).objects.link(e)
    return e


def register_root(root, target, direction, n):
    root["cs_support_target"] = target
    root["cs_support_direction"] = direction
    for cname in ("MODULE_spawn-room", "PPE_STATIONS", "CS_SUPPORT_REQUIRED", "CS_FLOOR_DRESSING"):
        c = bpy.data.collections.get(cname)
        if c and root.name not in c.objects:
            c.objects.link(root)


MESH_COLS = [c for c in (bpy.data.collections.get("MODULE_spawn-room"), bpy.data.collections.get("PPE_STATIONS")) if c]
ROOT_COLS = MESH_COLS

report = {}
for n in (1, 2, 3, 4):
    P = bpy.data.objects["PPE_0%d" % n]
    clear_old(n)
    bpy.context.view_layer.update()
    mw = P.matrix_world

    # ---- suit
    root = bpy.data.objects.new("PPE_0%d_suit" % n, None)
    root.parent = P
    root.matrix_parent_inverse = Matrix.Identity(4)
    root.empty_display_size = 0.05
    bk = Bucket()
    build_suit(bk, n, n)
    finish(bk, root, "PPE_0%d_suit" % n)
    # hook over the rail: back post, bridge, front lip; bridge rests on the measured rail top
    hit, ro = cast(P, (CX, 0.15, 2.03 - ZO), (0, 0, -1), 0.5)
    rail_top_local = hit.z
    bk2 = Bucket()
    zt = rail_top_local + ZO + 0.0004                     # world z of the rail top
    box(bk2, STEEL, (CX, 0.172, 1.975), (.03, .012, .09), bevel=.002)
    box(bk2, STEEL, (CX, 0.150, zt + 0.007), (.03, .058, .014), bevel=.002)
    box(bk2, STEEL, (CX, 0.126, zt - 0.012), (.03, .012, .04), bevel=.002)
    finish(bk2, root, "PPE_0%d_suit_hook" % n)
    for ax in (CX - 0.045, CX + 0.045):
        pass
    anchors = []
    for i, ax in enumerate((CX - 0.075, CX + 0.075)):
        h2, _ = cast(P, (ax, 0.15, 2.03 - ZO), (0, 0, -1), 0.5)
        anchors.append(anchor(root, "PPE_0%d_suit_contact_%02d" % (n, i), Vector((ax, 0.15, h2.z + 0.0005 + 0.0004 + 0.0)), P))
    register_root(root, ro.name, "WORLD_-Z", n)

    # ---- helmet cradle (bolted to the left side panel) and helmet
    wall_hit, wall_obj = cast(P, (-0.30, 0.0, 1.0 - ZO - 0.05), (-1, 0, 0), 0.5)
    wx = wall_hit.x
    cradle_top = 1.02
    cr = bpy.data.objects.new("PPE_0%d_helmet_cradle" % n, None)
    cr.parent = P
    cr.matrix_parent_inverse = Matrix.Identity(4)
    bk3 = Bucket()
    box(bk3, STEEL, (wx + 0.14, 0.0, cradle_top - 0.01), (.28, .30, .02), bevel=.004)
    box(bk3, STEEL, (wx + 0.12, -0.12, cradle_top - 0.07), (.24, .012, .10), bevel=.003)
    box(bk3, STEEL, (wx + 0.12, 0.12, cradle_top - 0.07), (.24, .012, .10), bevel=.003)
    box(bk3, D := "SUIT_dark", (wx + 0.14, 0.0, cradle_top + 0.003), (.20, .22, .006), bevel=.002)   # rubber pad
    finish(bk3, cr, "PPE_0%d_helmet_cradle" % n)
    for i, ay in enumerate((-0.10, 0.10)):
        anchor(cr, "PPE_0%d_helmet_cradle_contact_%02d" % (n, i), Vector((wx + 0.0003, ay, Z(cradle_top - 0.07))), P)
    register_root(cr, wall_obj.name, "LOCAL_-X", n)

    helm = bpy.data.objects.new("PPE_0%d_helmet" % n, None)
    helm.parent = P
    helm.matrix_parent_inverse = Matrix.Identity(4)
    bk4 = Bucket()
    pad_top = cradle_top + 0.006
    # build the helmet around its own centre at the cradle, ring bottom resting on the pad
    hx = wx + 0.14
    yaw = build_helmet(bk4, n, n, pad_top)
    for b_ in bk4.bms.values():
        for v in b_.verts:
            v.co.x += hx
    finish(bk4, helm, "PPE_0%d_helmet" % n)
    anchor(helm, "PPE_0%d_helmet_contact_00" % n, Vector((hx - 0.05, 0.0, Z(pad_top) + 0.0003)), P)
    anchor(helm, "PPE_0%d_helmet_contact_01" % n, Vector((hx + 0.05, 0.0, Z(pad_top) + 0.0003)), P)
    register_root(helm, "PPE_0%d_helmet_cradle_%s" % (n, "dark"), "WORLD_-Z", n)
    P["contents"] = "One hanging hazmat suit (hook on the rail), helmet on a wall cradle, personal items on the upper shelf"
    report[n] = {"rail": ro.name, "side_wall": wall_obj.name, "wall_x": round(wx, 3), "rail_top_local": round(rail_top_local, 4)}

print("SUIT_REPORT", report)
if OUT:
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("saved", OUT)
