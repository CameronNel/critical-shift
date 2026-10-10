"""Stage 1 of the medical-reanimation material bake: unique, non-overlapping UVs.

Blender 5.2.2 LTS:
  blender --background --disable-autoexec -noaudio module_overhaul_R2.blend --python-exit-code 1 \
    --python med_bake_prep.py -- --out PREP.blend [--atlases 8]

Works on a derivative; the source module is never saved over. For every render-visible mesh
that has at least one procedural or image-driven material it
  * applies modifiers (so the baked mesh is the shipped mesh),
  * adds a second UV layer 'BAKE' (UV0 is left alone),
  * packs all of them into N square atlases at a shared texel density, with a higher
    density for props than for the big room shells,
  * parks faces nobody can see (the outer side of floor, ceiling and walls) on a
    single junk texel so they cost no atlas space.
Writes bake_groups.json (object -> atlas index) beside the output.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument('--out', type=Path, required=True)
ap.add_argument('--atlases', type=int, default=8)
args = ap.parse_args(argv)

PROC = ('TEX_NOISE', 'TEX_VORONOI', 'TEX_WAVE', 'TEX_MUSGRAVE', 'TEX_BRICK', 'TEX_CHECKER',
        'TEX_GRADIENT', 'BEVEL', 'AMBIENT_OCCLUSION', 'TEX_MAGIC', 'TEX_IMAGE', 'BUMP', 'NORMAL_MAP')
ROOM_CENTRE = Vector((0.0, 5.55, 1.8))      # interior point used to tell visible shell faces
SHELL_AREA = 5.0                            # m2: objects above this are room shells
SHELL_FACTOR, PROP_FACTOR = 0.6, 1.3        # relative texel density
MARGIN = 0.004                              # island gap, fraction of the atlas (8 px at 2K)
JUNK = (0.9985, 0.9985)

scene = bpy.context.scene
view_layer = bpy.context.view_layer


def is_procedural(mat):
    return bool(mat and mat.use_nodes and any(n.type in PROC for n in mat.node_tree.nodes))


targets = [o for o in scene.objects
           if o.type == 'MESH' and not o.hide_render
           and any(is_procedural(s.material) for s in o.material_slots)]
for o in targets:
    o.hide_viewport = False
    o.hide_set(False)
for lc in view_layer.layer_collection.children:
    lc.exclude = False
unselectable = [o.name for o in targets if o.name not in view_layer.objects]
assert not unselectable, f'objects not in the view layer: {unselectable[:5]}'
print('TARGETS', len(targets))

# 1. apply modifiers so the baked mesh is the shipped mesh
dg = bpy.context.evaluated_depsgraph_get()
applied = 0
for o in targets:
    if o.modifiers:
        new = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        new.name = o.data.name + '_baked'
        o.modifiers.clear()
        o.data = new
        applied += 1
print('MODIFIERS_APPLIED_ON', applied)
view_layer.update()

# 2. per-object visible area and culled (unseen) faces
vis_area, culled = {}, {}
for o in targets:
    me = o.data
    me.calc_loop_triangles()
    mw3 = o.matrix_world.to_3x3()
    total = sum(p.area for p in me.polygons)
    shell = total * abs(o.matrix_world.to_scale().x * o.matrix_world.to_scale().y) > SHELL_AREA
    dead, area = [], 0.0
    for p in me.polygons:
        if shell:
            c = o.matrix_world @ p.center
            n = (mw3 @ p.normal).normalized()
            if n.dot(ROOM_CENTRE - c) <= 0:
                dead.append(p.index)
                continue
        area += p.area
    vis_area[o.name] = area
    culled[o.name] = dead
    o['bake_shell'] = bool(shell)
    if not me.uv_layers.get('BAKE'):
        uv = me.uv_layers.new(name='BAKE')
        me.uv_layers.active = uv
        uv.active_render = True
print('VISIBLE_AREA_M2', round(sum(vis_area.values()), 1), 'CULLED_FACES', sum(len(v) for v in culled.values()))

# 3. balanced groups (first-fit decreasing on density-weighted area)
weight = {o.name: vis_area[o.name] * (SHELL_FACTOR if o['bake_shell'] else PROP_FACTOR) ** 2 for o in targets}
order = sorted(targets, key=lambda o: -weight[o.name])
bins = [[] for _ in range(args.atlases)]
load = [0.0] * args.atlases
for o in order:
    k = load.index(min(load))
    bins[k].append(o)
    load[k] += weight[o.name]
print('GROUP_LOAD', [round(v) for v in load])


def pack_group(objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    view_layer.objects.active = objs[0]
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='FACE')
    bpy.ops.mesh.reveal()
    for o in objs:
        bm = bmesh.from_edit_mesh(o.data)
        bm.faces.ensure_lookup_table()
        for i in culled[o.name]:
            bm.faces[i].hide_set(True)
        bmesh.update_edit_mesh(o.data)
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.0, scale_to_bounds=False)
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.average_islands_scale()
    for o in objs:                        # density tier, applied about the origin before packing
        f = SHELL_FACTOR if o['bake_shell'] else PROP_FACTOR
        bm = bmesh.from_edit_mesh(o.data)
        lay = bm.loops.layers.uv['BAKE']
        for face in bm.faces:
            if not face.hide:
                for loop in face.loops:
                    loop[lay].uv *= f
        bmesh.update_edit_mesh(o.data)
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=MARGIN)
    for o in objs:                        # keep a free strip for the junk texel, park culled faces on it
        bm = bmesh.from_edit_mesh(o.data)
        lay = bm.loops.layers.uv['BAKE']
        for face in bm.faces:
            if face.hide:
                for loop in face.loops:
                    loop[lay].uv = Vector(JUNK)
            else:
                for loop in face.loops:
                    loop[lay].uv *= 0.985
        bmesh.update_edit_mesh(o.data)
    bpy.ops.mesh.reveal(select=False)
    bpy.ops.object.mode_set(mode='OBJECT')


groups = {}
stats = []
for k, objs in enumerate(bins):
    if not objs:
        continue
    pack_group(objs)
    used = world = 0.0
    for o in objs:
        lay = o.data.uv_layers['BAKE'].data
        o['bake_atlas'] = k
        groups[o.name] = k
        m = o.data
        for p in m.polygons:
            if p.index in set(culled[o.name]):
                continue
            pts = [lay[i].uv for i in p.loop_indices]
            a = 0.0
            for i in range(1, len(pts) - 1):
                a += abs((pts[i] - pts[0]).cross(pts[i + 1] - pts[0])) / 2
            used += a
            world += p.area
    px_per_m = math.sqrt(used / world) * 2048 if world else 0
    stats.append((k, len(objs), round(world, 1), round(used, 3), round(px_per_m)))
    print('ATLAS', k, 'objects', len(objs), 'world_m2', round(world, 1), 'uv_fill', round(used, 3), 'avg_px_per_m_at_2K', round(px_per_m))

out_json = args.out.with_suffix('.groups.json')
out_json.write_text(json.dumps({'groups': groups, 'stats': stats}, indent=1))
bpy.ops.wm.save_as_mainfile(filepath=str(args.out), compress=True)
print('SAVED', args.out, out_json)
