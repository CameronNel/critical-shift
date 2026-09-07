"""Read-only, CPU-only objective validation of the authoritative Waste Storage blend.

Run in a NEW Blender process with section-local BLENDER_USER_RESOURCES::

  blender --background --factory-startup path/to/waste-storage.blend --python-exit-code 2 \
      --python sections/waste-storage/production/validate_scene.py -- \
      --output sections/waste-storage/production/validation/cycle-01.json

Never renders, changes geometry, saves a blend, or accesses a live Blender instance.
Exit status 1 means an objective check failed. PASS here is technical evidence only;
pixel review, runtime collision, final renders and complete cold-start acceptance
remain separate gates. A missing specification or unperformed mandatory check fails.

Support schema: roots have support_required=true, support_target (object name),
support_direction (JSON vector in world coordinates), support_max_gap <= .005,
support_max_penetration <= .002, support_angle_tolerance_deg <= 12, and
support_anchors (JSON child-empty names). Geometry has support_role architectural
or assembly_part; the latter has support_root naming its registered ancestor.
All assemblies use explicit anchors, including irregular assemblies. An anchor
must touch actual assembly geometry as well as the intended target surface.
"""

import argparse
import collections
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
import traceback

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


EPS = 1e-7
SECTION = Path(__file__).resolve().parents[1]
CHECKS = []


def emit(name, passed, **evidence):
    CHECKS.append(dict(name=name, status="PASS" if passed else "FAIL", **evidence))


def prop(value, fallback=None):
    if value is None:
        return fallback
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return value
    return value


def vec(value):
    return Vector(tuple(float(v) for v in prop(value)))


def rounded(value):
    return [round(float(v), 7) for v in value]


def digest(path):
    path = Path(path)
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inside_path(path, root):
    try:
        Path(path).resolve().relative_to(Path(root).resolve())
        return True
    except ValueError:
        return False


def ancestors(obj):
    seen = set()
    while obj.parent and obj.parent.name not in seen:
        obj = obj.parent
        seen.add(obj.name)
        yield obj


class Geometry:
    """Snapshot of actual evaluated polygons in world space, without source edits."""

    def __init__(self, obj, depsgraph):
        self.obj = obj
        self.name = obj.name
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            self.vertices = [evaluated.matrix_world @ v.co for v in mesh.vertices]
            self.faces = [tuple(p.vertices) for p in mesh.polygons]
            mesh.calc_loop_triangles()
            self.triangles = [tuple(t.vertices) for t in mesh.loop_triangles]
            self.material_indices = [p.material_index for p in mesh.polygons]
            self.materials = list(evaluated.data.materials)
        finally:
            evaluated.to_mesh_clear()
        self.lo = Vector(tuple(min(v[i] for v in self.vertices) for i in range(3)))
        self.hi = Vector(tuple(max(v[i] for v in self.vertices) for i in range(3)))
        # Blender curve/font conversion duplicates caps' rim vertices. Analyze
        # topology after a 1 micrometre positional weld without editing the mesh.
        weld_keys = [tuple(round(float(component), 6) for component in point) for point in self.vertices]
        weld_ids = {key: index for index, key in enumerate(dict.fromkeys(weld_keys))}
        self.welded_ids = [weld_ids[key] for key in weld_keys]
        edges = collections.Counter(tuple(sorted((self.welded_ids[face[i]], self.welded_ids[face[(i+1) % len(face)]])))
                                    for face in self.faces for i in range(len(face))
                                    if self.welded_ids[face[i]] != self.welded_ids[face[(i+1) % len(face)]])
        self.closed = bool(edges) and all(count == 2 for count in edges.values())
        original_edges = {tuple(sorted((face[i], face[(i+1) % len(face)]))) for face in self.faces for i in range(len(face))}
        self.edges = [(self.vertices[a], self.vertices[b]) for a, b in original_edges]
        self.bvh = BVHTree.FromPolygons(self.vertices, self.triangles, all_triangles=True, epsilon=0)

    def ray(self, origin, direction, distance):
        location, normal, index, length = self.bvh.ray_cast(origin, direction, distance)
        if location is None:
            return None
        return location, normal, index, length

    def point_inside(self, point):
        if not self.closed:
            return False
        if not all(self.lo[i] - EPS <= point[i] <= self.hi[i] + EPS for i in range(3)):
            return False
        # Odd/even crossing on an oblique ray; avoid coplanar box-face rays.
        direction = Vector((.917631, .283711, .277089)).normalized()
        origin = point.copy()
        count = 0
        for _ in range(500):
            hit = self.ray(origin, direction, 1000)
            if hit is None:
                return bool(count % 2)
            count += 1
            origin = hit[0] + direction * 1e-5
        raise RuntimeError(f"Containment ray exceeded 500 crossings in {self.name}")


def triangle_box_overlap(points, lo, hi):
    """Separating-axis test: triangle normal, 3 box axes, 9 edge cross axes."""
    center = (lo + hi) / 2
    half = (hi - lo) / 2
    vertices = [point - center for point in points]
    edges = [vertices[(i + 1) % 3] - vertices[i] for i in range(3)]
    box_axes = [Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))]
    axes = box_axes + [edges[0].cross(edges[1])]
    axes += [edge.cross(axis) for edge in edges for axis in box_axes]
    for axis in axes:
        if axis.length_squared < 1e-20:
            continue
        projections = [point.dot(axis) for point in vertices]
        radius = sum(abs(axis[i]) * half[i] for i in range(3))
        if min(projections) > radius + EPS or max(projections) < -radius - EPS:
            return False
    return True


def box_hits(geometry, lo, hi):
    # A mathematically shared boundary is not an obstruction. Twenty micrometres
    # removes floating-point edge ambiguity without relaxing metric clearances.
    lo, hi = lo + Vector((.00002,)*3), hi - Vector((.00002,)*3)
    if any(geometry.hi[i] < lo[i] or geometry.lo[i] > hi[i] for i in range(3)):
        return None
    for triangle in geometry.triangles:
        if triangle_box_overlap([geometry.vertices[i] for i in triangle], lo, hi):
            return "evaluated_triangle_intersects_volume"
    if geometry.point_inside((lo + hi) / 2):
        return "clearance_volume_contained_inside_geometry"
    return None


def sample_interval(start, end, maximum_step):
    count = max(1, math.ceil((end - start) / maximum_step))
    return [start + (end - start) * i / count for i in range(count + 1)]


def connected_surfaces(first, second, maximum_gap=.005):
    """Actual mesh surface contact or solid overlap; boxes only reject far pairs."""
    if any(first.hi[i]+maximum_gap < second.lo[i] or second.hi[i]+maximum_gap < first.lo[i] for i in range(3)):
        return False
    if first.bvh.overlap(second.bvh):
        return True
    if first.point_inside(second.vertices[0]) or second.point_inside(first.vertices[0]):
        return True
    for source, target in ((first, second), (second, first)):
        for point in source.vertices:
            nearest = target.bvh.find_nearest(point, maximum_gap + EPS)
            if nearest[0] is not None and nearest[3] <= maximum_gap + EPS:
                return True
    # Nearest points may be in two edge interiors (e.g. a long conduit and a
    # narrow saddle), with neither mesh vertex near the other surface.
    for a, b in first.edges:
        for c, d in second.edges:
            if any(max(a[i], b[i])+maximum_gap < min(c[i], d[i]) or
                   max(c[i], d[i])+maximum_gap < min(a[i], b[i]) for i in range(3)):
                continue
            if segment_distance_squared(a, b, c, d) <= (maximum_gap+EPS)**2:
                return True
    return False


def segment_distance_squared(p1, q1, p2, q2):
    d1, d2, r = q1-p1, q2-p2, p1-p2
    a, e, f = d1.dot(d1), d2.dot(d2), d2.dot(r)
    clamp = lambda value: max(0., min(1., value))
    if a <= 1e-20 and e <= 1e-20:
        return r.length_squared
    if a <= 1e-20:
        s, t = 0., clamp(f/e)
    else:
        c = d1.dot(r)
        if e <= 1e-20:
            t, s = 0., clamp(-c/a)
        else:
            b = d1.dot(d2)
            denominator = a*e-b*b
            s = clamp((b*f-c*e)/denominator) if abs(denominator) > 1e-20 else 0.
            t = (b*s+f)/e
            if t < 0:
                t, s = 0., clamp(-c/a)
            elif t > 1:
                t, s = 1., clamp((b-c)/a)
    return ((p1+d1*s)-(p2+d2*t)).length_squared


def signed_mesh_volume(geometry):
    # Translation-invariant double precision avoids catastrophic cancellation
    # for millimetre instruments positioned several metres from the room origin.
    origin = tuple(float(v) for v in geometry.vertices[0])
    shifted = [tuple(float(v[i])-origin[i] for i in range(3)) for v in geometry.vertices]
    terms = []
    for indices in geometry.triangles:
        a, b, c = [shifted[i] for i in indices]
        terms.append((a[0]*(b[1]*c[2]-b[2]*c[1]) + a[1]*(b[2]*c[0]-b[0]*c[2]) + a[2]*(b[0]*c[1]-b[1]*c[0]))/6.)
    return math.fsum(terms)


def extract_geometry():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    result = {}
    errors = []
    for obj in bpy.context.scene.objects:
        if obj.type not in {"MESH", "CURVE", "FONT", "SURFACE", "META"}:
            continue
        try:
            geometry = Geometry(obj, depsgraph)
            if geometry.triangles:
                result[obj.name] = geometry
            else:
                errors.append(dict(object=obj.name, error="No evaluated triangles"))
        except Exception as error:
            errors.append(dict(object=obj.name, error=str(error)))
    emit("evaluated_geometry_snapshot", bool(result) and not errors,
         evaluated_objects=len(result), triangle_count=sum(len(g.triangles) for g in result.values()), errors=errors)
    return result


def geometry_specification(interface, stage):
    """Derive immutable tests from the published interface, not collision labels.

    Geometry target names were confirmed against the original source builder.
    Slice depth is an explicit temporary source decision (4.6 m), never substituted
    for the full 18 m handoff envelope. The absent rear/full areas stay out of scope.
    """
    if interface.get("geometry_validation"):
        return interface["geometry_validation"]
    bounds = interface["interior_bounds"]
    lo, hi = vec(bounds["min"]), vec(bounds["max"])
    depth = hi.y if stage == "full" else 4.6
    specification = dict(floor_target="Floor", surface_probes=[], clearance_volumes=[],
                         render_config=dict(engine="CYCLES", resolution_x=1280, resolution_y=800,
                             resolution_percentage=100, image_format="PNG", view_transform="AgX", samples=64,
                             use_denoising=True, film_transparent=False, seed=4217))
    def probe(name, target, origin, direction, expected):
        specification["surface_probes"].append(dict(name=name, target=target, origin=origin,
              direction=direction, expected_distance_m=expected, tolerance_m=.005))
    probe("floor_receiving_elevation", "Floor", (0, 1, 1), (0, 0, -1), 1-lo.z)
    probe("west_interior_plane", "West_Wall", (0, depth/2, 3.3), (-1, 0, 0), -lo.x)
    probe("east_interior_plane", "East_Wall_Rear", (0, depth-.5, 3.3), (1, 0, 0), hi.x)
    probe("entry_interior_plane", "Front_Wall_East", (3, 1, 3.6), (0, -1, 0), 1-lo.y)
    probe("ceiling_clear_height", "Ceiling", (0, depth/2, 1), (0, 0, 1), hi.z-1)
    probe("floor_rear_elevation", "Floor", (0, depth-.5, 1), (0, 0, -1), 1-lo.z)
    if stage == "full":
        probe("rear_interior_plane", "Rear_Wall_Right", (3, 15, 3.6), (0, 1, 0), hi.y-15)
    def volume(name, purpose, minimum, maximum):
        specification["clearance_volumes"].append(dict(name=name, purpose=purpose, min=minimum, max=maximum))
    portals = list(interface["portals"])
    if stage == "full":
        portals += interface.get("internal_portals", [])
    for portal in portals:
        if stage == "slice" and portal["id"] == "WS_DISPATCH":
            continue
        center = vec(portal["center"])
        normal = vec(portal.get("outward_normal", portal.get("normal")))
        horizontal_axis = 1 if abs(normal.x) > .5 else 0
        normal_axis = 1-horizontal_axis
        low, high = center.copy(), center.copy()
        low[horizontal_axis] -= portal["clear_width"] / 2 - .002
        high[horizontal_axis] += portal["clear_width"] / 2 - .002
        low[normal_axis] -= .18
        high[normal_axis] += .18
        low.z += .021
        high.z += portal["clear_height"]-.002
        volume(portal["id"]+"_aperture", "portal", list(low), list(high))
    # Only receiving aperture/short entry movement is part of the slice gate.
    volume("entry_cart_approach", "cart_route", [-1.48, .02, .021], [1.48, .68, 2.4])
    if stage == "full":
        targets = interface["clearance_targets"]
        route = targets["center_cart_route"]
        x1, y1, x2, y2 = route["bounds_xy"]
        volume("center_cart_route", "cart_route", [x1, y1, .021], [x2, y2, route["minimum_clear_height"]])
        for key in ("receiving_turn_circle", "rear_turn_circle"):
            circle = targets[key]
            x, y, z = circle["center"]
            radius = circle["diameter"] / 2
            volume(key+"_conservative_square", "cart_turn", [x-radius, y-radius, .021], [x+radius, y+radius, 2.4])
        volume("entry_to_turn_cart_connection", "cart_route", [-1.48, .65, .021], [1.48, 1, 2.4])
        volume("receiving_to_center_cart_connection", "cart_route", [-.90, 4.20, .021], [.90, 4.6, 2.4])
        volume("rear_to_dispatch_cart_connection", "cart_route", [-1.18, 17.4, .021], [1.18, 17.99, 2.4])
        volume("personnel_to_receiving_walk", "player_route", [1.7, 1.9, .021], [5.9, 2.9, 2.2])
        volume("booth_to_receiving_walk", "player_route", [-2.4, 1.7, .021], [-1.65, 2.7, 2.2])
        declared = prop(bpy.context.scene.get("route_clearances"), [])
        circulation = list(specification["clearance_volumes"])
        for item in declared:
            if item.get("purpose") in {"cell_access", "maintenance_access"}:
                specification["clearance_volumes"].append(dict(item))
                # Test the intervening floor strip as well as the working box;
                # merely checking two disjoint boxes would not prove a route.
                a_lo, a_hi = vec(item["min"]), vec(item["max"])
                candidates = []
                for corridor in circulation:
                    if corridor["purpose"] not in {"cart_route", "cart_turn"}:
                        continue
                    b_lo, b_hi = vec(corridor["min"]), vec(corridor["max"])
                    for axis in (0, 1):
                        across = 1-axis
                        width_min = max(a_lo[across], b_lo[across])
                        width_max = min(a_hi[across], b_hi[across])
                        if width_max-width_min < .996:
                            continue
                        if a_hi[axis] < b_lo[axis]:
                            edge_min, edge_max = a_hi[axis], b_lo[axis]
                        elif b_hi[axis] < a_lo[axis]:
                            edge_min, edge_max = b_hi[axis], a_lo[axis]
                        else:
                            edge_min = edge_max = max(a_lo[axis], b_lo[axis])
                        if edge_max-edge_min > 2:
                            continue
                        bridge_lo, bridge_hi = a_lo.copy(), a_hi.copy()
                        bridge_lo[across], bridge_hi[across] = width_min, width_max
                        bridge_lo[axis], bridge_hi[axis] = edge_min-.01, edge_max+.01
                        bridge_lo.z, bridge_hi.z = .021, min(a_hi.z, b_hi.z)
                        candidates.append((edge_max-edge_min, list(bridge_lo), list(bridge_hi)))
                if candidates:
                    distance, bridge_lo, bridge_hi = min(candidates, key=lambda c: c[0])
                    if distance > .0001:
                        volume(item["name"]+"_connection_to_circulation", "player_route", bridge_lo, bridge_hi)
    return specification


def validate_support(geometries):
    roots = {o.name: o for o in bpy.context.scene.objects if bool(o.get("support_required", False))}
    registration_errors = []
    members = collections.defaultdict(list)
    for name, geometry in geometries.items():
        obj = geometry.obj
        role = obj.get("support_role")
        if role == "architectural":
            if "00_ARCHITECTURE" not in {collection.name for collection in obj.users_collection}:
                registration_errors.append(dict(object=name, error="Architectural exemption used outside the dedicated architecture collection"))
            continue
        root_name = obj.get("support_root")
        if role != "assembly_part":
            registration_errors.append(dict(object=name, error="Missing/unknown support_role"))
        elif root_name not in roots:
            registration_errors.append(dict(object=name, error="No registered support_root", support_root=root_name))
        elif root_name not in {a.name for a in ancestors(obj)}:
            registration_errors.append(dict(object=name, error="support_root is not an ancestor", support_root=root_name))
        else:
            members[root_name].append(geometry)
    # Catch roots carrying partial metadata without the mandatory registration flag.
    for obj in bpy.context.scene.objects:
        if obj.get("support_target") and obj.name not in roots:
            registration_errors.append(dict(object=obj.name, error="support_target lacks support_required registration"))
    emit("support_registration", bool(roots) and not registration_errors,
         registered_assemblies=len(roots), architectural_objects=sum(g.obj.get("support_role") == "architectural" for g in geometries.values()),
         assembly_parts=sum(len(v) for v in members.values()), errors=registration_errors)
    dependency_rows = []
    for name in roots:
        current = name
        chain = []
        errors = []
        while True:
            if current in chain:
                errors.append("Support dependency cycle")
                break
            chain.append(current)
            target_name = roots[current].get("support_target")
            target = geometries.get(target_name)
            if not target:
                errors.append("Support chain target has no evaluated geometry")
                break
            if target.obj.get("support_role") == "architectural":
                chain.append(target_name)
                break
            current = target.obj.get("support_root")
            if current not in roots:
                errors.append("Support chain has no registered ancestor or architectural terminus")
                break
        dependency_rows.append(dict(root=name, support_chain=chain, errors=errors))
    emit("support_chains_reach_architecture", bool(dependency_rows) and not any(r["errors"] for r in dependency_rows),
         assemblies=dependency_rows)
    results = []
    claimed_anchors = set()
    for name, root in roots.items():
        result = dict(root=name, target=root.get("support_target"), irregular=bool(root.get("support_irregular", False)), anchors=[], errors=[])
        errors = result["errors"]
        target = geometries.get(root.get("support_target"))
        if not target:
            errors.append("Intended target does not exist as evaluated geometry")
        if not members[name]:
            errors.append("Registered root has no validated geometry members")
        try:
            direction = vec(root.get("support_direction"))
            if direction.length < .999 or direction.length > 1.001:
                errors.append("support_direction must be a world-space unit vector")
            direction.normalize()
            gap_max = float(root["support_max_gap"])
            penetration_max = float(root["support_max_penetration"])
            angle_max = float(root["support_angle_tolerance_deg"])
            if not (0 <= gap_max <= .005 and 0 <= penetration_max <= .002 and 0 <= angle_max <= 12):
                errors.append("Tolerances exceed mandatory 5 mm gap / 2 mm penetration / 12 degree limits")
            result["tolerances"] = dict(gap_m=gap_max, penetration_m=penetration_max, angle_deg=angle_max)
        except Exception as error:
            errors.append("Missing or malformed support direction/tolerances: " + str(error))
            results.append(result)
            continue
        anchor_names = prop(root.get("support_anchors"), [])
        if not isinstance(anchor_names, (list, tuple)) or not anchor_names:
            errors.append("No explicit support-anchor empty list")
            results.append(result)
            continue
        if len(set(anchor_names)) != len(anchor_names):
            errors.append("Duplicate anchors in root registration")
        for anchor_name in anchor_names:
            row = dict(name=anchor_name, errors=[])
            result["anchors"].append(row)
            anchor = bpy.data.objects.get(anchor_name)
            if not anchor or anchor.type != "EMPTY" or not anchor.get("support_anchor"):
                row["errors"].append("Missing tagged anchor EMPTY")
                continue
            if anchor_name in claimed_anchors:
                row["errors"].append("Anchor claimed by more than one root")
            claimed_anchors.add(anchor_name)
            if name not in {a.name for a in ancestors(anchor)}:
                row["errors"].append("Anchor is not a child of registered root")
            point = anchor.matrix_world.translation.copy()
            row["position_world_m"] = rounded(point)
            nearest = [(g.bvh.find_nearest(point), g.name) for g in members[name]]
            nearest = [(hit[3], member_name) for hit, member_name in nearest if hit[0] is not None]
            if nearest:
                distance, member_name = min(nearest)
                row["nearest_assembly_surface"] = dict(object=member_name, distance_m=round(distance, 8))
                if distance > .005 + EPS:
                    row["errors"].append("Anchor floats more than 5 mm from actual assembly surface")
            else:
                row["errors"].append("No assembly geometry near anchor")
            if target:
                # Back up opposite the intended support direction. A contact before
                # the anchor is negative gap (= penetration); beyond it is a gap.
                backoff = .05
                hit = target.ray(point - direction * backoff, direction, .55)
                if not hit:
                    row["errors"].append("No target surface in expected support direction")
                else:
                    location, normal, index, distance = hit
                    signed_gap = (location - point).dot(direction)
                    cosine = max(-1., min(1., normal.normalized().dot(-direction)))
                    angle = math.degrees(math.acos(cosine))
                    row.update(contact_world_m=rounded(location), target_triangle=index,
                               signed_gap_m=round(signed_gap, 8), normal_angle_deg=round(angle, 6))
                    if signed_gap > gap_max + EPS:
                        row["errors"].append("Gap exceeds tolerance")
                    if signed_gap < -penetration_max - EPS:
                        row["errors"].append("Penetration exceeds tolerance")
                    if angle > angle_max + 1e-5:
                        row["errors"].append("Target surface normal exceeds orientation tolerance")
        results.append(result)
    orphan_anchors = [o.name for o in bpy.context.scene.objects if o.get("support_anchor") and o.name not in claimed_anchors]
    failed = [r["root"] for r in results if r["errors"] or any(a["errors"] for a in r["anchors"])]
    emit("support_contact_geometry", bool(results) and not failed and not orphan_anchors,
         method="World-space evaluated target BVH ray casts and assembly BVH nearest-surface checks; explicit child empties for every assembly",
         failed_assemblies=failed, orphan_anchors=orphan_anchors, assemblies=results)
    connectivity = []
    for name, root in roots.items():
        assembly = {g.name: g for g in members[name]}
        seeds = set()
        for anchor_name in prop(root.get("support_anchors"), []):
            anchor = bpy.data.objects.get(anchor_name)
            if not anchor:
                continue
            point = anchor.matrix_world.translation
            for member_name, geometry in assembly.items():
                hit = geometry.bvh.find_nearest(point, .005 + EPS)
                if hit[0] is not None and hit[3] <= .005 + EPS:
                    seeds.add(member_name)
        reached = set(seeds)
        frontier = list(seeds)
        remaining = set(assembly) - reached
        while frontier:
            source = assembly[frontier.pop()]
            for other in list(remaining):
                if connected_surfaces(source, assembly[other]):
                    remaining.remove(other)
                    reached.add(other)
                    frontier.append(other)
        connectivity.append(dict(root=name, member_count=len(assembly), anchor_touching_members=sorted(seeds),
                                 connected_members=len(reached), disconnected_members=sorted(remaining)))
    emit("assembly_component_support_connectivity", bool(connectivity) and all(r["member_count"] and not r["disconnected_members"] for r in connectivity),
         method="Connectivity from anchor-touching members via evaluated BVH triangle intersection, closed-solid containment or <=5 mm vertex-to-surface/edge-to-edge separation",
         assemblies=connectivity, limitation="Subcomponents inside a single disconnected mesh datablock are not independently registered; geometry/normals audit remains separate")


def validate_dimensions(specification, geometries):
    probes = specification.get("surface_probes", [])
    rows = []
    for probe in probes:
        row = dict(name=probe.get("name"), target=probe.get("target"), errors=[])
        try:
            geometry = geometries.get(probe["target"])
            if not geometry:
                raise ValueError("Probe target is absent from evaluated geometry")
            direction = vec(probe["direction"]).normalized()
            expected = float(probe["expected_distance_m"])
            tolerance = float(probe.get("tolerance_m", .005))
            if tolerance < 0 or tolerance > .01:
                raise ValueError("Surface probe tolerance must be 0–10 mm")
            hit = geometry.ray(vec(probe["origin"]), direction, max(1, expected + .25))
            if not hit:
                raise ValueError("Expected evaluated architectural surface not found")
            row.update(expected_distance_m=expected, actual_distance_m=round(hit[3], 7), tolerance_m=tolerance,
                       hit_world_m=rounded(hit[0]), target_normal=rounded(hit[1]))
            if abs(hit[3] - expected) > tolerance + EPS:
                row["errors"].append("Metric surface position differs from specification")
        except Exception as error:
            row["errors"].append(str(error))
        rows.append(row)
    emit("metric_envelope_geometry", len(rows) >= 6 and not any(r["errors"] for r in rows),
         required_minimum_surface_probes=6, method="Named evaluated architecture surface ray casts", probes=rows,
         errors=[] if len(rows) >= 6 else ["At least six independent floor/wall/ceiling envelope probes required"])
    return specification


def validate_routes(specification, geometries, stage):
    volumes = specification.get("clearance_volumes", [])
    rows = []
    for volume in volumes:
        row = dict(name=volume.get("name"), purpose=volume.get("purpose"), errors=[], obstructions=[])
        try:
            lo, hi = vec(volume["min"]), vec(volume["max"])
            row.update(min_m=rounded(lo), max_m=rounded(hi), dimensions_m=rounded(hi - lo))
            if any(hi[i] <= lo[i] for i in range(3)):
                raise ValueError("Invalid clearance volume bounds")
            if volume.get("purpose") == "cell_access":
                if hi.y-lo.y < 1.396 or hi.z < 2.398:
                    row["errors"].append("Cell access is narrower than 1.4 m or lower than 2.4 m (2 mm edge tolerance)")
                row["cell_root"] = volume.get("cell_root")
                cell = bpy.data.objects.get(volume.get("cell_root", ""))
                if not cell or cell.get("function") != "segregated_storage_cell":
                    row["errors"].append("Cell access does not identify its segregated storage cell root")
            if volume.get("purpose") == "maintenance_access":
                if min(hi.x-lo.x, hi.y-lo.y) < .896 or hi.z < 2.198:
                    row["errors"].append("Maintenance access lacks 0.9 m working depth or standing headroom")
                row["equipment_root"] = volume.get("equipment_root")
                if not bpy.data.objects.get(volume.get("equipment_root", "")):
                    row["errors"].append("Maintenance volume has no existing equipment root")
            for geometry in geometries.values():
                # Only objectively flat applied floor paint may be excluded. A
                # collision_role label alone never exempts a physical obstruction.
                role = geometry.obj.get("collision_role")
                if role == "route_marking" and geometry.hi.z <= .02 and geometry.lo.z >= -.005:
                    continue
                hit = box_hits(geometry, lo, hi)
                if hit:
                    row["obstructions"].append(dict(object=geometry.name, reason=hit))
            if row["obstructions"]:
                row["errors"].append("Physical evaluated geometry obstructs required clearance volume")
            support = volume.get("floor_target", specification.get("floor_target"))
            floor = geometries.get(support)
            if not floor:
                row["errors"].append("No evaluated floor target specified for route")
            else:
                expected_z = float(volume.get("floor_z", 0))
                misses = []
                sample_count = 0
                for x in sample_interval(lo.x, hi.x, .25):
                    for y in sample_interval(lo.y, hi.y, .25):
                        sample_count += 1
                        hit = floor.ray(Vector((x, y, expected_z + .2)), Vector((0, 0, -1)), .25)
                        if not hit or abs(hit[0].z - expected_z) > .005 or hit[1].z < math.cos(math.radians(12)):
                            misses.append([round(x, 4), round(y, 4), None if not hit else round(hit[0].z, 5)])
                row["floor_support"] = dict(target=support, samples=sample_count, maximum_grid_step_m=.25, misses=misses)
                if misses:
                    row["errors"].append("Route has missing, displaced or steep floor support")
        except Exception as error:
            row["errors"].append(str(error))
        rows.append(row)
    purposes = {r.get("purpose") for r in rows}
    required = {"player_route", "cart_route", "cart_turn", "portal"} if stage == "full" else {"cart_route", "portal"}
    missing = sorted(required - purposes)
    access_errors = []
    if stage == "full":
        cell_roots = {o.name for o in bpy.context.scene.objects if o.get("function") == "segregated_storage_cell"}
        addressed_roots = [r.get("cell_root") for r in rows if r.get("purpose") == "cell_access"]
        if len(cell_roots) != 4 or set(addressed_roots) != cell_roots or len(addressed_roots) != 4:
            access_errors.append("Exactly four separate segregated storage cells and one measured access volume per cell are required")
        if "maintenance_access" not in purposes:
            access_errors.append("No measured maintenance working volume provided")
        # A graph of intersecting free-floor rectangles establishes continuity
        # from entry through the authored corridor to each branch and portal.
        connected = {"WS_RECEIVING_aperture"}
        pending = {r["name"]: r for r in rows if "min_m" in r}
        frontier = ["WS_RECEIVING_aperture"]
        while frontier:
            a = pending.get(frontier.pop())
            if not a:
                continue
            for name, b in pending.items():
                if name in connected:
                    continue
                overlap = [min(a["max_m"][i], b["max_m"][i])-max(a["min_m"][i], b["min_m"][i]) for i in (0, 1)]
                # Shared region must admit at least a 1 m wide passage in one
                # direction; the other dimension may be a threshold-depth strip.
                if min(overlap) >= -.0001 and max(overlap) >= .996:
                    connected.add(name)
                    frontier.append(name)
        disconnected = sorted(set(pending)-connected)
        if disconnected:
            access_errors.append("Clearance path not continuously connected from entry: " + ", ".join(disconnected))
    else:
        connected, disconnected = set(), []
    emit("physical_portals_and_circulation", bool(rows) and not missing and not access_errors and not any(r["errors"] for r in rows),
         method="Exact evaluated triangle/AABB separating-axis tests plus solid containment; 250 mm floor-support grid",
         missing_required_purposes=missing, volumes=rows,
         access_errors=access_errors, connected_clearance_volumes=sorted(connected), disconnected_clearance_volumes=disconnected,
         stage=stage, full_circulation_evaluated=stage == "full",
         excluded_for_slice=[] if stage == "full" else ["Receiving turning circle occupied by temporary slice hero staging", "Full-depth cart route", "Rear dispatch", "Storage cell access", "Booth internal passage"],
         limitations="Static authored swept clearance volumes; dynamic door movement and runtime navigation are engine handoff checks")


def validate_meshes(geometries):
    invalid = []
    open_meshes = []
    signatures = collections.defaultdict(list)
    for geometry in geometries.values():
        obj = geometry.obj
        errors = []
        if not all(math.isfinite(v) for p in geometry.vertices for v in p):
            errors.append("Nonfinite evaluated vertex coordinates")
        edge_faces = collections.defaultdict(list)
        for index, face in enumerate(geometry.faces):
            for i, a in enumerate(face):
                b = face[(i + 1) % len(face)]
                a, b = geometry.welded_ids[a], geometry.welded_ids[b]
                if a == b:
                    continue
                edge_faces[tuple(sorted((a, b)))].append((index, a, b))
        boundaries = sum(len(uses) == 1 for uses in edge_faces.values())
        nonmanifold = sum(len(uses) > 2 for uses in edge_faces.values())
        inconsistent = sum(len(uses) == 2 and uses[0][1:] == uses[1][1:] for uses in edge_faces.values())
        zero_area = sum((geometry.vertices[t[1]] - geometry.vertices[t[0]]).cross(geometry.vertices[t[2]] - geometry.vertices[t[0]]).length < 1e-12 for t in geometry.triangles)
        if nonmanifold:
            errors.append(f"{nonmanifold} edges shared by more than two polygons")
        if inconsistent:
            errors.append(f"{inconsistent} inconsistent adjacent polygon windings")
        if zero_area:
            errors.append(f"{zero_area} degenerate evaluated triangles")
        signed_volume = signed_mesh_volume(geometry)
        if boundaries:
            reason = obj.get("open_surface_reason", "")
            open_meshes.append(dict(object=geometry.name, boundary_edges=boundaries, declared_reason=reason,
                                    normals_volume_check="NOT_APPLICABLE_OPEN_SURFACE"))
            if not reason:
                errors.append("Open evaluated surface lacks explicit open_surface_reason")
        elif signed_volume < -1e-9:
            errors.append("Closed evaluated mesh has negative signed volume (inward winding or mirrored normals)")
        if obj.hide_render or obj.hide_viewport or obj.hide_get():
            errors.append("Geometry unexpectedly hidden in render or viewport")
        if obj.get("collision_role") not in {"solid", "route_marking", "noncolliding"}:
            errors.append("Missing collision_role")
        if not geometry.materials or any(m is None for m in geometry.materials):
            errors.append("Missing material slot")
        if any(i >= len(geometry.materials) for i in geometry.material_indices):
            errors.append("Evaluated polygon references absent material")
        if errors:
            invalid.append(dict(object=geometry.name, errors=errors, signed_volume_m3=round(signed_volume, 9)))
        # World-space polygon signatures detect exact coincident duplicates while
        # preserving deliberately reused parts in different positions.
        vertex_keys = [tuple(round(v, 6) for v in p) for p in geometry.vertices]
        canonical_faces = sorted(tuple(sorted(vertex_keys[i] for i in face)) for face in geometry.faces)
        signature = hashlib.sha256(repr(canonical_faces).encode()).hexdigest()
        signatures[signature].append(geometry.name)
    duplicates = [names for names in signatures.values() if len(names) > 1]
    emit("mesh_normals_material_assignment_and_registration", bool(geometries) and not invalid,
         checked_objects=len(geometries), errors=invalid, declared_open_surfaces=open_meshes,
         topology_weld_tolerance_m=.000001, signed_volume_arithmetic="Translated local origin, Python double precision, compensated summation",
         limitations="No general all-pairs self-intersection or outward-normal proof for open surfaces; support and routes are independently collision-tested")
    emit("exact_coincident_duplicates", not duplicates, duplicates=duplicates,
         method="World-coordinate evaluated polygon signatures rounded to 1 micrometre; not an all-pairs intersection claim")


def validate_transforms_and_pivots(geometries):
    invalid = []
    pivots = []
    for obj in bpy.context.scene.objects:
        values = [float(v) for row in obj.matrix_world for v in row]
        if not all(math.isfinite(v) for v in values) or abs(obj.matrix_world.determinant()) < 1e-12:
            invalid.append(dict(object=obj.name, error="Nonfinite or singular object transform"))
        interaction = obj.get("interaction")
        if not interaction:
            continue
        children = [g for g in geometries.values() if obj.name in {a.name for a in ancestors(g.obj)}]
        row = dict(name=obj.name, interaction=interaction, pivot_world_m=rounded(obj.matrix_world.translation),
                   descendant_geometry_count=len(children), errors=[])
        if not children:
            row["errors"].append("Interactive pivot has no evaluated geometry descendants")
        else:
            low = Vector(tuple(min(g.lo[i] for g in children) for i in range(3)))
            high = Vector(tuple(max(g.hi[i] for g in children) for i in range(3)))
            point = obj.matrix_world.translation
            separation = math.sqrt(sum(max(low[i]-point[i], 0, point[i]-high[i])**2 for i in range(3)))
            row.update(descendant_min_m=rounded(low), descendant_max_m=rounded(high), distance_to_descendant_bounds_m=round(separation, 7))
            if separation > .15:
                row["errors"].append("Interactive origin is more than 150 mm outside its descendant geometry bounds")
        pivots.append(row)
    found = {p["interaction"] for p in pivots}
    required = {"controlled_access", "unseal_lift"}
    emit("transforms_and_interactive_pivot_sanity", not invalid and not (required-found) and not any(p["errors"] for p in pivots),
         invalid_transforms=invalid, missing_interaction_pivots=sorted(required-found), pivots=pivots,
         limitations="Checks geometry-relative export origins and finite transforms; does not validate animation, physics, interaction scripts or complete door sweep")


def validate_full_inventory(geometries, stage):
    if stage != "full":
        return
    expected = {"segregated_storage_cell": (4, 4), "monitoring": (1, None),
                "ventilation": (1, None), "transfer": (1, None)}
    rows = []
    errors = []
    for function, (minimum, maximum) in expected.items():
        roots = [o for o in bpy.context.scene.objects if o.get("function") == function]
        entries = []
        for root in roots:
            children = [g.name for g in geometries.values() if root.name in {a.name for a in ancestors(g.obj)}]
            entries.append(dict(name=root.name, registered_support=bool(root.get("support_required")),
                                evaluated_geometry_members=len(children)))
            if not root.get("support_required") or not children:
                errors.append(function+": "+root.name+" is not a registered assembly with evaluated geometry")
        if len(roots) < minimum or maximum is not None and len(roots) > maximum:
            errors.append(function+": required "+str(minimum)+("–"+str(maximum) if maximum else "+")+", actual "+str(len(roots)))
        rows.append(dict(function=function, minimum_count=minimum, maximum_count=maximum, assemblies=entries))
    emit("full_functional_geometry_inventory", not errors, functions=rows, errors=errors,
         limitations="Counts and geometry registration establish physical source presence; function, legibility and art quality require rendered review and runtime implementation")


def validate_cameras(camera_spec):
    cameras = camera_spec.get("cameras", camera_spec.get("camera_manifest", [])) if isinstance(camera_spec, dict) else camera_spec
    if isinstance(cameras, dict):
        cameras = [dict(name=name, **value) for name, value in cameras.items()]
    rows = []
    scene_cameras = {o.name for o in bpy.context.scene.objects if o.type == "CAMERA"}
    for expected in cameras:
        row = dict(name=expected.get("name"), errors=[])
        obj = bpy.data.objects.get(expected.get("name"))
        if obj is None or obj.type != "CAMERA":
            row["errors"].append("Named camera missing")
        else:
            try:
                location = vec(expected.get("location", expected.get("position")))
                actual = obj.matrix_world.translation
                row["position_error_m"] = (actual - location).length
                if (actual - location).length > .0001:
                    row["errors"].append("Camera location differs from fixed baseline")
                if "target" in expected:
                    rotation = (vec(expected["target"]) - location).to_track_quat("-Z", "Y")
                elif "rotation_quaternion" in expected:
                    from mathutils import Quaternion
                    rotation = Quaternion(expected["rotation_quaternion"])
                else:
                    from mathutils import Euler
                    rotation = Euler(expected["rotation_euler"], "XYZ").to_quaternion()
                angle = obj.matrix_world.to_quaternion().rotation_difference(rotation).angle
                row["rotation_error_deg"] = math.degrees(angle)
                if angle > .0001:
                    row["errors"].append("Camera orientation differs from fixed baseline")
                lens = float(expected.get("lens_mm", expected.get("lens")))
                row.update(lens_mm=obj.data.lens, expected_lens_mm=lens)
                if abs(obj.data.lens - lens) > .001:
                    row["errors"].append("Camera lens differs from fixed baseline")
                if obj.data.type != "PERSP" or obj.data.clip_start <= 0 or obj.data.clip_end < 30:
                    row["errors"].append("Invalid perspective camera or clipping limits")
            except Exception as error:
                row["errors"].append("Incomplete camera baseline: " + str(error))
        rows.append(row)
    expected_names = {row["name"] for row in rows}
    extras = sorted(scene_cameras - expected_names)
    emit("ten_fixed_cameras", len(rows) == 10 and len(expected_names) == 10 and not extras and not any(r["errors"] for r in rows),
         expected_count=10, actual_count=len(scene_cameras), extra_cameras=extras, cameras=rows)


def validate_render(specification):
    expected = specification.get("render_config", {})
    scene = bpy.context.scene
    actual = dict(engine=scene.render.engine, resolution_x=scene.render.resolution_x,
                  resolution_y=scene.render.resolution_y, resolution_percentage=scene.render.resolution_percentage,
                  film_transparent=scene.render.film_transparent, image_format=scene.render.image_settings.file_format,
                  view_transform=scene.view_settings.view_transform)
    if scene.render.engine == "CYCLES":
        actual.update(samples=scene.cycles.samples, use_denoising=scene.cycles.use_denoising, seed=scene.cycles.seed)
    errors = []
    required = {"engine", "resolution_x", "resolution_y", "resolution_percentage", "image_format", "view_transform"}
    for missing in sorted(required - set(expected)):
        errors.append("Missing specified render setting: " + missing)
    for key, value in expected.items():
        if key not in actual:
            errors.append("Unimplemented specified render setting: " + key)
        elif actual[key] != value:
            errors.append(f"{key}: actual {actual[key]!r} != expected {value!r}")
    if not scene.camera or scene.camera.type != "CAMERA":
        errors.append("No active render camera")
    emit("render_configuration", not errors, expected=expected, actual=actual, errors=errors)


def validate_dependencies():
    errors = []
    images = []
    for image in bpy.data.images:
        if image.source in {"GENERATED", "VIEWER"}:
            continue
        packed = bool(image.packed_file or image.packed_files)
        path = Path(bpy.path.abspath(image.filepath)) if image.filepath else None
        exists = bool(path and path.is_file())
        row = dict(name=image.name, source=image.source, packed=packed, filepath=image.filepath, exists=exists)
        images.append(row)
        if not packed and not exists:
            errors.append("Missing image: " + image.name)
        if not packed and image.filepath and not image.filepath.startswith("//"):
            errors.append("Unpacked absolute image dependency: " + image.name)
    libraries = []
    for library in bpy.data.libraries:
        exists = Path(bpy.path.abspath(library.filepath)).is_file()
        libraries.append(dict(name=library.name, filepath=library.filepath, exists=exists))
        if not exists:
            errors.append("Missing linked library: " + library.name)
        if not library.filepath.startswith("//"):
            errors.append("Absolute linked library dependency: " + library.name)
    fonts = []
    for font in bpy.data.fonts:
        if font.filepath == "<builtin>":
            continue
        packed = bool(font.packed_file)
        exists = Path(bpy.path.abspath(font.filepath)).is_file()
        fonts.append(dict(name=font.name, filepath=font.filepath, packed=packed, exists=exists))
        if not packed and (not exists or not font.filepath.startswith("//")):
            errors.append("Missing or nonportable font dependency: " + font.name)
    material_rows = []
    for material in bpy.data.materials:
        if not material.users:
            continue
        row = dict(name=material.name, users=material.users, use_nodes=material.use_nodes, surface_connected=False, principled=[])
        tree = material.node_tree
        if material.use_nodes and tree:
            outputs = [n for n in tree.nodes if n.type == "OUTPUT_MATERIAL" and n.is_active_output]
            row["surface_connected"] = any(n.inputs["Surface"].is_linked for n in outputs)
            for node in tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    row["principled"].append(dict(roughness_default=node.inputs["Roughness"].default_value,
                        roughness_linked=node.inputs["Roughness"].is_linked, metallic_default=node.inputs["Metallic"].default_value))
        if not row["surface_connected"]:
            errors.append("Material has no active connected surface shader: " + material.name)
        material_rows.append(row)
    emit("materials_and_portable_dependencies", bool(material_rows) and not errors,
         images=images, libraries=libraries, fonts=fonts, materials=material_rows, errors=errors,
         limitations="Shader connectivity/dependency checks do not establish tactile quality or anti-plastic visual acceptance")


def main():
    started = time.monotonic()
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--interface", default=str(SECTION / "interface.json"))
    parser.add_argument("--cameras", default=str(SECTION / "blender" / "scene_manifest.json"))
    parser.add_argument("--stage", choices=("auto", "slice", "full"), default="auto")
    parser.add_argument("--build-source", default=str(SECTION / "blender" / "build_scene.py"))
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    output = Path(args.output).resolve()
    if not inside_path(output, SECTION / "production" / "validation"):
        raise ValueError("Validation reports must stay inside production/validation")
    input_paths = {"blend": bpy.data.filepath, "interface": args.interface, "cameras": args.cameras,
                   "validator": __file__, "build_script": args.build_source}
    report = dict(schema_version=1, section="waste-storage", status="FAIL", validation_kind="fresh_process_read_only_geometry",
                  utc_timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), process_id=os.getpid(),
                  blender_version=bpy.app.version_string, background=bool(bpy.app.background),
                  inputs={name: dict(path=str(Path(path).resolve()), sha256=digest(path)) for name, path in input_paths.items()},
                  acceptance_scope="Objective source geometry only. This report is not visual approval, render comparison, runtime validation or full cold-start acceptance.", checks=CHECKS)
    try:
        private = os.environ.get("BLENDER_USER_RESOURCES", "")
        factory = "--factory-startup" in sys.argv
        emit("isolated_authoritative_source", bool(bpy.app.background and factory and bpy.data.filepath and inside_path(bpy.data.filepath, SECTION) and private and inside_path(private, SECTION)),
             blend_path=bpy.data.filepath, background=bool(bpy.app.background), private_user_resources=private,
             factory_startup=factory,
             scene_modified=bool(bpy.data.is_dirty), no_render_performed=True)
        recorded_source = bpy.context.scene.get("build_source_sha256")
        actual_source = digest(input_paths["build_script"])
        emit("saved_build_source_fingerprint", bool(recorded_source and recorded_source == actual_source),
             recorded_source_sha256=recorded_source, current_build_source_sha256=actual_source,
             saved_revision=bpy.context.scene.get("revision"),
             limitation="Fingerprint proves saved metadata matches current script bytes; independent clean rebuild/render comparison remains a separate final gate")
        inputs = {}
        for name in ("interface", "cameras"):
            path = Path(input_paths[name])
            try:
                inputs[name] = json.loads(path.read_text(encoding="utf-8-sig"))
                emit(name + "_specification_present", True, path=str(path), sha256=digest(path))
            except Exception as error:
                inputs[name] = {}
                emit(name + "_specification_present", False, path=str(path), error=str(error))
        units = bpy.context.scene.unit_settings
        emit("metric_units", units.system == "METRIC" and abs(units.scale_length - 1) < EPS,
             unit_system=units.system, scale_length=units.scale_length)
        geometries = extract_geometry()
        saved_stage = bpy.context.scene.get("build_stage")
        stage = saved_stage if args.stage == "auto" else args.stage
        report["stage"] = stage
        emit("build_stage_scope", stage in {"slice", "full"} and saved_stage == stage,
             saved_stage=saved_stage, requested_stage=args.stage,
             acceptance_scope="Full objective geometry" if stage == "full" else "Temporary receiving style slice only; no full-section circulation/acceptance claim")
        try:
            specification = geometry_specification(inputs["interface"], stage)
        except Exception as error:
            specification = {}
            emit("geometry_specification_derivation", False, error=str(error))
        operations = [lambda: validate_support(geometries),
                      lambda: validate_routes(validate_dimensions(specification, geometries), geometries, stage),
                      lambda: validate_meshes(geometries), lambda: validate_transforms_and_pivots(geometries),
                      lambda: validate_full_inventory(geometries, stage),
                      lambda: validate_cameras(inputs["cameras"]),
                      lambda: validate_render(specification), validate_dependencies]
        for operation in operations:
            try:
                operation()
            except Exception as error:
                emit("validator_check_exception", False, error=str(error), traceback=traceback.format_exc())
    except Exception as error:
        emit("validator_fatal_exception", False, error=str(error), traceback=traceback.format_exc())
    report["status"] = "PASS" if CHECKS and all(c["status"] == "PASS" for c in CHECKS) else "FAIL"
    report["summary"] = dict(passed=sum(c["status"] == "PASS" for c in CHECKS), failed=sum(c["status"] == "FAIL" for c in CHECKS),
                             failing_checks=[c["name"] for c in CHECKS if c["status"] == "FAIL"], elapsed_seconds=round(time.monotonic() - started, 3))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("WASTE_STORAGE_VALIDATION " + json.dumps(dict(status=report["status"], report=str(output), **report["summary"])))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
