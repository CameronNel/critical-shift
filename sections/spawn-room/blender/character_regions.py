#!/usr/bin/env python3
"""
Body regions for the crew worker (Blender 5.2 / bpy).

The merged body is cut into separate meshes so an outfit can hide the skin it covers (no poke-through, fewer triangles
drawn): TORSO, ARM_L/R, HAND_L/R, LEG_L/R, FOOT_L/R. The head is already its own object. All regions keep the shading
of the uncut body (per-vertex normals are copied), so the seams are invisible until a region is hidden.

    split_body(body_obj, collection)  -> {region: object}
    set_hidden(root, ["TORSO", "ARM_L", ...])  # hide or show regions (render + viewport), e.g. under a suit
"""

import bmesh
import bpy
from mathutils import Vector

REGIONS = ("TORSO", "ARM_L", "ARM_R", "HAND_L", "HAND_R", "LEG_L", "LEG_R", "FOOT_L", "FOOT_R")

# cut heights/widths in metres (body frame, feet at z=0, wearer's left = +x)
HIP_Z = 0.62         # below this, per-leg regions
ANKLE_Z = 0.165      # below this, feet
WRIST_Z = 0.685      # below this (outside the torso), hands
ARM_X = 0.24         # outside this: arm above the wrist, hand below it


def classify(c):
    x, z = c.x, c.z
    side = "L" if x > 0 else "R"
    if abs(x) > ARM_X:
        return ("HAND_" if z < WRIST_Z else "ARM_") + side
    if z < HIP_Z:
        return ("FOOT_" if z < ANKLE_Z else "LEG_") + side
    return "TORSO"


def _cut_mesh(me):
    """Copy of the mesh with clean edge loops at every region boundary, so the cuts are straight rings."""
    bm = bmesh.new()
    bm.from_mesh(me)
    planes = [((0, 0, HIP_Z), (0, 0, 1)), ((0, 0, ANKLE_Z), (0, 0, 1)), ((0, 0, WRIST_Z), (0, 0, 1)),
              ((ARM_X, 0, 0), (1, 0, 0)), ((-ARM_X, 0, 0), (1, 0, 0))]
    for co, no in planes:
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    cut = bpy.data.meshes.new("CS_cut_tmp")
    bm.to_mesh(cut)
    bm.free()
    return cut


def split_body(body, coll, name_prefix="WORKER"):
    me = _cut_mesh(body.data)
    bm_full = bmesh.new()
    bm_full.from_mesh(me)
    bm_full.verts.ensure_lookup_table()
    normals = {tuple(round(k, 5) for k in v.co): v.normal.copy() for v in bm_full.verts}
    groups = {r: [] for r in REGIONS}
    for f in bm_full.faces:
        groups[classify(f.calc_center_median())].append(f.index)
    bm_full.free()
    out = {}
    for region in REGIONS:
        keep = set(groups[region])
        if not keep:
            continue
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.faces.ensure_lookup_table()
        drop = [f for f in bm.faces if f.index not in keep]
        bmesh.ops.delete(bm, geom=drop, context="FACES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        new_me = bpy.data.meshes.new("%s_BODY_%s" % (name_prefix, region))
        bm.to_mesh(new_me)
        bm.free()
        for p in new_me.polygons:
            p.use_smooth = True
        new_me.normals_split_custom_set_from_vertices(
            [normals.get(tuple(round(k, 5) for k in v.co), Vector((0, 0, 1))) for v in new_me.vertices])
        for m in body.data.materials:
            new_me.materials.append(m)
        o = bpy.data.objects.new(new_me.name, new_me)
        o["cs_region"] = region
        coll.objects.link(o)
        out[region] = o
    bpy.data.meshes.remove(me)
    return out


def set_hidden(root, hidden):
    """Hide (True) the named regions on this character, show the rest."""
    hidden = set(hidden)
    for o in root.children_recursive:
        r = o.get("cs_region")
        if r:
            o.hide_render = r in hidden
            o.hide_viewport = r in hidden
