#!/usr/bin/env python3
"""Spawn room delivery optimisation (look-preserving). Run with Blender 5.2:

    blender -b --factory-startup -P optimise_spawn.py -- <module.blend> <module_optimised.blend> [report.json]

The canonical module is never edited: this writes a separate delivery derivative.

What it does, in order (each step is meant to leave the rendered look unchanged):
 1. Every curve / text object becomes a mesh (evaluated), keeping name, parent, collections, custom properties and
    children. Modifiers on eligible parts are baked.
 2. Texture-space coordinates that depend on the object (Generated / Object) are frozen into per-vertex attributes
    CS_GEN / CS_OBJ and the materials read those attributes instead, so joining objects cannot change a pattern.
 3. Materials that are only constants (Principled with no links) are folded into one palette material PAL_flat: three tiny
    float images (albedo, roughness+metal, emission) sampled with Closest interpolation through a UV layer CS_PAL.
 4. Within each asset (the empty that carries the support-contact properties), parts that share the same material and
    object flags are joined into one mesh. The asset empty, its custom properties, anchors and every object that is
    animated, has children, carries its own properties, lives in a support-checked collection or looks like an
    interactive part stays exactly as it was.
 5. Real-time light roles are written to each light as custom properties (cs_rt_role), nothing else changes.
"""
import collections
import json
import math
import re
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

SUPPORT_COLLECTIONS = ("CS_SUPPORT_REQUIRED", "CS_WALL_DRESSING", "CS_FLOOR_DRESSING", "CS_CEILING_DRESSING")
KEEP_NAME = re.compile(r"(door|hinge|pivot|hatch|gate|lever|button|handle|switch)", re.I)
MOVING_PROPS = ("states", "open_translation_x", "open_translation_y", "open_translation_z", "open_rotation_deg",
                "clear_width_m", "clear_height_m")
BAKE_MODS = {"BEVEL", "WEIGHTED_NORMAL", "SOLIDIFY", "TRIANGULATE", "MIRROR", "ARRAY"}
GEO = ("MESH", "CURVE", "FONT", "SURFACE")
PAL_G = 16


def props(o):
    return {k: o[k] for k in o.keys() if not k.startswith("_") and k != "cycles"}


def _ad_live(ad):
    return bool(ad and (ad.action or ad.drivers or ad.nla_tracks))


def anim(o):
    """True if anything that shapes this object over time is animated, driven or in NLA: the object itself, its data
    block (text body, extrusion, bevel...), or its shape keys. A shape-keyed object is also treated as animated, because
    baking or joining would drop the keys."""
    if _ad_live(o.animation_data):
        return True
    d = getattr(o, "data", None)
    if d is not None:
        if _ad_live(getattr(d, "animation_data", None)):
            return True
        sk = getattr(d, "shape_keys", None)
        if sk is not None:
            return True
    return False


def nearest_asset(o):
    p = o.parent
    while p:
        if props(p):
            return p
        p = p.parent
    return None


def stats(tag):
    dg = bpy.context.evaluated_depsgraph_get()
    n = t = 0
    mats = set()
    slots = 0
    for o in bpy.context.scene.objects:
        if o.type not in GEO or o.hide_render:
            continue
        e = o.evaluated_get(dg)
        try:
            m = e.to_mesh()
        except RuntimeError:
            continue
        t += sum(len(p.vertices) - 2 for p in m.polygons)
        e.to_mesh_clear()
        n += 1
        ms = [s.material for s in o.material_slots if s.material]
        slots += max(1, len(ms))
        mats.update(x.name for x in ms)
    print("OPT %-22s objects %5d  triangles %7d  draw-call estimate %5d  materials in use %4d" % (tag, n, t, slots, len(mats)))
    return {"objects": n, "triangles": t, "draw_call_estimate": slots, "materials_in_use": len(mats)}


# ----------------------------------------------------------------------------------------------------------- step 1
def to_mesh_objects():
    """Curves, surfaces and text become meshes. Returns how many were converted."""
    dg = bpy.context.evaluated_depsgraph_get()
    done = 0
    for o in list(bpy.context.scene.objects):
        if o.type not in ("CURVE", "FONT", "SURFACE") or o.hide_render:
            continue
        if anim(o) or o.constraints:
            continue                       # a mesh copy would freeze its keyframes
        data = o.data
        tex = (Vector(data.texspace_location), Vector(data.texspace_size))
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
        me.name = o.name
        mw = o.matrix_world.copy()
        new = bpy.data.objects.new(o.name + ".tmp", me)
        for c in o.users_collection:
            c.objects.link(new)
        for k, v in props(o).items():
            new[k] = v
        new["_cs_texspace"] = [*tex[0], *tex[1]]
        for attr in ("hide_render", "hide_viewport", "visible_camera", "visible_shadow", "visible_diffuse",
                     "visible_glossy", "visible_transmission", "visible_volume_scatter", "pass_index"):
            setattr(new, attr, getattr(o, attr))
        for ch in list(o.children):
            cm = ch.matrix_world.copy()
            ch.parent = new
            ch.matrix_world = cm
        new.parent = o.parent
        new.matrix_parent_inverse = o.matrix_parent_inverse.copy()
        new.matrix_basis = o.matrix_basis.copy()
        name = o.name
        bpy.data.objects.remove(o, do_unlink=True)
        new.name = name
        done += 1
    return done


def bakeable(o):
    return o.type == "MESH" and o.modifiers and {m.type for m in o.modifiers} <= BAKE_MODS


# ----------------------------------------------------------------------------------------------------------- 2
def texspace_of(o):
    if "_cs_texspace" in o.keys():
        v = o["_cs_texspace"]
        return Vector(v[:3]), Vector(v[3:])
    d = o.data
    return Vector(d.texspace_location), Vector(d.texspace_size)


def add_coord_attributes(o, tex):
    """CS_OBJ = object-space position, CS_GEN = Blender's Generated coordinate (bounding box 0..1 of the ORIGINAL mesh)."""
    me = o.data
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float32)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    loc, size = np.array(tex[0], dtype=np.float32), np.array(tex[1], dtype=np.float32)
    size = np.where(np.abs(size) < 1e-8, 1.0, size)
    gen = (co - loc) / (2.0 * size) + 0.5
    for name, arr in (("CS_OBJ", co), ("CS_GEN", gen)):
        if name in me.attributes:
            me.attributes.remove(me.attributes[name])
        a = me.attributes.new(name, "FLOAT_VECTOR", "POINT")
        a.data.foreach_set("vector", arr.astype(np.float32).ravel())


def rewrite_material_coords(ma):
    """Make a material read CS_OBJ / CS_GEN instead of the object-dependent texture coordinates. Returns True if changed."""
    nt = ma.node_tree
    if nt is None:
        return False
    changed = False
    cache = {}

    def attr_node(name):
        if name not in cache:
            n = nt.nodes.new("ShaderNodeAttribute")
            n.attribute_type = "GEOMETRY"
            n.attribute_name = name
            n.label = name
            cache[name] = n
        return cache[name]

    for n in list(nt.nodes):
        if n.type == "TEX_COORD":
            for out_name, attr in (("Object", "CS_OBJ"), ("Generated", "CS_GEN")):
                out = n.outputs[out_name]
                for lk in list(out.links):
                    target = lk.to_socket
                    nt.links.remove(lk)
                    nt.links.new(attr_node(attr).outputs["Vector"], target)
                    changed = True
        elif n.type in ("TEX_NOISE", "TEX_BRICK", "TEX_VORONOI", "TEX_WAVE", "TEX_MUSGRAVE", "TEX_MAGIC", "TEX_CHECKER",
                        "TEX_GRADIENT"):
            v = n.inputs.get("Vector")
            if v is not None and not v.is_linked:
                nt.links.new(attr_node("CS_GEN").outputs["Vector"], v)
                changed = True
    return changed


def uses_object_coords(ma):
    nt = ma.node_tree
    if nt is None:
        return False
    for n in nt.nodes:
        if n.type == "TEX_COORD" and (n.outputs["Object"].is_linked or n.outputs["Generated"].is_linked):
            return True
        if n.type in ("TEX_NOISE", "TEX_BRICK", "TEX_VORONOI", "TEX_WAVE", "TEX_MUSGRAVE", "TEX_MAGIC", "TEX_CHECKER",
                      "TEX_GRADIENT") and n.inputs.get("Vector") is not None and not n.inputs["Vector"].is_linked:
            return True
    return False


# ----------------------------------------------------------------------------------------------------------- 3
def flat_info(ma):
    """(rgb, rough, metal, emission rgb) if the material is a plain constant Principled, else None."""
    if ma is None or not ma.use_nodes or ma.node_tree is None:
        return None
    nodes = [n for n in ma.node_tree.nodes if n.type != "OUTPUT_MATERIAL"]
    if len(nodes) != 1 or nodes[0].type != "BSDF_PRINCIPLED":
        return None
    p = nodes[0]
    if any(i.is_linked for i in p.inputs):
        return None
    defaults = {"Specular IOR Level": 0.5, "IOR": 1.5, "Coat Weight": 0.0, "Sheen Weight": 0.0,
                "Subsurface Weight": 0.0, "Transmission Weight": 0.0, "Anisotropic": 0.0, "Alpha": 1.0}
    for k, v in defaults.items():
        i = p.inputs.get(k)
        if i is not None and abs(i.default_value - v) > 1e-4:
            return None
    out = [n for n in ma.node_tree.nodes if n.type == "OUTPUT_MATERIAL"]
    if not out or not out[0].inputs["Surface"].is_linked or out[0].inputs["Surface"].links[0].from_node != p:
        return None
    if p.distribution != "MULTI_GGX" or p.subsurface_method != "RANDOM_WALK":
        return None
    bc = tuple(p.inputs["Base Color"].default_value)[:3]
    em = tuple(p.inputs["Emission Color"].default_value)[:3]
    es = p.inputs["Emission Strength"].default_value
    return bc, p.inputs["Roughness"].default_value, p.inputs["Metallic"].default_value, tuple(c * es for c in em)


def build_palette(flat):
    """flat: {material name: info}. Returns (PAL_flat material, {name: cell index})."""
    order = sorted(flat)
    assert len(order) <= PAL_G * PAL_G
    cell = {n: i for i, n in enumerate(order)}
    imgs = {}
    for key in ("albedo", "rough_metal", "emission"):
        img = bpy.data.images.new("PAL_" + key, PAL_G, PAL_G, alpha=False, float_buffer=True, is_data=True)
        img.colorspace_settings.name = "Non-Color"
        px = np.zeros((PAL_G * PAL_G, 4), dtype=np.float32)
        px[:, 3] = 1.0
        for n, i in cell.items():
            bc, r, m, em = flat[n]
            if key == "albedo":
                px[i, :3] = bc
            elif key == "rough_metal":
                px[i, 0], px[i, 1] = r, m
            else:
                px[i, :3] = em
        img.pixels.foreach_set(px.ravel())
        img.file_format = "OPEN_EXR"
        img.pack()
        imgs[key] = img
    ma = bpy.data.materials.new("PAL_flat")
    ma.use_nodes = True
    nt = ma.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    uv = nt.nodes.new("ShaderNodeUVMap")
    uv.uv_map = "CS_PAL"
    pb = nt.nodes.new("ShaderNodeBsdfPrincipled")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(pb.outputs["BSDF"], out.inputs["Surface"])

    def tex(key):
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = imgs[key]
        t.interpolation = "Closest"
        t.extension = "EXTEND"
        nt.links.new(uv.outputs["UV"], t.inputs["Vector"])
        return t

    ta, tr, te = tex("albedo"), tex("rough_metal"), tex("emission")
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(tr.outputs["Color"], sep.inputs["Color"])
    nt.links.new(ta.outputs["Color"], pb.inputs["Base Color"])
    nt.links.new(sep.outputs["Red"], pb.inputs["Roughness"])
    nt.links.new(sep.outputs["Green"], pb.inputs["Metallic"])
    nt.links.new(te.outputs["Color"], pb.inputs["Emission Color"])
    pb.inputs["Emission Strength"].default_value = 1.0
    return ma, cell


def apply_palette(o, pal, cell):
    """Point every polygon that uses a flat material at its palette cell and at the PAL_flat slot. Returns polygons moved."""
    me = o.data
    slots = [s.material for s in o.material_slots]
    flat_slot = {i: cell[m.name] for i, m in enumerate(slots) if m is not None and m.name in cell}
    if not flat_slot:
        return 0
    if "CS_PAL" not in me.uv_layers:
        active = me.uv_layers.active_index if me.uv_layers else None
        render_active = next((i for i, l in enumerate(me.uv_layers) if l.active_render), None)
        layer = me.uv_layers.new(name="CS_PAL")
        if render_active is not None:
            me.uv_layers[render_active].active_render = True
        if active is not None:
            me.uv_layers.active_index = active
    layer = me.uv_layers["CS_PAL"]
    if pal.name not in [m.name for m in me.materials if m]:
        me.materials.append(pal)
    pal_index = [i for i, m in enumerate(me.materials) if m and m.name == pal.name][0]
    npoly, nloop = len(me.polygons), len(me.loops)
    mi = np.empty(npoly, dtype=np.int32)
    me.polygons.foreach_get("material_index", mi)
    ls = np.empty(npoly, dtype=np.int32)
    lt = np.empty(npoly, dtype=np.int32)
    me.polygons.foreach_get("loop_start", ls)
    me.polygons.foreach_get("loop_total", lt)
    uv = np.zeros((nloop, 2), dtype=np.float32)
    cur = np.empty(nloop * 2, dtype=np.float32)
    layer.uv.foreach_get("vector", cur)
    uv[:] = cur.reshape(-1, 2)
    moved = 0
    for p in range(npoly):
        c = flat_slot.get(int(mi[p]))
        if c is None:
            continue
        uv[ls[p]:ls[p] + lt[p]] = ((c % PAL_G + 0.5) / PAL_G, (c // PAL_G + 0.5) / PAL_G)
        mi[p] = pal_index
        moved += 1
    layer.uv.foreach_set("vector", uv.ravel())
    me.polygons.foreach_set("material_index", mi)
    return moved


def drop_unused_slots(o):
    """Remove material slots no polygon uses (keeps the slot order of the others)."""
    me = o.data
    mi = np.empty(len(me.polygons), dtype=np.int32)
    me.polygons.foreach_get("material_index", mi)
    used = set(int(x) for x in np.unique(mi))
    keep = [i for i in range(len(me.materials)) if i in used]
    if len(keep) == len(me.materials) or not keep:
        return
    mats = [me.materials[i] for i in keep]
    remap = {old: new for new, old in enumerate(keep)}
    mi = np.array([remap[int(x)] for x in mi], dtype=np.int32)
    me.materials.clear()                      # clearing resets polygon indices, so set them afterwards
    for m in mats:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", mi)
    me.update()


# ----------------------------------------------------------------------------------------------------------- 4
def asset_is_fixed(asset, kids):
    if any(k in asset.keys() for k in MOVING_PROPS) or KEEP_NAME.search(asset.name):
        return "moving/interactive asset"
    p = asset
    while p:
        if anim(p) or p.constraints:
            return "animated asset"
        p = p.parent
    return None


SUPPORT_TARGETS = set()


def part_fixed(o):
    if o.name in SUPPORT_TARGETS:
        return "support-contact target"
    if props(o):
        return "own properties"
    if o.children:
        return "has children"
    if anim(o) or o.constraints:
        return "animated"
    if any(c.name in SUPPORT_COLLECTIONS for c in o.users_collection):
        return "support-checked collection"
    if KEEP_NAME.search(o.name):
        return "interactive name"
    if o.type != "MESH":
        return "not a mesh"
    if o.modifiers and not {m.type for m in o.modifiers} <= BAKE_MODS:
        return "modifier"
    if o.hide_render or o.hide_viewport:
        return "hidden"
    return None


def flags(o):
    return (o.visible_camera, o.visible_shadow, o.visible_diffuse, o.visible_glossy, o.visible_transmission,
            o.visible_volume_scatter, o.is_shadow_catcher, o.is_holdout, o.pass_index, o.display_type,
            tuple(c.name for c in o.users_collection))


def main():
    a = sys.argv[sys.argv.index("--") + 1:]
    src, dst = a[0], a[1]
    rep_path = a[2] if len(a) > 2 else dst.replace(".blend", "_report.json")
    bpy.ops.wm.open_mainfile(filepath=src)
    sc = bpy.context.scene
    report = {"source": src, "blender": bpy.app.version_string}
    report["before"] = stats("before")

    # objects that a support-contact check points at by name must keep that name (validate_contacts.py looks them up)
    for o in bpy.data.objects:
        t = o.get("cs_support_target")
        if isinstance(t, str):
            SUPPORT_TARGETS.add(t)
    print("OPT support-contact targets kept as named objects:", len(SUPPORT_TARGETS))

    # classify before touching anything
    asset_of = {}
    skipped = collections.Counter()
    fixed_assets = {}
    for o in sc.objects:
        if o.type not in GEO or o.hide_render:
            continue
        asset = nearest_asset(o)
        asset_of[o.name] = asset.name if asset else None

    # 1. curves/text -> mesh
    report["curves_text_converted"] = to_mesh_objects()
    print("OPT converted curve/text objects:", report["curves_text_converted"])

    # texspace for everything that will be re-based (captured before modifiers are baked)
    dg = bpy.context.evaluated_depsgraph_get()
    geo = [o for o in sc.objects if o.type == "MESH" and not o.hide_render]
    every_mesh = [o for o in bpy.data.objects if o.type == "MESH"]
    for o in every_mesh:
        if "_cs_texspace" not in o.keys():
            loc, size = texspace_of(o)
            o["_cs_texspace"] = [*loc, *size]

    # materials that depend on object coordinates
    coord_mats = {m.name for m in bpy.data.materials if m.users and uses_object_coords(m)}
    flat = {m.name: flat_info(m) for m in bpy.data.materials if m.users and flat_info(m)}
    print("OPT materials: object-coordinate dependent", len(coord_mats), " constant (palette) ", len(flat))
    report["coord_dependent_materials"] = len(coord_mats)
    report["flat_materials"] = len(flat)

    # 2. bake modifiers on eligible parts, attributes on every mesh that uses an object-coordinate material
    baked = 0
    for o in geo:
        if part_fixed(o) is None and o.modifiers:
            me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
            old = o.data
            o.modifiers.clear()
            o.data = me
            if old.users == 0:
                bpy.data.meshes.remove(old)
            baked += 1
    report["modifiers_baked_on_objects"] = baked
    for o in every_mesh:
        if any(s.material and s.material.name in coord_mats for s in o.material_slots):
            add_coord_attributes(o, texspace_of(o))
    # curve/text objects that were kept (animated or hidden) cannot carry the attributes: they keep an untouched copy
    clones = {}
    for o in bpy.data.objects:
        if o.type in ("CURVE", "FONT", "SURFACE"):
            for slot in o.material_slots:
                if slot.material and slot.material.name in coord_mats:
                    nm = slot.material.name
                    if nm not in clones:
                        clones[nm] = slot.material.copy()
                        clones[nm].name = nm + "__noattr"
                    slot.material = clones[nm]
    report["materials_kept_unrewritten_for_curves_text"] = len(clones)
    for name in coord_mats:
        rewrite_material_coords(bpy.data.materials[name])

    # 3. palette
    pal, cell = build_palette(flat)
    ptxt = bpy.data.texts.new("OPT_PALETTE")
    ptxt.write(json.dumps({"grid": PAL_G, "cells": cell}, indent=1, sort_keys=True))
    moved = 0
    for o in every_mesh:
        moved += apply_palette(o, pal, cell)
        drop_unused_slots(o)
    report["palette_polygons"] = moved
    print("OPT palette polygons:", moved)

    # 4. join parts per asset / material signature / object flags
    groups = collections.defaultdict(list)
    for o in geo:
        why = part_fixed(o)
        asset = nearest_asset(o)
        if why:
            skipped[why] += 1
            continue
        sig = tuple(sorted({s.material.name for s in o.material_slots if s.material}))
        if asset is None:
            # shell / architecture parts outside any asset: join per collection, material and 5 m cell
            c = o.matrix_world @ (sum((Vector(b) for b in o.bound_box), Vector()) / 8.0)
            groups[("", sig, flags(o), (math.floor(c.x / 5), math.floor(c.y / 5), math.floor(c.z / 5)))].append(o)
            continue
        if asset_is_fixed(asset, None):
            skipped["asset: " + asset_is_fixed(asset, None)] += 1
            continue
        groups[(asset.name, sig, flags(o))].append(o)
    merged_manifest = {}
    joined_objects = 0
    n_groups = 0
    for key, objs in groups.items():
        if len(objs) < 2:
            continue
        asset = bpy.data.objects.get(key[0]) if key[0] else None
        for o in objs:
            mw = o.matrix_world.copy()
            o.parent = asset
            o.matrix_world = mw
            # identical attribute / uv sets so the join cannot invent defaults
        names = set()
        for o in objs:
            for l in o.data.uv_layers:
                names.add(l.name)
        for o in objs:
            for nm in names:
                if nm not in o.data.uv_layers:
                    o.data.uv_layers.new(name=nm)
        att = {}
        for o in objs:
            for at in o.data.attributes:
                if at.name in ("CS_OBJ", "CS_GEN"):
                    att[at.name] = True
        for o in objs:
            for nm in att:
                if nm not in o.data.attributes:
                    o.data.attributes.new(nm, "FLOAT_VECTOR", "POINT")
        # align material slots: join keeps the active object's slots and appends the others'
        active = max(objs, key=lambda x: len(x.data.polygons))
        part_names = sorted(o.name for o in objs)
        n_parts = len(objs)
        with bpy.context.temp_override(active_object=active, selected_editable_objects=objs, selected_objects=objs):
            bpy.ops.object.join()
        n_groups += 1
        joined_objects += n_parts
        nm = "%s__merged_%d" % (key[0] or "SHELL_" + (objs[0].users_collection[0].name if objs[0].users_collection else "scene"), n_groups)
        merged_manifest[nm] = part_names
        active.name = nm
        active["cs_merged_parts"] = n_parts
        drop_unused_slots(active)
    report["join_groups"] = n_groups
    report["objects_joined_away"] = joined_objects
    report["skipped"] = dict(skipped)
    print("OPT joined", joined_objects, "objects into", n_groups, "; kept:", dict(skipped))
    txt = bpy.data.texts.new("OPT_MERGE_MANIFEST")
    txt.write(json.dumps(merged_manifest, indent=1, sort_keys=True))

    # 5. light roles (metadata only; no light is changed)
    n_dyn = 0
    for l in (o for o in sc.objects if o.type == "LIGHT"):
        if l.name.startswith(("HALL_light", "SERVICE_light")):
            l["cs_rt_role"], l["cs_rt_group"] = "dynamic_key", "hall_power"
            n_dyn += 1
        elif l.name.startswith("LOCKER_light"):
            l["cs_rt_role"], l["cs_rt_group"] = "baked_plus_emissive_fixture", "locker_power"
        else:
            l["cs_rt_role"], l["cs_rt_group"] = "baked_plus_emissive_fixture", "briefing_and_accents"
    report["lights"] = sum(1 for o in sc.objects if o.type == "LIGHT")
    report["lights_dynamic_key"] = n_dyn

    # cleanup
    for m in list(bpy.data.materials):
        if m.users == 0:
            bpy.data.materials.remove(m)
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)
    report["after"] = stats("after")
    bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True)
    with open(rep_path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    print("OPT saved", dst)


if __name__ == "__main__":
    main()
