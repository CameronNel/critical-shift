"""Check the linked HZ-01 suit and its original locker attachment coordinates.

Run after opening module.blend, with -- --output DIR [--render]. This checks the
actual linked instances, empty-library contents and dock contact; room contact
validation remains owned by validate_contacts.py.
"""

import argparse
import sys
import json
from pathlib import Path
import bpy
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--render", action="store_true")
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :])
out = args.output
out.mkdir(parents=True, exist_ok=True)
hero = bpy.data.collections["HERO_SUIT"]
instances = sorted(
    [
        o
        for o in bpy.context.scene.objects
        if o.instance_type == "COLLECTION" and o.instance_collection == hero
    ],
    key=lambda o: o.name,
)
assert len(instances) == 4, "Expected exactly four linked suit instances"
assert hero["cs_suit_style"] == "owner-reference-20261001"
assert hero["cs_placement_preserved"]
assert hero.get("cs_lod") == "locker", "hero_suit.blend is not the locker LOD: run lod_hero_suit.py after build_hero_suit.py"
meshes_all = [o for o in hero.all_objects if o.type == "MESH"]
assert not any(o.modifiers for o in meshes_all), "library meshes carry modifiers: apply them (lod_hero_suit.py does)"
current_tris = sum(len(p.vertices) - 2 for o in meshes_all for p in o.data.polygons)   # recomputed, not read from metadata
assert current_tris <= 30000, ("locker LOD triangle budget", current_tris)
assert current_tris == hero["cs_tris_lod"], ("cs_tris_lod is stale", current_tris, hero["cs_tris_lod"])
assert hero["cs_tris_lod"] < hero["cs_tris_full"]
assert not any(
    o.name.endswith("_HEAD") or o.name.startswith("FACE_") for o in hero.all_objects
)
missing = [
    lib.filepath
    for lib in bpy.data.libraries
    if not Path(bpy.path.abspath(lib.filepath)).exists()
]
assert not missing, "Missing linked libraries"
meshes = [o for o in hero.all_objects if o.type == "MESH" and not o.hide_render]
local = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
rows = []
for inst in instances:
    points = [inst.matrix_world @ p for p in local]
    station = inst.name.split("_suit_model")[0]
    dock = bpy.data.objects[station + "_boot_dock"]
    dock_meshes = [
        o for o in [dock] + list(dock.children_recursive) if o.type == "MESH"
    ]
    assert dock_meshes, "Boot dock has no geometry: " + dock.name
    dock_top = max(
        (o.matrix_world @ Vector(c)).z for o in dock_meshes for c in o.bound_box
    )
    foot = min(p.z for p in points)
    top = max(p.z for p in points)
    gap = foot - dock_top
    assert abs(gap) < 0.005, (station, "boot dock gap", gap)
    expected_top = (inst.matrix_world @ Vector((0, 0, hero["cs_top_z"]))).z
    assert abs(top - expected_top) < 0.001, (
        station,
        "top alignment",
        top,
        expected_top,
    )
    rows.append(
        {
            "instance": inst.name,
            "library": hero.library.filepath,
            "boot_dock_gap_m": gap,
            "top_z_m": top,
        }
    )
report = {
    "status": "PASS",
    "blender": bpy.app.version_string,
    "instances": rows,
    "lod": {"cs_lod": hero["cs_lod"], "triangles_full": hero["cs_tris_full"], "triangles_locker": hero["cs_tris_lod"], "triangles_current": current_tris},
    "placement_anchors": {
        k: hero[k] for k in ("cs_top_z", "cs_pack_back_y", "cs_foot_zmin")
    },
    "missing_libraries": missing,
    "wearer_in_empty_library": False,
    "scope": "Linked authoring suit only; no room art or Unity acceptance",
}
(out / "LINKED_LOCKER_VALIDATION.json").write_text(json.dumps(report, indent=2) + "\n")
print("LINKED_SUIT_VALIDATION", json.dumps(report))
s = bpy.context.scene
if args.render:
    s.camera = bpy.data.objects["VALIDATE_Hero_A"]
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.cycles.samples = 20
    s.cycles.use_denoising = True
    s.render.resolution_x = 960
    s.render.resolution_y = 540
    s.render.resolution_percentage = 100
    (out / "final").mkdir(exist_ok=True)
    s.render.filepath = str(out / "final" / "linked_lockers.png")
    bpy.ops.render.render(write_still=True)
