"""Rebuild the shallow pools under the Gullet Mine's two bridges.

Run inside the live Blender scene.

The mine crosses water twice: a timber deck around y = 7..16, and a ballast
causeway on post bents around y = 24..42.  Each crossing should read as a
wadeable pool - a solid bottom, water over it, and nothing else.  The player
has to be able to climb out, so neither pool is deeper than a long step.

Three passes, in order, because each depends on the last:

1. Carve.  As imported, the deck crossing was an 8.6 m shaft dressed with an
   iron platform, two hanging lanterns, ropes and scaffolding.  Everything
   inside the shaft below the new bottom is cut away.  Faces are bisected on
   the carve boundary first, so a post spanning the cut loses only the part
   below it instead of vanishing whole.

2. Floor.  The shaft gets a solid slab, gently uneven so it reads as silt
   rather than as a lid, grown outwards into the rock so no seam opens at the
   wall.  The causeway crossing already has ground under it and gets none.

3. Water.  For every point on a grid a ray drops from head height, passes
   through timber, rail and props, and stops at the first rock, ground or pool
   floor.  The point is wet when that surface sits below the waterline, so the
   shoreline lands exactly where the bottom dips under the water - wall to wall
   under each bridge, on both sides, and never out through the tunnel.

The material is a real water shader - dark body, near-mirror specular, ripples
from a seamless CC0 ocean normal map sampled at three scales and angles - with
only a faint, uneven glow added on top.
"""

from __future__ import annotations

import random
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector, noise


SEED = 260806


TEXTURES = Path(r"C:\Users\Camer\Games\critical-shift\art\textures\water\proctexture_ocean_cc0\water-ocean-normal-map-1k")
SOURCE = "https://proctexture.com/textures/water/normal-maps/ocean-normal-map"
LICENSE = "CC0-1.0"

COLLECTION = "MinePit_Water"
MATERIAL = "MinePit_Water"
FLOOR_MATERIAL = "PBR_rock"
STALE = ("MinePit_RightWater", "MinePitGlow_A", "MinePitGlow_B",
         "MinePit_RavineGlow", "MinePit_TrestleGlow", "MinePit_CC0_OceanWater")

# Surfaces the ray must stop on.  Everything else - timber, rail, ballast,
# rope, ore - is bridge or clutter and gets passed through, so the water still
# forms directly underneath a deck.  Pool floors are added as they are built.
ROCK = {"cave_001", "earth_001", "capRock_001", "darkRock_001", "rock_001"}

# Rock the mine is cut from.  Carving must never touch it or the shaft loses
# its walls along with its clutter.
BEDROCK = ROCK | {"SafetyFloor"}

CELL = 0.14
PROBE_Z = 2.5

# The deck crossing as imported was a shaft 8.6 m deep, furnished most of the
# way down.  Cut everything inside this footprint below the level given; the
# new floor sits just above it, so what survives reads as posts entering the
# bottom rather than as stumps hanging over a void.
CARVE = (("ravine shaft", (-25.2, -15.3, 6.0, 17.2), -1.10),)

# Each body carries its own dim lights.  EEVEE will not bounce the surface's
# emission onto the rock on its own, so without these the glow stops dead at
# the waterline and reads as a decal rather than as light in the pit.
BODIES = (
    # name, waterline, search box, glows, floor (level, thickness) or None
    ("MinePit_RavineWater", -0.55, (-25.5, -15.0, 6.0, 17.5),
     (((-22.6, 10.5, -0.35), 11.0), ((-17.2, 12.5, -0.35), 11.0)),
     (-0.95, 0.60)),
    ("MinePit_TrestleWater", -0.52, (-19.5, -9.0, 23.0, 43.0),
     (((-16.3, 28.5, -0.15), 13.0), ((-11.9, 36.0, -0.15), 13.0)),
     None),
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


# ---------------------------------------------------------------- carving


def carve_below(footprint, cut_z):
    """Delete everything inside *footprint* that sits below *cut_z*.

    Faces are bisected on all five carve planes first.  Without that a post
    running the full height of the shaft has its centre far below the cut and
    would be deleted whole, taking the part above the cut with it.
    """
    x0, x1, y0, y1 = footprint
    planes = (((x0, 0.0, 0.0), (1.0, 0.0, 0.0)),
              ((x1, 0.0, 0.0), (1.0, 0.0, 0.0)),
              ((0.0, y0, 0.0), (0.0, 1.0, 0.0)),
              ((0.0, y1, 0.0), (0.0, 1.0, 0.0)),
              ((0.0, 0.0, cut_z), (0.0, 0.0, 1.0)))

    emptied, cut = [], []
    for obj in list(bpy.context.scene.objects):
        if obj.type != "MESH" or obj.name in BEDROCK or obj.name.startswith("MinePit_"):
            continue
        matrix = obj.matrix_world
        corners = [matrix @ Vector(corner) for corner in obj.bound_box]
        if (min(c.x for c in corners) > x1 or max(c.x for c in corners) < x0
                or min(c.y for c in corners) > y1 or max(c.y for c in corners) < y0
                or min(c.z for c in corners) > cut_z):
            continue  # nowhere near the carve, leave its topology alone

        inverse = matrix.inverted()
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        for point, normal in planes:
            local_point = inverse @ Vector(point)
            local_normal = (matrix.to_3x3().transposed() @ Vector(normal)).normalized()
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
                                   dist=1e-5, plane_co=local_point, plane_no=local_normal)

        doomed = []
        for face in bm.faces:
            centre = matrix @ face.calc_center_median()
            if x0 <= centre.x <= x1 and y0 <= centre.y <= y1 and centre.z <= cut_z:
                doomed.append(face)
        if not doomed:
            bm.free()
            continue

        before = len(bm.faces)
        bmesh.ops.delete(bm, geom=doomed, context="FACES")
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context="VERTS")
        bm.to_mesh(obj.data)
        obj.data.update()
        remaining = len(obj.data.polygons)
        bm.free()

        cut.append("%s -%d" % (obj.name, before - remaining))
        if remaining == 0:
            emptied.append(obj.name)

    for name in emptied:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    return cut, emptied


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


def sample_below(level, x0, x1, y0, y1):
    """Grid of which columns have solid ground below *level*."""
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    nx = int(round((x1 - x0) / CELL)) + 1
    ny = int(round((y1 - y0) / CELL)) + 1
    grid = [[False] * ny for _ in range(nx)]
    for i in range(nx):
        x = x0 + i * CELL
        for j in range(ny):
            floor = rock_below(scene, depsgraph, x, y0 + j * CELL)
            grid[i][j] = floor is not None and floor < level
    return grid, nx, ny


def grow(grid, nx, ny, rings):
    """Dilate a grid so a slab built from it buries its rim in the rock."""
    for _ in range(rings):
        grown = [row[:] for row in grid]
        for i in range(nx):
            for j in range(ny):
                if grid[i][j]:
                    continue
                for a, b in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)):
                    if 0 <= a < nx and 0 <= b < ny and grid[a][b]:
                        grown[i][j] = True
                        break
        grid = grown
    return grid


def build_surface(name, level, x0, x1, y0, y1, collection, material):
    wet, nx, ny = sample_below(level, x0, x1, y0, y1)

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
    return obj, len(faces), (cell, nx, ny, x0, y0)


def build_floor(name, level, thickness, x0, x1, y0, y1, collection):
    """Solid bottom for a carved-out shaft.

    Grown two cells outwards so the slab's rim ends up inside the rock rather
    than beside it, and shaken by a little smooth noise so the bottom reads as
    silt under shallow water instead of as a lid dropped in.
    """
    open_shaft, nx, ny = sample_below(level, x0, x1, y0, y1)
    open_shaft = grow(open_shaft, nx, ny, 2)

    verts, index, faces = [], {}, []

    def vertex(i, j):
        key = (i, j)
        if key not in index:
            x, y = x0 + i * CELL, y0 + j * CELL
            drift = noise.noise(Vector((x * 0.75, y * 0.75, 0.0))) * 0.05
            index[key] = len(verts)
            verts.append((x, y, level + drift))
        return index[key]

    for i in range(nx - 1):
        for j in range(ny - 1):
            if (open_shaft[i][j] and open_shaft[i + 1][j]
                    and open_shaft[i + 1][j + 1] and open_shaft[i][j + 1]):
                faces.append((vertex(i, j), vertex(i + 1, j),
                              vertex(i + 1, j + 1), vertex(i, j + 1)))

    if not faces:
        raise RuntimeError("no open shaft found for %s at z=%.2f" % (name, level))

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    rock = bpy.data.materials.get(FLOOR_MATERIAL)
    if rock is not None:
        mesh.materials.append(rock)

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=-thickness)
    # solidify offsets along the vertex normals, and which way that ends up
    # pointing depends on the winding it inferred.  Measure instead of trusting
    # it: the slab is far thicker than the noise, so a top that has risen by
    # anything like the thickness means it extruded the wrong way.
    if max(v.co.z for v in bm.verts) > level + thickness * 0.5:
        bmesh.ops.translate(bm, verts=bm.verts[:], vec=(0.0, 0.0, -thickness))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    old = bpy.data.objects.get(name)
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    ROCK.add(name)
    return obj, len(faces)


def open_safety_floor(pools):
    """Cut the wet footprints out of the walk-navigation plane.

    SafetyFloor is an invisible plane at z = -0.34 that catches the player in
    Blender's walk mode.  It sits above both waterlines, so with it intact you
    walk across the top of the pools instead of into them and the bottoms may
    as well not exist.

    The hole is the wet footprint itself, not a rectangle around it.  That is
    what makes this safe: a cell is only wet because the ray already found rock
    or pool floor below the waterline there, so every square removed has
    something solid underneath it to land on.  Everywhere else in the search
    box - deck, ballast, bank - keeps its tile.
    """
    obj = bpy.data.objects.get("SafetyFloor")
    if obj is None:
        return "no SafetyFloor to open"

    offset = obj.matrix_world.translation
    outer = (min(v.co.x for v in obj.data.vertices), max(v.co.x for v in obj.data.vertices),
             min(v.co.y for v in obj.data.vertices), max(v.co.y for v in obj.data.vertices))

    boxes = [(x0 - offset.x, x0 + (nx - 1) * CELL - offset.x,
              y0 - offset.y, y0 + (ny - 1) * CELL - offset.y)
             for _cell, nx, ny, x0, y0 in pools]

    verts, index, faces = [], {}, []

    def vertex(x, y):
        key = (round(x, 4), round(y, 4))
        if key not in index:
            index[key] = len(verts)
            verts.append((x, y, 0.0))
        return index[key]

    def quad(ax, bx, ay, by):
        faces.append((vertex(ax, ay), vertex(bx, ay), vertex(bx, by), vertex(ax, by)))

    # Everything outside the pool search boxes, as a handful of big tiles.
    xs = sorted({outer[0], outer[1]} | {v for b in boxes for v in b[:2]})
    ys = sorted({outer[2], outer[3]} | {v for b in boxes for v in b[2:]})
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cx, cy = (xs[i] + xs[i + 1]) / 2.0, (ys[j] + ys[j + 1]) / 2.0
            if any(x0 < cx < x1 and y0 < cy < y1 for x0, x1, y0, y1 in boxes):
                continue
            quad(xs[i], xs[i + 1], ys[j], ys[j + 1])

    # Inside them, one tile per dry cell.
    dropped = 0
    for cell, nx, ny, x0, y0 in pools:
        bx, by = x0 - offset.x, y0 - offset.y
        for i in range(nx - 1):
            for j in range(ny - 1):
                if cell[i][j]:
                    dropped += 1
                    continue
                quad(bx + i * CELL, bx + (i + 1) * CELL,
                     by + j * CELL, by + (j + 1) * CELL)

    mesh = bpy.data.meshes.new("SafetyFloor")
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    for slot in obj.data.materials:
        mesh.materials.append(slot)
    old = obj.data
    obj.data = mesh
    if old.users == 0:
        bpy.data.meshes.remove(old)
    return ("SafetyFloor: %d wet squares opened, %d tiles standing"
            % (dropped, len(faces)))


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
    pools = []

    for label, footprint, cut_z in CARVE:
        trimmed, emptied = carve_below(footprint, cut_z)
        report.append("carved %s below z=%.2f: %s%s"
                      % (label, cut_z, ", ".join(trimmed) or "nothing left to cut",
                         "; removed " + ", ".join(emptied) if emptied else ""))

    for name, level, (x0, x1, y0, y1), glows, floor in BODIES:
        if floor is not None:
            floor_level, thickness = floor
            slab_name = name.replace("Water", "Floor")
            slab, slab_faces = build_floor(slab_name, floor_level, thickness,
                                           x0, x1, y0, y1, collection)
            report.append("%s: %d quads at z=%.2f, %.2f m under the waterline"
                          % (slab_name, slab_faces, floor_level, level - floor_level))

        obj, faces, grid = build_surface(name, level, x0, x1, y0, y1, collection, material)
        stem = name.replace("Water", "Glow")
        for index, (position, energy) in enumerate(glows, start=1):
            glow_light("%s_%02d" % (stem, index), position, energy, 3.5, collection)
        report.append("%s: %d quads, %.1f m2 at z=%.2f"
                      % (name, faces, sum(f.area for f in obj.data.polygons), level))
        pools.append(grid)

    report.append(open_safety_floor(pools))
    return report


__result__ = main()
