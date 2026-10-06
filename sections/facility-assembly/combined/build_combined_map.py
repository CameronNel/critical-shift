"""Combined facility scene, built one room at a time from the drafted layout (design/facility-layout plan v7 and
design/facility-layout/front-end-area/DESIGN.md).

World frame: plan frame of the layout, metres, +x east, +y north, +z up. The front-end area keeps its as-built placement
(its local frame is plan + (-8, +80)); every other room is placed from its own interface, not guessed.

Rooms are linked (not copied) as collection instances, so the source modules are never edited. Run:

    blender --background --python build_combined_map.py -- --through <room-key> [--output combined_map.blend]

ROOMS is ordered; the scene contains every room up to and including --through. Each step is added only after the owner's OK.
Status of everything here: unreviewed, not accepted.
"""
import bpy, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', 'sources'))

# key, library file (relative to SRC), collection to instance, plan translation (x, y, z), rotation about z (degrees), note
# Objects left out of a room's linked membership (open doorways), by room key. Spawn: the 22 airlock exclusions of
# sections/facility-assembly/connections/access/DOOR_BINDINGS.json (row spawn_airlock) plus the four SERVICE_end closures
# that the old map's fix_spawn_transition.py removed.
OMIT = {'spawn-room': ['AIRLOCK_leaf_body', 'AIRLOCK_steel_face', 'AIRLOCK_structural_rib', 'AIRLOCK_structural_rib.001', 'AIRLOCK_leaf_body.001', 'AIRLOCK_steel_face.001', 'AIRLOCK_structural_rib.002', 'AIRLOCK_structural_rib.003', 'LIFE_airlock_gauge_case', 'LIFE_airlock_gauge_dial', 'LIFE_airlock_pressure_tick', 'LIFE_airlock_pressure_tick.001', 'LIFE_airlock_pressure_tick.002', 'LIFE_airlock_pressure_tick.003', 'LIFE_airlock_pressure_tick.004', 'LIFE_airlock_pressure_tick.005', 'LIFE_airlock_pressure_tick.006', 'LIFE_airlock_pressure_tick.007', 'LIFE_airlock_pressure_tick.008', 'LIFE_airlock_pressure_tick.009', 'LIFE_airlock_pressure_tick.010', 'LIFE_airlock_pressure_unit', 'SERVICE_end', 'SERVICE_end_washable_dado', 'SERVICE_end_coved_skirt', 'SERVICE_end_dado_cap']}

ROOMS = [
    ('front-end-area', 'front-end-area/front_end_area.blend', 'MODULE_front-end-area', (8.0, -80.0, 0.0), 0.0,
     'As built: local origin is the spawn airlock threshold centre, so plan = local + (8, -80).'),
    ('spawn-room', 'spawn-room/module.blend', 'MODULE_spawn-room', (8.0, -92.38, 0.0), 0.0,
     'Service stub end (spawn-local y 12.38, the old map\'s "spawn clean-route portal") sits on the cafeteria south wall, plan (8, -80); '
     'exit +Y into the cafeteria. DESIGN.md: spawn 12 m north of plan v7, reactor axis x = 8. Linked through a membership wrapper that omits '
     'the airlock leaves and the four SERVICE_end closures, as the old map did (ENVIRONMENT_BACKUP.md, DOOR_BINDINGS.json).'),
    ('mine', 'mine-r39/module_r39_aaa.blend', 'MODULE_mine-r39', (-14.4, -41.0, 0.0), 0.0,
     'Tunnel centre line (module y -29.0) on the yard mine lane (plan y -70); tunnel mouth (module x -39.0, first timber set) on the '
     'end of the yard portal mouth (front-end local x -61.4 = plan x -53.4). Both tunnels run west, so no rotation.'),
]

def build(through, output):
    keys = [r[0] for r in ROOMS]
    if through not in keys: raise SystemExit(f'unknown room {through}; choose from {keys}')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; sc.name = 'COMBINED_MAP'
    root = bpy.data.collections.new('COMBINED_MAP'); sc.collection.children.link(root)
    for key, lib, coll, loc, rz, note in ROOMS[:keys.index(through) + 1]:
        path = os.path.join(SRC, lib)
        with bpy.data.libraries.load(path, link=True, relative=True) as (src, dst):
            if coll not in src.collections: raise SystemExit(f'{lib} has no collection {coll}')
            dst.collections = [coll]
        lib_coll = dst.collections[0]; omit = set(OMIT.get(key, ()))
        if omit:
            # membership wrapper: the room's objects are linked individually into a local collection, minus the omitted doorway closures.
            # Linked objects cannot be re-parented, so the wrapper itself is instanced at the placement transform (the source module is not edited).
            wrap = bpy.data.collections.new('ROOM_' + key + '_members'); kept = left = 0
            for o in lib_coll.all_objects:
                if o.name in omit: left += 1; continue
                wrap.objects.link(o); kept += 1
            inst = bpy.data.objects.new('ROOM_' + key, None); inst.instance_type = 'COLLECTION'; inst.instance_collection = wrap
            inst.location = loc; inst.rotation_euler = (0, 0, math.radians(rz)); inst['source'] = lib; inst['note'] = note
            root.objects.link(inst)
            print('WRAPPER', key, 'objects', kept, 'omitted', left)
        else:
            inst = bpy.data.objects.new('ROOM_' + key, None); inst.instance_type = 'COLLECTION'; inst.instance_collection = lib_coll
            inst.location = loc; inst.rotation_euler = (0, 0, math.radians(rz)); inst['source'] = lib; inst['note'] = note
            root.objects.link(inst)
    bpy.ops.wm.save_as_mainfile(filepath=output, relative_remap=True)
    print('COMBINED', through, [r[0] for r in ROOMS[:keys.index(through) + 1]], '->', output)

if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    through = a[a.index('--through') + 1] if '--through' in a else ROOMS[0][0]
    out = a[a.index('--output') + 1] if '--output' in a else os.path.join(HERE, 'combined_map.blend')
    build(through, out)
