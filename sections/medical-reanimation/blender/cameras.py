"""Fixed evaluation cameras. Transforms freeze after R01 unless a camera is invalid."""
from mathutils import Vector

import bpy

import config
import mesh as g


def aim(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def build():
    scene = bpy.context.scene
    with g.use("CAMERAS"):
        for name, spec in config.CAMERAS.items():
            cam = bpy.data.cameras.new(name)
            cam.lens = spec["lens"]
            cam.clip_start = 0.05
            cam.clip_end = 40.0
            cam.sensor_width = 36
            cam.dof.use_dof = False
            o = bpy.data.objects.new(name, cam)
            o.location = spec["loc"]
            aim(o, spec["look"])
            o["role"] = spec["role"]
            g.finish(o, name)
    scene.camera = bpy.data.objects["CAM_ENTRY"]
