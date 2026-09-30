#!/usr/bin/env python3
"""
Rig and animations for the crew worker (Blender 5.2 / bpy). Unity Humanoid compatible.

Skeleton: Root > Hips > Spine > Chest > Neck > Head, Chest > Left/RightShoulder > UpperArm > LowerArm > Hand, Hips >
Left/RightUpperLeg > LowerLeg > Foot, plus non-humanoid extras: Belly (jiggle), Pack (backpack lag) and Tool (a free
bone under Root that the hand tools are skinned to). Bone names follow Unity's humanoid naming so the Avatar auto-maps.
Feet have no toes, so there is no Toes bone. Rest pose is an A-pose.

Skinning: weights come from distance to the skeleton (a smooth falloff around each bone), a function of position only,
so coincident vertices on the region seams and on the suit get identical weights and never open. Each leg only follows
its own leg bones (no cross-leg contamination below the crotch); arms only reach into the flank near the shoulder.
Head, hood, visor and face decals are rigid to Head; long suit parts (belt, straps, boots, tank) are rigid to one bone.

Animations (all loop, in place):
    RUN           cartoon run, hands waving above the head (erratic but ordered: mixed harmonics, arms out of phase)
    HOLD_SHOVEL   two-handed shovel hold with breathing
    HOLD_PICKAXE  pickaxe resting on the shoulder, right hand on the handle
"""

import math

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector

import character_regions as CR
import character_tools as CT
import character_worker as CW

ZS = CW.T(0.94)                       # shoulder height

_CENTRE = [
    ("Root", None, (0, 0.0, 0.0), (0, 0.0, 0.16)),
    ("Hips", "Root", (0, 0.0, 0.70), (0, 0.0, 0.79)),
    ("Spine", "Hips", (0, 0.0, 0.79), (0, 0.0, 0.92)),
    ("Chest", "Spine", (0, 0.0, 0.92), (0, 0.0, 1.06)),
    ("Neck", "Chest", (0, 0.0, 1.06), (0, 0.0, 1.117)),
    ("Head", "Neck", (0, 0.0, 1.117), (0, 0.0, 1.62)),
    ("Belly", "Spine", (0, 0.05, 0.80), (0, 0.22, 0.80)),
    ("Pack", "Chest", (0, -0.26, 0.90), (0, -0.26, 1.15)),
    ("Tool", "Root", (0, 0.0, 0.0), (0, 0.0, 0.2)),
]
_SIDE = [
    ("Shoulder", "Chest", (0.05, 0.0, 1.03), (0.14, 0.0, ZS - 0.01)),
    ("UpperArm", "Shoulder", (0.14, 0.0, ZS - 0.01), (0.305, 0.03, ZS - 0.20)),
    ("LowerArm", "UpperArm", (0.305, 0.03, ZS - 0.20), (0.345, 0.065, ZS - 0.385)),
    ("Hand", "LowerArm", (0.345, 0.065, ZS - 0.385), (0.355, 0.075, ZS - 0.52)),
    ("UpperLeg", "Hips", (0.075, 0.0, 0.72), (0.106, 0.008, 0.44)),
    ("LowerLeg", "UpperLeg", (0.106, 0.008, 0.44), (0.110, 0.014, 0.13)),
    ("Foot", "LowerLeg", (0.110, 0.014, 0.13), (0.110, 0.24, 0.045)),
]
DEFORM = ["Hips", "Spine", "Chest", "Neck", "Head", "Belly", "Pack", "Tool"] + [
    s + n for s in ("Left", "Right") for n in ("Shoulder", "UpperArm", "LowerArm", "Hand", "UpperLeg", "LowerLeg", "Foot")]
_PARENTS_WITH_SIDE = ("Shoulder", "UpperArm", "LowerArm", "UpperLeg", "LowerLeg")


def _bone_table():
    rows = list(_CENTRE)
    for side, sx in (("Left", 1), ("Right", -1)):
        for name, parent, h, t in _SIDE:
            par = side + parent if parent in _PARENTS_WITH_SIDE else parent
            rows.append((side + name, par, (h[0] * sx, h[1], h[2]), (t[0] * sx, t[1], t[2])))
    return rows


SEGMENTS = {n: (Vector(h), Vector(t)) for n, _, h, t in _bone_table()}


def build_rig(root, coll=None, name="WORKER_RIG"):
    coll = coll or bpy.context.scene.collection
    data = bpy.data.armatures.new(name)
    arm = bpy.data.objects.new(name, data)
    coll.objects.link(arm)
    view = bpy.context.view_layer
    for o in view.objects:
        o.select_set(False)
    view.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    made = {}
    for bname, parent, head, tail in _bone_table():
        eb = data.edit_bones.new(bname)
        eb.head, eb.tail = Vector(head), Vector(tail)
        eb.roll = 0.0
        if parent:
            eb.parent = made[parent]
            eb.use_connect = False
        made[bname] = eb
        eb.use_deform = bname != "Root"
    bpy.ops.object.mode_set(mode="OBJECT")
    arm.parent = root
    arm.show_in_front = True
    data.display_type = "OCTAHEDRAL"
    arm["cs_rig"] = "unity-humanoid"
    return arm


# ------------------------------------------------------------------------------------------------------ skinning

_LEG_R = {"UpperLeg": 0.11, "LowerLeg": 0.09, "Foot": 0.09}
_SIGMA = 0.045


def _ss(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def _seg_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length


def leg_weights(p):
    """Same-side leg weights from distance to the leg bones: smooth blend at the knee and ankle, and a leg never
    follows the other leg's bones (that cross-contamination made the pants morph)."""
    side = "Left" if p.x > 0 else "Right"
    raw = {}
    for base in ("UpperLeg", "LowerLeg", "Foot"):
        h, t = SEGMENTS[side + base]
        d = max(0.0, _seg_dist(p, h, t) - _LEG_R[base])
        raw[side + base] = math.exp(-(d / _SIGMA) ** 2)
    h, t = SEGMENTS["Hips"]
    raw["Hips"] = 0.6 * math.exp(-(max(0.0, _seg_dist(p, h, t) - 0.17) / _SIGMA) ** 2)
    tot = sum(raw.values())
    if tot < 1e-6:
        return {side + "UpperLeg": 1.0}
    return {n: w / tot for n, w in raw.items() if w / tot > 0.01}


_ARM_R = {"UpperArm": 0.08, "LowerArm": 0.07, "Hand": 0.08}


def _leg_gate(p):
    """0 where the point belongs to the arm (hanging beside the hip), 1 where it belongs to a leg, by which limb's surface
    is closer. A fixed |x| cut let the sleeve pick up leg weights."""
    side = "Left" if p.x > 0 else "Right"
    dl = min(_seg_dist(p, *SEGMENTS[side + b]) - _LEG_R[b] for b in ("UpperLeg", "LowerLeg"))
    da = min(_seg_dist(p, *SEGMENTS[side + b]) - _ARM_R[b] for b in ("UpperArm", "LowerArm", "Hand"))
    return _ss(0.0, 0.05, da - dl)


def _weld_source(root):
    """All skin regions joined and welded into one closed mesh, for heat weighting."""
    bm = bmesh.new()
    for o in root.children:
        if o.get("cs_region"):
            bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    me = bpy.data.meshes.new("CS_rig_src")
    bm.to_mesh(me)
    bm.free()
    src = bpy.data.objects.new("CS_rig_src", me)
    bpy.context.scene.collection.objects.link(src)
    return src


def _heat_weights(src, arm):
    view = bpy.context.view_layer
    for o in view.objects:
        o.select_set(False)
    src.select_set(True)
    arm.select_set(True)
    view.objects.active = arm
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    names = {i: g.name for i, g in enumerate(src.vertex_groups)}
    return [{names[g.group]: g.weight for g in v.groups if g.weight > 1e-4} for v in src.data.vertices]


def _nearest_bone(p, arm):
    best, bd = None, 1e9
    for b in arm.data.bones:
        if not b.use_deform or b.name == "Tool":
            continue
        d = _seg_dist(p, b.head_local, b.tail_local)
        if d < bd:
            best, bd = b.name, d
    return {best: 1.0}


def _smooth_weights(src, weights, iterations=6, keep=4):
    """Laplacian-smooth the per-vertex bone weights over the mesh graph so joints blend softly (no pinching)."""
    import numpy as np
    me = src.data
    n = len(me.vertices)
    names = sorted({b for w in weights for b in w})
    idx = {b: i for i, b in enumerate(names)}
    W = np.zeros((n, len(names)))
    for i, w in enumerate(weights):
        for b, x in w.items():
            W[i, idx[b]] = x
    nbr = [[] for _ in range(n)]
    for e in me.edges:
        a, b = e.vertices
        nbr[a].append(b)
        nbr[b].append(a)
    for _ in range(iterations):
        new = W.copy()
        for i in range(n):
            if nbr[i]:
                new[i] = 0.5 * W[i] + 0.5 * W[nbr[i]].mean(axis=0)
        W = new
    out = []
    for i in range(n):
        top = np.argsort(W[i])[::-1][:keep]
        w = {names[j]: float(W[i, j]) for j in top if W[i, j] > 1e-3}
        t = sum(w.values()) or 1.0
        out.append({b: x / t for b, x in w.items()})
    return out


def _make_weight_fn(root, arm):
    """Position-only weight function: heat weights (nearest welded vertex, smoothed) for torso and arms, blended into
    same-side distance weights below the hips so the legs never mix."""
    from mathutils.kdtree import KDTree
    src = _weld_source(root)
    weights = _heat_weights(src, arm)
    for i, v in enumerate(src.data.vertices):
        if not weights[i]:
            weights[i] = _nearest_bone(v.co, arm)
    weights = _smooth_weights(src, weights, iterations=int(__import__("os").environ.get("SMOOTH", "6")))
    kd = KDTree(len(src.data.vertices))
    for i, v in enumerate(src.data.vertices):
        kd.insert(v.co, i)
    kd.balance()
    bpy.data.objects.remove(src, do_unlink=True)

    def heat_at(p):
        acc, tot = {}, 0.0
        for co, idx, d in kd.find_n(p, 3):
            k = 1.0 / (d + 1e-4) ** 2
            tot += k
            for n, w in weights[idx].items():
                acc[n] = acc.get(n, 0.0) + w * k
        acc = {n: w / tot for n, w in acc.items()}
        z, ax = p.z, abs(p.x)
        leg_mask = _ss(0.88, 0.70, z) * (_leg_gate(p) if z < 0.88 else 1.0)
        arm_mask = max(_ss(0.12, 0.26, ax), _ss(0.95, 1.05, z))
        for n in list(acc):
            if "Leg" in n or n.endswith("Foot"):
                acc[n] *= leg_mask
            elif n.endswith(("UpperArm", "LowerArm", "Hand", "Shoulder")):
                acc[n] *= arm_mask
        t = sum(acc.values())
        return {n: w / t for n, w in acc.items()} if t > 1e-6 else {"Spine": 1.0}

    def _arm_share(w, side):
        return sum(x for n, x in w.items() if n.startswith(side) and n[len(side):] in ("UpperArm", "LowerArm", "Hand"))

    def blur_arm(p, w):
        """Spread the arm/torso hand-over across ~0.12 m so a raised arm pulls a wide fold of fabric instead of a thin
        stretched web where the sleeve meets the flank."""
        if abs(p.x) < 0.10 or p.z > 1.02 or p.z < 0.50:
            return w
        side = "Left" if p.x > 0 else "Right"
        s0 = _arm_share(w, side)
        acc = [s0]
        for dx, dy, dz in ((0.07, 0, 0), (-0.07, 0, 0), (0, 0.06, 0), (0, -0.06, 0), (0, 0, 0.07), (0, 0, -0.07),
                           (0.05, 0, 0.05), (-0.05, 0, -0.05)):
            acc.append(_arm_share(heat_at(p + Vector((dx, dy, dz))), side))
        s1 = sum(acc) / len(acc)
        if s1 < 1e-4 and s0 < 1e-4:
            return w
        out = {}
        for n, x in w.items():
            if n.startswith(side) and n[len(side):] in ("UpperArm", "LowerArm", "Hand"):
                out[n] = x * (s1 / s0) if s0 > 1e-6 else 0.0
            else:
                out[n] = x * ((1 - s1) / (1 - s0)) if s0 < 1 - 1e-6 else 0.0
        if s0 < 1e-6:                              # arm weight appears where there was none: give it to UpperArm/LowerArm
            out[side + "LowerArm"] = out.get(side + "LowerArm", 0.0) + s1 * 0.5
            out[side + "UpperArm"] = out.get(side + "UpperArm", 0.0) + s1 * 0.5
        t = sum(out.values())
        return {n: x / t for n, x in out.items() if x / t > 1e-3}

    def weight_at(p):
        a = _ss(0.80, 0.66, p.z)                 # 0 above the hips, 1 in the legs
        if 0.0 < a:
            a *= _leg_gate(p)                    # ...but never on a sleeve hanging beside the hip
        if a <= 0.0:
            acc = heat_at(p)
        elif a >= 1.0:
            acc = leg_weights(p)
        else:
            acc = {}
            for n, w in heat_at(p).items():
                acc[n] = acc.get(n, 0.0) + w * (1 - a)
            for n, w in leg_weights(p).items():
                acc[n] = acc.get(n, 0.0) + w * a
        acc = blur_arm(p, acc)
        # soft belly: the front of the lower torso follows the Belly bone
        ax = abs(p.x)
        if p.y > 0.03 and ax < 0.26 and p.z > 0.66:
            lat = _ss(0.26, 0.10, ax)
            k = max(0.0, 1.0 - math.hypot(p.y - 0.22, (p.z - 0.80) * 1.2) / 0.22) * 0.55 * lat
            if k > 0:
                acc = {n: w * (1 - k) for n, w in acc.items()}
                acc["Belly"] = acc.get("Belly", 0.0) + k
        return acc

    return weight_at


def _islands(me):
    parent = list(range(len(me.vertices)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for e in me.edges:
        ra, rb = find(e.vertices[0]), find(e.vertices[1])
        if ra != rb:
            parent[ra] = rb
    groups = {}
    for i in range(len(parent)):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


_ARM_BONES = ("UpperArm", "LowerArm", "Hand", "Shoulder")


def _limb_key(w):
    """Which limb a weight set belongs to: armL/armR, legL/legR or core."""
    sums = {"armL": 0.0, "armR": 0.0, "legL": 0.0, "legR": 0.0, "core": 0.0}
    for n, x in w.items():
        side = "L" if n.startswith("Left") else "R" if n.startswith("Right") else ""
        if side and n[len(("Left" if side == "L" else "Right")):] in _ARM_BONES:
            sums["arm" + side] += x
        elif side and ("Leg" in n or n.endswith("Foot")):
            sums["leg" + side] += x
        else:
            sums["core"] += x
    return max(sums, key=sums.get)


def _split_limbs(o, weight_at, mw, z_split=0.96):
    """The suit body is one fused mesh, so the sleeve is webbed to the hip and the legs to each other where they touch.
    A raised arm or a striding leg stretches those webs into dark slivers. Split the mesh along those creases (below
    `z_split`) and return {vertex: limb key} so each side can be weighted to its own limb only."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    fkey = {f.index: _limb_key(weight_at(mw @ f.calc_center_median())) for f in bm.faces}
    cut = []
    for e in bm.edges:
        if len(e.link_faces) != 2:
            continue
        k1, k2 = fkey[e.link_faces[0].index], fkey[e.link_faces[1].index]
        if k1 == k2 or (mw @ ((e.verts[0].co + e.verts[1].co) * 0.5)).z > z_split:
            continue
        if {k1[:3], k2[:3]} == {"cor", "leg"}:
            continue                               # hips to leg is a joint, not a web
        cut.append(e)
    bmesh.ops.split_edges(bm, edges=cut)
    bm.faces.ensure_lookup_table()
    vkey = {}
    for v in bm.verts:
        ks = [_limb_key(weight_at(mw @ f.calc_center_median())) for f in v.link_faces]
        vkey[v.index] = max(set(ks), key=ks.count) if ks else "core"
    bm.to_mesh(o.data)
    bm.free()
    o.data.update()
    return vkey


def _restrict(w, key, z, z_split=0.96):
    """Weights confined to the vertex's own limb below the armpit, fading back to the plain weights above it."""
    r = _ss(z_split + 0.06, z_split, z)
    if r <= 0.0 or key == "core" and not any(n.endswith(_ARM_BONES) for n in w):
        return w
    if key.startswith("arm"):
        side = "Left" if key.endswith("L") else "Right"
        keep = {n: x for n, x in w.items() if n.startswith(side) and n[len(side):] in _ARM_BONES}
    else:
        keep = {n: x for n, x in w.items() if not any(n.endswith(b) for b in _ARM_BONES)}
        if key.startswith("leg"):
            side = "Left" if key.endswith("L") else "Right"
            keep = {n: x for n, x in keep.items() if not (n.startswith(("Left", "Right")) and not n.startswith(side))}
    t = sum(keep.values())
    if t < 1e-6:
        return w
    out = {}
    for n, x in w.items():
        out[n] = (1 - r) * x
    for n, x in keep.items():
        out[n] = out.get(n, 0.0) + r * x / t
    return {n: x for n, x in out.items() if x > 1e-4}


def skin_worker(root, arm):
    weight_at = _make_weight_fn(root, arm)
    n_meshes = 0
    for o in [o for o in root.children_recursive if o.type == "MESH"]:
        head_rigid = o.parent is not None and o.parent.name.endswith("_HEAD_PIVOT")
        mw = o.matrix_world.copy()
        for n in DEFORM:
            o.vertex_groups.new(name=n)
        vg = o.vertex_groups
        rigid_bone = {}
        vkey = None
        if o.name == "SUIT_KIT":
            for isl in _islands(o.data):
                pts = [mw @ o.data.vertices[i].co for i in isl]
                ext = max(max(q[a] for q in pts) - min(q[a] for q in pts) for a in range(3))
                c = sum(pts, Vector()) / len(pts)
                behind = sum(1 for q in pts if q.y < -0.19 and 0.68 < q.z < 1.25 and abs(q.x) < 0.30) / len(pts)
                if behind > 0.5:
                    bone = "Pack"                # whole island, so a strap is never half rigid and half stretching
                elif abs(c.x) > 0.10 and 0.95 < c.z < 1.30:
                    continue                     # shoulder straps and piping fold with the fabric
                elif ext < 0.14 and not (0.86 < c.z < 1.12 and abs(c.x) > 0.06):
                    continue                     # small patches, pockets and buttons follow the fabric (except in the
                                                 # armpit band, where the fabric shears too hard: those stay rigid)
                else:
                    wc = {n: x for n, x in weight_at(c).items() if n != "Belly"}
                    bone = max(wc, key=wc.get)
                for i in isl:
                    rigid_bone[i] = bone
        for v in o.data.vertices:
            p = mw @ v.co
            if head_rigid:
                w = {"Head": 1.0}
            elif v.index in rigid_bone:
                w = {rigid_bone[v.index]: 1.0}
            else:
                w = weight_at(p)
                if vkey is not None:
                    w = _restrict(w, vkey[v.index], p.z)
            for n, x in w.items():
                vg[n].add([v.index], x, "REPLACE")
        o.parent = None
        o.matrix_world = mw
        o.parent = arm
        o.matrix_parent_inverse = arm.matrix_world.inverted()
        mod = o.modifiers.new("Armature", "ARMATURE")
        mod.object = arm
        n_meshes += 1
    for o in root.children_recursive:
        if o.type == "EMPTY" and o.name.endswith("_HEAD_PIVOT"):
            o.hide_viewport = True
    return n_meshes, 0


def add_tools(root, arm, coll=None):
    """Shovel and pickaxe as meshes rigidly skinned to the Tool bone. Hidden unless an animation shows them."""
    coll = coll or bpy.context.scene.collection
    out = {}
    for kind in ("SHOVEL", "PICKAXE"):
        o = CT.build_tool(kind, coll, "%s_TOOL_%s" % (root.name, kind))
        vg = o.vertex_groups.new(name="Tool")
        vg.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
        o.parent = arm
        o.matrix_parent_inverse = arm.matrix_world.inverted()
        mod = o.modifiers.new("Armature", "ARMATURE")
        mod.object = arm
        o.hide_render = True
        o.hide_viewport = True
        out[kind] = o
    return out


def show_tool(tools, kind):
    for k, o in tools.items():
        o.hide_render = k != kind
        o.hide_viewport = k != kind


# ------------------------------------------------------------------------------------------------------ animation core

_prevq = {}


def _rot(axis, deg):
    return Matrix.Rotation(math.radians(deg), 3, axis)


def _aim_bone(arm, bone, direction, up=True):
    """Rotation delta (armature space) that turns a bone's rest direction onto `direction`. Arms rest pointing down, so
    for raised arms (`up`) the base turn is a 180 degree flip about X (a fixed, unambiguous twist) and only the small
    remainder is solved; hanging arms solve directly from rest."""
    b = arm.data.bones[bone]
    rest = (b.tail_local - b.head_local).normalized()
    base = _rot("X", 180) if up else Matrix.Identity(3)
    rem = (base @ rest).rotation_difference(Vector(direction).normalized()).to_matrix()
    return rem @ base


def _rest3(arm, bone):
    return arm.data.bones[bone].matrix_local.to_3x3()


def _new_action(arm, name):
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data_create()
    arm.animation_data.action = act
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)
    _prevq.clear()
    return act


def _key(arm, frame, D, loc=None):
    """D: {bone: absolute 3x3 rotation delta in armature space}; parents are applied through their own D."""
    pose = arm.pose
    for name, Dm in D.items():
        pb = pose.bones[name]
        Rr = _rest3(arm, name)
        par = pb.parent
        Dp = D.get(par.name) if par is not None else None
        rel = (Dp.inverted() @ Dm) if Dp is not None else Dm
        q = (Rr.inverted() @ rel @ Rr).to_quaternion()
        pq = _prevq.get(name)
        if pq is not None and pq.dot(q) < 0:
            q.negate()
        _prevq[name] = q.copy()
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = q
        pb.keyframe_insert("rotation_quaternion", frame=frame)
    if loc:
        for name, t in loc.items():
            pb = pose.bones[name]
            pb.location = _rest3(arm, name).inverted() @ Vector(t)
            pb.keyframe_insert("location", frame=frame)


def _key_tool(arm, frame, M):
    """Place the Tool bone so its skinned mesh (authored at the origin) moves by the 4x4 armature-space matrix M."""
    pb = arm.pose.bones["Tool"]
    R = arm.data.bones["Tool"].matrix_local
    B = R.inverted() @ M @ R
    loc, quat, _ = B.decompose()
    pq = _prevq.get("Tool")
    if pq is not None and pq.dot(quat) < 0:
        quat.negate()
    _prevq["Tool"] = quat.copy()
    pb.rotation_mode = "QUATERNION"
    pb.location, pb.rotation_quaternion, pb.scale = loc, quat, (1, 1, 1)
    pb.keyframe_insert("location", frame=frame)
    pb.keyframe_insert("rotation_quaternion", frame=frame)
    pb.keyframe_insert("scale", frame=frame)


def _eval_bones(arm):
    dg = bpy.context.evaluated_depsgraph_get()
    return arm.evaluated_get(dg).pose.bones


def _sole_height(arm):
    ev = _eval_bones(arm)
    lows = []
    for side in ("Left", "Right"):
        pb = ev[side + "Foot"]
        m = pb.matrix
        head = m.translation
        tail = m @ Vector((0, pb.length, 0))
        lows.append(min(head.z - 0.13, tail.z - 0.045))
    return min(lows)


def _plant_feet(arm, frames, sways, hop_amp=0.03, hops_per_cycle=2):
    """Re-key the hips height so the lower foot touches the ground every frame, plus a hop that peaks between
    footfalls."""
    sc = bpy.context.scene
    lows = []
    for f in range(frames + 1):
        sc.frame_set(f)
        bpy.context.view_layer.update()
        lows.append(_sole_height(arm))
    for f in range(frames + 1):
        ph = (f % frames) / frames
        hop = hop_amp * (0.5 - 0.5 * math.cos(hops_per_cycle * 2 * math.pi * ph + math.pi))
        pb = arm.pose.bones["Hips"]
        pb.location = _rest3(arm, "Hips").inverted() @ Vector((sways[f], 0.0, -lows[f] + hop))
        pb.keyframe_insert("location", frame=f)


def _finish(arm, act, frames):
    arm.animation_data.action = act
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 0, frames - 1
    sc.render.fps = 24


# ------------------------------------------------------------------------------------------------------ two-bone IK

def _ik_arm(arm, side, S, T, pole):
    """Analytic two-bone IK in armature space. S: posed shoulder joint, T: target wrist point, pole: elbow direction.
    Returns absolute rotation deltas (upper, lower) taking each bone's rest direction to the solved direction."""
    ub, lb = arm.data.bones[side + "UpperArm"], arm.data.bones[side + "LowerArm"]
    ru, rl = ub.tail_local - ub.head_local, lb.tail_local - lb.head_local
    l1, l2 = ru.length, rl.length
    v = T - S
    d = min(max(v.length, 0.03), l1 + l2 - 1e-3)
    u = v.normalized()
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(l1 * l1 - a * a, 0.0))
    perp = pole - u * pole.dot(u)
    perp = perp.normalized() if perp.length > 1e-6 else Vector((0, 0, -1))
    E = S + u * a + perp * h
    W = S + u * d
    up_dir, lo_dir = (E - S).normalized(), (W - E).normalized()
    Du = ru.normalized().rotation_difference(up_dir).to_matrix()
    Dl = rl.normalized().rotation_difference(lo_dir).to_matrix()
    return Du, Dl


# ------------------------------------------------------------------------------------------------------ action builder

def _aim(dirn):
    """3x3 rotation taking +Z to the given direction."""
    return Vector((0, 0, 1)).rotation_difference(Vector(dirn).normalized()).to_matrix()


def _compose(arm, frames, name, body, arms, hop_amp=None):
    """Build one looping action in two passes. Pass 1 keys the body and legs (and plants the feet when `hop_amp` is
    given). Pass 2 evaluates each frame and lets `arms(ph, D, ev, chest_def)` set the arm deltas and return the tool's
    armature-space matrix (or None), so arms and tools follow the final, planted body."""
    act = _new_action(arm, name)
    sc = bpy.context.scene
    sways = []
    for f in range(frames + 1):
        D, sway = body((f % frames) / frames)
        for side in ("Left", "Right"):                                # provisional arms so the frame evaluates
            for b in ("Shoulder", "UpperArm", "LowerArm", "Hand"):
                D[side + b] = D["Chest"]
        _key(arm, f, D, loc={"Hips": (sway, 0.0, 0.0)})
        _key_tool(arm, f, Matrix.Identity(4))
        sways.append(sway)
    if hop_amp is not None:
        _plant_feet(arm, frames, sways, hop_amp=hop_amp)
    for f in range(frames + 1):
        ph = (f % frames) / frames
        D, _ = body(ph)
        sc.frame_set(f)
        bpy.context.view_layer.update()
        ev = _eval_bones(arm)
        chest_def = ev["Chest"].matrix @ arm.data.bones["Chest"].matrix_local.inverted()
        M = arms(ph, D, ev, chest_def)
        _key(arm, f, D)
        _key_tool(arm, f, M if M is not None else Matrix.Identity(4))
    _finish(arm, act, frames)
    return act


# ------------------------------------------------------------------------------------------------------ bodies

def _run_body(ph, cartoon=True):
    """Torso, head and legs of a run. `cartoon` exaggerates waddle and bounce; otherwise a plain athletic run."""
    tp = 2 * math.pi
    k = 1.0 if cartoon else 0.45
    s1, c1 = math.sin(tp * ph), math.cos(tp * ph)
    c2 = math.cos(2 * tp * ph)
    lean = -6.0 if cartoon else -10.0
    ident = Matrix.Identity(3)
    D = {"Root": ident}
    D["Hips"] = _rot("Y", 8 * k * s1) @ _rot("Z", 10 * k * c1) @ _rot("X", lean * 0.4)
    D["Spine"] = D["Hips"] @ _rot("Z", -8 * k * c1) @ _rot("Y", -5 * s1 * (1 if cartoon else 1.6)) @ _rot("X", lean * 0.3)
    D["Chest"] = D["Spine"] @ _rot("Z", -5 * k * c1) @ _rot("Y", -3 * s1) @ _rot("X", lean * 0.3 + 3 * c2)
    D["Neck"] = D["Chest"] @ _rot("X", 4 * c2)
    D["Head"] = (D["Neck"] @ _rot("X", -lean * 0.9 + 7 * k * math.cos(tp * 2 * (ph - 0.1))) @ _rot("Y", -5 * k * s1)
                 @ _rot("Z", 6 * k * c1))
    D["Belly"] = D["Spine"] @ _rot("X", 16 * math.sin(tp * 2 * (ph - 0.16)))
    D["Pack"] = D["Chest"] @ _rot("X", 10 * math.sin(tp * 2 * (ph - 0.28))) @ _rot("Y", 4 * s1)
    for side, sgn in (("Left", 1), ("Right", -1)):
        p = (ph + (0.0 if sgn == 1 else 0.5)) % 1.0
        sp = math.sin(tp * p)
        thigh = (44 if cartoon else 38) * sp
        flex = 8 + (56 if cartoon else 48) * max(0.0, math.cos(tp * (p - 0.08))) ** 1.5
        lower_abs = thigh - flex
        D[side + "UpperLeg"] = D["Hips"] @ _rot("X", thigh) @ _rot("Y", -sgn * 3)
        D[side + "LowerLeg"] = _rot("X", lower_abs) @ D["Hips"]
        D[side + "Foot"] = _rot("X", -0.75 * lower_abs) @ D["Hips"]
    return D, (0.030 if cartoon else 0.012) * s1


def _stand_body(ph):
    """Relaxed standing with breathing and a slow weight shift."""
    tp = 2 * math.pi
    s, c = math.sin(tp * ph), math.cos(tp * ph)
    ident = Matrix.Identity(3)
    D = {"Root": ident}
    D["Hips"] = _rot("Y", 1.6 * s) @ _rot("Z", 1.2 * c)
    D["Spine"] = D["Hips"] @ _rot("X", -1.5 + 1.2 * s) @ _rot("Z", -0.8 * c)
    D["Chest"] = D["Spine"] @ _rot("X", 1.4 * s) @ _rot("Y", -0.8 * s)
    D["Neck"] = D["Chest"] @ _rot("X", -0.8 * s)
    D["Head"] = D["Neck"] @ _rot("Z", 4.0 * math.sin(tp * (ph + 0.15))) @ _rot("X", 1.2 * c)
    D["Belly"] = D["Spine"] @ _rot("X", 5 * math.sin(tp * (ph - 0.12)))
    D["Pack"] = D["Chest"] @ _rot("X", 2.5 * math.sin(tp * (ph - 0.2)))
    for side, sgn in (("Left", 1), ("Right", -1)):
        shift = 2.2 * math.sin(tp * ph) * sgn
        D[side + "UpperLeg"] = D["Hips"] @ _rot("Y", -sgn * 3) @ _rot("X", 1.0 + 0.8 * shift)
        D[side + "LowerLeg"] = D["Hips"] @ _rot("X", -1.0 - 0.5 * shift)
        D[side + "Foot"] = D["Hips"] @ _rot("X", 0.0)
    return D, 0.006 * s


# ------------------------------------------------------------------------------------------------------ arms

def _arm_neutral(arm, side, sgn, ph, D, swing=0.0, bend=14.0):
    """Arm hanging by the side. `swing` (degrees, + forward) and `bend` (elbow, forward) pose it; used for idle and for
    the free arm while running."""
    ch = D["Chest"]
    tp = 2 * math.pi
    D[side + "Shoulder"] = ch
    fw = math.sin(math.radians(swing))
    up_dir = ch @ Vector((sgn * 0.13, fw, -math.cos(math.radians(swing))))
    D[side + "UpperArm"] = _aim_bone(arm, side + "UpperArm", up_dir, up=False)
    b = math.radians(swing + bend)
    lo_dir = ch @ Vector((sgn * 0.09, math.sin(b), -math.cos(b)))
    D[side + "LowerArm"] = _aim_bone(arm, side + "LowerArm", lo_dir, up=False)
    D[side + "Hand"] = D[side + "LowerArm"]


def _arms_idle(arm):
    tp = 2 * math.pi

    def arms(ph, D, ev, chest_def):
        for side, sgn in (("Left", 1), ("Right", -1)):
            _arm_neutral(arm, side, sgn, ph, D, swing=2.5 * math.sin(tp * (ph + 0.2 * sgn)), bend=10 + 3 * math.sin(tp * ph))
        return None
    return arms


def _arms_cheer(arm):
    """\\o/ : both arms straight up beside the head, mittens waving a little (mixed harmonics, arms out of step), so it
    looks lively but repeats every cycle."""
    tp = 2 * math.pi

    def arms(ph, D, ev, chest_def):
        ch = D["Chest"]
        for side, sgn in (("Left", 1), ("Right", -1)):
            off = 0.0 if sgn == 1 else 0.37
            spread = 31 + 8 * math.sin(tp * (ph + off + 0.1)) + 4 * math.sin(tp * (3 * ph + off))
            fwd = 0.06 * math.sin(tp * (2 * ph + off + 0.3))
            el = 4 + 9 * math.sin(tp * (3 * ph + off + 0.25)) + 4 * math.sin(tp * (2 * ph + off))
            sp, e = math.radians(spread), math.radians(el)
            D[side + "Shoulder"] = ch @ _rot("Y", -sgn * 14)
            D[side + "UpperArm"] = _aim_bone(arm, side + "UpperArm", ch @ Vector((sgn * math.sin(sp), fwd, math.cos(sp))))
            fa = ch @ Vector((sgn * math.sin(sp + e), fwd * 1.5, math.cos(sp + e)))
            D[side + "LowerArm"] = _aim_bone(arm, side + "LowerArm", fa)
            fl = math.radians(sgn * 8 * math.sin(tp * (4 * ph + off)))
            D[side + "Hand"] = _aim_bone(arm, side + "Hand", ch @ Vector((sgn * math.sin(sp + e + fl), 0.0, math.cos(sp + e + fl))))
        return None
    return arms


# Tool in the right hand, the way a first-person game holds it: grip at the right hip, in front of the body.
TOOL_HOLD = {
    "SHOVEL": (Vector((-0.27, 0.24, 0.80)), (-0.06, -0.42, 0.90)),      # blade forward and down, handle back
    "PICKAXE": (Vector((-0.27, 0.24, 0.80)), (-0.15, 0.85, 0.40)),      # head forward, just above the hip
}
# Running with a tool: the shovel is carried mid-shaft with the blade forward so it clears the ground.
TOOL_RUN = {"SHOVEL": (Vector((-0.27, 0.20, 0.88)), (-0.05, -0.72, 0.69)), "PICKAXE": TOOL_HOLD["PICKAXE"]}


def _arms_tool(arm, kind, running):
    """Right hand on the tool (two-bone IK to the grip), left arm hanging (idle) or swinging (running)."""
    tp = 2 * math.pi
    R0, aim = (TOOL_RUN if running else TOOL_HOLD)[kind]
    Mrest = Matrix.Translation(R0) @ _aim(aim).to_4x4()

    def arms(ph, D, ev, chest_def):
        M = chest_def @ Mrest
        if running:
            M = M @ Matrix.Translation((0, 0, 0.012 * math.sin(tp * 2 * ph)))
        for side, sgn in (("Left", 1), ("Right", -1)):
            if side == "Left":
                if running:
                    p = ph % 1.0
                    _arm_neutral(arm, side, sgn, ph, D, swing=-38 * math.sin(tp * p), bend=70 + 15 * math.cos(tp * p))
                else:
                    _arm_neutral(arm, side, sgn, ph, D, swing=2.5 * math.sin(tp * (ph + 0.2)), bend=10 + 3 * math.sin(tp * ph))
                continue
            D[side + "Shoulder"] = D["Chest"]
            S = ev[side + "UpperArm"].head.copy()
            Du, Dl = _ik_arm(arm, side, S, M @ Vector((0, 0, 0)), Vector((-0.55, -0.35, -0.75)))
            D[side + "UpperArm"], D[side + "LowerArm"], D[side + "Hand"] = Du, Dl, Dl
        return M
    return arms


# ------------------------------------------------------------------------------------------------------ actions

def make_idle(arm, frames=48, name="IDLE"):
    """Standing still, arms neutral at the sides."""
    return _compose(arm, frames, name, _stand_body, _arms_idle(arm))


def make_run_cycle(arm, frames=24, name="RUN"):
    """Cartoon run, arms up beside the head like \\o/, hands waving a little. Heavy plants, waddle, hop, belly and pack
    lag. Loops seamlessly."""
    return _compose(arm, frames, name, _run_body, _arms_cheer(arm), hop_amp=0.05)


def make_shovel_hold(arm, frames=48, name="HOLD_SHOVEL"):
    """Standing, shovel in the right hand held low in front of the hip (first-person style)."""
    return _compose(arm, frames, name, _stand_body, _arms_tool(arm, "SHOVEL", False))


def make_pickaxe_hold(arm, frames=48, name="HOLD_PICKAXE"):
    return _compose(arm, frames, name, _stand_body, _arms_tool(arm, "PICKAXE", False))


def make_shovel_run(arm, frames=24, name="RUN_SHOVEL"):
    """A plain run, shovel carried in the right hand, left arm pumping."""
    return _compose(arm, frames, name, lambda ph: _run_body(ph, False), _arms_tool(arm, "SHOVEL", True), hop_amp=0.06)


def make_pickaxe_run(arm, frames=24, name="RUN_PICKAXE"):
    return _compose(arm, frames, name, lambda ph: _run_body(ph, False), _arms_tool(arm, "PICKAXE", True), hop_amp=0.06)


ACTIONS = {"IDLE": (make_idle, None), "RUN": (make_run_cycle, None), "HOLD_SHOVEL": (make_shovel_hold, "SHOVEL"),
           "HOLD_PICKAXE": (make_pickaxe_hold, "PICKAXE"), "RUN_SHOVEL": (make_shovel_run, "SHOVEL"),
           "RUN_PICKAXE": (make_pickaxe_run, "PICKAXE")}



# ------------------------------------------------------------------------------------------------------ export

def set_action(arm, name):
    arm.animation_data.action = bpy.data.actions[name]


def export_fbx(root, arm, path, action=None, tools=("SHOVEL", "PICKAXE")):
    """Export the rigged worker (armature, skinned meshes, optional tools) with one action as a Unity clip."""
    if action:
        set_action(arm, action)
    view = bpy.context.view_layer
    for o in view.objects:
        o.select_set(False)
    arm.select_set(True)
    for o in arm.children_recursive:
        if o.type != "MESH":
            continue
        if o.get("cs_tool"):
            if o["cs_tool"] in tools:
                o.select_set(True)
        elif not o.hide_render:
            o.select_set(True)
    view.objects.active = arm
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False,
                             primary_bone_axis="Y", secondary_bone_axis="X", bake_anim=True,
                             bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
                             bake_anim_simplify_factor=0.0, mesh_smooth_type="FACE", apply_unit_scale=True,
                             apply_scale_options="FBX_SCALE_UNITS", path_mode="COPY", embed_textures=False)
    return path
