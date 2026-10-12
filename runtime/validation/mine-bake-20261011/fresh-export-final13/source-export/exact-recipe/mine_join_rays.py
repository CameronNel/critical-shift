"""Export physical join expectations from the actual mine geometry, including its cart."""
from mathutils import Vector


def collision_eligible(mapping):
    return mapping["visible"] and not mapping["dynamic"] and not any(
        t in mapping["source"].lower() for t in ("haze", "fog", "leaf", "paper", "rug", "carpet", "state_"))


def generate(objects, mappings):
    source = {m["node"]:m for m in mappings}
    meshes = [o for o in objects if o.type == "MESH" and collision_eligible(source[o.name])
              and not source[o.name]["source"].lower().startswith(("stain_", "decal_", "scuff_"))]
    rays = []
    for lane in (-30.2, -29.0, -27.8):
        for height in (0.6, 1.7, 3.0):
            origin = Vector((-21.6, lane, height)); direction = Vector((-1, 0, 0)); hits = []
            for o in meshes:
                inverse = o.matrix_world.inverted(); local_direction = inverse.to_3x3() @ direction
                hit, point, _, _ = o.ray_cast(inverse @ origin, local_direction.normalized(), distance=25 * local_direction.length)
                if hit:
                    point = o.matrix_world @ point; distance = (point - origin).length
                    if distance <= 25: hits.append((distance, o.name, list(point)))
            closest = min(hits) if hits else None
            if lane != -29.0 and closest:
                raise ValueError("Authored mine walking lane is blocked: " + closest[1])
            rays.append({"origin":list(origin), "direction":list(direction), "distance":25,
                         "hit":closest is not None, "node":closest[1] if closest else "",
                         "point":closest[2] if closest else []})
    return rays
