"""Compact map, assembly pass (2026-10-12/13): THE main layout. Run:

    blender --background --factory-startup --python build_compact_map.py -- [--output combined_map.blend]

Owner instructions: "the map should be as compact as possible", then (for this pass) "Ignore all previous specs and planning docs - build and decide what comes where
on your own with the goal of the most compact and logical map possible. Move around, rotate, transform, structural changes etc are all allowed."
Everything here is unreviewed and not accepted. It imports `build_combined_map.py` (the shared machinery, not edited) and overrides the room placements,
the hall list and the per-room patches. Rooms are still linked, never edited: every change is a local copy made below. Record: COMPACT_MAP.md, ASSEMBLY_REPORT.md.

Layout ("street" layout, short fuel corridor; 2026-10-13). The front block (front end, spawn, mine, refinery, medical) keeps its placement: the yard rail fixes the
refinery and the refinery fuel door fixes the fuel corridor. The fuel corridor is the SHORT corridor S1 (sections/fuel-corridor/blender/build_short_corridor.py: F23ci
with its north half removed and its waste-transfer door moved to the east wall as the reactor door F02E; owner: "yes do the rebuild to the same graphical fidelity").
Its east door sets the concourse, and the concourse sets the reactor, which moves RY = -18.7 m south (0.47 m clear of the corridor's new north wall). The rest moves with it:
  * turbine on the reactor north stub, condenser bay under it, reached by a new stair from a door in the turbine's west wall;
  * electrical on the turbine's east flank, through a new 2.4 m door between two wall columns (turbine-local y 18.5);
  * waste on the reactor's east wall, through a new 2.84 m opening cut in the wall's patch panel (the reactor had a 4 m panel there);
  * the compliance dock on the spine's east wall; the front end's spine is shortened to 14.8 m (its end door moved with the reactor, the bays between left out);
  * the concourse joins the corridor's F02E door, the shortened spine and the reactor south door; cooling stays on the reactor west stub.
Doors that now open onto nothing are closed with their own leaves (local copies moved to the closed position) or, where the module has none (waste dispatch roller
shutter), a new curtain. Dropped against the first assembly pass: the S03 transfer hall and the spine's waste door (and earlier the 7 m diagonal waste hall, the 3.9 m
waste-to-spine hall and the three PLACEHOLDER plates)."""
import bpy, sys, os, math, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_combined_map as BM, reactor_links as R
from mathutils import Vector, Matrix

# ------------------------------------------------------------------------------------------------------------------------------------------------
# Placements (plan metres, rotation about z in degrees). Every number below is a measured module face; see COMPACT_MAP.md "Assembly pass".
# ------------------------------------------------------------------------------------------------------------------------------------------------
SPINE_E = 10.15          # spine east wall outer face (front-end spine_wall_1, local x 1.85..2.15, plan = local + (8, -80))
SPINE_W = 5.85           # spine west wall outer face (spine_wall_-1)
FUEL = (-22.2, -43.6, 0.0)                       # short corridor F01 on the refinery fuel door (unchanged placement); module bounds x -2.54..16.74, y 0..12.83
F02E = (FUEL[0] + 16.74, FUEL[1] + 6.98)         # corridor reactor door F02E: east outer face, plan (-5.46, -36.62), 2.38 x 3.0 clear (module_short_S1.blend.json)
RY = -18.7               # reactor centre, plan y: the concourse (reactor y - 19.6 .. - 14.8) holds F02E, and the reactor's south wall (y RY - 11.6) clears the corridor's north wall (plan -30.77) by 0.47 m
REACTOR = (0.0, RY, 0.0)
TURB = (0.0, RY + 14.5, 0.0)  # turbine end wall face (module y 0) on the reactor north stub end (reactor-local y 14.5)
COND = (TURB[0] + 1.6, TURB[1] + 7.4, -6.0)       # condenser bay under the turbine (its CONNECTIONS.md: turbine = local + (1.6, 7.4, -6.0))
ELEC_DOOR_Y = 18.5       # turbine-local y of the new east door: clear bay between wall columns at y 16 and 21 (feet +-0.32) and past the condensate return (ends y 16.8)
ELEC = (10.25 + 0.25, TURB[1] + ELEC_DOOR_Y, 0.0) # electrical D01 exterior face (module y -0.25) on the turbine east wall outer face (module x 10.25); rotation -90: D01 faces west
WASTE_HOLE = (2.44, 5.28, 3.2)                    # reactor-local y range and head of the east opening: inside the 4 m patch panel (y 1.6..5.6), clear of the lockers (to y 2.42) and the column plinth (from 5.29)
WASTE = (11.62 + 0.32, RY + (WASTE_HOLE[0] + WASTE_HOLE[1]) / 2, 0.0)   # waste WS_RECEIVING exterior face (module y -0.32) on the reactor's east outer face (x 11.6, plan cut); rotation -90: receiving faces west
DOCK = (SPINE_E + 2.0, -40.39, 0.0)              # dock P1 corridor (module y -2.0..0, back wall omitted) starts on the spine east face; rotation -90, P2 faces east (outside)
COOL = (-14.5, RY, 0.0)                          # cooling CP-P01 on the reactor west stub end
COOL_EXIT_Y = (-17.8, -16.2)  # plan y of the cooling plant's new rear-wall emergency door (1.6 x 2.35 m; rear wall clear between the maintenance alcove (y -20.3) and the north wall)
STAIR_DOOR_Y = 13.45     # turbine-local y of the condenser stair door (west wall): bay between columns at y 11 and 16, clear of the power conduit (ends y 12.4), 2.0 m wide
# reactor south concourse (plan): the corridor's east face to the spine's west inner face; same depth and height as build_combined_map.CONC, moved with the reactor
CONC = {'x0': F02E[0], 'x1': 6.15, 'y0': RY - 19.6, 'y1': RY - 14.8, 'wall': 0.3, 'roof': 5.9, 'slab': 0.25}
FE_LOC = (8.0, -80.0)    # front-end placement
SPINE_END_L = 65.45 + RY # front-end local y of the spine's end door after the shortening (the door, its frame, the last rib, beam and lamp move by RY)
SPINE_END = FE_LOC[1] + SPINE_END_L               # plan y -33.25
def rot(rz): c, s = math.cos(math.radians(rz)), math.sin(math.radians(rz)); return lambda x, y: (c * x - s * y, s * x + c * y)
def wxy(loc, rz, x, y): r = rot(rz)(x, y); return Vector((loc[0] + r[0], loc[1] + r[1]))

old = {r[0]: r for r in BM.ROOMS}
NEW = [old[k] for k in ('front-end-area', 'spawn-room', 'mine', 'refinery', 'medical-reanimation')]
NEW += [
    ('fuel-corridor', 'fuel-corridor/module_short_S1.blend', 'MODULE_fuel-corridor', FUEL, 0.0,
     'SHORT corridor S1 (2026-10-13, unreviewed): F23ci (reviewed 99) with its north half removed (bypass, plant header and S01, S02, delivery bay, F02 adapter) and the S03 '
     'waste-transfer door moved to the east wall as the reactor door F02E (module (16.74, 6.98), outward +X, 2.38 x 3.0). Built by sections/fuel-corridor/blender/build_short_corridor.py. '
     'F01 on the refinery north fuel door as before: x -22.2 (door centre), y -43.6 (refinery outer sill).'),
    ('reactor-room', BM.REACTOR_LIB, BM.REACTOR_COLLECTIONS, REACTOR, 0.0,
     'Candidate A (the refined hall), no rotation, moved to plan y %.1f so its south door meets the concourse in front of the short corridor. New local cuts: south door '
     '(reactor_links), east waste opening through the patch panel.' % RY),
    ('turbine-room', 'turbine-room/module_overhaul_R1.blend', 'MODULE_turbine-room', TURB, 0.0,
     'AAA finish (owner accepted 2026-10-12, unreviewed). End wall face (module y 0.0) on the reactor north stub end (reactor-local y 14.5). New local cuts: east door (electrical) and west door (condenser stair).'),
    ('electrical-room', 'electrical-room/overhaul/checkpoints/full-R11.blend', 'MODULE_electrical-room', ELEC, -90.0,
     'ASSEMBLY: on the turbine east flank. D01 exterior face (module y -0.25) on the turbine east wall outer face (module x 10.25) at turbine-local y 18.5; rotation -90 turns D01 to face west. D02 closed (no neighbour).'),
    ('condenser-bay', 'condenser-bay/module_aaa_A1.blend', 'MODULE_condenser-bay', COND, 0.0,
     'Under the turbine, origin at turbine (1.6, 7.4, -6.0) (its CONNECTIONS.md). D01 stub blanking removed locally; reached by the new condenser stair.'),
    ('waste-storage', 'waste-storage/module_aaa_A1.blend', 'MODULE_waste-storage', WASTE, -90.0,
     'ASSEMBLY: on the reactor east wall. WS_RECEIVING exterior face (module y -0.32) on the reactor east outer face (reactor-local x 11.6) at reactor-local y %.2f; rotation -90 turns receiving west. '
     'Personnel and dispatch doors closed.' % (WASTE[1] - RY)),
    ('cooling-plant', 'cooling-plant/module_aaa_A1.blend', 'MODULE_cooling-plant', COOL, 90.0,
     'CP-P01 on the reactor W stub end (reactor-local (-14.5, 0)); rotation +90 sends inward +Y to plan -X (unchanged).'),
    ('compliance-dock', 'compliance-dock/module_overhaul_R1.blend', ['MODULE_compliance-dock', '09 Overhaul | full'], DOCK, -90.0,
     'ASSEMBLY: on the spine east wall. P1 corridor start (module y -2.0) on the spine east face; rotation -90 turns P1 west and the sealed arrival P2 east, to the outside.'),
]
BM.ROOMS = NEW

# ------------------------------------------------------------------------------------------------------------------------------------------------
# Halls: none. The south concourse is built below (add_concourse) instead of build_combined_map.add_reactor_concourse.
# ------------------------------------------------------------------------------------------------------------------------------------------------
BM.LINKS.clear()
BM.CONC = CONC

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
LEAF_NAMES = {}  # door id -> names of the closed-leaf local copies (the evacuation walk test opens them)

def local_copy(wrap, omit, o, M, tag):
    """A local copy of linked object o (same mesh data, modifiers kept) with module-frame matrix M @ wm(o); the original is left out of the membership."""
    n = o.copy(); n.parent = None; n.matrix_basis = M @ BM.wm(o); n.name = o.name + tag
    wrap.objects.link(n); omit.add(o.name); return n

def bbox(o):
    """Module-frame box. Local meshes made by this script are measured from their vertices (their bound_box is not computed before the depsgraph runs)."""
    m = BM.wm(o)
    if o.library is None and o.type == 'MESH' and len(o.data.vertices):
        import numpy as np
        co = np.empty(len(o.data.vertices) * 3, np.float32); o.data.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        M = np.array(m, np.float32); w = co @ M[:3, :3].T + M[:3, 3]
        return Vector(w.min(0).tolist()), Vector(w.max(0).tolist())
    q = [m @ Vector(c) for c in o.bound_box]
    return Vector([min(p[i] for p in q) for i in range(3)]), Vector([max(p[i] for p in q) for i in range(3)])

def _part_layer(bm):
    """Tag every vertex with its loose part (union-find over edges); returns the layer and {part: (lo, hi)}."""
    bm.verts.index_update(); par = list(range(len(bm.verts)))
    def find(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    for e in bm.edges:
        a, b = find(e.verts[0].index), find(e.verts[1].index)
        if a != b: par[a] = b
    old = bm.verts.layers.int.get('_split_part')
    if old is not None: bm.verts.layers.int.remove(old)
    lay = bm.verts.layers.int.new('_split_part'); B = {}
    for v in bm.verts:
        p = find(v.index); v[lay] = p; c = v.co
        if p in B:
            lo, hi = B[p]
            for i in range(3): lo[i] = min(lo[i], c[i]); hi[i] = max(hi[i], c[i])
        else: B[p] = ([c.x, c.y, c.z], [c.x, c.y, c.z])
    return lay, B

def split_openings(wrap, omit, objs, along, band, holes, tag=' cut'):
    """Open doorways (a0, a1 along `along`, below ztop) in a wall band (module frame, axis 1 - along) by splitting meshes, not by deleting faces.
    Only the loose parts of a mesh that reach into a hole are cut, and only inside the band: they are split by bisect planes into the parts outside the band and,
    inside it, the parts beside each hole and a lintel above it. Closed parts get their cuts capped (solid jambs); open ones (decals, skins) are clipped only.
    Every other loose part of the mesh is kept whole (merged room-wide meshes are not touched away from the doorway). Small parts wholly inside a hole go;
    text and curves go when their centre is inside a hole. The pieces keep the source mesh's materials and the source object's transform. Returns the number of objects replaced."""
    import bmesh
    nrm = 1 - along; done = 0
    def drop(o):
        if o.library is None:
            if any(x is o for x in wrap.objects): wrap.objects.unlink(o)
        else: omit.add(o.name)
    def meets(lo, hi, h): return hi[nrm] > band[0] and lo[nrm] < band[1] and hi[along] > h[0] + 1e-4 and lo[along] < h[1] - 1e-4 and lo[2] < h[2] and hi[2] > 0.02
    for o in objs:
        if (o.library is not None and o.name in omit) or o.type not in ('MESH', 'CURVE', 'FONT'): continue      # local copies may share an omitted linked name
        lo, hi = bbox(o)
        if not any(meets(lo, hi, h) for h in holes): continue
        if o.type != 'MESH':
            c = (lo + hi) / 2
            if band[0] <= c[nrm] <= band[1] and any(h[0] <= c[along] <= h[1] and c.z <= h[2] for h in holes): drop(o); done += 1
            continue
        M = BM.wm(o); base = o.data.copy(); base.transform(M)
        bm = bmesh.new(); bm.from_mesh(base); lay, B = _part_layer(bm)
        hit = {p for p, (l, h_) in B.items() if any(meets(l, h_, hh) for hh in holes)}
        if not hit: bm.free(); bpy.data.meshes.remove(base); continue
        gone = {p for p in hit if any(h[0] - 0.01 <= B[p][0][along] and B[p][1][along] <= h[1] + 0.01 and band[0] - 0.01 <= B[p][0][nrm] and B[p][1][nrm] <= band[1] + 0.01
                                      and B[p][1][2] <= h[2] + 0.3 and B[p][1][along] - B[p][0][along] < 0.6 for h in holes)}
        def sub(parts):
            b2 = bm.copy(); l2 = b2.verts.layers.int['_split_part']
            bmesh.ops.delete(b2, geom=[v for v in b2.verts if v[l2] not in parts], context='VERTS'); return b2
        pieces = []
        rest = set(B) - hit
        if rest: pieces.append(sub(rest))
        cut = hit - gone
        if cut:
            hb = sub(cut); closed = not any(e.is_boundary for e in hb.edges)
        if cut:
            l2 = [min(v.co[i] for v in hb.verts) for i in range(3)]; h2 = [max(v.co[i] for v in hb.verts) for i in range(3)]
            hs = sorted(h for h in holes if meets(l2, h2, h))
            def piece(planes):
                b3 = hb.copy()
                for ax, v, below in planes:
                    co = [0.0, 0.0, 0.0]; co[ax] = v; no = [0.0, 0.0, 0.0]; no[ax] = 1.0
                    bmesh.ops.bisect_plane(b3, geom=b3.verts[:] + b3.edges[:] + b3.faces[:], plane_co=co, plane_no=no, clear_outer=below, clear_inner=not below)
                if not b3.faces: b3.free(); return
                if closed:
                    edges = [e for e in b3.edges if e.is_boundary]
                    if edges: bmesh.ops.holes_fill(b3, edges=edges, sides=0)
                pieces.append(b3)
            piece([(nrm, band[0], True)]); piece([(nrm, band[1], False)])
            inb = [(nrm, band[0], False), (nrm, band[1], True)]; prev = None
            for a, b, zt in hs:
                piece(inb + ([(along, prev, False)] if prev is not None else []) + [(along, a, True)]); prev = b
            piece(inb + [(along, prev, False)])
            for a, b, zt in hs: piece(inb + [(along, a, False), (along, b, True), (2, zt, False)])
            hb.free()
        bm.free()
        for k, b3 in enumerate(pieces):
            b3.verts.layers.int.remove(b3.verts.layers.int['_split_part'])
            me = base.copy(); me.name = o.name + tag; b3.to_mesh(me); b3.free()        # a copy of the source mesh keeps its material slots
            me.transform(M.inverted_safe())                                            # back into the source object's own frame: Object texture coordinates stay as they were
            n = o.copy(); n.data = me; n.parent = None; n.matrix_basis = M; n.name = o.name + tag + str(k)
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
        me = base.copy(); me.name = o.name + ' holed'; bm.to_mesh(me); bm.free(); me.transform(BM.wm(o).inverted_safe())
        c = o.copy(); c.data = me; c.parent = None; c.matrix_basis = BM.wm(o); c.name = o.name + ' piece %d' % k; wrap.objects.link(c); n += 1
    bpy.data.meshes.remove(base); omit.add(o.name); return n

def clip_mesh(wrap, omit, o, axis, value, keep_below=True, tag=' clipped'):
    """Replace a mesh by a local copy cut at one plane (module frame), the far side removed and, for a closed mesh, the cut capped."""
    import bmesh
    base = o.data.copy(); base.transform(BM.wm(o)); bm = bmesh.new(); bm.from_mesh(base); closed = not any(e.is_boundary for e in bm.edges)
    co = [0.0, 0.0, 0.0]; co[axis] = value; no = [0.0, 0.0, 0.0]; no[axis] = 1.0
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=co, plane_no=no, clear_outer=keep_below, clear_inner=not keep_below)
    if closed:
        edges = [e for e in bm.edges if e.is_boundary]
        if edges: bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    base.name = o.name + tag; bm.to_mesh(base); bm.free(); M = BM.wm(o); base.transform(M.inverted_safe())
    n = o.copy(); n.data = base; n.parent = None; n.matrix_basis = M; n.name = o.name + tag
    wrap.objects.link(n); omit.add(o.name); return n

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
        LEAF_NAMES.setdefault(door, []).append(local_copy(wrap, omit, o, Matrix.Translation((d, 0, 0)), ' closed').name); n += 1
    CLOSED.append((room, door, n, 'sliding leaves moved %.2f m to the closed position' % shift)); print('CLOSED', room, door, n, 'objects')

def relabel(wrap, lib_coll, omit, name, body):
    """A door label whose text is wrong in this layout: a local copy with its own copy of the text data (font, size, material and place kept), new text."""
    o = next((x for x in lib_coll.all_objects if x.name == name and x.type == 'FONT'), None)
    if o is None: print('RELABEL missing', name); return
    n = local_copy(wrap, omit, o, Matrix.Identity(4), ' relabelled'); n.data = o.data.copy(); n.data.body = body; print('RELABEL', name, '->', body)

def patch_turbine(wrap, lib_coll, omit):
    objs = list(dict.fromkeys(lib_coll.all_objects))
    # east wall, electrical door 2.4 x 2.7 m (like D01/D02) between the wall columns at y 16 and 21; west wall, condenser stair door 2.0 x 2.6 m between y 11 and 16
    ne = split_openings(wrap, omit, objs, 1, (9.85, 10.35), [(ELEC_DOOR_Y - 1.2, ELEC_DOOR_Y + 1.2, 2.7)])
    nw = split_openings(wrap, omit, objs, 1, (-4.35, -3.85), [(STAIR_DOOR_Y - 1.0, STAIR_DOOR_Y + 1.0, 2.6)])
    print('TURBINE doors cut: east', ne, 'west', nw, 'objects split')
    # D02 (north end) now opens onto the outside: its two parked leaves (module x +-1.39..2.57, y 23.87..23.98) and their fittings slide shut
    close_sliding_pair(wrap, lib_coll, omit, 'turbine-room', 'TURBINE_D02', 23.80, 24.00, 1.30, 2.66, 1.37)
    relabel(wrap, lib_coll, omit, 'D02 electrical direction', 'EXIT / D02')          # its sign said ELECTRICAL / D02; D02 is the emergency exit now (electrical is on the east door)

def patch_electrical(wrap, lib_coll, omit):
    # D02 (module y 16.4) faces east onto the outside now: leaves parked at |x| 1.24..2.45, y 16.03..16.11 slide shut
    close_sliding_pair(wrap, lib_coll, omit, 'electrical-room', 'ELECTRICAL_D02', 16.00, 16.12, 1.22, 2.50, 1.25)
    relabel(wrap, lib_coll, omit, 'Engraved WASTE / D02', 'EXIT / D02')                 # D02 was planned to lead to waste; it is the emergency exit to the east road now

WASTE_LEAF = ('Personnel leaf', 'Personnel kick plate', 'Personnel panic bar', 'Panic bar bracket', 'Recessed engraved plate.017', 'Engraved WS_PERSONNEL')

def patch_waste(wrap, lib_coll, omit):
    # personnel door: the outward leaf (hinge (6.345, 3.065), shown swung open 90 degrees) is turned back into the opening; it faces the dock's wall now
    hinge = Vector((6.345, 3.065, 0.0)); M = Matrix.Translation(hinge) @ Matrix.Rotation(math.radians(-90), 4, 'Z') @ Matrix.Translation(-hinge); n = 0
    for o in list(lib_coll.all_objects):
        if o.name.startswith(WASTE_LEAF) and o.name not in omit: LEAF_NAMES.setdefault('WASTE_PERSONNEL', []).append(local_copy(wrap, omit, o, M, ' closed').name); n += 1
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

def patch_cooling(wrap, lib_coll, omit):
    # rear wall (module y 13.0..13.3, outer bounds to 13.3): a 1.6 x 2.35 m emergency door; module x = plan y - RY (rotation +90). evacuation.py adds the leaf, frames and threshold
    a0, a1 = COOL_EXIT_Y[0] - RY, COOL_EXIT_Y[1] - RY
    print('COOLING rear emergency door cut:', split_openings(wrap, omit, list(dict.fromkeys(lib_coll.all_objects)), 0, (12.8, 13.7), [(a0, a1, 2.4)]), 'objects split')

def patch_fuel(wrap, lib_coll, omit):
    n = 0
    for o in lib_coll.all_objects:
        # the reactor door F02E (the moved S03 leaves) and the refinery boundary F01 are closed in the source; the freight route needs them open
        if o.name.startswith(('FC | Reactor transfer', 'FC | Refinery boundary')) and ('leaf' in o.name or 'wear' in o.name): omit.add(o.name); n += 1
    print('FUEL F01 and F02E leaves left out', n)

def _reactor_objs(omit, wrap):
    objs = [o for c in bpy.data.collections if c.library and os.path.basename(c.library.filepath) == os.path.basename(BM.REACTOR_LIB) for o in c.all_objects if o.name not in omit]
    return list(dict.fromkeys(objs + [o for o in wrap.objects if o.library is None]))

def patch_reactor_assembly(wrap, lib_coll, omit):
    BM.patch_reactor(wrap, lib_coll, omit)
    n = 0
    for c in bpy.data.collections:
        if c.library and os.path.basename(c.library.filepath) == os.path.basename(BM.REACTOR_LIB):
            for o in c.all_objects:
                if (o.name.startswith(('FUEL HANDLING.', 'MAIN ACCESS.')) and 'door' in o.name.lower()) or o.name.startswith(('RH refine door hardware FUEL', 'RH refine door hardware MAIN')): omit.add(o.name); n += 1
    print('REACTOR N and W stub doors and their leaf hardware left out', n, '(the SE stub door stays closed)')
    # the south door cut (reactor_links.HALL_CUTS south_door) keeps 'RH walls trim YELLOW' whole: a 0.5 m high trim bar stayed across the doorway (walk test). Split it and anything else left in the opening
    print('REACTOR south doorway cleared:', split_openings(wrap, omit, _reactor_objs(omit, wrap), 0, (-12.3, -9.95), [(-2.5, 2.5, 5.0)]), 'objects split')
    # east wall: the waste receiving opening, 2.84 x 3.2 m, through every wall layer (panels x 10.8, patch panel 10.8..11.08, wall mass to 11.6) the wall-base plinth (from x 10.3) and the floor bollard in front of the panel (x 9.9).
    # The patch panel (`East wall patch door`, y 1.6..5.6, z 0..5) is split with it and stays as the jambs and head; the bollard and posters inside the opening go.
    a0, a1, zt = WASTE_HOLE
    print('REACTOR east waste opening:', split_openings(wrap, omit, _reactor_objs(omit, wrap), 1, (9.85, 11.7), [(a0, a1, zt)]), 'objects split')
    # threshold through the wall depth (the hall floor ends at x 10.8, the waste receiving exterior face is x 11.62), in the hall's own floor material, with a hazard strip
    mats = {m.name: m for m in bpy.data.materials if m.library and os.path.basename(m.library.filepath) == os.path.basename(BM.REACTOR_LIB)}
    floor = mats.get('RH floor wet concrete') or BM._mat('ASSEMBLY reactor threshold', (0.3, 0.3, 0.29), 0.8)
    BM._box(wrap, 'ASSEMBLY reactor east threshold', (10.78, 11.64), (a0, a1), (-0.3, 0.0), floor)
    BM._box(wrap, 'ASSEMBLY reactor east threshold strip', (10.45, 10.75), (a0 + 0.05, a1 - 0.05), (0.0, 0.006), mats.get('RH hazard stripes') or BM._mat('ASSEMBLY hazard', (0.75, 0.55, 0.05), 0.6))

def fe(y): return y - FE_LOC[1]        # plan y -> front-end local y

def fold_spine(wrap, lib_coll, omit):
    """Shorten the spine (front-end local frame, x +-2.15, y 32.0..65.6, 3.5 m bays) to end at SPINE_END_L: the end door, its frame and the last bay's rib, beam and lamp
    (local y >= 64.3) move by RY as local copies; the bays between are left out; the long pieces (walls, dado, floor, roof, route line) are clipped 0.15 m past the new door plane."""
    moved = dropped = clipped = 0; cut = SPINE_END_L + 0.15
    for o in list(dict.fromkeys(lib_coll.all_objects)):
        if o.name in omit or o.type not in ('MESH', 'CURVE', 'FONT'): continue
        lo, hi = bbox(o)
        if lo.x < -2.7 or hi.x > 2.7 or lo.y < 31.9: continue
        if lo.y >= 64.3: local_copy(wrap, omit, o, Matrix.Translation((0.0, RY, 0.0)), ' moved'); moved += 1
        elif hi.y <= SPINE_END_L: continue
        elif lo.y >= SPINE_END_L - 0.3: omit.add(o.name); dropped += 1
        else: clip_mesh(wrap, omit, o, 1, cut); clipped += 1
    print('SPINE shortened by %.2f m: %d moved, %d left out, %d clipped at local y %.2f' % (-RY, moved, dropped, clipped, cut))
    # the end door was a leaf on a solid frame panel (reactor_door_frame: 4.0 x 0.25 x 3.6 m, no opening behind the leaf; found by the evacuation walk test).
    # It is an emergency exit now, so the panel gets the leaf's 3.3 x 3.3 m opening; the leaf (reactor_door) closes it
    fr = [o for o in wrap.objects if o.library is None and o.name.startswith('reactor_door_frame')]
    print('SPINE end door opening cut through its frame panel:', split_openings(wrap, omit, fr, 0, (SPINE_END_L - 0.1, SPINE_END_L + 0.4), [(-1.65, 1.65, 3.3)]), 'objects')

def patch_front_end_spine(wrap, lib_coll, omit):
    """The spine shortened, then two openings in its walls (front-end local frame): the concourse on the west wall, dock P1 on the east wall."""
    fold_spine(wrap, lib_coll, omit)
    keep = ('spine_beam', 'spine_roof', 'spine_floor', 'spine_route', 'spine_light')    # overhead beams and roof run over the openings; floors are under them
    live = lambda: [o for o in dict.fromkeys(lib_coll.all_objects) if o.name not in omit and not o.name.startswith(keep)] + \
                   [o for o in wrap.objects if o.library is None and not o.name.startswith(keep)]
    nw = split_openings(wrap, omit, live(), 1, (-2.3, -1.7), [(fe(CONC['y0']), fe(CONC['y1']), 4.6)])
    ne = split_openings(wrap, omit, live(), 1, (1.7, 2.3), [(fe(DOCK[1]) - 1.3, fe(DOCK[1]) + 1.3, 2.6)])
    # skirt dust decals that run across doorways that are open in the source (found by the walk test): clipped at the openings
    objs = [o for o in dict.fromkeys(lib_coll.all_objects) if o.name not in omit and o.name.startswith('stain_')]
    nd = split_openings(wrap, omit, objs, 1, (-15.95, -15.6), [(8.62, 11.4, 2.6)]) + split_openings(wrap, omit, objs, 1, (17.6, 17.95), [(8.8, 11.18, 2.6)]) \
        + split_openings(wrap, omit, objs, 1, (-11.95, -11.6), [(24.83, 27.17, 2.7)]) + split_openings(wrap, omit, objs, 0, (0.0, 0.5), [(-1.3, 1.3, 2.6)]) \
        + split_openings(wrap, omit, objs, 0, (31.1, 31.9), [(-1.8, 1.8, 3.2)]) + split_openings(wrap, omit, objs, 0, (19.4, 20.6), [(-3.0, 3.0, 3.0)]) \
        + split_openings(wrap, omit, objs, 1, (23.5, 23.95), [(24.83, 27.17, 2.7)])          # hall east door: an emergency exit now (evacuation walk test)
    # the front end's context_ground (an 8-vertex box, plan x -170..90, y -200..60, z -0.9..-0.15) roofs the condenser stair shaft: a hole is cut for the shaft
    g = next((o for o in lib_coll.all_objects if o.name == 'context_ground'), None)
    if g is not None:
        x0, x1 = ST['xw'] - ST['t'] - FE_LOC[0], ST['xe'] + ST['t'] - FE_LOC[0]; y0, y1 = ST['ybot'] - FE_LOC[1], ST['yn'] + ST['t'] - FE_LOC[1]
        print('GROUND hole for the stair shaft:', hole_in_slab(wrap, omit, g, x0, x1, y0, y1), 'pieces')
    print('SPINE openings: west (concourse)', nw, 'east (dock)', ne, 'objects split; doorway decals clipped', nd)

_FE_BASE = (BM.open_portal_cap, BM.clear_yard_for_shed, BM.localise_evac_sign, BM.totem_back_board)      # build_combined_map's front-end patches without trim_spine_for_concourse
BM.PATCHES['front-end-area'] = lambda w, l, o: ([f(w, l, o) for f in _FE_BASE], patch_front_end_spine(w, l, o))
BM.PATCHES['reactor-room'] = patch_reactor_assembly
BM.PATCHES['turbine-room'] = patch_turbine
BM.PATCHES['electrical-room'] = patch_electrical
BM.PATCHES['waste-storage'] = patch_waste
BM.PATCHES['condenser-bay'] = patch_condenser
BM.PATCHES['fuel-corridor'] = patch_fuel
BM.PATCHES['cooling-plant'] = patch_cooling
BM.TURBINE_CUTS.clear(); BM.MEDICAL_CUTS.clear()

# ------------------------------------------------------------------------------------------------------------------------------------------------
# Condenser stair: turbine west door (reactor-local x -4.25, y 26.95..28.95) -> top landing -> 34 risers down to z -6 -> corridor east under the turbine end -> condenser D01 stub.
# The y values are reactor-local plus RY (the stair moved with the reactor).
# ------------------------------------------------------------------------------------------------------------------------------------------------
ST = dict(xw=-6.65, xe=-4.55, t=0.3, ytop=RY + 26.8, ybot=RY + 16.9, yn=RY + 29.25, risers=34, drop=6.0, roof=2.9,
          cy0=RY + 14.5, cy1=RY + 16.9, cx1=COND[0] + 1.24, cx0b=COND[0] - 1.24, vy=COND[1] - 2.56, ch=2.7)

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
    lights = [((s['xw'] + s['xe']) / 2, RY + 28.0, s['roof'] - 0.12, 140), ((s['xw'] + s['xe']) / 2, RY + 22.0, s['roof'] - 0.12, 260), ((s['xw'] + s['xe']) / 2, RY + 18.0, -2.6, 160),
              (-3.0, RY + 15.7, zc - 0.12, 70), (0.6, RY + 15.7, zc - 0.12, 70), (COND[0], RY + 18.2, zc - 0.12, 60)]     # corridor lights lowered from 110 W: 6.9 % clipped at the D01 view
    for i, (x, y, z, e) in enumerate(lights):
        ld = bpy.data.lights.new('STAIR light %d' % i, 'AREA'); ld.energy = e; ld.size = 1.4; ld.size_y = 0.4; ld.color = (1.0, 0.93, 0.82)
        lo = bpy.data.objects.new('STAIR light %d' % i, ld); lo.location = (x, y, z); coll.objects.link(lo)
        box('lamp %d' % i, (x - 0.7, x + 0.7), (y - 0.2, y + 0.2), (z + 0.06, z + 0.11), lamp)
    print('STAIR condenser: %d risers of %.3f m, going %.3f m, %.1f degrees; corridor %.1f m' % (n, rise, g, math.degrees(math.atan2(rise, g)), (cx1 - cx0) + (s['vy'] - cy1)))

# ------------------------------------------------------------------------------------------------------------------------------------------------
# South concourse (replaces build_combined_map.add_reactor_concourse, which was sized for the long corridor's F02 adapter): one room joining the short corridor's
# F02E door (its west wall is the corridor's east outer face, x -5.46), the shortened spine (west wall opening) and the reactor south door (tunnel north).
# Same build as the old concourse: concrete shell, spawn plaster, floor, ceiling, dado and lamps; the tunnel is reactor_links.hall with the tunnel zone dressing.
# ------------------------------------------------------------------------------------------------------------------------------------------------
def add_concourse():
    C = CONC; w = C['wall']; sl = C['slab']; top = C['roof'] + sl
    coll = bpy.data.collections.new('CONNECTOR_reactor_south_concourse'); bpy.context.scene.collection.children['COMBINED_MAP'].children.link(coll)
    M, _air = BM.spawn_assets(); box = lambda n, xs, ys, zs, m: BM._box(coll, 'CONNECTOR ' + n, xs, ys, zs, m)
    plaster, conc, floor, ceil, steel, lamp, dado, skirt = M['wall'], M['slab'], M['floor'], M['ceiling'], M['steel'], M['lamp'], M['dado'], M['skirt']
    x0, x1, y0, y1 = C['x0'], C['x1'], C['y0'], C['y1']; xs = SPINE_W                # x1 is the spine's west inner face; its floor and roof take over at x 5.85
    fy0, fy1, fh = F02E[1] - 1.19, F02E[1] + 1.19, 3.0                                # corridor door clear opening on the west wall
    cn = FUEL[1] + 5.53                                                               # the corridor's east wall starts at module y 5.53 (plan cut); south of it a notch is filled
    box('floor slab', (x0, xs), (y0 - w, y1 + w), (-sl, -0.04), conc); box('floor', (x0, xs), (y0, y1), (-0.04, 0.0), floor)
    box('roof', (x0 - w, x1), (y0 - w, y1 + w), (C['roof'], top), conc); box('ceiling skin', (x0, x1), (y0, y1), (C['roof'] - 0.04, C['roof']), ceil)
    # west: the corridor wall (outer face x0, top z 4.84) is the wall up to its roof; a concrete band above it to the concourse roof, a fill in the corridor's corner notch
    box('west wall above corridor', (x0 - w, x0), (y0 - w, y1 + w), (4.84, top), conc)
    box('west corner fill', (x0 - w, x0), (y0 - w, cn), (0.0, 4.84), conc)
    for nm, ys_, zs_ in (('south', (y0, fy0), (0.04, C['roof'] - 0.04)), ('north', (fy1, y1), (0.04, C['roof'] - 0.04)), ('over door', (fy0, fy1), (fh, C['roof'] - 0.04))):
        box('plaster west ' + nm, (x0, x0 + 0.04), ys_, zs_, plaster)
    box('south wall', (x0, x1), (y0 - w, y0), (0.0, top), conc); box('plaster south', (x0, x1), (y0, y0 + 0.04), (0.04, C['roof'] - 0.04), plaster)
    box('east wall above spine roof', (xs, x1), (y0, y1 + w), (4.2, top), conc)
    # north wall: solid either side of the hall door opening (x -2.5..2.5, height 5.0), lintel above it
    box('north wall west', (x0, -2.5), (y1, y1 + w), (0.0, top), conc); box('north wall east', (2.5, x1), (y1, y1 + w), (0.0, top), conc)
    box('north lintel', (-2.5, 2.5), (y1, y1 + w), (5.0, top), conc)
    box('plaster north west', (x0, -2.5), (y1 - 0.04, y1), (0.04, C['roof'] - 0.04), plaster); box('plaster north east', (2.5, xs), (y1 - 0.04, y1), (0.04, C['roof'] - 0.04), plaster)
    box('hall frame head', (-2.9, 2.9), (y1 - 0.05, y1 + w), (4.8, 5.0), steel)
    box('corridor door frame head', (x0 + 0.04, x0 + 0.16), (fy0 - 0.2, fy1 + 0.2), (fh, fh + 0.2), steel)
    for nm, ys_ in (('south', (fy0 - 0.2, fy0)), ('north', (fy1, fy1 + 0.2))): box('corridor door jamb ' + nm, (x0 + 0.04, x0 + 0.16), ys_, (0.0, fh), steel)
    # tunnel through the hall's south wall (cut by reactor_links.HALL_CUTS['south_door']) to the concourse north wall
    import reactor_links
    Mt = BM.zone_mats('tunnel')
    tp = reactor_links.hall(coll, 'CONNECTOR hall tunnel', reactor_links.fillet([(0.0, RY - 10.9), (0.0, y1 + w)], 1.0), 5.0, 5.0, Mt)
    reactor_links.dress_hall(coll, tp, 'tunnel', Mt, [], haze=False)
    # washable dado and skirt (spawn trim materials)
    for nm, xr, yr in (('west south', (x0 + 0.04, x0 + 0.09), (y0, fy0 - 0.2)), ('west north', (x0 + 0.04, x0 + 0.09), (fy1 + 0.2, y1)), ('south', (x0, xs - 0.2), (y0 + 0.04, y0 + 0.09)),
                       ('north west', (x0, -2.5), (y1 - 0.09, y1 - 0.04)), ('north east', (2.5, xs), (y1 - 0.09, y1 - 0.04))):
        box('dado ' + nm, xr, yr, (0.1, 1.15), dado); box('dado cap ' + nm, xr, yr, (1.15, 1.2), skirt)
    yc = (y0 + y1) / 2
    for i, x in enumerate((-3.2, 0.0, 3.2)):
        box('lamp %d' % i, (x - 0.9, x + 0.9), (yc - 0.2, yc + 0.2), (C['roof'] - 0.08, C['roof']), lamp)
        ld = bpy.data.lights.new('CONNECTOR light %d' % i, 'AREA'); ld.energy = 170; ld.size = 1.8; ld.size_y = 0.4; ld.color = (1.0, 0.92, 0.8)
        lo = bpy.data.objects.new('CONNECTOR light %d' % i, ld); lo.location = (x, yc, C['roof'] - 0.12); coll.objects.link(lo)
    # the spine's end door frame stops at z 3.6 and the spine roof top is z 4.4: cap the slot over it (as on the old concourse, measured with rays 2026-10-11)
    box('spine end cap', (6.15, 9.85), (SPINE_END - 0.07, SPINE_END + 0.05), (3.5, 4.4), conc)
    # wayfinding: threshold strips at the three openings and a sign over each way out
    paint = BM._mat('CONNECTOR hazard paint', (0.75, 0.55, 0.05), 0.6)
    box('strip hall', (-3.0, 3.0), (y1 - 0.55, y1 - 0.25), (0.0, 0.012), paint)
    box('strip fuel corridor', (x0 + 0.25, x0 + 0.55), (fy0, fy1), (0.0, 0.012), paint)
    box('strip spine', (5.3, 5.6), (y0, y1), (0.0, 0.012), paint)
    sign = BM._mat('CONNECTOR sign paint', (0.9, 0.85, 0.7), 0.5, 0.0, 1.2)
    def _sign(text, loc, rz, size=0.42):
        cu = bpy.data.curves.new('CONNECTOR sign ' + text, 'FONT'); cu.body = text; cu.size = size; cu.align_x = 'CENTER'; cu.extrude = 0.01; cu.materials.append(sign)
        o = bpy.data.objects.new('CONNECTOR sign ' + text, cu); o.location = loc; o.rotation_euler = (math.pi / 2, 0, rz); coll.objects.link(o)
    _sign('FUEL CORRIDOR', (x0 + 0.06, F02E[1], 3.6), math.pi / 2)            # west wall over the corridor door, facing +x
    _sign('FRONT-END SPINE', (5.83, yc, 5.0), -math.pi / 2)                  # over the spine opening, facing -x
    _sign('REACTOR HALL', (0.0, y1 - 0.06, 5.35), 0.0)                       # north lintel over the tunnel, facing -y
    print('CONCOURSE added: clear x %.2f to %.2f, y %.2f to %.2f, height %.1f' % (x0, xs, y0, y1, C['roof']))

BM.add_reactor_concourse = add_concourse

# ------------------------------------------------------------------------------------------------------------------------------------------------
# Wayfinding over the new doors (plan frame, ivory emissive text like the concourse signs).
# ------------------------------------------------------------------------------------------------------------------------------------------------
def add_signs(root):
    coll = bpy.data.collections.new('CONNECTOR_signs'); root.children.link(coll)
    mat = BM._mat('ASSEMBLY sign paint', (0.9, 0.85, 0.7), 0.5, 0.0, 1.2)
    def sign(text, loc, rz, size=0.32):
        cu = bpy.data.curves.new('SIGN ' + text, 'FONT'); cu.body = text; cu.size = size; cu.align_x = 'CENTER'; cu.extrude = 0.01; cu.materials.append(mat)
        o = bpy.data.objects.new('SIGN ' + text, cu); o.location = loc; o.rotation_euler = (math.pi / 2, 0, rz); coll.objects.link(o)     # rz +90: text faces +x, -90: faces -x
    sign('WASTE', (10.74, WASTE[1], 4.45), -math.pi / 2, 0.4)                      # reactor east wall, inner face x 10.8, over the new opening above the wall's gauges and panels (facing -x)
    sign('COMPLIANCE DOCK', (SPINE_E - 0.33, DOCK[1], 2.9), -math.pi / 2)            # spine east wall, inner face x 9.85 (facing -x)
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
    ('HALL_EAST', 'front-end-area', (23.97, 26.0), (1, 0), 2.32, 2.6, 'double leaf', 'closed', 'east evacuation road (canopy)', 'hall_E_door_leaf_+-1.001 kept in the closed position'),
    ('MINE_PORTAL', 'mine', (-39.0, -29.0), (1, 0), 7.2, 3.9, 'portal (no leaf)', 'open', 'front-end-area (yard)', 'tunnel mouth (first timber set); front end portal_void and the portal cap faces left out'),
    ('YARD_SERVICE', 'front-end-area', (-54.0, 19.85), (0, 1), 2.4, 2.35, 'single leaf', 'closed', 'west evacuation path', 'service_door_leaf kept closed'),
    ('YARD_EVAC_GATE', 'front-end-area', (-36.0, -4.0), (0, -1), 5.8, 2.3, 'double gate (evacuation)', 'closed', 'outside: the evacuation point', 'evac_leaf_frame+-1, push bars, stripes (closed; opens for evacuation)'),
    ('YARD_FREIGHT_GATE', 'front-end-area', (-30.2, 19.9), (0, 1), 3.1, 3.1, 'sliding gate', 'open', 'refinery freight door', 'freight_gate_leaf parked'),
    ('REFINERY_FUEL', 'fuel-corridor', (0, 0), (0, -1), 2.6, 3.0, 'opening (refinery Door_Reactor)', 'open', 'refinery', 'refinery REACTOR door: open frame'),
    ('FUEL_F02E', 'fuel-corridor', (16.74, 6.98), (1, 0), 2.38, 3.0, 'double leaf (the S03 door moved to the east wall)', 'open', 'concourse (reactor south)', 'FC | Reactor transfer leaves left out (closed-state asset)'),
    ('REACTOR_S', 'reactor-room', (0, -12.2), (0, -1), 5.0, 5.0, 'opening (cut)', 'open', 'concourse', 'hall wall cut south_door'),
    ('REACTOR_N', 'reactor-room', (0, 14.4), (0, 1), 5.0, 5.0, 'stub double door', 'open', 'turbine-room D01', 'FUEL HANDLING.* door pieces left out (closed-state asset)'),
    ('REACTOR_W', 'reactor-room', (-14.4, 0), (-1, 0), 5.0, 5.0, 'stub double door', 'open', 'cooling-plant CP-P01', 'MAIN ACCESS.* door pieces left out (closed-state asset)'),
    ('REACTOR_SE', 'reactor-room', (11.0, -11.0), (0.7071, -0.7071), 5.0, 5.0, 'stub double door', 'closed', 'east evacuation yard', 'COOLING PLANT.* door pieces kept (closed)'),
    ('REACTOR_BLAST', 'reactor-room', (0, CONC['y1'] - 0.27 - RY), (0, -1), 5.0, 4.96, 'blast door, sliding pair (new)', 'open', 'concourse',
     'BLAST reactor leaf west/east parked behind the concourse north wall; closed position x -2.75..0 and 0..2.75 (seal chamber)'),
    ('REACTOR_E_WASTE', 'reactor-room', (11.2, (WASTE_HOLE[0] + WASTE_HOLE[1]) / 2), (1, 0), round(WASTE_HOLE[1] - WASTE_HOLE[0], 2), WASTE_HOLE[2], 'opening (new cut through the east wall patch panel)', 'open', 'waste-storage',
     'no leaf (waste receiving shutter is the door)'),
    ('TURBINE_D01', 'turbine-room', (0, 0), (0, -1), 2.4, 2.7, 'two opposed sliding leaves', 'open', 'reactor north stub', 'contract: parked in module pockets'),
    ('TURBINE_D02', 'turbine-room', (0, 24.0), (0, 1), 2.4, 2.7, 'two opposed sliding leaves', 'closed', 'east evacuation road (north strip)', 'D02 electrical parked leaf pair moved shut (local copies)'),
    ('TURBINE_E_ELECTRICAL', 'turbine-room', (10.125, ELEC_DOOR_Y), (1, 0), 2.4, 2.7, 'opening (new cut) + electrical D01 leaves', 'open', 'electrical-room D01', 'leaves are electrical D01 (parked inside electrical)'),
    ('ELECTRICAL_D01', 'electrical-room', (0, 0), (0, -1), 2.4, 2.7, 'sliding pair', 'open', 'turbine-room (east door)', 'parked'),
    ('ELECTRICAL_D02', 'electrical-room', (0, 16.4), (0, 1), 2.4, 2.7, 'sliding pair', 'closed', 'east evacuation road', 'leaves moved shut (local copies)'),
    ('TURBINE_W_STAIR', 'turbine-room', (-4.125, STAIR_DOOR_Y), (-1, 0), 2.0, 2.6, 'opening (new cut)', 'open', 'condenser stair', 'no leaf'),
    ('CONDENSER_D01', 'condenser-bay', (0, 0), (0, -1), 2.0, 2.4, 'two opposed sliding leaves', 'open', 'condenser stair corridor', 'parked open (contract); stub blanking left out'),
    ('COOLING_P01', 'cooling-plant', (0, 0), (0, -1), 5.0, 5.0, 'overhead folding shutter', 'open', 'reactor west stub', 'raised (contract: fixed open)'),
    ('COOLING_W_EXIT', 'cooling-plant', ((COOL_EXIT_Y[0] + COOL_EXIT_Y[1]) / 2 - RY, 13.3), (0, 1), 1.6, 2.35, 'single leaf (new emergency door)', 'closed', 'west evacuation path',
     'EVAC cooling exit leaf (closed; opens for evacuation)'),
    ('WASTE_RECEIVING', 'waste-storage', (0, 0), (0, -1), 3.0, 3.2, 'rolling shutter', 'open', 'reactor hall (east opening)', 'rolled up (contract: parked fully open)'),
    ('WASTE_PERSONNEL', 'waste-storage', (6.16, 2.4), (1, 0), 1.2, 2.3, 'hinged leaf, outward', 'closed', 'east evacuation yard', 'leaf turned into the frame (local copies)'),
    ('WASTE_DISPATCH', 'waste-storage', (0, 18.0), (0, 1), 2.4, 2.8, 'rolling shutter', 'closed', 'east evacuation road', 'new curtain'),
    ('DOCK_P1', 'compliance-dock', (0, -1.0), (0, -1), 2.4, 2.6, 'sliding (X) in perimeter wall', 'open', 'spine (east door)', 'P1 deep back wall and leaf left out'),
    ('DOCK_P2', 'compliance-dock', (0, 15.8), (0, 1), 4.6, 3.5, 'opposed sliding blast leaves', 'closed', 'outside (arrival)', 'contract default sealed'),
    ('SPINE_NORTH_END', 'front-end-area', (0, SPINE_END_L), (0, 1), 3.3, 3.3, 'single leaf', 'closed', 'east evacuation alley (emergency exit)',
     'reactor_door kept closed (moved with the spine end)'),
    ('SPINE_W_CONCOURSE', 'front-end-area', (-2.0, fe((CONC['y0'] + CONC['y1']) / 2)), (-1, 0), round(CONC['y1'] - CONC['y0'], 2), 4.2, 'opening (west wall split out)', 'open', 'concourse (reactor south)', 'no leaf'),
    ('SPINE_E_DOCK', 'front-end-area', (2.0, fe(DOCK[1])), (1, 0), 2.6, 2.6, 'opening (new cut)', 'open', 'compliance-dock', 'no leaf (dock P1 is the door)'),
]
# Emergency exits: closed in normal play, open in the evacuation state; leaf_regex names the closed-leaf objects (the walk test's --meltdown mode leaves them out).
EMERGENCY = {'REACTOR_SE': r'^(COOLING PLANT\..*door|RH refine door hardware COOLING PLANT)', 'WASTE_DISPATCH': r'^WASTE dispatch shutter', 'SPINE_NORTH_END': r'^reactor_door moved$',
             'HALL_EAST': r'^hall_E_door_leaf_', 'YARD_SERVICE': r'^service_door_(leaf|push)$', 'YARD_EVAC_GATE': r'^evac_(leaf_frame|push_bar|stripe)',
             'TURBINE_D02': None, 'ELECTRICAL_D02': None, 'WASTE_PERSONNEL': None, 'COOLING_W_EXIT': None}      # None: filled from LEAF_NAMES / evacuation.build
STATE_ANCHORS = {'closed': 'blocks: collider DOOR_<id>_blocker enabled', 'open': 'passes: blocker disabled', 'locked': 'closed and refuses interaction'}

def add_door_anchors(root):
    coll = bpy.data.collections.new('DOORS'); root.children.link(coll)
    place = {r[0]: (r[3], r[4]) for r in BM.ROOMS}; rows = []
    for did, room, c, n, w, h, kind, state, to, leaf in DOORS:
        loc, rz = place[room]; p = wxy(loc, rz, *c); d = Vector(rot(rz)(*n)).normalized()
        e = bpy.data.objects.new('DOOR_' + did, None); e.empty_display_type = 'ARROWS'; e.empty_display_size = 0.6
        e.location = (p.x, p.y, loc[2]); e.rotation_euler = (0, 0, math.atan2(d.y, d.x)); coll.objects.link(e)
        em = did in EMERGENCY; rx = EMERGENCY.get(did) or ''
        for k, v in (('door_id', did), ('owner_room', room), ('kind', kind), ('state_default', state), ('states', 'open,closed,locked'), ('leads_to', to),
                     ('clear_width_m', w), ('clear_height_m', h), ('leaf', leaf), ('emergency_exit', em), ('evac_state', 'open' if em else state), ('leaf_regex', rx)): e[k] = v
        rows.append(dict(id=did, owner=room, plan=[round(p.x, 3), round(p.y, 3), loc[2]], outward=[round(d.x, 4), round(d.y, 4)], clear_w=w, clear_h=h, kind=kind, state=state, leads_to=to, leaf=leaf,
                         emergency_exit=em, evac_state='open' if em else state, leaf_regex=rx))
    os.makedirs(os.path.join(HERE, 'validation'), exist_ok=True)
    json.dump(dict(note='Door table of the compact map, assembly pass. Unreviewed. Runtime states: ' + json.dumps(STATE_ANCHORS) + '. Emergency exits (emergency_exit true) are closed '
                        'in normal play and open in the evacuation state (evac_state); leaf_regex matches their closed-leaf objects.', closed_copies=CLOSED, doors=rows),
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

EMISSION_OVERRIDES = {}  # material name -> emission strength (the first pass dimmed the S03 transfer hall's accents; that hall is gone)
HALL_LIGHT_SCALE = {}    # connector collection -> light energy factor

def post_build():
    root = bpy.context.scene.collection.children['COMBINED_MAP']
    bpy.context.scene['reactor_y'] = RY                      # read by walk_test.py, measure_lighting.py and the plan tools
    for name, strength in EMISSION_OVERRIDES.items():
        m = bpy.data.materials.get(name)
        if m and m.node_tree:
            for n in m.node_tree.nodes:
                if n.type == 'BSDF_PRINCIPLED': n.inputs['Emission Strength'].default_value = strength
            print('EMISSION override', name, strength)
    for cname, k in HALL_LIGHT_SCALE.items():
        c = bpy.data.collections.get(cname)
        if c:
            for o in c.all_objects:
                if o.type == 'LIGHT': o.data.energy *= k
            print('LIGHT scale', cname, k)
    add_condenser_stair(root); add_signs(root); add_fill_lights(root)
    import re, evacuation
    EMERGENCY.update(evacuation.build(root, sys.modules[__name__]))
    for did in ('TURBINE_D02', 'ELECTRICAL_D02', 'WASTE_PERSONNEL'):
        EMERGENCY[did] = '^(' + '|'.join(re.escape(n) for n in LEAF_NAMES.get(did, ['(none)'])) + ')$'
    add_door_anchors(root)
    try:
        import assembly_colliders; assembly_colliders.build(root, sys.modules[__name__])
    except ImportError: print('COLLIDERS module not found')

BM.add_door_placeholders = post_build

if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    out = a[a.index('--output') + 1] if '--output' in a else os.path.join(HERE, 'combined_map.blend')
    BM.build('compliance-dock', out)
