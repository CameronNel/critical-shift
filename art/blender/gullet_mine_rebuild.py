"""Deterministic repair pass for the Gullet Mine Blender look-dev scene.

Run this script through the live Blender bridge with `transport="bridge"`.
It replaces the failed straight-track polish pass with a correctly scaled rail
that follows the authored cave centerline, restores the real terrain, grounds
timber supports against the cave shell, adds restrained ore seams, and installs
CC0 caged industrial lamps with subtle asynchronous light animation.

The script deliberately edits only the look-dev blend and saves the active
file after all validation checks pass.
"""

from __future__ import annotations

import math
import os
import random
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree


SEED = 240806
VERSION = "2026-08-06-rebuild-01"
REBUILD_COLLECTION = "CriticalShift_Mine_Rebuild"
ASSET_COLLECTION = "CS_IndustrialWallLamp_Source"
FAILED_COLLECTION = "GulletMine_Polish"
GAUGE = 0.90
SLEEPER_HEIGHT = 0.14
RAIL_HEIGHT = 0.18
RAIL_PROFILE = (
    (-0.075, 0.000),
    (0.075, 0.000),
    (0.075, 0.040),
    (0.038, 0.070),
    (0.034, 0.125),
    (0.078, 0.140),
    (0.078, RAIL_HEIGHT),
    (-0.078, RAIL_HEIGHT),
    (-0.078, 0.140),
    (-0.034, 0.125),
    (-0.038, 0.070),
    (-0.075, 0.040),
)

# Original Three.js route.  x/z are transformed through the imported
# GulletMine root so the Blender repair stays locked to the authored cave.
ROUTE_NODES = (
    (0.0, 21.0),
    (0.0, 16.0),
    (0.0, 11.0),
    (0.0, 6.0),
    (0.0, 1.0),
    (0.0, -4.0),
    (0.0, -10.0),
    (0.0, -16.0),
    (2.5, -21.0),
    (5.5, -26.0),
    (5.5, -32.0),
    (3.5, -38.0),
    (0.5, -44.0),
    (-2.5, -49.0),
    (-6.0, -54.0),
    (-7.0, -60.0),
)
ROUTE_WIDTHS = (3.5, 3.4, 2.9, 2.7, 2.8, 3.6, 4.0, 3.7, 3.8, 4.1, 4.1, 4.0, 3.3, 3.4, 3.8, 3.9)


@dataclass
class TrackPoint:
    position: Vector
    tangent: Vector
    side: Vector
    distance: float = 0.0
    floor_z: float | None = None
    half_width: float = 3.5


def get_collection(name: str, *, link: bool = True) -> bpy.types.Collection:
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
    if link and collection.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(collection)
    return collection


def remove_collection(name: str) -> None:
    collection = bpy.data.collections.get(name)
    if collection is None:
        return
    for child in list(collection.children):
        remove_collection(child.name)
    for obj in list(collection.objects):
        data = obj.data if hasattr(obj, "data") else None
        obj_type = obj.type
        bpy.data.objects.remove(obj, do_unlink=True)
        if data is not None and data.users == 0:
            if obj_type == "MESH":
                bpy.data.meshes.remove(data)
            elif obj_type == "CURVE":
                bpy.data.curves.remove(data)
            elif obj_type == "CAMERA":
                bpy.data.cameras.remove(data)
            elif obj_type == "LIGHT":
                bpy.data.lights.remove(data)
    bpy.data.collections.remove(collection)


def move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)


def assign_material(obj: bpy.types.Object, material: bpy.types.Material) -> None:
    if not hasattr(obj.data, "materials"):
        return
    obj.data.materials.clear()
    obj.data.materials.append(material)


def image_path(set_name: str, channel: str) -> str:
    path = bpy.path.abspath(f"//textures/{set_name}/{set_name}_2K-JPG_{channel}.jpg")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return path


def load_image(set_name: str, channel: str, *, non_color: bool = False) -> bpy.types.Image:
    image = bpy.data.images.load(image_path(set_name, channel), check_existing=True)
    if non_color:
        image.colorspace_settings.name = "Non-Color"
    return image


def make_triplanar_material(
    name: str,
    set_name: str,
    tint: Sequence[float],
    scale: float,
    *,
    saturation: float = 0.75,
    value: float = 0.72,
    normal_strength: float = 0.45,
    rough_min: float = 0.72,
    rough_max: float = 0.96,
    macro_bump: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    geometry = nodes.new("ShaderNodeNewGeometry")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.vector_type = "POINT"
    mapping.inputs["Scale"].default_value = (scale, scale, scale)
    links.new(geometry.outputs["Position"], mapping.inputs["Vector"])

    color = nodes.new("ShaderNodeTexImage")
    color.image = load_image(set_name, "Color")
    color.projection = "BOX"
    color.projection_blend = 0.28
    color.extension = "REPEAT"
    normal = nodes.new("ShaderNodeTexImage")
    normal.image = load_image(set_name, "NormalGL", non_color=True)
    normal.projection = "BOX"
    normal.projection_blend = 0.28
    normal.extension = "REPEAT"
    rough = nodes.new("ShaderNodeTexImage")
    rough.image = load_image(set_name, "Roughness", non_color=True)
    rough.projection = "BOX"
    rough.projection_blend = 0.28
    rough.extension = "REPEAT"
    for node in (color, normal, rough):
        links.new(mapping.outputs["Vector"], node.inputs["Vector"])

    hue = nodes.new("ShaderNodeHueSaturation")
    hue.inputs["Saturation"].default_value = saturation
    hue.inputs["Value"].default_value = value
    links.new(color.outputs["Color"], hue.inputs["Color"])
    tint_node = nodes.new("ShaderNodeRGB")
    tint_node.outputs[0].default_value = (*tint, 1.0)
    multiply = nodes.new("ShaderNodeMixRGB")
    multiply.blend_type = "MULTIPLY"
    multiply.inputs[0].default_value = 0.56
    links.new(hue.outputs["Color"], multiply.inputs[1])
    links.new(tint_node.outputs[0], multiply.inputs[2])

    normal_map = nodes.new("ShaderNodeNormalMap")
    normal_map.inputs["Strength"].default_value = normal_strength
    links.new(normal.outputs["Color"], normal_map.inputs["Color"])

    final_normal = normal_map.outputs["Normal"]
    if macro_bump > 0.0:
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 1.45
        noise.inputs["Detail"].default_value = 3.0
        noise.inputs["Roughness"].default_value = 0.78
        links.new(geometry.outputs["Position"], noise.inputs["Vector"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = macro_bump
        bump.inputs["Distance"].default_value = 0.12
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(normal_map.outputs["Normal"], bump.inputs["Normal"])
        final_normal = bump.outputs["Normal"]

    rough_map = nodes.new("ShaderNodeMapRange")
    rough_map.inputs["From Min"].default_value = 0.0
    rough_map.inputs["From Max"].default_value = 1.0
    rough_map.inputs["To Min"].default_value = rough_min
    rough_map.inputs["To Max"].default_value = rough_max
    rough_map.clamp = True
    links.new(rough.outputs["Color"], rough_map.inputs["Value"])

    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Metallic"].default_value = 0.0
    links.new(multiply.outputs[0], shader.inputs["Base Color"])
    links.new(rough_map.outputs["Result"], shader.inputs["Roughness"])
    links.new(final_normal, shader.inputs["Normal"])
    output = nodes.new("ShaderNodeOutputMaterial")
    links.new(shader.outputs[0], output.inputs[0])
    material.diffuse_color = (*tint, 1.0)
    material["projection"] = "world-space box projection; stretch resistant"
    material["source"] = f"ambientCG {set_name}, CC0 1.0"
    return material


def make_wood_material() -> bpy.types.Material:
    material = bpy.data.materials.get("CS_SawnMineTimber") or bpy.data.materials.new("CS_SawnMineTimber")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    texcoord = nodes.new("ShaderNodeTexCoord")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.noise_dimensions = "4D"
    noise.inputs["Scale"].default_value = 3.3
    noise.inputs["Detail"].default_value = 4.0
    noise.inputs["Roughness"].default_value = 0.72
    noise.inputs["Distortion"].default_value = 0.22
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1.25, 1.25, 0.20)
    links.new(texcoord.outputs["Object"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    object_info = nodes.new("ShaderNodeObjectInfo")
    random_scale = nodes.new("ShaderNodeMath")
    random_scale.operation = "MULTIPLY"
    random_scale.inputs[1].default_value = 11.0
    links.new(object_info.outputs["Random"], random_scale.inputs[0])
    links.new(random_scale.outputs[0], noise.inputs["W"])
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.22
    ramp.color_ramp.elements[0].color = (0.018, 0.007, 0.003, 1.0)
    ramp.color_ramp.elements[1].position = 0.82
    ramp.color_ramp.elements[1].color = (0.155, 0.050, 0.015, 1.0)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.26
    bump.inputs["Distance"].default_value = 0.055
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Roughness"].default_value = 0.83
    shader.inputs["Metallic"].default_value = 0.0
    links.new(ramp.outputs["Color"], shader.inputs["Base Color"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    output = nodes.new("ShaderNodeOutputMaterial")
    links.new(shader.outputs[0], output.inputs[0])
    material.diffuse_color = (0.16, 0.045, 0.012, 1.0)
    material["finish"] = "procedural matte sawn timber; local beam coordinates"
    return material


def make_metal_material(name: str, color: Sequence[float], metallic: float, roughness: float) -> bpy.types.Material:
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    geometry = nodes.new("ShaderNodeNewGeometry")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 5.2
    noise.inputs["Detail"].default_value = 3.0
    noise.inputs["Roughness"].default_value = 0.72
    links.new(geometry.outputs["Position"], noise.inputs["Vector"])
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (color[0] * 0.35, color[1] * 0.32, color[2] * 0.28, 1.0)
    ramp.color_ramp.elements[1].color = (*color, 1.0)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.18
    bump.inputs["Distance"].default_value = 0.018
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    links.new(ramp.outputs["Color"], shader.inputs["Base Color"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    output = nodes.new("ShaderNodeOutputMaterial")
    links.new(shader.outputs[0], output.inputs[0])
    material.diffuse_color = (*color, 1.0)
    return material


def make_simple_material(
    name: str,
    color: Sequence[float],
    roughness: float,
    metallic: float = 0.0,
    emission: Sequence[float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    material = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    shader = nodes.new("ShaderNodeBsdfPrincipled")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    if emission is not None:
        shader.inputs["Emission Color"].default_value = (*emission, 1.0)
        shader.inputs["Emission Strength"].default_value = emission_strength
    output = nodes.new("ShaderNodeOutputMaterial")
    links.new(shader.outputs[0], output.inputs[0])
    material.diffuse_color = (*color, 1.0)
    return material


def cardinal_point(p0: Vector, p1: Vector, p2: Vector, p3: Vector, t: float) -> Vector:
    t2 = t * t
    t3 = t2 * t
    return 0.5 * (
        2.0 * p1
        + (-p0 + p2) * t
        + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2
        + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3
    )


def route_world_nodes() -> list[Vector]:
    root = bpy.data.objects.get("GulletMine")
    if root is None:
        raise RuntimeError("GulletMine import root is missing")
    scale = root.matrix_world.to_scale().x
    translation = root.matrix_world.translation
    return [Vector((translation.x + scale * x, translation.y - scale * z, translation.z)) for x, z in ROUTE_NODES]


def sample_route(subdivisions: int = 12) -> list[TrackPoint]:
    nodes = route_world_nodes()
    root_scale = bpy.data.objects["GulletMine"].matrix_world.to_scale().x
    positions: list[Vector] = []
    half_widths: list[float] = []
    for index in range(len(nodes) - 1):
        p0 = nodes[max(index - 1, 0)]
        p1 = nodes[index]
        p2 = nodes[index + 1]
        p3 = nodes[min(index + 2, len(nodes) - 1)]
        for step in range(subdivisions):
            factor = step / subdivisions
            positions.append(cardinal_point(p0, p1, p2, p3, factor))
            half_widths.append((ROUTE_WIDTHS[index] * (1.0 - factor) + ROUTE_WIDTHS[index + 1] * factor) * root_scale * 0.90)
    positions.append(nodes[-1].copy())
    half_widths.append(ROUTE_WIDTHS[-1] * root_scale * 0.90)
    points: list[TrackPoint] = []
    distance = 0.0
    for index, position in enumerate(positions):
        if index == 0:
            tangent = positions[1] - position
        elif index == len(positions) - 1:
            tangent = position - positions[index - 1]
        else:
            tangent = positions[index + 1] - positions[index - 1]
        tangent.z = 0.0
        tangent.normalize()
        side = Vector((-tangent.y, tangent.x, 0.0))
        if index:
            distance += (position - positions[index - 1]).length
        points.append(TrackPoint(position.copy(), tangent, side, distance, None, half_widths[index]))
    return points


def bvh_for(obj: bpy.types.Object) -> BVHTree:
    # Raycast the evaluated render shape, including the cave's restrained
    # displacement, so lamps, ore and support ends sit flush with what is seen.
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        vertices = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
        polygons = [list(poly.vertices) for poly in mesh.polygons]
        return BVHTree.FromPolygons(vertices, polygons, all_triangles=False)
    finally:
        evaluated.to_mesh_clear()


def ray_hit(bvh: BVHTree, origin: Vector, direction: Vector, distance: float) -> tuple[Vector, Vector] | None:
    location, normal, _index, _distance = bvh.ray_cast(origin, direction.normalized(), distance)
    if location is None:
        return None
    return location, normal


def fill_missing(values: list[float | None]) -> list[float]:
    result = list(values)
    valid = [index for index, value in enumerate(result) if value is not None]
    if not valid:
        raise RuntimeError("No route samples intersect the authored floor")
    for index in range(0, valid[0]):
        result[index] = result[valid[0]]
    for index in range(valid[-1] + 1, len(result)):
        result[index] = result[valid[-1]]
    for left, right in zip(valid, valid[1:]):
        if right == left + 1:
            continue
        start = float(result[left])
        end = float(result[right])
        for index in range(left + 1, right):
            factor = (index - left) / (right - left)
            result[index] = start * (1.0 - factor) + end * factor
    return [float(value) for value in result]


def prepare_track(points: list[TrackPoint], floor_bvh: BVHTree) -> None:
    floor_values: list[float | None] = []
    for point in points:
        hit = ray_hit(floor_bvh, point.position + Vector((0.0, 0.0, 5.0)), Vector((0.0, 0.0, -1.0)), 12.0)
        point.floor_z = hit[0].z if hit else None
        floor_values.append(point.floor_z)
    filled = fill_missing(floor_values)
    clearances = []
    for index in range(len(points)):
        neighbors = [floor_values[j] for j in range(max(0, index - 2), min(len(points), index + 3)) if floor_values[j] is not None]
        reference = max(neighbors) if neighbors else filled[index]
        clearances.append(reference + 0.035)
    heights = list(clearances)
    # A track can follow the terrain without copying every small displaced
    # bump.  Relax the clearance envelope repeatedly, never below its required
    # height, then propagate high spots so grade changes remain mine-cart safe.
    for _ in range(18):
        relaxed = list(heights)
        for index in range(1, len(heights) - 1):
            candidate = (heights[index - 1] + 2.0 * heights[index] + heights[index + 1]) * 0.25
            relaxed[index] = max(clearances[index], candidate)
        heights = relaxed
    max_slope = 0.045
    for _ in range(3):
        for index in range(1, len(points)):
            run = max((points[index].position - points[index - 1].position).length, 0.001)
            heights[index] = max(heights[index], heights[index - 1] - max_slope * run)
        for index in range(len(points) - 2, -1, -1):
            run = max((points[index + 1].position - points[index].position).length, 0.001)
            heights[index] = max(heights[index], heights[index + 1] - max_slope * run)
    for point, height in zip(points, heights):
        point.position.z = height


def at_distance(points: Sequence[TrackPoint], distance: float) -> TrackPoint:
    distance = max(0.0, min(distance, points[-1].distance))
    for index in range(1, len(points)):
        if points[index].distance < distance:
            continue
        left = points[index - 1]
        right = points[index]
        span = max(right.distance - left.distance, 0.001)
        factor = (distance - left.distance) / span
        position = left.position.lerp(right.position, factor)
        tangent = left.tangent.lerp(right.tangent, factor).normalized()
        side = Vector((-tangent.y, tangent.x, 0.0))
        floor_z = None
        if left.floor_z is not None and right.floor_z is not None:
            floor_z = left.floor_z * (1.0 - factor) + right.floor_z * factor
        half_width = left.half_width * (1.0 - factor) + right.half_width * factor
        return TrackPoint(position, tangent, side, distance, floor_z, half_width)
    return points[-1]


def create_mesh(name: str, vertices: Iterable[Sequence[float]], faces: Iterable[Sequence[int]], collection: bpy.types.Collection, material: bpy.types.Material) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(list(vertices), [], list(faces))
    mesh.validate(verbose=False)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    assign_material(obj, material)
    return obj


BOX_FACES = (
    (0, 1, 2, 3),
    (4, 7, 6, 5),
    (0, 4, 5, 1),
    (1, 5, 6, 2),
    (2, 6, 7, 3),
    (4, 0, 3, 7),
)


def batch_boxes(name: str, boxes: Iterable[tuple[Vector, Vector, Vector, Vector, Vector]], collection: bpy.types.Collection, material: bpy.types.Material) -> bpy.types.Object:
    vertices: list[Vector] = []
    faces: list[tuple[int, ...]] = []
    for center, axis_x, axis_y, axis_z, size in boxes:
        start = len(vertices)
        for sx, sy, sz in ((-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)):
            vertices.append(center + axis_x * (sx * size.x * 0.5) + axis_y * (sy * size.y * 0.5) + axis_z * (sz * size.z * 0.5))
        faces.extend(tuple(start + index for index in face) for face in BOX_FACES)
    return create_mesh(name, vertices, faces, collection, material)


def beam_between(name: str, start: Vector, end: Vector, width: float, depth: float, collection: bpy.types.Collection, material: bpy.types.Material, bevel: float = 0.025) -> bpy.types.Object:
    direction = end - start
    if direction.length < 0.001:
        raise ValueError(f"Zero-length beam: {name}")
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(start + end) * 0.5)
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, collection)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0.0, 0.0, 1.0)).rotation_difference(direction.normalized())
    obj.scale = (width, depth, direction.length)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign_material(obj, material)
    modifier = obj.modifiers.new("Worn timber edges", "BEVEL")
    modifier.width = bevel
    modifier.segments = 2
    return obj


def rail_mesh(name: str, points: Sequence[TrackPoint], offset: float, collection: bpy.types.Collection, material: bpy.types.Material) -> bpy.types.Object:
    vertices: list[Vector] = []
    faces: list[tuple[int, int, int, int]] = []
    ring = len(RAIL_PROFILE)
    for point in points:
        center = point.position + point.side * offset + Vector((0.0, 0.0, SLEEPER_HEIGHT))
        for across, height in RAIL_PROFILE:
            vertices.append(center + point.side * across + Vector((0.0, 0.0, height)))
    for index in range(len(points) - 1):
        start = index * ring
        next_start = (index + 1) * ring
        for profile_index in range(ring):
            next_profile = (profile_index + 1) % ring
            faces.append((start + profile_index, next_start + profile_index, next_start + next_profile, start + next_profile))
    obj = create_mesh(name, vertices, faces, collection, material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj["gauge_m"] = GAUGE
    obj["role"] = "continuous curved mine rail"
    return obj


def ribbon_mesh(
    name: str,
    points: Sequence[TrackPoint],
    width: float,
    thickness: float,
    collection: bpy.types.Collection,
    material: bpy.types.Material,
    include: Callable[[TrackPoint], bool],
) -> bpy.types.Object:
    vertices: list[Vector] = []
    faces: list[tuple[int, ...]] = []
    for left, right in zip(points, points[1:]):
        mid = at_distance((left, right), (left.distance + right.distance) * 0.5)
        if not include(mid):
            continue
        start = len(vertices)
        top_left_a = left.position - left.side * (width * 0.5) + Vector((0.0, 0.0, 0.02))
        top_right_a = left.position + left.side * (width * 0.5) + Vector((0.0, 0.0, 0.02))
        top_left_b = right.position - right.side * (width * 0.5) + Vector((0.0, 0.0, 0.02))
        top_right_b = right.position + right.side * (width * 0.5) + Vector((0.0, 0.0, 0.02))
        vertices.extend((top_left_a, top_right_a, top_left_b, top_right_b, top_left_a - Vector((0, 0, thickness)), top_right_a - Vector((0, 0, thickness)), top_left_b - Vector((0, 0, thickness)), top_right_b - Vector((0, 0, thickness))))
        faces.extend(
            (
                (start, start + 2, start + 3, start + 1),
                (start + 4, start + 5, start + 7, start + 6),
                (start, start + 4, start + 6, start + 2),
                (start + 1, start + 3, start + 7, start + 5),
                (start, start + 1, start + 5, start + 4),
                (start + 2, start + 6, start + 7, start + 3),
            )
        )
    return create_mesh(name, vertices, faces, collection, material)


def cave_floor_mesh(points: Sequence[TrackPoint], collection: bpy.types.Collection, material: bpy.types.Material) -> bpy.types.Object:
    vertices: list[Vector] = []
    faces: list[tuple[int, int, int, int]] = []
    for point in points:
        floor_z = point.position.z - 0.045
        vertices.extend(
            (
                Vector((point.position.x, point.position.y, floor_z)) - point.side * point.half_width,
                Vector((point.position.x, point.position.y, floor_z)) + point.side * point.half_width,
            )
        )
    for index in range(len(points) - 1):
        mid = at_distance(points, (points[index].distance + points[index + 1].distance) * 0.5)
        if in_gap(mid):
            continue
        start = index * 2
        faces.append((start, start + 2, start + 3, start + 1))
    floor = create_mesh("CS_CaveFloor", vertices, faces, collection, material)
    floor["source"] = "authored cave width profile; stretch-resistant triplanar ground"
    return floor


def gap_ranges() -> tuple[tuple[float, float], ...]:
    root = bpy.data.objects["GulletMine"]
    scale = root.matrix_world.to_scale().x
    offset = root.matrix_world.translation.y
    return (
        (offset + scale * 6.4, offset + scale * 13.6),
        (offset + scale * 22.4, offset + scale * 35.4),
    )


def in_gap(point: TrackPoint) -> bool:
    return any(low <= point.position.y <= high for low, high in gap_ranges())


def build_track(points: list[TrackPoint], collection: bpy.types.Collection, materials: dict[str, bpy.types.Material]) -> dict[str, object]:
    cave_floor_mesh(points, collection, materials["ground"])
    ribbon_mesh("CS_TrackBallast", points, 2.12, 0.14, collection, materials["gravel"], lambda p: not in_gap(p))
    # Cover the full worked width at the shaft and sump.  The openings remain
    # legible through the sign, bearers and edge change, but no longer read as
    # accidental black voids or leave an unsafe strip beside the tramway.
    ribbon_mesh("CS_ShaftAndSumpDeck", points, 7.20, 0.20, collection, materials["wood"], in_gap)

    sleeper_boxes = []
    distance = 0.25
    while distance <= points[-1].distance - 0.15:
        point = at_distance(points, distance)
        sleeper_boxes.append((point.position + Vector((0.0, 0.0, SLEEPER_HEIGHT * 0.5)), point.side, point.tangent, Vector((0, 0, 1)), Vector((1.72, 0.24, SLEEPER_HEIGHT))))
        distance += 0.82
    sleepers = batch_boxes("CS_CurvedTrackSleepers", sleeper_boxes, collection, materials["wood"])
    bevel = sleepers.modifiers.new("Worn sleeper edges", "BEVEL")
    bevel.width = 0.018
    bevel.segments = 2
    rail_mesh("CS_LeftRail", points, -GAUGE * 0.5, collection, materials["rail"])
    rail_mesh("CS_RightRail", points, GAUGE * 0.5, collection, materials["rail"])

    # Extra bearers make the two intentional floor gaps read as engineered
    # crossings instead of accidental black holes.
    bearer_boxes = []
    distance = 0.0
    while distance <= points[-1].distance:
        point = at_distance(points, distance)
        if in_gap(point):
            bearer_boxes.append((point.position - Vector((0, 0, 0.13)), point.side, point.tangent, Vector((0, 0, 1)), Vector((2.55, 0.30, 0.18))))
        distance += 1.65
    if bearer_boxes:
        batch_boxes("CS_CrossingBearers", bearer_boxes, collection, materials["dark_wood"])

    curve_data = bpy.data.curves.new("CS_TrackCenterline_Data", "CURVE")
    curve_data.dimensions = "3D"
    spline = curve_data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for handle, point in zip(spline.points, points):
        handle.co = (*point.position, 1.0)
    centerline = bpy.data.objects.new("CS_TrackCenterline", curve_data)
    collection.objects.link(centerline)
    centerline.hide_render = True
    centerline.display_type = "WIRE"
    centerline["validation_only"] = True
    return {"sleepers": len(sleeper_boxes), "length_m": round(points[-1].distance, 2)}


def wall_point(cave_bvh: BVHTree, point: TrackPoint, sign: float, height: float) -> tuple[Vector, Vector] | None:
    origin = Vector((point.position.x, point.position.y, height))
    return ray_hit(cave_bvh, origin, point.side * sign, 16.0)


def floor_point(floor_bvh: BVHTree, point: Vector, fallback: float) -> float:
    hit = ray_hit(floor_bvh, point + Vector((0.0, 0.0, 5.0)), Vector((0.0, 0.0, -1.0)), 12.0)
    return hit[0].z if hit else fallback


def build_supports(points: list[TrackPoint], cave_bvh: BVHTree, floor_bvh: BVHTree, collection: bpy.types.Collection, materials: dict[str, bpy.types.Material]) -> list[dict[str, object]]:
    frames = []
    distances = (4.5, 15.5, 25.5, 43.5, 56.5, 69.5, 82.0)
    for frame_index, distance in enumerate(distances, start=1):
        point = at_distance(points, distance)
        if in_gap(point):
            continue
        roof = ray_hit(cave_bvh, Vector((point.position.x, point.position.y, point.position.z + 0.1)), Vector((0, 0, 1)), 10.0)
        if roof is None:
            continue
        cap_z = roof[0].z - 0.24
        low_hits = [wall_point(cave_bvh, point, sign, 0.42) for sign in (-1.0, 1.0)]
        high_hits = [wall_point(cave_bvh, point, sign, cap_z) for sign in (-1.0, 1.0)]
        if any(hit is None for hit in low_hits + high_hits):
            continue
        feet = []
        tops = []
        for sign, low_hit, high_hit in zip((-1.0, 1.0), low_hits, high_hits):
            inward = point.side * -sign
            foot_xy = low_hit[0] + inward * 0.17
            foot_z = floor_point(floor_bvh, foot_xy, point.position.z) - 0.035
            top = high_hit[0] + inward * 0.16
            top.z = cap_z
            foot = Vector((foot_xy.x, foot_xy.y, foot_z))
            feet.append(foot)
            tops.append(top)
            post = beam_between(f"CS_TimberFrame_{frame_index:02d}_{'L' if sign < 0 else 'R'}_Post", foot, top, 0.31, 0.34, collection, materials["wood"], 0.024)
            post["contact"] = "raycast to authored cave rib and terrain"
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.25, depth=0.07, location=foot + Vector((0, 0, 0.02)))
            pad = bpy.context.object
            pad.name = f"CS_TimberFrame_{frame_index:02d}_{'L' if sign < 0 else 'R'}_FootPad"
            move_to_collection(pad, collection)
            assign_material(pad, materials["hardware"])
        cap = beam_between(f"CS_TimberFrame_{frame_index:02d}_Cap", tops[0], tops[1], 0.34, 0.36, collection, materials["wood"], 0.026)
        cap["contact"] = "ends inset 0.16 m from cave shell"
        for side_index in (0, 1):
            knee_start = feet[side_index].lerp(tops[side_index], 0.63)
            knee_end = tops[0].lerp(tops[1], 0.24 if side_index == 0 else 0.76)
            beam_between(f"CS_TimberFrame_{frame_index:02d}_Knee_{side_index + 1}", knee_start, knee_end, 0.17, 0.20, collection, materials["dark_wood"], 0.018)
        frames.append({"index": frame_index, "distance": distance, "span_m": round((tops[1] - tops[0]).length, 2), "height_m": round(cap_z - min(foot.z for foot in feet), 2)})
    return frames


def build_cart(points: list[TrackPoint], collection: bpy.types.Collection, materials: dict[str, bpy.types.Material]) -> None:
    point = at_distance(points, 33.5)
    up = Vector((0, 0, 1))
    base_z = point.position.z + SLEEPER_HEIGHT + RAIL_HEIGHT
    boxes = [
        (point.position + up * (SLEEPER_HEIGHT + RAIL_HEIGHT + 0.30), point.side, point.tangent, up, Vector((1.20, 1.50, 0.16))),
        (point.position + up * (SLEEPER_HEIGHT + RAIL_HEIGHT + 0.72), point.side, point.tangent, up, Vector((1.32, 1.42, 0.62))),
    ]
    cart = batch_boxes("CS_MineCart_Body", boxes, collection, materials["cart"])
    bevel = cart.modifiers.new("Cart worn edges", "BEVEL")
    bevel.width = 0.045
    bevel.segments = 2
    for axle_sign in (-1.0, 1.0):
        for side_sign in (-1.0, 1.0):
            wheel_center = point.position + point.tangent * (axle_sign * 0.48) + point.side * (side_sign * GAUGE * 0.5) + up * (SLEEPER_HEIGHT + RAIL_HEIGHT + 0.18)
            bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.18, depth=0.10, location=wheel_center)
            wheel = bpy.context.object
            wheel.name = f"CS_MineCart_Wheel_{int((axle_sign + 1) / 2)}_{int((side_sign + 1) / 2)}"
            move_to_collection(wheel, collection)
            wheel.rotation_mode = "QUATERNION"
            wheel.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(point.side)
            assign_material(wheel, materials["hardware"])
    rng = random.Random(SEED + 91)
    for index in range(7):
        location = point.position + point.side * rng.uniform(-0.40, 0.40) + point.tangent * rng.uniform(-0.42, 0.42) + up * rng.uniform(0.98, 1.16)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=rng.uniform(0.16, 0.26), location=location)
        rock = bpy.context.object
        rock.name = f"CS_MineCart_Load_{index + 1:02d}"
        move_to_collection(rock, collection)
        rock.scale = (rng.uniform(0.9, 1.35), rng.uniform(0.7, 1.1), rng.uniform(0.55, 0.85))
        rock.rotation_euler = (rng.random(), rng.random(), rng.random())
        assign_material(rock, materials["ground_rock"])
        for polygon in rock.data.polygons:
            polygon.use_smooth = False
    cart["rail_gauge_m"] = GAUGE
    cart["clearance_role"] = "visual cart envelope validation"


def cleanup_imported_asset_data() -> None:
    remove_collection(ASSET_COLLECTION)
    for material in list(bpy.data.materials):
        if material.name.startswith("industrial_wall_lamp") and material.users == 0:
            bpy.data.materials.remove(material)
    for mesh in list(bpy.data.meshes):
        if mesh.name.startswith("industrial_wall_lamp") and mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def import_lamp_source() -> bpy.types.Object:
    cleanup_imported_asset_data()
    source_collection = get_collection(ASSET_COLLECTION, link=False)
    path = bpy.path.abspath("//assets/polyhaven/industrial_wall_lamp_1k/industrial_wall_lamp_1k.gltf")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    created = [obj for obj in bpy.data.objects if obj not in before]
    meshes = [obj for obj in created if obj.type == "MESH"]
    if len(meshes) != 1:
        raise RuntimeError(f"Expected one lamp mesh, imported {len(meshes)}")
    source = meshes[0]
    source.name = "CS_IndustrialWallLamp_SourceMesh"
    move_to_collection(source, source_collection)
    # Poly Haven's glTF ships with a display-oriented emission strength of 100.
    # That reads as a blown-out white panel under the mine's close practical
    # lighting, so keep the authored emissive map but bring it into scene scale.
    for material in source.data.materials:
        if material is None or not material.use_nodes:
            continue
        for node in material.node_tree.nodes:
            if node.type == "BSDF_PRINCIPLED" and "Emission Strength" in node.inputs:
                if node.inputs["Emission Strength"].default_value > 0.0:
                    node.inputs["Emission Strength"].default_value = 8.0
    source["source"] = "Poly Haven industrial_wall_lamp, CC0 1.0, Kuutti Siitonen"
    return source


def lamp_rotation(outward: Vector) -> Matrix:
    outward = Vector((outward.x, outward.y, 0.0)).normalized()
    up = Vector((0, 0, 1))
    x_axis = outward.cross(up).normalized()
    return Matrix((x_axis, outward, up)).transposed()


def build_lights(points: list[TrackPoint], cave_bvh: BVHTree, collection: bpy.types.Collection, materials: dict[str, bpy.types.Material]) -> list[bpy.types.Object]:
    source = import_lamp_source()
    lamps: list[bpy.types.Object] = []
    for index, distance in enumerate((5.5, 14.0, 22.5, 31.0, 40.0, 49.0, 58.0, 67.0, 76.0, 84.5), start=1):
        point = at_distance(points, distance)
        sign = -1.0 if index % 2 else 1.0
        hit = wall_point(cave_bvh, point, sign, 2.18 + 0.18 * ((index % 3) - 1))
        if hit is None:
            sign *= -1.0
            hit = wall_point(cave_bvh, point, sign, 2.18)
        if hit is None:
            continue
        outward = point.side * sign
        inward = -outward
        back = hit[0] + inward * 0.025
        lamp = source.copy()
        lamp.data = source.data
        lamp.name = f"CS_IndustrialLamp_{index:02d}"
        collection.objects.link(lamp)
        lamp.location = back
        lamp.rotation_mode = "QUATERNION"
        lamp.rotation_quaternion = lamp_rotation(outward).to_quaternion()
        lamp.scale = (1.24, 1.24, 1.24)
        lamp["license"] = "CC0 1.0"
        lamp["source_asset"] = "https://polyhaven.com/a/industrial_wall_lamp"
        lamps.append(lamp)

        light_data = bpy.data.lights.new(f"{lamp.name}_Light", type="POINT")
        cool = index in (4, 8)
        light_data.color = (0.24, 0.52, 0.58) if cool else (1.0, 0.47, 0.16)
        base_energy = 126.0 if cool else 158.0
        light_data.energy = base_energy
        light_data.shadow_soft_size = 0.42
        light_data.use_shadow = True
        light = bpy.data.objects.new(f"{lamp.name}_Light", light_data)
        collection.objects.link(light)
        # Set the practical slightly proud of the cage. This keeps the wall
        # behind it readable instead of creating a hot spot at point-blank range.
        light.location = back + inward * 0.50
        driver = light_data.driver_add("energy").driver
        phase = index * 0.83
        driver.expression = f"{base_energy:.4f}*(1+0.035*sin(frame*0.19+{phase:.4f})+0.018*sin(frame*0.71+{phase * 1.71:.4f}))"
        light["animation"] = "subtle asynchronous electrical flicker"

        cable_start = back + outward * 0.015 + Vector((0, 0, 0.20))
        cable_end = cable_start + Vector((0, 0, 0.72))
        beam_between(f"{lamp.name}_Conduit", cable_start, cable_end, 0.035, 0.035, collection, materials["cable"], 0.006)
    return lamps


def oriented_ico(
    name: str,
    location: Vector,
    axes: tuple[Vector, Vector, Vector],
    scale: Sequence[float],
    collection: bpy.types.Collection,
    material: bpy.types.Material,
    rng: random.Random,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    move_to_collection(obj, collection)
    matrix = Matrix(axes).transposed()
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = matrix.to_quaternion()
    obj.rotation_euler.rotate_axis("Z", rng.uniform(-0.32, 0.32))
    obj.scale = scale
    assign_material(obj, material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = False
    return obj


def ore_vein_segment(
    name: str,
    center: Vector,
    outward: Vector,
    direction: Vector,
    length: float,
    width: float,
    collection: bpy.types.Collection,
    material: bpy.types.Material,
    rng: random.Random,
) -> bpy.types.Object:
    """Create a thin jagged mineral vein, not a protruding crystal."""
    direction = direction.normalized()
    across = outward.cross(direction).normalized()
    vertices: list[Vector] = []
    for factor in (-0.5, 0.0, 0.5):
        mid = center + direction * (factor * length)
        jitter = across * rng.uniform(-width * 0.35, width * 0.35)
        half_width = width * rng.uniform(0.65, 1.15)
        vertices.append(mid + jitter - across * half_width)
    for factor in (0.5, 0.0, -0.5):
        mid = center + direction * (factor * length)
        jitter = across * rng.uniform(-width * 0.35, width * 0.35)
        half_width = width * rng.uniform(0.65, 1.15)
        vertices.append(mid + jitter + across * half_width)
    vein = create_mesh(name, vertices, [(0, 1, 2, 3, 4, 5)], collection, material)
    vein["visual_language"] = "thin embedded mineral seam"
    return vein


def ore_vein_curve(
    name: str,
    center: Vector,
    outward: Vector,
    tangent_axis: Vector,
    collection: bpy.types.Collection,
    material: bpy.types.Material,
    rng: random.Random,
) -> bpy.types.Object:
    """Create a restrained, branching emissive crack embedded in the wall."""
    up = Vector((0, 0, 1))
    main_direction = (up * rng.uniform(0.82, 0.96) + tangent_axis * rng.uniform(-0.28, 0.28)).normalized()
    across = outward.cross(main_direction).normalized()
    half_length = rng.uniform(0.16, 0.24)
    main_points = [
        center + main_direction * (factor * half_length * 2.0) + across * rng.uniform(-0.022, 0.022)
        for factor in (-0.50, -0.25, 0.0, 0.25, 0.50)
    ]
    branch_a = [main_points[1], main_points[1] + across * rng.uniform(0.045, 0.075) + main_direction * rng.uniform(0.025, 0.050)]
    branch_b = [main_points[3], main_points[3] - across * rng.uniform(0.040, 0.070) - main_direction * rng.uniform(0.020, 0.045)]

    data = bpy.data.curves.new(f"{name}_Data", "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 1
    data.bevel_depth = rng.uniform(0.0020, 0.0032)
    data.bevel_resolution = 0
    data.resolution_v = 0
    data.use_fill_caps = True
    for points in (main_points, branch_a, branch_b):
        spline = data.splines.new("POLY")
        spline.points.add(len(points) - 1)
        for handle, point in zip(spline.points, points):
            handle.co = (*point, 1.0)
    vein = bpy.data.objects.new(name, data)
    collection.objects.link(vein)
    data.materials.append(material)
    vein["visual_language"] = "thin branching embedded mineral seam"
    return vein


def build_ore(points: list[TrackPoint], cave_bvh: BVHTree, collection: bpy.types.Collection, materials: dict[str, bpy.types.Material]) -> int:
    rng = random.Random(SEED + 17)
    cluster_count = 0
    for index, distance in enumerate((7.5, 13.5, 19.5, 26.0, 32.5, 39.5, 46.0, 52.5, 59.0, 65.5, 72.0, 78.5, 85.0), start=1):
        point = at_distance(points, distance)
        sign = -1.0 if index % 2 else 1.0
        height = (0.82, 1.28, 1.72)[index % 3]
        hit = wall_point(cave_bvh, point, sign, height)
        if hit is None:
            continue
        outward = point.side * sign
        inward = -outward
        up = Vector((0, 0, 1))
        tangent_axis = up.cross(outward).normalized()
        ore_vein_curve(
            f"CS_OreSeam_{index:02d}_Vein",
            hit[0] + inward * 0.022,
            outward,
            tangent_axis,
            collection,
            materials["ore_a" if index % 3 else "ore_b"],
            rng,
        )
        if index % 4 == 0:
            light_data = bpy.data.lights.new(f"CS_OreSeam_{index:02d}_Glow", type="POINT")
            light_data.color = (0.04, 0.55, 0.24)
            light_data.energy = 0.65
            light_data.shadow_soft_size = 0.26
            light = bpy.data.objects.new(f"CS_OreSeam_{index:02d}_Glow", light_data)
            collection.objects.link(light)
            light.location = hit[0] + inward * 0.18
        cluster_count += 1
    return cluster_count


def build_wet_patches(points: list[TrackPoint], floor_bvh: BVHTree, collection: bpy.types.Collection, material: bpy.types.Material) -> int:
    rng = random.Random(SEED + 38)
    count = 0
    for index, distance in enumerate((10.5, 21.0, 45.0, 61.5, 80.0), start=1):
        point = at_distance(points, distance)
        if in_gap(point):
            continue
        side_offset = point.side * rng.choice((-1.25, 1.25))
        location = point.position + side_offset
        ground = floor_point(floor_bvh, location, point.position.z)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0, location=(location.x, location.y, ground + 0.012))
        patch = bpy.context.object
        patch.name = f"CS_WetGround_{index:02d}"
        move_to_collection(patch, collection)
        patch.scale = (rng.uniform(0.55, 0.85), rng.uniform(0.85, 1.35), 0.018)
        patch.rotation_euler.z = rng.uniform(-0.4, 0.4)
        assign_material(patch, material)
        for polygon in patch.data.polygons:
            polygon.use_smooth = False
        count += 1
    return count


def build_materials() -> dict[str, bpy.types.Material]:
    rock = make_triplanar_material("CS_CaveRock_Triplanar", "Rock030", (0.30, 0.24, 0.17), 0.66, saturation=0.64, value=0.63, normal_strength=0.58, rough_min=0.78, rough_max=0.97, macro_bump=0.32)
    dark_rock = make_triplanar_material("CS_DarkRock_Triplanar", "Rock023", (0.18, 0.16, 0.13), 0.72, saturation=0.54, value=0.54, normal_strength=0.52, rough_min=0.80, rough_max=0.98, macro_bump=0.26)
    ground = make_triplanar_material("CS_Ground_Triplanar", "Ground054", (0.19, 0.13, 0.075), 0.82, saturation=0.58, value=0.48, normal_strength=0.56, rough_min=0.84, rough_max=0.98, macro_bump=0.18)
    gravel = make_triplanar_material("CS_TrackGravel_Triplanar", "Gravel023", (0.20, 0.17, 0.13), 0.92, saturation=0.55, value=0.52, normal_strength=0.62, rough_min=0.86, rough_max=0.99, macro_bump=0.14)
    wood = make_wood_material()
    dark_wood = make_simple_material("CS_DarkTimber", (0.070, 0.020, 0.006), 0.91)
    rail = make_metal_material("CS_RailSteel", (0.23, 0.075, 0.018), 0.68, 0.58)
    hardware = make_metal_material("CS_DarkIron", (0.085, 0.050, 0.028), 0.78, 0.60)
    cart = make_metal_material("CS_MineCartIron", (0.12, 0.055, 0.026), 0.72, 0.55)
    cable = make_simple_material("CS_RubberCable", (0.012, 0.014, 0.013), 0.82)
    wet = make_simple_material("CS_WetGround", (0.025, 0.040, 0.038), 0.26)
    ore_host = make_simple_material("CS_OreHost", (0.11, 0.095, 0.055), 0.91)
    ore_a = make_simple_material("CS_UraniumOre_Subtle", (0.005, 0.028, 0.010), 0.60, emission=(0.010, 0.14, 0.035), emission_strength=0.24)
    ore_b = make_simple_material("CS_UraniumOre_Accent", (0.008, 0.026, 0.018), 0.62, emission=(0.007, 0.095, 0.045), emission_strength=0.20)
    return {"rock": rock, "dark_rock": dark_rock, "ground": ground, "gravel": gravel, "wood": wood, "dark_wood": dark_wood, "rail": rail, "hardware": hardware, "cart": cart, "cable": cable, "wet": wet, "ore_host": ore_host, "ore_a": ore_a, "ore_b": ore_b, "ground_rock": dark_rock}


def repair_legacy_scene(materials: dict[str, bpy.types.Material]) -> None:
    remove_collection(FAILED_COLLECTION)
    safety_floor = bpy.data.objects.get("SafetyFloor")
    if safety_floor:
        safety_floor.hide_render = True
        safety_floor.hide_viewport = True
        safety_floor.display_type = "WIRE"
        safety_floor["role"] = "navigation-only; never render or export"
    earth = bpy.data.objects.get("earth_001")
    if earth is None:
        raise RuntimeError("Authored earth_001 terrain is missing")
    earth.hide_render = True
    earth.hide_viewport = True
    assign_material(earth, materials["ground"])
    earth["role"] = "hidden terrain height source; rendered floor rebuilt without vertical hole boundaries"

    for name in ("cave_001", "capRock_001"):
        obj = bpy.data.objects.get(name)
        if obj:
            obj.hide_render = False
            obj.hide_viewport = False
            assign_material(obj, materials["rock"])
            for polygon in obj.data.polygons:
                polygon.use_smooth = name != "capRock_001"
    dark = bpy.data.objects.get("darkRock_001")
    if dark:
        dark.hide_render = False
        dark.hide_viewport = False
        assign_material(dark, materials["dark_rock"])
        for polygon in dark.data.polygons:
            polygon.use_smooth = False

    cave = bpy.data.objects.get("cave_001")
    if cave:
        for modifier in list(cave.modifiers):
            if modifier.name == "CS_JaggedRockSurface":
                cave.modifiers.remove(modifier)
        texture = bpy.data.textures.get("CS_JaggedRockNoise") or bpy.data.textures.new("CS_JaggedRockNoise", type="DISTORTED_NOISE")
        texture.noise_scale = 0.72
        modifier = cave.modifiers.new("CS_JaggedRockSurface", "DISPLACE")
        modifier.texture = texture
        modifier.texture_coords = "GLOBAL"
        modifier.strength = 0.045
        modifier.mid_level = 0.50

    for name in (
        "TimberSets", "wood_001", "woodDark_001", "railHead_001", "metal_001", "ironDark_001",
        "COPPER_001", "IRON_001", "IRON_002", "GLIMMER_001", "GLIMMER_002", "gold_001",
        "matrix_001", "matrix_002", "matrix_003", "matrix_004", "rock_001",
    ):
        obj = bpy.data.objects.get(name)
        if obj:
            obj.hide_render = True
            obj.hide_viewport = True
            obj["hidden_by"] = VERSION

    # The imported label remains useful, but the original scale dominated the
    # cart view and intersected later timber passes.
    sign = bpy.data.objects.get("mesh_021")
    if sign:
        if "cs_original_scale" not in sign:
            sign["cs_original_scale"] = list(sign.scale)
            sign["cs_original_location"] = list(sign.location)
        original_scale = Vector(sign["cs_original_scale"])
        original_location = Vector(sign["cs_original_location"])
        sign.scale = original_scale * 0.78
        sign.location = original_location + Vector((0.0, 0.0, 0.30))
        sign.hide_render = False
        sign.hide_viewport = False


def add_camera(name: str, location: Vector, target: Vector, lens: float, collection: bpy.types.Collection) -> bpy.types.Object:
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_width = 36.0
    data.clip_start = 0.05
    data.clip_end = 220.0
    camera = bpy.data.objects.new(name, data)
    collection.objects.link(camera)
    camera.location = location
    camera.rotation_euler = (target - location).to_track_quat("-Z", "Y").to_euler()
    return camera


def build_cameras(points: list[TrackPoint], lamps: list[bpy.types.Object], collection: bpy.types.Collection) -> list[bpy.types.Object]:
    cameras = []
    entry = at_distance(points, 2.5)
    target = at_distance(points, 24.0)
    cameras.append(add_camera("CS_EntryRailCam", entry.position + entry.side * 1.25 + Vector((0, 0, 1.15)), target.position + Vector((0, 0, 0.55)), 39.0, collection))
    curve = at_distance(points, 48.0)
    curve_target = at_distance(points, 65.0)
    cameras.append(add_camera("CS_CurveRailCam", curve.position - curve.side * 1.65 + Vector((0, 0, 1.45)), curve_target.position + Vector((0, 0, 0.45)), 41.0, collection))
    low = at_distance(points, 20.0)
    low_target = at_distance(points, 34.0)
    cameras.append(add_camera("CS_LowTrackCam", low.position + low.side * 0.92 + Vector((0, 0, 0.40)), low_target.position + Vector((0, 0, 0.16)), 46.0, collection))
    support_view = at_distance(points, 9.5)
    support = at_distance(points, 15.5)
    cameras.append(add_camera("CS_SupportCam", support_view.position + support_view.side * 0.65 + Vector((0, 0, 1.20)), support.position + Vector((0, 0, 1.45)), 43.0, collection))
    if lamps:
        lamp = lamps[0]
        inward = at_distance(points, 5.5).position - lamp.location
        inward.z = 0.0
        if inward.length < 0.01:
            inward = Vector((0, 1, 0))
        inward.normalize()
        lamp_track = at_distance(points, 5.5)
        cameras.append(add_camera("CS_LampCam", lamp.location + inward * 1.55 + lamp_track.tangent * 0.58 + Vector((0, 0, 0.14)), lamp.location + Vector((0, 0, 0.02)), 55.0, collection))
    ore = bpy.data.objects.get("CS_OreSeam_08_Vein")
    if ore:
        ore_track = at_distance(points, 52.5)
        ore_points = [ore.matrix_world @ Vector(point.co[:3]) for spline in ore.data.splines for point in spline.points]
        ore_location = sum(ore_points, Vector()) / len(ore_points)
        inward = ore_track.position - ore_location
        inward.z = 0.0
        if inward.length < 0.01:
            inward = ore_track.side.copy()
        inward.normalize()
        ore_camera = ore_location + inward * 1.85 - ore_track.tangent * 0.32 + Vector((0, 0, 0.22))
        cameras.append(add_camera("CS_OreCam", ore_camera, ore_location, 60.0, collection))
    return cameras


def configure_lighting(collection: bpy.types.Collection) -> None:
    for obj in bpy.context.scene.objects:
        if obj.type == "LIGHT" and obj.name.startswith("group_"):
            if "cs_original_energy" not in obj:
                obj["cs_original_energy"] = float(obj.data.energy)
            obj.data.energy = float(obj["cs_original_energy"]) * 0.68
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 850
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.95
    if scene.world and scene.world.use_nodes:
        for node in scene.world.node_tree.nodes:
            if node.bl_idname == "ShaderNodeBackground":
                node.inputs["Color"].default_value = (0.006, 0.009, 0.010, 1.0)
                node.inputs["Strength"].default_value = 0.038
            elif node.bl_idname == "ShaderNodeVolumeScatter":
                node.inputs["Density"].default_value = 0.0
    collection["lighting"] = "CC0 caged work lamps plus restrained legacy feature lights"


def validate(points: list[TrackPoint], frames: list[dict[str, object]], lamps: list[bpy.types.Object], ore_count: int) -> dict[str, object]:
    gauge_errors = []
    for point in points[::12]:
        left = point.position - point.side * GAUGE * 0.5
        right = point.position + point.side * GAUGE * 0.5
        gauge_errors.append(abs((right - left).length - GAUGE))
    clearances = [point.position.z - point.floor_z for point in points if point.floor_z is not None]
    if not clearances or min(clearances) < 0.025:
        raise RuntimeError(f"Track clips terrain: minimum sleeper-bottom clearance {min(clearances) if clearances else None}")
    if max(gauge_errors, default=0.0) > 1e-5:
        raise RuntimeError("Rail gauge drifted along the spline")
    if len(frames) < 5:
        raise RuntimeError(f"Only {len(frames)} grounded timber frames were built")
    if len(lamps) < 8:
        raise RuntimeError(f"Only {len(lamps)} industrial lamps were built")
    if ore_count < 10:
        raise RuntimeError(f"Only {ore_count} ore seams were built")
    safety_floor = bpy.data.objects.get("SafetyFloor")
    if safety_floor and (not safety_floor.hide_render or not safety_floor.hide_viewport):
        raise RuntimeError("SafetyFloor must remain invisible")
    earth = bpy.data.objects.get("earth_001")
    if earth and (not earth.hide_render or not earth.hide_viewport):
        raise RuntimeError("Legacy earth boundary mesh must remain a hidden height source")
    if bpy.data.collections.get(FAILED_COLLECTION):
        raise RuntimeError(f"Failed polish collection still exists: {FAILED_COLLECTION}")
    projection_materials = ("CS_CaveRock_Triplanar", "CS_Ground_Triplanar", "CS_TrackGravel_Triplanar")
    for material_name in projection_materials:
        material = bpy.data.materials.get(material_name)
        if material is None or "stretch resistant" not in str(material.get("projection", "")):
            raise RuntimeError(f"Missing stretch-resistant projection metadata: {material_name}")
    lamp_lights = [bpy.data.objects.get(f"{lamp.name}_Light") for lamp in lamps]
    animated_lights = [
        light for light in lamp_lights
        if light is not None and light.data.animation_data and light.data.animation_data.drivers
    ]
    if len(animated_lights) != len(lamps):
        raise RuntimeError("Every industrial practical must have a flicker driver")
    legacy_rocks = ("rock_001", "matrix_001", "matrix_002", "matrix_003", "matrix_004")
    visible_legacy_rocks = [name for name in legacy_rocks if bpy.data.objects.get(name) and not bpy.data.objects[name].hide_render]
    if visible_legacy_rocks:
        raise RuntimeError(f"Floating legacy rocks still render: {visible_legacy_rocks}")
    return {
        "route_length_m": round(points[-1].distance, 2),
        "gauge_m": GAUGE,
        "max_gauge_error_m": round(max(gauge_errors, default=0.0), 8),
        "min_ground_clearance_m": round(min(clearances), 3),
        "max_track_slope_percent": round(max(abs((b.position.z - a.position.z) / max((b.position - a.position).length, 0.001)) for a, b in zip(points, points[1:])) * 100.0, 2),
        "support_frames": len(frames),
        "lamps": len(lamps),
        "animated_lights": len(animated_lights),
        "ore_seams": ore_count,
        "ore_style": "thin branching embedded seams",
        "stretch_resistant_materials": list(projection_materials),
        "hidden_floor_sources": [name for name in ("SafetyFloor", "earth_001") if bpy.data.objects.get(name) and bpy.data.objects[name].hide_render],
        "floating_legacy_rocks_hidden": [name for name in legacy_rocks if bpy.data.objects.get(name) and bpy.data.objects[name].hide_render],
    }


def main() -> dict[str, object]:
    random.seed(SEED)
    remove_collection(REBUILD_COLLECTION)
    collection = get_collection(REBUILD_COLLECTION)
    materials = build_materials()
    repair_legacy_scene(materials)

    earth = bpy.data.objects["earth_001"]
    cave = bpy.data.objects["cave_001"]
    floor_bvh = bvh_for(earth)
    cave_bvh = bvh_for(cave)
    points = sample_route()
    prepare_track(points, floor_bvh)

    track_result = build_track(points, collection, materials)
    frames = build_supports(points, cave_bvh, floor_bvh, collection, materials)
    build_cart(points, collection, materials)
    lamps = build_lights(points, cave_bvh, collection, materials)
    ore_count = build_ore(points, cave_bvh, collection, materials)
    wet_count = build_wet_patches(points, floor_bvh, collection, materials["wet"])
    cameras = build_cameras(points, lamps, collection)
    configure_lighting(collection)
    validation = validate(points, frames, lamps, ore_count)

    scene = bpy.context.scene
    if cameras:
        scene.camera = cameras[0]
    scene["critical_shift_mine_rebuild_version"] = VERSION
    scene["critical_shift_mine_validation"] = str(validation)
    collection["source_route"] = "prototype/gullet-mine authored Catmull-Rom centerline"
    collection["rail"] = "900 mm gauge, terrain-cleared, curved continuous rails"
    collection["supports"] = "raycast grounded against authored floor, ribs, and crown"
    collection["ore"] = "small embedded emissive seams; restrained point-light accents"
    collection["external_asset"] = "Poly Haven industrial wall lamp 1K glTF, CC0 1.0"
    collection["wet_patch_count"] = wet_count
    collection["track_sleepers"] = track_result["sleepers"]

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    return {
        "version": VERSION,
        "collection": collection.name,
        "objects": len(collection.objects),
        "cameras": [camera.name for camera in cameras],
        "validation": validation,
        "blend_file": bpy.data.filepath,
    }


__result__ = main()
