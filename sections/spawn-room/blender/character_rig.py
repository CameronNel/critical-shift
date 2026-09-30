#!/usr/bin/env python3
"""
Rig and run cycle for the crew worker (Blender 5.2 / bpy). First pass, Unity Humanoid compatible.

Skeleton: Root > Hips > Spine > Chest > Neck > Head, Chest > Left/RightShoulder > UpperArm > LowerArm > Hand, Hips >
Left/RightUpperLeg > LowerLeg > Foot. Bone names follow Unity's humanoid naming so the Avatar auto-maps. Two extra
(non-humanoid) bones give the secondary motion: Belly (jiggle) and Pack (backpack lag). Feet have no toes, so there is
no Toes bone (optional in Unity). The rest pose is an A-pose (arms hang slightly out), which Unity accepts.

Skinning: bone-heat weights are computed once on the welded body mesh (all skin regions joined), then copied to every
piece (skin regions, suit coverall, gloves, boots, kit) by nearest body vertex, so seams between regions and outfits
deform identically. The head, hood, visor and face decals are rigid to Head; the pack area is rigid to Pack.

    arm = build_rig(root, coll)            # armature object, parented to nothing, worker root unchanged
    skin_worker(root, arm)                 # vertex groups + Armature modifiers
    make_run_cycle(arm, frames=24)         # looping in-place run with waddle, bounce, head bob, belly and pack lag
"""

import math

import bmesh
import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector
from mathutils.kdtree import KDTree

import character_regions as CR
import character_worker as CW

ZS = CW.T(0.94)                       # shoulder height

# (name, parent, head, tail) for the left side; right side mirrors x. Positions are in worker root space (feet at z=0,
# +y forward, wearer's left = +x).
_CENTRE = [
    ("Root", None, (0, 0.0, 0.0), (0, 0.0, 0.16)),
    ("Hips", "Root", (0, 0.0, 0.70), (0, 0.0, 0.79)),
    ("Spine", "Hips", (0, 0.0, 0.79), (0, 0.0, 0.92)),
    ("Chest", "Spine", (0, 0.0, 0.92), (0, 0.0, 1.06)),
    ("Neck", "Chest", (0, 0.0, 1.06), (0, 0.0, 1.117)),
    ("Head", "Neck", (0, 0.0, 1.117), (0, 0.0, 1.62)),
    ("Belly", "Spine", (0, 0.05, 0.80), (0, 0.22, 0.80)),
    ("Pack", "Chest", (0, -0.26, 0.90), (0, -0.26, 1.15)),
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
DEFORM = ["Hips", "Spine", "Chest", "Neck", "Head", "Belly", "Pack"] + [
    s + n for s in ("Left", "Right") for n in ("Shoulder", "UpperArm", "LowerArm", "Hand", "UpperLeg", "LowerLeg", "Foot")]


def _bone_table():
    rows = list(_CENTRE)
    for side, sx in (("Left", 1), ("Right", -1)):
        for name, parent, h, t in _SIDE:
            par = side + parent if parent in ("Shoulder", "UpperArm", "LowerArm", "UpperLeg", "LowerLeg") else parent
            rows.append((side + name, par, (h[0] * sx, h[1], h[2]), (t[0] * sx, t[1], t[2])))
    return rows


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
            if bname.endswith(("Shoulder", "UpperLeg")) or bname in ("Spine", "Chest", "Neck", "Head", "Belly", "Pack", "Hips"):
                eb.use_connect = False
        made[bname] = eb
        eb.use_deform = bname != "Root"
    bpy.ops.object.mode_set(mode="OBJECT")
    arm.parent = root                 # keep the hierarchy root > armature > skinned meshes (root sits at the origin)
    arm.show_in_front = True
    data.display_type = "OCTAHEDRAL"
    arm["cs_rig"] = "unity-humanoid"
    return arm


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
    weights = []
    names = {i: g.name for i, g in enumerate(src.vertex_groups)}
    for v in src.data.vertices:
        w = {names[g.group]: g.weight for g in v.groups if g.weight > 1e-4}
        weights.append(w)
    return weights


def _fallback(p, arm, weights_out=None):
    """Nearest-bone weight if heat weighting left a vertex without influence."""
    best, bd = None, 1e9
    for b in arm.data.bones:
        if not b.use_deform:
            continue
        a, c = b.head_local, b.tail_local
        ab = c - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
        d = (p - (a + ab * t)).length
        if d < bd:
            best, bd = b.name, d
    return {best: 1.0}


def _smooth_weights(src, weights, iterations=6, keep=4):
    """Laplacian-smooth the per-vertex bone weights over the mesh graph so joints blend softly (no pinching)."""
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


def _islands(me):
    """Loose parts of a mesh (lists of vertex indices) via union-find over edges."""
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
    src = _weld_source(root)
    weights = _heat_weights(src, arm)
    missing = 0
    for i, v in enumerate(src.data.vertices):
        if not weights[i]:
            weights[i] = _fallback(v.co, arm)
            missing += 1
    weights = _smooth_weights(src, weights, iterations=6)
    kd = KDTree(len(src.data.vertices))
    for i, v in enumerate(src.data.vertices):
        kd.insert(v.co, i)
    kd.balance()

    def ss(a, b, x):
        t = max(0.0, min(1.0, (x - a) / (b - a)))
        return t * t * (3 - 2 * t)

    def weight_at(p):
        """Position-only weights (identical for coincident points, so region seams never open)."""
        near = kd.find_n(p, 3)
        acc = {}
        tot = 0.0
        for co, idx, d in near:
            k = 1.0 / (d + 1e-4) ** 2
            tot += k
            for n, w in weights[idx].items():
                acc[n] = acc.get(n, 0.0) + w * k
        acc = {n: w / tot for n, w in acc.items()}
        # legs do not drag the waist; arms do not drag the flank below the shoulder line
        leg_mask = ss(0.88, 0.70, p.z)
        arm_mask = max(ss(0.12, 0.26, abs(p.x)), ss(0.95, 1.05, p.z))
        for n in list(acc):
            if "Leg" in n or n.endswith("Foot"):
                acc[n] *= leg_mask
            elif n.endswith(("UpperArm", "LowerArm", "Hand", "Shoulder")):
                acc[n] *= arm_mask
        t = sum(acc.values())
        acc = {n: w / t for n, w in acc.items()} if t > 1e-6 else {"Spine": 1.0}
        # soft belly: the front of the lower torso follows the Belly bone
        lat = ss(0.26, 0.10, abs(p.x))
        k = max(0.0, 1.0 - math.hypot(p.y - 0.22, (p.z - 0.80) * 1.2) / 0.22) * 0.55 * lat if p.y > 0.03 else 0.0
        if k > 0:
            acc = {n: w * (1 - k) for n, w in acc.items()}
            acc["Belly"] = acc.get("Belly", 0.0) + k
        return acc

    meshes = [o for o in root.children_recursive if o.type == "MESH"]
    n_meshes = 0
    for o in meshes:
        if o.name == "CS_rig_src":
            continue
        head_rigid = o.parent is not None and o.parent.name.endswith("_HEAD_PIVOT")
        mw = o.matrix_world.copy()
        for n in DEFORM:
            o.vertex_groups.new(name=n)
        vg = o.vertex_groups
        rigid_bone = {}
        if o.get("cs_outfit") and o.name == "SUIT_KIT":
            # each long loose part (belt, strap, boot shaft, sole, tank...) is rigid to one bone, so it never shears
            for isl in _islands(o.data):
                pts = [mw @ o.data.vertices[i].co for i in isl]
                ext = max(max(q[a] for q in pts) - min(q[a] for q in pts) for a in range(3))
                if ext < 0.14:
                    continue                     # small patches, pockets and buttons follow the fabric (blended weights)
                c = sum(pts, Vector()) / len(isl)
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
                if n in vg:
                    vg[n].add([v.index], x, "REPLACE")
        if head_rigid:
            o.parent = None
            o.matrix_world = mw
        else:
            o.parent = None
            o.matrix_world = mw
        o.parent = arm
        o.matrix_parent_inverse = arm.matrix_world.inverted()
        mod = o.modifiers.new("Armature", "ARMATURE")
        mod.object = arm
        n_meshes += 1
    bpy.data.objects.remove(src, do_unlink=True)
    for o in root.children_recursive:
        if o.type == "EMPTY" and o.name.endswith("_HEAD_PIVOT"):
            o.hide_viewport = True
    return n_meshes, missing


# ---------------------------------------------------------------------------------------------------- animation

def _rot(axis, deg):
    return Matrix.Rotation(math.radians(deg), 3, axis)


def _rest3(arm, bone):
    return arm.data.bones[bone].matrix_local.to_3x3()


def _key(arm, frame, deltas, loc=None):
    """deltas: {bone: 3x3 rotation about world axes at the bone head (armature space)}; parents applied automatically."""
    pose = arm.pose
    for name, D in deltas.items():
        pb = pose.bones[name]
        Rr = _rest3(arm, name)
        par = pb.parent
        Dp = deltas.get(par.name) if par is not None else None
        rel = (Dp.inverted() @ D) if Dp is not None else D
        q = (Rr.inverted() @ rel @ Rr).to_quaternion()
        pb.rotation_mode = "QUATERNION"
        pb.rotation_quaternion = q
        pb.keyframe_insert("rotation_quaternion", frame=frame)
    if loc:
        for name, t in loc.items():
            pb = pose.bones[name]
            pb.location = _rest3(arm, name).inverted() @ Vector(t)
            pb.keyframe_insert("location", frame=frame)


def _sole_heights(arm):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = arm.evaluated_get(dg)
    out = []
    for side in ("Left", "Right"):
        pb = ev.pose.bones[side + "Foot"]
        m = pb.matrix
        head = m.translation
        tail = m @ Vector((0, pb.length, 0))
        out.append(min(head.z - 0.13, tail.z - 0.045))
    return out


def _plant_feet(arm, frames, sways, hop_amp=0.03):
    """Re-key the hips height so the lower foot touches the ground every frame, plus a hop that peaks in the
    passing pose (both legs near the body) and is lowest at each footfall."""
    sc = bpy.context.scene
    lows = []
    for f in range(frames + 1):
        sc.frame_set(f)
        bpy.context.view_layer.update()
        lows.append(min(_sole_heights(arm)))
    for f in range(frames + 1):
        ph = (f % frames) / frames
        hop = hop_amp * (0.5 - 0.5 * math.cos(2 * 2 * math.pi * ph + math.pi))
        pb = arm.pose.bones["Hips"]
        pb.location = _rest3(arm, "Hips").inverted() @ Vector((sways[f], 0.0, -lows[f] + hop))
        pb.keyframe_insert("location", frame=f)


def make_run_cycle(arm, frames=24, name="RUN"):
    """Looping in-place run: heavy foot plants, hip waddle and bounce, exaggerated arm swing, head bob, belly and
    pack lag. Frame 0 == frame `frames` (loops)."""
    act = bpy.data.actions.new(name)
    arm.animation_data_create()
    arm.animation_data.action = act
    two_pi = 2 * math.pi
    ident = Matrix.Identity(3)
    sways = []

    for f in range(frames + 1):
        ph = (f % frames) / frames
        s1, c1 = math.sin(two_pi * ph), math.cos(two_pi * ph)
        s2, c2 = math.sin(2 * two_pi * ph), math.cos(2 * two_pi * ph)
        D = {}
        lean = -9.0                                            # forward lean (about +X, negative leans forward)
        D["Root"] = ident
        D["Hips"] = _rot("Y", 7 * s1) @ _rot("Z", 9 * math.cos(two_pi * ph)) @ _rot("X", lean * 0.4)
        D["Spine"] = D["Hips"] @ _rot("Z", -7 * math.cos(two_pi * ph)) @ _rot("Y", -4 * s1) @ _rot("X", lean * 0.3)
        D["Chest"] = D["Spine"] @ _rot("Z", -5 * math.cos(two_pi * ph)) @ _rot("Y", -3 * s1) @ _rot("X", lean * 0.3 + 3 * c2)
        D["Neck"] = D["Chest"] @ _rot("X", 4 * c2)
        D["Head"] = D["Neck"] @ _rot("X", -lean * 0.9 + 6 * math.cos(two_pi * 2 * (ph - 0.1))) @ _rot("Y", -4 * s1) @ _rot("Z", 5 * math.cos(two_pi * ph))
        D["Belly"] = D["Spine"] @ _rot("X", 14 * math.sin(two_pi * 2 * (ph - 0.16)))
        D["Pack"] = D["Chest"] @ _rot("X", 9 * math.sin(two_pi * 2 * (ph - 0.28))) @ _rot("Y", 4 * s1)
        for side, sgn in (("Left", 1), ("Right", -1)):
            p = (ph + (0.0 if sgn == 1 else 0.5)) % 1.0      # this leg's phase
            sp = math.sin(two_pi * p)
            thigh = 40 * sp                                     # + = forward
            flex = 8 + 62 * max(0.0, math.cos(two_pi * (p - 0.08))) ** 1.5
            lower_abs = thigh - flex
            foot_abs = -0.75 * lower_abs + (16 if (0.55 < p < 0.95) else 0) * 0.0
            hip = D["Hips"]
            D[side + "UpperLeg"] = hip @ _rot("X", thigh) @ _rot("Y", -sgn * 3)
            D[side + "LowerLeg"] = _rot("X", lower_abs) @ D["Hips"]
            D[side + "Foot"] = _rot("X", foot_abs + 0.25 * lower_abs * 0) @ D["Hips"]
            # arms swing opposite to the same-side leg, big and bouncy
            arm_swing = -58 * sp
            elbow = 32 + 30 * max(0.0, -sp)
            ch = D["Chest"]
            D[side + "Shoulder"] = ch @ _rot("X", 0.28 * arm_swing)       # collar follows the swing a little
            D[side + "UpperArm"] = ch @ _rot("X", arm_swing) @ _rot("Y", sgn * (-6 + 4 * s2))
            D[side + "LowerArm"] = ch @ _rot("X", arm_swing + elbow)
            D[side + "Hand"] = ch @ _rot("X", arm_swing + elbow + 8 * math.sin(two_pi * (p - 0.15)))
        # keep the foot rotation about the ankle relative to the lower leg's absolute delta
        sway = 0.030 * math.sin(two_pi * ph)
        _key(arm, f, D, loc={"Hips": (sway, 0.0, 0.0)})
        sways.append(sway)
    _plant_feet(arm, frames, sways)
    arm.animation_data.action = act
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = frames - 1
    bpy.context.scene.render.fps = 24
    return act


def export_fbx(root, arm, path):
    """Export the rigged worker (armature + skinned meshes + the RUN action) as FBX for Unity (Humanoid Avatar)."""
    view = bpy.context.view_layer
    for o in view.objects:
        o.select_set(False)
    arm.select_set(True)
    for o in arm.children_recursive:
        if o.type == "MESH" and not o.hide_render:
            o.select_set(True)
    view.objects.active = arm
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False,
                             primary_bone_axis="Y", secondary_bone_axis="X", bake_anim=True,
                             bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
                             bake_anim_simplify_factor=0.0, mesh_smooth_type="FACE", apply_unit_scale=True,
                             apply_scale_options="FBX_SCALE_UNITS", path_mode="COPY", embed_textures=False)
    return path
