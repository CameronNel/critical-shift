"""Owner-reference hazmat styling, using the existing worker and equip contract.

Metres, feet at z=0, +Y forward. The unseen back is an authored continuation of
the supplied front-three-quarter image. This is editable hero authoring geometry,
not a rigged, budgeted, or engine-validated delivery mesh.
"""

import math
from pathlib import Path

import bpy
from mathutils import Vector

import character_face as CF
import character_scout as SC
import character_worker as CW
from cozy_geo import B, tri_count

TAU = 2 * math.pi
ASSETS = Path(__file__).parent / "character_faces"


def material(name, color, roughness, metallic=0, grain=0, fabric=False):
    import character_suit as CS

    m = CS._m(color, roughness, metallic).copy()
    m.name = "HZ01_" + name
    nt = m.node_tree
    bs = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    if fabric:
        bs.inputs["Sheen Weight"].default_value = 0.24
        bs.inputs["Sheen Roughness"].default_value = 0.7
        bs.inputs["Coat Weight"].default_value = 0.06
        bs.inputs["Coat Roughness"].default_value = 0.4
        bs.inputs["Specular IOR Level"].default_value = 0.25
        bs.inputs["Sheen Tint"].default_value = bs.inputs["Base Color"].default_value
    if grain:
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.name = "Physical surface grain"
        tex.inputs["Scale"].default_value = 360 if fabric else 460
        tex.inputs["Detail"].default_value = 2.0
        coords = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(coords.outputs["Object"], tex.inputs["Vector"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.30
        bump.inputs["Distance"].default_value = grain
        nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
        ramp = nt.nodes.new("ShaderNodeMapRange")
        ramp.inputs["To Min"].default_value = roughness - 0.08
        ramp.inputs["To Max"].default_value = min(0.95, roughness + 0.12)
        nt.links.new(tex.outputs["Fac"], ramp.inputs["Value"])
        nt.links.new(ramp.outputs["Result"], bs.inputs["Roughness"])
        if fabric:
            tint = nt.nodes.new("ShaderNodeMixRGB")
            tint.blend_type = "MULTIPLY"
            tint.inputs[0].default_value = 0.16
            tint.inputs[1].default_value = bs.inputs["Base Color"].default_value
            nt.links.new(tex.outputs["Fac"], tint.inputs[2])
            nt.links.new(tint.outputs[0], bs.inputs["Base Color"])
    return m


def scuff(m):
    """Sparse embedded surface wear, strongest on the boot's lower toe and sole."""
    nt = m.node_tree
    bs = nt.nodes.get("Principled BSDF")
    coords = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 170
    noise.inputs["Detail"].default_value = 3
    nt.links.new(coords.outputs["Object"], noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.61
    ramp.color_ramp.elements[1].position = 0.77
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    xyz = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coords.outputs["Object"], xyz.inputs[0])
    low = nt.nodes.new("ShaderNodeMapRange")
    low.inputs["From Min"].default_value = 0.025
    low.inputs["From Max"].default_value = 0.2
    low.inputs["To Min"].default_value = 0.30
    low.inputs["To Max"].default_value = 0.025
    nt.links.new(xyz.outputs["Z"], low.inputs["Value"])
    amount = nt.nodes.new("ShaderNodeMath")
    amount.operation = "MULTIPLY"
    nt.links.new(low.outputs["Result"], amount.inputs[0])
    nt.links.new(ramp.outputs[0], amount.inputs[1])
    tint = nt.nodes.new("ShaderNodeMixRGB")
    tint.inputs[1].default_value = bs.inputs["Base Color"].default_value
    tint.inputs[2].default_value = (0.20, 0.175, 0.105, 1)
    nt.links.new(amount.outputs[0], tint.inputs[0])
    nt.links.new(tint.outputs[0], bs.inputs["Base Color"])


def obj(kit, name, parent, coll, covers=()):
    o = kit.build(name, floor_normalize=False)
    coll.objects.link(o)
    o.parent = parent
    o["cs_outfit"] = "hazmat"
    o["cs_covers"] = list(covers)
    return o


def smooth_mesh(o, levels):
    if not levels:
        return
    mod = o.modifiers.new("Hero surface subdivision", "SUBSURF")
    mod.levels = mod.render_levels = levels
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    old = o.data
    o.modifiers.clear()
    o.data = me
    if not old.users:
        bpy.data.meshes.remove(old)


def tube(kit, points, r, m, seg=8):
    if len(points) >= 2:
        kit.tube(points, r, m, seg=seg)


def stitch(kit, points, m, step=0.010, radius=0.00065):
    """Actual short stitches at a physical spacing along a construction seam."""
    carry = 0.0
    for a, b in zip(points, points[1:]):
        a, b = Vector(a), Vector(b)
        d = b - a
        length = d.length
        if length < 1e-7:
            continue
        tangent = d / length
        at = carry
        while at + 0.0035 <= length:
            kit.tube([a + tangent * at, a + tangent * (at + 0.0035)], radius, m, seg=4)
            at += step
        carry = max(0, at - length)


def oval(rx, rz, y, z, n=96):
    return [
        (rx * math.cos(i * TAU / n), y, z + rz * math.sin(i * TAU / n))
        for i in range(n + 1)
    ]


def boot(kit, s, rubber, sole, lod):
    """Rounded toe and shaft with a continuous shaped outsole, no slab plate."""
    n = {0: 64, 1: 40}.get(lod, 24)
    profile = [
        (0.002, 0.100, 0.156, 0.075),
        (0.014, 0.112, 0.174, 0.075),
        (0.026, 0.114, 0.176, 0.075),
        (0.040, 0.111, 0.171, 0.075),
        (0.060, 0.114, 0.168, 0.078),
        (0.085, 0.118, 0.165, 0.076),
        (0.110, 0.111, 0.145, 0.060),
        (0.135, 0.100, 0.113, 0.035),
        (0.162, 0.096, 0.098, 0.018),
        (0.195, 0.096, 0.099, 0.016),
        (0.222, 0.099, 0.102, 0.016),
    ]
    # Smooth profile interpolation creates a dome over the toe, not a sphere
    # punched through an unrelated sole box.
    rings = []
    for z, rx, ry, cy in profile:
        ring = []
        for i in range(n):
            a = i * TAU / n
            ca, sa = math.cos(a), math.sin(a)
            # A soft superellipse gives the broad work-boot toe its squared edges.
            power = 0.78
            x = s * 0.105 + rx * math.copysign(abs(ca) ** power, ca)
            y = cy + ry * math.copysign(abs(sa) ** power, sa)
            ring.append(kit.bm.verts.new((x, y, z)))
        rings.append(ring)
    for j in range(len(rings) - 1):
        idx = kit._idx(sole if j < 2 else rubber)
        for i in range(n):
            f = kit.bm.faces.new(
                (
                    rings[j][i],
                    rings[j][(i + 1) % n],
                    rings[j + 1][(i + 1) % n],
                    rings[j + 1][i],
                )
            )
            f.material_index = idx
            f.smooth = True
    for row in (rings[0], rings[-1]):
        f = kit.bm.faces.new(row)
        f.material_index = kit._idx(sole if row is rings[0] else rubber)


def hood(parent, coll, cloth, rubber, steel, gold, stitch_m, glass, lod):
    rx, ry, rz = 0.325, 0.310, 0.307
    hz = SC.HZ + 0.003
    phi0 = 0.970
    na, nr = {0: (96, 36), 1: (64, 24)}.get(lod, (40, 16))
    shell = B()
    rows = []
    for j in range(nr):
        phi = phi0 + (math.pi - phi0) * j / nr
        row = []
        for i in range(na):
            a = i * TAU / na
            row.append(
                shell.bm.verts.new(
                    (
                        rx * math.sin(phi) * math.cos(a),
                        ry * math.cos(phi),
                        hz + rz * math.sin(phi) * math.sin(a),
                    )
                )
            )
        rows.append(row)
    for j in range(nr - 1):
        for i in range(na):
            f = shell.bm.faces.new(
                (
                    rows[j][i],
                    rows[j][(i + 1) % na],
                    rows[j + 1][(i + 1) % na],
                    rows[j + 1][i],
                )
            )
            f.material_index = shell._idx(cloth)
            f.smooth = True
    pole = shell.bm.verts.new((0, -ry, hz))
    for i in range(na):
        f = shell.bm.faces.new((rows[-1][i], rows[-1][(i + 1) % na], pole))
        f.material_index = shell._idx(cloth)
        f.smooth = True
    made = [obj(shell, "SUIT_HOOD", parent, coll)]
    # Domed thin visor and sealed, concentric rim hardware.
    ox, oz = rx * math.sin(phi0), rz * math.sin(phi0)
    edge_y = ry * math.cos(phi0) + 0.009
    vis = B()
    centre = vis.bm.verts.new((0, edge_y + 0.137, hz))
    rows = []
    for j in range(1, 15 if lod == 0 else 9):
        r = j / (14 if lod == 0 else 8)
        ring = []
        for i in range(na):
            a = i * TAU / na
            ring.append(
                vis.bm.verts.new(
                    (
                        ox * r * math.cos(a),
                        edge_y + 0.137 * (1 - r * r),
                        hz + oz * r * math.sin(a),
                    )
                )
            )
        rows.append(ring)
    for i in range(na):
        f = vis.bm.faces.new((centre, rows[0][i], rows[0][(i + 1) % na]))
        f.material_index = vis._idx(glass)
        f.smooth = True
    for j in range(len(rows) - 1):
        for i in range(na):
            f = vis.bm.faces.new(
                (
                    rows[j][i],
                    rows[j + 1][i],
                    rows[j + 1][(i + 1) % na],
                    rows[j][(i + 1) % na],
                )
            )
            f.material_index = vis._idx(glass)
            f.smooth = True
    v = obj(vis, "SUIT_VISOR", parent, coll)
    solid = v.modifiers.new("2 mm visor wall", "SOLIDIFY")
    solid.thickness = 0.002
    solid.offset = -1
    made.append(v)
    k = B()
    tube(k, oval(ox + 0.011, oz + 0.011, edge_y - 0.008, hz), 0.024, rubber, 12)
    tube(k, oval(ox - 0.010, oz - 0.010, edge_y + 0.012, hz), 0.0045, steel, 8)
    tube(k, oval(ox + 0.024, oz + 0.024, edge_y - 0.007, hz), 0.0028, steel, 6)
    # Eight secured rim segments and recessed screw heads.
    for i in range(8):
        a = (i + 0.18) * TAU / 8
        x = (ox + 0.015) * math.cos(a)
        z = hz + (oz + 0.015) * math.sin(a)
        k.sph(0.011, (x, edge_y + 0.015, z), rubber, scale=(1, 0.45, 1), seg=16, ring=8)
        k.cyl(0.005, 0.002, (x, edge_y + 0.020, z), steel, seg=12, axis="Y")
        tube(
            k,
            [(x - 0.0024, edge_y + 0.023, z), (x + 0.0024, edge_y + 0.023, z)],
            0.0007,
            rubber,
            4,
        )
    # Crown seams and inset stitch lines follow the hood, including its back.
    for a in [math.radians(v) for v in (40, 70, 100, 130, 165, 220, 290)]:
        pts = []
        for i in range(55):
            phi = phi0 + 0.055 + (math.pi - phi0 - 0.16) * i / 54
            pts.append(
                (
                    (rx + 0.003) * math.sin(phi) * math.cos(a),
                    (ry + 0.003) * math.cos(phi),
                    hz + (rz + 0.003) * math.sin(phi) * math.sin(a),
                )
            )
        tube(k, pts, 0.0017, gold, 6)
        if lod < 2:
            a += 0.017
            stitch(
                k,
                [
                    (
                        (rx + 0.004) * math.sin(phi) * math.cos(a),
                        (ry + 0.004) * math.cos(phi),
                        hz + (rz + 0.004) * math.sin(phi) * math.sin(a),
                    )
                    for phi in [
                        phi0 + 0.055 + (math.pi - phi0 - 0.16) * i / 80
                        for i in range(81)
                    ]
                ],
                stitch_m,
            )
    # Small headlamp, not an antenna; black housing, yellow lens and silver rim.
    k.cyl(0.023, 0.059, (0.06, 0.14, hz + rz - 0.007), rubber, seg=32, axis="Y")
    k.cyl(0.020, 0.004, (0.06, 0.201, hz + rz - 0.007), steel, seg=32, axis="Y")
    k.cyl(0.017, 0.003, (0.06, 0.206, hz + rz - 0.007), gold, seg=32, axis="Y")
    lens = material("lamp lens", "#FFF092", 0.22)
    bs = lens.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Emission Color"].default_value = (1, 0.76, 0.12, 1)
    bs.inputs["Emission Strength"].default_value = 1.5
    k.sph(
        0.016, (0.06, 0.211, hz + rz - 0.007), lens, scale=(1, 0.2, 1), seg=24, ring=12
    )
    # Side filter port. A matched rear seal on the hidden side is a design assumption.
    for s in (-1, 1):
        x = s * 0.311
        y = -0.005
        z = hz - 0.13
        k.cyl(0.042, 0.027, (x if s > 0 else x - 0.027, y, z), rubber, seg=40, axis="X")
        k.cyl(
            0.034, 0.009, (s * 0.339 if s > 0 else -0.348, y, z), gold, seg=40, axis="X"
        )
        k.cyl(
            0.023,
            0.005,
            (s * 0.349 if s > 0 else -0.354, y, z),
            steel,
            seg=32,
            axis="X",
        )
        k.cyl(
            0.016,
            0.006,
            (s * 0.354 if s > 0 else -0.360, y, z),
            rubber,
            seg=24,
            axis="X",
        )
    for s in (-1, 1):
        x = s * 0.09
        z = hz - oz - 0.028
        tube(
            k,
            [
                (x, edge_y + 0.002, z + 0.027),
                (x, edge_y + 0.026, z - 0.030),
                (x + s * 0.006, edge_y + 0.027, z - 0.061),
            ],
            0.003,
            rubber,
            8,
        )
        k.sph(
            0.012,
            (x + s * 0.006, edge_y + 0.027, z - 0.064),
            material("red toggles", "#D65035", 0.38),
            scale=(0.75, 0.75, 1),
            seg=20,
            ring=12,
        )
    made.append(obj(k, "SUIT_HOOD_KIT", parent, coll))
    return made


def surface(body, centre, normal, dx, dz, offset=0.002):
    """Project a local plane to the existing coat mesh, preserving its curvature."""
    n = Vector(normal).normalized()
    right = Vector((-n.y, n.x, 0)).normalized()
    origin = Vector(centre) + right * dx + Vector((0, 0, dz)) + n * 1
    hit, p, no, _ = body.ray_cast(origin, -n, distance=2)
    return p + no * offset if hit else Vector(centre) + right * dx + Vector((0, 0, dz))


def patch(body, kit, centre, normal, w, h, m):
    na, nr = 48, 5
    centre_v = kit.bm.verts.new(surface(body, centre, normal, 0, 0, 0.003))
    rows = []
    for j in range(1, nr + 1):
        r = j / nr
        row = []
        for i in range(na):
            a = i * TAU / na
            ca, sa = math.cos(a), math.sin(a)
            x = r * w / 2 * math.copysign(abs(ca) ** 0.42, ca)
            z = r * h / 2 * math.copysign(abs(sa) ** 0.42, sa)
            row.append(kit.bm.verts.new(surface(body, centre, normal, x, z, 0.003)))
        rows.append(row)
    for i in range(na):
        f = kit.bm.faces.new((centre_v, rows[0][i], rows[0][(i + 1) % na]))
        f.material_index = kit._idx(m)
        f.smooth = True
    for j in range(nr - 1):
        for i in range(na):
            f = kit.bm.faces.new(
                (
                    rows[j][i],
                    rows[j + 1][i],
                    rows[j + 1][(i + 1) % na],
                    rows[j][(i + 1) % na],
                )
            )
            f.material_index = kit._idx(m)
            f.smooth = True


def lettering(text, name, body, centre, normal, width, height, m, root, coll):
    font = bpy.data.curves.new(name, "FONT")
    font.body = text
    font.align_x = "CENTER"
    font.align_y = "CENTER"
    font_path = (
        Path(__file__).parent.parent / "assets/fonts/DejaVuSansCondensed-Bold.ttf"
    )
    if font_path.exists():
        font.font = bpy.data.fonts.load(str(font_path), check_existing=True)
    font.resolution_u = 6
    font.extrude = 0
    o = bpy.data.objects.new(name, font)
    coll.objects.link(o)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    for other in bpy.context.selected_objects:
        if other != o:
            other.select_set(False)
    bpy.ops.object.convert(target="MESH")
    me = o.data
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    if not xs:
        return o
    mx = (min(xs) + max(xs)) / 2
    my = (min(ys) + max(ys)) / 2
    sx = width / (max(xs) - min(xs))
    sy = height / (max(ys) - min(ys))
    for v in me.vertices:
        v.co = surface(
            body, centre, normal, (v.co.x - mx) * sx, (v.co.y - my) * sy, 0.0045
        )
    me.materials.append(m)
    o.parent = root
    o["cs_outfit"] = "hazmat"
    o["cs_covers"] = []
    return o


def buckle(kit, centre, w, h, steel, black):
    x, y, z = centre
    for dx in (-w / 2, w / 2):
        kit.box((0.006, 0.012, h), (x + dx, y, z), steel, bevel=0.002, seg=3)
    for dz in (-h / 2, h / 2):
        kit.box((w, 0.012, 0.006), (x, y, z + dz), steel, bevel=0.002, seg=3)
    kit.box((w, 0.014, 0.004), (x, y + 0.002, z), steel, bevel=0.001)


def ribbon(kit, path, w, m):
    """Flat webbing, with a rectangular cross section instead of a round rope."""
    kit.ribbon(
        [(p.y, p.z) for p in path], path[0].x - w / 2, path[0].x + w / 2, 0.006, m
    )


def reference_face(root):
    """Reference eyes share the existing swappable face-decal contract."""
    from PIL import Image, ImageDraw

    ASSETS.mkdir(exist_ok=True)
    eye_path = ASSETS / "eyes_reference.png"
    mouth_path = ASSETS / "mouth_reference.png"
    scale = 3
    ext = CF.EYES
    w = 1024
    h = round(w * (ext["z1"] - ext["z0"]) / (2 * ext["x"]))
    im = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def circle(ext, w, h, x, z, r, color):
        cx, cy = CF._px(w * scale, h * scale, ext, x, z)
        rr = r / (2 * ext["x"]) * w * scale
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=color)

    for s in (-1, 1):
        x = s * 0.101
        ez = 0.019
        circle(ext, w, h, x, ez, 0.080, (244, 242, 234, 255))
        circle(ext, w, h, x + 0.003, ez - 0.004, 0.060, (50, 53, 56, 255))
        circle(ext, w, h, x + 0.001, ez - 0.010, 0.034, (38, 40, 43, 255))
        circle(ext, w, h, x + 0.019, ez + 0.030, 0.013, (255, 255, 249, 255))
    im.resize((w, h), Image.Resampling.LANCZOS).save(eye_path)
    ext = CF.MOUTH
    w = 512
    h = round(w * (ext["z1"] - ext["z0"]) / (2 * ext["x"]))
    im = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [
        CF._px(w * scale, h * scale, ext, u * 0.065, -0.138 + 0.030 * u * u)
        for u in [i / 32 * 2 - 1 for i in range(33)]
    ]
    lw = round(0.012 / (2 * ext["x"]) * w * scale)
    d.line(pts, fill=(42, 43, 39, 255), width=lw, joint="curve")
    for x, y in (pts[0], pts[-1]):
        d.ellipse(
            (x - lw / 2, y - lw / 2, x + lw / 2, y + lw / 2), fill=(42, 43, 39, 255)
        )
    im.resize((w, h), Image.Resampling.LANCZOS).save(mouth_path)
    for o in root.children_recursive:
        if o.get("cs_face_layer") in ("eyes", "mouth"):
            tex = o.data.materials[0].node_tree.nodes.get("FACE_TEXTURE")
            if (
                tex
                and tex.image
                and Path(tex.image.filepath).name
                in ("eyes_round.png", "mouth_smile.png")
            ):
                CF.set_face_texture(
                    o, str(eye_path if o.get("cs_face_layer") == "eyes" else mouth_path)
                )
        if o.name.endswith("_HEAD"):
            o.data.materials.clear()
            o.data.materials.append(material("orange face", "#DB7447", 0.60))
            for v in o.data.vertices:
                v.co.z = SC.HZ + (v.co.z - SC.HZ) * 1.13 - 0.016
                v.co.y += 0.022
                # Keep the skull inside the fabric outside the visor opening.
                v.co.z = max(v.co.z, SC.HZ + 0.003 - 0.307 + 0.015)
                rho = math.hypot(v.co.x / 0.268, (v.co.z - SC.HZ - 0.003) / 0.253)
                if rho > 1 and v.co.y > 0:
                    inside = (
                        1
                        - (v.co.x / 0.325) ** 2
                        - ((v.co.z - SC.HZ - 0.003) / 0.307) ** 2
                    )
                    v.co.y = min(v.co.y, 0.310 * math.sqrt(max(0, inside)) - 0.012)
            smooth_mesh(o, 1)
    for o in root.children_recursive:
        if o.get("cs_face_layer"):
            for v in o.data.vertices:
                v.co.y = (
                    SC._fy(v.co.x, (v.co.z - SC.HZ + 0.016) / 1.13) + CF.LIFT + 0.022
                )


def build_reference(root, coll, colors=None, lod=0):
    import character_suit as CS

    CS.LODF = 1 + int(lod)
    c = dict(
        suit="#E9AD25",
        gloves="#30322F",
        boots="#292B28",
        accent="#D95837",
        pack="#363B38",
    )
    c.update(colors or {})
    cloth = material("yellow coated fabric", c["suit"], 0.54, grain=0.0020, fabric=True)
    glove = material("rubber glove", c["gloves"], 0.66, grain=0.001)
    rubber = material("black seals", "#262A28", 0.43, grain=0.0005)
    boot_m = material("rubber boot", c["boots"], 0.63, grain=0.001)
    scuff(boot_m)
    sole = material("outsole", "#222520", 0.74)
    web = material("woven webbing", "#292C29", 0.72, grain=0.0006)
    steel = material("brushed hardware", "#A1A5A3", 0.30, 0.78)
    gold = material("ochre piping", "#D89B26", 0.47)
    stitch_m = material("cream thread", "#E8CF86", 0.78)
    red = material("safety tabs", c["accent"], 0.48)
    tape = material("reflective tape", "#E9E9D7", 0.30, 0.1)
    pack_m = material("filter pack", c["pack"], 0.74, grain=0.0008)
    glass = material("clear visor", "#EDF2ED", 0.055)
    # Thin-surface visualization: transparency plus Fresnel reflection, with no
    # refraction. It preserves the decal face without double optical images.
    nt = glass.node_tree
    clear = nt.nodes.new("ShaderNodeBsdfTransparent")
    clear.inputs["Color"].default_value = (*c.get("visor", (1.0, 1.0, 1.0)), 1.0)
    reflection = nt.nodes.new("ShaderNodeBsdfAnisotropic")
    reflection.inputs["Roughness"].default_value = 0.065
    fresnel = nt.nodes.new("ShaderNodeFresnel")
    fresnel.inputs["IOR"].default_value = 1.45
    weight = nt.nodes.new("ShaderNodeMath")
    weight.operation = "MULTIPLY"
    nt.links.new(fresnel.outputs[0], weight.inputs[0])
    coords = nt.nodes.new("ShaderNodeTexCoord")
    xyz = nt.nodes.new("ShaderNodeSeparateXYZ")
    clarity = nt.nodes.new("ShaderNodeMapRange")
    clarity.name = "Face-readable reflection falloff"
    clarity.inputs["From Min"].default_value = SC.HZ + 0.035
    clarity.inputs["From Max"].default_value = SC.HZ + 0.160
    clarity.inputs["To Min"].default_value = 0.045
    clarity.inputs["To Max"].default_value = 0.55
    nt.links.new(coords.outputs["Object"], xyz.inputs[0])
    nt.links.new(xyz.outputs["Z"], clarity.inputs["Value"])
    nt.links.new(clarity.outputs["Result"], weight.inputs[1])
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(weight.outputs[0], mix.inputs[0])
    nt.links.new(clear.outputs[0], mix.inputs[1])
    nt.links.new(reflection.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], nt.nodes.get("Material Output").inputs["Surface"])
    glass["cs_transparency_model"] = "thin_surface_no_refraction"
    pivot = next(o for o in root.children if o.name.endswith("_HEAD_PIVOT"))
    body = CS._fabric_body(root, coll, cloth)
    # Reference arms hang closer to the coat; the base worker is preserved underneath.
    for v in body.data.vertices:
        v.co.x *= 0.90
    smooth_mesh(body, 1 if lod < 2 else 0)
    for v in body.data.vertices:
        x, y, z = v.co
        ax = abs(x)
        # Broad cloth compression where the elbow bends and the trouser gathers.
        if ax > 0.215 and 0.70 < z < 1.03:
            phase = math.atan2(y - 0.030, ax - 0.278)
            amount = (
                0.009
                * math.sin(86 * z + 1.2 * math.sin(phase))
                * math.exp(-(((z - 0.83) / 0.115) ** 2))
            )
            amount += (
                0.004
                * math.sin(115 * z + phase)
                * math.exp(-(((z - 0.97) / 0.050) ** 2))
            )
            v.co += v.normal * amount
        elif ax < 0.22 and 0.24 < z < 0.56:
            phase = math.atan2(y - 0.012, ax - 0.094)
            amount = (
                0.004
                * math.sin(79 * z + math.sin(phase))
                * math.exp(-(((z - 0.295) / 0.042) ** 2))
            )
            v.co += v.normal * amount
    body.data.update()
    gloves = CS._shell(
        root, coll, CS.HAND_REGIONS, "SUIT_GLOVES", glove, CS.HAND_REGIONS, 0.015
    )
    for v in gloves.data.vertices:
        v.co.x *= 0.91
    smooth_mesh(gloves, 1 if lod < 2 else 0)
    bk = B()
    for s in (-1, 1):
        boot(bk, s, boot_m, sole, lod)
    boots = obj(bk, "SUIT_BOOTS", root, coll, CS.FOOT_REGIONS)
    smooth_mesh(boots, 1 if lod < 2 else 0)
    pieces = [body, gloves, boots]
    k = B()
    zs = CW.T(0.94)
    # Built cuffs and protective hems, layered at actual wrist/ankle heights.
    for s in (-1, 1):
        hx = s * 0.314
        k.cyl(
            0.090,
            0.057,
            (hx, 0.065, zs - 0.367),
            rubber,
            r2=0.093,
            seg=48 if lod < 2 else 24,
        )
        tube(
            k,
            [
                (hx + 0.094 * math.cos(a), 0.065 + 0.094 * math.sin(a), zs - 0.310)
                for a in [i * TAU / 64 for i in range(65)]
            ],
            0.005,
            cloth,
        )
        tube(
            k,
            [
                (hx + 0.092 * math.cos(a), 0.065 + 0.092 * math.sin(a), zs - 0.367)
                for a in [i * TAU / 64 for i in range(65)]
            ],
            0.0038,
            gold,
        )
        k.box(
            (0.030, 0.014, 0.035),
            (hx + s * 0.021, 0.155, zs - 0.387),
            red,
            bevel=0.003,
            seg=3,
        )
        lx = s * 0.104
        tube(
            k,
            [
                (lx + 0.107 * math.cos(a), 0.016 + 0.103 * math.sin(a), 0.225)
                for a in [i * TAU / 64 for i in range(65)]
            ],
            0.010,
            cloth,
            12,
        )
        ring = CS._ring(body, (lx, 0.012, 0.305), n=80, max_r=0.18)
        tube(k, ring, 0.0065, tape, 8)
        if ring:
            stitch(k, [(p.x, p.y, p.z + 0.012) for p in ring], stitch_m)
        # Local toe-cap stitching and small red side pull tab.
        pts = [
            (lx + 0.105 * math.cos(a), 0.075 + 0.169 * math.sin(a), 0.055)
            for a in [i * math.pi / 48 for i in range(49)]
        ]
        tube(k, pts, 0.0015, gold, 6)
        stitch(k, [(x, y, z + 0.005) for x, y, z in pts], stitch_m)
        k.box(
            (0.027, 0.089, 0.011),
            (lx + s * 0.101, 0.035, 0.148),
            red,
            bevel=0.005,
            seg=3,
        )
        # Knee protection follows the trouser, with stitched borders.
        centre = (s * 0.097, 0, 0.409)
        patch(body, k, centre, (0, 1, 0), 0.096, 0.125, rubber)
        edge = []
        for i in range(65):
            a = i * TAU / 64
            x = 0.044 * math.copysign(abs(math.cos(a)) ** 0.42, math.cos(a))
            z = 0.056 * math.copysign(abs(math.sin(a)) ** 0.42, math.sin(a))
            edge.append(surface(body, centre, (0, 1, 0), x, z, 0.004))
        tube(k, edge, 0.0014, gold, 6)
        stitch(k, edge, stitch_m)
    # Flat waist belt, centred brushed-steel release clasp.
    belt_z = CW.T(0.63)
    belt_rows = []
    for z in (belt_z, belt_z + 0.037):
        row = []
        for i in range(97):
            a = i * TAU / 96
            d = Vector((math.cos(a), math.sin(a), 0))
            p, no = CS._cast(body, (0, 0, z), d, 0.6)
            if p is None:
                raise RuntimeError("Coat belt projection missed its surface")
            row.append(k.bm.verts.new(p + no * 0.010))
        belt_rows.append(row)
    for i in range(96):
        f = k.bm.faces.new(
            (belt_rows[0][i], belt_rows[0][i + 1], belt_rows[1][i + 1], belt_rows[1][i])
        )
        f.material_index = k._idx(web)
        f.smooth = True
    hit, _ = CS._cast(body, (0, 3, belt_z + 0.020), (0, -1, 0))
    if hit:
        k.box(
            (0.069, 0.022, 0.048),
            (0, hit.y + 0.017, belt_z + 0.019),
            steel,
            bevel=0.007,
            seg=4,
        )
        k.box(
            (0.029, 0.006, 0.034),
            (0.008, hit.y + 0.033, belt_z + 0.019),
            rubber,
            bevel=0.002,
        )
        k.box(
            (0.014, 0.007, 0.035),
            (-0.022, hit.y + 0.034, belt_z + 0.019),
            steel,
            bevel=0.002,
        )
    # Centre zipper, flanking stitched storm seams and an actual pull loop.
    z0, z1 = belt_z + 0.048, 1.115
    zipper = CS._line(
        body, [(0, z0 + (z1 - z0) * i / 70, "F") for i in range(71)], 0.003
    )
    tube(k, zipper, 0.005, rubber, 6)
    for s in (-1, 1):
        seam = CS._line(
            body, [(s * 0.014, z0 + (z1 - z0) * i / 70, "F") for i in range(71)], 0.004
        )
        tube(k, seam, 0.0014, gold, 6)
        stitch(k, seam, stitch_m)
    for i, p in enumerate(zipper):
        if i % 2 == 0:
            k.box(
                (0.011, 0.003, 0.0023),
                (p.x, p.y + 0.004, p.z),
                steel,
                bevel=0.0005,
                seg=1,
            )
    if zipper:
        p = zipper[-1]
        buckle(k, (p.x, p.y + 0.010, p.z - 0.019), 0.012, 0.024, steel, rubber)
    # Two broad harness straps that conform to the coat and pass over the shoulder.
    for s in (-1, 1):
        x = s * 0.112
        pts = CS._line(
            body,
            [
                (x, belt_z + 0.015 + i * (1.13 - belt_z - 0.015) / 40, "F")
                for i in range(41)
            ],
            0.015,
        )
        if len(pts) > 3:
            ribbon(k, pts, 0.026, web)
        for dx in (-0.010, 0.010):
            edge = [p + Vector((dx, 0.004, 0)) for p in pts]
            if lod < 2:
                stitch(k, edge, web, step=0.008, radius=0.0007)
        loc, _ = CS._cast(body, (x, 3, 1.020), (0, -1, 0))
        if loc:
            buckle(k, (x, loc.y + 0.028, 1.020), 0.035, 0.035, steel, rubber)
        loc, _ = CS._cast(body, (x, 3, 0.873), (0, -1, 0))
        if loc:
            buckle(k, (x, loc.y + 0.029, 0.873), 0.033, 0.031, steel, rubber)
            k.cyl(
                0.006, 0.010, (x - 0.019, loc.y + 0.019, 0.873), gold, seg=12, axis="Y"
            )
            k.cyl(
                0.006, 0.010, (x + 0.019, loc.y + 0.019, 0.873), gold, seg=12, axis="Y"
            )
        # Webbing tail extends below the belt, with a red keeper and yellow tip.
        tail = CS._line(
            body, [(x, 0.57 + i * 0.16 / 16, "F") for i in range(17)], 0.012
        )
        if len(tail) > 3:
            ribbon(k, tail, 0.022, web)
            p = tail[0]
            k.box((0.026, 0.009, 0.009), (p.x, p.y + 0.005, p.z), cloth, bevel=0.003)
            p = tail[-2]
            k.box((0.029, 0.013, 0.022), (p.x, p.y + 0.005, p.z), red, bevel=0.003)
        # Rear shoulder straps are functional; no decorative hose spaghetti.
        rear = CS._line(
            body, [(x, 0.82 + i * 0.32 / 24, "B") for i in range(25)], 0.012
        )
        if len(rear) > 3:
            ribbon(k, rear, 0.026, web)
        crown = CS._line(
            body,
            [(x, y, "T") for y in [-0.10 + i * 0.22 / 24 for i in range(25)]],
            0.012,
        )
        if len(crown) > 2:
            tube(k, crown, 0.010, web, 6)
    # Small dosimeter on the left of the image, yellow status window, silver clip.
    p, _ = CS._cast(body, (0.112, 3, 0.943), (0, -1, 0))
    if p:
        k.box(
            (0.050, 0.033, 0.071),
            (0.112, p.y + 0.026, 0.944),
            rubber,
            bevel=0.008,
            seg=4,
        )
        k.box(
            (0.029, 0.004, 0.022), (0.112, p.y + 0.046, 0.953), gold, bevel=0.002, seg=3
        )
        k.box((0.033, 0.006, 0.007), (0.112, p.y + 0.045, 0.922), steel, bevel=0.002)
    # Stitching identifies garment construction: shoulder yokes, sleeves and side seams.
    for s in (-1, 1):
        centre = (s * 0.275, 0.025, 0.92)
        for z in (0.927, 0.990):
            centre = (s * 0.255, 0.025, z)
            normal = (s * 0.8, 0.6, 0)
            seam = [
                surface(body, centre, normal, -0.065 + i * 0.13 / 40, 0, 0.003)
                for i in range(41)
            ]
            tube(k, seam, 0.0014, gold, 6)
            if lod < 2:
                stitch(k, [p + Vector((0, 0, 0.005)) for p in seam], stitch_m)
        # Long sleeve panel lines and elbow protection, projected on the curved sleeve.
        side = "SR" if s > 0 else "SL"
        seam = CS._line(
            body, [(0.028, 0.72 + i * 0.29 / 45, side) for i in range(46)], 0.002
        )
        tube(k, seam, 0.0016, gold, 6)
        stitch(k, seam, stitch_m)
        elbow = (s * 0.293, 0.03, 0.817)
        normal = (s * 0.80, 0.60, 0)
        patch(body, k, elbow, normal, 0.085, 0.106, rubber)
        edge = []
        for i in range(65):
            a = i * TAU / 64
            dx = 0.037 * math.copysign(abs(math.cos(a)) ** 0.42, math.cos(a))
            dz = 0.046 * math.copysign(abs(math.sin(a)) ** 0.42, math.sin(a))
            edge.append(surface(body, elbow, normal, dx, dz, 0.005))
        tube(k, edge, 0.0014, gold, 6)
        stitch(k, edge, stitch_m)
        # The sleeve reinforcement carries the reference's simple yellow chevron.
        for tri in [
            [(-0.021, 0.015), (0.022, 0.015), (0.008, -0.001)],
            [(-0.019, 0.005), (-0.002, -0.021), (0.004, -0.003)],
        ]:
            f = k.bm.faces.new(
                [
                    k.bm.verts.new(surface(body, elbow, normal, x, z, 0.006))
                    for x, z in tri
                ]
            )
            f.material_index = k._idx(cloth)
        # Hip-to-ankle seam follows the outside of each leg.
        pts = []
        for i in range(50):
            z = 0.245 + i * 0.40 / 49
            origin = (s * 0.104 + s * 0.4, 0.014, z)
            hit, p, no, _ = body.ray_cast(
                Vector(origin), Vector((-s, 0, 0)), distance=0.4
            )
            if hit:
                pts.append(p + no * 0.003)
        tube(k, pts, 0.0015, gold, 6)
        stitch(k, pts, stitch_m)
    # Compact squared filter pack: visible on the right edge in the supplied view.
    k.box((0.269, 0.121, 0.322), (0, -0.302, 0.930), pack_m, bevel=0.028, seg=6)
    k.box((0.218, 0.019, 0.268), (0, -0.371, 0.935), rubber, bevel=0.018, seg=5)
    for s in (-1, 1):
        k.box(
            (0.054, 0.105, 0.125),
            (s * 0.160, -0.281, 0.810),
            rubber,
            bevel=0.012,
            seg=5,
        )
        k.box(
            (0.028, 0.003, 0.073),
            (s * 0.160, -0.337, 0.810),
            pack_m,
            bevel=0.006,
            seg=3,
        )
    # Real rescue handle at the placing script's existing attachment height (1.19 m).
    tube(
        k,
        [
            (-0.075, -0.244, 1.080),
            (-0.075, -0.252, 1.150),
            (-0.051, -0.256, 1.183),
            (0.051, -0.256, 1.183),
            (0.075, -0.252, 1.150),
            (0.075, -0.244, 1.080),
        ],
        0.009,
        web,
        12,
    )
    kit = obj(k, "SUIT_KIT", root, coll)
    pieces.append(kit)
    # The fabric neck seal covers the extended chin below the open visor. It is
    # part of the garment, so the same seal remains on the empty hanging suit.
    collar = B()
    collar.lathe(
        [
            (0, 1.065),
            (0.14, 1.065),
            (0.18, 1.092),
            (0.18, 1.105),
            (0.17, 1.125),
            (0, 1.125),
        ],
        (0, 0, 0),
        cloth,
        seg=64,
    )
    tube(
        collar,
        [
            (0.175 * math.cos(i * TAU / 96), 0.175 * math.sin(i * TAU / 96), 1.112)
            for i in range(97)
        ],
        0.0016,
        gold,
        6,
    )
    pieces.append(obj(collar, "SUIT_COLLAR", root, coll))
    # Readable sleeve identifier and hazard markings, projected on the fabric.
    for s in (-1, 1):
        normal = (s * 0.80, 0.60, 0)
        centre = (s * 0.253, 0.025, 0.960)
        panel = B()
        edge = []
        for i in range(81):
            a = i * TAU / 80
            ca, sa = math.cos(a), math.sin(a)
            edge.append(
                surface(
                    body,
                    centre,
                    normal,
                    0.065 * math.copysign(abs(ca) ** 0.42, ca),
                    0.046 * math.copysign(abs(sa) ** 0.42, sa),
                    0.0025,
                )
            )
        tube(panel, edge, 0.0016, gold, 6)
        stitch(panel, edge, stitch_m)
        pieces.append(obj(panel, "SUIT_LABEL_SHOULDER_STITCH", root, coll))
        pieces.append(
            lettering(
                "HZ-01",
                "SUIT_LABEL_HZ01",
                body,
                centre,
                normal,
                0.102,
                0.036,
                rubber,
                root,
                coll,
            )
        )
        bars = B()
        for i in range(5):
            cx = -0.041 + i * 0.017
            # Bars are surface-projected narrow quads, not floating text plates.
            points = [
                surface(body, centre, normal, cx + dx, -0.031 + dz, 0.004)
                for dx, dz in [
                    (-0.005, -0.004),
                    (0.005, -0.004),
                    (0.005, 0.004),
                    (-0.005, 0.004),
                ]
            ]
            f = bars.bm.faces.new([bars.bm.verts.new(q) for q in points])
            f.material_index = bars._idx(rubber)
        pieces.append(obj(bars, "SUIT_LABEL_SERIAL", root, coll))
    pieces.append(
        lettering(
            "CAUTION",
            "SUIT_LABEL_CAUTION",
            body,
            (-0.108, 0.008, 0.398),
            (-0.82, 0.58, 0),
            0.070,
            0.013,
            rubber,
            root,
            coll,
        )
    )
    # A leg warning on the side avoids covering the front knee reinforcement.
    pieces.append(
        lettering(
            "BIOHAZARD",
            "SUIT_LABEL_BIOHAZARD",
            body,
            (-0.108, 0.008, 0.377),
            (-0.82, 0.58, 0),
            0.070,
            0.009,
            rubber,
            root,
            coll,
        )
    )
    pieces.append(
        lettering(
            "LEVEL 8",
            "SUIT_LABEL_LEVEL",
            body,
            (-0.108, 0.008, 0.363),
            (-0.82, 0.58, 0),
            0.050,
            0.008,
            rubber,
            root,
            coll,
        )
    )
    # Triangle and a recognizable biohazard insignia above the zipper, between straps.
    icons = B()
    centre = (-0.065, 0, 1.033)
    normal = (0, 1, 0)
    points = [
        surface(body, centre, normal, x, z, 0.0038)
        for x, z in [(-0.022, -0.020), (0.022, -0.020), (0, 0.022), (-0.022, -0.020)]
    ]
    tube(icons, points, 0.0017, rubber, 6)
    for i in range(3):
        a = math.pi / 2 + i * TAU / 3
        cx = 0.008 * math.cos(a)
        cz = 0.008 * math.sin(a)
        pts = [
            surface(
                body,
                centre,
                normal,
                cx + 0.009 * math.cos(t),
                cz + 0.009 * math.sin(t),
                0.004,
            )
            for t in [a + math.pi / 2 + j * math.pi * 1.5 / 32 for j in range(33)]
        ]
        tube(icons, pts, 0.0013, rubber, 6)
    pieces.append(obj(icons, "SUIT_LABEL_BIOHAZARD_CHEST", root, coll))
    pieces += hood(pivot, coll, cloth, rubber, steel, gold, stitch_m, glass, lod)
    reference_face(root)
    root["cs_suit_style"] = "owner-reference-20261001"
    root["cs_suit_reference"] = (
        "Owner-supplied yellow HZ-01 hazmat front-three-quarter image"
    )
    return pieces, sum(tri_count(o) for o in pieces)
