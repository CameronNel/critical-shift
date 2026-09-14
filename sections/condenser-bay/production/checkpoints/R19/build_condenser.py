"""Factory-empty original Turbine Condenser Bay. Run through run.ps1 / gpu_gate."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import kit as k
from layout import *
from scene_arch import build_architecture
from scene_equip import build_equipment

ap = __import__("argparse").ArgumentParser()
ap.add_argument("--revision", default="R01")
ap.add_argument("--render", default="")
ap.add_argument("--samples", type=int, default=32)
ap.add_argument("--width", type=int, default=1920)
ap.add_argument("--height", type=int, default=1080)
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else [])

bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
k.S = S
S.unit_settings.system = "METRIC"
S.unit_settings.scale_length = 1
k.palette()

CAMERAS = [
    # From the unbound stub looking in: D01 jambs, leaves, identity, hall.
    ("C01_ENTRY", (0.00, -1.12, 1.55), (2.15, 3.55, 2.15), 22),
    ("C02_HERO", (-1.35, 1.20, 1.70), (3.20, 4.40, 2.60), 22),
    ("C03_REVERSE", (3.05, 9.05, 1.72), (3.00, 4.20, 2.20), 22),
    # Exterior receive: neck/bellows/flange into the slab from south of the shell.
    ("C04_EXHAUST", (1.15, 1.85, 4.35), (3.05, 3.60, 5.50), 26),
    ("C05_RETURN", (0.45, 8.55, 1.58), (3.10, 5.85, 1.25), 24),
    ("C06_COOLING", (6.35, 2.05, 1.75), (8.75, 4.15, 3.22), 26),
    ("C07_OPERATOR", (1.18, 4.05, 1.52), (-1.15, 4.05, 1.68), 26),
    ("C08_MAINT", (5.55, 3.45, 5.28), (5.50, 5.55, 5.10), 28),
    ("C09_ROOF", (5.55, 4.72, 5.28), (3.15, 4.05, 5.52), 28),
    ("C10_MATERIALS", (2.50, 5.92, 1.12), (2.40, 7.05, 0.95), 32),
]
WALK = [
    ("W01_ENTRY_CORNER", (0.25, 1.55, 1.52), (0.00, -0.12, 1.35), 22),
    ("W02_SW_TURN", (0.50, 1.70, 1.58), (3.70, 1.35, 1.90), 24),
    ("W03_NW", (-1.35, 8.90, 1.60), (2.50, 6.60, 1.40), 24),
    ("W04_NE", (8.55, 7.15, 1.62), (7.70, 4.10, 0.18), 24),
    ("W05_SE", (8.15, 3.45, 1.62), (6.80, 2.20, 2.85), 22),
    ("W06_WEST_AISLE", (0.12, 6.85, 1.55), (1.15, 9.18, 1.58), 24),
    ("W07_EAST_PULL", (8.20, 2.35, 1.58), (7.55, 5.35, 0.85), 26),
    ("W08_GALLERY_TURN", (5.52, 4.88, 5.28), (3.25, 4.05, 5.35), 26),
]


def cameras():
    k.group("90 Evidence cameras")
    for n, p, t, lens in CAMERAS + WALK:
        k.camera(n, p, t, lens)
    S.camera = S.objects["C02_HERO"]


def settings():
    S.render.engine = "BLENDER_EEVEE"
    ee = S.eevee
    ee.use_raytracing = False
    ee.taa_render_samples = max(16, args.samples)
    ee.use_shadows = True
    try:
        ee.shadow_pool_size = "2048"
    except Exception:
        pass
    ee.use_fast_gi = True
    try:
        ee.fast_gi_method = "GLOBAL_ILLUMINATION"
    except Exception:
        pass
    try:
        ee.fast_gi_quality = 0.35
    except Exception:
        pass
    S.render.resolution_x = args.width
    S.render.resolution_y = args.height
    S.render.resolution_percentage = 100
    S.render.image_settings.file_format = "PNG"
    S.render.image_settings.color_mode = "RGB"
    S.render.image_settings.color_depth = "8"
    S.render.film_transparent = False
    world = bpy.data.worlds.new("Warm dim basement ambient")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.22, 0.205, 0.18, 1)
    bg.inputs[1].default_value = 0.28
    S.world = world
    S.view_settings.view_transform = "AgX"
    S.view_settings.look = "AgX - Medium High Contrast"
    S.view_settings.exposure = 0.55


def source_hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob("*.py"))}


def write_interface():
    data = {
        "schema": "critical-shift.section-interface.design.v1",
        "section_id": "condenser-bay",
        "revision": args.revision,
        "date": "2026-09-11",
        "status": "local_authoring_in_progress",
        "units": "metres",
        "dimensions_are_implementation_decisions": True,
        "frame": {
            "origin": [0, 0, 0],
            "origin_meaning": "D01 service threshold centre at finished bay floor",
            "inward_axis": "+Y",
            "up_axis": "+Z",
            "right_axis": "+X",
            "origin_in_turbine_local": list(ORIGIN_IN_TURBINE),
            "transform_note": "turbine_xyz = condenser_xyz + origin_in_turbine_local",
            "neighbor_alignment_verified": False,
        },
        "envelopes": {
            "main_clear": {"min": [X0, Y0, Z0], "max": [X1, Y1, Z1]},
            "wall_thickness_m": WALL,
            "floor_z": 0,
            "ceiling_z": Z1,
            "justification": "6.0 m height: hotwell + 2.9 m shell + neck to turbine slab + 2.4 m aisle headroom. Plan sized around CD-01, 3.5 m east bundle reserve, west operator aisle and south stair strip.",
        },
        "portals": [
            {
                "id": "D01",
                "marker": "IF_PORTAL_D01_SERVICE",
                "centre": [0, 0, 0],
                "outward_normal": [0, -1, 0],
                "clear_width_m": D01_W,
                "clear_height_m": D01_H,
                "type": "two_opposed_sliding_leaves_parked_open",
                "adjacent_section": None,
                "binding_status": "unbound_receiving_service_connector",
                "traversable_design_intent": True,
            }
        ],
        "utilities": [
            {
                "id": "U04_RECEIVE",
                "marker": "IF_LP_EXHAUST_CONDENSER",
                "kind": "LP_steam_exhaust_receive",
                "centre": list(EXH_C),
                "centre_in_turbine_local": list(to_turbine(EXH_C)),
                "outward_normal": [0, 0, 1],
                "cross_section_m": [EXH_X, EXH_Y],
                "adjacent_section": "turbine-room",
                "adjacent_marker": "IF_LP_EXHAUST_CONDENSER",
                "binding_status": "geometric_receive_of_accepted_U04_opening_not_assembled",
            },
            {
                "id": "U02_HANDOFF",
                "marker": "IF_CONDENSATE_HANDOFF",
                "kind": "condensate_return_stub",
                "centre": list(IF_CONDENSATE_HANDOFF),
                "outward_normal": [0, -1, 0],
                "diameter_design_m": 0.2,
                "adjacent_section": "turbine-room",
                "adjacent_marker": "IF_CONDENSATE_RETURN",
                "binding_status": "local_stub_only; turbine U02 cap remains turbine-owned; integrator must route south then up to turbine (9.5,0,0.45)",
            },
            {
                "id": "CW_S",
                "marker": "IF_CW_SUPPLY",
                "centre": list(IF_CW_SUPPLY),
                "outward_normal": [1, 0, 0],
                "diameter_design_m": 0.3,
                "binding_status": "provisional_unbound",
            },
            {
                "id": "CW_R",
                "marker": "IF_CW_RETURN",
                "centre": list(IF_CW_RETURN),
                "outward_normal": [1, 0, 0],
                "diameter_design_m": 0.3,
                "binding_status": "provisional_unbound",
            },
            {"id": "DRAIN", "marker": "IF_DRAIN_OUT", "centre": list(IF_DRAIN_OUT), "binding_status": "provisional_unbound"},
            {"id": "VENT", "marker": "IF_VENT_OUT", "centre": list(IF_VENT_OUT), "binding_status": "provisional_unbound"},
        ],
        "equipment_zones": [
            {"id": "CD-01", "purpose": "surface condenser under U04", "centre": list(CD_C)},
            {"id": "CEP-A", "purpose": "condensate extraction pump A", "centre": list(P1)},
            {"id": "CEP-B", "purpose": "condensate extraction pump B", "centre": list(P2)},
            {"id": "EJ-01", "purpose": "two-stage air ejector", "centre": list(EJ_C)},
            {"id": "OP", "purpose": "operator station", "centre": list(OP_C)},
        ],
        "circulation": {
            "west_aisle": WEST_AISLE,
            "south_walk": SOUTH_WALK,
            "east_pull": EAST_PULL,
            "north_pump_apron": NORTH_PUMP_APRON,
            "stretcher_cart_test_envelope_m": list(CART),
            "navigation_mesh": "not_built",
        },
        "interaction_hooks": k.HOOKS,
        "engine_handoff": {
            "runtime_collision": "engine_owned_pending",
            "navigation": "engine_owned_pending",
            "thermodynamics": "not_simulated_scenic_only",
            "whole_facility_travel_validation": "pending",
        },
        "known_issues": [
            "Turbine U02 blind cap is not removed; required integrator action is documented, not performed.",
            "Cooling-water wall flanges are local and capped; they do not prove a facility loop to the cooling plant.",
            "D01 has no constructed remote corridor. Door opening is real inside this module.",
            "No engineering ratings are certified.",
        ],
    }
    (ROOT / "interface.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    S["support_registry"] = json.dumps(k.SUPPORT)
    S["interaction_hooks"] = json.dumps(k.HOOKS)


def main():
    build_architecture()
    build_equipment()
    cameras()
    settings()
    skip_shadow = ("bolt", "tick", "grate", "stud", "saw cut", "lettering", "needle", "pivot", "slat", "fin")
    for o in S.objects:
        low = o.name.lower()
        if o.type == "FONT" or any(s in low for s in skip_shadow):
            o.visible_shadow = False
    hashes = source_hashes()
    S["section_id"] = "condenser-bay"
    S["source_revision"] = args.revision
    S["authoring_source_sha256"] = json.dumps(hashes)
    S["origin_in_turbine_local"] = json.dumps(list(ORIGIN_IN_TURBINE))
    write_interface()
    counts = {
        "objects": len(S.objects),
        "meshes": len(bpy.data.meshes),
        "materials": len(bpy.data.materials),
        "cameras": len([o for o in S.objects if o.type == "CAMERA"]),
        "lights": len([o for o in S.objects if o.type == "LIGHT"]),
        "collections": [c.name for c in bpy.data.collections],
    }
    out_rev = ROOT / "production" / "renders" / "review" / args.revision
    out_rev.mkdir(parents=True, exist_ok=True)
    ckpt = ROOT / "production" / "checkpoints" / args.revision
    ckpt.mkdir(parents=True, exist_ok=True)
    for source in HERE.glob("*.py"):
        shutil.copy2(source, ckpt / source.name)
    (ROOT / "production" / "cameras.json").write_text(json.dumps({"fixed": CAMERAS, "walk": WALK}, indent=2), encoding="utf-8")
    blend = HERE / "condenser_bay.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
    blend_hash = hashlib.sha256(blend.read_bytes()).hexdigest()
    manifest = {
        "revision": args.revision,
        "blend": str(blend),
        "blend_sha256": blend_hash,
        "source_sha256": hashes,
        "counts": counts,
        "support_anchors": len(k.SUPPORT),
        "hooks": len(k.HOOKS),
        "render_engine": S.render.engine,
        "eevee_raytracing": bool(S.eevee.use_raytracing),
        "origin_in_turbine_local": list(ORIGIN_IN_TURBINE),
    }
    (out_rev / "build_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (ckpt / "build_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("CONDENSER_BUILD_OK", args.revision, counts["objects"], "objects", blend_hash[:16], flush=True)
    from validate import main as validate_main

    validate_main()
    if args.render:
        from render import render_set

        render_set(ROOT, args.revision, args.render, args.samples, args.width, args.height)


if __name__ == "__main__":
    main()
