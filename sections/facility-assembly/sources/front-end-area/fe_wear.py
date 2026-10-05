"""Light wear pass (about two years of use): baked decal atlas quads for scuffs, grime, streaks, floor traffic paths.
All decals are single-quad meshes with UVs into textures/wear_atlas.png (4 x 2 cells), named stain_* / streak_* so the lane check ignores them."""
from fe_common import *
from fe_yard3 import on_pad

CELLS = {'scuff': (0, 0), 'path': (1, 0), 'drip': (2, 0), 'corner': (3, 0), 'smudge': (0, 1), 'skid': (1, 1), 'blotch': (2, 1), 'dust': (3, 1)}
_dm = {}
def decal_mat(strength):
    k = round(strength, 2)
    if k in _dm: return _dm[k]
    m = bpy.data.materials.new(f'wear_decal_{k}'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); b = nt.nodes.new('ShaderNodeBsdfPrincipled'); t = nt.nodes.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(os.path.join(TEXDIR, 'wear_atlas.png'), check_existing=True); t.image.colorspace_settings.name = 'sRGB'; t.image.alpha_mode = 'STRAIGHT'; t.interpolation = 'Linear'
    b.inputs['Roughness'].default_value = 0.92
    if 'Specular IOR Level' in b.inputs: b.inputs['Specular IOR Level'].default_value = 0.1
    mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = k; mu.use_clamp = True
    nt.links.new(t.outputs['Color'], b.inputs['Base Color']); nt.links.new(t.outputs['Alpha'], mu.inputs[0]); nt.links.new(mu.outputs[0], b.inputs['Alpha'])
    nt.links.new(b.outputs[0], out.inputs['Surface'])
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass
    _dm[k] = m; return m

def decal(coll, name, cell, face, a, b, z0, z1, off, strength=0.5, flip=False):
    """face: 'F' floor (a,b = x0,x1 plan; z0,z1 = y0,y1 plan; off = z), 'N','S','E','W' = direction the decal faces on a wall.
    Walls: a,b = span along the wall (plan x for N/S, plan y for E/W); z0,z1 = heights; off = plan coordinate of the wall face."""
    cx, cy = CELLS[cell]; u0, u1 = cx / 4.0, (cx + 1) / 4.0; v0, v1 = 1 - (cy + 1) / 2.0, 1 - cy / 2.0
    if face == 'F': P = [(a, z0, off), (b, z0, off), (b, z1, off), (a, z1, off)]
    elif face == 'S': P = [(b, off, z0), (a, off, z0), (a, off, z1), (b, off, z1)]      # faces -y
    elif face == 'N': P = [(a, off, z0), (b, off, z0), (b, off, z1), (a, off, z1)]      # faces +y
    elif face == 'E': P = [(off, b, z0), (off, a, z0), (off, a, z1), (off, b, z1)]      # faces +x
    else: P = [(off, a, z0), (off, b, z0), (off, b, z1), (off, a, z1)]                  # faces -x
    uv = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    if flip: uv = [uv[1], uv[0], uv[3], uv[2]]
    me = bpy.data.meshes.new(name)
    vs = [(LX(p[0]), LY(p[1]), p[2]) for p in P] if face == 'F' else [(LX(p[0]), LY(p[1]), p[2]) for p in P]
    me.from_pydata(vs, [], [(0, 1, 2, 3)])
    uvl = me.uv_layers.new(name='UVMap')
    for i, l in enumerate(me.polygons[0].loop_indices): uvl.data[l].uv = uv[i]
    me.materials.append(decal_mat(strength))
    o = bpy.data.objects.new(name, me); coll.objects.link(o); o.visible_shadow = False
    return o

def _wall_wear(coll, walls, rnd, nm, scuffs=14, drips=3):
    """Dado scuffs, skirting dust and water streaks along interior wall faces. walls: (facing, wall face coordinate, (lo, hi) span, [excluded spans])."""
    for face, off, (lo, hi), excl in walls:
        def free(a, b): return not any(a < e1 and b > e0 for e0, e1 in excl)
        for k in range(scuffs):
            a = rnd.uniform(lo, hi - 1.2); w = rnd.uniform(0.6, 1.3)
            if free(a, a + w):
                doff = off + (0.08 if face in ('N', 'E') else -0.08)
                decal(coll, nm('dado_scuff'), 'scuff', face, a, a + w, 0.15, 0.15 + w * 0.6, doff, rnd.uniform(0.35, 0.6), flip=rnd.random() < 0.5)
        decal(coll, nm('skirt_dust'), 'dust', face, lo, hi, 0.12, 0.7, off + (0.08 if face in ('N', 'E') else -0.08), 0.55)
        for k in range(drips):
            a = rnd.uniform(lo, hi - 1.5); w = rnd.uniform(0.9, 1.6)
            if free(a, a + w): decal(coll, nm('streak_drip'), 'drip', face, a, a + w, 1.35, 2.7, off + (0.005 if face in ('N', 'E') else -0.005), rnd.uniform(0.3, 0.5), flip=rnd.random() < 0.5)

RAIL_X_ = -22.2

def build_wear(F, C):
    caf, hall = C['CAFETERIA'], C['HALL']
    rnd = random.Random(77); n = 0
    def nm(k): 
        nonlocal n; n += 1; return f'stain_{k}_{n}'
    # --- floor traffic paths (soft, long): airlock -> hall opening, yard door -> kitchen/queue, door to medical, queue in front of the counter
    decal(caf, nm('path_spine'), 'path', 'F', 6.4, 9.6, -79.6, -60.4, 0.004, 0.55)
    decal(caf, 'streak_path_yard', 'path', 'F', -7.6, 12.0, -71.2, -68.8, 0.004, 0.5)
    decal(caf, 'streak_path_med', 'path', 'F', 12.0, 25.6, -71.0, -68.9, 0.004, 0.45)
    decal(caf, 'streak_path_queue', 'path', 'F', 13.2, 24.5, -67.9, -65.7, 0.004, 0.55)
    decal(caf, 'streak_path_lounge', 'path', 'F', -3.0, 5.0, -75.0, -66.0, 0.004, 0.25)
    decal(hall, 'streak_path_hall', 'path', 'F', -3.6, 31.6, -55.0, -53.0, 0.004, 0.5)
    decal(hall, 'streak_path_hall_s', 'path', 'F', 6.4, 9.6, -59.8, -48.4, 0.004, 0.5)
    # scuffs and skids near doors, tables and the counter
    for (x0, x1, y0, y1) in ((5.5, 10.5, -79.8, -77.0), (-7.8, -5.0, -72.0, -68.0), (22.6, 25.8, -72.0, -68.0), (13.5, 20.0, -67.5, -66.0)):
        decal(caf, nm('skid'), 'skid', 'F', x0, x1, y0, y1, 0.005, 0.5, flip=rnd.random() < 0.5)
    for k in range(18):
        x = rnd.uniform(-6.5, 24.5); y = rnd.uniform(-78.5, -61.5); s = rnd.uniform(0.7, 1.4)
        decal(caf, nm('floor_scuff'), 'scuff', 'F', x - s, x + s, y - s * 0.6, y + s * 0.6, 0.005, rnd.uniform(0.3, 0.55), flip=rnd.random() < 0.5)
    for k in range(5):
        x = rnd.uniform(-2.0, 22.0); y = rnd.uniform(-78.0, -62.0); s = rnd.uniform(0.5, 0.9)
        decal(caf, nm('floor_blotch'), 'blotch', 'F', x - s, x + s, y - s, y + s, 0.0045, rnd.uniform(0.2, 0.35))
    # --- walls: (face direction, wall coordinate, span range, plaster-face offset); decals sit 1 cm proud of the finish
    walls = (('N', -79.80, (-7.4, 25.4), [(6.5, 9.5)]), ('S', -60.17, (-7.4, 25.4), [(4.5, 11.5)]), ('E', -7.82, (-79.4, -60.6), [(-71.7, -68.3)]), ('W', 25.82, (-79.4, -60.6), [(-71.4, -68.6)]))
    for face, off, (lo, hi), excl in walls:
        def free(a, b): return not any(a < e1 and b > e0 for e0, e1 in excl)
        # dado scuffs (low, on the navy paint, 2 cm proud of the dado)
        for k in range(14):
            a = rnd.uniform(lo, hi - 1.2); w = rnd.uniform(0.6, 1.3)
            if free(a, a + w):
                doff = off + (0.03 if face in ('N', 'E') else -0.03)
                decal(caf, nm('dado_scuff'), 'scuff', face, a, a + w, 0.15, 0.15 + w * 0.6, doff, rnd.uniform(0.35, 0.6), flip=rnd.random() < 0.5)
        # dust along the skirting and grime in floor corners
        a = lo; 
        decal(caf, nm('skirt_dust'), 'dust', face, lo, hi, 0.12, 0.7, off + (0.03 if face in ('N', 'E') else -0.03), 0.55)
        # water streaks from the rail down
        for k in range(3):
            a = rnd.uniform(lo, hi - 1.5); w = rnd.uniform(0.9, 1.6)
            if free(a, a + w): decal(caf, nm('streak_drip'), 'drip', face, a, a + w, 1.35, 2.7, off + (0.005 if face in ('N', 'E') else -0.005), rnd.uniform(0.3, 0.5), flip=rnd.random() < 0.5)
        # smudges beside doors, at hand height
    for (face, off, ya, yb) in (('E', -7.82, -72.4, -71.5), ('E', -7.82, -68.5, -67.6), ('W', 25.82, -72.2, -71.3), ('W', 25.82, -68.7, -67.8)):
        decal(caf, nm('smudge'), 'smudge', face, ya, yb, 0.95, 1.55, off + (0.006 if face == 'E' else -0.006), 0.6)
    for (xa, xb) in ((5.4, 6.4), (9.6, 10.6)): decal(caf, nm('smudge'), 'smudge', 'N', xa, xb, 0.95, 1.55, -79.8 + 0.006, 0.6)
    # corner grime where the floor meets the walls
    for (face, off, a, b) in (('N', -79.8, -7.8, -6.0), ('N', -79.8, 24.0, 25.8), ('S', -60.17, -7.8, -6.0), ('S', -60.17, 24.0, 25.8)):
        decal(caf, nm('corner'), 'corner', face, a, b, 0.12, 1.9, off + (0.005 if face == 'N' else -0.005), 0.55, flip=(a > 0))
    # window streaks below the high yard windows (west wall)
    for (a, b) in ((-78.8, -77.2), (-75.8, -74.2), (-72.8, -71.4), (-67.6, -66.0), (-64.6, -63.0), (-61.8, -61.0)):
        decal(caf, nm('streak_window'), 'drip', 'E', a, b, 1.7, 2.72, -7.82 + 0.005, 0.45)
    # hall: same treatment, lighter
    for k in range(10):
        x = rnd.uniform(-3.0, 30.0); s = rnd.uniform(0.6, 1.2)
        decal(hall, nm('hall_floor_scuff'), 'scuff', 'F', x - s, x + s, rnd.uniform(-58.5, -49.5) - 0.5, rnd.uniform(-58.5, -49.5) + 0.5, 0.005, rnd.uniform(0.3, 0.5))
    # hall: lanes, doors, dispatch bays and the blast door take the traffic
    for k in range(14):
        x = rnd.uniform(-3.0, 30.0); sx = rnd.uniform(0.7, 1.4)
        decal(hall, nm('hall_floor_scuff'), 'scuff', 'F', x - sx, x + sx, -55.2 + rnd.uniform(-0.3, 1.9) - 0.5, -55.2 + rnd.uniform(-0.3, 1.9) + 0.5, 0.005, rnd.uniform(0.3, 0.5), flip=rnd.random() < 0.5)
    for (x0, x1, y0, y1) in ((20.4, 30.0, -58.8, -56.4), (6.3, 9.7, -52.0, -48.6), (-3.8, -1.5, -56.6, -52.6), (28.4, 31.8, -56.0, -52.4)):
        decal(hall, nm('skid'), 'skid', 'F', x0, x1, y0, y1, 0.005, 0.5, flip=rnd.random() < 0.5)
    for (x, y) in ((24.0, -57.7), (3.0, -57.0), (-1.5, -50.8)):
        decal(hall, nm('hall_blotch'), 'blotch', 'F', x - 0.8, x + 0.8, y - 0.8, y + 0.8, 0.0045, 0.3)
    decal(hall, 'streak_path_hall_ns', 'path', 'F', 6.4, 9.6, -59.8, -48.4, 0.004, 0.55)
    _wall_wear(hall, (('N', -59.83, (-3.7, 31.7), [(4.9, 11.1)]), ('S', -48.17, (-3.7, 31.7), [(5.7, 10.3)]), ('E', -3.83, (-59.7, -48.3), [(-55.4, -52.6)]), ('W', 31.83, (-59.7, -48.3), [(-55.4, -52.6)])), rnd, nm, scuffs=12, drips=2)
    # yard: traffic along the mine lane and to the gates, vehicle bays, fuel, ore bays, dock approach
    yd = C['YARD']
    decal(yd, 'streak_path_dock', 'path', 'F', RAIL_X_ - 1.6, RAIL_X_ + 1.6, -67.2, -60.6, 0.004, 0.5)
    decal(yd, 'streak_path_porch', 'path', 'F', -12.0, -8.2, -76.0, -64.0, 0.004, 0.45)
    for (x0, x1, y0, y1) in ((-39.0, -30.0, -83.4, -77.9), (-42.8, -39.8, -83.2, -79.6), (-24.0, -18.0, -71.4, -69.0), (-34.0, -30.0, -72.0, -68.4), (-12.0, -9.0, -83.0, -78.0)):
        if on_pad((x0 + x1) / 2, (y0 + y1) / 2, -1.0): decal(yd, nm('skid'), 'skid', 'F', x0, x1, y0, y1, 0.005, 0.5, flip=rnd.random() < 0.5)
    for (x, y, r_) in ((-37.5, -80.6, 0.9), (-34.5, -80.6, 0.9), (-41.9, -80.6, 1.1), (-12.4, -80.9, 0.9), (-31.5, -81.2, 0.7), (-27.0, -67.5, 0.8), (-39.0, -62.8, 1.3)):
        if on_pad(x, y): decal(yd, nm('yard_blotch'), 'blotch', 'F', x - r_, x + r_, y - r_, y + r_, 0.0045, 0.4)
    for k in range(26):
        x = rnd.uniform(-46.5, -9.0); y = rnd.uniform(-83.0, -61.0); s_ = rnd.uniform(0.6, 1.2)
        if on_pad(x, y, -0.5): decal(yd, nm('yard_scuff'), 'scuff', 'F', x - s_, x + s_, y - s_ * 0.6, y + s_ * 0.6, 0.005, rnd.uniform(0.25, 0.5), flip=rnd.random() < 0.5)
        else: rnd.uniform(0, 1)
    # vertical wear: lamp room walls, container doors, bay walls
    decal(yd, nm('cabin_dust'), 'dust', 'N', -45.8, -39.8, 0.0, 0.9, -73.1 + 0.02, 0.6)
    decal(yd, nm('cabin_drip'), 'drip', 'N', -45.4, -44.0, 0.5, 2.55, -73.1 + 0.015, 0.55); decal(yd, nm('cabin_drip'), 'drip', 'N', -43.0, -41.6, 0.5, 2.55, -73.1 + 0.015, 0.5)
    for i, y in enumerate((-82.0, -79.1, -76.2)): decal(yd, nm('container_drip'), 'drip', 'W', y - 1.0, y + 1.0, 0.2, 2.5, -23.64 - 0.01, 0.5); decal(yd, nm('container_dust'), 'dust', 'W', y - 1.1, y + 1.1, 0.0, 0.8, -23.64 - 0.012, 0.55)
    for i, cx in enumerate((-41.9, -37.4, -32.9)): decal(yd, nm('bay_dust'), 'dust', 'S', cx - 1.4, cx + 1.4, 0.0, 0.9, -61.5 - 0.01, 0.6)
    # cafeteria exterior wall facing the yard: water streaks below the gutters
    for (a, b) in ((-79.0, -77.5), (-72.5, -71.0), (-67.5, -66.0), (-62.5, -61.2)): decal(yd, nm('streak_wall'), 'drip', 'W', a, b, 0.8, 4.0, -8.16 - 0.01, 0.35)
    return n
