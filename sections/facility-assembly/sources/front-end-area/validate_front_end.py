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
    if o.type != 'MESH' or o.get('support') is None or o.get('support') in ('hanging', 'wall', 'overhead'): continue
    if any(a in o.name.lower() for a in ALLOW): continue
    bb = wbbox(o)
    if bb[5] - bb[4] < 0.25 or bb[4] > 2.0: continue
    for k, (x0, x1, y0, y1) in lanes.items():
        if bb[0] + 8 < x1 and bb[1] + 8 > x0 and bb[2] - 80 < y1 and bb[3] - 80 > y0: viol[k].append(o.name)
R['lane_violations'] = viol
R['lane_pass'] = all(len(v) == 0 for v in viol.values())
# Additive cafeteria passes register actual support anchors. Validate against the
# named evaluated support mesh, not merely a z=0 bounding-box convention.
if bpy.context.scene.get('cafeteria_revamp_supports'):
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parent/'cafeteria-revamp'))
    from support_coverage import missing_registrations, needs_registration
    from mathutils.bvhtree import BVHTree
    trees = {}
    contact_rows = []
    registrations = json.loads(bpy.context.scene['cafeteria_revamp_supports'])
    for row in registrations:
        ob = bpy.data.objects.get(row['object']); target = bpy.data.objects.get(row['target'])
        if ob is None or target is None:
            contact_rows.append({'object':row['object'], 'target':row['target'], 'pass':False, 'reason':'missing object or target'})
            continue
        if target.name not in trees:
            e = target.evaluated_get(dg); mesh = e.to_mesh()
            trees[target.name] = BVHTree.FromPolygons([target.matrix_world @ v.co for v in mesh.vertices], [list(p.vertices) for p in mesh.polygons])
            e.to_mesh_clear()
        tree = trees[target.name]; direction = Vector(row['direction']).normalized()
        for anchor in row['anchors']:
            p = ob.matrix_world @ Vector(anchor)
            hit, normal, index, distance = tree.ray_cast(p - direction * .10, direction, .25)
            if hit is None:
                contact_rows.append({'object':ob.name,'target':target.name,'anchor_world_m':list(p),'pass':False,'reason':'no support along expected direction'})
                continue
            gap = (hit-p).dot(direction); angle = math.degrees(math.acos(max(-1,min(1,normal.dot(-direction)))))
            passed = -.00201 <= gap <= .00501 and angle <= 12
            contact_rows.append({'object':ob.name,'target':target.name,'gap_m':round(gap,6),'angle_deg':round(angle,3),'pass':passed})
    imports = json.loads(bpy.context.scene['cafeteria_revamp_imports'])
    missing_images = [im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not __import__('os').path.isfile(bpy.path.abspath(im.filepath))]
    external_fonts = [f for f in bpy.data.fonts if f.filepath!='<builtin>']
    missing_fonts = [f.name for f in external_fonts if not f.packed_file and not __import__('os').path.isfile(bpy.path.abspath(f.filepath))]
    original_ports = json.loads(bpy.context.scene['cafeteria_revamp_interfaces'])
    actual_ports = [{'name':o.name,'matrix':[list(r) for r in o.matrix_world],'width':o.get('clear_width_m'),'height':o.get('clear_height_m')} for o in bpy.data.collections['INTERFACES'].objects]
    R['cafeteria_revamp'] = {
        'support_anchors_checked':len(contact_rows), 'support_anchor_pass':all(r['pass'] for r in contact_rows),
        'support_anchors':contact_rows, 'reimport_instances':imports,
        'reimport_bounds_pass':all(r['bounds_error_m']<.00001 for r in imports),
        'interfaces_unchanged':original_ports==actual_ports, 'missing_image_dependencies':missing_images,
        'all_file_images_packed':all(im.packed_file for im in bpy.data.images if im.source=='FILE'),
        'external_fonts_packed':all(f.packed_file for f in external_fonts), 'missing_font_dependencies':missing_fonts,
        'linked_libraries':[bpy.path.abspath(lib.filepath) for lib in bpy.data.libraries],
        'support_coverage':{'required_objects':sum(needs_registration(o) for o in bpy.data.collections['CAFETERIA'].all_objects),
                            'registered_objects':len({row['object'] for row in registrations}),
                            'missing':missing_registrations(bpy.data.collections['CAFETERIA'],registrations)},
        'door_poses':[{'name':o.name,'pose':o['door_pose'],'hinge_axis':o.get('hinge_axis')} for o in bpy.data.objects if o.get('door_pose')]
    }
    # Optional read-only comparison to the original module: geometry and transforms
    # of the unrelated yard, hall and shared shell must remain identical. Material
    # indices are excluded because the cafeteria face of its north wall is painted.
    argv = sys.argv[sys.argv.index('--')+1:]
    if '--original' in argv:
        import hashlib, array
        def geometry_signature(c):
            h=hashlib.sha256()
            for o in sorted(c.all_objects,key=lambda x:x.name):
                h.update(o.name.encode());h.update(o.type.encode())
                h.update(str((tuple(o.location),tuple(o.rotation_euler),tuple(o.scale))).encode())
                if o.type=='MESH':
                    a=array.array('f',[0])*(3*len(o.data.vertices));o.data.vertices.foreach_get('co',a);h.update(a.tobytes())
                    for p in o.data.polygons:h.update(array.array('I',p.vertices).tobytes())
            return h.hexdigest()
        names=('YARD','HALL','SHARED');before={n:geometry_signature(bpy.data.collections[n]) for n in names}
        source=argv[argv.index('--original')+1]
        with bpy.data.libraries.load(source,link=True) as (src,dst):dst.collections=list(names)
        original={n:geometry_signature(c) for n,c in zip(names,dst.collections)}
        R['cafeteria_revamp']['unrelated_geometry']={n:{'unchanged':before[n]==original[n],'candidate_sha256':before[n],'original_sha256':original[n]} for n in names}
json.dump(R, open(OUT, 'w'), indent=1)
print('VALIDATION', json.dumps({'tris': R['triangles'], 'interior_checked': rep['interior']['checked'], 'interior_gap_fail': len(rep['interior']['gap_fail']), 'interior_pen_fail': len(rep['interior']['pen_fail']), 'yard_checked': rep['yard']['checked'], 'yard_gap_fail': len(rep['yard']['gap_fail']), 'yard_pen_fail': len(rep['yard']['pen_fail']), 'lane_violations': {k: v for k, v in viol.items() if v}}))
if 'cafeteria_revamp' in R:
    detail=R['cafeteria_revamp']
    failures=[]
    if detail['support_coverage']['missing']:failures.append('support_registration_coverage')
    if not detail['support_anchor_pass']:failures.append('support_contact')
    if not R['lane_pass']:failures.append('furniture_lanes')
    if not R['triangles']['within_budget']:failures.append('triangle_budget')
    if not detail['interfaces_unchanged']:failures.append('interfaces')
    if not detail['reimport_bounds_pass']:failures.append('reimport_bounds')
    if detail['missing_image_dependencies'] or detail['missing_font_dependencies']:failures.append('dependencies')
    if failures:raise RuntimeError('Cafeteria validation failures: '+', '.join(failures))
