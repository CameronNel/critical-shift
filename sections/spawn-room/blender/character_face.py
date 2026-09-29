#!/usr/bin/env python3
"""
2D face layers for the crew worker (Blender 5.2 / bpy + Pillow).

The eyes and mouth are flat, transparent PNG decals on thin curved patches that hug the head surface, so a custom
eye or mouth is just another PNG. Nothing needs modelling, and the same layers map onto a Unity cutout/transparent
material with one texture slot per layer.

  python character_face.py            # (re)generate the PNG library in character_faces/

Contract for custom art (transparent background, sRGB):
  eyes_<name>.png   2.44 : 1  (1024 x 420)  both eyes on one image, eye centres at +-0.098 m from the face centre line
  mouth_<name>.png  2.18 : 1  (512 x 235)   mouth centred; the patch is 0.24 m x 0.11 m
"""

import math
import os

import bpy
import bmesh

import character_scout as SC

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "character_faces")

# patch extents in head-local metres (x across, z up relative to the head centre)
EYES = dict(x=0.22, z0=0.02 - 0.09, z1=0.02 + 0.09, nx=22, nz=8)          # 0.44 x 0.18
MOUTH = dict(x=0.12, z0=-0.17, z1=-0.06, nx=12, nz=6)                     # 0.24 x 0.11
LIFT = 0.0015                                                              # keep decals just off the skin
PPM = 2330                                                                 # texture pixels per metre

INK = (24, 22, 30, 255)
WHITE = (255, 255, 255, 255)
IRIS = (36, 40, 92, 255)


def _px(w, h, ext, x, z):
    return ((x + ext["x"]) / (2 * ext["x"]) * w, (ext["z1"] - z) / (ext["z1"] - ext["z0"]) * h)


def make_library(out_dir=DIR):
    from PIL import Image, ImageDraw
    os.makedirs(out_dir, exist_ok=True)
    SS = 2

    def canvas(ext, w):
        h = round(w * (ext["z1"] - ext["z0"]) / (2 * ext["x"]))
        return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0)), w, h

    def save(im, w, h, name):
        im.resize((w, h), Image.LANCZOS).save(os.path.join(out_dir, name))

    def disc(d, ext, w, h, x, z, r, fill):
        cx, cy = _px(w * SS, h * SS, ext, x, z)
        rr = r / (2 * ext["x"]) * w * SS
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=fill)

    def line_w(ext, w, metres):
        return max(2, round(metres / (2 * ext["x"]) * w * SS))

    ez = 0.02
    # ---- eyes ----
    def eyes(name, painter):
        im, w, h = canvas(EYES, 1024)
        d = ImageDraw.Draw(im)
        for s in (-1, 1):
            painter(d, im, w, h, s * 0.098)
        save(im, w, h, "eyes_%s.png" % name)

    def round_eye(d, im, w, h, x):
        disc(d, EYES, w, h, x, ez, 0.078, WHITE)
        disc(d, EYES, w, h, x, ez - 0.004, 0.056, IRIS)
        disc(d, EYES, w, h, x, ez - 0.004, 0.027, INK)
        disc(d, EYES, w, h, x + 0.017 * (1 if x > 0 else -1), ez + 0.022, 0.013, WHITE)

    def dot_eye(d, im, w, h, x):
        disc(d, EYES, w, h, x, ez, 0.042, INK)
        disc(d, EYES, w, h, x + 0.012, ez + 0.014, 0.011, WHITE)

    def happy_eye(d, im, w, h, x):
        cx, cy = _px(w * SS, h * SS, EYES, x, ez - 0.02)
        r = 0.058 / (2 * EYES["x"]) * w * SS
        d.arc((cx - r, cy - r, cx + r, cy + r), 200, 340, fill=INK, width=line_w(EYES, w, 0.02))

    def sleepy_eye(d, im, w, h, x):
        disc(d, EYES, w, h, x, ez, 0.074, WHITE)
        disc(d, EYES, w, h, x, ez - 0.012, 0.054, IRIS)
        disc(d, EYES, w, h, x, ez - 0.012, 0.026, INK)
        cx, cy = _px(w * SS, h * SS, EYES, x, ez + 0.012)              # heavy upper lid: skin-coloured cover is not
        r = 0.082 / (2 * EYES["x"]) * w * SS                           # possible on transparency, so draw a lid line
        d.line((cx - r, cy, cx + r, cy), fill=INK, width=line_w(EYES, w, 0.014))
        d.rectangle((cx - r * 1.02, cy - r, cx + r * 1.02, cy - 1), fill=(0, 0, 0, 0))

    def wide_eye(d, im, w, h, x):
        disc(d, EYES, w, h, x, ez, 0.082, WHITE)
        disc(d, EYES, w, h, x, ez, 0.024, INK)
        disc(d, EYES, w, h, x + 0.010, ez + 0.010, 0.008, WHITE)

    for name, fn in (("round", round_eye), ("dot", dot_eye), ("happy", happy_eye), ("sleepy", sleepy_eye),
                     ("wide", wide_eye)):
        eyes(name, fn)

    # ---- mouths ----
    def mouth(name, painter):
        im, w, h = canvas(MOUTH, 512)
        d = ImageDraw.Draw(im)
        painter(d, w, h)
        save(im, w, h, "mouth_%s.png" % name)

    mz = -0.115
    lw = lambda m: line_w(MOUTH, 512, m)

    def smile(d, w, h):
        pts = [_px(w * SS, h * SS, MOUTH, u * 0.064, mz + 0.02 * u * u - 0.008 - 0.014) for u in [i / 12 * 2 - 1 for i in range(13)]]
        d.line(pts, fill=INK, width=lw(0.013), joint="curve")
        for p in (pts[0], pts[-1]):
            d.ellipse((p[0] - lw(0.013) / 2, p[1] - lw(0.013) / 2, p[0] + lw(0.013) / 2, p[1] + lw(0.013) / 2), fill=INK)

    def grin(d, w, h):
        pts = [_px(w * SS, h * SS, MOUTH, u * 0.08, mz + 0.03 * u * u + 0.012) for u in [i / 16 * 2 - 1 for i in range(17)]]
        low = [_px(w * SS, h * SS, MOUTH, u * 0.08, mz + 0.012 - 0.038 * (1 - u * u)) for u in [1 - i / 16 * 2 for i in range(17)]]
        d.polygon(pts + low, fill=INK)

    def oh(d, w, h):
        cx, cy = _px(w * SS, h * SS, MOUTH, 0, mz)
        rx, ry = 0.028 / 0.24 * w * SS, 0.034 / 0.24 * w * SS
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=INK)

    def flat(d, w, h):
        a, b = _px(w * SS, h * SS, MOUTH, -0.045, mz), _px(w * SS, h * SS, MOUTH, 0.045, mz)
        d.line((a, b), fill=INK, width=lw(0.013))

    def smirk(d, w, h):
        pts = [_px(w * SS, h * SS, MOUTH, -0.05 + i / 12 * 0.10, mz - 0.006 + 0.026 * (i / 12) ** 2 * 1.2 - 0.004 * i / 12) for i in range(13)]
        d.line(pts, fill=INK, width=lw(0.013), joint="curve")

    for name, fn in (("smile", smile), ("grin", grin), ("o", oh), ("flat", flat), ("smirk", smirk)):
        mouth(name, fn)


def _patch(name, ext, path, layer, coll):
    """Curved decal patch that follows the head surface, UV-mapped 1:1 to the texture."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    grid = []
    for j in range(ext["nz"] + 1):
        row = []
        for i in range(ext["nx"] + 1):
            x = -ext["x"] + 2 * ext["x"] * i / ext["nx"]
            z = ext["z1"] - (ext["z1"] - ext["z0"]) * j / ext["nz"]
            y = SC._fy(x, z) + LIFT
            row.append(bm.verts.new((x, y, SC.HZ + z)))
        grid.append(row)
    for j in range(ext["nz"]):
        for i in range(ext["nx"]):
            f = bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
            f.normal_update()
            for loop in f.loops:
                v = loop.vert
                x, z = v.co.x, v.co.z - SC.HZ
                loop[uv].uv = ((x + ext["x"]) / (2 * ext["x"]), (z - ext["z0"]) / (ext["z1"] - ext["z0"]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    o["cs_face_layer"] = layer
    o.data.materials.append(_material(name, path))
    return o


def _material(name, path):
    m = bpy.data.materials.new("FACE_" + name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.name = "FACE_TEXTURE"
    tex.image = bpy.data.images.load(path, check_existing=True)
    tex.image.colorspace_settings.name = "sRGB"
    tex.interpolation = "Linear"
    tex.extension = "CLIP"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = 0.7
    bsdf.inputs["Specular IOR Level"].default_value = 0.15
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = "DITHERED"
    return m


def set_face_texture(obj, path):
    """Swap a decal layer's image, so a custom eye or mouth is one call."""
    node = obj.data.materials[0].node_tree.nodes["FACE_TEXTURE"]
    node.image = bpy.data.images.load(path, check_existing=True)


def build_face(collection, parent, eyes="round", mouth="smile", lod=0):
    """Add the eyes and mouth decal layers under `parent` (the head pivot). Returns (eyes_obj, mouth_obj, tris)."""
    global coll
    coll = collection
    eyes_ext = dict(EYES, nx=14, nz=5) if lod >= 2 else EYES
    mouth_ext = dict(MOUTH, nx=8, nz=4) if lod >= 2 else MOUTH
    e = _patch("FACE_EYES", eyes_ext, os.path.join(DIR, "eyes_%s.png" % eyes), "eyes", coll)
    m = _patch("FACE_MOUTH", mouth_ext, os.path.join(DIR, "mouth_%s.png" % mouth), "mouth", coll)
    for o in (e, m):
        o.parent = parent
    return e, m, sum(len(o.data.polygons) * 2 for o in (e, m))


if __name__ == "__main__":
    make_library()
    print("faces written to", DIR)
