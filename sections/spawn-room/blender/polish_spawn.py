#!/usr/bin/env python3
"""
Spawn Room polish pass (final-pass critic findings): wear, doorway light, bench posts, Material_A framing.

Run headlessly (Blender 5.2) on the canonical module, after add_hero_suits.py:
    blender -b <input.blend> -P polish_spawn.py -- <output.blend>

Idempotent: every step sets absolute values or removes what it added before adding it again.
  1. BRIEFING_backrest_upright.*: posts moved behind the backrest boards, ending under the top board (they poked through
     the boards as spikes), with capped ends.
  2. Wear: a scuff layer (object-space noise mask: darker grime/scuffs, higher roughness) is added to V_locker_steel
     (lockers), pressure_metal (airlock door face), CS_tile_floor, CS_hall_floor and rubber (mats, feet). Nothing is
     recoloured: the original graph still drives the base colour, the layer only multiplies/mixes over it.
  3. Doorway colour spill: one baked area light inside each of the briefing and locker rooms beside its hall door, tinted
     to the room, so the hall gets colour falloff near the doors. Both are tagged like the existing baked lights.
  4. Door-frame portals use a slightly lifted graphite instead of the pure-black darksteel so the frames read as frames.
  5. VALIDATE_Material_A (26 mm, from the locker-room door side) is reframed to hold wall, floor, painted equipment, rubber, paper and glass (CAMERAS.md).
"""
import math
import sys

import bpy
from mathutils import Vector

OUT = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else None
M = bpy.data.materials
scene = bpy.context.scene
LAYER = "POLISH_scuff"


# ---------------------------------------------------------------- 1. bench posts
for o in bpy.data.objects:
    if o.name.startswith("BRIEFING_backrest_upright") and o.type == "CURVE":
        s = o.data.splines[0]
        sx = s.points[0].co[0]
        for p, (y, z) in zip(s.points, ((0.18, 0.35), (0.28, 0.59), (0.335, 0.82))):
            p.co = (sx, y, z, 1.0)
        o.data.use_fill_caps = True
        o.data.bevel_resolution = 4


# ---------------------------------------------------------------- 2. wear
def add_scuffs(mat, scale, tint, strength, rough_add, streak=0.0, lo=0.52, hi=0.8):
    nt = mat.node_tree
    pr = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    # a previous run: put the original base colour / roughness source back before removing the layer
    for key, idx in (("Base Color", 6), ("Roughness", 2)):
        sock = pr.inputs[key]
        if sock.is_linked and sock.links[0].from_node.label.startswith(LAYER):
            src = sock.links[0].from_node
            if src.inputs[idx].is_linked:
                nt.links.new(src.inputs[idx].links[0].from_socket, sock)
            else:
                sock.default_value = src.inputs[idx].default_value if key == "Base Color" else src.inputs[idx].default_value
    for n in [n for n in nt.nodes if n.label.startswith(LAYER)]:
        nt.nodes.remove(n)

    def node(kind, label, **kw):
        n = nt.nodes.new(kind)
        n.label = "%s %s" % (LAYER, label)
        for k, v in kw.items():
            setattr(n, k, v)
        return n

    tc = node("ShaderNodeTexCoord", "coords")
    mp = node("ShaderNodeMapping", "map")
    mp.inputs["Scale"].default_value = (scale, scale, scale)
    nz = node("ShaderNodeTexNoise", "noise")
    nz.inputs["Scale"].default_value = 1.0
    nz.inputs["Detail"].default_value = 9.0
    nz.inputs["Roughness"].default_value = 0.68
    nz.inputs["Distortion"].default_value = 0.35
    ramp = node("ShaderNodeValToRGB", "ramp")
    ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[1].position = lo, hi
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    mask = ramp.outputs["Color"]
    if streak:
        sm = node("ShaderNodeMapping", "streak_map")
        sm.inputs["Scale"].default_value = (scale * 0.7, scale * 0.7, scale * 9.0)
        sn = node("ShaderNodeTexNoise", "streak_noise")
        sn.inputs["Scale"].default_value = 1.0
        sn.inputs["Detail"].default_value = 5.0
        sr = node("ShaderNodeValToRGB", "streak_ramp")
        sr.color_ramp.elements[0].position, sr.color_ramp.elements[1].position = 0.55, 0.78
        nt.links.new(tc.outputs["Object"], sm.inputs["Vector"])
        nt.links.new(sm.outputs["Vector"], sn.inputs["Vector"])
        nt.links.new(sn.outputs["Fac"], sr.inputs["Fac"])
        mx = node("ShaderNodeMath", "streak_mix", operation="MAXIMUM")
        mul = node("ShaderNodeMath", "streak_scale", operation="MULTIPLY")
        mul.inputs[1].default_value = streak
        nt.links.new(sr.outputs["Color"], mul.inputs[0]) if False else None
        # ramp output is colour: take its red through a Separate node via Math on the Color's first channel
        sep = node("ShaderNodeSeparateColor", "streak_sep")
        sep2 = node("ShaderNodeSeparateColor", "mask_sep")
        nt.links.new(sr.outputs["Color"], sep.inputs["Color"])
        nt.links.new(ramp.outputs["Color"], sep2.inputs["Color"])
        nt.links.new(sep.outputs["Red"], mul.inputs[0])
        nt.links.new(sep2.outputs["Red"], mx.inputs[0])
        nt.links.new(mul.outputs["Value"], mx.inputs[1])
        mask = mx.outputs["Value"]
    else:
        sep2 = node("ShaderNodeSeparateColor", "mask_sep")
        nt.links.new(ramp.outputs["Color"], sep2.inputs["Color"])
        mask = sep2.outputs["Red"]
    fac = node("ShaderNodeMath", "strength", operation="MULTIPLY")
    fac.inputs[1].default_value = strength
    nt.links.new(mask, fac.inputs[0])

    # base colour: original -> mix toward the scuff tint by the mask (the original graph is untouched)
    bc = pr.inputs["Base Color"]
    mixc = node("ShaderNodeMix", "colour", data_type="RGBA", blend_type="MIX")
    if bc.is_linked:
        orig = bc.links[0].from_socket
        nt.links.new(orig, mixc.inputs[6])
    else:
        mixc.inputs[6].default_value = bc.default_value
    base_rgb = [bc.default_value[i] for i in range(3)]
    mixc.inputs[7].default_value = (tint[0], tint[1], tint[2], 1.0) if tint is not None else (*[c * 0.55 for c in base_rgb], 1.0)
    nt.links.new(fac.outputs["Value"], mixc.inputs[0])
    nt.links.new(mixc.outputs[2], bc)
    # roughness: original + mask * rough_add
    rg = pr.inputs["Roughness"]
    ra = node("ShaderNodeMath", "rough_add", operation="MULTIPLY_ADD", use_clamp=True)
    ra.inputs[1].default_value = rough_add
    nt.links.new(fac.outputs["Value"], ra.inputs[0])
    if rg.is_linked:
        nt.links.new(rg.links[0].from_socket, ra.inputs[2])
    else:
        ra.inputs[2].default_value = rg.default_value
    nt.links.new(ra.outputs["Value"], rg)


add_scuffs(M["V_locker_steel"], 7.0, None, 0.55, 0.22, streak=0.8)
add_scuffs(M["pressure_metal"], 4.0, (0.20, 0.20, 0.19), 0.6, 0.28, streak=0.9)
add_scuffs(M["CS_tile_floor"], 2.4, (0.20, 0.19, 0.17), 0.40, 0.12, lo=0.5, hi=0.85)
add_scuffs(M["CS_hall_floor"], 2.0, (0.18, 0.12, 0.08), 0.35, 0.12, lo=0.5, hi=0.85)
add_scuffs(M["rubber"], 5.0, (0.10, 0.10, 0.10), 0.45, 0.10, lo=0.5, hi=0.82)


# ---------------------------------------------------------------- 3. doorway colour spill
for o in [o for o in bpy.data.objects if o.name.startswith(("LOCKER_light_spill", "COZY_light_BRIEFING_spill"))]:
    bpy.data.objects.remove(o, do_unlink=True)


def spill(name, loc, colour, watts, group):
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape, ld.size, ld.size_y, ld.energy, ld.color = "RECTANGLE", 0.7, 0.7, watts, colour
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    aim = Vector((0.0, loc[1], 1.1)) - Vector(loc)
    lo.rotation_euler = aim.to_track_quat("-Z", "Y").to_euler()
    lo["cs_rt_role"] = "baked_plus_emissive_fixture"
    lo["cs_rt_group"] = group
    lo["cs_rt_shadow"] = False
    col = bpy.data.collections.get("MODULE_spawn-room") or scene.collection
    col.objects.link(lo)


spill("COZY_light_BRIEFING_spill", (-2.3, 3.7, 2.5), (1.0, 0.60, 0.38), 70.0, "briefing_and_accents")
spill("LOCKER_light_spill", (2.3, 3.7, 2.5), (0.70, 0.80, 1.00), 70.0, "locker_power")


# ---------------------------------------------------------------- 4. portal frames
if "portal_frame" not in M:
    pf = M.new("portal_frame")
    pf.use_nodes = True
pb = next(n for n in M["portal_frame"].node_tree.nodes if n.type == "BSDF_PRINCIPLED")
pb.inputs["Base Color"].default_value = (0.02, 0.021, 0.024, 1.0)
pb.inputs["Roughness"].default_value = 0.5
for o in bpy.data.objects:
    if o.type == "MESH" and ("_portal_head" in o.name or "_portal_jamb" in o.name):
        o.data.materials.clear()
        o.data.materials.append(M["portal_frame"])


# ---------------------------------------------------------------- 5. Material_A framing
cam = bpy.data.objects["VALIDATE_Material_A"]
MAT_LOC = (2.5, 4.3, 1.15)
MAT_TGT = (5.2, 2.7, 0.7)
cam.location = MAT_LOC
cam.data.lens = 26.0
cam.rotation_euler = (Vector(MAT_TGT) - Vector(MAT_LOC)).to_track_quat("-Z", "Y").to_euler()

if OUT:
    bpy.ops.wm.save_as_mainfile(filepath=OUT)
    print("saved", OUT)
