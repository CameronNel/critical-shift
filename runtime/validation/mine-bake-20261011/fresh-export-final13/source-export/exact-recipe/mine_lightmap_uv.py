"""Dedicated per-mesh lighting UVs; preserve geometry and every surface UV channel."""
import hashlib
import numpy as np
import bpy


def surface_uv_digest(mesh):
    digest = hashlib.sha256()
    for index in (0, 2):
        values = np.empty(len(mesh.loops) * 2, dtype=np.float32)
        mesh.uv_layers[index].data.foreach_get("uv", values)
        digest.update(values.tobytes())
    return digest.hexdigest()


def generate(objects):
    meshes = [o for o in objects if o.type == "MESH" and len(o.data.uv_layers) >= 3
              and any(m and m.name.startswith("CS_mine_surface_") for m in o.data.materials)]
    for o in meshes:
        before = surface_uv_digest(o.data)
        bpy.ops.object.select_all(action="DESELECT")
        o.hide_set(False); o.select_set(True)
        bpy.context.view_layer.objects.active = o
        o.data.uv_layers.active_index = 1
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=np.radians(66), island_margin=0.002,
                                 area_weight=0.0, correct_aspect=False, scale_to_bounds=True)
        bpy.ops.object.mode_set(mode="OBJECT")
        o.data.uv_layers.active_index = 0
        o.data.uv_layers[0].active_render = True
        if before != surface_uv_digest(o.data):
            raise ValueError("Lighting unwrap changed surface UVs: " + o.name)
        values = np.empty(len(o.data.loops) * 2, dtype=np.float32)
        o.data.uv_layers[1].data.foreach_get("uv", values)
        if not np.isfinite(values).all() or values.min() < 0 or values.max() > 1.001:
            raise ValueError("Invalid lighting UV layout: " + o.name)
        print("CS_MINE_LIGHTMAP_UV", o.name, flush=True)
    return len(meshes)
