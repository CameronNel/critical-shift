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
sys.path.insert(0, HERE)
SRC = os.path.normpath(os.path.join(HERE, '..', 'sources'))

# key, library file (relative to SRC), collection to instance, plan translation (x, y, z), rotation about z (degrees), note
# Objects left out of a room's linked membership (open doorways), by room key. Spawn: the 22 airlock exclusions of
# sections/facility-assembly/connections/access/DOOR_BINDINGS.json (row spawn_airlock) plus the four SERVICE_end closures
# that the old map's fix_spawn_transition.py removed.
# Front end: portal_void (a dark box closing the portal mouth, local x -66 to -61.4) and mountain_mass (an 8-vertex rock box,
# local x -98 to -64, y -16 to 30, z -1 to 9) are its stand-ins for the mountain and mine; the real mine module replaces both.
OMIT = {'compliance-dock': ['P1 deep back wall', 'P1 deep door leaf'], 'fuel-corridor': ['FC | Plant service left leaf', 'FC | Plant service right leaf', 'FC | Plant service left handling wear', 'FC | Plant service right handling wear'], 'front-end-area': ['portal_void', 'mountain_mass', 'cliff_face', 'hall_E_door_leaf_-1.001', 'hall_E_door_leaf_1.001', 'service_door_leaf', 'service_door_push'], 'spawn-room': ['AIRLOCK_leaf_body', 'AIRLOCK_steel_face', 'AIRLOCK_structural_rib', 'AIRLOCK_structural_rib.001', 'AIRLOCK_leaf_body.001', 'AIRLOCK_steel_face.001', 'AIRLOCK_structural_rib.002', 'AIRLOCK_structural_rib.003', 'LIFE_airlock_gauge_case', 'LIFE_airlock_gauge_dial', 'LIFE_airlock_pressure_tick', 'LIFE_airlock_pressure_tick.001', 'LIFE_airlock_pressure_tick.002', 'LIFE_airlock_pressure_tick.003', 'LIFE_airlock_pressure_tick.004', 'LIFE_airlock_pressure_tick.005', 'LIFE_airlock_pressure_tick.006', 'LIFE_airlock_pressure_tick.007', 'LIFE_airlock_pressure_tick.008', 'LIFE_airlock_pressure_tick.009', 'LIFE_airlock_pressure_tick.010', 'LIFE_airlock_pressure_unit', 'SERVICE_end', 'SERVICE_end_washable_dado', 'SERVICE_end_coved_skirt', 'SERVICE_end_dado_cap']}

def wm(o):
    """World matrix from the object's own transforms. Linked objects that have not been through a depsgraph report an identity matrix_world,
    so it cannot be trusted at build time."""
    m = o.matrix_basis.copy()
    return (wm(o.parent) @ o.matrix_parent_inverse @ m) if o.parent else m

# Local replacement for the front end's cliff_face with the tunnel opening cut: the 420 faces of the rock plate that closes the portal
# stub (local plane x -61.6, y 6.6 to 13.4, z -0.1 to 4.3) are deleted so the mine tunnel opens into the yard. Linked meshes cannot be
# edited, so the object is copied locally; the source module is unchanged.
def open_portal_cap(wrap, lib_coll, omit):
    import bmesh
    src = next(o for o in lib_coll.all_objects if o.name == 'cliff_face')
    me = src.data.copy(); me.name = 'cliff_face_opened'
    bm = bmesh.new(); bm.from_mesh(me)
    dead = [f for f in bm.faces if abs(f.calc_center_median().x + 61.6) < 0.3 and 6.6 <= f.calc_center_median().y <= 13.4
            and -0.1 <= f.calc_center_median().z <= 4.3]
    bmesh.ops.delete(bm, geom=dead, context='FACES'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('cliff_face', me); o.matrix_basis = src.matrix_basis; wrap.objects.link(o)
    print('PORTAL_CAP faces removed', len(dead))

MINE_MOUTH_X = -39.0   # module frame: first timber set of the tunnel; mine surface east of it is trimmed, except the portal shed
SHED = (-39.6, -21.9, -37.6, -20.0)   # module frame x0, x1, y0, y1: the portal shed footprint (measured: boards -39.25 to -22.25, -37.28 to -20.36)
SHED_COLLECTIONS = ('R39 | Portal shed', 'R39 | Shed floor')

def mesh_islands(bm):
    seen = set(); out = []
    for v in bm.verts:
        if v.index in seen: continue
        st = [v]; seen.add(v.index); cur = []
        while st:
            a = st.pop(); cur.append(a)
            for e in a.link_edges:
                b = e.other_vert(a)
                if b.index not in seen: seen.add(b.index); st.append(b)
        out.append(cur)
    return out

# North-west service path (front end: x -47.4 to -44.8 from the lane y -68.8 to the cooling-plant service gate in the north fence at y -60.1).
# The mine's portal shed stands across it, so the shed gets a walkable passage: an opening in its north wall on the gate line and a clear corridor
# down to the mine lane. Module frame (plan + (14.4, 41)); 2.8 m wide, 2.9 m high.
PASSAGE_X = (-33.1, -30.3)
PASSAGE_Y = (-27.8, -19.5)
PASSAGE_Z = (0.25, 2.9)

def carve_passage(wrap, lib_coll, omit):
    """Local copies of the shed meshes with the passage volume cut out. Small islands (props, rope, boards) inside the volume are deleted whole;
    larger ones (wall, frame, beams) are sliced at the volume faces, the faces inside deleted and the cut ends capped. Floors and ground (under 0.5 m high) are left."""
    import bmesh
    from mathutils import Vector
    xa, xb = PASSAGE_X; ya, yb = PASSAGE_Y; za, zb = PASSAGE_Z; eps = 1e-3
    inbox = lambda p: xa < p.x < xb and ya < p.y < yb and za < p.z < zb
    hits = []
    for o in list(lib_coll.all_objects):   # whole objects inside the passage volume (wall signs left hanging once the wall they hang on is cut) go
        if o.name in omit or o.type not in ('MESH', 'FONT', 'CURVE') or any(k in o.name.lower() for k in ('haze', 'fog')): continue
        q = [wm(o) @ Vector(c) for c in o.bound_box]
        dim = [max(p[i] for p in q) - min(p[i] for p in q) for i in range(3)]
        crosses = max(p.x for p in q) > xa and min(p.x for p in q) < xb and max(p.y for p in q) > ya and min(p.y for p in q) < yb and max(p.z for p in q) > za and min(p.z for p in q) < zb
        thin_sign = crosses and min(dim[0], dim[1]) <= 0.1 and dim[2] < 1.2     # a flat board hanging across the passage
        if thin_sign or all(xa - 0.1 < p.x < xb + 0.1 and ya < p.y < yb and za - 0.1 < p.z < zb + 0.1 for p in q): omit.add(o.name); hits.append((o.name, 'removed whole'))
    for o in list(lib_coll.all_objects):
        if o.name in omit or o.type != 'MESH' or o.modifiers or o.parent or any(k in o.name.lower() for k in ('haze', 'fog')) or any(c.name.startswith('R40') for c in o.users_collection): continue
        pts = [wm(o) @ Vector(c) for c in o.bound_box]
        if not (max(p.x for p in pts) > xa and min(p.x for p in pts) < xb and max(p.y for p in pts) > ya and min(p.y for p in pts) < yb and max(p.z for p in pts) - min(p.z for p in pts) >= 0.5 and max(p.z for p in pts) > za): continue
        me = o.data.copy(); me.transform(wm(o)); bm = bmesh.new(); bm.from_mesh(me)
        gone = sliced = 0; big = False
        for isl in mesh_islands(bm):
            lo = Vector((min(v.co.x for v in isl), min(v.co.y for v in isl), min(v.co.z for v in isl))); hi = Vector((max(v.co.x for v in isl), max(v.co.y for v in isl), max(v.co.z for v in isl)))
            if not (hi.x > xa and lo.x < xb and hi.y > ya and lo.y < yb and hi.z > za and lo.z < zb): continue
            if max(hi.x - lo.x, hi.y - lo.y, hi.z - lo.z) <= 2.5:
                bmesh.ops.delete(bm, geom=isl, context='VERTS'); gone += 1
            else: big = True
        if big:
            for pl in ((xa, 0), (xb, 0), (za, 2), (zb, 2)):
                no = [0, 0, 0]; no[pl[1]] = 1; co = [0, 0, 0]; co[pl[1]] = pl[0]
                bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), plane_co=co, plane_no=no)
            dead = [f for f in bm.faces if inbox(f.calc_center_median())]
            sliced = len(dead); bmesh.ops.delete(bm, geom=dead, context='FACES')
            near = lambda v: xa - eps <= v.co.x <= xb + eps and ya - eps <= v.co.y <= yb + eps and za - eps <= v.co.z <= zb + eps
            edges = [e for e in bm.edges if e.is_boundary and all(near(v) for v in e.verts)]
            if edges: bmesh.ops.holes_fill(bm, edges=edges, sides=0)
        if gone or sliced:
            bm.normal_update(); bm.to_mesh(me); bm.free()
            n = bpy.data.objects.new(o.name, me); wrap.objects.link(n); omit.add(o.name); hits.append((o.name, gone, sliced))
        else: bm.free(); bpy.data.meshes.remove(me)
    print('PASSAGE carved:', hits)

# The mine mountain (R40) is 103 m long (plan y -123 to -20) against v7's mountain y -104 to -60, and its north end sits where the cooling plant and the yard-to-cooling
# link go. Its two ends are eased down to the ground: heights scale by 1 - smoothstep along y, module frame (plan + (14.4, 41)).
MOUNTAIN_TAPER_NORTH = (-8.0, 12.0)     # plan y -49 to -29
MOUNTAIN_TAPER_SOUTH = (-58.0, -76.0)   # plan y -99 to -117

def taper_mountain(wrap, lib_coll, omit):
    import numpy as np
    def f(y):
        n0, n1 = MOUNTAIN_TAPER_NORTH; s0, s1 = MOUNTAIN_TAPER_SOUTH
        tn = np.clip((y - n0) / (n1 - n0), 0, 1); ts = np.clip((y - s0) / (s1 - s0), 0, 1)
        sm = lambda t: t * t * (3 - 2 * t)
        return 1.0 - np.maximum(sm(tn), sm(ts))
    done = []
    for o in list(lib_coll.all_objects):
        if o.name in omit or o.type != 'MESH' or o.parent or o.modifiers or not any(c.name.startswith('R40') for c in o.users_collection): continue
        me = o.data.copy(); n = len(me.vertices); co = np.empty(n * 3, dtype=np.float32); me.vertices.foreach_get('co', co); co = co.reshape(n, 3)
        m = np.array(wm(o)); w = co @ m[:3, :3].T + m[:3, 3]            # module frame
        up = w[:, 2] > 0
        w[up, 2] = w[up, 2] * f(w[up, 1]).astype(np.float32)
        me.vertices.foreach_set('co', w.astype(np.float32).ravel()); me.update()
        obj = bpy.data.objects.new(o.name, me); wrap.objects.link(obj); omit.add(o.name); done.append((o.name, n))
    print('MOUNTAIN tapered:', done)

def trim_mine_surface(wrap, lib_coll, omit):
    """Drop the mine's own surface (apron, yard puddles, yard fog, lamps and props outside the shed) east of the tunnel mouth: the front-end
    yard is the surface depot. The owner requires the portal shed in front of the mine, so the shed (and everything inside its footprint)
    is kept. Objects wholly east of the mouth and outside the shed are omitted; meshes that straddle are copied locally with the faces east
    of the mouth and outside the shed deleted. R40 (the mountain) is kept whole."""
    import bmesh
    from mathutils import Vector
    x0, x1, y0, y1 = SHED
    inside = lambda p, m=0.0: x0 - m <= p.x <= x1 + m and y0 - m <= p.y <= y1 + m
    whole = clipped = skipped = shed = 0
    refinery = 'refinery' in INCLUDED
    for o in list(lib_coll.all_objects):
        if refinery and any(c.name == 'R39 | Track' for c in o.users_collection): continue   # the mine's own railway is kept whole and extended
        if o.name in omit or any(c.name.startswith('R40') or c.name in SHED_COLLECTIONS for c in o.users_collection):
            shed += any(c.name in SHED_COLLECTIONS for c in o.users_collection); continue
        if o.type == 'LIGHT':
            if o.data.type != 'SUN' and wm(o).translation.x > MINE_MOUTH_X and not inside(wm(o).translation):
                omit.add(o.name); whole += 1
            continue
        if o.type not in ('MESH', 'CURVE', 'FONT'): continue
        pts = [wm(o) @ Vector(c) for c in o.bound_box]
        mnx = min(p.x for p in pts); mxx = max(p.x for p in pts)
        if mxx <= MINE_MOUTH_X: continue
        if all(inside(p, 0.3) for p in pts): shed += 1; continue
        hits_shed = min(p.y for p in pts) < y1 and max(p.y for p in pts) > y0 and mnx < x1
        if any(k in o.name.lower() for k in ('fog', 'haze')):
            if mnx < MINE_MOUTH_X - 5: continue          # tunnel haze: west of the mouth
            omit.add(o.name); whole += 1; continue
        if mnx >= MINE_MOUTH_X and not hits_shed: omit.add(o.name); whole += 1; continue
        if o.type != 'MESH' or o.modifiers or o.parent: skipped += 1; print('TRIM kept whole (not a plain mesh):', o.name); continue
        me = o.data.copy(); bm = bmesh.new(); bm.from_mesh(me)
        dead = [f for f in bm.faces if (lambda c: c.x > MINE_MOUTH_X and not inside(c))(wm(o) @ f.calc_center_median())]
        bmesh.ops.delete(bm, geom=dead, context='FACES'); bm.to_mesh(me); bm.free()
        n = bpy.data.objects.new(o.name, me); n.matrix_basis = o.matrix_basis; wrap.objects.link(n); omit.add(o.name); clipped += 1
    if refinery: extend_mine_rail(wrap, lib_coll)
    carve_passage(wrap, lib_coll, omit)
    taper_mountain(wrap, lib_coll, omit)
    print('TRIM mine surface: omitted whole', whole, 'clipped', clipped, 'kept whole (non-plain)', skipped, 'shed objects kept', shed)

RAIL_RADIUS = 4.0   # m, turn from the mine lane (y -70) north onto the refinery freight line (x -22.2)

def extend_mine_rail(wrap, lib_coll):
    """Owner preference: the mine's railway replaces the yard's. The mine's last 4.92 m rail segment (rails, sleepers, ironwork; level) is copied end to end
    past the track end (module x -16.0), kept straight, bent through a quarter circle onto the refinery freight line and run to the freight door.
    Rails are sliced every 0.25 m and bent per vertex; sleepers and ironwork are placed rigidly, one island at a time."""
    import bmesh, math
    from mathutils import Vector
    mx, my, _ = next(r[3] for r in ROOMS if r[0] == 'mine')
    Tx, Ey = -22.2 - mx, -60.0 - my                   # module frame: freight line x, rail end y (plan x -22.2, y -60.0 at the refinery freight door)
    R, S0, YC, XS = RAIL_RADIUS, -16.0, -29.0, -20.92
    W = S0 - XS; E = (Tx - R) - S0; A = math.pi * R / 2; Cx, Cy = Tx - R, YC + R; Nn = Ey - Cy; L = E + A + Nn
    def frame(s):
        if s <= E: return Vector((S0 + s, YC)), 0.0
        if s <= E + A: th = (s - E) / R; return Vector((Cx + R * math.sin(th), Cy - R * math.cos(th))), th
        return Vector((Tx, Cy + (s - E - A))), math.pi / 2
    def islands(bm):
        seen = set(); out = []
        for v in bm.verts:
            if v.index in seen: continue
            st = [v]; seen.add(v.index); cur = []
            while st:
                a = st.pop(); cur.append(a)
                for e in a.link_edges:
                    b = e.other_vert(a)
                    if b.index not in seen: seen.add(b.index); st.append(b)
            out.append(cur)
        return out
    src = {o.name: o for o in lib_coll.all_objects if o.name in ('R39 | Rails', 'R39 | Sleepers', 'R39 | Track ironwork')}
    made = 0; k = 0
    while k * W < L:
        sk = k * W; umax = min(W, L - sk)
        for name, o in src.items():
            me = o.data; bm = bmesh.new(); bm.from_mesh(me)
            keep = []; drop = []
            for isl in islands(bm):
                cx = sum(v.co.x for v in isl) / len(isl)
                (keep if (XS - 0.05 <= cx <= XS + (W if name == 'R39 | Rails' else umax)) else drop).append(isl)
            bmesh.ops.delete(bm, geom=[v for isl in drop for v in isl], context='VERTS')
            if name == 'R39 | Rails':
                cut = lambda x, **kw: bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), plane_co=(x, 0, 0), plane_no=(1, 0, 0), **kw)
                if umax < W: cut(XS + umax, clear_outer=True); bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)
                for j in range(1, int(math.ceil(umax / 0.25))): cut(XS + j * 0.25)
                for v in bm.verts:
                    P, psi = frame(sk + v.co.x - XS); t = v.co.y - YC
                    v.co = Vector((P.x - t * math.sin(psi), P.y + t * math.cos(psi), v.co.z))
            else:
                for isl in keep:
                    c = sum((v.co for v in isl), Vector()) / len(isl)
                    P, psi = frame(sk + c.x - XS); t = c.y - YC; cs, sn = math.cos(psi), math.sin(psi)
                    ctr = Vector((P.x - t * sn, P.y + t * cs))
                    for v in isl:
                        rx, ry = v.co.x - c.x, v.co.y - c.y
                        v.co = Vector((ctr.x + rx * cs - ry * sn, ctr.y + rx * sn + ry * cs, v.co.z))
            bm.normal_update()
            me2 = bpy.data.meshes.new(f'{name} ext{k}'); bm.to_mesh(me2); bm.free()
            for m in me.materials: me2.materials.append(m)
            wrap.objects.link(bpy.data.objects.new(f'{name} ext{k}', me2)); made += 1
        k += 1
    print('RAIL extension: straight', round(E, 2), 'arc', round(A, 2), 'north', round(Nn, 2), 'total', round(L, 2), 'tiles', k, 'objects', made)

# Option 1 (owner decision): where the mine's portal shed stands, the front end's own props give way to it. The portal collar, rock face, signage on it,
# ground pads and ground stay. Only objects whose plan centre lies inside the shed footprint are removed, so look-alikes elsewhere in the yard stay.
YARD_PROPS_UNDER_SHED = ('lamp_room_cabin', 'LIGHT_cabin_door', 'sign_lamp_room', 'stain_cabin_', 'board_tag', 'ore_bay_', 'ore_pile_', 'sign_bay_',
                         'stain_bay_', 'floor_bay_no_', 'ore_cart_', 'sign_car_', 'pole_', 'LIGHT_pole_', 'vent_fan', 'ballast_')
YARD_RAIL_CLIPPED = ('rail_rails', 'rail_sleepers')   # the shed carries the mine's own rail through its footprint; the yard rail resumes east of it

def clear_yard_for_shed(wrap, lib_coll, omit):
    if 'mine' not in INCLUDED: return
    import bmesh
    from mathutils import Vector
    mx, my, _ = next(r[3] for r in ROOMS if r[0] == 'mine'); fx, fy, _ = next(r[3] for r in ROOMS if r[0] == 'front-end-area')
    x0, x1, y0, y1 = SHED
    px0, px1, py0, py1 = x0 + mx, x1 + mx, y0 + my, y1 + my
    inside = lambda v: px0 <= v.x + fx <= px1 and py0 <= v.y + fy <= py1
    gone = []; clipped = []
    refinery = 'refinery' in INCLUDED   # owner preference: the mine's railway replaces the yard's, so the whole yard rail goes
    if refinery:   # the loading docks run on past the refinery's south wall (plan y -60.1, the fence line); cut them at the wall
        for o in list(lib_coll.all_objects):
            if o.name in ('dock_west', 'dock_east') and o.type == 'MESH' and not o.modifiers and not o.parent:
                me = o.data.copy(); me.transform(wm(o)); bm = bmesh.new(); bm.from_mesh(me)
                bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), plane_co=(0, -60.1 - fy, 0), plane_no=(0, 1, 0), clear_outer=True)
                bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0); bm.to_mesh(me); bm.free()
                n = bpy.data.objects.new(o.name, me); wrap.objects.link(n); omit.add(o.name); print('DOCK clipped', o.name)
    for o in list(lib_coll.all_objects):
        if o.name in omit: continue
        if refinery and o.name.startswith(('rail_', 'ballast_')): omit.add(o.name); gone.append(o.name); continue
        if o.type == 'LIGHT': c = wm(o).translation
        else:
            ws = [wm(o) @ Vector(v) for v in o.bound_box]; c = sum(ws, Vector()) / len(ws)
        if o.name in YARD_RAIL_CLIPPED and o.type == 'MESH' and not o.modifiers:
            me = o.data.copy(); bm = bmesh.new(); bm.from_mesh(me)
            dead = [f for f in bm.faces if inside(wm(o) @ f.calc_center_median())]
            bmesh.ops.delete(bm, geom=dead, context='FACES'); bm.to_mesh(me); bm.free()
            n = bpy.data.objects.new(o.name, me); n.matrix_basis = o.matrix_basis; wrap.objects.link(n); omit.add(o.name); clipped.append((o.name, len(dead)))
        elif o.name.startswith(YARD_PROPS_UNDER_SHED) and inside(c): omit.add(o.name); gone.append(o.name)
    print('SHED_CLEAR yard objects removed', len(gone), gone, 'rail meshes clipped', clipped)

def localise_evac_sign(wrap, lib_coll, omit):
    src = next((o for o in lib_coll.all_objects if o.name == 'sign_evac_gate'), None)
    if not src: return
    n = bpy.data.objects.new('sign_evac_gate', src.data.copy()); n.matrix_basis = src.matrix_basis; wrap.objects.link(n); omit.add('sign_evac_gate')

def totem_back_board(wrap, lib_coll, omit):
    """directory_totem has its directory board on the south face only; the north face, in the cafeteria's main sightline from the hall, is a bare lilac slab. A copy of board_directory
    rotated 180 degrees about the totem's vertical centre line (front-end local x 2.8, y 13.5) goes on the back."""
    import math
    from mathutils import Matrix
    src = next((o for o in lib_coll.all_objects if o.name == 'board_directory'), None)
    if not src: return
    cx, cy = 2.8, 13.5
    rot = Matrix.Translation((cx, cy, 0)) @ Matrix.Rotation(math.pi, 4, 'Z') @ Matrix.Translation((-cx, -cy, 0))
    n = bpy.data.objects.new('board_directory_back', src.data); n.matrix_basis = rot @ src.matrix_basis; wrap.objects.link(n)

# Reactor room: candidate A, the refined hall (sections/reactor-room/blender/reactorroom.blend). The scene is the room: these are its content
# collections; the review cameras (10 CAMERAS, MF PLAYER WALKTHROUGH), the hidden collision proxy (32 CR COLLISION) and the empty or duplicate
# MODULE_reactor-room / QA collections are left out. 16 'RH refine roof bay' area lights sit directly in the scene root, so they are loaded by name.
REACTOR_LIB = '../../reactor-room/blender/reactorroom.blend'
REACTOR_COLLECTIONS = ['02 ROOF STRUCTURE', '03 POOL AND RAIL', '04 BANK MECHANISMS', '05 PERIMETER EQUIPMENT', 'RF APPROVED SKYLIGHT ROOF',
                       'MF WORKFLOW MACHINERY', 'WA A FUEL BAY', 'WB B WASTE VENT', 'WD D COOLING WALL', 'WF F RIM SERVICE HANDLING',
                       '20 CONTROL MEZZANINE', '23 ASSET PORTS', '24 REACTOR STATE', '25 LIGHTING', '22 R2 ARCHITECTURE', '23 R2 FLOOR AND DRESSING',
                       '26 R2 CONTROL ROOM', '24 R2 PIPING AND CABLES', '27 R2 STATIONS', '29 R2 DRESSING 2', '30 R2 DOOR STUBS', '31 CR CONTROL ROOM REDO',
                       'RH REFINEMENT', 'RH HOIST ANCHOR CORRECTION']

def patch_reactor(wrap, lib_coll, omit):
    path = os.path.normpath(os.path.join(SRC, REACTOR_LIB))
    with bpy.data.libraries.load(path, link=True, relative=True) as (src, dst):
        dst.objects = [n for n in src.objects if n.startswith('RH refine roof bay') and n.endswith((' up', ' down'))]
    for o in dst.objects:
        if o is not None: wrap.objects.link(o)
    print('REACTOR scene-root lights linked', len(dst.objects))
    sys.path.insert(0, HERE); import reactor_links
    hall = [o for c in bpy.data.collections if c.library and os.path.basename(c.library.filepath) == os.path.basename(REACTOR_LIB) for o in c.all_objects]
    reactor_links.cut_hall(wrap, omit, list(dict.fromkeys(hall)), wm, INCLUDED)
    lab = next((m for m in bpy.data.materials if m.library and m.name == 'RH refine signal ivory'), None)
    reactor_links.add_stub_labels(wrap, INCLUDED, lab or _mat('HALL label ivory', (0.9, 0.88, 0.8), 0.5, 0.0, 1.0))

# Reactor south concourse (proposed, unreviewed). Candidate A is rotated 180 degrees so its existing 6.0 m x 5.5 m FUEL HANDLING stub (module north,
# closed double door at the stub end) faces south: plan door plane y -14.5, clear x -3.0 to 3.0, roof z 5.74. The plan's x = -8 and x = +8 south
# doors cannot be cut (module lift stack at the south-west, diagonal cooling stub at the south-east), so one concourse joins three existing openings:
#  * hall stub door, centre x 0, north wall of the concourse (opening 6.0 m wide, lintel above z 5.74);
#  * fuel corridor reactor adapter, open between x -10.62 and -5.38 at plan y -19.6 (its own door stands 0.5 m inside), floor z 0, ceiling 5.9;
#  * spine (front end, plan x 5.85 to 10.15, clear 3.7 m), whose west wall is trimmed locally between plan y -19.6 and -14.8 so the concourse opens into it.
# Concourse clear space: x -10.8 to 5.85, y -19.6 to -14.8 (4.8 m deep), height 5.9. All measured from the modules; see COMBINED_MAP.md.
CONC = {'x0': -10.8, 'x1': 6.15, 'y0': -19.6, 'y1': -14.8, 'wall': 0.3, 'roof': 5.9, 'slab': 0.25}
SPINE_CUT = (-19.6, -14.8)    # plan y range removed from the spine's west wall (spine_wall_-1 and its dado), ribs inside it omitted

def trim_spine_for_concourse(wrap, lib_coll, omit):
    if 'reactor-room' not in INCLUDED: return
    import bmesh
    fx, fy, _ = next(r[3] for r in ROOMS if r[0] == 'front-end-area')
    y0, y1 = SPINE_CUT[0] - fy, SPINE_CUT[1] - fy          # front-end local
    for name in ('spine_wall_-1', 'spine_dado_-1'):
        o = lib_coll.objects.get(name) or next((x for x in lib_coll.all_objects if x.name == name), None)
        if o is None: print('SPINE trim missing', name); continue
        for tag, lo_clamp, hi_clamp in (('a', None, y0), ('b', y1, None)):
            if name == 'spine_dado_-1' and tag == 'b': continue
            me = o.data.copy(); me.transform(wm(o)); bm = bmesh.new(); bm.from_mesh(me)
            for v in bm.verts:
                if hi_clamp is not None and v.co.y > hi_clamp: v.co.y = hi_clamp
                if lo_clamp is not None and v.co.y < lo_clamp: v.co.y = lo_clamp
            bm.to_mesh(me); bm.free()
            n = bpy.data.objects.new(o.name + '_trim_' + tag, me); wrap.objects.link(n)
        omit.add(name)
    for rib in ('spine_rib_-1_8', 'spine_rib_-1_9'): omit.add(rib)
    print('SPINE west wall trimmed between plan y', SPINE_CUT, 'ribs omitted')

def _mat(name, base, rough, metal=0.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = base + (1,); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit: b.inputs['Emission Color'].default_value = (1.0, 0.92, 0.78, 1); b.inputs['Emission Strength'].default_value = emit
    return m

def _box(coll, name, xs, ys, zs, mat):
    import bmesh
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = xs[0] if v.co.x < 0 else xs[1]; v.co.y = ys[0] if v.co.y < 0 else ys[1]; v.co.z = zs[0] if v.co.z < 0 else zs[1]
    import reactor_links
    reactor_links._uv(bm)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = bpy.data.objects.new(name, me); coll.objects.link(o); return o

ASSETS = {}

def spawn_assets():
    """Spawn-room materials and airlock door objects (linked once)."""
    if not ASSETS:
        import reactor_links
        fb = bpy.data.materials.get('CONNECTOR concrete') or _mat('CONNECTOR concrete', (0.20, 0.21, 0.23), 0.85)
        ASSETS['mats'], ASSETS['air'] = reactor_links.load_spawn_assets(os.path.join(SRC, 'spawn-room', 'module.blend'), fb)
    return ASSETS['mats'], ASSETS['air']

def add_reactor_concourse():
    if 'reactor-room' not in INCLUDED: return
    C = CONC; w = C['wall']; sl = C['slab']; top = C['roof'] + sl
    coll = bpy.data.collections.new('CONNECTOR_reactor_south_concourse'); bpy.context.scene.collection.children['COMBINED_MAP'].children.link(coll)
    M, _air = spawn_assets()      # spawn-room plaster, floor, ceiling and trim materials
    plaster = M['wall']; conc = M['slab']; floor = M['floor']; ceil = M['ceiling']; steel = M['steel']; lamp = M['lamp']     # concrete shell outside, spawn plaster, floor and ceiling skins inside
    x0, x1, y0, y1 = C['x0'], C['x1'], C['y0'], C['y1']
    _box(coll, 'CONNECTOR floor slab', (x0 - w, x1), (y0, y1 + w), (-sl, -0.04), conc); _box(coll, 'CONNECTOR floor', (x0, x1), (y0, y1), (-0.04, 0.0), floor)
    _box(coll, 'CONNECTOR roof', (x0 - w, x1), (y0 - w, y1 + w), (C['roof'], top), conc); _box(coll, 'CONNECTOR ceiling skin', (x0, x1), (y0, y1), (C['roof'] - 0.04, C['roof']), ceil)
    for nm, xs, ys in (('west', (x0, x0 + 0.04), (y0, y1)), ('south', (-5.2, x1), (y0, y0 + 0.04)), ('north west', (x0, -2.5), (y1 - 0.04, y1)), ('north east', (2.5, 5.85), (y1 - 0.04, y1))):
        _box(coll, f'CONNECTOR plaster {nm}', xs, ys, (0.04, C['roof'] - 0.04), plaster)
    _box(coll, 'CONNECTOR west wall', (x0 - w, x0), (y0, y1 + w), (0.0, top), conc)
    _box(coll, 'CONNECTOR south wall', (-5.2, x1), (y0 - w, y0), (0.0, top), conc)
    _box(coll, 'CONNECTOR east wall above spine roof', (5.85, x1), (y0, y1 + w), (4.2, top), conc)
    # north wall (y1 to y1 + w): solid left and right of the hall door opening (x -2.5 to 2.5, height 5.0), lintel above it
    _box(coll, 'CONNECTOR north wall west', (x0 - w, -2.5), (y1, y1 + w), (0.0, top), conc)
    _box(coll, 'CONNECTOR north wall east', (2.5, x1), (y1, y1 + w), (0.0, top), conc)
    _box(coll, 'CONNECTOR north lintel', (-2.5, 2.5), (y1, y1 + w), (5.0, top), conc)
    # reducer frame on the hall opening and the tunnel through the hall's south wall (cut by reactor_links.HALL_CUTS['south_door'])
    _box(coll, 'CONNECTOR hall frame head', (-2.9, 2.9), (y1 - 0.05, y1 + w), (4.8, 5.0), steel)
    import reactor_links
    Mt = zone_mats('tunnel')
    tp = reactor_links.hall(coll, 'CONNECTOR hall tunnel', reactor_links.fillet([(0.0, -10.9), (0.0, y1 + w)], 1.0), 5.0, 5.0, Mt)
    reactor_links.dress_hall(coll, tp, 'tunnel', Mt, [], haze=False)
    # washable dado and skirt on the concourse walls (spawn trim materials)
    dado = M['dado']; skirt = M['skirt']
    for nm, xs, ys in (('west', (x0 + 0.04, x0 + 0.09), (y0, y1)), ('south east', (-5.2, x1 - 0.2), (y0 + 0.04, y0 + 0.09)), ('north west', (x0, -2.5), (y1 - 0.09, y1 - 0.04)), ('north east', (2.5, 5.85), (y1 - 0.09, y1 - 0.04))):
        _box(coll, f'CONNECTOR dado {nm}', xs, ys, (0.1, 1.15), dado); _box(coll, f'CONNECTOR dado cap {nm}', xs, ys, (1.15, 1.2), skirt)
    for i, x in enumerate((-2.0, 0.0, 2.0)):
        _box(coll, f'CONNECTOR lamp {i}', (x - 0.9, x + 0.9), (-17.4, -17.0), (C['roof'] - 0.08, C['roof']), lamp)
        ld = bpy.data.lights.new(f'CONNECTOR light {i}', 'AREA'); ld.energy = 170; ld.size = 1.8; ld.size_y = 0.4; ld.color = (1.0, 0.92, 0.8)
        lo = bpy.data.objects.new(f'CONNECTOR light {i}', ld); lo.location = (x - 4.5 if i == 0 else x + (1.5 if i == 2 else 0.0), -17.2, C['roof'] - 0.12); coll.objects.link(lo)
    # the spine's end door frame stops at z 3.6 and the spine roof top is z 4.4, so a 0.8 m slot looked through to the hall wall; cap it (measured with rays, 2026-10-11)
    _box(coll, 'CONNECTOR spine end cap', (6.15, 9.85), (-14.62, -14.50), (3.5, 4.4), conc)
    # wayfinding: painted threshold strips on the floor at the three openings and one sign over each way out (local to the combined scene)
    paint = _mat('CONNECTOR hazard paint', (0.75, 0.55, 0.05), 0.6)
    _box(coll, 'CONNECTOR strip hall', (-3.0, 3.0), (y1 - 0.55, y1 - 0.25), (0.0, 0.012), paint)
    _box(coll, 'CONNECTOR strip fuel corridor', (-10.62, -5.38), (y0 + 0.25, y0 + 0.55), (0.0, 0.012), paint)
    _box(coll, 'CONNECTOR strip spine', (5.3, 5.6), (y0, y1), (0.0, 0.012), paint)
    sign = _mat('CONNECTOR sign paint', (0.9, 0.85, 0.7), 0.5, 0.0, 1.2)
    import math
    def _sign(text, loc, rot, size=0.42):
        cu = bpy.data.curves.new('CONNECTOR sign ' + text, 'FONT'); cu.body = text; cu.size = size; cu.align_x = 'CENTER'; cu.extrude = 0.01; cu.materials.append(sign)
        o = bpy.data.objects.new('CONNECTOR sign ' + text, cu); o.location = loc; o.rotation_euler = rot; coll.objects.link(o)
    _sign('FUEL CORRIDOR', (-8.0, y0 + 0.02, 4.6), (math.pi / 2, 0, math.pi))
    _sign('FRONT-END SPINE', (5.83, -17.2, 5.0), (math.pi / 2, 0, -math.pi / 2))
    _sign('REACTOR CONCOURSE', (x0 + 0.02, -17.2, 3.6), (math.pi / 2, 0, math.pi / 2))
    print('CONCOURSE added: clear x %.1f to %.2f, y %.1f to %.1f, height %.1f' % (x0, 5.85, y0, y1, C['roof']))


# Plan v7 links from the reactor to each neighbour (design/facility-layout/README.md, generate_plan.py SP): turbine 3 m north on x 0; electrical (10,13.75) to (18,26); waste (13.75,-6) to (28,-24);
# cooling (-13.75,-5) to (-30,-19) to (-44.1,-19). Each uses the hall's own stub where it has one (N FUEL HANDLING, W MAIN ACCESS, SE diagonal) and ends on the neighbour's measured door; the electrical door is a new cut in the NE wall.
# polyline in plan metres, clear width, clear height
# Halls (plan metres). pts: centre-line corners, r: smoothing radius, w/h: clear width/height, airlocks: metres along the line (negative: before the end), requires: rooms that must be placed.
# into=(parent, side, (x, y)): a branch that opens into the wall of another hall at that plan point (side +1 left of the parent's direction, -1 right); the branch's last point lies on the parent's inner wall plane.
# Sources: plan v7 links (design/facility-layout/generate_plan.py SP and outer ring), each room's contracts/interface.json and CONNECTIONS.md; see COMBINED_MAP.md "Rooms 7 to 10, connections".
LINKS = {
    'turbine-room': dict(pts=[(0.0, 14.5), (0.0, 17.0)], r=1.0, airlocks=[1.4]),
    'electrical-room': dict(pts=[(8.0, 8.0), (19.75, 19.75), (19.75, 26.0)], r=10.0, airlocks=[-1.6]),
    # reactor to waste: WS_RECEIVING threshold (contracts/waste-storage CONNECTIONS.md); corner moved to (15,-24) so the hall has a straight run for the junction below
    'waste-storage': dict(pts=[(11.15, -11.15), (14.0, -14.0), (15.0, -24.0), (27.68, -24.0)], r=6.0, airlocks=[-1.2]),
    'cooling-plant': dict(pts=[(-14.5, 0.0), (-22.0, 0.0), (-30.0, -19.0), (-44.1, -19.0)], r=8.0, airlocks=[None]),
    # turbine D02 (far end) north, east along y 53 past the electrical room, down the east side (the plan's outer ring east arm direction) and west into the waste hall: turbine - electrical - waste
    'bridge': dict(pts=[(0.0, 42.2), (0.0, 53.0), (34.0, 53.0), (34.0, -12.0), (22.9, -12.0), (22.9, -21.5)], r=4.5, airlocks=[1.8], into=('waste-storage', 1, (22.9, -24.0)),
                   requires=('turbine-room', 'electrical-room', 'waste-storage')),
    # electrical D02_Waste (north door, 2.4 x 2.7, electrical contracts/CONNECTIONS.md) up to the bridge
    'electrical-spur': dict(pts=[(19.75, 42.9), (19.75, 50.5)], r=1.0, airlocks=[2.4], into=('bridge', -1, (19.75, 53.0)), requires=('turbine-room', 'electrical-room', 'waste-storage'), zone='electrical-room'),
    # fuel corridor S01_PLANT (interface.json: centre (-5.4, 17.4), outward -X, 2.0 x 2.5, plant_header cell height 3.0, route (0,17.4)-(-5.4,17.4)) to the cooling hall
    # east trunk: hall east door (front end, stub to x 36, 2.4 m clear, DESIGN.md "Hall east end to east trunk 2.4 m; the trunk splits just outside: dock one way, waste the other") east along y -54, then the plan's outer-ring east arm (x 56) north to y 39.45 and west into the bridge's east leg
    'east-trunk': dict(pts=[(36.0, -54.0), (56.0, -54.0), (56.0, 39.45), (36.5, 39.45)], r=4.5, airlocks=[1.5], into=('bridge', 1, (34.0, 39.45)), requires=('compliance-dock', 'waste-storage', 'electrical-room'), zone='trunk'),
    # compliance dock facility_entry P1 (plan (60,-79); sill face x 57.9): plan v7 dock link (56,-54)-(56,-79)-(60,-79), moved to x 48 so the corner has room for a 4.5 m radius
    'dock-link': dict(pts=[(48.0, -56.5), (48.0, -79.0), (57.9, -79.0)], r=4.5, airlocks=[-0.3], into=('east-trunk', -1, (48.0, -54.0)), requires=('compliance-dock', 'waste-storage', 'electrical-room'), zone='dock'),
    # waste WS_PERSONNEL (module (6, 2.4), outward +X = plan south, 1.2 x 2.3 m; plan point (30.72, -30.3)) from the trunk: plan v7 "hall right -> waste" (32,-48)-(32,-38)
    'waste-personnel': dict(pts=[(42.0, -51.5), (42.0, -36.5), (30.72, -36.5), (30.72, -30.3)], r=3.0, w=2.4, h=3.0, airlocks=[], into=('east-trunk', 1, (42.0, -54.0)), requires=('compliance-dock', 'waste-storage', 'electrical-room'), zone='service'),
    # waste WS_DISPATCH (module (0, 18), outward +Y = plan east, 2.4 x 2.8 m; plan point (46.64, -24)) to the east arm
    'waste-dispatch': dict(pts=[(46.64, -24.0), (53.5, -24.0)], r=1.0, w=2.4, h=3.0, airlocks=[], into=('east-trunk', 1, (56.0, -24.0)), requires=('compliance-dock', 'waste-storage', 'electrical-room'), zone='service'),
    # plan v7 outer ring west arm (-33.7,-49)-(-38,-49)-(-38,30)-(-7.4,30) with the yard-to-cooling passage (DESIGN.md: "Yard to cooling passage 2.4 m, north-west corner"; yard service door at plan (-46,-60.0)). Deviations: the passage joins the ring at y -49 instead of the refinery's
    # west wall (the refinery wall behind (-33.7,-49) is blocked by the crusher and acoustic enclosure, ray scan), and the ring crosses the reactor-cooling hall at (-38,-19) as a T pair instead of an unbuilt cooling east door
    # medical direct door (plan v7 (38.5,-71.7)-(38.5,-54)): door cut in the rear wall of medical's decon cell (plan x 37.3, y -72.33) east then north to the trunk
    'medical-direct': dict(pts=[(37.3, -72.33), (42.0, -72.33), (42.0, -56.5)], r=3.0, w=2.4, h=3.0, airlocks=[], into=('east-trunk', -1, (42.0, -54.0)), requires=('compliance-dock', 'waste-storage', 'electrical-room'), zone='service'),
    'ring-south': dict(pts=[(-46.0, -60.0), (-46.0, -49.0), (-38.0, -49.0), (-38.0, -21.5)], r=4.5, airlocks=[1.2], into=('cooling-plant', 1, (-38.0, -19.0)), requires=('cooling-plant',), zone='passage'),
    'ring-north': dict(pts=[(-38.0, -16.5), (-38.0, 30.8), (-4.25, 30.8)], r=4.5, airlocks=[-0.3], outof=('cooling-plant', -1, (-38.0, -19.0)), requires=('cooling-plant', 'turbine-room'), zone='ring'),
    # fuel corridor S01_PLANT (interface.json: centre (-5.4, 17.4), outward -X, 2.0 x 2.5, plant_header cell height 3.0; route (0,17.4)-(-5.4,17.4)) to the ring
    'fuel-service': dict(pts=[(-27.66, -26.2), (-35.5, -26.2)], r=1.0, w=2.4, h=3.0, airlocks=[], into=('ring-south', -1, (-38.0, -26.2)), requires=('fuel-corridor', 'cooling-plant'), zone='service'),
}

LINK_NAMES = {'electrical-spur': 'ELECTRICAL', 'bridge': 'TURBINE / BRIDGE', 'dock-link': 'COMPLIANCE DOCK', 'waste-personnel': 'WASTE (PERSONNEL)', 'waste-dispatch': 'WASTE (DISPATCH)',
              'medical-direct': 'MEDICAL', 'ring-south': 'YARD / FUEL CORRIDOR', 'ring-north': 'OUTER RING NORTH', 'fuel-service': 'FUEL CORRIDOR', 'east-trunk': 'EAST TRUNK', 'waste-storage': 'WASTE STORAGE', 'cooling-plant': 'COOLING PLANT'}

def zone_mats(zone_key):
    """Per-zone material set: the spawn wall plaster multiplied by the zone tint."""
    import reactor_links
    M, _ = spawn_assets()
    Mz = dict(M)
    Mz['wall'] = Mz['wall_t'] = reactor_links.tinted_copy(M['wall'], reactor_links.ZONES[zone_key]['tint'], 'HALL plaster ' + zone_key)
    return Mz

def spawn_props():
    if 'props' not in ASSETS:
        import reactor_links
        ASSETS['props'] = reactor_links.load_spawn_props(os.path.join(SRC, 'spawn-room', 'module.blend'))
    return ASSETS['props']

def add_reactor_links():
    import reactor_links
    M, air = spawn_assets(); props = spawn_props()
    root = bpy.context.scene.collection.children['COMBINED_MAP']
    active = {k: L for k, L in LINKS.items() if all(r in INCLUDED for r in L.get('requires', (k,)))}
    for _ in range(4):      # a branch needs its parent hall
        active = {k: L for k, L in active.items() if all(L[t][0] in active or L[t][0] in INCLUDED for t in ('into', 'outof') if t in L) and ('into' not in L or L['into'][0] in active or L['into'][0] in INCLUDED and L['into'][0] not in LINKS)}
    paths = {k: reactor_links.Path(reactor_links.fillet(L['pts'], L['r'])) for k, L in active.items()}
    openings = {k: [] for k in active}
    for k, L in active.items():
        for t in ('into', 'outof'):
            if t in L:
                par, sg, pt = L[t]
                if par in active:
                    c = paths[par].nearest(pt); wb = L.get('w', 5.0); openings[par].append((c - wb / 2, c + wb / 2, sg))
    jl = {k: [] for k in active}
    for k, L in active.items():
        for t in ('into', 'outof'):
            if t in L and L[t][0] in active:
                par, sg, pt = L[t]; jl[par].append((paths[par].nearest(pt), sg, LINK_NAMES.get(k, k.upper())))
    for key, L in active.items():
        coll = bpy.data.collections.new('CONNECTOR_reactor_to_' + key); root.children.link(coll)
        w, h = L.get('w', 5.0), L.get('h', 5.0); zone = L.get('zone', key)
        Mz = zone_mats(zone); props_ = props if w >= 3 else []
        path = reactor_links.hall(coll, 'CONNECTOR ' + key, paths[key].P, w, h, Mz, openings=openings[key])
        spos = [path.length - 2.4 if s is None else (path.length + s if s < 0 else s) for s in L['airlocks']]       # None: 2.4 m in front of the room door at the far end; negative: that many m before the end
        na = 0
        for s_ in spos:
            pos, d, _n = path.at(s_)
            na += reactor_links.airlock(coll, air, pos, d, w, h, Mz)
        pl = reactor_links.dress_hall(coll, path, zone, Mz, props_, h=h, w=w, airlock_s=spos, seed=sum(map(ord, key)) % 1000, openings=openings[key], jlabels=jl[key])
        if 'into' in L and L['into'][0] in active and h < active[L['into'][0]].get('h', 5.0):
            par, sg, pt = L['into']; pp = paths[par]; c = pp.nearest(pt); Hp = active[par].get('h', 5.0)
            reactor_links.lintel(coll, 'CONNECTOR lintel ' + key, pp, c - w / 2, c + w / 2, sg, active[par].get('w', 5.0) / 2, h, Hp, Mz)
        print('LINK', key, 'length %.1f m' % path.length, 'openings', [(round(a, 1), round(b, 1), sg) for a, b, sg in openings[key]], 'airlock objects', na, 'props', pl)

# Doors of the newly placed rooms that the plan does not connect to anything (found by ray audit: they opened onto empty night). Closed plates stand in until the room behind them is placed; named PLACEHOLDER_.
# name, room that must be included, (x0, x1), (y0, y1) plan metres, top z
DOOR_PLACEHOLDERS = [('PLACEHOLDER_turbine_D02_shutter', 'turbine-room', (-1.3, 1.3), (42.2, 42.3), 2.9),
                     ('PLACEHOLDER_electrical_D02_shutter', 'electrical-room', (18.45, 21.05), (42.9, 43.0), 2.9),
                     ('PLACEHOLDER_waste_dispatch_shutter', 'waste-storage', (46.64, 46.74), (-25.3, -22.7), 3.0)]

BRIDGED = {'PLACEHOLDER_turbine_D02_shutter': 'bridge', 'PLACEHOLDER_electrical_D02_shutter': 'electrical-spur', 'PLACEHOLDER_waste_dispatch_shutter': 'waste-dispatch'}   # doors that a link now connects

def add_door_placeholders():
    mat = bpy.data.materials.new('PLACEHOLDER_shutter_steel'); mat.use_nodes = True; b = mat.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.09, 0.1, 0.11, 1); b.inputs['Metallic'].default_value = 0.7; b.inputs['Roughness'].default_value = 0.5
    root = bpy.context.scene.collection.children['COMBINED_MAP']
    for name, room, xs, ys, top in DOOR_PLACEHOLDERS:
        if room in INCLUDED and not (name in BRIDGED and all(r in INCLUDED for r in LINKS[BRIDGED[name]].get('requires', (BRIDGED[name],)))): _box(root, name, xs, ys, (0.0, top), mat); print('PLACEHOLDER', name)

# Turbine west door for the outer ring: the turbine's west wall (two skins 'West wall' at module x -4.00 and -4.25, plinth and cable trunk) is cut 2.6 m wide at module y 13.8 (= plan y 30.8), the clear stretch found by ray scan (module y 12.0 to 15.6 had no equipment within 3 m of the wall)
TURBINE_CUTS = {'west_door': dict(ang=math.pi, ox=0.0, oy=13.8, hw=1.3, a0=3.55, a1=4.4, z0=0.0, z1=2.9, walls=('West wall', 'Concrete impact plinth', 'Control cable trunk'), rooms=('turbine-room', 'cooling-plant'))}

def patch_turbine(wrap, lib_coll, omit):
    import reactor_links
    objs = list(dict.fromkeys(lib_coll.all_objects))
    reactor_links.cut_hall(wrap, omit, objs, wm, INCLUDED, table={k: dict(v, oy=v['oy']) for k, v in TURBINE_CUTS.items()})

# Medical direct door (plan v7 "medical direct door" (38.5,-71.7)-(38.5,-54) to the east trunk). The medical module has a decon cell on its far side (module x 1.3 to 3.36, y 9.0 to 11.3, entered by the open 1.2 m "Decon doorway" in the rear wall at plan x 35.0) whose own rear wall (plan x 37.12 to 37.3) is solid piers and an extraction grille.
# That is the only stretch of the far wall with a clear straight lane from the room (ray scan with equipment counted: module x 1.4 to 3.0 from y 2 to the wall; the planned y -71.7 is module x 1.7), so the direct door is the decon cell's rear wall opened 1.2 m wide, 2.3 m high at module x 2.33 (plan y -72.33), with the wash fixtures
# in that 1.2 m stripe cleared. Local copies only; the module is unchanged.
MEDICAL_CUTS = {'east_door': dict(ang=math.pi / 2, ox=2.33, oy=0.0, hw=0.6, a0=11.0, a1=11.45, clear_a0=10.7, z0=0.0, z1=2.3, walls=('Decon rear wall',), rooms=('medical-reanimation', 'compliance-dock'))}

def patch_medical(wrap, lib_coll, omit):
    import reactor_links
    skin = [o for o in wrap.objects if o.library is not None]
    reactor_links.cut_hall(wrap, omit, list(dict.fromkeys(list(lib_coll.all_objects) + skin)), wm, INCLUDED, table=MEDICAL_CUTS)
    for o in skin:
        if o.name in omit: wrap.objects.unlink(o)       # the exterior skin pieces that were cut or are in the doorway: the cut copy (or nothing) stands in

PATCHES = {'front-end-area': lambda w, l, o: (open_portal_cap(w, l, o), clear_yard_for_shed(w, l, o), localise_evac_sign(w, l, o), totem_back_board(w, l, o), trim_spine_for_concourse(w, l, o)), 'mine': trim_mine_surface, 'reactor-room': patch_reactor, 'turbine-room': patch_turbine, 'medical-reanimation': patch_medical}
INCLUDED = set()

# Refinery: every root collection of the overhaul scene except the duplicate MODULE_refinery wrapper and the review cameras.
REFINERY_COLLECTIONS = ['REFINERY_ARCHITECTURE', 'REFINERY_MACHINES', 'REFINERY_CONVEYORS', 'REFINERY_UTILITIES', 'REFINERY_PROPS', 'REFINERY_LIGHTING',
                        'REFINERY_INTERACTION', 'REFINERY_VALIDATION', 'CS_SUPPORT_REQUIRED', 'CS_FLOOR_DRESSING', '03_CART_UNLOAD', 'CS_SURFACE_DRESSING',
                        'CS_WALL_DRESSING', 'CS_CEILING_DRESSING', 'REFINERY_STATE_PREVIEWS', 'REFINERY_COBALT_ARCHITECTURE', 'REFINERY_OVERHAUL']

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
    ('refinery', 'refinery/module_overhaul_R1.blend', REFINERY_COLLECTIONS, (-26.28, -52.2, 0.0), 90.0,
     'Rotated 90 degrees: freight door (module Door_Mine, west wall) goes to the south wall on the yard freight gate centre x -22.2; fuel door (Door_Reactor, east wall) to the north wall; '
     'personnel door (Door_Entry, south wall) to the east wall on the hall colonnade centre line y -54. East outer face lands on the colonnade end, x -18.9.'),
    ('medical-reanimation', 'medical-reanimation/module_overhaul_R2.blend', 'MODULE_medical-reanimation', (26.0, -70.0, 0.0), -90.0,
     'Local origin is the main entry threshold, inward +Y, door 2.2 m clear (contracts/interface.json). Cafeteria east door IF_PORTAL_CAF_E_MEDICAL is at plan (26, -70), 2.2 m (DESIGN.md), '
     'so threshold on threshold and rotation -90 degrees take inward +Y to plan +X (east). Room x 26.0 to 38.3 (outer), y -75.0 to -65.2.'),
    ('fuel-corridor', '../../fuel-corridor/production/checkpoints/fuel_full_F23ci.blend', 'MODULE_fuel-corridor', (-22.2, -43.6, 0.0), 0.0,
     'F23ci (reviewed 99; the AAA finish on top is unreviewed and not used). Local origin is port F01_REFINERY (centre (0,0,0), outward -Y, 2.6 m x 3.0 m), corridor runs +Y 24 m, no rotation. '
     'Placed on the refinery north fuel door: x -22.2 (door centre) and y -43.6 (refinery outer sill). Far end F02_REACTOR lands at plan (-8.0, -19.6), outward +Y.'),
    ('reactor-room', REACTOR_LIB, REACTOR_COLLECTIONS, (0.0, 0.0, 0.0), 0.0,
     'Candidate A (the refined hall; owner chose it 2026-10-11): module origin is the pool centre, hall floor 21.6 x 21.6 m (measured walls +-10.8), so the module origin goes on the plan origin '
     '(plan frame: origin at the reactor centre) with no rotation (owner chose no rotation and new south doors). The hall has no interface.json; its own doors are MAIN ACCESS (west), FUEL HANDLING (north) '
     'and a diagonal COOLING PLANT link in the south-east corner. New doors on the south wall come from the plan, see COMBINED_MAP.md for what was cut.'),
    ('turbine-room', 'turbine-room/module_overhaul_R1.blend', 'MODULE_turbine-room', (0.0, 17.0, 0.0), 0.0,
     'Plan v7 turbine, north of the reactor on the axis x = 0 (link 0,13.75 to 0,17). The owner asked for the AAA finish (branch claude/turbine-aaa, additive module_overhaul_R1.blend, unreviewed; it is the ORIGINAL turbine module with a dark material and lighting pass, not the v2 rebuild). '
     'Local D01 (reactor door, outward -Y, 2.4 x 2.7 m, open doorway) is at module x 0 and the end wall face at module y 0.0 (measured with rays), so the face goes on plan y 17.0 (the plan rectangle edge): origin y = 17.0, and D01 sits on the hall FUEL HANDLING stub axis. '
     'The room is not centred on its door (module x -4.52 to 10.25), so it spans plan x -4.52 to 10.25, not the drawn -7.4 to 7.4.'),
    ('electrical-room', 'electrical-room/overhaul/checkpoints/full-R11.blend', 'MODULE_electrical-room', (19.75, 26.25, 0.0), 0.0,
     'Plan v7 electrical, north-east (rectangle x 14 to 29.4, y 26 to 43.2). Reviewed overhaul R11. Local D01_Turbine (0,0,0), outward -Y, 2.4 x 2.7 m, exterior wall face at y -0.25 (contract and measurement); module x -5.75 to 8.55 puts the left edge on plan x 14 '
     'when origin x = 19.75, and the exterior face on plan y 26 when origin y = 26.25.'),
    ('waste-storage', 'waste-storage/module.blend', 'MODULE_waste-storage', (28.32, -24.0, 0.0), -90.0,
     'Plan v7 waste, east-south-east (rectangle x 28 to 42.9, y -38 to -17.2), link end (28,-24). Local origin is the WS_RECEIVING threshold (outward -Y, 3.0 x 3.2 m), exterior wall face at module y -0.32 (contract). Rotation -90 turns outward -Y to plan -X (west, towards the reactor), '
     'so the exterior face lands on plan x 28 (origin x 28.32) and the receiving door on plan y -24.'),
    ('cooling-plant', 'cooling-plant/module.blend', 'MODULE_cooling-plant', (-44.1, -19.0, 0.0), 90.0,
     'Plan v7 cooling, west-south-west (rectangle x -57 to -44.1, y -30 to -15), link end (-44.1,-19). Local origin CP-P01 (centre (0,0,0), +Y inward, 5 x 5 m); the module starts at y 0. Rotation +90 turns outward -Y to plan +X (east, towards the reactor), '
     'so the door face lands on plan x -44.1 and the door on plan y -19.'),
    ('compliance-dock', 'compliance-dock/module_overhaul_R1.blend', ['MODULE_compliance-dock', '09 Overhaul | full'], (60.0, -79.0, 0.0), -90.0,
     'Plan v7 compliance dock, hanging off the east trunk (rectangle x 60 to 78.7, y -87 to -71.2, "locked link" (56,-79) to (60,-79)). The AAA/overhaul module_overhaul_R1.blend (merged on main as #66 with the unreviewed finish #79; failed its recorded gate, C9 88.625 against 99). '
     'Local origin is the facility_entry threshold P1 (0,0,0), inward +Y, 2.4 x 2.6 m, aperture depth 0.28 (contracts/interface.json); room long axis (15.8 m to the sealed external arrival P2 at local y 15.8) runs along local Y, and plan v7 draws it 18.7 wide in x and 15.8 in y, so inward +Y goes to plan +X: rotation -90 degrees, threshold on plan (60,-79). '
     'Measured local bbox x -7.1 to 7.21, y -2.1 (sill) to 16.08, so the plan footprint is x 57.9 to 76.1, y -86.2 to -71.8.'),
]

CLIFF_TINT = {'saturation': 0.0, 'value': 3.6, 'warm': (0.82, 0.79, 0.68, 1.0)}   # measured from renders: mountain hsv ~(0.15, 0.10, 0.30), yard cliff was (0.55, 0.20, 0.13); grey it, brighten, warm it

def unify_cliff_rock():
    """The yard's cliff_face (front-end `rock` material, brown) butts against the mine mountain (R41 cliff rock, grey). Using the mountain's own material renders near black on the yard mesh, so the
    yard material is copied locally and a Hue/Saturation node is put between its colour texture and the shader to match the mountain's grey."""
    obj = bpy.data.objects.get('cliff_face')
    if not (obj and obj.library is None and obj.data.materials): return
    src = obj.data.materials[0]
    m = src.copy(); m.name = 'rock_matched_to_mountain'; nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    link = next((l for l in nt.links if l.to_node.name == bsdf.name and l.to_socket.name == 'Base Color'), None)
    if not link: print('CLIFF no base colour link'); return
    hs = nt.nodes.new('ShaderNodeHueSaturation'); hs.inputs['Saturation'].default_value = CLIFF_TINT['saturation']; hs.inputs['Value'].default_value = CLIFF_TINT['value']
    wm_ = nt.nodes.new('ShaderNodeMix'); wm_.data_type = 'RGBA'; wm_.blend_type = 'MULTIPLY'; wm_.inputs[0].default_value = 1.0; wm_.inputs[7].default_value = CLIFF_TINT['warm']
    nt.links.new(link.from_socket, hs.inputs['Color']); nt.links.new(hs.outputs['Color'], wm_.inputs[6]); nt.links.new(wm_.outputs[2], bsdf.inputs['Base Color'])   # replaces the old link into Base Color
    obj.data.materials[0] = m; print('CLIFF material tinted', CLIFF_TINT)

def fix_evac_sign_back():
    """sign_evac_gate is a 6-face box; only the face towards the yard has atlas UVs, the other five are collapsed to one pixel of the board's green, so from outside the gate it is a blank
    green slab. The face on the opposite side gets the same atlas rectangle, mapped by local x so the lettering reads from outside. (Mesh is already a local copy.)"""
    o = bpy.data.objects.get('sign_evac_gate')
    if not (o and o.library is None): return
    me = o.data; uv = me.uv_layers.active
    front = max(me.polygons, key=lambda p: max(uv.data[l].uv[0] for l in p.loop_indices) - min(uv.data[l].uv[0] for l in p.loop_indices))
    us = [uv.data[l].uv[0] for l in front.loop_indices]; vs = [uv.data[l].uv[1] for l in front.loop_indices]
    u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
    back = [p for p in me.polygons if p.normal.dot(front.normal) < -0.9]
    xs = [v.co.x for v in me.vertices]; zs = [v.co.z for v in me.vertices]; x0, x1, z0, z1 = min(xs), max(xs), min(zs), max(zs)
    for p in back:
        for l in p.loop_indices:
            c = me.vertices[me.loops[l].vertex_index].co
            uv.data[l].uv = (u0 + (c.x - x0) / (x1 - x0) * (u1 - u0), v0 + (c.z - z0) / (z1 - z0) * (v1 - v0))
    print('SIGN back face mapped:', len(back), 'face(s)')

# Exterior skins (additive, from sections/facility-assembly/exteriors/): the spawn room's own outside is flat saturated colour boxes, so its R05 exterior (167 objects, same footprint) is added.
# Unreviewed. key -> (file under SRC/../exteriors, collection)
EXTERIOR_SKINS = {'spawn-room': ('spawn-room/exterior-R05.blend', 'EXTERIOR_spawn-room'),
                  'refinery': ('refinery/exterior-R01.blend', 'EXTERIOR_refinery'),
                  'medical-reanimation': ('medical-reanimation/exterior-R04.blend', 'EXTERIOR_medical-reanimation')}

def add_exterior_skin(key, wrap, as_child=False):
    f, c = EXTERIOR_SKINS[key]
    with bpy.data.libraries.load(os.path.normpath(os.path.join(SRC, '..', 'exteriors', f)), link=True, relative=True) as (src, dst):
        if c not in src.collections: print('EXTERIOR missing', c); return
        dst.collections = [c]
    n = len(dst.collections[0].all_objects)
    if as_child: wrap.children.link(dst.collections[0])
    else:
        for o in dst.collections[0].all_objects: wrap.objects.link(o)
    print('EXTERIOR skin', key, n, 'objects')

def placeholder_fuel_shutter():
    """The refinery's fuel door (module Door_Reactor (7.51, -4.08), 2.6 m x 3.0 m per DOOR_BINDINGS fuel_refinery) leads to the fuel corridor, which is not placed yet and opens onto empty night. A plain closed
    shutter, named PLACEHOLDER_, stands in the doorway until the corridor is added and must be deleted then."""
    if 'refinery' not in INCLUDED or 'fuel-corridor' in INCLUDED: return
    mat = bpy.data.materials.new('PLACEHOLDER_shutter'); mat.diffuse_color = (0.09, 0.1, 0.11, 1)
    mat.use_nodes = True; b = mat.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (0.09, 0.1, 0.11, 1); b.inputs['Metallic'].default_value = 0.7; b.inputs['Roughness'].default_value = 0.5
    me = bpy.data.meshes.new('PLACEHOLDER_fuel_door_shutter'); me.materials.append(mat)
    cx, cy, w, d, h = -22.2, -44.69, 2.7, 0.14, 3.1
    v = [(cx + a * w / 2, cy + b_ * d / 2, c * h) for a in (-1, 1) for b_ in (-1, 1) for c in (0, 1)]
    me.from_pydata(v, [], [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]); me.update()
    o = bpy.data.objects.new('PLACEHOLDER_fuel_door_shutter', me); bpy.context.scene.collection.children['COMBINED_MAP'].objects.link(o)
    print('PLACEHOLDER fuel door shutter added')

SCENE_LIGHT = {'world_color': (0.045, 0.055, 0.09), 'world_strength': 1.0, 'sun_energy': 1.6, 'sun_color': (0.62, 0.72, 1.0), 'sun_rot_deg': (52.0, 0.0, 38.0)}

def add_scene_lighting():
    """The combined scene had no world and no sun of its own, so every exterior rendered near black. A cold dusk matching the mine's mood: dim blue sky and a moon-strength sun, set once for the whole map."""
    sc = bpy.context.scene; L = SCENE_LIGHT
    w = bpy.data.worlds.new('COMBINED dusk'); w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = L['world_color'] + (1.0,); bg.inputs['Strength'].default_value = L['world_strength']; sc.world = w
    ld = bpy.data.lights.new('COMBINED moon', 'SUN'); ld.energy = L['sun_energy']; ld.color = L['sun_color']; ld.angle = math.radians(1.5)
    o = bpy.data.objects.new('COMBINED moon', ld); o.rotation_euler = tuple(math.radians(a) for a in L['sun_rot_deg'])
    sc.collection.children['COMBINED_MAP'].objects.link(o)
    sc.view_settings.view_transform = 'Khronos PBR Neutral'; sc.view_settings.exposure = 0.5
    print('LIGHT dusk world and moon added')

def build(through, output):
    keys = [r[0] for r in ROOMS]
    INCLUDED.update(keys[:keys.index(through) + 1] if through in keys else ())
    if through not in keys: raise SystemExit(f'unknown room {through}; choose from {keys}')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; sc.name = 'COMBINED_MAP'
    root = bpy.data.collections.new('COMBINED_MAP'); sc.collection.children.link(root)
    for key, lib, coll, loc, rz, note in ROOMS[:keys.index(through) + 1]:
        path = os.path.join(SRC, lib)
        colls = [coll] if isinstance(coll, str) else list(coll)
        with bpy.data.libraries.load(path, link=True, relative=True) as (src, dst):
            for c in colls:
                if c not in src.collections: raise SystemExit(f'{lib} has no collection {c}')
            dst.collections = colls
        loaded = list(dst.collections)
        lib_coll = loaded[0]; omit = set(OMIT.get(key, ()))
        if omit or key in PATCHES:
            # membership wrapper: the room's objects are linked individually into a local collection, minus the omitted doorway closures.
            # Linked objects cannot be re-parented, so the wrapper itself is instanced at the placement transform (the source module is not edited).
            wrap = bpy.data.collections.new('ROOM_' + key + '_members'); kept = left = 0
            if key in EXTERIOR_SKINS: add_exterior_skin(key, wrap)        # skin first so patches can cut it too
            if key in PATCHES: PATCHES[key](wrap, lib_coll, omit)
            for o in dict.fromkeys(o for c in loaded for o in c.all_objects):
                if o.name in omit: left += 1; continue
                if o.name in wrap.objects: continue
                wrap.objects.link(o); kept += 1
            inst = bpy.data.objects.new('ROOM_' + key, None); inst.instance_type = 'COLLECTION'; inst.instance_collection = wrap
            inst.location = loc; inst.rotation_euler = (0, 0, math.radians(rz)); inst['source'] = lib; inst['note'] = note
            root.objects.link(inst)
            print('WRAPPER', key, 'objects', kept, 'omitted', left)
        else:
            if len(loaded) > 1 or key in EXTERIOR_SKINS:
                lib_coll = bpy.data.collections.new('ROOM_' + key + '_members')
                for c in loaded: lib_coll.children.link(c)
                if key in EXTERIOR_SKINS: add_exterior_skin(key, lib_coll, as_child=True)
            inst = bpy.data.objects.new('ROOM_' + key, None); inst.instance_type = 'COLLECTION'; inst.instance_collection = lib_coll
            inst.location = loc; inst.rotation_euler = (0, 0, math.radians(rz)); inst['source'] = lib; inst['note'] = note
            root.objects.link(inst)
    unify_cliff_rock()
    fix_evac_sign_back()
    add_reactor_concourse()
    add_reactor_links()
    add_door_placeholders()
    add_scene_lighting()
    placeholder_fuel_shutter()
    bpy.ops.wm.save_as_mainfile(filepath=output, relative_remap=True)
    print('COMBINED', through, [r[0] for r in ROOMS[:keys.index(through) + 1]], '->', output)

if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    through = a[a.index('--through') + 1] if '--through' in a else ROOMS[0][0]
    out = a[a.index('--output') + 1] if '--output' in a else os.path.join(HERE, 'combined_map.blend')
    build(through, out)
