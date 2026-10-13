"""Meltdown flow for the compact map (2026-10-13): a second way out for every station, a sealable reactor chamber, and the signage and light to find both.
Called by build_compact_map.py (post_build) as `evacuation.build(root, L)`. Everything is new geometry in the collection EXTERIOR_evacuation (plan frame) or reuses the
front end's own yard assets (its LED pole mesh and pole spotlights, `apron_wet` paving, `paint` lane paint); no room source is edited.

Why (design/GAME_SPEC.md section 18): stage 5 of a meltdown brings "door failures, route collapse" and the objectives "seal chamber, restore blast door, recover
workers, escape". Before this pass every station north of the front end (turbine, electrical, condenser, cooling, waste) could only leave through the reactor hall
itself, and the reactor hall had one way out (the south tunnel). Now:
  * EAST: a paved, lit evacuation road along the east side. The doors that faced nothing open onto it as emergency exits: reactor SE stub, waste personnel and
    dispatch, electrical D02, turbine D02 (by a strip past the turbine's north end), and the spine's end door (by a short alley between the reactor and the dock).
    The road runs south to the hall's east door, behind the spine blast door, and so to the cafeteria, the yard and the yard evacuation gate.
  * WEST: a new emergency door in the cooling plant's rear wall and a paved path south, past the refinery's west face, to the yard's north service door.
  * SEAL: a sliding blast door pair at the reactor tunnel's concourse end (parked open), so the chamber can be sealed; the front end's spine blast door already seals the
    front block.
Emergency exits default closed in normal play and open in the evacuation state (validation/doors.json: emergency_exit, evac_state, leaf_regex). Unreviewed."""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix

FE_LIB = 'front_end_area.blend'
APRON_Z = (-0.3, 0.0)

# ---- paved areas (plan metres). Polygons are counter-clockwise; every one is checked against the plan cut in ASSEMBLY_REPORT.md section 3. ----
def east_polys(RY):
    return {
        # alley north of the spine end door and the yard between the reactor's SE stub, waste (south face y -21.2) and the dock (north wall y -33.29)
        'east yard': [(2.85, -33.22), (32.4, -33.22), (32.4, -21.25), (11.65, -21.25), (11.65, -26.36), (13.08, -27.79), (9.04, -31.83), (7.55, -30.37), (2.85, -30.37)],
        'east road': [(32.4, -50.5), (36.4, -50.5), (36.4, 25.0), (32.4, 25.0)],
        'north strip': [(-4.5, 21.0), (32.4, 21.0), (32.4, 25.0), (-4.5, 25.0)],
        'north strip west of D02': [(-4.5, 20.07), (-1.47, 20.07), (-1.47, 21.0), (-4.5, 21.0)],          # the turbine D02 porch keeps its own floor (x +-1.45, y 20.05..21.0)
        'north strip east of D02': [(1.47, 20.07), (32.4, 20.07), (32.4, 21.0), (1.47, 21.0)],
        'electrical D02 spur': [(27.3, 12.3), (32.4, 12.3), (32.4, 16.3), (27.3, 16.3)],
        'waste dispatch spur': [(30.32, -16.9), (32.4, -16.9), (32.4, -12.8), (30.32, -12.8)],
        'hall canopy apron': [(32.4, -57.0), (40.4, -57.0), (40.4, -50.5), (32.4, -50.5)],
    }

def west_polys(RY):
    return {
        'cooling exit apron': [(-38.5, -19.2), (-27.8, -19.2), (-27.8, -14.8), (-38.5, -14.8)],
        'west path': [(-38.5, -56.3), (-34.5, -56.3), (-34.5, -19.2), (-38.5, -19.2)],
        'yard service apron': [(-48.4, -60.05), (-34.5, -60.05), (-34.5, -56.3), (-48.4, -56.3)],
    }

# route centre lines for the painted arrows (towards safety) and the lamp posts: (points, arrow spacing)
def east_lines(RY):
    return [([(0.0, 22.6), (34.4, 22.6), (34.4, -50.0), (38.0, -52.5), (37.2, -54.0)], 7.0),
            ([(12.4, -31.2), (22.0, -27.5), (34.4, -27.5)], 6.0),
            ([(29.3, 14.3), (34.4, 14.3)], 0), ([(31.3, -14.84), (34.4, -14.84)], 0)]

def west_lines(RY):
    return [([(-29.0, -17.0), (-36.5, -17.0), (-36.5, -58.2), (-46.0, -58.2), (-46.0, -59.6)], 7.0)]

# pole positions (x, y, arm yaw degrees: the arm and the spot point that way)
def poles(RY):
    east = [(36.25, y, 180.0) for y in (22.0, 9.0, -4.0, -17.0, -30.0, -43.0)] + [(6.0, 24.85, -90.0), (20.0, 24.85, -90.0), (22.0, -33.1, 90.0), (40.25, -56.85, 135.0)]
    west = [(-38.35, y, 0.0) for y in (-19.0, -31.0, -43.0, -55.0)]
    return east + west

def fe_mat(name, fallback):
    m = next((m for m in bpy.data.materials if m.name == name and m.library and os.path.basename(m.library.filepath) == FE_LIB), None)
    return m or fallback

def mat(name, rgb, rough=0.6, metal=0.0, emit=0.0, emit_rgb=None):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = rgb + (1,); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit: b.inputs['Emission Color'].default_value = (emit_rgb or rgb) + (1,); b.inputs['Emission Strength'].default_value = emit
    return m

def slab(coll, name, poly, z, material):
    """A paved slab: the polygon extruded from z[0] to z[1], box-mapped UVs (reactor_links._uv)."""
    import reactor_links
    bm = bmesh.new(); vs = [bm.verts.new((x, y, z[1])) for x, y in poly]; f = bm.faces.new(vs)
    if f.normal.z < 0: f.normal_flip()
    r = bmesh.ops.extrude_face_region(bm, geom=[f]); bmesh.ops.translate(bm, vec=(0, 0, z[0] - z[1]), verts=[v for v in r['geom'] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); reactor_links._uv(bm)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(material)
    o = bpy.data.objects.new(name, me); coll.objects.link(o); return o

def flat_poly(coll, name, pts, z, material):
    bm = bmesh.new(); f = bm.faces.new([bm.verts.new((x, y, z)) for x, y in pts])
    if f.normal.z < 0: f.normal_flip()
    import reactor_links; reactor_links._uv(bm)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(material)
    o = bpy.data.objects.new(name, me); coll.objects.link(o); return o

def box(coll, name, xs, ys, zs, material):
    import build_combined_map as BM
    return BM._box(coll, name, xs, ys, zs, material)

def arrow(coll, name, p, ang, material, s=1.0):
    """Painted floor arrow at p pointing along ang (radians): shaft 0.36 x 1.1, head 1.0 x 0.8."""
    pts = [(-0.95, -0.18), (0.15, -0.18), (0.15, -0.5), (0.95, 0.0), (0.15, 0.5), (0.15, 0.18), (-0.95, 0.18)]
    c, s_ = math.cos(ang), math.sin(ang)
    return flat_poly(coll, name, [(p[0] + s * (c * x - s_ * y), p[1] + s * (s_ * x + c * y)) for x, y in pts], 0.004, material)

def text(coll, name, body, loc, rot, size, material, extrude=0.008):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.size = size; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.extrude = extrude; cu.materials.append(material)
    o = bpy.data.objects.new(name, cu); o.location = loc; o.rotation_euler = rot; coll.objects.link(o); return o

def exit_sign(coll, name, loc, facing_deg, M, label='EXIT'):
    """Lit emergency-exit sign: green box (0.62 x 0.06 x 0.24) with white text on the face, facing the given plan direction."""
    a = math.radians(facing_deg); n = Vector((math.cos(a), math.sin(a), 0.0)); t = Vector((-n.y, n.x, 0.0))
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.62, 0.06, 0.24), verts=bm.verts)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(a - math.pi / 2, 3, 'Z'), verts=bm.verts)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(M['exit green'])
    o = bpy.data.objects.new(name, me); o.location = loc; coll.objects.link(o)
    text(coll, name + ' text', label, Vector(loc) + n * 0.035, (math.pi / 2, 0, a + math.pi / 2), 0.15, M['exit white'], 0.004)

def bulkhead(coll, name, loc, facing_deg, M, energy=70.0):
    """Wall bulkhead lamp over an exit (outside): emissive lens and a warm point light 0.25 m in front of it."""
    a = math.radians(facing_deg); n = Vector((math.cos(a), math.sin(a), 0.0))
    box(coll, name + ' body', (loc[0] - 0.17, loc[0] + 0.17), (loc[1] - 0.17, loc[1] + 0.17), (loc[2] - 0.07, loc[2] + 0.07), M['steel'])
    box(coll, name + ' lens', (loc[0] - 0.13 + n.x * 0.1, loc[0] + 0.13 + n.x * 0.1), (loc[1] - 0.13 + n.y * 0.1, loc[1] + 0.13 + n.y * 0.1), (loc[2] - 0.05, loc[2] + 0.05), M['lamp'])
    ld = bpy.data.lights.new(name, 'POINT'); ld.energy = energy; ld.color = (1.0, 0.86, 0.66); ld.shadow_soft_size = 0.15
    lo = bpy.data.objects.new(name, ld); lo.location = Vector(loc) + n * 0.3 - Vector((0, 0, 0.1)); coll.objects.link(lo)

def lamp_pole(coll, name, x, y, yaw_deg, pole_obj, spot_obj):
    """The front end's yard LED pole (its mesh data, linked) and a copy of its 2600 W spotlight, aimed along the arm as in the yard."""
    yaw = math.radians(yaw_deg)
    if pole_obj is not None:
        p = bpy.data.objects.new(name, pole_obj.data); p.location = (x, y, 0.0); p.rotation_euler = (0, 0, yaw); coll.objects.link(p)
    else:
        box(coll, name, (x - 0.08, x + 0.08), (y - 0.08, y + 0.08), (0.0, 6.3), mat('EVAC pole steel', (0.2, 0.2, 0.2), 0.5, 0.8))
    if spot_obj is not None: ld = spot_obj.data.copy()
    else:
        ld = bpy.data.lights.new(name + ' light', 'SPOT'); ld.energy = 2600; ld.spot_size = 2.18; ld.spot_blend = 0.8; ld.color = (1.0, 0.92, 0.78)
    ld.name = name + ' light'
    lo = bpy.data.objects.new(name + ' light', ld); lo.location = (x + 0.8 * math.cos(yaw), y + 0.8 * math.sin(yaw), 6.12); lo.rotation_euler = (0, -0.663, yaw); coll.objects.link(lo)

def lane(coll, name, pts, material, M, spacing):
    """Painted centre arrows every `spacing` metres along a polyline (towards its last point)."""
    n = 0
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L = math.hypot(bx - ax, by - ay); ang = math.atan2(by - ay, bx - ax); k = 1
        if spacing <= 0: arrow(coll, '%s arrow %d' % (name, n), ((ax + bx) / 2, (ay + by) / 2), ang, material, 0.8); n += 1; continue
        while k * spacing < L - 1.0:
            f = k * spacing / L; arrow(coll, '%s arrow %d' % (name, n), (ax + (bx - ax) * f, ay + (by - ay) * f), ang, material); n += 1; k += 1
    return n

def edge_lines(coll, name, poly, material, w=0.1, inset=0.25):
    """Painted edge lines inset along the long sides of a rectangle polygon."""
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]; x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    if (x1 - x0) >= (y1 - y0):
        for k, y in enumerate((y0 + inset, y1 - inset)): box(coll, '%s line %d' % (name, k), (x0 + inset, x1 - inset), (y - w / 2, y + w / 2), (0.0, 0.004), material)
    else:
        for k, x in enumerate((x0 + inset, x1 - inset)): box(coll, '%s line %d' % (name, k), (x - w / 2, x + w / 2), (y0 + inset, y1 - inset), (0.0, 0.004), material)

def blast_door(coll, L, M):
    """Reactor blast door: two 2.75 x 4.98 x 0.3 m sliding leaves on the concourse side of the tunnel mouth (x -2.5..2.5), parked open behind the north wall faces,
    on a header track and a floor guide. Closed position: x -2.75..0.0 and 0.0..2.75 (0.25 m lap on each jamb)."""
    y1 = L.CONC['y1']; ya, yb = y1 - 0.42, y1 - 0.12; steel, panel, hazard = M['blast steel'], M['blast panel'], M['hazard']
    for side, (x0, x1) in (('west', (-5.38, -2.63)), ('east', (2.63, 5.38))):
        box(coll, 'BLAST reactor leaf %s' % side, (x0, x1), (ya, yb), (0.02, 4.98), panel)
        box(coll, 'BLAST reactor leaf %s edge' % side, (x1 - 0.12, x1) if side == 'west' else (x0, x0 + 0.12), (ya - 0.02, yb + 0.02), (0.02, 4.98), hazard)
        box(coll, 'BLAST reactor leaf %s kick band' % side, (x0, x1), (ya - 0.02, yb + 0.02), (0.1, 0.55), hazard)
        for k, z in enumerate((1.4, 2.8, 4.2)): box(coll, 'BLAST reactor leaf %s rib %d' % (side, k), (x0 + 0.1, x1 - 0.1), (ya - 0.05, ya), (z - 0.08, z + 0.08), steel)
    box(coll, 'BLAST reactor track', (-5.5, 5.6), (y1 - 0.5, y1 - 0.04), (5.02, 5.3), steel)
    box(coll, 'BLAST reactor floor guide', (-5.4, 5.4), (y1 - 0.34, y1 - 0.2), (0.0, 0.015), steel)

def cooling_exit(coll, L, M):
    """The new cooling rear-wall emergency door (wall cut by build_compact_map.patch_cooling): a steel leaf closed mid-wall, frames on both faces, push bar inside,
    and a threshold through the wall depth (the cut removes the wall's footing in the opening)."""
    y0, y1 = L.COOL_EXIT_Y; xo, xi = -27.8, -27.5; h = 2.35
    box(coll, 'EVAC cooling exit leaf', (-27.68, -27.62), (y0 + 0.02, y1 - 0.02), (0.02, h), M['door green'])
    box(coll, 'EVAC cooling exit leaf push bar', (-27.62, -27.56), (y0 + 0.2, y1 - 0.2), (1.0, 1.06), M['steel'])
    for face, (a, b) in (('outside', (xo - 0.06, xo)), ('inside', (xi, xi + 0.06))):
        box(coll, 'EVAC cooling exit frame %s south' % face, (a, b), (y0 - 0.1, y0), (0.0, h + 0.1), M['steel'])
        box(coll, 'EVAC cooling exit frame %s north' % face, (a, b), (y1, y1 + 0.1), (0.0, h + 0.1), M['steel'])
        box(coll, 'EVAC cooling exit frame %s head' % face, (a, b), (y0 - 0.1, y1 + 0.1), (h, h + 0.1), M['steel'])
    box(coll, 'EVAC cooling exit threshold', (xo - 0.05, xi + 0.05), (y0, y1), (-0.3, 0.0), M['steel'])

def build(root, L):
    """Returns {door id: leaf regex} for the emergency exits it equips."""
    coll = bpy.data.collections.new('EXTERIOR_evacuation'); root.children.link(coll)
    RY = L.RY
    apron = fe_mat('apron_wet', mat('EVAC apron concrete', (0.32, 0.32, 0.31), 0.8))
    paint = fe_mat('paint', mat('EVAC lane yellow', (0.75, 0.55, 0.05), 0.6))
    M = dict(steel=fe_mat('steel_charcoal', mat('EVAC steel', (0.15, 0.15, 0.16), 0.5, 0.8)), lamp=fe_mat('emissive', mat('EVAC lamp', (1.0, 0.9, 0.75), 0.4, 0.0, 6.0)),
             hazard=next((m for m in bpy.data.materials if m.name == 'RH hazard stripes' and m.library), None) or mat('EVAC hazard', (0.75, 0.55, 0.05), 0.6),
             **{'exit green': mat('EVAC exit sign green', (0.02, 0.55, 0.2), 0.4, 0.0, 4.0, (0.05, 1.0, 0.35)), 'exit white': mat('EVAC exit sign white', (0.95, 0.97, 0.95), 0.4, 0.0, 3.0),
                'route green': mat('EVAC route paint green', (0.04, 0.42, 0.16), 0.7), 'door green': mat('EVAC exit door green', (0.06, 0.32, 0.14), 0.55, 0.3),
                'blast steel': next((m for m in bpy.data.materials if m.name == 'RH refine structural steel' and m.library), None) or mat('EVAC blast steel', (0.25, 0.26, 0.27), 0.45, 0.85),
                'blast panel': next((m for m in bpy.data.materials if m.name == 'RH refine wall steel panel' and m.library), None) or mat('EVAC blast panel', (0.3, 0.32, 0.33), 0.5, 0.7)})
    n_slab = 0
    for name, poly in list(east_polys(RY).items()) + list(west_polys(RY).items()):
        slab(coll, 'EVAC apron ' + name, poly, APRON_Z, apron); n_slab += 1
        if len(poly) == 4: edge_lines(coll, 'EVAC ' + name, poly, paint)
    n_arrow = sum(lane(coll, 'EVAC east %d' % i, pts, M['route green'], M, sp) for i, (pts, sp) in enumerate(east_lines(RY)))
    n_arrow += sum(lane(coll, 'EVAC west %d' % i, pts, M['route green'], M, sp) for i, (pts, sp) in enumerate(west_lines(RY)))
    flat_text = lambda nm, body, loc, ang, size=0.55: text(coll, nm, body, (loc[0], loc[1], 0.006), (0, 0, ang), size, M['route green'], 0.0)
    # floor text read by someone walking towards safety (letters' tops point the way): south on the road and the west path, east across the yard
    flat_text('EVAC floor text east road', 'EVACUATION ROUTE', (34.4, 18.0), math.pi, 0.36)
    flat_text('EVAC floor text east yard', 'EVACUATION ROUTE', (24.0, -25.2), -math.pi / 2, 0.36)
    flat_text('EVAC floor text west path', 'EVACUATION ROUTE', (-36.5, -24.0), math.pi, 0.36)
    pole_src = next((o for o in bpy.data.objects if o.name == 'proto_led_pole' and o.library), None)
    spot_src = next((o for o in bpy.data.objects if o.name == 'LIGHT_pole_0' and o.library), None)
    for i, (x, y, yaw) in enumerate(poles(RY)): lamp_pole(coll, 'EVAC pole %02d' % i, x, y, yaw, pole_src, spot_src)
    # exit signs inside each emergency exit (facing into the room) and bulkhead lamps outside
    SIGNS = [('reactor SE stub', (10.8, -29.5, 4.62), 135.0), ('turbine D02', (0.0, 19.55, 3.62), -90.0), ('electrical D02', (26.55, 14.3, 2.98), 180.0),
             ('waste dispatch', (29.55, L.WASTE[1], 3.08), 180.0), ('waste personnel', (14.34, -20.75, 2.55), 90.0), ('cooling exit', (-27.4, sum(L.COOL_EXIT_Y) / 2, 2.62), 0.0),
             ('spine end', (8.0, L.SPINE_END - 0.3, 3.72), -90.0)]
    for nm, loc, f in SIGNS: exit_sign(coll, 'EVAC exit sign ' + nm, loc, f, M)
    BULK = [('reactor SE stub', (11.25, -29.95, 5.25), -45.0), ('turbine D02', (0.0, 20.12, 3.4), 90.0), ('electrical D02', (27.6, 14.3, 3.1), 0.0), ('waste dispatch', (30.45, L.WASTE[1], 3.25), 0.0),
            ('waste personnel', (14.34, -21.35, 2.65), -90.0), ('cooling exit', (-27.95, sum(L.COOL_EXIT_Y) / 2, 2.7), 180.0), ('spine end', (8.0, L.SPINE_END + 0.2, 3.85), 90.0),
            ('hall east canopy', (35.85, -54.0, 3.25), 0.0)]
    for nm, loc, f in BULK: bulkhead(coll, 'EVAC bulkhead ' + nm, loc, f, M)
    # wayfinding over the two re-entries into the front block
    sign_mat = mat('EVAC sign paint', (0.9, 0.85, 0.7), 0.5, 0.0, 1.2)
    board = fe_mat('steel_painted', M['steel'])
    box(coll, 'EVAC sign board hall', (36.0, 36.05), (-55.3, -52.7), (2.78, 3.4), board)                 # fascia under the canopy roof edge (roof z 3.4..3.6, x 32..36)
    text(coll, 'EVAC sign hall', 'HALL  >  YARD GATE', (36.08, -54.0, 3.09), (math.pi / 2, 0, math.pi / 2), 0.22, sign_mat)
    box(coll, 'EVAC sign board yard', (-47.35, -44.65), (-59.97, -59.93), (2.55, 2.95), board)            # on the service door's header (z 2.4..2.55)
    text(coll, 'EVAC sign yard', 'YARD  >  EVACUATION GATE', (-46.0, -59.9, 2.75), (math.pi / 2, 0, math.pi), 0.19, sign_mat)
    blast_door(coll, L, M); cooling_exit(coll, L, M)
    print('EVAC built: %d paved areas, %d arrows, %d poles, %d exit signs, %d bulkheads, blast door, cooling exit door' % (n_slab, n_arrow, len(poles(RY)), len(SIGNS), len(BULK)))
    return {'COOLING_W_EXIT': r'^EVAC cooling exit leaf'}

def collider_polys(RY):
    """Paved areas as floor proxies for assembly_colliders (role floor, zone 'evacuation route')."""
    return list(east_polys(RY).items()) + list(west_polys(RY).items())
