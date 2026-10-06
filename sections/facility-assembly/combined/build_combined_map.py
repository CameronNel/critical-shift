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
# Front end: portal_void (a dark box closing the portal mouth, local x -66 to -61.4) and mountain_mass (an 8-vertex rock box,
# local x -98 to -64, y -16 to 30, z -1 to 9) are its stand-ins for the mountain and mine; the real mine module replaces both.
OMIT = {'front-end-area': ['portal_void', 'mountain_mass', 'cliff_face'], 'spawn-room': ['AIRLOCK_leaf_body', 'AIRLOCK_steel_face', 'AIRLOCK_structural_rib', 'AIRLOCK_structural_rib.001', 'AIRLOCK_leaf_body.001', 'AIRLOCK_steel_face.001', 'AIRLOCK_structural_rib.002', 'AIRLOCK_structural_rib.003', 'LIFE_airlock_gauge_case', 'LIFE_airlock_gauge_dial', 'LIFE_airlock_pressure_tick', 'LIFE_airlock_pressure_tick.001', 'LIFE_airlock_pressure_tick.002', 'LIFE_airlock_pressure_tick.003', 'LIFE_airlock_pressure_tick.004', 'LIFE_airlock_pressure_tick.005', 'LIFE_airlock_pressure_tick.006', 'LIFE_airlock_pressure_tick.007', 'LIFE_airlock_pressure_tick.008', 'LIFE_airlock_pressure_tick.009', 'LIFE_airlock_pressure_tick.010', 'LIFE_airlock_pressure_unit', 'SERVICE_end', 'SERVICE_end_washable_dado', 'SERVICE_end_coved_skirt', 'SERVICE_end_dado_cap']}

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

PATCHES = {'front-end-area': lambda w, l, o: (open_portal_cap(w, l, o), clear_yard_for_shed(w, l, o), localise_evac_sign(w, l, o)), 'mine': trim_mine_surface}
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
            if key in PATCHES: PATCHES[key](wrap, lib_coll, omit)
            for o in lib_coll.all_objects:
                if o.name in omit: left += 1; continue
                wrap.objects.link(o); kept += 1
            inst = bpy.data.objects.new('ROOM_' + key, None); inst.instance_type = 'COLLECTION'; inst.instance_collection = wrap
            inst.location = loc; inst.rotation_euler = (0, 0, math.radians(rz)); inst['source'] = lib; inst['note'] = note
            root.objects.link(inst)
            print('WRAPPER', key, 'objects', kept, 'omitted', left)
        else:
            if len(loaded) > 1:
                lib_coll = bpy.data.collections.new('ROOM_' + key + '_members')
                for c in loaded: lib_coll.children.link(c)
            inst = bpy.data.objects.new('ROOM_' + key, None); inst.instance_type = 'COLLECTION'; inst.instance_collection = lib_coll
            inst.location = loc; inst.rotation_euler = (0, 0, math.radians(rz)); inst['source'] = lib; inst['note'] = note
            root.objects.link(inst)
    unify_cliff_rock()
    fix_evac_sign_back()
    bpy.ops.wm.save_as_mainfile(filepath=output, relative_remap=True)
    print('COMBINED', through, [r[0] for r in ROOMS[:keys.index(through) + 1]], '->', output)

if __name__ == '__main__':
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    through = a[a.index('--through') + 1] if '--through' in a else ROOMS[0][0]
    out = a[a.index('--output') + 1] if '--output' in a else os.path.join(HERE, 'combined_map.blend')
    build(through, out)
