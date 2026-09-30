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
    raw["Hips"] += 2.5 * _ss(0.10, 0.0, abs(p.x)) * _ss(0.40, 0.55, p.z)   # the crotch web rides on the pelvis
    raw["Hips"] += 1.5 * _ss(-0.04, -0.15, p.y) * _ss(0.40, 0.58, p.z)     # so do the glutes; only the fold follows the thigh
    tot = sum(raw.values())
    if tot < 1e-6:
        return {side + "UpperLeg": 1.0}
    return {n: w / tot for n, w in raw.items() if w / tot > 0.01}


_ARM_R = {"UpperArm": 0.08, "LowerArm": 0.07, "Hand": 0.08}


def _torso_weights(p):
    """Hips/Spine/Chest weights from distance to the spine segments (where a point has no heat weight of its own)."""
    raw = {}
    for n in ("Hips", "Spine", "Chest"):
        h, t = SEGMENTS[n]
        raw[n] = math.exp(-(_seg_dist(p, h, t) / 0.10) ** 2) + 1e-6
    tot = sum(raw.values())
    return {n: w / tot for n, w in raw.items()}


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

    def heat_at(p, no_arm=False):
        acc, tot = {}, 0.0
        for co, idx, d in kd.find_n(p, 3):
            k = 1.0 / (d + 1e-4) ** 2
            tot += k
            for n, w in weights[idx].items():
                acc[n] = acc.get(n, 0.0) + w * k
        acc = {n: w / tot for n, w in acc.items()}
        z, ax = p.z, abs(p.x)
        leg_mask = _ss(0.88, 0.70, z) * (_leg_gate(p) if z < 0.88 and not no_arm else 1.0)
        arm_mask = 0.0 if no_arm else max(_ss(0.12, 0.26, ax), _ss(0.95, 1.05, z))
        for n in list(acc):
            if "Leg" in n or n.endswith("Foot"):
                acc[n] *= leg_mask
            elif n.endswith(("UpperArm", "LowerArm", "Hand", "Shoulder")):
                acc[n] *= arm_mask
        t = sum(acc.values())
        if no_arm:                                 # the arm's share goes to the torso bones nearest the point
            for n, w in _torso_weights(p).items():
                acc[n] = acc.get(n, 0.0) + w * max(0.0, 1.0 - t)
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

    def weight_at(p, no_arm=False):
        """Bone weights at p. `no_arm`: as if the arm were not there (for the flank, once it is cut free of the arm)."""
        a = _ss(0.80, 0.66, p.z)                 # 0 above the hips, 1 in the legs
        if 0.0 < a and not no_arm:
            a *= _leg_gate(p)                    # ...but never on a sleeve hanging beside the hip
        if a <= 0.0:
            acc = heat_at(p, no_arm)
        elif a >= 1.0:
            acc = leg_weights(p)
        else:
            acc = {}
            for n, w in heat_at(p, no_arm).items():
                acc[n] = acc.get(n, 0.0) + w * (1 - a)
            for n, w in leg_weights(p).items():
                acc[n] = acc.get(n, 0.0) + w * a
        if not no_arm:
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


Z_LEG = 0.50          # the legs are fused to each other below here (crotch)
Z_ARM = 0.97          # the inner arm is fused to the flank below here (armpit)
_CLS = ("core", "legL", "legR", "armL", "armR")


def _face_classes(bm, weight_at, mw, side_only=False):
    """Limb class per face of the fused suit body: legL/legR (by side) below the crotch, armL/armR where the weights say
    arm, else core (`side_only`: just left/right, for the boots). Smoothed and cleaned of small islands so the cut runs
    along one clean line per crease."""
    bm.faces.ensure_lookup_table()
    cls = []
    for f in bm.faces:
        c = mw @ f.calc_center_median()
        k = "core" if side_only else _limb_key(weight_at(c))
        if (c.z < Z_LEG or side_only) and not k.startswith("arm"):
            k = "legL" if c.x > 0 else "legR"
        elif k.startswith("leg"):
            k = "core"
        cls.append(k)
    nbr = [[g.index for e in f.edges for g in e.link_faces if g is not f] for f in bm.faces]
    for _ in range(4):                                             # majority filter: no saw-tooth cut lines
        new = list(cls)
        for i, ns in enumerate(nbr):
            ks = [cls[j] for j in ns]
            best = max(set(ks), key=ks.count) if ks else cls[i]
            if best != cls[i] and ks.count(best) * 2 > len(ks):
                new[i] = best
        cls = new
    for _ in range(2):                                             # islands under 40 faces join their surroundings
        seen = [False] * len(cls)
        for i in range(len(cls)):
            if seen[i]:
                continue
            comp, stack = [], [i]
            seen[i] = True
            while stack:
                j = stack.pop()
                comp.append(j)
                for n in nbr[j]:
                    if not seen[n] and cls[n] == cls[i]:
                        seen[n] = True
                        stack.append(n)
            if len(comp) < 40:
                ks = [cls[n] for j in comp for n in nbr[j] if cls[n] != cls[i]]
                if ks:
                    k = max(set(ks), key=ks.count)
                    for j in comp:
                        cls[j] = k
    return cls


def _zip(bm, a, b):
    """Close the gap between two boundary vertex chains (both ordered from the top end down) with a strip of triangles,
    each wound against the suit face it borders so the normals stay consistent."""
    def params(ch):
        d = [0.0]
        for p, q in zip(ch, ch[1:]):
            d.append(d[-1] + (q.co - p.co).length)
        return [x / (d[-1] or 1.0) for x in d]

    def wound(p, q, r):
        e = bm.edges.get((p, q))
        for f in (e.link_faces if e else ()):
            for lp in f.loops:
                if lp.vert is p and lp.link_loop_next.vert is q:
                    return (q, p, r)
        return (p, q, r)
    ta, tb = params(a), params(b)
    i = j = 0
    faces = []
    while i < len(a) - 1 or j < len(b) - 1:
        if j == len(b) - 1 or (i < len(a) - 1 and ta[i + 1] <= tb[j + 1]):
            tri = wound(a[i], a[i + 1], b[j])
            i += 1
        else:
            tri = wound(b[j], b[j + 1], a[i])
            j += 1
        if len(set(tri)) == 3 and bm.faces.get(tri) is None:
            faces.append(bm.faces.new(tri))
    return faces


def _chains(edges):
    """Split a set of boundary edges into vertex chains (ordered paths); closed loops come back as one path."""
    adj = {}
    for e in edges:
        a, b = e.verts
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    left, out = set(adj), []
    while left:
        ends = [v for v in left if len(adj[v]) == 1]
        v = ends[0] if ends else next(iter(left))
        ch = [v]
        left.discard(v)
        while True:
            nxt = [n for n in adj[ch[-1]] if n in left]
            if not nxt:
                break
            ch.append(nxt[0])
            left.discard(nxt[0])
        out.append(ch)
    return out


def _separate_limbs(o, weight_at, mw, side_only=False):
    """The suit body is one fused mesh: the legs touch each other from the crotch down and the inner arm touches the
    flank below the armpit, so a striding leg or a raised arm stretches the shared fabric into torn-looking slivers.
    Cut those creases open and close each side with its own wall (a strip between the front and back cut lines), so each
    limb is a closed surface that moves on its own and nothing opens. Returns the class of every vertex and a lookup
    for the class of the nearest suit face (used so patches on the suit follow the same side)."""
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(o.data)
    cls = _face_classes(bm, weight_at, mw, side_only)
    lay = bm.faces.layers.int.new("cs_cls")
    for f in bm.faces:
        f[lay] = _CLS.index(cls[f.index])

    def key(e):
        return frozenset(v.co.to_tuple(6) for v in e.verts)
    old_open = {key(e) for e in bm.edges if e.is_boundary}
    cut = []
    for e in bm.edges:
        if len(e.link_faces) != 2:
            continue
        a, b = (_CLS[f[lay]] for f in e.link_faces)
        z = (mw @ ((e.verts[0].co + e.verts[1].co) * 0.5)).z
        if a != b and ({a, b} == {"legL", "legR"} or (z < Z_ARM and "arm" in a + b)):
            cut.append(e)
    bmesh.ops.split_edges(bm, edges=cut)
    groups = {}
    for e in bm.edges:
        if e.is_boundary and key(e) not in old_open:
            k = e.link_faces[0][lay]
            groups.setdefault((k, (mw @ e.verts[0].co).x > 0 if _CLS[k] == "core" else None), []).append(e)
    walls = 0
    for (k, sd), edges in groups.items():
        chains = _chains(edges)
        if __import__("os").environ.get("RIG_DEBUG"):
            print("RIG cut group", _CLS[k], sd, [(len(c), round(min(v.co.z for v in c), 3), round(max(v.co.z for v in c), 3),
                                                  c[0] in {n for e in c[-1].link_edges for n in e.verts}) for c in chains])
        if len(chains) == 1:                   # one U-shaped cut (the arm): split it at its lowest point
            ch = chains[0]
            low = min(range(len(ch)), key=lambda i: ch[i].co.z)
            a, b = ch[:low + 1], ch[low:][::-1]
        elif len(chains) == 2:                 # two cuts reaching an existing opening (the legs, front and back)
            a, b = (c if c[0].co.z > c[-1].co.z else c[::-1] for c in chains)
        else:
            raise RuntimeError("suit body %s cut makes %d chains" % (_CLS[k], len(chains)))
        for f in _zip(bm, a, b):
            f[lay] = k
            f.smooth = True
            walls += 1
    bm.verts.index_update()
    bm.faces.index_update()
    vcls = {}
    for v in bm.verts:
        ks = [_CLS[f[lay]] for f in v.link_faces]
        vcls[v.index] = max(set(ks), key=ks.count) if ks else "core"
    fcls = [_CLS[f[lay]] for f in bm.faces]
    tree = BVHTree.FromBMesh(bm)
    bm.to_mesh(o.data)
    bm.free()
    o.data.update()

    def near(p, reach=0.08):
        """(class, distance) of the nearest face of this mesh, or ("core", None) if none is within `reach`."""
        hit = tree.find_nearest(mw.inverted() @ p, reach)
        return (fcls[hit[2]], hit[3]) if hit[0] is not None else ("core", None)
    print("RIG %s: %d cut edges, %d wall faces" % (o.name, len(cut), walls))
    return vcls, near


def _restricted(weight_at, p, key):
    """Weights at p confined to limb `key` where the suit body was cut (below the crotch for the legs, below the armpit
    for the arms and flank), fading back to the plain weights where the cut ends."""
    side = {"L": "Left", "R": "Right"}.get(key[-1], "")
    if key.startswith("leg") and (p.x > 0) != (side == "Left"):
        p = Vector((-p.x, p.y, p.z))           # a face of this leg that sits over the midline: use this leg's weights
    w = weight_at(p)
    r_leg = _ss(Z_LEG, Z_LEG - 0.06, p.z)
    r_arm = _ss(Z_ARM, Z_ARM - 0.08, p.z)
    if key.startswith("arm"):
        r = r_arm
        keep = {n: x for n, x in w.items() if n.startswith(side) and n[len(side):] in _ARM_BONES}
    else:                                      # flank and legs: the arm is cut free, so none of its weight below the armpit
        if r_arm > 0.0:
            na = weight_at(p, no_arm=True)
            w = {n: (1 - r_arm) * w.get(n, 0.0) + r_arm * na.get(n, 0.0) for n in set(w) | set(na)}
        if not key.startswith("leg"):
            return {n: x for n, x in w.items() if x > 1e-4}
        r = r_leg
        keep = {n: x for n, x in w.items() if not n.startswith(("Left", "Right")) or n.startswith(side)}
    t = sum(keep.values())
    if r <= 0.0 or t < 1e-6:
        return w
    out = {n: (1 - r) * x for n, x in w.items()}
    for n, x in keep.items():
        out[n] = out.get(n, 0.0) + r * x / t
    return {n: x for n, x in out.items() if x > 1e-4}


def _kit_mode(pts, near):
    """How a SUIT_KIT island is skinned: "Pack" (rides the backpack), "follow" (anything lying flat on the fabric: patches,
    piping, straps, bands; follows it vertex by vertex), "piece" (a small raised item that moves as one piece with the
    fabric under it) or "rigid" (a long raised hard part such as the belt or a sole, rigid to one bone)."""
    ext = max(max(q[a] for q in pts) - min(q[a] for q in pts) for a in range(3))
    c = sum(pts, Vector()) / len(pts)
    behind = sum(1 for q in pts if q.y < -0.19 and 0.68 < q.z < 1.25 and abs(q.x) < 0.30) / len(pts)
    if behind > 0.5:
        return "Pack"                          # whole island, so a strap is never half rigid and half stretching
    if abs(c.x) > 0.10 and 0.95 < c.z < 1.30:
        return "follow"                        # shoulder straps and piping fold with the fabric
    if ext < 0.14 and 0.86 < c.z < 1.12 and abs(c.x) > 0.06:
        return "rigid"                         # small patches in the armpit band, where the fabric shears hardest
    size = [max(q[a] for q in pts) - min(q[a] for q in pts) for a in range(3)]
    if c.z < 0.66 and size[2] < 0.07 and min(size[0], size[1]) > 0.10:
        return "piece"                         # a band round a leg: turns as one ring (half-way at the knee)
    lift = max((near(q)[1] or 0.08) for q in pts)
    if lift < 0.025 and (ext < 0.14 or c.z < 0.66):
        return "follow"                        # flat on the fabric; long ones only on the legs, where they must bend
    return "piece" if ext < 0.14 else "rigid"


def _densify(o, keep, max_len=0.03):
    """Subdivide the long edges of the islands `keep` selects (by vertex list) so a strap or patch that follows the fabric
    bends with it instead of cutting across the curve in straight spikes."""
    mw = o.matrix_world
    tagged = set()
    for isl in _islands(o.data):
        if keep([mw @ o.data.vertices[i].co for i in isl]):
            tagged.update(isl)
    bm = bmesh.new()
    bm.from_mesh(o.data)
    lay = bm.verts.layers.int.new("cs_follow")
    bm.verts.ensure_lookup_table()
    for i in tagged:
        bm.verts[i][lay] = 1
    for _ in range(5):
        for _ in range(2):                         # new vertices of a tagged island are tagged too
            for v in bm.verts:
                if not v[lay] and any(e.other_vert(v)[lay] for e in v.link_edges):
                    v[lay] = 1
        long_edges = [e for e in bm.edges if e.verts[0][lay] and e.verts[1][lay] and e.calc_length() * mw.median_scale > max_len]
        if not long_edges:
            break
        bmesh.ops.subdivide_edges(bm, edges=long_edges, cuts=1, use_grid_fill=True)
    bm.to_mesh(o.data)
    bm.free()
    o.data.update()


def skin_worker(root, arm):
    weight_at = _make_weight_fn(root, arm)
    meshes = sorted((o for o in root.children_recursive if o.type == "MESH"), key=lambda o: o.name != "SUIT_BODY")
    near = None
    n_meshes = 0
    for o in meshes:
        head_rigid = o.parent is not None and o.parent.name.endswith("_HEAD_PIVOT")
        mw = o.matrix_world.copy()
        for n in DEFORM:
            o.vertex_groups.new(name=n)
        vg = o.vertex_groups
        fixed = {}
        vcls = None
        if o.name == "SUIT_BODY":
            vcls, near = _separate_limbs(o, weight_at, mw)
        elif o.name == "SUIT_BOOTS":
            vcls, _ = _separate_limbs(o, weight_at, mw, side_only=True)   # the two boots touch at the instep

        def w_at(p, i=None, k=None):
            """Weights for a point on this mesh: its own class on a cut mesh, or class `k` (the class of the suit under
            a kit island, so a pocket on the flank does not leave with the arm)."""
            if vcls is not None:
                return _restricted(weight_at, p, vcls[i])
            if k is not None:
                return _restricted(weight_at, p, k)
            return weight_at(p)
        if o.name == "SUIT_KIT" and near is not None:
            _densify(o, lambda pts: _kit_mode(pts, near) == "follow")
            for isl in _islands(o.data):
                pts = [mw @ o.data.vertices[i].co for i in isl]
                mode = _kit_mode(pts, near)
                ks = [near(q, 0.05)[0] for q in pts if q.z < Z_ARM and near(q, 0.05)[1] is not None]
                k = max(set(ks), key=ks.count) if ks else None      # one class per island: the arm and flank (and the
                if mode == "follow":                                 # two legs) coincide at rest where they were fused
                    for i, q in zip(isl, pts):
                        fixed[i] = w_at(q, k=k)
                    continue
                if mode == "Pack":
                    w = {"Pack": 1.0}
                elif mode == "rigid":
                    wc = {n: x for n, x in w_at(sum(pts, Vector()) / len(pts), k=k).items() if n != "Belly"}
                    w = {max(wc, key=wc.get): 1.0}
                else:                                # one averaged weight set: the item moves as a piece
                    w = {}
                    for q in pts:
                        for n, x in w_at(q, k=k).items():
                            w[n] = w.get(n, 0.0) + x / len(pts)
                for i in isl:
                    fixed[i] = w
        for v in o.data.vertices:
            p = mw @ v.co
            if head_rigid:
                w = {"Head": 1.0}
            elif v.index in fixed:
                w = fixed[v.index]
            else:
                w = w_at(p, v.index)
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


def _finish(arm, act, frames):
    arm.animation_data.action = act
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 0, frames - 1
    sc.render.fps = 24


# ------------------------------------------------------------------------------------------------------ two-bone IK

def _ik_two(arm, upper, lower, S, T, pole):
    """Analytic two-bone IK in armature space. S: posed root joint, T: target end point, pole: direction the middle
    joint bends towards. Returns absolute rotation deltas (upper, lower) taking each bone's rest direction to the solved
    direction."""
    ub, lb = arm.data.bones[upper], arm.data.bones[lower]
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


def _ik_arm(arm, side, S, T, pole):
    return _ik_two(arm, side + "UpperArm", side + "LowerArm", S, T, pole)


# ------------------------------------------------------------------------------------------------------ feet and gait

ANKLE_REST = {"Left": Vector((0.110, 0.014, 0.13)), "Right": Vector((-0.110, 0.014, 0.13))}
_HEEL, _TOE = (-0.10, -0.13), (0.20, -0.13)       # (y, z) of the boot sole's heel and toe edges from the ankle


def _ankle(c, clear, pitch):
    """Ankle (y, z) of a foot whose ankle would sit at y=c if it stood flat, with its lowest sole edge `clear` above the
    floor, pitched `pitch` degrees (+ toes up, rolling on the heel; - toes down, rolling on the toe)."""
    th = math.radians(pitch)
    py, pz = _HEEL if th >= 0 else _TOE
    ry, rz = py * math.cos(th) - pz * math.sin(th), py * math.sin(th) + pz * math.cos(th)
    return c + py - ry, clear - rz


def _hermite(keys, t):
    """Cubic Hermite through keys (t, Vector, tangent or None); finite-difference tangents where None."""
    tans = []
    for i, (ti, vi, mi) in enumerate(keys):
        if mi is None:
            a, b = keys[max(i - 1, 0)], keys[min(i + 1, len(keys) - 1)]
            mi = (b[1] - a[1]) / (b[0] - a[0])
        tans.append(mi)
    for i in range(len(keys) - 1):
        (t0, v0, _), (t1, v1, _) = keys[i], keys[i + 1]
        if t <= t1 or i == len(keys) - 2:
            h = t1 - t0
            u = (t - t0) / h
            u2, u3 = u * u, u * u * u
            return (v0 * (2 * u3 - 3 * u2 + 1) + tans[i] * (h * (u3 - 2 * u2 + u)) + v1 * (-2 * u3 + 3 * u2)
                    + tans[i + 1] * (h * (u3 - u2)))


def _loop(keys, t):
    """Periodic cubic through (t, value) keys on [0, 1]; the first key is at 0 and the last at 1 with the same value."""
    m = (keys[1][1] - keys[-2][1]) / (keys[1][0] + 1.0 - keys[-2][0])
    ks = [(k[0], Vector((k[1], 0.0)), None) for k in keys]
    ks[0] = (0.0, ks[0][1], Vector((m, 0.0)))
    ks[-1] = (1.0, ks[-1][1], Vector((m, 0.0)))
    return _hermite(ks, t % 1.0)[0]


# Run gaits, per leg phase p (0 = foot strike). Stance (p < duty): the foot is planted and slides back at treadmill speed
# from `stride[0]` to `stride[1]` (flat-ankle y), landing a little heel first and rolling onto the toe. Swing keys
# (p, flat-ankle y, sole clearance, pitch): toe-off, heel kicked up behind, knee drive, reach, then the foot pulls back
# into the strike. `hips` (per step, u = 0 at a strike): low at mid-stance, high in the flight phase, so one foot at most
# is ever on the floor. Everything is in metres and degrees for this 0.72 m-legged worker.
GAIT_PLAIN = dict(strides=1, duty=0.36, stride=(0.07, -0.25), land=6.0, push=24.0, width=0.095,
                  swing=[(0.45, -0.31, 0.06, -38), (0.56, -0.26, 0.16, -30), (0.68, -0.08, 0.21, -10),
                         (0.80, 0.10, 0.17, 6), (0.90, 0.17, 0.05, 10)],
                  hips=[(0.0, -0.005), (0.30, -0.030), (0.72, 0.028), (0.86, 0.034), (1.0, -0.005)],
                  lean=-9.0, yaw=8.0, roll=3.0, waddle=0.0, sway=0.012, nod=2.5, belly=10.0, pack=7.0)
GAIT_CARTOON = dict(GAIT_PLAIN, strides=2, duty=0.34, land=8.0, push=26.0, width=0.10,
                    swing=[(0.44, -0.31, 0.08, -40), (0.55, -0.25, 0.25, -34), (0.67, -0.06, 0.31, -10),
                           (0.79, 0.12, 0.21, 8), (0.90, 0.18, 0.07, 12)],
                    hips=[(0.0, -0.008), (0.30, -0.042), (0.70, 0.030), (0.85, 0.040), (1.0, -0.008)],
                    lean=-4.0, yaw=10.0, roll=4.0, waddle=6.0, sway=0.026, nod=5.0, belly=16.0, pack=10.0)


def _run_foot(p, g):
    """(flat-ankle y, sole clearance, pitch) of one foot at leg phase p."""
    s, (c0, c1) = g["duty"], g["stride"]
    v = (c1 - c0) / s
    lift = 0.45 * s
    if p <= s:
        pitch = g["land"] * _ss(0.06, 0.0, p) - g["push"] * (max(0.0, p - lift) / (s - lift)) ** 2
        return c0 + v * p, 0.0, pitch
    keys = [(s, Vector((c1, 0.0, -g["push"])), Vector((v, 0.0, -2 * g["push"] / (s - lift))))]
    keys += [(k[0], Vector(k[1:]), None) for k in g["swing"]]
    keys.append((1.0, Vector((c0, 0.0, g["land"])), Vector((v, -0.8, 0.0))))
    c, clear, pitch = _hermite(keys, p)
    return c, max(0.0, clear), pitch


def _run_feet(q, g):
    feet = {}
    for side, sgn in (("Left", 1), ("Right", -1)):
        c, clear, pitch = _run_foot((q + (0.0 if sgn == 1 else 0.5)) % 1.0, g)
        y, z = _ankle(c, clear, pitch)
        feet[side] = (Vector((sgn * g["width"], y, z)), pitch)
    return feet


# ------------------------------------------------------------------------------------------------------ action builder

def _aim(dirn, side=(1, 0, 0)):
    """3x3 rotation taking +Z to `dirn` and +X as close to `side` as it can (the tool's roll)."""
    z = Vector(dirn).normalized()
    x = Vector(side) - z * z.dot(Vector(side))
    x = x.normalized() if x.length > 1e-6 else z.orthogonal().normalized()
    y = z.cross(x)
    return Matrix((x, y, z)).transposed()


def _slerp3(a, b, t):
    return a.to_quaternion().slerp(b.to_quaternion(), t).to_matrix()


def _compose(arm, frames, name, body, arms):
    """Build one looping action in two passes. Pass 1 keys the torso and the hips (sway, height). Pass 2 evaluates each
    frame, solves both legs with two-bone IK to the body's foot targets (so a planted foot stays planted) and lets
    `arms(ph, D, ev, chest_def)` set the arm deltas and return the tool's armature-space matrix (or None), so legs, arms
    and tools all follow the final body."""
    act = _new_action(arm, name)
    sc = bpy.context.scene
    for f in range(frames + 1):
        D, loc, _ = body((f % frames) / frames)
        for side in ("Left", "Right"):                                # provisional limbs so the frame evaluates
            for b in ("Shoulder", "UpperArm", "LowerArm", "Hand"):
                D[side + b] = D["Chest"]
            for b in ("UpperLeg", "LowerLeg", "Foot"):
                D[side + b] = D["Hips"]
        _key(arm, f, D, loc={"Hips": loc})
        _key_tool(arm, f, Matrix.Identity(4))
    for f in range(frames + 1):
        ph = (f % frames) / frames
        D, _, feet = body(ph)
        sc.frame_set(f)
        bpy.context.view_layer.update()
        ev = _eval_bones(arm)
        for side, sgn in (("Left", 1), ("Right", -1)):
            T, pitch = feet[side]
            D[side + "UpperLeg"], D[side + "LowerLeg"] = _ik_two(
                arm, side + "UpperLeg", side + "LowerLeg", ev[side + "UpperLeg"].head.copy(), T,
                Vector((sgn * 0.15, 1.0, 0.0)))
            D[side + "Foot"] = _rot("X", pitch)
        chest_def = ev["Chest"].matrix @ arm.data.bones["Chest"].matrix_local.inverted()
        M = arms(ph, D, ev, chest_def)
        _key(arm, f, D)
        _key_tool(arm, f, M if M is not None else Matrix.Identity(4))
    _finish(arm, act, frames)
    return act


# ------------------------------------------------------------------------------------------------------ bodies

def _run_body(ph, g):
    """Torso, head, hips (sway and height) and foot targets of a run with gait `g`. The pelvis turns the striding hip
    forward and drops on the swing side, the chest counter-rotates, the head stays level with a small nod on landing."""
    tp = 2 * math.pi
    q = (ph * g["strides"]) % 1.0                  # leg phase: 0 = left foot strike, 0.5 = right foot strike
    u = (2 * q) % 1.0                              # step phase: 0 = either strike
    c1 = math.cos(tp * q)
    st = math.sin(tp * (q + 0.07))                 # + while the left foot carries the weight, - for the right
    sq = math.cos(tp * (u - 0.3))                  # 1 at mid-stance (hips lowest)
    lean, yaw, roll, wad = g["lean"], g["yaw"], g["roll"], g["waddle"]
    D = {"Root": Matrix.Identity(3)}
    D["Hips"] = _rot("Z", yaw * c1) @ _rot("Y", -roll * st) @ _rot("X", lean * 0.4)
    D["Spine"] = D["Hips"] @ _rot("Z", -yaw * 0.7 * c1) @ _rot("Y", (roll + wad) * 0.6 * st) @ _rot("X", lean * 0.3 - 1.5 * sq)
    D["Chest"] = D["Spine"] @ _rot("Z", -yaw * 0.6 * c1) @ _rot("Y", wad * 0.4 * st) @ _rot("X", lean * 0.3 - 1.5 * sq)
    D["Head"] = (_rot("Z", 0.15 * yaw * c1) @ _rot("Y", 0.3 * wad * st)
                 @ _rot("X", -g["nod"] * math.cos(tp * (u - 0.38))))
    D["Neck"] = _slerp3(D["Chest"], D["Head"], 0.5)
    D["Belly"] = D["Spine"] @ _rot("X", g["belly"] * math.sin(tp * (u - 0.42)))
    D["Pack"] = D["Chest"] @ _rot("X", g["pack"] * math.sin(tp * (u - 0.5))) @ _rot("Y", 3 * st)
    loc = Vector((g["sway"] * st, 0.0, _loop(g["hips"], u)))
    return D, loc, _run_feet(q, g)


def _stand_body(ph):
    """Relaxed standing with breathing and a slow weight shift; both feet planted where they rest."""
    tp = 2 * math.pi
    s, c = math.sin(tp * ph), math.cos(tp * ph)
    D = {"Root": Matrix.Identity(3)}
    D["Hips"] = _rot("Y", 1.6 * s) @ _rot("Z", 1.2 * c)
    D["Spine"] = D["Hips"] @ _rot("X", -1.5 + 1.2 * s) @ _rot("Z", -0.8 * c)
    D["Chest"] = D["Spine"] @ _rot("X", 1.4 * s) @ _rot("Y", -0.8 * s)
    D["Neck"] = D["Chest"] @ _rot("X", -0.8 * s)
    D["Head"] = D["Neck"] @ _rot("Z", 4.0 * math.sin(tp * (ph + 0.15))) @ _rot("X", 1.2 * c)
    D["Belly"] = D["Spine"] @ _rot("X", 5 * math.sin(tp * (ph - 0.12)))
    D["Pack"] = D["Chest"] @ _rot("X", 2.5 * math.sin(tp * (ph - 0.2)))
    feet = {side: (ANKLE_REST[side].copy(), 0.0) for side in ("Left", "Right")}
    return D, Vector((0.006 * s, 0.0, -0.003 + 0.0012 * math.sin(tp * (ph - 0.1)))), feet


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
            spread = 36 + 6 * math.sin(tp * (ph + off + 0.1)) + 3 * math.sin(tp * (3 * ph + off))
            fwd = 0.06 * math.sin(tp * (2 * ph + off + 0.3))
            el = 10 + 7 * math.sin(tp * (3 * ph + off + 0.25)) + 3 * math.sin(tp * (2 * ph + off))   # always outward
            sp, e = math.radians(spread), math.radians(el)
            D[side + "Shoulder"] = ch @ _rot("Y", -sgn * 14)
            D[side + "UpperArm"] = _aim_bone(arm, side + "UpperArm", ch @ Vector((sgn * math.sin(sp), fwd, math.cos(sp))))
            fa = ch @ Vector((sgn * math.sin(sp + e), fwd * 1.5, math.cos(sp + e)))
            D[side + "LowerArm"] = _aim_bone(arm, side + "LowerArm", fa)
            fl = math.radians(sgn * 8 * math.sin(tp * (4 * ph + off)))
            D[side + "Hand"] = _aim_bone(arm, side + "Hand", ch @ Vector((sgn * math.sin(sp + e + fl), 0.0, math.cos(sp + e + fl))))
        return None
    return arms


# Tool in the right hand. `grip`: where the hand holds it (chest space at rest), `shaft`: direction of the tool's +Z
# (towards the handle top / the pick head), `side`: where the tool's +X points (shovel blade width / pick head bar), `at`:
# the point on the shaft (tool-local z) that sits in the fist.
TOOL_HOLD = {                                     # standing, first-person style: low at the right hip
    "SHOVEL": dict(grip=(-0.28, 0.26, 0.80), shaft=(-0.22, -0.78, 0.58), side=(1, 0, 0), at=0.24),  # blade forward-down
    "PICKAXE": dict(grip=(-0.27, 0.26, 0.80), shaft=(0.10, 0.95, 0.25), side=(0, 0, 1), at=-0.14),  # head forward
}
TOOL_RUN = {                                      # running: carried at the trail, low by the right hip, pointing ahead
    "SHOVEL": dict(grip=(-0.31, 0.10, 0.81), shaft=(0.10, -0.97, 0.14), side=(1, 0, 0), at=-0.32),   # blade forward
    "PICKAXE": dict(grip=(-0.30, 0.10, 0.82), shaft=(-0.12, 0.95, 0.30), side=(0, 0, 1), at=0.40),   # choked up, head forward
}
_HAND_GRIP = 0.065                                # wrist to the middle of the mitten


def _tool_matrix(t):
    return Matrix.Translation(Vector(t["grip"])) @ _aim(t["shaft"], t["side"]).to_4x4() @ Matrix.Translation((0, 0, -t["at"]))


def _arms_tool(arm, kind, running, gait=GAIT_PLAIN):
    """Right hand on the tool (two-bone IK so the mitten closes on the grip), left arm hanging (standing) or pumping in
    step with the legs (running). The tool rides on the chest, and while running it swings a little against the left
    arm."""
    tp = 2 * math.pi
    Mrest = _tool_matrix((TOOL_RUN if running else TOOL_HOLD)[kind])

    def arms(ph, D, ev, chest_def):
        q = (ph * gait["strides"]) % 1.0
        pump = math.sin(tp * (q - 0.2))           # + when the left arm is forward (right leg forward)
        M = chest_def @ Mrest
        if running:
            g = M @ Vector((0, 0, TOOL_RUN[kind]["at"]))
            M = (Matrix.Translation(g + Vector((0.0, -0.035 * pump, 0.008 * math.cos(tp * 2 * q)))) @ _rot("X", 5 * pump).to_4x4()
                 @ Matrix.Translation(-g) @ M)
        if running:
            _arm_neutral(arm, "Left", 1, ph, D, swing=36 * pump, bend=78 + 14 * pump)
        else:
            _arm_neutral(arm, "Left", 1, ph, D, swing=2.5 * math.sin(tp * (ph + 0.2)), bend=10 + 3 * math.sin(tp * ph))
        grip = M @ Vector((0, 0, (TOOL_RUN if running else TOOL_HOLD)[kind]["at"]))
        D["RightShoulder"] = D["Chest"]
        S = ev["RightUpperArm"].head.copy()
        pole = Vector((-0.55, -0.35, -0.75))
        wrist = grip
        for _ in range(2):                        # aim the wrist so the mitten, not the wrist, closes on the grip
            Du, Dl = _ik_arm(arm, "Right", S, wrist, pole)
            fore = Dl @ (arm.data.bones["RightLowerArm"].tail_local - arm.data.bones["RightLowerArm"].head_local).normalized()
            wrist = grip - fore * _HAND_GRIP
        D["RightUpperArm"], D["RightLowerArm"], D["RightHand"] = Du, Dl, Dl
        return M
    return arms


# ------------------------------------------------------------------------------------------------------ actions

def make_idle(arm, frames=48, name="IDLE"):
    """Standing still, arms neutral at the sides."""
    return _compose(arm, frames, name, _stand_body, _arms_idle(arm))


def make_run_cycle(arm, frames=32, name="RUN"):
    """Cartoon run (two strides per loop), arms up beside the head like \\o/, hands waving a little. Bouncy flight
    phase, waddle, belly and pack lag. Loops seamlessly."""
    return _compose(arm, frames, name, lambda ph: _run_body(ph, GAIT_CARTOON), _arms_cheer(arm))


def make_shovel_hold(arm, frames=48, name="HOLD_SHOVEL"):
    """Standing, shovel in the right hand low at the hip, blade forward and down (first-person style)."""
    return _compose(arm, frames, name, _stand_body, _arms_tool(arm, "SHOVEL", False))


def make_pickaxe_hold(arm, frames=48, name="HOLD_PICKAXE"):
    """Standing, pickaxe in the right hand low at the hip, head forward."""
    return _compose(arm, frames, name, _stand_body, _arms_tool(arm, "PICKAXE", False))


def make_shovel_run(arm, frames=18, name="RUN_SHOVEL"):
    """A plain run, shovel carried at the trail in the right hand, left arm pumping."""
    return _compose(arm, frames, name, lambda ph: _run_body(ph, GAIT_PLAIN), _arms_tool(arm, "SHOVEL", True))


def make_pickaxe_run(arm, frames=18, name="RUN_PICKAXE"):
    """A plain run, pickaxe choked up in the right hand, head forward, left arm pumping."""
    return _compose(arm, frames, name, lambda ph: _run_body(ph, GAIT_PLAIN), _arms_tool(arm, "PICKAXE", True))


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
