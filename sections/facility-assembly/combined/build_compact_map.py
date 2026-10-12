"""Compact variant of the combined map: the same rooms, halls and materials, packed tightly around the reactor hall. Run:

    blender --background --python build_compact_map.py -- [--output combined_map.blend]

Owner instruction (2026-10-12): the map should be as compact as possible. This is now THE main layout (owner instruction 2026-10-12: "Use the compact layout as the main map"): it writes `combined_map.blend`. It works by overriding the room placements and the hall list of
`build_combined_map.py` (imported, not edited), which is kept as the older spread-out layout (rebuild it with `build_combined_map.py --through compliance-dock --output spread_layout.blend`). Everything is unreviewed.

Layout rules: every room sits directly on the reactor hall's own stub or on its neighbour's door, so most links are zero-length. Door positions come from each room's module frame
(contracts/interface.json and measured meshes), transformed by the placement below, never typed in by hand. The front block (front end, spawn, mine, refinery, medical, fuel corridor)
keeps its placement: its rails, 34 m spine and corridor are fixed by those modules and moving them would break their interfaces."""
import bpy, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_combined_map as BM, reactor_links as R
from mathutils import Vector, Matrix

U = Vector((math.sqrt(0.5), -math.sqrt(0.5)))          # reactor SE stub direction
SEAM = Vector((11.0163, -11.0163))                      # SE stub outer seam (cooling-plant CONNECTIONS.md)
D_WASTE = 7.0                                            # hall length from the stub seam to the waste exterior face
TURB = (0.0, 14.5, 0.0)                                  # turbine D01 exterior face on the N stub end (y 14.5)
ELEC = (0.0, TURB[1] + 25.45, 0.0)                       # electrical on turbine D02 (turbine/electrical CONNECTIONS.md: origin (0, 25.45) in turbine coordinates)
COND = (TURB[0] + 1.6, TURB[1] + 7.4, -6.0)              # condenser bay below the turbine (condenser CONNECTIONS.md: turbine = local + (1.6, 7.4, -6.0))
COOL = (-14.5, 0.0, 0.0)                                 # cooling CP-P01 on the W stub end, inward +Y local = plan -X
WO = SEAM + U * (D_WASTE + 0.32)                         # waste WS_RECEIVING threshold (exterior face 0.32 before it)
WASTE = (WO.x, WO.y, 0.0)
DOCK = (38.0, -54.0, 0.0)                                # dock P1 threshold 2 m past the front-end hall's east stub end (x 36)

def rot(rz): c, s = math.cos(math.radians(rz)), math.sin(math.radians(rz)); return lambda x, y: (c * x - s * y, s * x + c * y)
def wxy(loc, rz, x, y): r = rot(rz)(x, y); return Vector((loc[0] + r[0], loc[1] + r[1]))

old = {r[0]: r for r in BM.ROOMS}
def room(key, lib, coll, loc, rz, note): return (key, lib, coll, loc, rz, note)
NEW = [old[k] for k in ('front-end-area', 'spawn-room', 'mine', 'refinery', 'medical-reanimation', 'fuel-corridor', 'reactor-room')]
NEW += [
    room('turbine-room', 'turbine-room/module_overhaul_R1.blend', 'MODULE_turbine-room', TURB, 0.0,
         'COMPACT: AAA finish (owner choice). End wall face (module y 0.0) on the reactor N stub outer end (plan y 14.5), so no hall: reactor, 3.7 m stub, turbine D01.'),
    room('electrical-room', 'electrical-room/overhaul/checkpoints/full-R11.blend', 'MODULE_electrical-room', ELEC, 0.0,
         'COMPACT: the contracts\' own proposal: origin (0, 25.45) in turbine coordinates, rotation 0; turbine reveal ends where the electrical south wall (module y -0.25) begins. D01 on turbine D02.'),
    room('condenser-bay', 'condenser-bay/module.blend', 'MODULE_condenser-bay', COND, 0.0,
         'COMPACT: condenser bay under the turbine, origin at turbine (1.6, 7.4, -6.0) (its CONNECTIONS.md); its U04 receive (3.0, 4.05, 6.0) lands on turbine U04 (4.6, 11.45, 0). Original R34 module (the AAA finish is unreviewed).'),
    room('waste-storage', 'waste-storage/module.blend', 'MODULE_waste-storage', WASTE, -135.0,
         'COMPACT: WS_RECEIVING threshold on the reactor SE diagonal stub axis, 7 m from the stub seam (a 7 m hall); rotation -135 sends inward +Y along plan (+0.707, -0.707). Clear of the spine and concourse.'),
    room('cooling-plant', 'cooling-plant/module.blend', 'MODULE_cooling-plant', COOL, 90.0,
         'COMPACT: CP-P01 on the reactor W stub end (plan (-14.5, 0)); rotation +90 sends inward +Y to plan -X. Cooling owns y >= 0 and the reactor owns the stub (cooling CONNECTIONS.md).'),
    room('compliance-dock', 'compliance-dock/module_overhaul_R1.blend', ['MODULE_compliance-dock', '09 Overhaul | full'], DOCK, -90.0,
         'COMPACT: facility_entry P1 2 m past the front-end hall east stub end; rotation -90 sends inward +Y to plan +X.'),
]
BM.ROOMS = NEW
for r in NEW[7:]: pass

# --- halls: only what the compact layout needs
E_DOOR = wxy(WASTE, -135.0, 6.32, 2.4)                    # WS_PERSONNEL exterior face (module (6.32, 2.4)), outward = module +X
OUT = Vector(rot(-135.0)(1, 0))
P1 = E_DOOR + OUT * 2.2
SPINE_X = 10.15
BM.LINKS.clear()
BM.LINKS['waste-link'] = dict(pts=[tuple(SEAM), tuple(SEAM + U * D_WASTE)], r=1.0, airlocks=[D_WASTE - 2.4], requires=('waste-storage',), zone='waste-storage')
BM.LINKS['waste-spine'] = dict(pts=[tuple(E_DOOR), tuple(P1), (SPINE_X, P1.y)], r=1.0, w=2.4, h=3.0, airlocks=[], requires=('waste-storage',), zone='service')

# --- reactor: drop the NE door and electrical label; open the stub doors that now lead into rooms
R.HALL_CUTS.pop('northeast_door', None); R.LABEL_SKIP.add('ELECTRICAL')
_orig_reactor = BM.PATCHES['reactor-room']
def patch_reactor_compact(wrap, lib_coll, omit):
    _orig_reactor(wrap, lib_coll, omit)
    n = 0
    for c in bpy.data.collections:
        if c.library and os.path.basename(c.library.filepath) == os.path.basename(BM.REACTOR_LIB):
            for o in c.all_objects:
                if o.name.startswith(('FUEL HANDLING.', 'MAIN ACCESS.', 'COOLING PLANT.')) and 'door' in o.name.lower(): omit.add(o.name); n += 1
    print('REACTOR stub doors left out', n)
BM.PATCHES['reactor-room'] = patch_reactor_compact
BM.TURBINE_CUTS.clear(); BM.MEDICAL_CUTS.clear()
BM.OMIT['fuel-corridor'] = []; BM.OMIT['compliance-dock'] = ['P1 deep back wall', 'P1 deep door leaf']
BM.OMIT.setdefault('front-end-area', [])
BM.OMIT['front-end-area'] = [n for n in BM.OMIT['front-end-area'] if n != 'service_door_leaf' and n != 'service_door_push']

# --- front-end spine east wall opened for the waste personnel hall (local copy, like the concourse cut on the west wall)
_orig_fe = BM.PATCHES['front-end-area']
def trim_spine_east(wrap, lib_coll, omit):
    import bmesh
    fx, fy, _ = next(r[3] for r in BM.ROOMS if r[0] == 'front-end-area')
    y0, y1 = P1.y - 1.2 - fy, P1.y + 1.2 - fy
    for name in ('spine_wall_1', 'spine_dado_1'):
        o = lib_coll.objects.get(name) or next((x for x in lib_coll.all_objects if x.name == name), None)
        if o is None: print('SPINE east trim missing', name); continue
        for tag, lo_clamp, hi_clamp in (('a', None, y0), ('b', y1, None)):
            me = o.data.copy(); me.transform(BM.wm(o)); bm = bmesh.new(); bm.from_mesh(me)
            for v in bm.verts:
                if hi_clamp is not None and v.co.y > hi_clamp: v.co.y = hi_clamp
                if lo_clamp is not None and v.co.y < lo_clamp: v.co.y = lo_clamp
            bm.to_mesh(me); bm.free(); n = bpy.data.objects.new(o.name + '_trim_' + tag, me); wrap.objects.link(n)
        omit.add(name)
    for k in range(10):
        rib = f'spine_rib_1_{k}'; ro = lib_coll.objects.get(rib) or next((x for x in lib_coll.all_objects if x.name == rib), None)
        if ro is not None:
            ry = (BM.wm(ro) @ Vector((0, 0, 0))).y + fy
            if y0 + fy - 0.6 <= ry <= y1 + fy + 0.6: omit.add(rib)
    print('SPINE east wall opened plan y %.2f to %.2f' % (P1.y - 1.2, P1.y + 1.2))
BM.PATCHES['front-end-area'] = lambda w, l, o: (_orig_fe(w, l, o), trim_spine_east(w, l, o))

# --- plates on doors that open onto nothing
def plates():
    mat = bpy.data.materials.new('PLACEHOLDER_shutter_steel'); mat.use_nodes = True; b = mat.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.09, 0.1, 0.11, 1); b.inputs['Metallic'].default_value = 0.7; b.inputs['Roughness'].default_value = 0.5
    root = bpy.context.scene.collection.children['COMBINED_MAP']
    e = wxy(ELEC, 0.0, 0.0, 16.65); BM._box(root, 'PLACEHOLDER_electrical_D02_shutter', (e.x - 1.3, e.x + 1.3), (e.y - 0.05, e.y + 0.05), (0.0, 2.9), mat)
    d = wxy(WASTE, -135.0, 0.0, 18.2); t = Vector(rot(-135.0)(1, 0)); R.obox(root, 'PLACEHOLDER_waste_dispatch_shutter', d, t, 2.8, 0.12, 0.0, 3.0, mat)
    BM._box(root, 'PLACEHOLDER_condenser_D01_shutter', (COND[0] - 1.2, COND[0] + 1.2), (COND[1] - 0.1, COND[1] + 0.0), (COND[2], COND[2] + 2.6), mat)
    print('PLACEHOLDER plates added')
BM.add_door_placeholders = plates

if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    out = a[a.index('--output') + 1] if '--output' in a else os.path.join(HERE, 'combined_map.blend')
    BM.build('compliance-dock', out)
