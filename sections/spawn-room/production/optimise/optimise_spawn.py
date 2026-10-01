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


# ----------------------------------------------------------------------------------------------------------- 3b
# Material families (design/MATERIAL_BUDGETS.md): materials with the same node graph that differ only in constants become ONE
# material; the constants travel on the mesh (FAM0.. colour attributes, 4 floats each), so the graph, and with it the look,
# stays exactly the same.
SKIP_NODE_PROPS = {"name", "label", "location", "width", "height", "dimensions", "select", "hide", "mute", "show_options",
                   "show_preview", "show_texture", "use_custom_color", "color", "parent", "width_hidden", "bl_idname",
                   "bl_label", "bl_description", "bl_icon", "bl_static_type", "bl_width_default", "bl_width_min",
                   "bl_width_max", "bl_height_default", "bl_height_min", "bl_height_max", "internal_links", "inputs",
                   "outputs", "image_user", "texture_mapping", "color_mapping", "color_ramp", "node_tree", "image",
                   "script", "rna_type", "type"}
RAMP_TYPES = ("TEX_IMAGE",)


def _node_props(n):
    out = {}
    for p in n.bl_rna.properties:
        if p.identifier in SKIP_NODE_PROPS or p.type not in ("BOOLEAN", "INT", "FLOAT", "STRING", "ENUM"):
            continue
        try:
            out[p.identifier] = getattr(n, p.identifier)
        except Exception:
            pass
    return out


def _round(v):
    try:
        return [round(x, 6) for x in v]
    except TypeError:
        return round(v, 6) if isinstance(v, float) else v


def _struct_key(ma):
    nt = ma.node_tree
    nodes = sorted((n.name, n.bl_idname, json.dumps(_node_props(n), sort_keys=True, default=str),
                    len(n.color_ramp.elements) if n.bl_idname == "ShaderNodeValToRGB" else 0,
                    n.image.name if getattr(n, "image", None) else None) for n in nt.nodes)
    links = sorted((l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier) for l in nt.links)
    import hashlib
    return hashlib.md5(json.dumps([nodes, links], default=str).encode()).hexdigest()[:8]


def _params(ma):
    """{(node, kind, id): value} of every unlinked constant input and every colour-ramp stop."""
    P = {}
    for n in ma.node_tree.nodes:
        for i in n.inputs:
            if i.is_linked or not hasattr(i, "default_value") or i.type not in ("VALUE", "INT", "RGBA", "VECTOR", "BOOLEAN"):
                continue
            if not i.enabled:
                continue
            P[(n.name, "in", i.identifier)] = _round(i.default_value)
        if n.bl_idname == "ShaderNodeValToRGB":
            for k, e in enumerate(n.color_ramp.elements):
                P[(n.name, "stop%d" % k, "pos")] = round(e.position, 6)
                P[(n.name, "stop%d" % k, "col")] = _round(e.color)
    return P


def _liftable(ma):
    nt = ma.node_tree
    if nt is None or nt.animation_data:
        return False
    for n in nt.nodes:
        if n.bl_idname == "ShaderNodeValToRGB":
            if len(n.color_ramp.elements) != 2 or n.color_ramp.interpolation not in ("LINEAR", "EASE") \
                    or n.color_ramp.color_mode != "RGB" or n.outputs["Alpha"].is_linked:
                return False
        if n.bl_idname in ("ShaderNodeGroup", "ShaderNodeScript"):
            return False
    return True


def lift_families(every_mesh, report):
    users = collections.Counter()
    for o in every_mesh:
        for slot in o.material_slots:
            if slot.material:
                users[slot.material.name] += 1
    groups = collections.defaultdict(list)
    for ma in bpy.data.materials:
        if users[ma.name] and ma.node_tree and ma.name != "PAL_flat" and "__noattr" not in ma.name and _liftable(ma):
            groups[_struct_key(ma)].append(ma)
    plan = {}                     # material name -> (family material, param row or None)
    fam_manifest = {}
    n_attr_max = 0
    for key, mats in groups.items():
        mats.sort(key=lambda m: -users[m.name])
        if len(mats) < 2:
            continue
        Ps = [_params(m) for m in mats]
        keys = sorted(Ps[0].keys(), key=str)
        varying = [k for k in keys if any(p.get(k) != Ps[0][k] for p in Ps)]
        # stop positions and colour alpha must stay constant; INT/BOOLEAN sockets would need rounding
        if any(k[1].startswith("stop") and k[2] == "pos" for k in varying):
            continue
        first = mats[0]
        sockets = {}
        for n in first.node_tree.nodes:
            for i in n.inputs:
                sockets[(n.name, "in", i.identifier)] = i
        bad = False
        for k in varying:
            if k[1] == "in":
                i = sockets[k]
                if i.type in ("INT", "BOOLEAN"):
                    bad = True
                if i.type == "RGBA" and len({p[k][3] for p in Ps}) > 1:
                    bad = True
            elif k[2] == "col" and len({p[k][3] for p in Ps}) > 1:
                bad = True
        if bad:
            continue
        if not varying:                               # identical materials: just point everything at the first
            for m in mats:
                plan[m.name] = (first, None)
            fam_manifest[first.name] = [m.name for m in mats]
            continue
        # ------- build the family: copy of the biggest member, constants replaced by attribute reads
        fam = first.copy()
        fam.name = "FAM %s" % first.name
        nt = fam.node_tree
        by_name = {n.name: n for n in nt.nodes}
        layout = []                                   # (param key, attribute index, channel, width)
        v3 = [k for k in varying if (k[1] != "in" and k[2] == "col") or (k[1] == "in" and sockets[k].type in ("RGBA", "VECTOR"))]
        sc = [k for k in varying if k not in v3]
        a = 0
        free = []                                     # (attr index, channel) still free
        for k in v3:
            layout.append((k, a, 0, 3))
            free.append((a, 3))
            a += 1
        for k in sc:
            if free:
                ai, ch = free.pop(0)
            else:
                ai, ch = a, 0
                free = [(a, c) for c in (1, 2, 3)]
                a += 1
            layout.append((k, ai, ch, 1))
        n_attr = a
        n_attr_max = max(n_attr_max, n_attr)
        attr_nodes, sep_nodes = {}, {}

        def attr_node(ai):
            if ai not in attr_nodes:
                an = nt.nodes.new("ShaderNodeAttribute")
                an.attribute_type = "GEOMETRY"
                an.attribute_name = "FAM%d" % ai
                an.label = "FAM%d" % ai
                attr_nodes[ai] = an
            return attr_nodes[ai]

        def channel(ai, ch):
            an = attr_node(ai)
            if ch == 3:
                return an.outputs["Alpha"]
            if ai not in sep_nodes:
                sp = nt.nodes.new("ShaderNodeSeparateXYZ")
                nt.links.new(an.outputs["Vector"], sp.inputs["Vector"])
                sep_nodes[ai] = sp
            return sep_nodes[ai].outputs[("X", "Y", "Z")[ch]]

        ramp_cols = {}
        for k, ai, ch, w in layout:
            if k[1] == "in":
                node = by_name[k[0]]
                sock = [i for i in node.inputs if i.identifier == k[2]][0]
                if w == 3:
                    nt.links.new(attr_node(ai).outputs["Vector"], sock)
                else:
                    nt.links.new(channel(ai, ch), sock)
            else:
                ramp_cols[(k[0], k[1])] = (ai, ch)
        # colour ramps -> Map Range (position to 0..1, smoothstep for EASE) + Mix of the two stop colours
        for n in list(nt.nodes):
            if n.bl_idname != "ShaderNodeValToRGB":
                continue
            e0, e1 = n.color_ramp.elements[0], n.color_ramp.elements[1]
            mr = nt.nodes.new("ShaderNodeMapRange")
            mr.data_type = "FLOAT"
            mr.interpolation_type = "SMOOTHSTEP" if n.color_ramp.interpolation == "EASE" else "LINEAR"
            mr.clamp = True
            mr.inputs["From Min"].default_value = e0.position
            mr.inputs["From Max"].default_value = e1.position
            mr.inputs["To Min"].default_value = 0.0
            mr.inputs["To Max"].default_value = 1.0
            fac_in = n.inputs["Fac"]
            if fac_in.is_linked:
                nt.links.new(fac_in.links[0].from_socket, mr.inputs["Value"])
            else:
                mr.inputs["Value"].default_value = fac_in.default_value
            mx = nt.nodes.new("ShaderNodeMix")
            mx.data_type = "RGBA"
            mx.blend_type = "MIX"
            mx.clamp_result = False
            nt.links.new(mr.outputs["Result"], mx.inputs["Factor"])
            for idx, stop in ((6, "stop0"), (7, "stop1")):
                pk = (n.name, stop)
                if pk in ramp_cols:
                    nt.links.new(attr_node(ramp_cols[pk][0]).outputs["Vector"], mx.inputs[idx])
                else:
                    mx.inputs[idx].default_value = (e0 if stop == "stop0" else e1).color
            for lk in list(n.outputs["Color"].links):
                target = lk.to_socket
                nt.links.remove(lk)
                nt.links.new(mx.outputs[2], target)
            nt.nodes.remove(n)
        # parameter rows per member material
        for m, P in zip(mats, Ps):
            row = []
            for k, ai, ch, w in layout:
                v = P[k]
                row.append((ai, ch, w, v if w == 3 else [v]))
            plan[m.name] = (fam, row)
        fam_manifest[fam.name] = [m.name for m in mats]
        fam["cs_family_members"] = json.dumps([m.name for m in mats])
    # ---- write the constants onto the meshes and swap the slots
    moved = 0
    checked = 0
    for o in every_mesh:
        me = o.data
        mats = list(me.materials)
        hit = [i for i, m in enumerate(mats) if m is not None and m.name in plan]
        if not hit:
            continue
        nloop = len(me.loops)
        arrays = {}
        npoly = len(me.polygons)
        mi = np.empty(npoly, dtype=np.int32)
        ls = np.empty(npoly, dtype=np.int32)
        lt = np.empty(npoly, dtype=np.int32)
        me.polygons.foreach_get("material_index", mi)
        me.polygons.foreach_get("loop_start", ls)
        me.polygons.foreach_get("loop_total", lt)
        for ai in range(n_attr_max):
            name = "FAM%d" % ai
            ca = me.color_attributes.get(name) or me.color_attributes.new(name, "FLOAT_COLOR", "CORNER")
            arr = np.zeros((nloop, 4), dtype=np.float32)
            ca.data.foreach_get("color", arr.reshape(-1))
            arrays[ai] = arr
        expected = []
        for p in range(npoly):
            m = mats[int(mi[p])] if int(mi[p]) < len(mats) else None
            if m is None or m.name not in plan or plan[m.name][1] is None:
                continue
            for ai, ch, w, v in plan[m.name][1]:
                arrays[ai][ls[p]:ls[p] + lt[p], ch:ch + w] = np.array(v, dtype=np.float32)[:w]
            expected.append(p)
            moved += 1
        for ai, arr in arrays.items():
            me.color_attributes["FAM%d" % ai].data.foreach_set("color", arr.reshape(-1))
        # read back and compare
        for ai in range(n_attr_max):
            back = np.empty(nloop * 4, dtype=np.float32)
            me.color_attributes["FAM%d" % ai].data.foreach_get("color", back)
            if not np.allclose(back.reshape(-1, 4), arrays[ai], atol=1e-6):
                raise RuntimeError("attribute read-back mismatch on %s FAM%d" % (o.name, ai))
        checked += 1
        # swap slots to the family materials and collapse duplicates
        new = [plan[m.name][0] if (m is not None and m.name in plan) else m for m in mats]
        uniq = []
        for m in new:
            if m not in uniq:
                uniq.append(m)
        idx = [uniq.index(m) for m in new]
        remap = np.array(idx, dtype=np.int32)
        mi2 = remap[np.clip(mi, 0, len(idx) - 1)]
        me.materials.clear()
        for m in uniq:
            me.materials.append(m)
        me.polygons.foreach_set("material_index", mi2)
    report["families"] = {k: v for k, v in sorted(fam_manifest.items())}
    report["family_attributes"] = n_attr_max
    report["family_polygons"] = moved
    print("OPT families:", len(fam_manifest), "built;", moved, "polygons carry constants on", checked, "meshes; FAM attributes:", n_attr_max)
    return fam_manifest


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

    # 3b. material families: same graph, constants on the mesh
    fam_manifest = lift_families(every_mesh, report)
    ftxt = bpy.data.texts.new("OPT_FAMILIES")
    ftxt.write(json.dumps(fam_manifest, indent=1, sort_keys=True))

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

    # 5. light roles (metadata only; no light is changed). Budget as in the reactor control room: at most 6 dynamic lights
    # in view, at most 2 real-time shadow casters; everything else is baked at its rest value, flicker rides on emissives.
    SHADOW = ("HALL_light_01_area", "HALL_light_02_area")
    n_dyn = n_shadow = 0
    for l in (o for o in sc.objects if o.type == "LIGHT"):
        if l.name.startswith(("HALL_light", "SERVICE_light")):
            l["cs_rt_role"], l["cs_rt_group"] = "dynamic_key", "hall_power"
            n_dyn += 1
        elif l.name.startswith("LOCKER_light"):
            l["cs_rt_role"], l["cs_rt_group"] = "baked_plus_emissive_fixture", "locker_power"
        else:
            l["cs_rt_role"], l["cs_rt_group"] = "baked_plus_emissive_fixture", "briefing_and_accents"
        l["cs_rt_shadow"] = l.name in SHADOW
        n_shadow += int(l["cs_rt_shadow"])
    report["lights"] = sum(1 for o in sc.objects if o.type == "LIGHT")
    report["lights_dynamic_key"] = n_dyn
    report["lights_realtime_shadow_casters"] = n_shadow

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
