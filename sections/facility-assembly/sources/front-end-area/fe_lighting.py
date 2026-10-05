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

def build_lighting(F, C):
    lc = C['LIGHTS']; sc = bpy.context.scene
    sun = bpy.data.lights.new('FE_SUN', 'SUN'); sun.energy = 3.2; sun.angle = math.radians(1.6); sun.color = (1.0, 0.90, 0.74)
    so = bpy.data.objects.new('FE_SUN', sun); so.rotation_euler = (math.radians(52), 0, math.radians(-38)); lc.objects.link(so)
    w = bpy.data.worlds.new('FE_SKY'); sc.world = w; w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld'); bg = nt.nodes.new('ShaderNodeBackground'); sky = nt.nodes.new('ShaderNodeTexSky')
    sky.sky_type = 'MULTIPLE_SCATTERING'; sky.sun_elevation = math.radians(38); sky.sun_rotation = math.radians(142); sky.air_density = 1.0; sky.sun_disc = False
    bg.inputs['Strength'].default_value = 0.65
    nt.links.new(sky.outputs[0], bg.inputs['Color']); nt.links.new(bg.outputs[0], out.inputs['Surface'])
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
