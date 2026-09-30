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
    weights = _smooth_weights(src, weights, iterations=6)
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
        leg_mask = _ss(0.88, 0.70, z)
        arm_mask = max(_ss(0.12, 0.26, ax), _ss(0.95, 1.05, z))
        for n in list(acc):
            if "Leg" in n or n.endswith("Foot"):
                acc[n] *= leg_mask
            elif n.endswith(("UpperArm", "LowerArm", "Hand", "Shoulder")):
                acc[n] *= arm_mask
        t = sum(acc.values())
        return {n: w / t for n, w in acc.items()} if t > 1e-6 else {"Spine": 1.0}

    def weight_at(p):
        a = _ss(0.80, 0.66, p.z) * _ss(0.30, 0.22, abs(p.x))   # 0 above the hips / out at the arms, 1 in the legs
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
        if o.name == "SUIT_KIT":
            for isl in _islands(o.data):
                pts = [mw @ o.data.vertices[i].co for i in isl]
                ext = max(max(q[a] for q in pts) - min(q[a] for q in pts) for a in range(3))
                if ext < 0.14:
                    continue                     # small patches, pockets and buttons follow the fabric
                c = sum(pts, Vector()) / len(pts)
                if c.y < -0.19 and 0.68 < c.z < 1.25 and abs(c.x) < 0.30:
                    bone = "Pack"
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
            elif o.name == "SUIT_KIT" and p.y < -0.19 and 0.68 < p.z < 1.25 and abs(p.x) < 0.30:
                w = {"Pack": 1.0}
            else:
                w = weight_at(p)
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


def _aim_bone(arm, bone, direction):
    """Rotation delta (armature space) that turns a bone's rest direction onto `direction`."""
    b = arm.data.bones[bone]
    rest = (b.tail_local - b.head_local).normalized()
    return rest.rotation_difference(Vector(direction).normalized()).to_matrix()


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


# ------------------------------------------------------------------------------------------------------ RUN

def make_run_cycle(arm, frames=24, name="RUN"):
    """Cartoon run: hands waving above the head, erratic but ordered (mixed 1x/2x/3x harmonics, arms out of phase),
    high knees, heavy plants, hip waddle and bounce, head bob, belly and pack lag. Loops seamlessly."""
    act = _new_action(arm, name)
    tp = 2 * math.pi
    ident = Matrix.Identity(3)
    sways = []
    for f in range(frames + 1):
        ph = (f % frames) / frames
        s1, c1 = math.sin(tp * ph), math.cos(tp * ph)
        s2, c2 = math.sin(2 * tp * ph), math.cos(2 * tp * ph)
        lean = -6.0
        D = {"Root": ident}
        D["Hips"] = _rot("Y", 8 * s1) @ _rot("Z", 10 * c1) @ _rot("X", lean * 0.4)
        D["Spine"] = D["Hips"] @ _rot("Z", -8 * c1) @ _rot("Y", -5 * s1) @ _rot("X", lean * 0.3)
        D["Chest"] = D["Spine"] @ _rot("Z", -5 * c1) @ _rot("Y", -3 * s1) @ _rot("X", lean * 0.3 + 3 * c2)
        D["Neck"] = D["Chest"] @ _rot("X", 4 * c2)
        D["Head"] = (D["Neck"] @ _rot("X", -lean * 0.9 + 7 * math.cos(tp * 2 * (ph - 0.1))) @ _rot("Y", -5 * s1)
                     @ _rot("Z", 6 * c1))
        D["Belly"] = D["Spine"] @ _rot("X", 16 * math.sin(tp * 2 * (ph - 0.16)))
        D["Pack"] = D["Chest"] @ _rot("X", 10 * math.sin(tp * 2 * (ph - 0.28))) @ _rot("Y", 4 * s1)
        for side, sgn in (("Left", 1), ("Right", -1)):
            p = (ph + (0.0 if sgn == 1 else 0.5)) % 1.0
            sp = math.sin(tp * p)
            thigh = 44 * sp
            flex = 8 + 68 * max(0.0, math.cos(tp * (p - 0.08))) ** 1.5
            lower_abs = thigh - flex
            foot_abs = -0.75 * lower_abs
            D[side + "UpperLeg"] = D["Hips"] @ _rot("X", thigh) @ _rot("Y", -sgn * 3)
            D[side + "LowerLeg"] = _rot("X", lower_abs) @ D["Hips"]
            D[side + "Foot"] = _rot("X", foot_abs) @ D["Hips"]
            # arms: up above the head, waving. Each arm mixes 2x and 3x harmonics with its own phase so it looks
            # random, but repeats every cycle and the two arms stay out of step.
            off = 0.0 if sgn == 1 else 0.37
            raise_deg = 170 + 9 * math.sin(tp * (2 * ph + off)) + 6 * math.sin(tp * (3 * ph + 0.6 * off + 0.2))
            spread = 24 + 13 * math.sin(tp * (ph + off + 0.1)) + 6 * math.sin(tp * (3 * ph + off))
            ch = D["Chest"]
            D[side + "Shoulder"] = ch @ _rot("Y", -sgn * 11)             # shrug up
            # aim the bones: upper arm nearly vertical (fanning out by `spread`), forearm continuing up with a small
            # bend, hand flapping about the wrist.
            fwd = 0.10 * math.sin(tp * (2 * ph + off + 0.3))
            sp = math.radians(spread)
            up_dir = ch @ Vector((sgn * math.sin(sp), fwd, math.cos(sp)))
            D[side + "UpperArm"] = _aim_bone(arm, side + "UpperArm", up_dir)
            el = math.radians(6 + 16 * math.sin(tp * (3 * ph + off + 0.25)) + 6 * math.sin(tp * (2 * ph + off)))
            fa_dir = ch @ Vector((sgn * math.sin(sp + el), fwd + 0.25 * math.sin(el * 2 + tp * off), math.cos(sp + el)))
            D[side + "LowerArm"] = _aim_bone(arm, side + "LowerArm", fa_dir)
            fl = math.radians(28 * math.sin(tp * (3 * ph + off + 0.55)))
            fl2 = math.radians(sgn * 20 * math.sin(tp * (4 * ph + off)))
            D[side + "Hand"] = _aim_bone(arm, side + "Hand", ch @ Vector((sgn * math.sin(sp + el + fl2), math.sin(fl), math.cos(sp + el + fl2) * math.cos(fl))))
        sway = 0.030 * s1
        _key(arm, f, D, loc={"Hips": (sway, 0.0, 0.0)})
        _key_tool(arm, f, Matrix.Identity(4))
        sways.append(sway)
    _plant_feet(arm, frames, sways, hop_amp=0.05)
    _finish(arm, act, frames)
    return act


# ------------------------------------------------------------------------------------------------------ HOLD poses

def _stand_pose(ph):
    """Relaxed standing with breathing and a slow weight shift. Returns the torso/leg/head/pack deltas."""
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


def _hold(arm, frames, name, place, right_target, left_target, left_relaxed):
    """Generic hold builder. `place(chest_def)` returns the tool's armature-space matrix; the right/left targets are
    grip points in the tool's local frame (or None to leave that arm to `left_relaxed(ph)` FK)."""
    act = _new_action(arm, name)
    sc = bpy.context.scene
    for f in range(frames + 1):
        ph = (f % frames) / frames
        D, sway = _stand_pose(ph)
        for side in ("Left", "Right"):                                 # provisional arm pose so the frame evaluates
            D[side + "Shoulder"] = D["Chest"]
            D[side + "UpperArm"] = D["Chest"]
            D[side + "LowerArm"] = D["Chest"]
            D[side + "Hand"] = D["Chest"]
        _key(arm, f, D, loc={"Hips": (sway, 0.0, 0.0)})
        _key_tool(arm, f, Matrix.Identity(4))
        sc.frame_set(f)
        bpy.context.view_layer.update()
        ev = _eval_bones(arm)
        chest_def = ev["Chest"].matrix @ arm.data.bones["Chest"].matrix_local.inverted()
        M = place(chest_def)
        for side, target in (("Left", left_target), ("Right", right_target)):
            sgn = 1 if side == "Left" else -1
            if target is None:
                D.update(left_relaxed(side, sgn, ph, D["Chest"]))
                continue
            S = ev[side + "UpperArm"].head.copy()
            T = M @ Vector(target)
            Du, Dl = _ik_arm(arm, side, S, T, Vector((sgn * 0.55, -0.25, -0.8)))
            D[side + "UpperArm"], D[side + "LowerArm"], D[side + "Hand"] = Du, Dl, Dl
        _key(arm, f, D, loc={"Hips": (sway, 0.0, 0.0)})
        _key_tool(arm, f, M)
    _finish(arm, act, frames)
    return act


def _aim(dirn):
    """3x3 rotation taking +Z to the given direction."""
    return Vector((0, 0, 1)).rotation_difference(Vector(dirn).normalized()).to_matrix()


def make_shovel_hold(arm, frames=48, name="HOLD_SHOVEL"):
    """Two-handed hold: shovel held upright in front of the body, blade just off the ground, both hands on the shaft."""
    R0 = Vector((-0.10, 0.34, 0.85))
    Mrest = Matrix.Translation(R0) @ _aim((0.22, 0.03, 0.97)).to_4x4()

    def place(chest_def):
        return chest_def @ Mrest

    return _hold(arm, frames, name, place, (0, 0, 0), CT.GRIP_LEFT["SHOVEL"], None)


def make_pickaxe_hold(arm, frames=48, name="HOLD_PICKAXE"):
    """Pickaxe resting on the right shoulder, right hand on the handle in front of the chest, left arm relaxed."""
    R0 = Vector((-0.27, 0.27, 0.93))
    Mrest = Matrix.Translation(R0) @ _aim((-0.20, -0.86, 0.47)).to_4x4()

    def place(chest_def):
        return chest_def @ Mrest

    def left_relaxed(side, sgn, ph, ch):
        tp = 2 * math.pi
        up = ch @ _rot("X", 14 + 3 * math.sin(tp * ph)) @ _rot("Y", sgn * 4)
        low = up @ _rot("X", 22)
        return {side + "UpperArm": up, side + "LowerArm": low, side + "Hand": low}

    return _hold(arm, frames, name, place, (0, 0, 0), None, left_relaxed)


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
