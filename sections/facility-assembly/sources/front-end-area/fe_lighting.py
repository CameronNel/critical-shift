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
        area(f'HALL_FILL_{i}', (x, -54, 5.7), 1.8, 330, (0.92, 0.94, 1.0), lc, sy=0.5)

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
