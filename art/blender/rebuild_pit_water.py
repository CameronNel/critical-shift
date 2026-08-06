"""Rebuild the standing water under the Gullet Mine's two bridges.

Run inside the live Blender scene.

The mine crosses water twice: a deep ravine carried on a timber deck around
y = 7..16, and a flooded basin crossed on a ballast causeway and post bents
around y = 24..42.  Both crossings previously had either nothing under them or
a hand-placed rectangle that cut straight through the rock.

This script fits each water surface to the cavern instead of guessing at it.
For every point on a grid it drops a ray from head height, passes through
timber, rail and props, and stops at the first rock or ground surface.  The
point is wet when that rock sits below the waterline, so the shoreline lands
exactly where the floor dips under the water and nowhere else - the surface
reaches wall to wall under each bridge, on both sides, and never pokes out
through the tunnel.

The material is a real water shader - dark body, near-mirror specular, ripples
from a seamless CC0 ocean normal map sampled twice at different scales and
angles - with only a faint, uneven glow added on top.
"""

from __future__ import annotations

import random
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector


SEED = 260806


TEXTURES = Path(r"C:\Users\Camer\Games\critical-shift\art\textures\water\proctexture_ocean_cc0\water-ocean-normal-map-1k")
SOURCE = "https://proctexture.com/textures/water/normal-maps/ocean-normal-map"
LICENSE = "CC0-1.0"

COLLECTION = "MinePit_Water"
MATERIAL = "MinePit_Water"
STALE = ("MinePit_RightWater", "MinePitGlow_A", "MinePitGlow_B",
         "MinePit_RavineGlow", "MinePit_TrestleGlow", "MinePit_CC0_OceanWater")

# Surfaces the ray must stop on.  Everything else - timber, rail, ballast,
# rope, ore - is bridge or clutter and gets passed through, so the water still
# forms directly underneath a deck.
ROCK = {"cave_001", "earth_001", "capRock_001", "darkRock_001", "rock_001"}

CELL = 0.14
PROBE_Z = 2.5

# Each body carries its own dim lights.  EEVEE will not bounce the surface's
# emission onto the rock on its own, so without these the glow stops dead at
# the waterline and reads as a decal rather than as light in the pit.
BODIES = (
    # name, waterline, search box, (glow position, watts) ...
    ("MinePit_RavineWater", -8.35, (-25.5, -15.0, 6.0, 17.5),
     (((-22.7, 11.0, -7.5), 34.0), ((-17.1, 12.0, -7.5), 30.0))),
    ("MinePit_TrestleWater", -0.52, (-19.5, -9.0, 23.0, 43.0),
     (((-16.3, 28.5, -0.15), 13.0), ((-11.9, 36.0, -0.15), 13.0))),
)


# ---------------------------------------------------------------- material


def load_image(filename, noncolor=False):
    image = bpy.data.images.load(str(TEXTURES / filename), check_existing=True)
    image.filepath = bpy.path.relpath(str(TEXTURES / filename))
    if noncolor:
        image.colorspace_settings.name = "Non-Color"
    return image


def water_material():
    mat = bpy.data.materials.get(MATERIAL) or bpy.data.materials.new(MATERIAL)
    mat["source"] = SOURCE
    mat["license"] = LICENSE
    mat.use_nodes = True
    mat.node_tree.nodes.clear()
    n, l = mat.node_tree.nodes, mat.node_tree.links

    out = n.new("ShaderNodeOutputMaterial")
    out.location = (720, 0)
    bsdf = n.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (420, 0)

    # Standing water in an unlit drift is a dark mirror.  It is not a
    # transmissive pane: with nothing lit under the surface, transmission only
    # lets EEVEE fill the whole sheet with flat probe colour, which is what
    # made the first attempt read as glowing milk.  Keeping it opaque and
    # nearly black means the surface shows the rock, the lamps and the ripples
    # instead of showing itself.
    bsdf.inputs["Base Color"].default_value = (0.008, 0.020, 0.022, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.055
    bsdf.inputs["IOR"].default_value = 1.333
    bsdf.inputs["Transmission Weight"].default_value = 0.0
    bsdf.inputs["Alpha"].default_value = 1.0
    bsdf.inputs["Specular IOR Level"].default_value = 0.5

    # World-space coordinates so both bodies ripple at the same physical scale.
    geo = n.new("ShaderNodeNewGeometry")
    geo.location = (-1180, -200)

    def ripple(scale, rotation, y):
        mapping = n.new("ShaderNodeMapping")
        mapping.location = (-940, y)
        mapping.inputs["Scale"].default_value = (scale, scale, scale)
        mapping.inputs["Rotation"].default_value = (0.0, 0.0, rotation)
        tex = n.new("ShaderNodeTexImage")
        tex.location = (-740, y)
        tex.image = load_image("normal.png", noncolor=True)
        tex.extension = "REPEAT"
        l.new(geo.outputs["Position"], mapping.inputs["Vector"])
        l.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        return tex

    # A slow swell, a finer rotated ripple and a long low undulation.  The
    # rotations are what stop a single tiling normal map reading as wallpaper.
    swell = ripple(0.19, 0.0, 300)
    chop = ripple(0.62, 0.82, 60)
    drift = ripple(0.055, 2.06, -180)

    blend = n.new("ShaderNodeMixRGB")
    blend.location = (-500, 200)
    blend.inputs["Fac"].default_value = 0.45
    l.new(swell.outputs["Color"], blend.inputs["Color1"])
    l.new(chop.outputs["Color"], blend.inputs["Color2"])

    blend2 = n.new("ShaderNodeMixRGB")
    blend2.location = (-340, 200)
    blend2.inputs["Fac"].default_value = 0.30
    l.new(blend.outputs["Color"], blend2.inputs["Color1"])
    l.new(drift.outputs["Color"], blend2.inputs["Color2"])

    normal = n.new("ShaderNodeNormalMap")
    normal.location = (-160, 200)
    normal.inputs["Strength"].default_value = 0.62
    l.new(blend2.outputs["Color"], normal.inputs["Color"])
    l.new(normal.outputs["Normal"], bsdf.inputs["Normal"])

    # The glow is patchy rather than a lit sheet: soft noise ramped hard into
    # black so most of the surface stays dark and only drifts come up.  Keep
    # this dim - it is a hint of something in the water, not a light source.
    noise = n.new("ShaderNodeTexNoise")
    noise.location = (-740, -460)
    noise.inputs["Scale"].default_value = 0.42
    noise.inputs["Detail"].default_value = 3.0
    noise.inputs["Roughness"].default_value = 0.55
    l.new(geo.outputs["Position"], noise.inputs["Vector"])

    ramp = n.new("ShaderNodeValToRGB")
    ramp.location = (-500, -460)
    ramp.color_ramp.elements[0].position = 0.52
    ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp.color_ramp.elements[1].position = 0.88
    ramp.color_ramp.elements[1].color = (0.06, 0.34, 0.30, 1.0)
    l.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 0.26

    l.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # EEVEE needs to be told to trace through the surface, and the names for
    # that moved around between releases.
    for attr, value in (("use_raytrace_refraction", True),
                        ("use_screen_refraction", True),
                        ("use_backface_culling", False),
                        ("refraction_depth", 0.0)):
        if hasattr(mat, attr):
            setattr(mat, attr, value)
    return mat


# ---------------------------------------------------------------- geometry


def rock_below(scene, depsgraph, x, y):
    """Depth of the first rock or ground surface under (x, y).

    Timber, rail and props are passed through, so a bridge deck does not hide
    the floor beneath it.
    """
    z = PROBE_Z
    for _ in range(24):
        hit, location, _normal, _index, obj, _matrix = scene.ray_cast(
            depsgraph, Vector((x, y, z)), Vector((0.0, 0.0, -1.0)), distance=60.0)
        if not hit:
            return None
        if obj.name in ROCK:
            return location.z
        if location.z >= z - 1e-4:
            z -= 0.01
        else:
            z = location.z - 0.01
    return None


def build_surface(name, level, x0, x1, y0, y1, collection, material):
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()

    nx = int(round((x1 - x0) / CELL)) + 1
    ny = int(round((y1 - y0) / CELL)) + 1
    wet = [[False] * ny for _ in range(nx)]
    for i in range(nx):
        x = x0 + i * CELL
        for j in range(ny):
            floor = rock_below(scene, depsgraph, x, y0 + j * CELL)
            wet[i][j] = floor is not None and floor < level

    cell = [[wet[i][j] and wet[i + 1][j] and wet[i + 1][j + 1] and wet[i][j + 1]
             for j in range(ny - 1)] for i in range(nx - 1)]

    def interior(i, j):
        """A grid vertex is interior when all four cells touching it are wet."""
        return all(0 <= a < nx - 1 and 0 <= b < ny - 1 and cell[a][b]
                   for a, b in ((i - 1, j - 1), (i, j - 1), (i - 1, j), (i, j)))

    # A grid shoreline cuts in long straight runs that read as polygon edges
    # even under water.  Nudging only the rim vertices sideways breaks those
    # runs into something that passes for a waterline.
    rng = random.Random(SEED)
    verts, index, faces = [], {}, []

    def vertex(i, j):
        key = (i, j)
        if key not in index:
            x, y = x0 + i * CELL, y0 + j * CELL
            if not interior(i, j):
                x += rng.uniform(-0.45, 0.45) * CELL
                y += rng.uniform(-0.45, 0.45) * CELL
            index[key] = len(verts)
            verts.append((x, y, level))
        return index[key]

    for i in range(nx - 1):
        for j in range(ny - 1):
            if cell[i][j]:
                faces.append((vertex(i, j), vertex(i + 1, j),
                              vertex(i + 1, j + 1), vertex(i, j + 1)))

    if not faces:
        raise RuntimeError("no wet cells found for %s at z=%.2f" % (name, level))

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    mesh.materials.append(material)

    # A hard quad grid reflects in bands; smooth shading lets the normal map
    # own the surface.
    bm = bmesh.new()
    bm.from_mesh(mesh)
    for face in bm.faces:
        face.smooth = True
    bm.to_mesh(mesh)
    bm.free()

    old = bpy.data.objects.get(name)
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj, len(faces)


def glow_light(name, location, energy, radius, collection):
    old = bpy.data.objects.get(name)
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)
    light = bpy.data.lights.new(name, "POINT")
    light.energy = energy
    light.color = (0.30, 0.86, 0.78)
    light.shadow_soft_size = radius
    obj = bpy.data.objects.new(name, light)
    obj.location = location
    collection.objects.link(obj)
    return obj


# ---------------------------------------------------------------- entry


def main():
    scene = bpy.context.scene

    for name in STALE:
        obj = bpy.data.objects.get(name)
        if obj is not None:
            bpy.data.objects.remove(obj, do_unlink=True)
        mat = bpy.data.materials.get(name)
        if mat is not None:
            bpy.data.materials.remove(mat)

    # The imported asset ships a coarse stand-in pool; the fitted surfaces
    # replace it, and two water planes 100 mm apart would fight each other.
    stand_in = bpy.data.objects.get("water_001")
    if stand_in is not None:
        stand_in.hide_viewport = True
        stand_in.hide_render = True

    collection = bpy.data.collections.get(COLLECTION)
    if collection is None:
        collection = bpy.data.collections.new(COLLECTION)
        scene.collection.children.link(collection)

    material = water_material()

    if hasattr(scene.eevee, "use_raytracing"):
        scene.eevee.use_raytracing = True

    report = []
    for name, level, (x0, x1, y0, y1), glows in BODIES:
        obj, faces = build_surface(name, level, x0, x1, y0, y1, collection, material)
        stem = name.replace("Water", "Glow")
        for index, (position, energy) in enumerate(glows, start=1):
            glow_light("%s_%02d" % (stem, index), position, energy, 3.5, collection)
        report.append("%s: %d quads, %.1f m2 at z=%.2f"
                      % (name, faces, sum(f.area for f in obj.data.polygons), level))
    return report


__result__ = main()
