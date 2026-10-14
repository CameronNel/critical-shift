"""Scoped runtime export of the compact map's collision proxies and anchors, with a Blender re-import check. Run on a built scene:

    blender --background combined_map.blend --python export_unity.py -- export_dir

What is exported (and nothing else; no visual meshes, no whole-map export):
  * COLLIDERS: every proxy from assembly_colliders.py (boxes, the stair ramp), custom properties kept (collider_role, zone, door_id, is_trigger, enabled_when, enabled_now);
  * DOORS: one empty per door (door_id, owner_room, kind, state_default, states, leads_to, clear_width_m, clear_height_m, leaf);
  * ROOMS: one empty per room placement (ROOM_<key>, source file, rotation) so a runtime importer can place each room's own prefab.
Format: FBX (Unity's built-in importer reads FBX; no GLB importer is assumed or installed). Blender 5.2 FBX exporter, apply_unit_scale, axis forward -Z, up Y,
custom properties on. The binding manifest (export_dir/binding_manifest.json) lists the A08 fields; fields with no decision in the repository are marked UNRESOLVED.
The re-import check opens the FBX in an empty scene and compares object names, counts and world bounds (1 mm tolerance) after converting back to Blender axes.
No Unity editor exists in this environment, so engine import, prefab binding and Player behaviour are NotRun / Blocked (see ASSEMBLY_REPORT.md)."""
import bpy, sys, os, json, math, hashlib, subprocess
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]
out = os.path.abspath(a[0]); os.makedirs(out, exist_ok=True)
fbx = os.path.join(out, 'compact_map_colliders_anchors.fbx')

def bounds(o):
    q = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return [[round(min(p[i] for p in q), 3) for i in range(3)], [round(max(p[i] for p in q), 3) for i in range(3)]]

if '--reimport' in a:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx, use_custom_props=True)
    rows = {o.name: dict(type=o.type, bounds=bounds(o) if o.type == 'MESH' else [[round(v, 3) for v in o.matrix_world.translation]] * 2,
                         props={k: (v if isinstance(v, (int, float, str, bool)) else str(v)) for k, v in o.items() if k in ('collider_role', 'door_id', 'state_default', 'is_trigger', 'zone')}) for o in bpy.data.objects}
    json.dump(rows, open(os.path.join(out, 'reimport_dump.json'), 'w'), indent=0); print('REIMPORT', len(rows), 'objects'); raise SystemExit(0)

sc = bpy.context.scene
for o in sc.objects: o.select_set(False)
anchors = bpy.data.collections.new('EXPORT_room_anchors'); sc.collection.children.link(anchors)
rooms = []
for o in list(bpy.data.objects):
    if o.name.startswith('ROOM_') and o.instance_type == 'COLLECTION':
        e = bpy.data.objects.new('ANCHOR_' + o.name, None); e.matrix_world = o.matrix_world.copy(); anchors.objects.link(e)
        e['room'] = o.name[5:]; e['source'] = o.get('source', ''); e['rotation_z_deg'] = round(math.degrees(o.rotation_euler.z), 3); e['placement_note'] = o.get('note', '')[:500]
        rooms.append(dict(room=o.name[5:], source=o.get('source', ''), translation=[round(v, 4) for v in o.location], rotation_z_deg=round(math.degrees(o.rotation_euler.z), 3)))
sel = [o for o in bpy.data.objects if any(c.name in ('COLLIDERS', 'DOORS', 'EXPORT_room_anchors') for c in o.users_collection)]
for c in ('COLLIDERS', 'DOORS'):
    if c in bpy.data.collections: bpy.data.collections[c].hide_viewport = False
for o in sel: o.hide_set(False); o.hide_viewport = False; o.select_set(True)
bpy.context.view_layer.objects.active = sel[0]
opts = dict(filepath=fbx, use_selection=True, object_types={'MESH', 'EMPTY'}, use_custom_props=True, apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL',
            axis_forward='-Z', axis_up='Y', bake_space_transform=False, mesh_smooth_type='FACE', use_mesh_modifiers=True, add_leaf_bones=False, bake_anim=False)
bpy.ops.export_scene.fbx(**opts)
expect = {o.name: dict(type=o.type, bounds=bounds(o) if o.type == 'MESH' else [[round(v, 3) for v in o.matrix_world.translation]] * 2) for o in sel}
# re-import in a separate empty Blender process
blender = bpy.app.binary_path
r = subprocess.run([blender, '--background', '--factory-startup', '--python', os.path.abspath(__file__), '--', out, '--reimport'], capture_output=True, text=True)
got = json.load(open(os.path.join(out, 'reimport_dump.json')))
miss = sorted(set(expect) - set(got)); extra = sorted(set(got) - set(expect)); bad = []
for k, v in expect.items():
    if k in got:
        g = got[k]['bounds']; e = v['bounds']
        if max(abs(g[i][j] - e[i][j]) for i in range(2) for j in range(3)) > 0.001: bad.append(dict(name=k, expected=e, got=g))
h = hashlib.sha256(open(fbx, 'rb').read()).hexdigest()
src = bpy.data.filepath
rev = subprocess.run(['git', '-C', os.path.dirname(src), 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
# the export is usually made from uncommitted builder changes (they are committed together with it): record whether the combined folder was dirty and a content
# hash of the scene and the scripts that build it, so the artifact can be traced even when git_revision_at_export predates it
here = os.path.dirname(os.path.abspath(__file__))
dirty = bool(subprocess.run(['git', '-C', here, 'status', '--porcelain', '--', '.'], capture_output=True, text=True).stdout.strip())
inputs = ['build_compact_map.py', 'build_combined_map.py', 'reactor_links.py', 'evacuation.py', 'assembly_colliders.py', 'export_unity.py']
ih = hashlib.sha256()
for f in inputs + [os.path.relpath(src, here)]:
    p = os.path.join(here, f)
    if os.path.exists(p): ih.update(f.encode()); ih.update(open(p, 'rb').read())
input_hash = ih.hexdigest()
rays = bpy.context.scene.get('reactor_y', 0.0)
check = dict(fbx=os.path.basename(fbx), sha256=h, bytes=os.path.getsize(fbx), exported=len(expect), reimported=len(got), missing=miss, extra=extra, bounds_mismatch_over_1mm=bad[:20],
             n_bounds_mismatch=len(bad), passed=not miss and not bad)
manifest = dict(
    schema='critical-shift compact-map binding manifest, draft (A08 fields); unreviewed',
    source=dict(scene='sections/facility-assembly/combined/combined_map.blend', builder='build_compact_map.py', git_revision_at_export=rev or 'UNRESOLVED', worktree_dirty_at_export=dirty,
                inputs_sha256=input_hash, inputs=inputs + ['combined_map.blend'], blender=bpy.app.version_string),
    export=dict(format='FBX', file=os.path.basename(fbx), sha256=h, settings={k: (sorted(v) if isinstance(v, set) else v) for k, v in opts.items() if k != 'filepath'}),
    scale_axes_origin=dict(units='metres', blender_frame='plan frame: +x east, +y north, +z up; origin (0, 0, 0) is the layout\'s plan origin (the reactor centre before the compact layout moved it); '
                                                 'the reactor centre is now at (0, %.2f, 0). Every exported anchor and collider is in this frame' % rays, fbx_axes='forward -Z, up Y (Unity left-handed import converts)',
                           room_origins='each ANCHOR_ROOM_<key> carries its module origin; a room prefab is placed at that anchor'),
    logical_ids=dict(rooms=[r['room'] for r in rooms], doors='door_id on DOOR_<id> empties and on collider thresholds/blockers (validation/doors.json)'),
    room_placements=rooms,
    mesh_prefab_mapping='UNRESOLVED: no approved per-room export route or prefab set exists in the repository; rooms are referenced by source file only',
    collider_roles=dict(floor='static, walkable', wall='static', roof='static', ramp='static, walkable stair proxy (about 31 degrees)', ladder='trigger: climb volume of the condenser escape ladder',
                        door_blocker='static while state in enabled_when (closed, locked); disabled while open', door_threshold='trigger: door interaction and room-entry events'),
    spawn_interaction_points='UNRESOLVED: the spawn room module owns spawn points; door interaction points are the DOOR_<id> anchors',
    state_variants='doors: open | closed | locked; default per door in doors.json. Visual leaves for the non-default state are in each room module (see the leaf column).',
    material_conversion='NotApplicable for this package (colliders and anchors carry no materials)',
    licensing='first-party geometry generated by build_compact_map.py / assembly_colliders.py',
    runtime_owner='UNRESOLVED: no runtime owner for map collision or doors is decided (design/code-architecture DECISIONS_AND_RISKS); doors would belong to the Interaction feature per STATE_AND_CONTRACTS, not decided here',
    reimport_check=check)
json.dump(manifest, open(os.path.join(out, 'binding_manifest.json'), 'w'), indent=1)
os.remove(os.path.join(out, 'reimport_dump.json'))
print('EXPORT', check['exported'], 'objects ->', fbx, '%d bytes' % check['bytes'], 're-import', 'PASS' if check['passed'] else 'FAIL', 'missing', len(miss), 'extra', len(extra), 'bounds mismatches', len(bad))
