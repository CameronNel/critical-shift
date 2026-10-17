"""What of the combined map survives an FBX import into Unity? Per room: triangles by material kind, meshes without UVs, lights.
    blender --background combined/combined_map.blend --python unity/unity_audit.py -- unity/unity_audit.json"""
import bpy, sys, json, collections
PROC = {'TEX_NOISE', 'TEX_VORONOI', 'TEX_WAVE', 'TEX_MAGIC', 'TEX_GRADIENT', 'TEX_CHECKER', 'TEX_BRICK', 'TEX_WHITE_NOISE', 'AMBIENT_OCCLUSION', 'BEVEL', 'TEX_GABOR'}
def kind(m, cache={}):
    if m is None: return 'none'
    if m.name in cache: return cache[m.name]
    k = 'flat'
    if m.use_nodes and m.node_tree:
        types = {n.type for n in m.node_tree.nodes}
        for n in m.node_tree.nodes:
            if n.type == 'GROUP' and n.node_tree: types |= {x.type for x in n.node_tree.nodes}
        img = 'TEX_IMAGE' in types; proc = bool(types & PROC)
        coords = any(n.type == 'TEX_COORD' and any(o.is_linked and o.name in ('Object', 'Generated', 'Position') for o in n.outputs) for n in m.node_tree.nodes)
        principled = 'BSDF_PRINCIPLED' in types
        if proc or (coords and not img): k = 'procedural (needs baking)'
        elif img: k = 'image textures (exports)'
        elif not principled: k = 'non-principled shader'
        if 'VOLUME' in ''.join(types) or 'PRINCIPLED_VOLUME' in types: k = 'volume (no FBX)'
    cache[m.name] = k; return k
out = {}
for inst in [o for o in bpy.data.objects if o.name.startswith('ROOM_') and o.instance_type == 'COLLECTION']:
    tris = collections.Counter(); nouv = 0; nouv_t = 0; meshes = 0; lights = collections.Counter(); mats = collections.Counter()
    for o in inst.instance_collection.all_objects:
        if o.type == 'LIGHT': lights[o.data.type] += 1; continue
        if o.type != 'MESH' or not o.data.polygons: continue
        me = o.data; meshes += 1
        t = sum(len(p.vertices) - 2 for p in me.polygons)
        slots = [s.material for s in o.material_slots] or [None]
        if not me.uv_layers: nouv += 1; nouv_t += t
        per = collections.Counter(p.material_index for p in me.polygons) if len(slots) > 1 else {0: len(me.polygons)}
        tot = sum(per.values()) or 1
        for i, c in per.items():
            m = slots[i] if i < len(slots) else None; k = kind(m); tris[k] += t * c / tot; mats[k] += 0
    T = sum(tris.values()) or 1
    out[inst.name] = dict(triangles=int(T), share={k: round(v / T * 100, 1) for k, v in tris.most_common()}, meshes=meshes, meshes_without_uv=nouv,
                          tri_share_without_uv=round(nouv_t / T * 100, 1), lights=dict(lights))
allk = collections.Counter()
for r in out.values():
    for k, v in r['share'].items(): allk[k] += v * r['triangles'] / 100
T = sum(allk.values())
print('AUDIT TOTAL', int(T), {k: round(v / T * 100, 1) for k, v in allk.most_common()})
for k, r in sorted(out.items(), key=lambda kv: -kv[1]['triangles']): print('AUDIT', k, json.dumps(r))
json.dump(out, open((sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else 'unity_audit.json'), 'w'), indent=1)
