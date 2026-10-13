"""Static performance measurements of the built map (no frame rate: nothing here runs the game). Run on a built scene:

    blender --background combined_map.blend --python perf_report.py -- [validation/perf_report.json]

Per top-level owner (a room instance or a connector collection):
  triangles     evaluated (modifiers applied, instances counted), what a renderer would draw if nothing were culled
  objects       renderable object instances;  meshes: distinct mesh datablocks behind them (re-use = instancing already present in the source)
  submeshes     sum over instances of the materials actually used by their faces: the draw-call count before any batching or instancing (Unity: one per renderer submesh)
  lights        by type, shadow casters counted separately
  textures      distinct images and their uncompressed RGBA8 memory with mips (w * h * 4 * 4/3)
Then: the repository's only budget numbers (400k triangles per room is the flag in DESIGN.md / AGENTS.md, 800k for the front end), the heaviest single meshes
(LOD candidates), meshes repeated under different datablocks (instancing candidates), and a portal graph from validation/doors.json: what each room can see through
its open doors (own + neighbours), the worst-case visible set used for the streaming proposal."""
import bpy, sys, os, json, math
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
out = a[0] if a else os.path.join(HERE, 'validation', 'perf_report.json')
dg = bpy.context.evaluated_depsgraph_get()
R = defaultdict(lambda: dict(triangles=0, objects=0, meshes=set(), submeshes=0, materials=set(), lights=defaultdict(int), shadow_lights=0, images=set()))
mesh_cache = {}; heavy = []; shape = defaultdict(set)

def mats_used(ob):
    key = (ob.original.session_uid, ob.data.session_uid if ob.data else 0)
    if key in mesh_cache: return mesh_cache[key]
    try: me = ob.to_mesh()
    except Exception: me = None
    if me is None: mesh_cache[key] = (0, [], None); return mesh_cache[key]
    me.calc_loop_triangles(); n = len(me.loop_triangles)
    idx = sorted({p.material_index for p in me.polygons}) if len(me.polygons) < 400000 else list(range(len(ob.material_slots)))
    slots = ob.material_slots; used = [slots[i].material for i in idx if i < len(slots) and slots[i].material] or ([None] if n else [])
    sig = (len(me.vertices), n, tuple(round(d, 2) for d in ob.original.dimensions)) if n > 2000 else None
    ob.to_mesh_clear(); mesh_cache[key] = (n, used, sig); return mesh_cache[key]

def images_of(mat, acc):
    if mat is None or not mat.use_nodes or not mat.node_tree: return
    for nd in mat.node_tree.nodes:
        if nd.type == 'TEX_IMAGE' and nd.image: acc.add(nd.image)
        elif nd.type == 'GROUP' and nd.node_tree:
            for m2 in nd.node_tree.nodes:
                if m2.type == 'TEX_IMAGE' and m2.image: acc.add(m2.image)

for inst in dg.object_instances:
    ob = inst.object
    owner = inst.parent.original.name if (inst.is_instance and inst.parent) else (ob.original.users_collection[0].name if ob.original.users_collection else ob.name)
    if owner.startswith(('COLLIDERS', 'DOORS')): continue
    if owner.startswith(('SIGN ', 'CONNECTOR sign', 'HALL sign', 'CONNECTOR_signs')): owner = 'signs (wayfinding text)'
    r = R[owner]
    if ob.type == 'LIGHT':
        r['lights'][ob.data.type] += 1; r['shadow_lights'] += int(getattr(ob.data, 'use_shadow', True)); continue
    if ob.type not in ('MESH', 'CURVE', 'FONT'): continue
    n, used, sig = mats_used(ob)
    if not n: continue
    r['triangles'] += n; r['objects'] += 1; r['meshes'].add(ob.original.data.name if ob.original.data else ob.name); r['submeshes'] += max(1, len(used))
    for m in used:
        if m: r['materials'].add(m.name); images_of(m, r['images'])
    heavy.append((n, owner, ob.original.name))
    if sig: shape[sig].add((owner, ob.original.data.name if ob.original.data else ob.name))

def img_mb(ims): return round(sum(i.size[0] * i.size[1] * 4 * 4 / 3 for i in ims) / 2 ** 20, 1)
rooms = {}
for k, r in sorted(R.items(), key=lambda kv: -kv[1]['triangles']):
    if not r['objects'] and not r['lights']: continue
    budget = 800000 if k == 'ROOM_front-end-area' else (400000 if k.startswith('ROOM_') else None)
    rooms[k] = dict(triangles=r['triangles'], objects=r['objects'], meshes=len(r['meshes']), submeshes=r['submeshes'], materials=len(r['materials']),
                    lights=dict(r['lights']), shadow_lights=r['shadow_lights'], textures=len(r['images']), texture_mb_rgba8=img_mb(r['images']),
                    budget_flag=budget, over_flag=bool(budget and r['triangles'] > budget))
all_imgs = set().union(*[r['images'] for r in R.values()])
tot = dict(triangles=sum(v['triangles'] for v in rooms.values()), objects=sum(v['objects'] for v in rooms.values()), submeshes=sum(v['submeshes'] for v in rooms.values()),
           lights=sum(sum(v['lights'].values()) for v in rooms.values()), shadow_lights=sum(v['shadow_lights'] for v in rooms.values()),
           materials=len(set().union(*[r['materials'] for r in R.values()])), textures=len(all_imgs), texture_mb_rgba8=img_mb(all_imgs))
heavy.sort(reverse=True)
dups = sorted(([len(v), list(k), sorted({o for o, _ in v}), sorted({m for _, m in v})[:6]] for k, v in shape.items() if len({m for _, m in v}) > 1), reverse=True)[:25]
# portal graph from the door table: open doors join their owner room to the room/hall they lead to
doors = json.load(open(os.path.join(HERE, 'validation', 'doors.json')))['doors']
ALIAS = {'reactor': 'ROOM_reactor-room', 'spine': 'ROOM_front-end-area', 'yard': 'ROOM_front-end-area', 'front-end-area': 'ROOM_front-end-area', 'concourse': 'CONNECTOR_reactor_south_concourse',
         'condenser': 'CONNECTOR_condenser_stair', 'refinery': 'ROOM_refinery',
         'east': 'EXTERIOR_evacuation', 'west': 'EXTERIOR_evacuation'}
def nm(s):
    s = s.split(' ')[0]
    if s in ALIAS: return ALIAS[s]
    return 'ROOM_' + s if 'ROOM_' + s in rooms else s
G = defaultdict(set)
for d in doors:
    if d['state'] != 'open': continue
    a_, b_ = nm(d['owner']), nm(d['leads_to'])
    if a_ == b_ or b_.startswith('outside'): continue
    G[a_].add(b_); G[b_].add(a_)
G['CONNECTOR_condenser_escape'].add('ROOM_condenser-bay'); G['ROOM_condenser-bay'].add('CONNECTOR_condenser_escape')
G['CONNECTOR_condenser_stair'].update({'ROOM_turbine-room', 'ROOM_condenser-bay'}); G['ROOM_turbine-room'].add('CONNECTOR_condenser_stair'); G['ROOM_condenser-bay'].add('CONNECTOR_condenser_stair')
pvs = {}
for k in rooms:
    nb = sorted(G.get(k, ()))
    pvs[k] = dict(neighbours=nb, own=rooms[k]['triangles'], with_neighbours=rooms[k]['triangles'] + sum(rooms[n]['triangles'] for n in nb if n in rooms))
json.dump(dict(note='Static counts of the built scene; no frame rate was measured (no runtime build exists). Budgets: only the 400k per-room flag and 800k front-end figure exist in the repo.',
               totals=tot, rooms=rooms, heaviest_meshes=[dict(triangles=n, owner=o, object=ob) for n, o, ob in heavy[:30]], repeated_shapes=dups,
               portal_visible_sets=pvs), open(out, 'w'), indent=1)
print('PERF totals', json.dumps(tot))
for k, v in rooms.items(): print('PERF %-40s tris %9d obj %5d meshes %5d submeshes %5d mats %4d lights %3d tex %3d %6.1f MB %s' % (k, v['triangles'], v['objects'], v['meshes'], v['submeshes'], v['materials'], sum(v['lights'].values()), v['textures'], v['texture_mb_rgba8'], 'OVER FLAG' if v['over_flag'] else ''))
for k, v in pvs.items(): print('PVS %-40s own %9d with neighbours %9d %s' % (k, v['own'], v['with_neighbours'], v['neighbours']))
