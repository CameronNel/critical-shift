#!/usr/bin/env python3
"""
Critical Shift Spawn Room support-contact validator.

Run inside Blender:
    blender -b spawnroom.blend --python validate_contacts.py

Writes:
    ../production/contact_validation.json

Catches support-dependent props that cameras can miss: floating wall papers,
frames/signage, floor props hovering above the floor, ceiling props detached
from the ceiling, or props pushed too far into their support surface.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


REQUIRED_COLLECTION = "CS_SUPPORT_REQUIRED"
CANDIDATE_COLLECTIONS = (
    "CS_WALL_DRESSING",
    "CS_FLOOR_DRESSING",
    "CS_CEILING_DRESSING",
)

DEFAULT_MAX_GAP_M = 0.005
DEFAULT_MAX_PENETRATION_M = 0.002
DEFAULT_MAX_ANGLE_DEG = 12.0
RAY_EPSILON_M = 0.0001

AXES = {
    "LOCAL_+X": Vector((1.0, 0.0, 0.0)),
    "LOCAL_-X": Vector((-1.0, 0.0, 0.0)),
    "LOCAL_+Y": Vector((0.0, 1.0, 0.0)),
    "LOCAL_-Y": Vector((0.0, -1.0, 0.0)),
    "LOCAL_+Z": Vector((0.0, 0.0, 1.0)),
    "LOCAL_-Z": Vector((0.0, 0.0, -1.0)),
    "WORLD_+X": Vector((1.0, 0.0, 0.0)),
    "WORLD_-X": Vector((-1.0, 0.0, 0.0)),
    "WORLD_+Y": Vector((0.0, 1.0, 0.0)),
    "WORLD_-Y": Vector((0.0, -1.0, 0.0)),
    "WORLD_+Z": Vector((0.0, 0.0, 1.0)),
    "WORLD_-Z": Vector((0.0, 0.0, -1.0)),
}


def objects_recursive(collection):
    found = set(collection.objects)
    for child in collection.children:
        found.update(objects_recursive(child))
    return found


def get_collection_objects(name):
    collection = bpy.data.collections.get(name)
    return set() if collection is None else objects_recursive(collection)


def world_direction(obj, axis_name):
    axis = AXES.get(axis_name)
    if axis is None:
        raise ValueError(
            "Unknown cs_support_direction '%s'. Allowed: %s"
            % (axis_name, ", ".join(sorted(AXES)))
        )
    if axis_name.startswith("WORLD_"):
        return axis.normalized()
    return (obj.matrix_world.to_3x3() @ axis).normalized()


def support_samples(obj, direction_world):
    anchors = [
        child for child in obj.children
        if bool(child.get("cs_support_anchor", False))
    ]
    if anchors:
        return [
            ("anchor:" + anchor.name, anchor.matrix_world.translation.copy())
            for anchor in anchors
        ]

    if obj.type != "MESH" or not obj.bound_box:
        return [("origin", obj.matrix_world.translation.copy())]

    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    projections = [corner.dot(direction_world) for corner in corners]
    support_projection = max(projections)
    face = [
        corner for corner, projection in zip(corners, projections)
        if abs(projection - support_projection) <= 1e-5
    ]
    if not face:
        face = corners

    center = sum(face, Vector()) / len(face)
    samples = [("face:center", center)]
    for index, point in enumerate(face):
        samples.append(("face:corner:%d" % index, point))
    return samples


class TargetBVH:
    def __init__(self, obj, depsgraph):
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            matrix = evaluated.matrix_world
            vertices = [matrix @ vertex.co for vertex in mesh.vertices]
            polygons = [list(poly.vertices) for poly in mesh.polygons]
            self.bvh = BVHTree.FromPolygons(
                vertices, polygons, all_triangles=False
            )
        finally:
            evaluated.to_mesh_clear()


def validate_object(obj, target_bvhs, depsgraph):
    result = {
        "object": obj.name,
        "status": "PASS",
        "issues": [],
        "samples": [],
    }

    target_name = obj.get("cs_support_target")
    direction_name = obj.get("cs_support_direction")

    if not target_name:
        result["status"] = "FAIL"
        result["issues"].append("Missing cs_support_target")
        return result
    if not direction_name:
        result["status"] = "FAIL"
        result["issues"].append("Missing cs_support_direction")
        return result

    target = bpy.data.objects.get(str(target_name))
    if target is None:
        result["status"] = "FAIL"
        result["issues"].append(
            "Support target '%s' does not exist" % target_name
        )
        return result
    if target.type != "MESH":
        result["status"] = "FAIL"
        result["issues"].append(
            "Support target '%s' is %s, expected MESH"
            % (target_name, target.type)
        )
        return result

    try:
        direction = world_direction(obj, str(direction_name))
    except ValueError as exc:
        result["status"] = "FAIL"
        result["issues"].append(str(exc))
        return result

    max_gap = float(obj.get("cs_support_max_gap_m", DEFAULT_MAX_GAP_M))
    max_penetration = float(
        obj.get("cs_support_max_penetration_m", DEFAULT_MAX_PENETRATION_M)
    )
    max_angle = float(
        obj.get("cs_support_max_angle_deg", DEFAULT_MAX_ANGLE_DEG)
    )
    min_normal_alignment = math.cos(math.radians(max_angle))

    if target.name not in target_bvhs:
        target_bvhs[target.name] = TargetBVH(target, depsgraph)
    bvh = target_bvhs[target.name].bvh

    for sample_name, point in support_samples(obj, direction):
        sample = {
            "sample": sample_name,
            "point_world": [round(v, 6) for v in point],
            "status": "PASS",
        }

        expected_origin = point - direction * RAY_EPSILON_M
        hit_point, hit_normal, _face, hit_distance = bvh.ray_cast(
            expected_origin,
            direction,
            max_gap + RAY_EPSILON_M,
        )

        if hit_point is not None and hit_distance is not None:
            gap = max(0.0, float(hit_distance) - RAY_EPSILON_M)
            alignment = abs(hit_normal.normalized().dot(direction))
            sample.update({
                "relation": "gap",
                "distance_m": round(gap, 6),
                "normal_alignment": round(alignment, 6),
            })
            if gap > max_gap:
                sample["status"] = "FAIL"
                sample["issue"] = (
                    "Floating %.4f m from support; max gap is %.4f m"
                    % (gap, max_gap)
                )
            elif alignment < min_normal_alignment:
                sample["status"] = "FAIL"
                sample["issue"] = (
                    "Support surface angle exceeds %.1f degree tolerance"
                    % max_angle
                )
        else:
            opposite_origin = point + direction * RAY_EPSILON_M
            opp_point, opp_normal, _opp_face, opp_distance = bvh.ray_cast(
                opposite_origin,
                -direction,
                max_penetration + RAY_EPSILON_M,
            )

            if opp_point is not None and opp_distance is not None:
                penetration = max(
                    0.0, float(opp_distance) - RAY_EPSILON_M
                )
                alignment = abs(opp_normal.normalized().dot(direction))
                sample.update({
                    "relation": "penetration",
                    "distance_m": round(penetration, 6),
                    "normal_alignment": round(alignment, 6),
                })
                if penetration > max_penetration:
                    sample["status"] = "FAIL"
                    sample["issue"] = (
                        "Penetrates support by %.4f m; max penetration is %.4f m"
                        % (penetration, max_penetration)
                    )
                elif alignment < min_normal_alignment:
                    sample["status"] = "FAIL"
                    sample["issue"] = (
                        "Support surface angle exceeds %.1f degree tolerance"
                        % max_angle
                    )
            else:
                nearest_point, nearest_normal, _nearest_face, nearest_distance = (
                    bvh.find_nearest(point)
                )
                sample["status"] = "FAIL"
                if nearest_point is None or nearest_distance is None:
                    sample["issue"] = "No support surface found"
                else:
                    sample.update({
                        "relation": "nearest_only",
                        "distance_m": round(float(nearest_distance), 6),
                        "normal_alignment": round(
                            abs(nearest_normal.normalized().dot(direction)), 6
                        ),
                    })
                    sample["issue"] = (
                        "No support hit in expected direction within %.4f m; "
                        "nearest target surface is %.4f m away"
                        % (max_gap, float(nearest_distance))
                    )

        if sample["status"] == "FAIL":
            result["status"] = "FAIL"
            result["issues"].append(sample["issue"])
        result["samples"].append(sample)

    return result


def main():
    depsgraph = bpy.context.evaluated_depsgraph_get()

    required = get_collection_objects(REQUIRED_COLLECTION)
    candidates = set()
    candidate_membership = {}

    for collection_name in CANDIDATE_COLLECTIONS:
        members = get_collection_objects(collection_name)
        candidates.update(members)
        for obj in members:
            candidate_membership.setdefault(obj.name, []).append(collection_name)

    report = {
        "validator": "Critical Shift support-contact validator",
        "status": "PASS",
        "required_collection": REQUIRED_COLLECTION,
        "candidate_collections": list(CANDIDATE_COLLECTIONS),
        "objects_checked": 0,
        "failures": [],
        "objects": [],
    }

    for obj in sorted(candidates - required, key=lambda item: item.name):
        failure = {
            "object": obj.name,
            "status": "FAIL",
            "issues": [
                "Object is in a support-dependent dressing collection but "
                "is missing from %s" % REQUIRED_COLLECTION
            ],
            "candidate_collections": candidate_membership.get(obj.name, []),
            "samples": [],
        }
        report["objects"].append(failure)
        report["failures"].append({
            "object": obj.name,
            "issues": failure["issues"],
        })

    target_bvhs = {}
    for obj in sorted(required, key=lambda item: item.name):
        if obj.type not in {"MESH", "EMPTY", "CURVE", "FONT"}:
            continue
        result = validate_object(obj, target_bvhs, depsgraph)
        result["candidate_collections"] = candidate_membership.get(
            obj.name, []
        )
        report["objects"].append(result)
        report["objects_checked"] += 1

        if result["status"] == "FAIL":
            report["failures"].append({
                "object": obj.name,
                "issues": result["issues"],
            })

    report["status"] = "FAIL" if report["failures"] else "PASS"

    output_path = (
        Path(__file__).resolve().parent.parent
        / "production"
        / "contact_validation.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    print(
        "[Critical Shift] support contact validation: %s "
        "(%d tagged objects, %d failures)"
        % (
            report["status"],
            report["objects_checked"],
            len(report["failures"]),
        )
    )
    print("[Critical Shift] report: %s" % output_path)

    if report["failures"]:
        for failure in report["failures"]:
            print(
                "  FAIL %s: %s"
                % (
                    failure["object"],
                    "; ".join(failure["issues"]),
                )
            )
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    if exit_code:
        raise RuntimeError(
            "Critical Shift support-contact validation failed. "
            "See production/contact_validation.json"
        )
