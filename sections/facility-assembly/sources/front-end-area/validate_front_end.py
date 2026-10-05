"""Numeric checks for the front-end area module: triangles per zone, bounds, interface markers, support contact, clear lanes. Usage: blender -b file.blend -P validate_front_end.py -- out.json"""
import bpy, sys, json, math
from mathutils import Vector
OUT = sys.argv[sys.argv.index('--') + 1]
LX = lambda x: x - 8.0; LY = lambda y: y + 80.0
dg = bpy.context.evaluated_depsgraph_get()
def coll_objs(name):
    out = []
    def walk(c):
        out.extend(c.objects)
        for ch in c.children: walk(ch)
    walk(bpy.data.collections[name]); return out
def tris(objs):
    t = 0
    for o in objs:
        if o.type in ('MESH', 'CURVE', 'FONT') and not o.hide_render:
            e = o.evaluated_get(dg); m = e.to_mesh(); t += sum(len(p.vertices) - 2 for p in m.polygons); e.to_mesh_clear()
    return t
def wbbox(o):
    cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (min(c.x for c in cs), max(c.x for c in cs), min(c.y for c in cs), max(c.y for c in cs), min(c.z for c in cs), max(c.z for c in cs))
R = {'triangles': {}, 'budget_m': 800000}
for z in ('YARD', 'CAFETERIA', 'HALL', 'SHARED'): R['triangles'][z] = tris(coll_objs(z))
R['triangles']['TOTAL'] = sum(R['triangles'].values()); R['triangles']['within_budget'] = R['triangles']['TOTAL'] <= 800000
# bounds of the three zones (plan frame) vs declared footprints
decl = {'YARD': (-48, -8, -84, -60), 'CAFETERIA': (-8, 26, -80, -60), 'HALL': (-4, 32, -60, -48)}
R['bounds'] = {}
for z, (x0, x1, y0, y1) in decl.items():
    ob = [o for o in coll_objs(z) if o.type == 'MESH' and (z != 'YARD' or not o.name.startswith(('cliff', 'mountain', 'context', 'boulder', 'portal', 'mine_front', 'mouth')))]
    bb = [wbbox(o) for o in ob]
    mn = (min(b[0] for b in bb) + 8, min(b[2] for b in bb) - 80); mx = (max(b[1] for b in bb) + 8, max(b[3] for b in bb) - 80)
    R['bounds'][z] = {'declared': (x0, x1, y0, y1), 'actual_min_xy_plan': [round(v, 2) for v in mn], 'actual_max_xy_plan': [round(v, 2) for v in mx]}
# interface markers
R['interfaces'] = [{'name': o.name, 'plan_xy': [round(o.location.x + 8, 2), round(o.location.y - 80, 2)], 'clear_w': o['clear_width_m'], 'clear_h': o['clear_height_m']} for o in bpy.data.objects if o.name.startswith('IF_PORTAL_')]
# support contact
EXEMPT = ('heap', 'floor_broken', 'floor_debris', 'hanging', 'stack', 'table', 'wall')
strict = {'floor': [], 'n_checked': 0}; max_gap = 0.0; max_pen = 0.0
rep = {'interior': {'checked': 0, 'gap_fail': [], 'pen_fail': []}, 'yard': {'checked': 0, 'gap_fail': [], 'pen_fail': [], 'note': 'yard slabs are deliberately sunk/tilted up to 0.10 m, so yard contact uses 0.12 m'}}
exempt_counts = {}
for zname, key, g_tol, p_tol in (('CAFETERIA', 'interior', 0.005, 0.002), ('HALL', 'interior', 0.005, 0.002), ('YARD', 'yard', 0.12, 0.12)):
    for o in coll_objs(zname):
        s = o.get('support')
        if s is None: continue
        if s != 'floor':
            exempt_counts[s] = exempt_counts.get(s, 0) + 1; continue
        bb = wbbox(o); rep[key]['checked'] += 1
        if bb[4] > g_tol: rep[key]['gap_fail'].append([o.name, round(bb[4], 4)])
        if bb[4] < -p_tol: rep[key]['pen_fail'].append([o.name, round(bb[4], 4)])
R['support_contact'] = rep; R['support_exempt_by_kind'] = exempt_counts
# clear lanes: no prop taller than 0.25 m inside the lane rectangles (plan frame)
lanes = {'reactor_axis_hall_x6.8-9.2': (6.8, 9.2, -60.0, -48.0), 'reactor_axis_cafe_x6.8-9.2': (6.8, 9.2, -80.0, -60.0), 'hall_door_line_y-55.3--52.7': (-4.0, 32.0, -55.3, -52.7),
         'cafe_west_door_lane_y-71.2--68.8': (-8.0, 8.0, -71.2, -68.8), 'cafe_east_door_lane': (8.0, 26.0, -71.1, -68.9), 'mine_axis_lane_y-71.3--68.7': (-48.0, -8.0, -71.3, -68.7)}
ALLOW = ('rail', 'ballast', 'cart', 'lane_', 'crack', 'stain', 'puddle', 'pothole', 'slab', 'shard', 'earth', 'yard_base', 'litter', 'debris', 'tiles', 'rug', 'oche', 'cliff', 'portal', 'mouth', 'mine_front', 'kerb', 'rail_crossing', 'sign', 'joint', 'drain', 'floor', 'streak', 'wall', 'seg', 'frame', 'context', 'canopy', 'porch', 'door_leaf')
viol = {k: [] for k in lanes}
for o in bpy.data.objects:
    if o.type != 'MESH' or o.get('support') is None or o.get('support') in ('hanging', 'wall'): continue
    if any(a in o.name.lower() for a in ALLOW): continue
    bb = wbbox(o)
    if bb[5] - bb[4] < 0.25 or bb[4] > 2.0: continue
    for k, (x0, x1, y0, y1) in lanes.items():
        if bb[0] + 8 < x1 and bb[1] + 8 > x0 and bb[2] - 80 < y1 and bb[3] - 80 > y0: viol[k].append(o.name)
R['lane_violations'] = viol
R['lane_pass'] = all(len(v) == 0 for v in viol.values())
json.dump(R, open(OUT, 'w'), indent=1)
print('VALIDATION', json.dumps({'tris': R['triangles'], 'interior_checked': rep['interior']['checked'], 'interior_gap_fail': len(rep['interior']['gap_fail']), 'interior_pen_fail': len(rep['interior']['pen_fail']), 'yard_checked': rep['yard']['checked'], 'yard_gap_fail': len(rep['yard']['gap_fail']), 'yard_pen_fail': len(rep['yard']['pen_fail']), 'lane_violations': {k: v for k, v in viol.items() if v}}))
