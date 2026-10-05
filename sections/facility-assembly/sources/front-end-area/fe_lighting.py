"""Lighting and the fixed review cameras."""
from fe_common import *

CAMERAS = [
 ('CAF_01_ENTRY_NORTH', (8.0, -79.2, 1.65), (8.0, -60.0, 2.3), 20),
 ('CAF_02_DINING', (9.5, -78.8, 1.7), (21.5, -72.5, 1.0), 22),
 ('CAF_03_SERVING', (9.6, -70.9, 1.7), (20.5, -64.5, 1.4), 24),
 ('CAF_04_LOUNGE', (3.4, -71.2, 1.65), (-5.0, -77.0, 1.0), 20),
 ('CAF_05_GAME_CORNER', (3.0, -67.0, 1.65), (-5.0, -62.5, 1.2), 20),
 ('CAF_X1_AIRLOCK_DOOR', (8.0, -71.5, 1.65), (8.0, -80.0, 1.7), 20),
 ('CAF_X2_YARD_DOOR', (1.5, -70.0, 1.65), (-8.0, -70.0, 1.7), 20),
 ('CAF_X3_MEDICAL_DOOR', (18.5, -70.0, 1.65), (26.0, -70.0, 1.7), 20),
 ('HAL_01_FROM_CAFETERIA', (8.0, -59.4, 1.65), (8.0, -48.0, 2.3), 20),
 ('HAL_02_WEST_LOCKERS', (30.5, -54.0, 1.65), (-3.5, -55.5, 1.5), 20),
 ('HAL_03_LOCKERS_AND_PPE', (5.6, -54.2, 1.65), (-3.0, -58.2, 1.2), 22),
 ('HAL_04_DESK_AND_DISPATCH', (12.0, -53.4, 1.65), (24.0, -58.5, 1.3), 22),
 ('HAL_05_SAFETY_STATUS', (17.0, -54.6, 1.65), (16.0, -48.2, 2.1), 24),
 ('HAL_06_MAINTENANCE_BAY', (6.4, -54.6, 1.65), (-2.4, -50.4, 1.5), 22),
 ('HAL_X1_BLAST_DOOR', (8.0, -53.0, 1.65), (8.0, -48.0, 2.2), 24),
 ('HAL_X2_WEST_DOOR', (6.0, -54.0, 1.65), (-4.0, -54.0, 1.9), 20),
 ('HAL_X3_EAST_DOOR', (26.0, -54.0, 1.65), (32.0, -54.0, 1.9), 20),
 ('YRD_01_FROM_PORCH', (-8.8, -70.0, 1.65), (-48.0, -70.4, 2.2), 22),
 ('YRD_02_PORTAL', (-31.0, -70.6, 1.7), (-49.0, -70.0, 2.3), 24),
 ('YRD_03_ORE_BAYS', (-24.6, -69.3, 1.7), (-38.0, -62.0, 1.3), 22),
 ('YRD_04_VEHICLE_BAYS', (-28.5, -72.6, 1.7), (-36.0, -80.5, 1.2), 22),
 ('YRD_05_RAIL_DOCK', (-22.2, -68.5, 1.7), (-22.2, -60.5, 2.0), 22),
 ('YRD_06_STORE_AND_POWER', (-24.5, -71.2, 1.7), (-14.0, -79.0, 1.3), 22),
 ('YRD_07_AERIAL', (-24.0, -108.0, 52.0), (-28.0, -72.0, 0.0), 30),
 ('YRD_08_NIGHT_SKY', (-22.0, -70.5, 1.7), (-27.8, -103.1, 24.1), 18),
 ('YRD_X1_PORTAL_CLOSE', (-33.5, -71.3, 2.3), (-49.0, -70.0, 2.3), 28),
 ('YRD_X2_FREIGHT_GATE', (-22.2, -64.0, 1.7), (-22.2, -60.0, 2.4), 22),
 ('YRD_X3_EVAC_GATE', (-28.0, -76.0, 1.7), (-28.0, -84.0, 1.6), 20),
 # name, eye (plan x, y, z), target (plan x, y, z), lens
 ('FE_01_SPAWN_EXIT_NORTH', (8.0, -80.4, 1.65), (8.0, -30.0, 2.4), 20),
 ('FE_02_CAFE_DOOR_WEST_YARD', (-7.5, -70.0, 1.65), (-48.0, -70.4, 2.2), 22),
 ('FE_03_HALL_WEST_TO_EAST', (-3.4, -55.6, 1.7), (32.0, -53.0, 2.4), 20),
 ('FE_04_AERIAL', (14.0, -140.0, 66.0), (-6.0, -68.0, 0.0), 32),
 ('FE_05_CAFE_REVERSE_NORTH_TO_SOUTH', (8.0, -60.6, 1.65), (8.0, -85.0, 1.8), 20),
 ('FE_06_YARD_REVERSE_PORTAL_TO_EAST', (-47.4, -70.4, 1.65), (-8.0, -70.0, 2.6), 22),
 ('FE_07_HALL_SPINE_DOOR_BACK', (8.0, -48.6, 1.65), (8.0, -62.0, 2.2), 20),
 ('FE_09_MINE_FRONT', (-30.5, -70.9, 1.7), (-48.0, -70.0, 2.3), 24),
 ('FE_08_LOUNGE_CORNER', (7.4, -71.0, 1.7), (-5.0, -70.6, 1.1), 18),
]

def area(name, loc, size, energy, color, coll, rot=(0, 0, 0), shape='RECTANGLE', sy=None):
    l = bpy.data.lights.new(name, 'AREA'); l.energy = energy; l.color = color; l.shape = shape; l.size = size
    if sy: l.size_y = sy
    o = bpy.data.objects.new(name, l); o.location = (LX(loc[0]), LY(loc[1]), loc[2]); o.rotation_euler = rot; coll.objects.link(o); return o

def night_world(sc):
    """Night sky: star map (fe_sky) as the world, plus a faint horizon airglow so silhouettes read; the moon light is added by build_lighting."""
    import fe_sky
    w = bpy.data.worlds.new('FE_NIGHT'); sc.world = w; w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear(); Lk = nt.links.new
    def N(kind, **kw):
        n = nt.nodes.new(kind)
        for k, v in kw.items(): setattr(n, k, v)
        return n
    out = N('ShaderNodeOutputWorld'); bg = N('ShaderNodeBackground'); env = N('ShaderNodeTexEnvironment')
    env.image = bpy.data.images.load(fe_sky.ensure(), check_existing=True); env.image.colorspace_settings.name = 'sRGB'; env.interpolation = 'Cubic'
    tc = N('ShaderNodeTexCoord'); sep = N('ShaderNodeSeparateXYZ'); Lk(tc.outputs['Generated'], sep.inputs[0])
    mr = N('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -0.05; mr.inputs['From Max'].default_value = 0.5; mr.inputs['To Min'].default_value = 1.0; mr.inputs['To Max'].default_value = 0.0
    mr.clamp = True; Lk(sep.outputs['Z'], mr.inputs['Value'])
    glow = N('ShaderNodeMix', data_type='RGBA'); glow.inputs[6].default_value = (0.0016, 0.0024, 0.0050, 1); glow.inputs[7].default_value = (0.020, 0.026, 0.050, 1); Lk(mr.outputs[0], glow.inputs['Factor'])
    add = N('ShaderNodeMix', data_type='RGBA', blend_type='ADD'); add.inputs['Factor'].default_value = 1.0
    gain = N('ShaderNodeMix', data_type='RGBA', blend_type='MULTIPLY'); gain.inputs['Factor'].default_value = 1.0; gain.inputs[7].default_value = (fe_sky.GAIN,) * 3 + (1,)
    Lk(env.outputs['Color'], gain.inputs[6]); Lk(gain.outputs[2], add.inputs[6]); Lk(glow.outputs[2], add.inputs[7])
    Lk(add.outputs[2], bg.inputs['Color']); bg.inputs['Strength'].default_value = 1.0; Lk(bg.outputs[0], out.inputs['Surface'])
    return w

def point(name, loc, energy, color, coll, radius=0.08, plan=False):
    l = bpy.data.lights.new(name, 'POINT'); l.energy = energy; l.color = color; l.shadow_soft_size = radius
    o = bpy.data.objects.new(name, l); o.location = (loc if not plan else (LX(loc[0]), LY(loc[1]), loc[2])); coll.objects.link(o); return o

def spot(name, loc, rot_z, tilt, energy, color, coll, size=1.9, blend=0.7, radius=0.12):
    l = bpy.data.lights.new(name, 'SPOT'); l.energy = energy; l.color = color; l.spot_size = size; l.spot_blend = blend; l.shadow_soft_size = radius
    o = bpy.data.objects.new(name, l); o.location = loc
    o.rotation_euler = (Matrix.Rotation(rot_z, 3, 'Z') @ Matrix.Rotation(-tilt, 3, 'Y')).to_euler(); coll.objects.link(o); return o

def world_center(o):
    from mathutils import Vector as V
    cs = [o.matrix_world @ V(c) for c in o.bound_box]; return sum(cs, V()) / 8.0

def yard_night_lights(lc):
    """Real light for every yard fitting that is drawn lit: floodlight heads, canopy and portal lamps, gate beacons."""
    for o in [o for o in bpy.data.objects if o.name.startswith('pole_')]:
        loc = o.matrix_world @ Vector((0.8, 0.0, 6.12))
        spot(f'LIGHT_{o.name}', loc, o.rotation_euler.z, math.radians(38), 2600, (1.0, 0.92, 0.78), lc, size=math.radians(125), blend=0.8)
    for o in [o for o in bpy.data.objects if o.name.startswith('canopy_lamp')]:
        c = world_center(o); area_l = area(f'LIGHT_{o.name}', (0, 0, 0), 0.7, 380, (1.0, 0.82, 0.55), lc, sy=0.25); area_l.location = (c.x, c.y, c.z - 0.06)
    for o in [o for o in bpy.data.objects if o.name.startswith('portal_lamp_') or o.name.startswith('mouth_lamp_')]:
        c = world_center(o); point(f'LIGHT_{o.name}', (c.x, c.y, c.z - 0.05), 180, (1.0, 0.72, 0.40), lc, radius=0.1)
    for o in [o for o in bpy.data.objects if o.name.startswith('freight_beacon_')]:
        c = world_center(o); point(f'LIGHT_{o.name}', (c.x, c.y - 0.2, c.z), 90, (1.0, 0.55, 0.12), lc, radius=0.1)
    # cabin and gate lamps
    point('LIGHT_cabin_door', (LX(-42.8), LY(-73.4), 2.5), 160, (1.0, 0.85, 0.6), lc, radius=0.1)
    point('LIGHT_evac_gate', (LX(-28.0), LY(-83.2), 2.7), 140, (0.4, 1.0, 0.55), lc, radius=0.1)
    point('LIGHT_porch_door', (LX(-8.6), LY(-70.0), 3.0), 220, (1.0, 0.9, 0.72), lc, radius=0.1)

MOON_RES = None
def build_lighting(F, C):
    import fe_sky
    lc = C['LIGHTS']; sc = bpy.context.scene
    night_world(sc)
    md = Vector(tuple(fe_sky.moon_dir()))                                  # world direction toward the moon
    moon = bpy.data.lights.new('FE_MOON', 'SUN'); moon.energy = 0.55; moon.angle = math.radians(1.2); moon.color = (0.66, 0.77, 1.0)
    mo = bpy.data.objects.new('FE_MOON', moon); mo.rotation_euler = md.to_track_quat('Z', 'Y').to_euler(); lc.objects.link(mo)
    yard_night_lights(lc)
    area('KITCHEN_LIGHT_0', (17.0, -61.9, 2.9), 1.6, 220, (1.0, 0.95, 0.85), lc, sy=0.5); area('KITCHEN_LIGHT_1', (22.5, -61.9, 2.9), 1.6, 220, (1.0, 0.95, 0.85), lc, sy=0.5)
    # warm cafeteria fill under every ceiling fixture row, cool-white hall strips
    for i, x in enumerate((-2, 6, 14, 22)):
        for j, y in enumerate((-64.5, -70, -75.5)):
            area(f'CAF_FILL_{i}{j}', (x, y, 4.7), 1.6, 330, (1.0, 0.86, 0.68), lc, rot=(0, 0, 0), sy=0.6)
    for i, x in enumerate((0, 6, 12, 18, 24, 30)):
        for j, y in enumerate((-56.0, -52.0)):
            area(f'HALL_FILL_{i}{j}', (x, y, 5.4), 1.8, 260, (1.0, 0.94, 0.82), lc, sy=0.6)

def build_cameras(C):
    cc = C['CAMERAS']
    for name, eye, tgt, lens in CAMERAS:
        cam = bpy.data.cameras.new(name); cam.lens = lens; cam.clip_start = 0.05; cam.clip_end = 600
        o = bpy.data.objects.new(name, cam)
        o.location = (LX(eye[0]), LY(eye[1]), eye[2])
        d = Vector((LX(tgt[0]) - o.location.x, LY(tgt[1]) - o.location.y, tgt[2] - o.location.z))
        o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); cc.objects.link(o)

def hide_roofs(hide):
    for o in bpy.data.objects:
        if '_roof' in o.name or o.name.startswith('corner_column'): o.hide_render = hide
