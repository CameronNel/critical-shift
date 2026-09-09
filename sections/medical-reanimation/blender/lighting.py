"""Practical lighting. Cyan is local to OCRU and screens. Warm overhead key."""
from __future__ import annotations

import bpy
from mathutils import Vector

import mesh as g


def _area(name, loc, size, color, watts, look, shape="RECTANGLE"):
    data = bpy.data.lights.new(name, "AREA")
    data.shape = shape
    data.size = size[0]
    if hasattr(data, "size_y"):
        data.size_y = size[1]
    data.energy = watts
    data.color = color
    data.shadow_soft_size = 0.08
    if hasattr(data, "spread"):
        data.spread = 1.4
    o = bpy.data.objects.new(name, data)
    o.location = loc
    direction = Vector(look) - Vector(loc)
    if direction.length > 1e-6:
        o.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    g.finish(o, name)
    return o


def _point(name, loc, color, watts, radius=0.08):
    data = bpy.data.lights.new(name, "POINT")
    data.energy = watts
    data.color = color
    data.shadow_soft_size = radius
    o = bpy.data.objects.new(name, data)
    o.location = loc
    g.finish(o, name)
    return o


def setup_world(scene):
    scene.world = scene.world or bpy.data.worlds.new("OCRU_World")
    scene.world.use_nodes = True
    nt = scene.world.node_tree
    bg = nt.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.008, 0.009, 0.011, 1)
        bg.inputs["Strength"].default_value = 0.06


def setup_cycles(scene, samples, device="CPU"):
    scene.render.engine = "CYCLES"
    scene.cycles.device = device
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPENIMAGEDENOISE"
    scene.cycles.preview_samples = max(8, samples // 4)
    scene.cycles.max_bounces = 8
    scene.cycles.transparent_max_bounces = 8
    scene.cycles.transmission_bounces = 8
    scene.cycles.caustics_reflective = False
    scene.cycles.caustics_refractive = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.use_persistent_data = True
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.15
    scene.view_settings.gamma = 1.0
    if device == "GPU":
        prefs = bpy.context.preferences.addons.get("cycles")
        if prefs:
            c = prefs.preferences
            c.compute_device_type = "HIP"
            try:
                c.get_devices()
            except Exception:
                pass
            hip = False
            for d in getattr(c, "devices", []):
                if d.type in {"HIP", "CUDA", "OPTIX", "ONEAPI"}:
                    d.use = True
                    hip = True
            if not hip:
                c.compute_device_type = "CUDA"
                try:
                    c.get_devices()
                except Exception:
                    pass
                for d in getattr(c, "devices", []):
                    if d.type in {"CUDA", "OPTIX"}:
                        d.use = True


def build():
    with g.use("LIGHTING"):
        warm = (1.0, 0.78, 0.55)
        orange = (1.0, 0.42, 0.12)
        cyan = (0.35, 0.85, 1.0)
        fixtures = [
            (-1.8, 1.6, 180), (1.5, 1.6, 180),
            (-1.8, 4.0, 200), (1.5, 4.0, 190),
            (-1.8, 6.5, 170), (1.5, 6.5, 180),
            (0.0, 8.2, 140), (2.4, 8.4, 110),
        ]
        for i, (x, y, w) in enumerate(fixtures):
            _area(f"L_ceil_{i}", (x, y, 3.20), (1.15, 0.12), warm, int(w * 0.72), (x, y, 0))
        for i, (x, y) in enumerate([(-3.2, 2.0), (-3.2, 7.2), (3.3, 1.8), (3.3, 7.6)]):
            _area(f"L_em_{i}", (x, y, 3.12), (0.10, 0.7), orange, 55, (x, y, 1.2))
        # OCRU interior cyan — local only
        _area("L_ocru_a", (-2.15, 3.6, 2.00), (1.1, 0.06), cyan, 220, (-1.7, 3.6, 1.05))
        _area("L_ocru_b", (-2.15, 4.7, 2.00), (1.1, 0.06), cyan, 260, (-1.7, 4.7, 1.05))
        _area("L_ocru_c", (-2.15, 5.8, 2.00), (1.1, 0.06), cyan, 220, (-1.7, 5.8, 1.05))
        _point("L_ocru_spill", (-1.55, 4.7, 1.45), cyan, 90, 0.22)
        _area("L_ocru_mouth", (-1.42, 4.7, 1.35), (0.12, 1.6), cyan, 70, (-1.1, 4.7, 1.2))
        # Console / screens
        _area("L_console", (-0.4, 8.55, 1.55), (0.9, 0.2), (0.45, 0.8, 0.9), 35, (-0.4, 8.2, 1.1))
        # Decon
        _area("L_decon", (2.33, 10.2, 2.45), (0.4, 0.4), warm, 70, (2.33, 10.2, 1.0), shape="SQUARE")
        # Entry transom
        _area("L_entry", (0.0, 0.15, 2.55), (1.4, 0.1), warm, 80, (0.0, 1.2, 1.4))
        # Bench task
        _area("L_bench", (3.4, 1.4, 2.15), (0.6, 0.1), warm, 40, (3.4, 1.4, 0.9))
        # Recovery
        _point("L_rec", (3.2, 4.7, 2.1), warm, 35, 0.2)
        # Fill so shadows are readable, not crushed
        _area("L_fill", (0.4, 4.5, 3.0), (4.0, 3.0), (0.85, 0.88, 0.95), 8, (0.4, 4.5, 1.0))
