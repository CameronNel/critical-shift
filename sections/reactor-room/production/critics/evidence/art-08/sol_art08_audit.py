import bpy
import hashlib
import json
import math
import os
import sys
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path

from mathutils import Vector
from mathutils.bvhtree import BVHTree


ARGS = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
if len(ARGS) != 2:
    raise SystemExit("usage: -- OUTPUT_JSON IMMUTABLE_SOURCE")
OUT_PATH = Path(ARGS[0])
SOURCE_PATH = Path(ARGS[1])
DEPSGRAPH = bpy.context.evaluated_depsgraph_get()
SCENE = bpy.context.scene


def r(value, digits=9):
    return round(float(value), digits)


def vec(values, digits=9):
    return [r(v, digits) for v in values]


def collections(ob):
    return sorted(c.name for c in ob.users_collection)


@contextmanager
def evaluated_mesh(ob):
    evaluated = ob.evaluated_get(DEPSGRAPH)
    mesh = None
    try:
        mesh = evaluated.to_mesh()
        yield evaluated, mesh
    finally:
        if mesh is not None:
            evaluated.to_mesh_clear()


def world_bounds(ob):
    evaluated = ob.evaluated_get(DEPSGRAPH)
    if not getattr(evaluated, "bound_box", None):
        return None
    points = [evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box]
    if not points:
        return None
    lo = Vector(min(p[i] for p in points) for i in range(3))
    hi = Vector(max(p[i] for p in points) for i in range(3))
    return lo, hi


def union_bounds(objects):
    bounds = [world_bounds(ob) for ob in objects]
    bounds = [b for b in bounds if b]
    if not bounds:
        return None
    return (
        Vector(min(b[0][i] for b in bounds) for i in range(3)),
        Vector(max(b[1][i] for b in bounds) for i in range(3)),
    )


def object_record(ob):
    b = world_bounds(ob)
    return {
        "name": ob.name,
        "type": ob.type,
        "collections": collections(ob),
        "parent": ob.parent.name if ob.parent else None,
        "children": sorted(ch.name for ch in ob.children),
        "location": vec(ob.matrix_world.translation),
        "bounds": [vec(b[0]), vec(b[1])] if b else None,
        "custom": {str(k): ob[k] for k in sorted(ob.keys())},
    }


def edge_distance_origin_2d(a, b):
    a = Vector((a[0], a[1]))
    b = Vector((b[0], b[1]))
    d = b - a
    if d.length_squared == 0:
        return a.length
    t = max(0.0, min(1.0, -a.dot(d) / d.length_squared))
    return (a + t * d).length


def radial_range(ob):
    with evaluated_mesh(ob) as (evaluated, mesh):
        if not mesh or not mesh.vertices:
            return None
        points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        minimum = min(math.hypot(p.x, p.y) for p in points)
        for edge in mesh.edges:
            minimum = min(minimum, edge_distance_origin_2d(points[edge.vertices[0]], points[edge.vertices[1]]))
        maximum = max(math.hypot(p.x, p.y) for p in points)
        return minimum, maximum


def action_curves(action):
    found = []
    seen = set()

    def add_curve(fc):
        key = id(fc)
        if key in seen:
            return
        seen.add(key)
        found.append(
            {
                "data_path": fc.data_path,
                "array_index": int(fc.array_index),
                "keys": [
                    {
                        "frame": r(k.co.x, 6),
                        "value": r(k.co.y, 9),
                        "interpolation": k.interpolation,
                    }
                    for k in fc.keyframe_points
                ],
            }
        )

    legacy = getattr(action, "fcurves", None)
    if legacy is not None:
        for fc in legacy:
            add_curve(fc)
    for layer in getattr(action, "layers", []):
        for strip in getattr(layer, "strips", []):
            for bag in getattr(strip, "channelbags", []):
                for fc in getattr(bag, "fcurves", []):
                    add_curve(fc)
    return found


def audit_normals():
    summary = {
        "geometry_objects_checked": 0,
        "closed_manifold": 0,
        "open_or_nonmanifold": 0,
        "closed_negative": [],
        "closed_near_zero": [],
        "orientation_conflicts": [],
        "large_closed_checked": 0,
        "large_closed_negative": [],
    }
    focused = {
        "hall_floor_segments": [],
        "sealed_floor_slabs": [],
        "sealed_riser_panels": [],
        "glazing": [],
    }
    for index, ob in enumerate(bpy.data.objects):
        if ob.type not in {"MESH", "CURVE", "SURFACE", "FONT", "META"}:
            continue
        try:
            with evaluated_mesh(ob) as (evaluated, mesh):
                if not mesh or not mesh.polygons or not mesh.vertices:
                    continue
                summary["geometry_objects_checked"] += 1
                world = [evaluated.matrix_world @ v.co for v in mesh.vertices]
                edge_use = defaultdict(list)
                for poly in mesh.polygons:
                    ids = list(poly.vertices)
                    for a, b in zip(ids, ids[1:] + ids[:1]):
                        edge_use[(min(a, b), max(a, b))].append(1 if a < b else -1)
                boundary = sum(len(v) != 2 for v in edge_use.values())
                conflicts = sum(len(v) == 2 and v[0] == v[1] for v in edge_use.values())
                closed = bool(edge_use) and boundary == 0
                volume = 0.0
                mesh.calc_loop_triangles()
                for tri in mesh.loop_triangles:
                    a, b, c = (world[i] for i in tri.vertices)
                    volume += a.dot(b.cross(c)) / 6.0
                bounds = world_bounds(ob)
                dims = bounds[1] - bounds[0] if bounds else Vector((0, 0, 0))
                rec = {
                    "name": ob.name,
                    "type": ob.type,
                    "collections": collections(ob),
                    "signed_volume_m3": r(volume, 9),
                    "boundary_or_nonmanifold_edges": boundary,
                    "orientation_conflicts": conflicts,
                    "dimensions_m": vec(dims, 6),
                }
                if closed:
                    summary["closed_manifold"] += 1
                    if max(dims) >= 0.5:
                        summary["large_closed_checked"] += 1
                    if volume < -1e-8:
                        summary["closed_negative"].append(rec)
                        if max(dims) >= 0.5:
                            summary["large_closed_negative"].append(rec)
                    elif abs(volume) <= 1e-8:
                        summary["closed_near_zero"].append(rec)
                else:
                    summary["open_or_nonmanifold"] += 1
                if conflicts:
                    summary["orientation_conflicts"].append(rec)

                if ob.name.startswith("Hall floor segment"):
                    normals = []
                    for poly in mesh.polygons:
                        center = evaluated.matrix_world @ poly.center
                        normal = evaluated.matrix_world.to_3x3().inverted().transposed() @ poly.normal
                        normals.append((center.z, normal.normalized().z))
                    top_z = max(z for z, nz in normals)
                    bottom_z = min(z for z, nz in normals)
                    rec["top_z"] = r(top_z)
                    rec["top_face_normal_z"] = [r(nz, 6) for z, nz in normals if abs(z - top_z) < 1e-5]
                    rec["bottom_face_normal_z"] = [r(nz, 6) for z, nz in normals if abs(z - bottom_z) < 1e-5]
                    focused["hall_floor_segments"].append(rec)
                elif ob.name.startswith("Sealed floor slab"):
                    focused["sealed_floor_slabs"].append(rec)
                elif ob.name.startswith("Sealed riser chamfer panel"):
                    focused["sealed_riser_panels"].append(rec)
                elif ob.name.startswith("W01 safety glass") or ob.name == "Control floor observation glass":
                    focused["glazing"].append(rec)
        except Exception as exc:
            summary.setdefault("errors", []).append({"name": ob.name, "error": repr(exc)})
        if index and index % 500 == 0:
            print(f"NORMAL_PROGRESS {index}/{len(bpy.data.objects)}", flush=True)
    summary["closed_negative"].sort(key=lambda x: x["signed_volume_m3"])
    summary["large_closed_negative"].sort(key=lambda x: x["signed_volume_m3"])
    return summary, focused


def curve_points(ob):
    points = []
    for spline in ob.data.splines:
        if spline.type == "BEZIER":
            pts = [ob.matrix_world @ p.co for p in spline.bezier_points]
        else:
            pts = [ob.matrix_world @ Vector(p.co[:3]) for p in spline.points]
        if pts:
            points.append(pts)
    return points


def named_curves(prefix):
    return [ob for ob in bpy.data.objects if ob.type == "CURVE" and (ob.name == prefix or ob.name.startswith(prefix + "."))]


def endpoints(ob):
    return [p for spline in curve_points(ob) for p in (spline[0], spline[-1])]


def min_endpoint_distance(prefix_a, prefix_b):
    aa = [p for ob in named_curves(prefix_a) for p in endpoints(ob)]
    bb = [p for ob in named_curves(prefix_b) for p in endpoints(ob)]
    if not aa or not bb:
        return None
    best = min((a - b).length for a in aa for b in bb)
    return r(best)


def point_segment_distance_3d(p, a, b):
    d = b - a
    if d.length_squared == 0:
        return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(d) / d.length_squared))
    return (p - (a + t * d)).length


def point_to_curve_distance(point, curve_ob):
    distances = []
    for spline in curve_points(curve_ob):
        distances.extend(point_segment_distance_3d(point, a, b) for a, b in zip(spline, spline[1:]))
    return min(distances) if distances else float("inf")


def audit_services():
    tracked = [
        "Coolant SUPPLY",
        "Coolant RETURN",
        "Pump rising outlet",
        "Turbine inlet",
        "Turbine return outlet",
        "Manifold wall tie",
        "Manifold upper tie",
        "ECCS maintained loop connection",
        "Sample inlet",
        "Vent relief riser",
        "Bound power loom",
        "Cabinet power drop",
        "Bank desk floor feed",
    ]
    records = []
    for prefix in tracked:
        for ob in named_curves(prefix):
            records.append(
                {
                    "name": ob.name,
                    "radius_m": r(ob.data.bevel_depth),
                    "endpoints": [vec(p) for p in endpoints(ob)],
                }
            )
    supply = bpy.data.objects.get("Coolant SUPPLY")
    return_line = bpy.data.objects.get("Coolant RETURN")
    eccs = bpy.data.objects.get("ECCS maintained loop connection")
    eccs_end = endpoints(eccs)[-1] if eccs else None
    return_start = endpoints(return_line)[0] if return_line else None
    pump_suction = bpy.data.objects.get("Pump suction")
    pump_suction_center = None
    if pump_suction:
        b = world_bounds(pump_suction)
        pump_suction_center = (b[0] + b[1]) / 2
    manifold_links = []
    for wall in named_curves("Manifold wall tie"):
        manifold_links.append(
            {
                "wall_tie": wall.name,
                "nearest_upper_tie_endpoint_gap_m": min(
                    (p - q).length
                    for p in endpoints(wall)
                    for upper in named_curves("Manifold upper tie")
                    for q in endpoints(upper)
                ),
            }
        )
    for item in manifold_links:
        item["nearest_upper_tie_endpoint_gap_m"] = r(item["nearest_upper_tie_endpoint_gap_m"])
    return {
        "curves": records,
        "connections": {
            "supply_to_pump_outlet_endpoint_gap_m": min_endpoint_distance("Coolant SUPPLY", "Pump rising outlet"),
            "supply_to_turbine_inlet_endpoint_gap_m": min_endpoint_distance("Coolant SUPPLY", "Turbine inlet"),
            "return_to_turbine_return_endpoint_gap_m": min_endpoint_distance("Coolant RETURN", "Turbine return outlet"),
            "return_start_to_pump_suction_center_m": r((return_start - pump_suction_center).length) if return_start is not None and pump_suction_center is not None else None,
            "eccs_terminal_to_supply_centerline_m": r(point_to_curve_distance(eccs_end, supply)) if eccs_end is not None and supply else None,
            "manifold_links": manifold_links,
        },
    }


def aabb_overlap(a, b, eps=1e-6):
    return all(a[0][i] <= b[1][i] + eps and b[0][i] <= a[1][i] + eps for i in range(3))


def object_bvh(ob):
    with evaluated_mesh(ob) as (evaluated, mesh):
        if not mesh or not mesh.polygons:
            return None
        vertices = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        polygons = [list(p.vertices) for p in mesh.polygons]
        return BVHTree.FromPolygons(vertices, polygons, all_triangles=False, epsilon=0.00001)


def overlaps(moving, candidates):
    found = []
    for a in moving:
        ba = world_bounds(a)
        if not ba:
            continue
        bvh_a = object_bvh(a)
        if bvh_a is None:
            continue
        for b in candidates:
            bb = world_bounds(b)
            if not bb or not aabb_overlap(ba, bb):
                continue
            bvh_b = object_bvh(b)
            if bvh_b is None:
                continue
            hits = bvh_a.overlap(bvh_b)
            if hits:
                found.append({"moving": a.name, "fixed": b.name, "triangle_pairs": len(hits)})
    return found


def articulation_state(root, rotation_z):
    old = root.rotation_euler.copy()
    root.rotation_euler.z = rotation_z
    bpy.context.view_layer.update()
    b = union_bounds(list(root.children))
    rec = {"rotation_z_rad": r(rotation_z), "child_bounds": [vec(b[0]), vec(b[1])] if b else None}
    root.rotation_euler = old
    bpy.context.view_layer.update()
    return rec


def audit_articulation():
    report = {}
    gate = bpy.data.objects["SERVICE_GATE_PIVOT"]
    gate_children = list(gate.children)
    gate_candidates = [
        ob
        for ob in bpy.data.objects
        if ob not in gate_children
        and ob.type in {"MESH", "CURVE"}
        and any(c.name == "03 POOL AND RAIL" for c in ob.users_collection)
        and (
            ob.name.startswith("Continuous guardrail")
            or ob.name.startswith("Rail upright")
            or ob.name.startswith("Gate hinge")
            or ob.name.startswith("ACKNOWLEDGE")
            or ob.name.startswith("SCRAM")
        )
    ]
    gate_states = {}
    old = gate.rotation_euler.copy()
    for label, angle in (("closed", 0.0), ("open", math.pi / 2)):
        gate.rotation_euler.z = angle
        bpy.context.view_layer.update()
        b = union_bounds(gate_children)
        gate_states[label] = {
            "rotation_z_rad": r(angle),
            "bounds": [vec(b[0]), vec(b[1])],
            "fixed_intersections": overlaps(gate_children, gate_candidates),
        }
    gate.rotation_euler = old
    bpy.context.view_layer.update()
    south_posts = []
    for ob in bpy.data.objects:
        if not ob.name.startswith("Rail upright"):
            continue
        b = world_bounds(ob)
        if b and b[1].y < -3 and abs((b[0].x + b[1].x) / 2) < 1:
            south_posts.append((ob, b))
    south_posts.sort(key=lambda item: item[1][0].x)
    fixed_gap = south_posts[-1][1][0].x - south_posts[0][1][1].x if len(south_posts) == 2 else None
    report["service_gate"] = {
        "root": object_record(gate),
        "fixed_post_gap_m": r(fixed_gap) if fixed_gap is not None else None,
        "states": gate_states,
        "action": action_curves(bpy.data.actions.get("SERVICE_GATE_CLOSED_TO_OPEN")),
    }

    for door, values in (("D01", (math.pi, 1.5 * math.pi)), ("D02", (-math.pi / 2, -math.pi))):
        root = bpy.data.objects[door + "_HINGE"]
        moving = list(root.children)
        candidates = []
        for ob in bpy.data.objects:
            if ob in moving or ob.type not in {"MESH", "CURVE"}:
                continue
            if not any(c.name in {"07 EAST CONTROL ROOM", "08 COMPACT EAST STAIR"} for c in ob.users_collection):
                continue
            if any(s in ob.name.lower() for s in ("floor", "roof", "light", "label", "marking")):
                continue
            candidates.append(ob)
        states = {}
        old = root.rotation_euler.copy()
        for label, angle in (("open", values[0]), ("closed", values[1])):
            root.rotation_euler.z = angle
            bpy.context.view_layer.update()
            b = union_bounds(moving)
            nearby = [ob for ob in candidates if world_bounds(ob) and aabb_overlap(b, world_bounds(ob), eps=0.02)]
            states[label] = {
                "rotation_z_rad": r(angle),
                "bounds": [vec(b[0]), vec(b[1])],
                "fixed_intersections": overlaps(moving, nearby),
            }
        root.rotation_euler = old
        bpy.context.view_layer.update()
        report[door] = {
            "root": object_record(root),
            "states": states,
            "action": action_curves(bpy.data.actions.get(door + "_OPEN_TO_CLOSED")),
        }
    return report


def interval_overlap(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


def audit_banks():
    report = {}
    original_frame = SCENE.frame_current
    for bank, x in (("A", -1.4), ("B", 1.4)):
        root = bpy.data.objects[f"BANK_{bank}_MOVING"]
        fixed = bpy.data.objects[f"BANK_{bank}_FIXED_HOUSING"]
        top = bpy.data.objects[f"{bank} top sliding engagement"]
        column = bpy.data.objects[f"BANK_{bank}_DRIVE_COLUMN"]
        guides = [ob for ob in bpy.data.objects if ob.name.startswith("Submerged guide body")]
        guide = min(guides, key=lambda ob: abs(world_bounds(ob)[0].x + world_bounds(ob)[1].x - 2 * x))
        states = []
        for frame in (1, 90, 180, 192, 196, 201, 240):
            SCENE.frame_set(frame)
            bpy.context.view_layer.update()
            fb = world_bounds(fixed)
            tb = world_bounds(top)
            cb = world_bounds(column)
            gb = world_bounds(guide)
            states.append(
                {
                    "frame": frame,
                    "root_world_z": r(root.matrix_world.translation.z),
                    "fixed_bounds_z": [r(fb[0].z), r(fb[1].z)],
                    "top_sliding_bounds_z": [r(tb[0].z), r(tb[1].z)],
                    "drive_column_bounds_z": [r(cb[0].z), r(cb[1].z)],
                    "submerged_guide_bounds_z": [r(gb[0].z), r(gb[1].z)],
                    "upper_engagement_m": r(interval_overlap(fb[0].z, fb[1].z, tb[0].z, tb[1].z)),
                    "lower_engagement_m": r(interval_overlap(cb[0].z, cb[1].z, gb[0].z, gb[1].z)),
                    "upper_axis_offset_xy_m": r(math.hypot((fb[0].x + fb[1].x - tb[0].x - tb[1].x) / 2, (fb[0].y + fb[1].y - tb[0].y - tb[1].y) / 2)),
                    "lower_axis_offset_xy_m": r(math.hypot((cb[0].x + cb[1].x - gb[0].x - gb[1].x) / 2, (cb[0].y + cb[1].y - gb[0].y - gb[1].y) / 2)),
                }
            )
        SCENE.frame_set(1)
        bpy.context.view_layer.update()
        report[bank] = {
            "root": object_record(root),
            "fixed": object_record(fixed),
            "fixed_is_descendant_of_moving": fixed.parent == root,
            "moving_child_count": len(root.children),
            "action": action_curves(root.animation_data.action if root.animation_data else None),
            "states": states,
        }
    SCENE.frame_set(original_frame)
    bpy.context.view_layer.update()
    return report


def projection_gap(objects):
    if len(objects) != 2:
        return None
    bounds_points = []
    centers = []
    for ob in objects:
        evaluated = ob.evaluated_get(DEPSGRAPH)
        pts = [evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box]
        bounds_points.append(pts)
        centers.append(sum(pts, Vector()) / len(pts))
    axis = Vector((centers[1].x - centers[0].x, centers[1].y - centers[0].y))
    axis.normalize()
    intervals = []
    for pts in bounds_points:
        values = [axis.dot(Vector((p.x, p.y))) for p in pts]
        intervals.append((min(values), max(values)))
    intervals.sort()
    return intervals[1][0] - intervals[0][1]


def convex_hull(points):
    pts = sorted(set((r(p[0], 6), r(p[1], 6)) for p in points))
    if len(pts) <= 1:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def point_polygon_distance(point, polygon):
    p = Vector(point)
    if point_in_polygon(point, polygon):
        return 0.0
    return min(edge_distance_origin_2d(Vector(a) - p, Vector(b) - p) for a, b in zip(polygon, polygon[1:] + polygon[:1]))


def route_obstacles():
    result = []
    for ob in bpy.data.objects:
        if ob.type not in {"MESH", "CURVE"} or ob.hide_render:
            continue
        in_equipment = any(c.name == "05 PERIMETER EQUIPMENT" for c in ob.users_collection)
        is_column = ob.name.startswith("Column ")
        if not (in_equipment or is_column):
            continue
        b = world_bounds(ob)
        if not b or b[1].z < 0.05 or b[0].z > 2.05:
            continue
        evaluated = ob.evaluated_get(DEPSGRAPH)
        points = [evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box]
        hull = convex_hull([(p.x, p.y) for p in points])
        if len(hull) < 3:
            continue
        radii = [math.hypot(x, y) for x, y in hull]
        result.append({"name": ob.name, "hull": hull, "rmin": min(radii), "rmax": max(radii)})
    return result


def polygon_edge_distance(point, polygon):
    p = Vector(point)
    return min(edge_distance_origin_2d(Vector(a) - p, Vector(b) - p) for a, b in zip(polygon, polygon[1:] + polygon[:1]))


def polar_route_test(clearance):
    hall = [(-6, 10.8), (6, 10.8), (10.8, 6), (10.8, -6), (6, -10.8), (-6, -10.8), (-10.8, -6), (-10.8, 6)]
    obstacles = route_obstacles()
    radial_step = 0.05
    angle_step_deg = 1.0
    radii = [5.2 + clearance + i * radial_step for i in range(int((10.05 - (5.2 + clearance)) / radial_step) + 1)]
    free = []
    for degree in range(360):
        angle = math.radians(degree)
        row = []
        for radius in radii:
            point = (radius * math.cos(angle), radius * math.sin(angle))
            okay = point_in_polygon(point, hall) and polygon_edge_distance(point, hall) >= clearance
            if okay:
                for obstacle in obstacles:
                    if radius < obstacle["rmin"] - clearance or radius > obstacle["rmax"] + clearance:
                        continue
                    if point_polygon_distance(point, obstacle["hull"]) < clearance:
                        okay = False
                        break
            row.append(okay)
        free.append(row)

    def components(row):
        result = []
        start = None
        for i, value in enumerate(row + [False]):
            if value and start is None:
                start = i
            elif not value and start is not None:
                result.append(set(range(start, i)))
                start = None
        return result

    initial_components = components(free[0])
    cycle = None
    for initial in initial_components:
        reachable = set(initial)
        for degree in range(1, 360):
            seeds = {j for i in reachable for j in (i - 1, i, i + 1) if 0 <= j < len(radii) and free[degree][j]}
            expanded = set()
            for component in components(free[degree]):
                if component & seeds:
                    expanded |= component
            reachable = expanded
            if not reachable:
                break
        if reachable and any(abs(i - j) <= 1 for i in reachable for j in initial):
            cycle = {"start_indices": sorted(initial), "end_indices": sorted(reachable)}
            break
    return {
        "required_half_width_m": r(clearance),
        "tested_route_width_m": r(2 * clearance),
        "angle_step_deg": angle_step_deg,
        "radial_step_m": radial_step,
        "obstacle_count": len(obstacles),
        "cycle_found": cycle is not None,
        "cycle_start_radius_range_m": [r(radii[min(cycle["start_indices"])]), r(radii[max(cycle["start_indices"])] )] if cycle else None,
        "minimum_free_radial_samples_per_angle": min(sum(row) for row in free),
        "angles_with_no_free_sample": [i for i, row in enumerate(free) if not any(row)],
    }


def audit_clearances():
    report = {}
    service = [ob for ob in bpy.data.objects if ob.name.startswith("Service ring slab")]
    service_ranges = [radial_range(ob) for ob in service]
    report["service_ring"] = {
        "pieces": len(service),
        "inner_radius_m": r(min(x[0] for x in service_ranges)),
        "outer_radius_m": r(max(x[1] for x in service_ranges)),
        "radial_width_m": r(max(x[1] for x in service_ranges) - min(x[0] for x in service_ranges)),
    }
    hall = [ob for ob in bpy.data.objects if ob.name.startswith("Hall floor segment")]
    hb = union_bounds(hall)
    report["hall_floor_span_m"] = vec(hb[1] - hb[0])
    water = bpy.data.objects.get("Water surface")
    pool_bottom = bpy.data.objects.get("Pool bottom")
    wb = world_bounds(water)
    pb = world_bounds(pool_bottom)
    report["pool"] = {
        "water_bounds": [vec(wb[0]), vec(wb[1])],
        "bottom_bounds": [vec(pb[0]), vec(pb[1])],
        "water_surface_to_bottom_vertical_m": r(wb[1].z - pb[1].z),
    }
    turbine = bpy.data.objects["06 turbine skid"]
    tr = radial_range(turbine)
    report["turbine_actual_skid_to_service_ring_m"] = r(tr[0] - report["service_ring"]["outer_radius_m"])
    report["turbine_p02_envelope_to_service_ring_m"] = r(math.hypot(7.5 - 1.05, 3.0 - 2.1) - 5.2)

    portal = {}
    for prefix in ("FUEL HANDLING.jamb liner", "COOLING PLANT.jamb liner", "MAIN ACCESS.jamb liner", "Control route jamb"):
        obs = [ob for ob in bpy.data.objects if ob.name == prefix or ob.name.startswith(prefix + ".")]
        portal[prefix] = {"objects": [ob.name for ob in obs], "clear_gap_m": r(projection_gap(obs)) if len(obs) == 2 else None}
    report["portal_clearances"] = portal

    d01_south = bpy.data.objects["Stair west lower south"]
    d01_north = bpy.data.objects["Stair west lower north"]
    bs, bn = world_bounds(d01_south), world_bounds(d01_north)
    d02_west = bpy.data.objects["Control north west return"]
    d02_east = bpy.data.objects["Control north east return"]
    bw, be = world_bounds(d02_west), world_bounds(d02_east)
    report["door_openings"] = {
        "D01_clear_width_m": r(bn[0].y - bs[1].y),
        "D01_clear_height_m": r(world_bounds(bpy.data.objects["Stair west upper"])[0].z),
        "D02_clear_width_m": r(be[0].x - bw[1].x),
        "D02_clear_height_m": r(world_bounds(bpy.data.objects["Control D02 lintel"])[0].z - 10.0),
    }
    stair_walls = [bpy.data.objects[n] for n in ("Stair east enclosure", "Stair west lower south", "Stair west lower north", "Stair west upper", "Stair north enclosure", "Stair south lower enclosure", "Stair south upper east")]
    sb = union_bounds(stair_walls)
    report["stair_enclosure_outer_bounds"] = [vec(sb[0]), vec(sb[1])]
    report["stair_enclosure_plan_m"] = [r(sb[1].x - sb[0].x), r(sb[1].y - sb[0].y)]
    handrails = named_curves("Continuous stair handrail")
    rail_rows = []
    for ob in handrails:
        pts = [p for spline in curve_points(ob) for p in spline]
        rail_rows.append({"name": ob.name, "mean_y": r(sum(p.y for p in pts) / len(pts)), "z_min": r(min(p.z for p in pts)), "z_max": r(max(p.z for p in pts)), "radius": r(ob.data.bevel_depth)})
    pairs = []
    for i in range(0, len(rail_rows), 2):
        pair = sorted(rail_rows[i : i + 2], key=lambda x: x["mean_y"])
        if len(pair) == 2:
            pairs.append(r(pair[1]["mean_y"] - pair[0]["mean_y"] - pair[0]["radius"] - pair[1]["radius"]))
    report["stair_flight_clear_widths_m"] = pairs
    report["stair_treads_per_flight"] = {f"F{i}": len([ob for ob in bpy.data.objects if ob.name.startswith(f"F{i} tread")]) for i in range(1, 5)}
    report["stair_riser_meshes_total_excluding_four_landing_rises"] = len([ob for ob in bpy.data.objects if ob.name.startswith("Stair riser")])
    landings = [ob for ob in bpy.data.objects if ob.name.startswith("Stair full landing")]
    report["landing_count"] = len(landings)
    report["landing_short_dimensions_m"] = sorted(r(min((world_bounds(ob)[1] - world_bounds(ob)[0]).x, (world_bounds(ob)[1] - world_bounds(ob)[0]).y)) for ob in landings)

    control_east = world_bounds(bpy.data.objects["Control east wall"])
    control_south = world_bounds(bpy.data.objects["Control south wall"])
    control_north = union_bounds([d02_west, d02_east])
    floor = world_bounds(bpy.data.objects["Control room main floor"])
    report["control_room"] = {
        "finished_floor_top_z_m": r(floor[1].z),
        "clear_y_m": r(control_north[0].y - control_south[1].y),
        "center_y_m": r((control_north[0].y + control_south[1].y) / 2),
        "east_inner_face_x_m": r(control_east[0].x),
        "operator_desks": len([ob for ob in bpy.data.objects if ob.name.startswith("OPERATOR DESK.plinth")]),
    }
    controls = {}
    for name in ("SCRAM_BUTTON", "ALARM_ACK", "BYPASS_SWITCH"):
        obs = [ob for ob in bpy.data.objects if ob.name == name or ob.name.startswith(name + ".")]
        controls[name] = [object_record(ob) for ob in obs]
    report["south_controls"] = controls

    support_registry = json.loads(SCENE.get("support_registry", "[]"))
    contacts = []
    for item in support_registry:
        ob = bpy.data.objects.get(item["object"])
        if not ob:
            contacts.append({"object": item["object"], "missing": True})
            continue
        b = world_bounds(ob)
        contacts.append({"object": ob.name, "expected_z": r(item["expected_z"]), "actual_bottom_z": r(b[0].z), "delta_m": r(b[0].z - item["expected_z"])})
    report["registered_support_contacts"] = {
        "count": len(contacts),
        "max_abs_delta_m": r(max(abs(c.get("delta_m", 0)) for c in contacts)),
        "outside_5mm": [c for c in contacts if c.get("missing") or abs(c.get("delta_m", 0)) > 0.005],
        "all": contacts,
    }
    report["continuous_route_tests"] = [polar_route_test(0.60), polar_route_test(0.65)]
    return report


def audit_scuffs_and_duplicates():
    scuffs = [ob for ob in bpy.data.objects if ob.name.startswith("Route surface scuff")]
    scuff_records = []
    for ob in scuffs:
        with evaluated_mesh(ob) as (evaluated, mesh):
            points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
            angles = [math.atan2(p.y, p.x) % (2 * math.pi) for p in points]
            sector_ids = sorted(set(int(a / (2 * math.pi / 32)) for a in angles))
            scuff_records.append(
                {
                    "name": ob.name,
                    "z_range_m": [r(min(p.z for p in points)), r(max(p.z for p in points))],
                    "radial_range_m": [r(min(math.hypot(p.x, p.y) for p in points)), r(max(math.hypot(p.x, p.y) for p in points))],
                    "sector_ids": sector_ids,
                    "visible_shadow": bool(ob.visible_shadow),
                    "world_normal_z": [r((evaluated.matrix_world.to_3x3().inverted().transposed() @ p.normal).normalized().z, 6) for p in mesh.polygons],
                }
            )

    signatures = defaultdict(list)
    for ob in bpy.data.objects:
        if ob.type not in {"MESH", "CURVE"}:
            continue
        b = world_bounds(ob)
        if not b or max(b[1] - b[0]) < 0.05:
            continue
        signature = tuple(round(v, 5) for p in b for v in p)
        signatures[signature].append(ob.name)
    duplicates = [{"bounds": list(sig), "objects": sorted(names)} for sig, names in signatures.items() if len(names) > 1]
    return {"scuffs": scuff_records, "exact_world_bound_duplicates": duplicates}


def external_dependencies():
    paths = []
    datablocks = []
    datablocks.extend(("IMAGE", block.name, block.filepath) for block in bpy.data.images if block.filepath)
    datablocks.extend(("FONT", block.name, block.filepath) for block in bpy.data.fonts if block.filepath)
    datablocks.extend(("MOVIECLIP", block.name, block.filepath) for block in bpy.data.movieclips if block.filepath)
    datablocks.extend(("SOUND", block.name, block.filepath) for block in bpy.data.sounds if block.filepath)
    for kind, name, raw in datablocks:
        resolved = bpy.path.abspath(raw)
        paths.append({"type": kind, "name": name, "raw": raw, "resolved": resolved, "exists": Path(resolved).exists()})
    libraries = [{"name": lib.name, "filepath": lib.filepath, "resolved": bpy.path.abspath(lib.filepath), "exists": Path(bpy.path.abspath(lib.filepath)).exists()} for lib in bpy.data.libraries]
    return {"libraries": libraries, "file_datablocks": paths, "missing": [p for p in paths + libraries if not p["exists"]]}


def main():
    print("SOL_ART08_AUDIT_BEGIN", flush=True)
    blend_path = Path(bpy.data.filepath)
    actions = []
    for action in bpy.data.actions:
        actions.append({"name": action.name, "fake_user": bool(action.use_fake_user), "curves": action_curves(action)})
    normals, focused = audit_normals()
    result = {
        "audit": {
            "mode": "read-only reopen; no save/render",
            "blender_version": bpy.app.version_string,
            "blend_path": str(blend_path),
            "blend_sha256": hashlib.sha256(blend_path.read_bytes()).hexdigest(),
            "source_path": str(SOURCE_PATH),
            "source_sha256": hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest(),
            "scene_source_sha256": SCENE.get("source_sha256"),
            "scene_art_revision": SCENE.get("art_revision"),
            "scene_authoring_source": SCENE.get("authoring_source"),
            "scene_layout_authority": SCENE.get("layout_authority"),
            "scene_visual_target": SCENE.get("visual_target"),
            "scene_counts": {"objects": len(bpy.data.objects), "meshes": len(bpy.data.meshes), "materials": len(bpy.data.materials)},
            "profile": {k: os.environ.get(k) for k in ("BLENDER_USER_CONFIG", "BLENDER_USER_SCRIPTS", "BLENDER_USER_DATAFILES")},
        },
        "external_dependencies": external_dependencies(),
        "actions": actions,
        "normals": normals,
        "focused_normals": focused,
        "articulation": audit_articulation(),
        "banks": audit_banks(),
        "clearances": audit_clearances(),
        "services": audit_services(),
        "surface_and_duplicate_checks": audit_scuffs_and_duplicates(),
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("SOL_ART08_AUDIT_JSON=" + str(OUT_PATH), flush=True)
    print("SOL_ART08_AUDIT_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
