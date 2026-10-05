"""Asset workspace: pull every prototype out of a built front-end scene into one library file, tag triangle counts, render contact sheets.
Usage: blender -b <built .blend> -P make_library.py -- <outdir> [samples]
Writes <outdir>/asset_library.blend (objects in per-group collections, custom props tri_count / budget_class) and <outdir>/sheet_<group>.png.
The BUILDERS stay the source of truth (fe_assets_*.py); this file only collects and reviews their output."""
import bpy, sys, os, math, json
from mathutils import Vector
a = sys.argv[sys.argv.index('--') + 1:]
OUT = a[0]; SAMPLES = int(a[1]) if len(a) > 1 else 24
os.makedirs(OUT, exist_ok=True)
GROUPS = {
 'dining': ['chair_0', 'chair_1', 'chair_2', 'chair_3', 'table', 'table_set', 'booth', 'tray', 'tray_stack', 'plate_stack', 'cup_stack', 'mug', 'bottle', 'bread_basket', 'cutlery_bin', 'sanitiser'],
 'serving': ['kitchen_block', 'serving_counter', 'kiosk_v2', 'stanchion', 'tray_trolley', 'vending_0', 'vending_1', 'fridge_display', 'water_cooler', 'microwave_bench', 'recycling', 'totem'],
 'lounge': ['sofa3', 'sofa2', 'armchair', 'coffee_table', 'side_table', 'bookcase_0', 'floor_lamp', 'table_lamp', 'cushion', 'plant_leafy_1', 'plant_spiky_3', 'planter_long', 'tv', 'coat_rack', 'wall_shelf_0', 'bulletin'],
 'game': ['arcade_basketball', 'foosball', 'dartboard', 'hoops', 'bean_bag', 'stool', 'bench', 'wall_clock', 'extinguisher', 'first_aid', 'pendant', 'ceiling_strip'],
 'doors': ['leaf_airlock', 'leaf_glazed', 'leaf_medical', 'leaf_staff', 'leaf_sliding', 'hall_W_door_leaf_1'],
 'hall_ops': ['lockers', 'locker_bench', 'ops_desk', 'office_chair', 'radio_dock', 'key_cabinet', 'ppe_dispenser', 'wet_cart'],
 'hall_work': ['workbench', 'tool_wall', 'tool_chest', 'bin_shelf', 'pallet_jack', 'parcels_0', 'roll_cage', 'staging_shelf'],
 'hall_safety': ['safety_station', 'hose_cabinet', 'blast_console', 'bollard_hall', 'cctv_dome', 'ceiling_smoke', 'ceiling_horn', 'ceiling_sprinkler'],
 'hall_shell': ['gantry_landing', 'gantry_stair', 'hall_cable_tray', 'hall_sprinkler_main'],
}
# triangle caps per asset class (owner-approved: hero up to ~15k, small props ~2k)
HERO = {'kitchen_block', 'fridge_display', 'serving_counter', 'foosball', 'arcade_basketball', 'vending_0', 'vending_1', 'sofa3', 'booth', 'bookcase_0', 'kiosk_v2', 'hoops', 'dartboard'}
HALL_CAP = {'lockers': 7000, 'gantry_landing': 7000, 'gantry_stair': 8000, 'hall_cable_tray': 4000, 'radio_dock': 3600, 'bin_shelf': 3500, 'tool_wall': 3500, 'ops_desk': 3500, 'ppe_dispenser': 3200, 'safety_station': 2500, 'parcels_0': 2500, 'workbench': 2000, 'pallet_jack': 1600, 'staging_shelf': 1600, 'office_chair': 1500, 'roll_cage': 1500}
CAP = lambda n: HALL_CAP[n] if n in HALL_CAP else 3000 if n == 'bulletin' else 2500 if n == 'recycling' else 15000 if n in HERO else 4000 if n.startswith(('sofa', 'armchair', 'leaf_', 'plant', 'table', 'chair', 'planter')) else 2000
dg = bpy.context.evaluated_depsgraph_get()
def tris(o):
    me = o.evaluated_get(dg).to_mesh(); t = sum(len(p.vertices) - 2 for p in me.polygons); o.evaluated_get(dg).to_mesh_clear(); return t
protos = {o.name.replace('proto_', ''): o for o in bpy.data.collections['PROTOTYPES'].objects}
report = {}
lib = bpy.data.collections.new('ASSET_LIBRARY'); bpy.context.scene.collection.children.link(lib)
for g, names in GROUPS.items():
    gc = bpy.data.collections.new('LIB_' + g); lib.children.link(gc)
    for n in names:
        o = protos.get(n)
        if o is None: continue
        t = tris(o); o['tri_count'] = t; o['tri_cap'] = CAP(n); o['group'] = g
        gc.objects.link(o); report[n] = {'group': g, 'tris': t, 'cap': CAP(n), 'ok': t <= CAP(n)}
json.dump(report, open(os.path.join(OUT, 'asset_report.json'), 'w'), indent=1)
print('LIBRARY over cap:', [n for n, r in report.items() if not r['ok']], 'total', sum(r['tris'] for r in report.values()))
# ---- contact sheets: one auto-framed 3/4 tile per asset, composed with PIL (labels carry triangle count vs cap)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(bpy.data.filepath)), 'pylib'))
for c in list(bpy.context.scene.collection.children):
    if c.name != 'ASSET_LIBRARY': bpy.context.scene.collection.children.unlink(c)
sc = bpy.context.scene
TW, TH = 640, 480
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = TW, TH
sc.view_settings.view_transform = 'AgX'; sc.view_settings.exposure = -0.2
w = bpy.data.worlds.new('studio'); w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.82, 0.84, 0.88, 1); bg.inputs[1].default_value = 0.8; sc.world = w
cam = bpy.data.objects.new('SheetCam', bpy.data.cameras.new('SheetCam')); sc.collection.objects.link(cam); sc.camera = cam; cam.data.lens = 45
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sc.collection.objects.link(sun); sun.data.energy = 3.2; sun.rotation_euler = (math.radians(50), 0, math.radians(35))
fill = bpy.data.objects.new('fill', bpy.data.lights.new('fill', 'SUN')); sc.collection.objects.link(fill); fill.data.energy = 1.0; fill.rotation_euler = (math.radians(70), 0, math.radians(-120))
fl = bpy.data.materials.new('floor'); fl.use_nodes = True; fb = fl.node_tree.nodes['Principled BSDF']; fb.inputs['Base Color'].default_value = (0.5, 0.5, 0.53, 1); fb.inputs['Roughness'].default_value = 0.85
floor = bpy.data.objects.new('floor', bpy.data.meshes.new('floor')); sc.collection.objects.link(floor); floor.data.materials.append(fl)
import bmesh
bm = bmesh.new(); [bm.verts.new(p) for p in ((-60, -60, -0.002), (60, -60, -0.002), (60, 60, -0.002), (-60, 60, -0.002))]; bm.faces.new(bm.verts); bm.to_mesh(floor.data); bm.free()
from PIL import Image, ImageDraw
tdir = os.path.join(OUT, 'tiles'); os.makedirs(tdir, exist_ok=True)
for g, names in GROUPS.items():
    tiles = []
    for n in names:
        o = protos.get(n)
        if o is None: continue
        for oo in protos.values(): oo.hide_render = oo is not o
        o.location = (0, 0, 0); bpy.context.view_layer.update()
        ws = [o.matrix_world @ Vector(c) for c in o.bound_box]
        mn = Vector((min(v[i] for v in ws) for i in range(3))); mx = Vector((max(v[i] for v in ws) for i in range(3))); c = (mn + mx) / 2; r = (mx - mn).length / 2
        d = Vector((1.0, 1.25, 0.7)).normalized() * (r * 3.0 + 0.5)
        cam.location = c + d; cam.rotation_euler = (c - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = os.path.join(tdir, n + '.png'); bpy.ops.render.render(write_still=True)
        tiles.append(n)
    cols = 4; rows = math.ceil(len(tiles) / cols)
    sheet = Image.new('RGB', (cols * TW, rows * TH), (255, 255, 255)); dr = ImageDraw.Draw(sheet)
    for i, n in enumerate(tiles):
        x, y = (i % cols) * TW, (i // cols) * TH; sheet.paste(Image.open(os.path.join(tdir, n + '.png')).convert('RGB'), (x, y))
        r_ = report[n]; dr.rectangle((x, y, x + 330, y + 26), fill=(20, 20, 24)); dr.text((x + 6, y + 7), f"{n}  {r_['tris']:,} / {r_['cap']:,} tris", fill=(255, 255, 255) if r_['ok'] else (255, 120, 90))
    sheet.save(os.path.join(OUT, f'sheet_{g}.png'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'asset_library.blend'), copy=True)
