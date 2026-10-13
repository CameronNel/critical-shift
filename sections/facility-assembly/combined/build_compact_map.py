"""Compact map, assembly pass (2026-10-12/13): THE main layout. Run:

    blender --background --factory-startup --python build_compact_map.py -- [--output combined_map.blend]

Owner instructions: "the map should be as compact as possible", then (for this pass) "Ignore all previous specs and planning docs - build and decide what comes where
on your own with the goal of the most compact and logical map possible. Move around, rotate, transform, structural changes etc are all allowed."
Everything here is unreviewed and not accepted. It imports `build_combined_map.py` (the shared machinery, not edited) and overrides the room placements,
the hall list and the per-room patches. Rooms are still linked, never edited: every change is a local copy made below. Record: COMPACT_MAP.md, ASSEMBLY_REPORT.md.

Layout ("street" layout). The front block (front end, spawn, mine, refinery, medical) and the fuel corridor keep their placement: the yard rail fixes the refinery,
the refinery fuel door fixes the fuel corridor, and the corridor's far port fixes the reactor (all measured, COMBINED_MAP.md). The rest is packed onto that chain:
  * turbine on the reactor north stub (as before), condenser bay under it, now reached by a new stair from a door in the turbine's west wall;
  * electrical moved from the turbine's far end to its east flank, through a new 2.4 m door between two wall columns (turbine-local y 18.5);
  * waste and the compliance dock moved into the empty pocket east of the 34 m spine, each on a new door cut into the spine's east wall;
  * the fuel corridor's S03 waste-transfer port opened onto a new 11 m hall into the spine's west wall, so refinery -> fuel corridor -> spine -> waste is one line;
  * cooling stays on the reactor west stub. Doors that now open onto nothing are closed with their own leaves (local copies moved to the closed position)
    or, where the module has none (waste dispatch roller shutter), a new curtain.
Dropped: the 7 m diagonal waste hall, the 3.9 m waste-to-spine hall and the three PLACEHOLDER plates."""
import bpy, sys, os, math, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_combined_map as BM, reactor_links as R
from mathutils import Vector, Matrix

# ------------------------------------------------------------------------------------------------------------------------------------------------
# Placements (plan metres, rotation about z in degrees). Every number below is a measured module face; see COMPACT_MAP.md "Assembly pass".
# ------------------------------------------------------------------------------------------------------------------------------------------------
SPINE_E = 10.15          # spine east wall outer face (front-end spine_wall_1, local x 1.85..2.15, plan = local + (8, -80))
SPINE_W = 5.85           # spine west wall outer face (spine_wall_-1)
TURB = (0.0, 14.5, 0.0)  # turbine end wall face (module y 0) on the reactor north stub end (plan y 14.5)
COND = (TURB[0] + 1.6, TURB[1] + 7.4, -6.0)       # condenser bay under the turbine (its CONNECTIONS.md: turbine = local + (1.6, 7.4, -6.0))
ELEC_DOOR_Y = 18.5       # turbine-local y of the new east door: clear bay between wall columns at y 16 and 21 (feet +-0.32) and past the condensate return (ends y 16.8)
ELEC = (10.25 + 0.25, TURB[1] + ELEC_DOOR_Y, 0.0) # electrical D01 exterior face (module y -0.25) on the turbine east wall outer face (module x 10.25); rotation -90: D01 faces west
WASTE = (SPINE_E + 0.32, -25.48, 0.0)            # waste WS_RECEIVING exterior face (module y -0.32) on the spine east face; rotation -90: receiving faces west
DOCK = (SPINE_E + 2.0, -40.39, 0.0)              # dock P1 corridor (module y -2.0..0, back wall omitted) starts on the spine east face; rotation -90, P2 faces east (outside)
COOL = (-14.5, 0.0, 0.0)                         # cooling CP-P01 on the reactor west stub end (unchanged)
S03_Y = -43.6 + 16.0                             # fuel corridor S03_WASTE centre (module (16.4, 16)), plan y -27.6; outer wall face module x 16.74 = plan x -5.46
STAIR_DOOR_Y = 13.45     # turbine-local y of the condenser stair door (west wall): bay between columns at y 11 and 16, clear of the power conduit (ends y 12.4), 2.0 m wide

def rot(rz): c, s = math.cos(math.radians(rz)), math.sin(math.radians(rz)); return lambda x, y: (c * x - s * y, s * x + c * y)
def wxy(loc, rz, x, y): r = rot(rz)(x, y); return Vector((loc[0] + r[0], loc[1] + r[1]))

old = {r[0]: r for r in BM.ROOMS}
NEW = [old[k] for k in ('front-end-area', 'spawn-room', 'mine', 'refinery', 'medical-reanimation', 'fuel-corridor', 'reactor-room')]
NEW += [
    ('turbine-room', 'turbine-room/module_overhaul_R1.blend', 'MODULE_turbine-room', TURB, 0.0,
     'AAA finish (owner accepted 2026-10-12, unreviewed). End wall face (module y 0.0) on the reactor north stub end (plan y 14.5). New local cuts: east door (electrical) and west door (condenser stair).'),
    ('electrical-room', 'electrical-room/overhaul/checkpoints/full-R11.blend', 'MODULE_electrical-room', ELEC, -90.0,
     'ASSEMBLY: on the turbine east flank. D01 exterior face (module y -0.25) on the turbine east wall outer face (plan x 10.25) at turbine-local y 18.5; rotation -90 turns D01 to face west. D02 closed (no neighbour).'),
    ('condenser-bay', 'condenser-bay/module_aaa_A1.blend', 'MODULE_condenser-bay', COND, 0.0,
     'Under the turbine, origin at turbine (1.6, 7.4, -6.0) (its CONNECTIONS.md). D01 stub blanking removed locally; reached by the new condenser stair.'),
    ('waste-storage', 'waste-storage/module_aaa_A1.blend', 'MODULE_waste-storage', WASTE, -90.0,
     'ASSEMBLY: east of the spine. WS_RECEIVING exterior face (module y -0.32) on the spine east face (plan x 10.15) at plan y -25.48; rotation -90 turns receiving west. Personnel and dispatch doors closed.'),
    ('cooling-plant', 'cooling-plant/module_aaa_A1.blend', 'MODULE_cooling-plant', COOL, 90.0,
     'CP-P01 on the reactor W stub end (plan (-14.5, 0)); rotation +90 sends inward +Y to plan -X (unchanged).'),
    ('compliance-dock', 'compliance-dock/module_overhaul_R1.blend', ['MODULE_compliance-dock', '09 Overhaul | full'], DOCK, -90.0,
     'ASSEMBLY: east of the spine, south of waste. P1 corridor start (module y -2.0) on the spine east face; rotation -90 turns P1 west and the sealed arrival P2 east, to the outside.'),
]
BM.ROOMS = NEW

# ------------------------------------------------------------------------------------------------------------------------------------------------
# Halls: the S03 waste-transfer hall only (the south concourse is built by build_combined_map.py).
# ------------------------------------------------------------------------------------------------------------------------------------------------
BM.LINKS.clear()
BM.LINKS['waste-transfer'] = dict(pts=[(-5.46, S03_Y), (SPINE_W, S03_Y)], r=1.0, w=2.4, h=3.0, airlocks=[], requires=('fuel-corridor', 'front-end-area'), zone='waste-storage')
BM.LINK_NAMES['waste-transfer'] = 'WASTE TRANSFER'

# ------------------------------------------------------------------------------------------------------------------------------------------------
# Membership: what each room leaves out (open doorways) and what it closes.
# ------------------------------------------------------------------------------------------------------------------------------------------------
BM.OMIT['fuel-corridor'] = []
BM.OMIT['compliance-dock'] = ['P1 deep back wall', 'P1 deep door leaf']           # P1 corridor opens onto the spine
# front end: hall east door closed (it now opens onto the outside), the hall west door to the refinery colonnade open, yard service door closed
BM.OMIT['front-end-area'] = [n for n in BM.OMIT['front-end-area'] if n not in ('hall_E_door_leaf_-1.001', 'hall_E_door_leaf_1.001', 'service_door_leaf', 'service_door_push')]
BM.OMIT['front-end-area'] += ['hall_W_door_leaf_-1.001', 'hall_W_door_leaf_1.001']
# the hall's floor stencil and hanging sign "to dock" point at the east door, which is now a closed exit: left out (render review 2026-10-13); the spine door sign below replaces them
BM.OMIT['front-end-area'] += ['floor_stencil_dock', 'hang_to_dock', 'hang_to_dock_rod+0.9', 'hang_to_dock_rod-0.9']
# spawn exit airlock: the leaf pieces are left out by build_combined_map.py; the leaf hardware that stayed behind in the open doorway goes too (walk test 2026-10-13)
BM.OMIT['spawn-room'] = BM.OMIT['spawn-room'] + ['AIRLOCK_meeting_stile', 'AIRLOCK_meeting_stile.001', 'AIRLOCK_grip_collar', 'AIRLOCK_grip_collar.001', 'AIRLOCK_grip_collar.002',
    'AIRLOCK_grip_collar.003', 'AIRLOCK_manual_grip', 'AIRLOCK_manual_grip.001', 'LIFE_airlock_lens_guard', 'LIFE_airlock_lens_guard.001', 'LIFE_airlock_pressure_needle']
R.HALL_CUTS.pop('northeast_door', None); R.LABEL_SKIP.update({'ELECTRICAL', 'WASTE STORAGE'})

CLOSED = []      # (room, door id, objects moved, how) for the report (validation/doors.json)

def local_copy(wrap, omit, o, M, tag):
    """A local copy of linked object o (same mesh data, modifiers kept) with module-frame matrix M @ wm(o); the original is left out of the membership."""
    n = o.copy(); n.parent = None; n.matrix_basis = M @ BM.wm(o); n.name = o.name + tag
    wrap.objects.link(n); omit.add(o.name); return n

def bbox(o):
    m = BM.wm(o); q = [m @ Vector(c) for c in o.bound_box]
    return Vector([min(p[i] for p in q) for i in range(3)]), Vector([max(p[i] for p in q) for i in range(3)])

def split_openings(wrap, omit, objs, along, band, holes, tag=' cut'):
    """Open doorways in wall-like meshes by splitting them, not by deleting faces: every mesh whose box meets the wall band (module frame, axis 1 - along) and a hole
    (a0, a1 along `along`, below ztop) is replaced by local pieces clipped with bisect planes: the parts beside each hole and a lintel above it. Closed meshes get their cut
    ends capped (solid jambs); open ones (decals, skins) are clipped only. UVs are interpolated by the bisect, not stretched. Small dressing wholly inside a hole goes;
    text and curves go when their centre is inside a hole. Returns the number of objects replaced."""
    import bmesh
    nrm = 1 - along; done = 0
    def drop(o):
        if o.library is None:
            if any(x is o for x in wrap.objects): wrap.objects.unlink(o)
        else: omit.add(o.name)
    for o in objs:
        if (o.library is not None and o.name in omit) or o.type not in ('MESH', 'CURVE', 'FONT'): continue      # local copies may share an omitted linked name
        lo, hi = bbox(o)
        if hi[nrm] < band[0] or lo[nrm] > band[1]: continue
        hs = sorted(h for h in holes if hi[along] > h[0] + 1e-4 and lo[along] < h[1] - 1e-4 and lo.z < h[2] and hi.z > 0.02)
        if not hs: continue
        if o.type != 'MESH':
            c = (lo + hi) / 2
            if any(h[0] <= c[along] <= h[1] and c.z <= h[2] for h in hs): drop(o); done += 1
            continue
        if all(h[0] - 0.01 <= lo[along] and hi[along] <= h[1] + 0.01 and hi.z <= h[2] + 0.3 for h in hs[:1]) and (hi[along] - lo[along]) < 0.6:
            drop(o); done += 1; continue
        base = o.data.copy(); base.transform(BM.wm(o))
        segs = []; cur = lo[along] - 1.0
        for a, b, zt in hs: segs.append((cur, a, None)); cur = b
        segs.append((cur, hi[along] + 1.0, None))
        pieces = [s_ for s_ in segs if s_[1] - s_[0] > 1e-3] + [(a, b, zt) for a, b, zt in hs if hi.z > zt + 0.005]
        for k, (a, b, zt) in enumerate(pieces):
            bm = bmesh.new(); bm.from_mesh(base); closed = not any(e.is_boundary for e in bm.edges)
            def clip(co, no, outer):
                bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=co, plane_no=no, clear_outer=outer, clear_inner=not outer)
            na = [0.0, 0.0, 0.0]; na[along] = 1.0; ca = [0.0, 0.0, 0.0]; ca[along] = a; cb = [0.0, 0.0, 0.0]; cb[along] = b
            clip(ca, na, False); clip(cb, na, True)
            if zt is not None: clip((0, 0, zt), (0, 0, 1), False)
            if not bm.faces: bm.free(); continue
            if closed:
                edges = [e for e in bm.edges if e.is_boundary]
                if edges: bmesh.ops.holes_fill(bm, edges=edges, sides=0)
            me = bpy.data.meshes.new(o.name + tag); bm.to_mesh(me); bm.free()
            n = o.copy(); n.data = me; n.parent = None; n.matrix_basis = Matrix.Identity(4); n.name = o.name + tag + str(k)
            wrap.objects.link(n)
        bpy.data.meshes.remove(base)
        drop(o); done += 1
    return done

def hole_in_slab(wrap, omit, o, x0, x1, y0, y1):
    """Replace a slab-like mesh by four local pieces around the rectangle x0..x1, y0..y1 (module frame), clipped with bisect planes and capped."""
    import bmesh
    base = o.data.copy(); base.transform(BM.wm(o)); n = 0
    for k, planes in enumerate(([(y0, 1, True)], [(y1, 1, False)], [(y0, 1, False), (y1, 1, True), (x0, 0, True)], [(y0, 1, False), (y1, 1, True), (x1, 0, False)])):
        bm = bmesh.new(); bm.from_mesh(base)
        for v, ax, outer in planes:
            co = [0.0, 0.0, 0.0]; co[ax] = v; no = [0.0, 0.0, 0.0]; no[ax] = 1.0
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=co, plane_no=no, clear_outer=outer, clear_inner=not outer)
        edges = [e for e in bm.edges if e.is_boundary]
        if edges: bmesh.ops.holes_fill(bm, edges=edges, sides=0)
        me = bpy.data.meshes.new(o.name + ' holed'); bm.to_mesh(me); bm.free()
        c = o.copy(); c.data = me; c.parent = None; c.matrix_basis = Matrix.Identity(4); c.name = o.name + ' piece %d' % k; wrap.objects.link(c); n += 1
    bpy.data.meshes.remove(base); omit.add(o.name); return n

def close_sliding_pair(wrap, lib_coll, omit, room, door, y0, y1, ax0, ax1, shift, skip=('running rail', 'jamb', 'portal', 'lintel', 'threshold', 'seal', 'return')):
    """Leaves parked beside a doorway (|x| in ax0..ax1, y0..y1, module frame) slid shut: each side moves toward the centre by `shift`."""
    n = 0
    for o in list(lib_coll.all_objects):
        if o.name in omit or o.type not in ('MESH', 'CURVE', 'FONT') or any(s in o.name.lower() for s in skip): continue
        lo, hi = bbox(o)
        if lo.y < y0 or hi.y > y1 or lo.z < -0.05: continue
        if ax0 <= lo.x and hi.x <= ax1: d = -shift
        elif -ax1 <= lo.x and hi.x <= -ax0: d = shift
        else: continue
        local_copy(wrap, omit, o, Matrix.Translation((d, 0, 0)), ' closed'); n += 1
    CLOSED.append((room, door, n, 'sliding leaves moved %.2f m to the closed position' % shift)); print('CLOSED', room, door, n, 'objects')

def patch_turbine(wrap, lib_coll, omit):
    objs = list(dict.fromkeys(lib_coll.all_objects))
    # east wall, electrical door 2.4 x 2.7 m (like D01/D02) between the wall columns at y 16 and 21; west wall, condenser stair door 2.0 x 2.6 m between y 11 and 16
    ne = split_openings(wrap, omit, objs, 1, (9.85, 10.35), [(ELEC_DOOR_Y - 1.2, ELEC_DOOR_Y + 1.2, 2.7)])
    nw = split_openings(wrap, omit, objs, 1, (-4.35, -3.85), [(STAIR_DOOR_Y - 1.0, STAIR_DOOR_Y + 1.0, 2.6)])
    print('TURBINE doors cut: east', ne, 'west', nw, 'objects split')
    # D02 (north end) now opens onto the outside: its two parked leaves (module x +-1.39..2.57, y 23.87..23.98) and their fittings slide shut
    close_sliding_pair(wrap, lib_coll, omit, 'turbine-room', 'TURBINE_D02', 23.80, 24.00, 1.30, 2.66, 1.37)

def patch_electrical(wrap, lib_coll, omit):
    # D02 (module y 16.4) faces east onto the outside now: leaves parked at |x| 1.24..2.45, y 16.03..16.11 slide shut
    close_sliding_pair(wrap, lib_coll, omit, 'electrical-room', 'ELECTRICAL_D02', 16.00, 16.12, 1.22, 2.50, 1.25)

WASTE_LEAF = ('Personnel leaf', 'Personnel kick plate', 'Personnel panic bar', 'Panic bar bracket', 'Recessed engraved plate.017', 'Engraved WS_PERSONNEL')

def patch_waste(wrap, lib_coll, omit):
    # personnel door: the outward leaf (hinge (6.345, 3.065), shown swung open 90 degrees) is turned back into the opening; it faces the dock's wall now
    hinge = Vector((6.345, 3.065, 0.0)); M = Matrix.Translation(hinge) @ Matrix.Rotation(math.radians(-90), 4, 'Z') @ Matrix.Translation(-hinge); n = 0
    for o in list(lib_coll.all_objects):
        if o.name.startswith(WASTE_LEAF) and o.name not in omit: local_copy(wrap, omit, o, M, ' closed'); n += 1
    CLOSED.append(('waste-storage', 'WASTE_PERSONNEL', n, 'hinged leaf turned 90 degrees into the frame'))
    # dispatch: the module only has the rolled-up shutter (barrel, seal tracks). A closed curtain between the seal tracks: 2.5 x 2.8 m, 80 mm slats
    src = next((o for o in lib_coll.all_objects if o.name == 'Roller door barrel.001'), None)
    mat = src.data.materials[0] if src and src.data.materials else BM._mat('WASTE shutter steel', (0.25, 0.26, 0.25), 0.5, 0.8)
    for i in range(35):
        z = 0.08 * i; BM._box(wrap, 'WASTE dispatch shutter slat %02d' % i, (-1.25, 1.25), (17.80 + (0.004 if i % 2 else 0.0), 17.845), (z, z + 0.076), mat)
    BM._box(wrap, 'WASTE dispatch shutter bottom bar', (-1.25, 1.25), (17.78, 17.86), (0.0, 0.06), mat)
    CLOSED.append(('waste-storage', 'WASTE_DISPATCH', 36, 'new closed roller curtain (36 slats) between the seal tracks; the module has only the rolled-up barrel'))

def patch_condenser(wrap, lib_coll, omit):
    # D01 stub (module x +-1.24, y -2.56..0): its end wall and the local blanking panel and frame are left out, so the stub opens onto the new stair corridor
    n = 0
    for o in lib_coll.all_objects:
        if o.name.startswith(('D01 stub end wall', 'D01 local blanking', 'D01 blanking')): omit.add(o.name); n += 1
    print('CONDENSER D01 stub opened', n)

def patch_fuel(wrap, lib_coll, omit):
    n = 0
    for o in lib_coll.all_objects:
        # S03 (waste transfer) and the two boundary doors (refinery F01, reactor F02) are closed in F23ci; the freight route needs them open
        if o.name.startswith(('FC | Waste transfer', 'FC | Refinery boundary', 'FC | Reactor boundary')) and ('leaf' in o.name or 'wear' in o.name): omit.add(o.name); n += 1
    print('FUEL S03, F01 and F02 leaves left out', n)

def patch_reactor_assembly(wrap, lib_coll, omit):
    BM.patch_reactor(wrap, lib_coll, omit)
    n = 0
    for c in bpy.data.collections:
        if c.library and os.path.basename(c.library.filepath) == os.path.basename(BM.REACTOR_LIB):
            for o in c.all_objects:
                if (o.name.startswith(('FUEL HANDLING.', 'MAIN ACCESS.')) and 'door' in o.name.lower()) or o.name.startswith(('RH refine door hardware FUEL', 'RH refine door hardware MAIN')): omit.add(o.name); n += 1
    print('REACTOR N and W stub doors and their leaf hardware left out', n, '(the SE stub door stays closed)')
    # the south door cut (reactor_links.HALL_CUTS south_door) keeps 'RH walls trim YELLOW' whole: a 0.5 m high trim bar stayed across the doorway (walk test). Split it and anything else left in the opening
    objs = [o for c in bpy.data.collections if c.library and os.path.basename(c.library.filepath) == os.path.basename(BM.REACTOR_LIB) for o in c.all_objects if o.name not in omit] + [o for o in wrap.objects if o.library is None]
    print('REACTOR south doorway cleared:', split_openings(wrap, omit, list(dict.fromkeys(objs)), 0, (-12.3, -9.95), [(-2.5, 2.5, 5.0)]), 'objects split')

FE = old['front-end-area'][3]          # front-end placement (8, -80)
def fe(y): return y - FE[1]            # plan y -> front-end local y

def patch_front_end_spine(wrap, lib_coll, omit):
    """Three new openings in the spine walls (front-end local frame): waste receiving and dock P1 on the east wall, the S03 transfer hall on the west wall."""
    objs = [o for o in dict.fromkeys(lib_coll.all_objects) if o.name not in omit] + [o for o in wrap.objects if o.library is None]
    ne = split_openings(wrap, omit, objs, 1, (1.7, 2.3), [(fe(WASTE[1]) - 1.55, fe(WASTE[1]) + 1.55, 3.2), (fe(DOCK[1]) - 1.3, fe(DOCK[1]) + 1.3, 2.6)])
    objs = [o for o in dict.fromkeys(lib_coll.all_objects) if o.name not in omit] + [o for o in wrap.objects if o.library is None]
    nw = split_openings(wrap, omit, objs, 1, (-2.3, -1.7), [(fe(S03_Y) - 1.2, fe(S03_Y) + 1.2, 3.0)])
    # skirt dust decals that run across three doorways that are open in the source (found by the walk test): clipped at the openings
    objs = [o for o in dict.fromkeys(lib_coll.all_objects) if o.name not in omit and o.name.startswith('stain_')]
    nd = split_openings(wrap, omit, objs, 1, (-15.95, -15.6), [(8.62, 11.4, 2.6)]) + split_openings(wrap, omit, objs, 1, (17.6, 17.95), [(8.8, 11.18, 2.6)]) \
        + split_openings(wrap, omit, objs, 1, (-11.95, -11.6), [(24.83, 27.17, 2.7)]) + split_openings(wrap, omit, objs, 0, (0.0, 0.5), [(-1.3, 1.3, 2.6)]) \
        + split_openings(wrap, omit, objs, 0, (31.1, 31.9), [(-1.8, 1.8, 3.2)]) + split_openings(wrap, omit, objs, 0, (19.4, 20.6), [(-3.0, 3.0, 3.0)])
    # the front end's context_ground (an 8-vertex box, plan x -170..90, y -200..60, z -0.9..-0.15) roofs the condenser stair shaft: a hole is cut for the shaft
    g = next((o for o in lib_coll.all_objects if o.name == 'context_ground'), None)
    if g is not None:
        x0, x1 = ST['xw'] - ST['t'] - FE[0], ST['xe'] + ST['t'] - FE[0]; y0, y1 = ST['ybot'] - FE[1], ST['yn'] + ST['t'] - FE[1]
        print('GROUND hole for the stair shaft:', hole_in_slab(wrap, omit, g, x0, x1, y0, y1), 'pieces')
    print('SPINE openings: east', ne, 'west', nw, 'objects split; doorway decals clipped', nd)

_fe = BM.PATCHES['front-end-area']
BM.PATCHES['front-end-area'] = lambda w, l, o: (_fe(w, l, o), patch_front_end_spine(w, l, o))
BM.PATCHES['reactor-room'] = patch_reactor_assembly
BM.PATCHES['turbine-room'] = patch_turbine
BM.PATCHES['electrical-room'] = patch_electrical
BM.PATCHES['waste-storage'] = patch_waste
BM.PATCHES['condenser-bay'] = patch_condenser
BM.PATCHES['fuel-corridor'] = patch_fuel
BM.TURBINE_CUTS.clear(); BM.MEDICAL_CUTS.clear()

# ------------------------------------------------------------------------------------------------------------------------------------------------
# Condenser stair: turbine west door (plan x -4.25, y 26.95..28.95) -> top landing -> 34 risers down to z -6 -> corridor east under the turbine end -> condenser D01 stub.
# ------------------------------------------------------------------------------------------------------------------------------------------------
ST = dict(xw=-6.65, xe=-4.55, t=0.3, ytop=26.8, ybot=16.9, yn=29.25, risers=34, drop=6.0, roof=2.9,
          cy0=14.5, cy1=16.9, cx1=COND[0] + 1.24, cx0b=COND[0] - 1.24, vy=COND[1] - 2.56, ch=2.7)

def add_condenser_stair(root):
    import reactor_links as RL
    M, _ = BM.spawn_assets(); coll = bpy.data.collections.new('CONNECTOR_condenser_stair'); root.children.link(coll)
    s = ST; t = s['t']; z1 = -s['drop']; yd0, yd1 = TURB[1] + STAIR_DOOR_Y - 1.0, TURB[1] + STAIR_DOOR_Y + 1.0
    box = lambda n, xs, ys, zs, m: BM._box(coll, 'STAIR ' + n, xs, ys, zs, m)
    conc, wall, floor, steel, lamp, yellow, ceil = M['slab'], M['wall'], M['floor'], M['steel'], M['lamp'], M['yellow'], M['ceiling']
    tread = BM._mat('STAIR concrete', (0.36, 0.36, 0.34), 0.85)      # mid-grey: the spawn CS_slab_concrete (base 0.11) read as black on treads and wainscot
    # shaft: west wall full height, east wall (under and beside the turbine wall) with the door hole, north wall, roof over the shaft
    box('west wall', (s['xw'] - t, s['xw']), (s['cy0'] - t, s['yn'] + t), (z1 - 0.25, s['roof'] + 0.25), conc)
    box('east wall south', (s['xe'], s['xe'] + t), (s['ybot'], yd0), (z1 - 0.25, s['roof'] + 0.25), conc)
    box('east wall north', (s['xe'], s['xe'] + t), (yd1, s['yn'] + t), (z1 - 0.25, s['roof'] + 0.25), conc)
    box('east wall below door', (s['xe'], s['xe'] + t), (yd0, yd1), (z1 - 0.25, -0.34), conc)
    box('east wall above door', (s['xe'], s['xe'] + t), (yd0, yd1), (2.6, s['roof'] + 0.25), conc)
    box('north wall', (s['xw'] - t, s['xe'] + t), (s['yn'], s['yn'] + t), (-0.25, s['roof'] + 0.25), conc)
    box('roof', (s['xw'] - t, s['xe'] + t), (s['ybot'], s['yn'] + t), (s['roof'], s['roof'] + 0.25), conc)
    box('ceiling skin', (s['xw'], s['xe']), (s['ybot'], s['yn']), (s['roof'] - 0.04, s['roof']), ceil)
    box('plaster west', (s['xw'], s['xw'] + 0.04), (s['ybot'], s['yn']), (z1, s['roof'] - 0.04), wall)
    box('plaster east south', (s['xe'] - 0.04, s['xe']), (s['ybot'], yd0), (z1, s['roof'] - 0.04), wall)
    box('plaster east north', (s['xe'] - 0.04, s['xe']), (yd1, s['yn']), (z1, s['roof'] - 0.04), wall)
    box('plaster east below door', (s['xe'] - 0.04, s['xe']), (yd0, yd1), (z1, -0.25), wall)
    box('plaster east above door', (s['xe'] - 0.04, s['xe']), (yd0, yd1), (2.6, s['roof'] - 0.04), wall)
    box('top landing slab', (s['xw'], s['xe'] + t), (s['ytop'], s['yn']), (-0.25, -0.04), conc)
    box('top landing floor', (s['xw'], s['xe'] + t), (s['ytop'], s['yn']), (-0.04, 0.0), floor)
    # flight: solid steps (one block per tread, down to the shaft floor), nosing strips
    n = s['risers']; rise = s['drop'] / n; g = (s['ytop'] - s['ybot']) / (n - 1)
    for i in range(1, n):
        ya, yb = s['ytop'] - i * g, s['ytop'] - (i - 1) * g; zt = -i * rise
        box('step %02d' % i, (s['xw'], s['xe']), (ya, yb), (z1 - 0.25, zt), tread)
        box('nosing %02d' % i, (s['xw'] + 0.05, s['xe'] - 0.05), (yb - 0.05, yb), (zt - 0.005, zt + 0.004), yellow)
    # handrails on both walls, 0.9 m above the pitch line: one sloped bar each (an oriented box along the pitch), on three wall brackets
    for x in (s['xw'] + 0.09, s['xe'] - 0.09):
        p0 = Vector((x, s['ytop'] + 0.3, 0.9)); p1 = Vector((x, s['ybot'], z1 + 0.9)); d = (p1 - p0).normalized(); up = Vector((0, 0, 1)) - d * d.z; up.normalize(); sd = d.cross(up)
        bm = __import__('bmesh').new(); V = [bm.verts.new(p + sd * u * 0.025 + up * w * 0.025) for p in (p0, p1) for u in (-1, 1) for w in (-1, 1)]
        for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)): bm.faces.new([V[i] for i in f])
        __import__('bmesh').ops.recalc_face_normals(bm, faces=bm.faces); me = bpy.data.meshes.new('STAIR handrail'); bm.to_mesh(me); bm.free(); me.materials.append(steel)
        ob = bpy.data.objects.new('STAIR handrail', me); coll.objects.link(ob)
        for f in (0.1, 0.5, 0.9):
            q = p0.lerp(p1, f); wx = s['xw'] if x < (s['xw'] + s['xe']) / 2 else s['xe']
            BM._box(coll, 'STAIR handrail bracket', (min(wx, x), max(wx, x)), (q.y - 0.02, q.y + 0.02), (q.z - 0.08, q.z - 0.02), steel)
    # lower corridor: east under the turbine end (y 14.5..16.9), then north to the condenser D01 stub end (plan y 19.34)
    cx0, cx1 = s['xw'], s['cx1']; cy0, cy1 = s['cy0'], s['cy1']; zc = z1 + s['ch']
    box('corridor slab', (cx0 - t, cx1 + t), (cy0 - t, cy1), (z1 - 0.25, z1 - 0.04), conc)
    box('corridor floor', (cx0, cx1), (cy0, cy1), (z1 - 0.04, z1), floor)
    box('corridor north slab', (s['cx0b'] - t, cx1 + t), (cy1, s['vy']), (z1 - 0.25, z1 - 0.04), conc)
    box('corridor north floor', (s['cx0b'], cx1), (cy1, s['vy']), (z1 - 0.04, z1), floor)
    box('shaft floor', (s['xw'], s['xe']), (cy1, s['ybot'] + 0.01), (z1 - 0.04, z1), floor)
    box('corridor south wall', (cx0 - t, cx1 + t), (cy0 - t, cy0), (z1 - 0.25, zc + 0.25), conc)
    box('corridor east wall', (cx1, cx1 + t), (cy0, s['vy']), (z1 - 0.25, zc + 0.25), conc)
    box('corridor north wall', (s['xe'], s['cx0b']), (cy1, cy1 + t), (z1 - 0.25, zc + 0.25), conc)
    box('corridor west jamb', (s['cx0b'] - t, s['cx0b']), (cy1, s['vy']), (z1 - 0.25, zc + 0.25), conc)
    box('corridor roof', (s['xe'], cx1 + t), (cy0 - t, cy1 + t), (zc, zc + 0.25), conc)
    box('corridor north roof', (s['cx0b'] - t, cx1 + t), (cy1, s['vy']), (zc, zc + 0.25), conc)
    box('corridor ceiling', (s['xe'], cx1), (cy0, cy1), (zc - 0.04, zc), ceil)
    box('corridor north ceiling', (s['cx0b'], cx1), (cy1, s['vy']), (zc - 0.04, zc), ceil)
    box('corridor west lintel', (s['xw'] - t, s['xe']), (cy0 - t, cy1), (zc, zc + 0.25), conc)   # under the shaft: closes the shaft bottom south of the flight
    for nm, xs, ys in (('south', (cx0, cx1), (cy0, cy0 + 0.04)), ('east', (cx1 - 0.04, cx1), (cy0, s['vy'])), ('north', (s['xe'], s['cx0b']), (cy1 - 0.04, cy1)), ('jamb', (s['cx0b'], s['cx0b'] + 0.04), (cy1, s['vy']))):
        box('corridor plaster ' + nm, xs, ys, (z1, zc - 0.04), wall)
        box('corridor wainscot ' + nm, (xs[0] - 0.01, xs[1] + 0.01) if xs[1] - xs[0] < 0.1 else xs, (ys[0] - 0.01, ys[1] + 0.01) if ys[1] - ys[0] < 0.1 else ys, (z1, z1 + 1.15), tread)   # not the navy dado: it read as a black band
    # threshold strips and lights
    box('strip turbine door', (s['xe'] - 0.3, s['xe']), (yd0, yd1), (0.0, 0.012), yellow)
    box('strip condenser', (s['cx0b'], cx1), (s['vy'] - 0.35, s['vy'] - 0.05), (z1, z1 + 0.012), yellow)
    lights = [((s['xw'] + s['xe']) / 2, 28.0, s['roof'] - 0.12, 140), ((s['xw'] + s['xe']) / 2, 22.0, s['roof'] - 0.12, 260), ((s['xw'] + s['xe']) / 2, 18.0, -2.6, 160),
              (-3.0, 15.7, zc - 0.12, 70), (0.6, 15.7, zc - 0.12, 70), (COND[0], 18.2, zc - 0.12, 60)]     # corridor lights lowered from 110 W: 6.9 % clipped at the D01 view
    for i, (x, y, z, e) in enumerate(lights):
        ld = bpy.data.lights.new('STAIR light %d' % i, 'AREA'); ld.energy = e; ld.size = 1.4; ld.size_y = 0.4; ld.color = (1.0, 0.93, 0.82)
        lo = bpy.data.objects.new('STAIR light %d' % i, ld); lo.location = (x, y, z); coll.objects.link(lo)
        box('lamp %d' % i, (x - 0.7, x + 0.7), (y - 0.2, y + 0.2), (z + 0.06, z + 0.11), lamp)
    print('STAIR condenser: %d risers of %.3f m, going %.3f m, %.1f degrees; corridor %.1f m' % (n, rise, g, math.degrees(math.atan2(rise, g)), (cx1 - cx0) + (s['vy'] - cy1)))

# ------------------------------------------------------------------------------------------------------------------------------------------------
# Wayfinding over the new doors (plan frame, ivory emissive text like the concourse signs).
# ------------------------------------------------------------------------------------------------------------------------------------------------
def add_signs(root):
    coll = bpy.data.collections.new('CONNECTOR_signs'); root.children.link(coll)
    mat = BM._mat('ASSEMBLY sign paint', (0.9, 0.85, 0.7), 0.5, 0.0, 1.2)
    def sign(text, loc, rz, size=0.32):
        cu = bpy.data.curves.new('SIGN ' + text, 'FONT'); cu.body = text; cu.size = size; cu.align_x = 'CENTER'; cu.extrude = 0.01; cu.materials.append(mat)
        o = bpy.data.objects.new('SIGN ' + text, cu); o.location = loc; o.rotation_euler = (math.pi / 2, 0, rz); coll.objects.link(o)     # rz +90: text faces +x, -90: faces -x
    sign('WASTE STORAGE', (SPINE_E - 0.33, WASTE[1], 3.45), -math.pi / 2)            # spine east wall, inner face x 9.85, read from the spine (facing -x)
    sign('COMPLIANCE DOCK', (SPINE_E - 0.33, DOCK[1], 2.9), -math.pi / 2)
    sign('WASTE TRANSFER / FUEL', (SPINE_W + 0.33, S03_Y, 3.3), math.pi / 2)       # spine west wall, inner face x 6.15 (facing +x)
    sign('ELECTRICAL', (9.9, ELEC[1], 2.95), -math.pi / 2)                           # inside the turbine, over the east door
    sign('CONDENSER BAY', (-3.9, TURB[1] + STAIR_DOOR_Y, 2.85), math.pi / 2)       # inside the turbine, over the stair door
    sign('TURBINE HALL', (ELEC[0] + 0.5, ELEC[1], 3.0), math.pi / 2, 0.28)          # inside electrical, over D01
    # in the hall, a floor stencil in front of the spine blast door (the old one pointed at the east door, now a closed exit)
    paint = BM._mat('ASSEMBLY floor stencil yellow', (0.75, 0.55, 0.05), 0.6)
    cu = bpy.data.curves.new('SIGN floor REACTOR WASTE DOCK', 'FONT'); cu.body = 'REACTOR  WASTE  DOCK'; cu.size = 0.42; cu.align_x = 'CENTER'; cu.materials.append(paint)
    o = bpy.data.objects.new('SIGN floor REACTOR WASTE DOCK', cu); o.location = (8.0, -50.9, 0.006); coll.objects.link(o)
    print('SIGNS added')

# ------------------------------------------------------------------------------------------------------------------------------------------------
# Door table: every door between two places, or between a place and the outside, with its owner leaf and states. DOOR_<id> empties carry it for runtime binding.
# local: centre in the owning module's frame; out: outward normal in that frame; state: default when the map opens.
# ------------------------------------------------------------------------------------------------------------------------------------------------
DOORS = [
    # id, owner room, local centre, local outward, clear w, h, kind, default state, leads to, leaf note
    ('SPAWN_EXIT', 'front-end-area', (0, 0), (0, -1), 2.58, 2.6, 'airlock', 'open', 'spawn-room', 'front end airlock_leaf_L/R shown parked; spawn AIRLOCK_* leaves left out (DOOR_BINDINGS spawn_airlock)'),
    ('CAF_YARD', 'front-end-area', (-15.27, 10.0), (-1, 0), 3.0, 2.51, 'double sliding', 'open', 'yard', 'yard_leaf_N/S parked'),
    ('CAF_MEDICAL', 'medical-reanimation', (0, 0), (0, -1), 2.2, 2.5, 'opposed sliding pressure leaves', 'open', 'front-end-area (cafeteria)', 'MED_R2 pressure leaves parked; contract: open traversal default'),
    ('HALL_WEST', 'front-end-area', (-11.97, 26.0), (-1, 0), 2.32, 2.6, 'double leaf', 'open', 'refinery (colonnade)', 'hall_W_door_leaf_+-1.001 left out (closed-state asset)'),
    ('HALL_SPINE', 'front-end-area', (0, 31.5), (0, 1), 3.6, 3.2, 'blast door, sliding pair', 'open', 'spine', 'blast_leaf_+-1 parked'),
    ('HALL_EAST', 'front-end-area', (23.97, 26.0), (1, 0), 2.32, 2.6, 'double leaf', 'closed', 'outside (east trunk canopy)', 'hall_E_door_leaf_+-1.001 kept in the closed position'),
    ('MINE_PORTAL', 'mine', (-39.0, -29.0), (1, 0), 7.2, 3.9, 'portal (no leaf)', 'open', 'front-end-area (yard)', 'tunnel mouth (first timber set); front end portal_void and the portal cap faces left out'),
    ('YARD_SERVICE', 'front-end-area', (-54.0, 19.85), (0, 1), 2.4, 2.35, 'single leaf', 'closed', 'outside', 'service_door_leaf kept closed'),
    ('YARD_FREIGHT_GATE', 'front-end-area', (-30.2, 19.9), (0, 1), 3.1, 3.1, 'sliding gate', 'open', 'refinery freight door', 'freight_gate_leaf parked'),
    ('REFINERY_FUEL', 'fuel-corridor', (0, 0), (0, -1), 2.6, 3.0, 'opening (refinery Door_Reactor)', 'open', 'refinery', 'refinery REACTOR door: open frame'),
    ('FUEL_F02', 'fuel-corridor', (14.2, 24.0), (0, 1), 5.0, 5.0, 'opening', 'open', 'reactor concourse', 'own door 0.5 m inside, open'),
    ('FUEL_S01_PLANT', 'fuel-corridor', (-5.4, 17.4), (-1, 0), 2.0, 2.5, 'double leaf', 'closed', 'outside', 'FC | Plant service leaves (source state)'),
    ('FUEL_S02_CLEAN', 'fuel-corridor', (6.6, 21.0), (0, 1), 2.0, 2.5, 'double leaf', 'closed', 'outside', 'FC | Clean service leaves (source state)'),
    ('FUEL_S03_WASTE', 'fuel-corridor', (16.4, 16.0), (1, 0), 2.4, 3.0, 'double leaf', 'open', 'waste-transfer hall', 'FC | Waste transfer leaves left out (closed-state asset)'),
    ('REACTOR_S', 'reactor-room', (0, -12.2), (0, -1), 5.0, 5.0, 'opening (cut)', 'open', 'concourse', 'hall wall cut south_door'),
    ('REACTOR_N', 'reactor-room', (0, 14.4), (0, 1), 5.0, 5.0, 'stub double door', 'open', 'turbine-room D01', 'FUEL HANDLING.* door pieces left out (closed-state asset)'),
    ('REACTOR_W', 'reactor-room', (-14.4, 0), (-1, 0), 5.0, 5.0, 'stub double door', 'open', 'cooling-plant CP-P01', 'MAIN ACCESS.* door pieces left out (closed-state asset)'),
    ('REACTOR_SE', 'reactor-room', (11.0, -11.0), (0.7071, -0.7071), 5.0, 5.0, 'stub double door', 'closed', 'outside', 'COOLING PLANT.* door pieces kept (closed)'),
    ('TURBINE_D01', 'turbine-room', (0, 0), (0, -1), 2.4, 2.7, 'two opposed sliding leaves', 'open', 'reactor north stub', 'contract: parked in module pockets'),
    ('TURBINE_D02', 'turbine-room', (0, 24.0), (0, 1), 2.4, 2.7, 'two opposed sliding leaves', 'closed', 'outside', 'D02 electrical parked leaf pair moved shut (local copies)'),
    ('TURBINE_E_ELECTRICAL', 'turbine-room', (10.125, ELEC_DOOR_Y), (1, 0), 2.4, 2.7, 'opening (new cut) + electrical D01 leaves', 'open', 'electrical-room D01', 'leaves are electrical D01 (parked inside electrical)'),
    ('ELECTRICAL_D01', 'electrical-room', (0, 0), (0, -1), 2.4, 2.7, 'sliding pair', 'open', 'turbine-room (east door)', 'parked'),
    ('ELECTRICAL_D02', 'electrical-room', (0, 16.4), (0, 1), 2.4, 2.7, 'sliding pair', 'closed', 'outside', 'leaves moved shut (local copies)'),
    ('TURBINE_W_STAIR', 'turbine-room', (-4.125, STAIR_DOOR_Y), (-1, 0), 2.0, 2.6, 'opening (new cut)', 'open', 'condenser stair', 'no leaf'),
    ('CONDENSER_D01', 'condenser-bay', (0, 0), (0, -1), 2.0, 2.4, 'two opposed sliding leaves', 'open', 'condenser stair corridor', 'parked open (contract); stub blanking left out'),
    ('COOLING_P01', 'cooling-plant', (0, 0), (0, -1), 5.0, 5.0, 'overhead folding shutter', 'open', 'reactor west stub', 'raised (contract: fixed open)'),
    ('WASTE_RECEIVING', 'waste-storage', (0, 0), (0, -1), 3.0, 3.2, 'rolling shutter', 'open', 'spine (east door)', 'rolled up (contract: parked fully open)'),
    ('WASTE_PERSONNEL', 'waste-storage', (6.16, 2.4), (1, 0), 1.2, 2.3, 'hinged leaf, outward', 'closed', 'outside (gap to the dock wall)', 'leaf turned into the frame (local copies)'),
    ('WASTE_DISPATCH', 'waste-storage', (0, 18.0), (0, 1), 2.4, 2.8, 'rolling shutter', 'closed', 'outside', 'new curtain'),
    ('DOCK_P1', 'compliance-dock', (0, -1.0), (0, -1), 2.4, 2.6, 'sliding (X) in perimeter wall', 'open', 'spine (east door)', 'P1 deep back wall and leaf left out'),
    ('DOCK_P2', 'compliance-dock', (0, 15.8), (0, 1), 4.6, 3.5, 'opposed sliding blast leaves', 'closed', 'outside (arrival)', 'contract default sealed'),
    ('SPINE_NORTH_END', 'front-end-area', (0, 65.45), (0, 1), 3.3, 3.3, 'single leaf', 'closed', 'outside (the concourse is entered through the spine west wall)', 'reactor_door kept closed'),
    ('SPINE_E_WASTE', 'front-end-area', (2.0, fe(WASTE[1])), (1, 0), 3.1, 3.2, 'opening (new cut)', 'open', 'waste-storage', 'no leaf (waste receiving shutter is the door)'),
    ('SPINE_E_DOCK', 'front-end-area', (2.0, fe(DOCK[1])), (1, 0), 2.6, 2.6, 'opening (new cut)', 'open', 'compliance-dock', 'no leaf (dock P1 is the door)'),
    ('SPINE_W_TRANSFER', 'front-end-area', (-2.0, fe(S03_Y)), (-1, 0), 2.4, 3.0, 'opening (new cut)', 'open', 'waste-transfer hall', 'no leaf (fuel S03 is the door)'),
]
STATE_ANCHORS = {'closed': 'blocks: collider DOOR_<id>_blocker enabled', 'open': 'passes: blocker disabled', 'locked': 'closed and refuses interaction'}

def add_door_anchors(root):
    coll = bpy.data.collections.new('DOORS'); root.children.link(coll)
    place = {r[0]: (r[3], r[4]) for r in BM.ROOMS}; rows = []
    for did, room, c, n, w, h, kind, state, to, leaf in DOORS:
        loc, rz = place[room]; p = wxy(loc, rz, *c); d = Vector(rot(rz)(*n)).normalized()
        e = bpy.data.objects.new('DOOR_' + did, None); e.empty_display_type = 'ARROWS'; e.empty_display_size = 0.6
        e.location = (p.x, p.y, loc[2]); e.rotation_euler = (0, 0, math.atan2(d.y, d.x)); coll.objects.link(e)
        for k, v in (('door_id', did), ('owner_room', room), ('kind', kind), ('state_default', state), ('states', 'open,closed,locked'), ('leads_to', to),
                     ('clear_width_m', w), ('clear_height_m', h), ('leaf', leaf)): e[k] = v
        rows.append(dict(id=did, owner=room, plan=[round(p.x, 3), round(p.y, 3), loc[2]], outward=[round(d.x, 4), round(d.y, 4)], clear_w=w, clear_h=h, kind=kind, state=state, leads_to=to, leaf=leaf))
    os.makedirs(os.path.join(HERE, 'validation'), exist_ok=True)
    json.dump(dict(note='Door table of the compact map, assembly pass. Unreviewed. Runtime states: ' + json.dumps(STATE_ANCHORS), closed_copies=CLOSED, doors=rows),
              open(os.path.join(HERE, 'validation', 'doors.json'), 'w'), indent=1)
    print('DOORS', len(rows), 'anchors')

# ------------------------------------------------------------------------------------------------------------------------------------------------
# Local lighting overrides (filled in from the junction measurements in ASSEMBLY_REPORT.md; source rooms are not edited).
# ------------------------------------------------------------------------------------------------------------------------------------------------
FILL_LIGHTS = []      # (name, (x, y, z), energy W, size m, colour)

def add_fill_lights(root):
    if not FILL_LIGHTS: return
    coll = bpy.data.collections.new('LIGHT_junction_fill'); root.children.link(coll)
    for name, loc, e, size, col in FILL_LIGHTS:
        ld = bpy.data.lights.new('FILL ' + name, 'AREA'); ld.energy = e; ld.size = size; ld.color = col
        lo = bpy.data.objects.new('FILL ' + name, ld); lo.location = loc; coll.objects.link(lo)
    print('FILL lights', len(FILL_LIGHTS))

EMISSION_OVERRIDES = {'HALL accent waste-storage': 0.4, 'HALL accent dim waste-storage': 0.2}   # transfer hall: 17.8 % clipped pixels at 7.0 / 2.6 (measured); local materials only
HALL_LIGHT_SCALE = {'CONNECTOR_reactor_to_waste-transfer': 0.35}                                   # its dress_hall lights are sized for 5 m halls; this one is 2.4 x 3.0 m

def post_build():
    root = bpy.context.scene.collection.children['COMBINED_MAP']
    for name, strength in EMISSION_OVERRIDES.items():
        m = bpy.data.materials.get(name)
        if m and m.node_tree:
            for n in m.node_tree.nodes:
                if n.type == 'BSDF_PRINCIPLED': n.inputs['Emission Strength'].default_value = strength
            print('EMISSION override', name, strength)
    lp = bpy.data.materials.get('HALL lamp panel')        # the transfer hall's lamp panels get a dimmer copy (the concourse and stair keep the shared one)
    c = bpy.data.collections.get('CONNECTOR_reactor_to_waste-transfer')
    if lp and c:
        dim = lp.copy(); dim.name = 'HALL lamp panel dim'; dim.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 1.4
        for o in c.all_objects:
            if o.type == 'MESH':
                for i, m in enumerate(o.data.materials):
                    if m == lp: o.data.materials[i] = dim
    for cname, k in HALL_LIGHT_SCALE.items():
        c = bpy.data.collections.get(cname)
        if c:
            for o in c.all_objects:
                if o.type == 'LIGHT': o.data.energy *= k
            print('LIGHT scale', cname, k)
    add_condenser_stair(root); add_signs(root); add_fill_lights(root); add_door_anchors(root)
    try:
        import assembly_colliders; assembly_colliders.build(root, sys.modules[__name__])
    except ImportError: print('COLLIDERS module not found')

BM.add_door_placeholders = post_build

if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    out = a[a.index('--output') + 1] if '--output' in a else os.path.join(HERE, 'combined_map.blend')
    BM.build('compliance-dock', out)
