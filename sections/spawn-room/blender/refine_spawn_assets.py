#!/usr/bin/env python3
"""
Spawn Room structural refinement pass (headless, Blender 5.2 / bpy, needs Pillow).

    python refine_spawn_assets.py -- <input.blend> <output.blend>

Run after restyle_cozy_modern.py and before add_cozy_trinkets.py. It:

  * replaces the 449k-triangle tile floor with one plane and a procedural tile material;
  * rebuilds the hanging jackets (about 42k triangles each) and hung towels as clean low-poly cloth;
  * swaps the chalkboard-like briefing display for a real wall TV (and soundbar) whose screen is a
    video-player still generated with Pillow and packed into the .blend;
  * rebuilds every ceiling fixture cleanly (housing plus diffuser, emitter at the diffuser plane, so
    no shadow wedge on the ceiling), removes the fake fill/bounce lights, and gives each room ONE
    fixture type: hall + locker keep linear fixtures, briefing gets pendants (placed by the
    trinket pass) instead of tubes;
  * removes the loose booklet lying on a briefing bench seat.

Idempotent: it always works from the original objects by name and skips what is already gone.
"""

import math
import os
import sys
import tempfile

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cozy_geo import B, mat, tri_count  # noqa: E402
import cozy_props as P  # noqa: E402

REPORT = []


def log(msg):
    REPORT.append(msg)
    print("REFINE", msg)


# ------------------------------------------------------------------ helpers
def delete_tree(obj):
    for c in list(obj.children):
        delete_tree(c)
    bpy.data.objects.remove(obj, do_unlink=True)


def delete_prefix(*prefixes, keep=()):
    n = 0
    names = [o.name for o in bpy.data.objects if o.name.startswith(prefixes) and o.name not in keep]
    for name in names:
        o = bpy.data.objects.get(name)       # may already be gone as a child of an earlier delete
        if o is not None:
            delete_tree(o)
            n += 1
    return n


def world_bbox(objs):
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        if o.type not in ("MESH", "CURVE", "FONT"):
            continue
        for c in o.bound_box:
            p = o.matrix_world @ Vector(c)
            lo = Vector((min(lo.x, p.x), min(lo.y, p.y), min(lo.z, p.z)))
            hi = Vector((max(hi.x, p.x), max(hi.y, p.y), max(hi.z, p.z)))
    return lo, hi


def link_like(new, old_collections):
    """Link into the source object's room/module collections, never the audited CS_* ones."""
    for c in old_collections:
        if c.name.startswith("CS_") or c.name == "Scene Collection":
            continue
        if new.name not in c.objects:
            c.objects.link(new)


def family(prefix):
    return [o for o in bpy.data.objects if o.name == prefix or o.name.startswith(prefix + "_")
            or o.name.startswith(prefix + ".")]


# --------------------------------------------------------------- tile floor
def rebuild_tile_floor():
    obj = bpy.data.objects.get("V_LOCKER_porcelain_tiles")
    if obj is None:
        return
    before = tri_count_eval(obj)
    lo, hi = world_bbox([obj])
    z = 0.004
    mesh = bpy.data.meshes.new("V_LOCKER_porcelain_tiles_plane")
    mesh.from_pydata([(lo.x, lo.y, z), (hi.x, lo.y, z), (hi.x, hi.y, z), (lo.x, hi.y, z)], [], [(0, 1, 2, 3)])
    mesh.update()
    obj.modifiers.clear()
    old = obj.data
    obj.data = mesh
    if old.users == 0:
        bpy.data.meshes.remove(old)
    m = tile_material()
    mesh.materials.append(m)
    log("tile floor: %d -> %d tris" % (before, 2))


def tri_count_eval(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    e = obj.evaluated_get(dg)
    me = e.to_mesh()
    me.calc_loop_triangles()
    n = len(me.loop_triangles)
    e.to_mesh_clear()
    return n


def tile_material():
    m = bpy.data.materials.get("CS_tile_floor") or bpy.data.materials.new("CS_tile_floor")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapn = nt.nodes.new("ShaderNodeMapping")
    mapn.inputs["Scale"].default_value = (10.0, 10.0, 10.0)       # 0.1 m tile pitch
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.offset = 0.0
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = 0.035
    brick.inputs["Mortar Smooth"].default_value = 0.1
    brick.inputs["Bias"].default_value = 0.0
    brick.inputs["Brick Width"].default_value = 1.0
    brick.inputs["Row Height"].default_value = 1.0
    brick.inputs["Color1"].default_value = (0.150, 0.163, 0.215, 1.0)
    brick.inputs["Color2"].default_value = (0.190, 0.205, 0.265, 1.0)
    brick.inputs["Mortar"].default_value = (0.020, 0.022, 0.033, 1.0)
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.25
    bump.inputs["Distance"].default_value = 0.004
    rough = nt.nodes.new("ShaderNodeMapRange")
    rough.inputs["From Min"].default_value = 0.0
    rough.inputs["From Max"].default_value = 1.0
    rough.inputs["To Min"].default_value = 0.9        # grout is matte
    rough.inputs["To Max"].default_value = 0.32       # glazed porcelain
    nt.links.new(coord.outputs["Object"], mapn.inputs["Vector"])
    nt.links.new(mapn.outputs["Vector"], brick.inputs["Vector"])
    nt.links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(brick.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(brick.outputs["Fac"], rough.inputs["Value"])
    nt.links.new(rough.outputs["Result"], bsdf.inputs["Roughness"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


# ------------------------------------------------------- jackets and towels
JACKETS = (
    ("BELONG_01_jacket", "forest"),
    ("BELONG_03_jacket", "navy"),
    ("LIFE_hall_jacket", "khaki"),
    ("V_BRIEF_draped_jacket", "olive"),
)


def rebuild_jackets():
    total_before = total_after = 0
    for prefix, cloth in JACKETS:
        root = bpy.data.objects.get(prefix)
        if root is None or root.get("cs_rebuilt"):
            continue
        parts = [o for o in family(prefix) if o != root]
        if not parts:
            continue
        total_before += sum(tri_count_eval(o) for o in parts if o.type == "MESH")
        lo, hi = world_bbox(parts)
        body = next((o for o in parts if o.name.endswith("_body")), parts[0])
        zip_ = next((o for o in parts if o.name.endswith("_zipper")), None)
        blo, bhi = world_bbox([body])
        centre = (blo + bhi) / 2
        front = Vector((0.0, 1.0, 0.0))
        if zip_ is not None:
            zlo, zhi = world_bbox([zip_])
            d = (zlo + zhi) / 2 - centre
            d.z = 0
            if d.length > 1e-3:
                front = d.normalized()
        yaw = math.atan2(-front.x, front.y)
        origin = Vector((centre.x, centre.y, hi.z - 0.06))
        old_cols = list(body.users_collection)
        for name in [o.name for o in parts]:
            o = bpy.data.objects.get(name)
            if o is not None:
                delete_tree(o)
        obj = P.jacket(cloth).build(prefix + "_new", floor_normalize=False)
        bpy.context.scene.collection.objects.link(obj)
        link_like(obj, [c for c in old_cols if c.name != "Scene Collection"])
        M = Matrix.Translation(origin) @ Matrix.Rotation(yaw, 4, "Z")
        obj.parent = root
        obj.matrix_parent_inverse = root.matrix_world.inverted()
        obj.matrix_world = M
        obj.name = prefix + "_body"
        root["cs_rebuilt"] = True
        total_after += tri_count(obj)
    if total_before:
        log("jackets: %d -> %d tris" % (total_before, total_after))


TOWELS = (
    # (root empty prefix, hook plate name, cloth colour)
    ("LIFE_locker_towel", "LIFE_towel_hook_plate", "sky"),
    ("V_PPE_hung_towel", "V_PPE_side_towel_hook_plate", "blush"),
)


def rebuild_towels():
    centre = Vector((5.0, 4.0, 1.0))                 # locker-room centre: hooks face the room
    for prefix, plate_name, cloth in TOWELS:
        root = bpy.data.objects.get(prefix)
        plate = bpy.data.objects.get(plate_name)
        if root is None or plate is None or root.get("cs_rebuilt"):
            continue
        plo, phi = world_bbox([plate])
        pc = (plo + phi) / 2
        dims = phi - plo
        axis = 0 if dims.x < dims.y else 1            # plate is thin along the wall normal
        n = Vector((0.0, 0.0, 0.0))
        n[axis] = 1.0 if (centre - pc)[axis] > 0 else -1.0
        for name in [o.name for o in family(prefix) if o != root]:
            o = bpy.data.objects.get(name)
            if o is not None:
                delete_tree(o)
        obj = P.hung_towel(cloth).build(prefix + "_new", floor_normalize=False)
        bpy.context.scene.collection.objects.link(obj)
        link_like(obj, [c for c in root.users_collection if c.name != "Scene Collection"])
        xaxis = Vector((0, 0, 1)).cross(n).normalized()
        yaxis = n.cross(xaxis).normalized()
        rot = Matrix((xaxis, yaxis, n)).transposed().to_4x4()
        wall_face = phi[axis] if n[axis] > 0 else plo[axis]
        origin = Vector((pc.x, pc.y, pc.z + 0.02))
        origin[axis] = wall_face
        obj.parent = root
        obj.matrix_parent_inverse = root.matrix_world.inverted()
        obj.matrix_world = Matrix.Translation(origin) @ rot
        obj.name = prefix + "_cloth"
        root["cs_rebuilt"] = True
    # loose draped/cart towels that were crude slabs
    n = delete_prefix("V_LOCKER_draped_", "V_LOCKER_cart_towel")
    if n:
        log("removed %d crude draped/cart towel objects" % n)


# ----------------------------------------------------------------------- TV
def make_screen_image(path):
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1920, 1080
    img = Image.new("RGB", (W, H))
    px = img.load()
    top, bot = (24, 30, 62), (224, 101, 74)
    for y in range(H):
        t = (y / H) ** 1.6
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = col
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((1150, 320, 1490, 660), fill=(255, 214, 140, 255))                 # low sun
    d.ellipse((1120, 290, 1520, 690), fill=(255, 190, 120, 60))
    ink = (26, 32, 58, 255)
    d.polygon([(0, 880), (0, 700), (140, 700), (170, 640), (300, 640), (330, 700), (520, 700),
               (560, 610), (640, 470), (760, 470), (840, 610), (880, 700), (1100, 700), (1130, 760),
               (1400, 760), (1430, 640), (1470, 640), (1500, 760), (1920, 760), (1920, 880)], fill=ink)
    d.polygon([(700, 470), (810, 470), (850, 350), (720, 350)], fill=(40, 48, 84, 255))
    for k in range(6):
        d.rectangle((900 + k * 70, 720, 930 + k * 70, 745), fill=(255, 206, 110, 230))
    d.rectangle((0, 860, W, H), fill=(18, 22, 44, 255))
    bold = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 132)
    med = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 40)
    small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 34)
    d.text((110, 150), "SHIFT", font=bold, fill=(255, 255, 255, 255))
    d.text((110, 285), "BRIEFING", font=bold, fill=(255, 255, 255, 255))
    d.text((116, 450), "PRE-ENTRY ORIENTATION  ·  SECTOR 04", font=med, fill=(255, 222, 190, 255))
    for i, (num, name, on) in enumerate((("01", "PREPARE", False), ("02", "PRODUCE", False), ("03", "RETURN", True))):
        x0 = 110 + i * 300
        d.rounded_rectangle((x0, 540, x0 + 270, 610), radius=35,
                            fill=(255, 255, 255, 235 if on else 70))
        d.text((x0 + 26, 556), f"{num}  {name}", font=small, fill=(24, 30, 62, 255) if on else (255, 255, 255, 255))
    d.ellipse((880, 380, 1040, 540), fill=(255, 255, 255, 60), outline=(255, 255, 255, 230), width=6)
    d.polygon([(936, 420), (936, 500), (1004, 460)], fill=(255, 255, 255, 240))
    d.rounded_rectangle((70, 900, W - 70, 1000), radius=20, fill=(255, 255, 255, 22))
    d.polygon([(120, 930), (120, 970), (156, 950)], fill=(255, 255, 255, 255))
    d.rounded_rectangle((220, 946, 1460, 956), radius=5, fill=(255, 255, 255, 90))
    d.rounded_rectangle((220, 946, 640, 956), radius=5, fill=(224, 101, 74, 255))
    d.ellipse((628, 938, 652, 962), fill=(255, 255, 255, 255))
    d.text((1500, 928), "02:14 / 06:30", font=small, fill=(255, 255, 255, 240))
    d.text((1730, 928), "CC  ⛶", font=small, fill=(255, 255, 255, 200))
    d.text((1500, 60), "CRITICAL SHIFT  TRAINING", font=small, fill=(255, 255, 255, 200))
    img.save(path)


def tv_screen_material(image_path):
    img = bpy.data.images.get("cs_tv_briefing_slide")
    if img is None:
        img = bpy.data.images.load(image_path)
        img.name = "cs_tv_briefing_slide"
        img.pack()
    m = bpy.data.materials.get("CS_tv_screen") or bpy.data.materials.new("CS_tv_screen")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.extension = "CLIP"
    bsdf.inputs["Base Color"].default_value = (0.005, 0.005, 0.008, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.05
    bsdf.inputs["Coat Weight"].default_value = 1.0
    bsdf.inputs["Coat Roughness"].default_value = 0.02
    bsdf.inputs["Emission Strength"].default_value = 1.1
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


def assign_planar_uv(obj, mat_index, w, h, centre=(0.0, 0.0)):
    """Front-projected UVs (local x right, y up) for the faces using one material."""
    me = obj.data
    uv = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        if poly.material_index != mat_index:
            continue
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = ((co.x - centre[0]) / w + 0.5, (co.y - centre[1]) / h + 0.5)


def rebuild_tv():
    if bpy.data.objects.get("BRIEFING_TV_display") is not None:
        return
    removed = delete_prefix("BRIEFING_TV_enclosure", "BRIEFING_TV_progress", "BRIEFING_TV_screen",
                            "BRIEFING_TV_status", "BRIEFING_TV_step", "BRIEFING_TV_subtitle",
                            "BRIEFING_TV_title", "LIFE_TV_")
    img_path = os.path.join(tempfile.gettempdir(), "cs_tv_briefing_slide.png")
    make_screen_image(img_path)
    screen = tv_screen_material(img_path)

    W, H, D = 1.9, 1.07, 0.04
    bezel = mat("ink", 0.25, 0.0)
    b = B()
    b.box((W, H, D), (0, 0, D / 2), bezel, bevel=0.004, seg=2)
    b.box((W - 0.03, H - 0.03, 0.0008), (0, 0.004, D + 0.0004), screen, bevel=0, seg=1)
    b.box((0.02, 0.006, 0.002), (0.0, -H / 2 + 0.013, D + 0.001), mat("coral", 0.4, emit=3.0), bevel=0, seg=1)
    b.box((0.8, 0.5, 0.012), (0, 0, -0.006), mat("charcoal", 0.6, 0.4), bevel=0, seg=1)
    tv = b.build("BRIEFING_TV_display", floor_normalize=False)
    bpy.context.scene.collection.objects.link(tv)
    assign_planar_uv(tv, list(tv.data.materials).index(screen), W - 0.03, H - 0.03, (0.0, 0.004))
    # local x -> world +y, local y -> world +z, local z -> world +x (faces the room)
    rot = Matrix(((0, 0, 1), (1, 0, 0), (0, 1, 0))).to_4x4()
    tv.matrix_world = Matrix.Translation((-7.245, 3.555, 1.94)) @ rot
    link_like(tv, bpy.data.objects["BRIEFING_TV"].users_collection)

    sb = B()
    sb.box((1.1, 0.07, 0.07), (0, 0, 0.035), mat("charcoal", 0.85), bevel=0.012, seg=2)
    sb.box((0.012, 0.004, 0.003), (0.5, 0.0, 0.0705), mat("coral", 0.4, emit=3.0), bevel=0, seg=1)
    bar = sb.build("BRIEFING_TV_soundbar", floor_normalize=False)
    bpy.context.scene.collection.objects.link(bar)
    bar.matrix_world = Matrix.Translation((-7.245, 3.555, 1.335)) @ rot
    link_like(bar, bpy.data.objects["BRIEFING_TV"].users_collection)
    log("TV: removed %d chalkboard parts, added BRIEFING_TV_display (%d tris) + soundbar" % (removed, tri_count(tv)))


# ------------------------------------------------------------------ lighting
FIXTURE_COLOR = {"HALL": (1.0, 0.88, 0.72), "LOCKER": (1.0, 0.78, 0.55), "SERVICE": (1.0, 0.88, 0.72)}
FIXTURE_WATTS = {"HALL": 135.0, "LOCKER": 95.0, "SERVICE": 135.0}


def rebuild_lighting():
    removed = delete_prefix("EEVEE_floor_bounce", "V_LIGHT_")
    # briefing: pendants replace the tube fixtures entirely
    briefing = 0
    for o in [o for o in bpy.data.objects if o.name.startswith("BRIEFING_light_")
              and o.parent is None and o.name.count("_") == 2]:
        delete_tree(o)
        briefing += 1
    rebuilt = 0
    for parent in [o for o in bpy.data.objects if o.type == "EMPTY" and o.parent is None
                   and (o.name.startswith(("HALL_light_", "LOCKER_light_")) or o.name == "SERVICE_light")
                   and o.name.count("_") in (1, 2) and "contact" not in o.name]:
        if parent.get("cs_fixture_rebuilt"):
            continue
        room = parent.name.split("_")[0]
        size_x = 1.2
        for c in parent.children:
            if c.type == "LIGHT":
                size_x = getattr(c.data, "size", size_x)
        for c in list(parent.children):
            if c.type in ("MESH", "LIGHT") or c.name.endswith(("_diffuser", "_backpan")):
                cols = list(c.users_collection)
                bpy.data.objects.remove(c, do_unlink=True)
        L, Wd, Hh = size_x + 0.08, 0.27, 0.055
        fb = B()
        fb.box((L, Wd, Hh), (0, 0, -Hh / 2), mat("white", 0.55, 0.1), bevel=0.006, seg=2)
        fb.box((size_x, 0.2, 0.004), (0, 0, -Hh - 0.001), mat("paper", 0.5, emit=0.0), bevel=0, seg=1)
        fix = fb.build(parent.name + "_fixture", floor_normalize=False)
        # emissive diffuser gets its own warm emission colour
        dm = bpy.data.materials.new("CS_diffuser_" + room)
        dm.use_nodes = True
        db = next(n for n in dm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        db.inputs["Base Color"].default_value = (1, 1, 1, 1)
        db.inputs["Emission Color"].default_value = (*FIXTURE_COLOR[room], 1.0)
        db.inputs["Emission Strength"].default_value = 3.0
        fix.data.materials[1] = dm
        bpy.context.scene.collection.objects.link(fix)
        fix.parent = parent
        fix.matrix_parent_inverse = Matrix.Identity(4)
        fix.location = (0, 0, 0)
        link_like(fix, parent.users_collection)
        ld = bpy.data.lights.new(parent.name + "_area", "AREA")
        ld.shape = "RECTANGLE"
        ld.size, ld.size_y = size_x, 0.2
        ld.spread = math.radians(180)
        ld.energy = FIXTURE_WATTS[room]
        ld.color = FIXTURE_COLOR[room]
        lo = bpy.data.objects.new(parent.name + "_area", ld)
        lo.parent = parent
        lo.location = (0, 0, -Hh - 0.004)
        bpy.context.scene.collection.objects.link(lo)
        parent["cs_fixture_rebuilt"] = True
        rebuilt += 1
    log("lighting: removed %d fill/bounce lights and %d briefing tube fixtures; rebuilt %d fixtures"
        % (removed, briefing, rebuilt))



# ------------------------------------------------------- plants (spec: 0-2 total)
KEEP_PLANTS = ()
DROP_PLANT_ROOTS = ("V_BRIEF_corner_ficus", "V_HALL_staff_ficus", "V_HALL_staff_snake", "V_LOCKER_corner_snake",
                    "V_LOCKER_corner_ficus", "V_BRIEF_table_pothos")
SHELF_ROOTS = ("V_HALL_plant_shelf", "V_LOCKER_green_shelf", "V_LOCKER_peg_shelf")
PLANT_TOKENS = ("_midrib", "pothos", "_leaf", "_vine", "_plant", "_pot", "_soil", "_band", "trailing")


def descendants(root):
    out = []
    for c in root.children:
        out.append(c)
        out.extend(descendants(c))
    return out


def remove_extra_plants():
    """SPAWN spec section 14: plants are 0-2 across the whole section (and were ~1000 objects)."""
    n = 0
    for name in DROP_PLANT_ROOTS:
        o = bpy.data.objects.get(name)
        if o is not None:
            delete_tree(o)
            n += 1
    for name in SHELF_ROOTS:
        root = bpy.data.objects.get(name)
        if root is None:
            continue
        for cname in [c.name for c in descendants(root)]:
            c = bpy.data.objects.get(cname)               # may already be gone with a deleted plant root
            if c is None or any(k in cname for k in ("_deck", "bracket", "towel")):
                continue                                   # the shelf itself, its brackets and towels stay
            if c.type == "EMPTY" and any(k in c.name for k in ("trailing_plant", "peg_plant", "shelf_pothos")):
                delete_tree(c)                             # the plant's registered root goes with its leaves
                n += 1
            elif c.type == "MESH" and any(tok in c.name for tok in PLANT_TOKENS):
                bpy.data.objects.remove(c, do_unlink=True)
                n += 1
    log("plants: removed %d original plant objects (~100k tris); low-poly plants come from the trinket pass" % n)


# ------------------------------------------------ replace lumpy / heavy assets
def replace_props():
    """Swap blob boots/bags/hamper for clean low-poly versions; keep root + contact anchors."""
    def swap(root_name, recipe, orient="long", fit=True, min_s=0.6, max_s=1.4):
        root = bpy.data.objects.get(root_name)
        if root is None or root.get("cs_rebuilt"):
            return 0
        parts = [c for c in descendants(root) if c.type in ("MESH", "CURVE", "FONT")]
        if not parts:
            return 0
        lo, hi = world_bbox(parts)
        dims = hi - lo
        centre = (lo + hi) / 2
        yaw = 0.0
        if orient == "heel":
            heel = next((c for c in parts if "heel_tab" in c.name), None)
            if heel is not None:
                hlo, hhi = world_bbox([heel])
                d = centre - (hlo + hhi) / 2
                d.z = 0
                if d.length > 1e-4:
                    d.normalize()
                    yaw = math.atan2(-d.x, d.y)
        elif orient == "long":
            yaw = 0.0 if dims.x >= dims.y else math.pi / 2
        before = sum(tri_count_eval(c) for c in parts if c.type == "MESH")
        cols = [c for c in root.users_collection if c.name != "Scene Collection"]
        for name in [c.name for c in parts]:
            o = bpy.data.objects.get(name)
            if o is not None:
                bpy.data.objects.remove(o, do_unlink=True)
        obj = recipe().build(root_name + "_mesh", floor_normalize=True)
        s = 1.0
        if fit and obj.dimensions.x > 0:
            # long axis of the new prop lies along its local x; compare in rotated frame
            fx, fy = (dims.x, dims.y) if yaw == 0.0 else (dims.y, dims.x)
            s = min(fx / obj.dimensions.x, fy / max(obj.dimensions.y, 1e-6), dims.z / max(obj.dimensions.z, 1e-6))
            s = max(min_s, min(max_s, s))
        bpy.context.scene.collection.objects.link(obj)
        link_like(obj, cols)
        M = Matrix.Translation((centre.x, centre.y, lo.z)) @ Matrix.Rotation(yaw, 4, "Z") @ Matrix.Diagonal((s, s, s, 1.0))
        obj.parent = root
        obj.matrix_parent_inverse = root.matrix_world.inverted()
        obj.matrix_world = M
        root["cs_rebuilt"] = True
        return before - tri_count(obj)

    saved = 0
    for n in ("PPE_01_work_boot", "PPE_01_work_boot.001", "PPE_02_work_boot", "PPE_02_work_boot.001",
              "PPE_03_work_boot", "PPE_03_work_boot.001", "PPE_04_work_boot", "PPE_04_work_boot.001",
              "LIFE_bench_boot_0", "LIFE_bench_boot_1"):
        saved += swap(n, lambda: P.r_boot("forest"), orient="heel", fit=False)
    saved += swap("LIFE_lunch_bag", lambda: P.r_tote("mustard"))
    saved += swap("BELONG_02_bag", lambda: P.r_tote("denim"))
    saved += swap("BELONG_04_bag", lambda: P.r_tote("coral"))
    saved += swap("V_LOCKER_floor_duffel", lambda: P.r_duffel("forest"))
    saved += swap("LIFE_laundry_hamper", P.r_hamper)
    log("replaced boots/bags/hamper: saved ~%d tris" % saved)

    # wall clock: 15.8k tris of digit meshes -> one clean clock
    clk = bpy.data.objects.get("LIFE_shift_clock")
    if clk is not None and not clk.get("cs_rebuilt"):
        parts = [c for c in descendants(clk) if c.type in ("MESH", "CURVE", "FONT")]
        lo, hi = world_bbox(parts)
        dims = hi - lo
        axis = 0 if dims.x < dims.y else 1                      # thin axis = wall normal
        centre_room = Vector((0.0, 4.6, 1.0))
        n = Vector((0.0, 0.0, 0.0))
        n[axis] = 1.0 if (centre_room - (lo + hi) / 2)[axis] > 0 else -1.0
        wall_face = lo[axis] if n[axis] > 0 else hi[axis]
        before = sum(tri_count_eval(c) for c in parts if c.type == "MESH")
        cols = [c for c in clk.users_collection if c.name != "Scene Collection"]
        for name in [c.name for c in parts]:
            o = bpy.data.objects.get(name)
            if o is not None:
                bpy.data.objects.remove(o, do_unlink=True)
        obj = P.w_clock().build("LIFE_shift_clock_mesh", floor_normalize=False)
        bpy.context.scene.collection.objects.link(obj)
        link_like(obj, cols)
        xaxis = Vector((0, 0, 1)).cross(n).normalized()
        yaxis = n.cross(xaxis).normalized()
        rot = Matrix((xaxis, yaxis, n)).transposed().to_4x4()
        c = (lo + hi) / 2
        origin = Vector((c.x, c.y, c.z))
        origin[axis] = wall_face
        s = max(dims.y, dims.z) / 0.34 if axis == 0 else max(dims.x, dims.z) / 0.34
        obj.parent = clk
        obj.matrix_parent_inverse = clk.matrix_world.inverted()
        obj.matrix_world = Matrix.Translation(origin) @ rot @ Matrix.Diagonal((s, s, s, 1.0))
        clk["cs_rebuilt"] = True
        log("clock: %d -> %d tris" % (before, tri_count(obj)))


# ------------------------------------------------------------------ pegboard
def pegboard_shader():
    root = bpy.data.objects.get("V_LOCKER_pegboard")
    if root is None or root.get("cs_rebuilt"):
        return
    kids = descendants(root)
    holes = [c for c in kids if "_hole" in c.name]
    board = next((c for c in kids if c.name.endswith("_board")), None)
    if not holes or board is None:
        return
    xs = sorted({round(world_bbox([h])[0].x, 3) for h in holes})
    zs = sorted({round(world_bbox([h])[0].z, 3) for h in holes})
    def pitch(v):
        d = [b - a for a, b in zip(v, v[1:]) if b - a > 0.005]
        return sorted(d)[len(d) // 2] if d else 0.06
    px, pz = pitch(xs), pitch(zs)
    for h in holes:
        bpy.data.objects.remove(h, do_unlink=True)
    m = bpy.data.materials.new("CS_pegboard")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mulx = nt.nodes.new("ShaderNodeMath"); mulx.operation = "DIVIDE"; mulx.inputs[1].default_value = px
    mulz = nt.nodes.new("ShaderNodeMath"); mulz.operation = "DIVIDE"; mulz.inputs[1].default_value = pz
    frx = nt.nodes.new("ShaderNodeMath"); frx.operation = "FRACT"
    frz = nt.nodes.new("ShaderNodeMath"); frz.operation = "FRACT"
    cmb = nt.nodes.new("ShaderNodeCombineXYZ")
    sub = nt.nodes.new("ShaderNodeVectorMath"); sub.operation = "SUBTRACT"; sub.inputs[1].default_value = (0.5, 0.5, 0.0)
    ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"
    ramp = nt.nodes.new("ShaderNodeMapRange"); ramp.inputs["From Min"].default_value = 0.11; ramp.inputs["From Max"].default_value = 0.16
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (0.040, 0.030, 0.022, 1.0)     # hole
    mix.inputs["B"].default_value = (0.560, 0.430, 0.290, 1.0)     # birch face
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.6; bump.inputs["Distance"].default_value = 0.004
    L = nt.links.new
    L(coord.outputs["Object"], sep.inputs["Vector"])
    L(sep.outputs["X"], mulx.inputs[0]); L(sep.outputs["Z"], mulz.inputs[0])
    L(mulx.outputs["Value"], frx.inputs[0]); L(mulz.outputs["Value"], frz.inputs[0])
    L(frx.outputs["Value"], cmb.inputs["X"]); L(frz.outputs["Value"], cmb.inputs["Y"])
    L(cmb.outputs["Vector"], sub.inputs[0]); L(sub.outputs["Vector"], ln.inputs[0])
    L(ln.outputs["Value"], ramp.inputs["Value"]); L(ramp.outputs["Result"], mix.inputs["Factor"])
    L(mix.outputs["Result"], bsdf.inputs["Base Color"]); L(ramp.outputs["Result"], bump.inputs["Height"])
    L(bump.outputs["Normal"], bsdf.inputs["Normal"]); L(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = 0.75
    board.data.materials.clear()
    board.data.materials.append(m)
    root["cs_rebuilt"] = True
    log("pegboard: removed %d hole objects, holes are now a shader" % len(holes))


# -------------------------------------------------------------- decimation
def bake_decimate(obj, mode, ratio=0.5, angle=math.radians(4.0)):
    """Apply modifiers + a Decimate pass into the mesh data (planar merges flat plaster relief)."""
    md = obj.modifiers.new("CS_decimate", "DECIMATE")
    if mode == "planar":
        md.decimate_type = "DISSOLVE"
        md.angle_limit = angle
        md.delimit = {"MATERIAL"}
    else:
        md.decimate_type = "COLLAPSE"
        md.ratio = ratio
    bpy.context.view_layer.update()
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    new = bpy.data.meshes.new_from_object(ev)
    obj.modifiers.clear()
    old = obj.data
    obj.data = new
    if old.users == 0:
        bpy.data.meshes.remove(old)


PROTECT = ("INTEGRITY_POD", "POD_", "AIRLOCK", "FACILITY_floor", "V_LOCKER_porcelain_tiles", "BRIEFING_wood_floor")


def decimate_heavy():
    before = sum(tri_count_eval(o) for o in bpy.data.objects if o.type == "MESH" and not o.hide_render)
    n = 0
    for name in [o.name for o in bpy.data.objects if o.type == "MESH"]:
        o = bpy.data.objects.get(name)
        if o is None or o.hide_render or o.name.startswith(("COZY_",) + PROTECT) or o.get("cs_decimated"):
            continue
        t_ = tri_count_eval(o)
        mods = {m.type for m in o.modifiers}
        if t_ > 2000 and "BEVEL" in mods:                      # plaster walls: flat but 2.6k polys of relief
            bake_decimate(o, "planar", angle=math.radians(4.0))
        elif name == "BRIEFING_carpet":
            bake_decimate(o, "planar", angle=math.radians(4.0))
        elif "_leaf" in name and t_ > 100:
            bake_decimate(o, "collapse", ratio=0.4)
        elif name.startswith("LIFE_socket") and t_ > 500:
            bake_decimate(o, "collapse", ratio=0.3)
        elif t_ > 1800:
            bake_decimate(o, "collapse", ratio=max(0.2, 1000.0 / t_))
        else:
            continue
        o["cs_decimated"] = True
        n += 1
    after = sum(tri_count_eval(o) for o in bpy.data.objects if o.type == "MESH" and not o.hide_render)
    log("decimation: %d objects, scene %d -> %d tris" % (n, before, after))



# --------------------------------------------------------------- hall floor
def _lin(hexstr):
    h = hexstr.lstrip("#")
    def c(v):
        v /= 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return tuple(c(int(h[i:i + 2], 16)) for i in (0, 2, 4)) + (1.0,)


def rebuild_hall_floor():
    """One plane + tile shader: warm clay tiles with a whole-tile navy border along the walls."""
    obj = bpy.data.objects.get("FACILITY_floor")
    if obj is None or obj.get("cs_rebuilt"):
        return
    before = tri_count_eval(obj)
    lo, hi = world_bbox([obj])
    z = hi.z
    mesh = bpy.data.meshes.new("FACILITY_floor_plane")
    mesh.from_pydata([(lo.x, lo.y, z), (hi.x, lo.y, z), (hi.x, hi.y, z), (lo.x, hi.y, z)], [], [(0, 1, 2, 3)])
    mesh.update()
    old = obj.data
    obj.data = mesh
    if old.users == 0:
        bpy.data.meshes.remove(old)
    m = bpy.data.materials.get("CS_hall_floor") or bpy.data.materials.new("CS_hall_floor")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    L = nt.links.new
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (2.5, 2.5, 2.5)            # 0.4 m tiles
    def brick(c1, c2, mortar):
        n = nt.nodes.new("ShaderNodeTexBrick")
        n.offset = 0.0
        n.inputs["Scale"].default_value = 1.0
        n.inputs["Brick Width"].default_value = 1.0
        n.inputs["Row Height"].default_value = 1.0
        n.inputs["Mortar Size"].default_value = 0.03
        n.inputs["Mortar Smooth"].default_value = 0.08
        n.inputs["Color1"].default_value = _lin(c1)
        n.inputs["Color2"].default_value = _lin(c2)
        n.inputs["Mortar"].default_value = _lin(mortar)
        L(mp.outputs["Vector"], n.inputs["Vector"])
        return n
    clay = brick("#9A7259", "#8A6650", "#3A2B25")
    navy = brick("#2E3654", "#39426A", "#151A2B")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    absx = nt.nodes.new("ShaderNodeMath"); absx.operation = "ABSOLUTE"
    tile_i = nt.nodes.new("ShaderNodeMath"); tile_i.operation = "MULTIPLY"; tile_i.inputs[1].default_value = 2.5   # x in tiles
    tile_f = nt.nodes.new("ShaderNodeMath"); tile_f.operation = "FLOOR"
    edge = nt.nodes.new("ShaderNodeMath"); edge.operation = "GREATER_THAN"
    edge.inputs[1].default_value = 2.5      # tile column 3+ (|x| >= 1.2 m): a whole-tile border along the walls
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.3; bump.inputs["Distance"].default_value = 0.004
    fmix = nt.nodes.new("ShaderNodeMix"); fmix.data_type = "FLOAT"
    rough = nt.nodes.new("ShaderNodeMapRange")
    rough.inputs["To Min"].default_value = 0.85
    rough.inputs["To Max"].default_value = 0.3
    L(coord.outputs["Object"], mp.inputs["Vector"])
    L(coord.outputs["Object"], sep.inputs["Vector"])
    L(sep.outputs["X"], absx.inputs[0]); L(absx.outputs["Value"], tile_i.inputs[0])
    L(tile_i.outputs["Value"], tile_f.inputs[0]); L(tile_f.outputs["Value"], edge.inputs[0])
    L(edge.outputs["Value"], mix.inputs["Factor"])
    L(clay.outputs["Color"], mix.inputs["A"]); L(navy.outputs["Color"], mix.inputs["B"])
    L(mix.outputs["Result"], bsdf.inputs["Base Color"])
    L(clay.outputs["Fac"], fmix.inputs["A"]); L(navy.outputs["Fac"], fmix.inputs["B"]); L(edge.outputs["Value"], fmix.inputs["Factor"])
    L(fmix.outputs["Result"], bump.inputs["Height"]); L(bump.outputs["Normal"], bsdf.inputs["Normal"])
    L(fmix.outputs["Result"], rough.inputs["Value"]); L(rough.outputs["Result"], bsdf.inputs["Roughness"])
    L(bsdf.outputs["BSDF"], out.inputs["Surface"])
    mesh.materials.append(m)
    obj["cs_rebuilt"] = True
    log("hall floor: %d -> 2 tris, clay tiles with a navy wall border" % before)


# ---------------------------------------------- non-AI poster art (replaces photos)
def make_poster_art(kind, path):
    from PIL import Image, ImageDraw
    if kind == "landscape":
        W, H = 1536, 1024
        img = Image.new("RGB", (W, H))
        px = img.load()
        top, bot = (33, 40, 78), (232, 150, 96)
        for y in range(H):
            t = (y / H) ** 1.3
            col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
            for x in range(W):
                px[x, y] = col
        d = ImageDraw.Draw(img, "RGBA")
        d.ellipse((980, 240, 1340, 600), fill=(255, 226, 170, 255))
        for k, (col, base, amp) in enumerate((((70, 78, 120, 255), 700, 90), ((48, 55, 94, 255), 790, 70), ((30, 36, 66, 255), 880, 50))):
            pts = [(0, H)]
            for x in range(0, W + 1, 96):
                pts.append((x, base - amp * (0.5 + 0.5 * ((x // 96 + k) % 3) / 2)))
            pts.append((W, H))
            d.polygon(pts, fill=col)
        for x0, w_, h_ in ((260, 90, 260), (390, 60, 190), (1180, 80, 230), (1290, 50, 170)):
            d.rectangle((x0, 880 - h_, x0 + w_, 880), fill=(22, 26, 50, 255))
        d.rectangle((0, 880, W, H), fill=(22, 26, 50, 255))
    else:
        W, H = 1024, 1536
        img = Image.new("RGB", (W, H), (43, 51, 80))
        d = ImageDraw.Draw(img, "RGBA")
        d.ellipse((160, 200, 864, 904), fill=(224, 101, 74, 255))
        d.ellipse((300, 340, 724, 764), fill=(227, 162, 47, 255))
        d.ellipse((410, 450, 614, 654), fill=(236, 233, 240, 255))
        d.polygon([(0, 1536), (0, 1120), (330, 900), (620, 1120), (1024, 960), (1024, 1536)], fill=(29, 34, 56, 255))
        d.polygon([(0, 1536), (0, 1300), (420, 1150), (760, 1330), (1024, 1200), (1024, 1536)], fill=(20, 24, 42, 255))
        d.rectangle((0, 60, W, 110), fill=(227, 162, 47, 255))
    img.save(path)


def replace_ai_images():
    """The crew photo and supervisor portrait were AI-generated; swap in flat generated art."""
    swaps = {"commissioning_crew.png": "landscape", "human_contribution.png": "portrait"}
    done = 0
    for old_name, kind in swaps.items():
        old = bpy.data.images.get(old_name)
        if old is None:
            continue
        path = os.path.join(tempfile.gettempdir(), "cs_poster_%s.png" % kind)
        make_poster_art(kind, path)
        new = bpy.data.images.load(path)
        new.name = "cs_poster_art_" + kind
        new.pack()
        for m in bpy.data.materials:
            if m.node_tree:
                for n in m.node_tree.nodes:
                    if n.type == "TEX_IMAGE" and n.image == old:
                        n.image = new
                        done += 1
        old.user_clear()
        bpy.data.images.remove(old)
    if done:
        log("removed AI-generated images; %d texture slots now use generated flat poster art" % done)


def remove_plain_mugs():
    """The original white mugs are plain cylinders; the trinket pass adds properly shaped ones."""
    n = delete_prefix("BRIEFING_mug", "V_BRIEF_mug_", "V_BRIEF_manual_", "V_BRIEF_refreshment_tray",
                       "V_BRIEF_thermal_coffee")
    if n:
        log("removed %d plain white mug roots" % n)


def remove_seat_clutter():
    n = delete_prefix("LIFE_training_booklet")
    if n:
        log("removed %d loose booklet parts from the briefing bench seat" % n)


def main():
    src, dst = sys.argv[sys.argv.index("--") + 1:][:2]
    bpy.ops.wm.open_mainfile(filepath=src)
    rebuild_tile_floor()
    rebuild_hall_floor()
    replace_ai_images()
    rebuild_jackets()
    rebuild_towels()
    rebuild_tv()
    rebuild_lighting()
    remove_seat_clutter()
    remove_plain_mugs()
    remove_extra_plants()
    replace_props()
    pegboard_shader()
    decimate_heavy()
    bpy.ops.wm.save_as_mainfile(filepath=dst, compress=True)


if __name__ == "__main__":
    main()
