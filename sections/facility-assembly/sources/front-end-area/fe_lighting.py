"""Lighting and the fixed review cameras."""
from fe_common import *

CAMERAS = [
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
    sun = bpy.data.lights.new('FE_SUN', 'SUN'); sun.energy = 2.0; sun.angle = math.radians(2.5); sun.color = (1.0, 0.82, 0.62)
    so = bpy.data.objects.new('FE_SUN', sun); so.rotation_euler = (math.radians(66), 0, math.radians(-38)); lc.objects.link(so)
    w = bpy.data.worlds.new('FE_SKY'); sc.world = w; w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld'); bg = nt.nodes.new('ShaderNodeBackground')
    # smoggy overcast dusk: warm grey, no blue sky
    bg.inputs['Color'].default_value = (0.36, 0.32, 0.26, 1); bg.inputs['Strength'].default_value = 0.8
    nt.links.new(bg.outputs[0], out.inputs['Surface'])
    # soft fill lights inside (warm cafeteria, cool hall); emissive fixtures are added by the room builders
    dead_caf = {(0, 0), (0, 2), (1, 1), (2, 0), (2, 2), (3, 1)}
    for i, x in enumerate((-2, 6, 14, 22)):
        for j, y in enumerate((-64.5, -70, -75.5)):
            if (i, j) in dead_caf: continue
            area(f'CAF_FILL_{i}{j}', (x, y, 4.7), 1.6, 120, (0.95, 0.80, 0.55), lc, rot=(0, 0, 0), sy=0.6)
    for i, x in enumerate((0, 6, 12, 18, 24, 30)):
        if i in (1, 4): continue
        area(f'HALL_FILL_{i}', (x, -54, 5.7), 1.8, 55, (0.85, 0.88, 0.90), lc, sy=0.5)
    # sickly emergency red over the spine door and a failing cold tube above the hall middle
    area('HALL_EMERGENCY_RED', (8.0, -50.0, 3.8), 0.8, 90, (1.0, 0.12, 0.06), lc, sy=0.4)

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
