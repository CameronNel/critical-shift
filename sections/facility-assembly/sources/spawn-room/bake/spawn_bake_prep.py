"""Stage 1 of the spawn-room material bake: unique, non-overlapping UVs on a derivative.

Blender 5.2.2 LTS:
  blender --background --disable-autoexec -noaudio module.blend --python-exit-code 1 \
    --python spawn_bake_prep.py -- --out PREP.blend [--atlases 10]

The source module is never saved over. A mesh is baked only if it has at least one opaque,
non-emissive Principled slot with procedural or image-driven inputs. Everything else stays on its
original material and is left to whatever the engine export already does with it: emissive
surfaces (screens, bulbs), glass and other transparent surfaces, mix/transparent shader roots, and
the whole EXTERIOR_spawn-room collection. UV0 is untouched; the bake uses a second layer 'BAKE'.
Shell faces that look away from their room (the outer side of floor, ceiling and wall slabs) are
parked on a single junk texel so they cost no atlas space. Nothing else is culled.
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
ap.add_argument('--atlases', type=int, default=10)
args = ap.parse_args(argv)

PROC = ('TEX_NOISE', 'TEX_VORONOI', 'TEX_WAVE', 'TEX_MUSGRAVE', 'TEX_BRICK', 'TEX_CHECKER',
        'TEX_GRADIENT', 'BEVEL', 'AMBIENT_OCCLUSION', 'TEX_MAGIC', 'TEX_IMAGE', 'BUMP', 'NORMAL_MAP')
SHELL_AREA = 5.0
SHELL_FACTOR, PROP_FACTOR = 0.6, 1.3
MARGIN = 0.004
JUNK = (0.9985, 0.9985)
EXTERIOR = 'EXTERIOR_spawn-room'

scene = bpy.context.scene
view_layer = bpy.context.view_layer


def slot_class(mat):
    if not (mat and mat.use_nodes):
        return 'none'
    nodes = mat.node_tree.nodes
    bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
    out = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output), None)
    root = out.inputs['Surface'].links[0].from_node if out and out.inputs['Surface'].links else None
    if bsdf is None or root is None or root.type != 'BSDF_PRINCIPLED':
        return 'special'
    ec = bsdf.inputs['Emission Color']
    es = bsdf.inputs['Emission Strength']
    if es.default_value > 0.001 and (es.is_linked or ec.is_linked or sum(ec.default_value[:3]) > 0.001):
        return 'emissive'
    t, a = bsdf.inputs['Transmission Weight'], bsdf.inputs['Alpha']
    if t.is_linked or t.default_value > 0.01 or a.is_linked or a.default_value < 0.999:
        return 'transparent'
    return 'proc' if any(n.type in PROC for n in nodes) else 'plain'


exterior = {o.name for o in bpy.data.collections[EXTERIOR].all_objects} if EXTERIOR in bpy.data.collections else set()
targets = [o for o in scene.objects
           if o.type == 'MESH' and not o.hide_render and o.name not in exterior
           and any(slot_class(s.material) == 'proc' for s in o.material_slots)]
for o in targets:
    o.hide_viewport = False
    o.hide_set(False)
for lc in view_layer.layer_collection.children:
    lc.exclude = False
missing = [o.name for o in targets if o.name not in view_layer.objects]
assert not missing, f'objects not in the view layer: {missing[:5]}'
print('TARGETS', len(targets), 'EXTERIOR_EXCLUDED', len(exterior))

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

# interior reference point per room: centre of the non-shell objects of each room collection
ROOM_COLLECTIONS = ('BRIEFING_ROOM', 'LOCKER_ROOM', 'FACILITY_HALL')


def bbox_centre(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return (lo + hi) / 2


def mesh_area(o):
    return sum(p.area for p in o.data.polygons) * abs(o.matrix_world.to_scale().x * o.matrix_world.to_scale().y)


room_centres = {}
for name in ROOM_COLLECTIONS:
    members = [o for o in bpy.data.collections[name].all_objects if o.type == 'MESH' and mesh_area(o) <= SHELL_AREA]
    room_centres[name] = bbox_centre(members)
print('ROOM_CENTRES', {k: [round(v, 1) for v in c] for k, c in room_centres.items()})

vis_area, culled = {}, {}
for o in targets:
    me = o.data
    mw3 = o.matrix_world.to_3x3()
    shell = mesh_area(o) > SHELL_AREA
    centre = None
    if shell:
        here = o.matrix_world.translation + bbox_centre([o]) - o.matrix_world.translation
        centre = min(room_centres.values(), key=lambda c: (c - here).length)
    dead, area = [], 0.0
    for p in me.polygons:
        if shell:
            c = o.matrix_world @ p.center
            n = (mw3 @ p.normal).normalized()
            # Only faces that look away from their room are dropped. A 'buried within 3 cm of another
            # surface' rule was tried and removed: large planks and wall panels that are only partly
            # covered (rug edge, flush dressing) were dropped whole and rendered black where visible.
            if n.dot(centre - c) <= 0:
                dead.append(p.index)
                continue
        area += p.area
    vis_area[o.name], culled[o.name] = area, dead
    o['bake_shell'] = bool(shell)
    if not me.uv_layers.get('BAKE'):
        uv = me.uv_layers.new(name='BAKE', do_init=False)
        me.uv_layers.active = uv
        uv.active_render = True
print('VISIBLE_AREA_M2', round(sum(vis_area.values()), 1), 'CULLED_FACES', sum(len(v) for v in culled.values()))

weight = {o.name: vis_area[o.name] * (SHELL_FACTOR if o['bake_shell'] else PROP_FACTOR) ** 2 for o in targets}
shells = sorted([o for o in targets if o['bake_shell']], key=lambda o: -weight[o.name])
props = sorted([o for o in targets if not o['bake_shell']], key=lambda o: o.matrix_world.translation.y)
shell_w = sum(weight[o.name] for o in shells)
total_w = shell_w + sum(weight[o.name] for o in props)
n_shell = max(1, min(args.atlases - 1, round(args.atlases * shell_w / total_w)))
bins = [[] for _ in range(args.atlases)]
load = [0.0] * args.atlases
for o in shells:
    k = load.index(min(load[:n_shell]))
    bins[k].append(o)
    load[k] += weight[o.name]
per_slab = sum(weight[o.name] for o in props) / (args.atlases - n_shell)
k = n_shell
for o in props:
    if load[k] >= per_slab and k < args.atlases - 1:
        k += 1
    bins[k].append(o)
    load[k] += weight[o.name]
print('GROUP_LOAD', [round(v) for v in load], 'shell atlases', n_shell)


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
    for o in objs:
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
    for o in objs:
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


groups, stats = {}, []
for k, objs in enumerate(bins):
    if not objs:
        continue
    pack_group(objs)
    used = world = 0.0
    for o in objs:
        o['bake_atlas'] = k
        groups[o.name] = k
        lay = o.data.uv_layers['BAKE'].data
        dead = set(culled[o.name])
        for p in o.data.polygons:
            if p.index in dead:
                continue
            pts = [lay[i].uv for i in p.loop_indices]
            a = sum(abs((pts[i] - pts[0]).cross(pts[i + 1] - pts[0])) / 2 for i in range(1, len(pts) - 1))
            used += a
            world += p.area
    px = math.sqrt(used / world) * 2048 if world else 0
    stats.append((k, len(objs), round(world, 1), round(used, 3), round(px)))
    print('ATLAS', k, 'objects', len(objs), 'world_m2', round(world, 1), 'uv_fill', round(used, 3), 'avg_px_per_m_at_2K', round(px))

args.out.with_suffix('.groups.json').write_text(json.dumps({'groups': groups, 'stats': stats}, indent=1))
bpy.ops.wm.save_as_mainfile(filepath=str(args.out), compress=True)
print('SAVED', args.out)
