"""Bake a room module's procedural materials into texture sets a Unity URP Lit material can use, and export the room as FBX (pilot, owner 2026-10-15:
"Importing this into unity will look like shit"; target URP, one room first). Run on the room's source file; the source is never saved:

    B=blender; U=sections/facility-assembly/unity; O=$U/cooling-plant
    $B -b sections/facility-assembly/sources/cooling-plant/module_aaa_A1.blend --python $U/bake_room.py -- --stage prep --room cooling-plant --out $O [--density 256] [--max 4096]
    $B -b $O/_work.blend --python $U/bake_room.py -- --stage bake --pass base --room cooling-plant --out $O --device GPU|CPU [--samples 4]   # then rough, normal, metal, emit
    $B -b $O/_work.blend --python $U/bake_room.py -- --stage finish --room cooling-plant --out $O

Stages, so that each run fits a job limit and nothing is lost: prep (convert, unwrap, save _work.blend and _plan.json), one bake per pass (writes _raw/*.png;
_work.blend is not saved), finish (URP maps, material swap, <room>_unity.blend, FBX, manifests). --stage all runs everything in one process.

Why: almost every room's look lives in Cycles shader nodes (noise, voronoi, ambient occlusion and bevel nodes, object-coordinate masks). FBX carries none of that:
Unity would import flat base colours, and most meshes have no UVs to hang textures on. The look has to become texture maps first.
What it does, on a copy in memory:
 1. curves and text become meshes and every modifier is applied (the bevels and weighted normals are part of the look);
 2. a new UV layer `UVBake` is unwrapped per material (Smart UV Project on that material's faces across all objects), so each material gets one atlas;
 3. per material, Cycles bakes base colour (DIFFUSE colour only: no lighting), roughness, tangent-space normal (OpenGL +Y, as Unity), metallic (through a temporary
    emission link) and emission. The shader's own AO and bevel nodes are baked in; scene lighting is not (lightmaps are the last step, in Unity, per the UV skill);
 4. the URP map set is written: _BaseMap (sRGB), _MetallicGlossMap (R metallic, A smoothness = 1 - roughness), _BumpMap, _EmissionMap; constant materials get
    no textures, only values;
 5. materials are swapped for image-based Principled ones on `UVBake` (the preview of what Unity gets), the other UV layers are removed, and the room is saved
    as <out>/<room>_unity.blend and exported as <out>/<room>.fbx (meshes only, Blender 5.2 exporter, -Z forward, Y up, apply unit scale);
 6. lights go to <out>/lights.json (Blender values and a URP mode suggestion: area lights are baked-only in URP), materials to <out>/materials.json,
    the run to <out>/bake_report.json.
Not done here: importing into Unity, building URP materials there, lightmaps, LODs. No Unity editor exists in this environment."""
import bpy, bmesh, sys, os, re, json, math, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import blender_device   # owner rule: GPU or CPU only as the owner says
import numpy as np
from mathutils import Vector

a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
def arg(k, d=None): return a[a.index(k) + 1] if k in a else d
ROOM = arg('--room'); OUT = os.path.abspath(arg('--out')); COLL = arg('--collection', 'MODULE_' + ROOM)
PROFILE = arg('--profile', 'default')     # 'home': the owner's PC (Ryzen 7 5800X, 32 GB, Radeon RX 9070 XT 16 GB): 4K atlases, 8 samples, AO/bevel nodes uncapped (device still as the owner says)
_home = PROFILE == 'home'; _rehearsal = PROFILE == 'rehearsal'      # 'rehearsal': every stage at 256 px and 1 sample, to prove a run before the real one
DENSITY = float(arg('--density', 64 if _rehearsal else 256)); MAXSZ = int(arg('--max', 4096 if _home else 256 if _rehearsal else 2048)); SAMPLES = int(arg('--samples', 8 if _home else 1))
# --device GPU|CPU (or CS_BLENDER_DEVICE) is required for the bake stages: blender_device.py, owner rule 2026-10-16
STAGE = arg('--stage', 'all'); PASS = arg('--pass')
if STAGE not in ('prep', 'bake', 'finish', 'all') or (STAGE == 'bake' and PASS not in ('base', 'rough', 'normal', 'metal', 'emit', 'mask')):
    raise SystemExit('unknown --stage %r / --pass %r' % (STAGE, PASS))
ONLY = set(arg('--materials').split(',')) if arg('--materials') else None      # bake only these materials in this run (batches that fit a job limit)
NODE_SAMPLES = int(arg('--node-samples', 0 if _home else 1 if _rehearsal else 4))   # >0: cap the AO and bevel shader nodes' own ray samples (they dominate bake time on a CPU)
SRC = bpy.data.filepath; WORK = os.path.join(OUT, '_work.blend'); RAW = os.path.join(OUT, '_raw'); PLAN = os.path.join(OUT, '_plan.json')
for d in (OUT, os.path.join(OUT, 'textures'), RAW): os.makedirs(d, exist_ok=True)
t0 = time.time(); log = dict(source=os.path.relpath(SRC, os.path.join(os.path.dirname(__file__), '..', '..', '..')), room=ROOM, collection=COLL, density_px_per_m=DENSITY,
                             max_size=MAXSZ, samples=SAMPLES, node_samples=NODE_SAMPLES, profile=PROFILE, blender=bpy.app.version_string, steps=[])
def step(msg, **kw): kw['msg'] = msg; kw['t'] = round(time.time() - t0, 1); log['steps'].append(kw); print('BAKE', STAGE, msg, kw, flush=True)

sc = bpy.context.scene; vl = bpy.context.view_layer
class _Rooms:
    """One or more collections (--collection a,b: rooms like the reactor or the dock span several), read fresh each time."""
    names = COLL.split(',')
    @property
    def all_objects(self):
        """Objects that render: a collection hidden from render hides everything under it (the mine's 'R38 | CC0 asset sources' holds source
        copies the room never shows, 2026-10-17), as it does in the map that links these collections."""
        out = []
        def walk(c):
            if c.hide_render: return
            out.extend(c.objects)
            for ch in c.children: walk(ch)
        for n in self.names: walk(bpy.data.collections[n])
        return list(dict.fromkeys(out))
    def show(self, objs):
        """Make the collections holding `objs` visible in the view layer: edit mode, convert and join skip what the viewport hides.
        Looked up fresh for each change (see _layer)."""
        want = set()
        for o in objs: want.update(c.name for c in o.users_collection)
        def paths(lc, trail, out):
            here = trail + [lc.collection.name]
            if lc.collection.name in want: out.update(here[1:])
            for ch in lc.children: paths(ch, here, out)
        hit = set(); paths(vl.layer_collection, [], hit)
        for n in hit:
            lc = _layer(n)
            if lc is not None: lc.exclude = False; lc.hide_viewport = False; lc.collection.hide_viewport = False
coll = _Rooms()
VOLUME = lambda m: m and m.node_tree and any(n.type == 'OUTPUT_MATERIAL' and n.inputs['Volume'].is_linked for n in m.node_tree.nodes)
def bsdf(m): return next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if m and m.node_tree else None
def linked(m, name): b = bsdf(m); return bool(b and b.inputs[name].is_linked)
def const(m, name, default):
    b = bsdf(m)
    if not b: return default
    v = b.inputs[name].default_value
    return list(v)[:3] if hasattr(v, '__len__') else float(v)
def non_principled(m):
    """URP Lit constants for a material with no Principled BSDF (the reactor's water: glossy and transparent shaders mixed by layer weight).
    Colour and roughness come from its glossy, glass, refraction or diffuse shader; any glass, refraction or transparent shader makes it 25 % alpha
    blend; an Emission shader gives the emission. Nothing is baked for it, so its procedural detail (noise, bump) is not carried over."""
    nodes = m.node_tree.nodes if m and m.node_tree else []
    def first(types, socket):
        for n in nodes:
            if n.type in types and socket in n.inputs and not n.inputs[socket].is_linked:
                v = n.inputs[socket].default_value
                return list(v)[:3] if hasattr(v, '__len__') else float(v)
        return None
    colour = first(('BSDF_GLOSSY', 'BSDF_GLASS', 'BSDF_REFRACTION', 'BSDF_DIFFUSE', 'BSDF_ANISOTROPIC'), 'Color') or [0.8, 0.8, 0.8]
    rough = first(('BSDF_GLOSSY', 'BSDF_GLASS', 'BSDF_REFRACTION', 'BSDF_ANISOTROPIC'), 'Roughness')
    e = dict(_BaseColor=[round(v, 4) for v in colour], _Metallic=0.0, _Smoothness=round(1 - (0.5 if rough is None else rough), 3), non_principled=True)
    if any(n.type in ('BSDF_GLASS', 'BSDF_REFRACTION') for n in nodes): e.update(_Surface='Transparent', _Alpha=GLASS_ALPHA, _PreserveSpecular=True, _BaseColor=[0.0, 0.0, 0.0])
    elif any(n.type == 'BSDF_TRANSPARENT' for n in nodes): e.update(_Surface='Transparent', _Alpha=0.25)
    em = next((n for n in nodes if n.type == 'EMISSION'), None)
    if em is not None:
        e.update(_EmissionColor=list(em.inputs['Color'].default_value)[:3], _EmissionColor_intensity=float(em.inputs['Strength'].default_value))
    return e
CLOSURES = {'BSDF_PRINCIPLED', 'BSDF_DIFFUSE', 'BSDF_GLOSSY', 'BSDF_ANISOTROPIC', 'BSDF_METALLIC', 'BSDF_GLASS', 'BSDF_REFRACTION', 'BSDF_TRANSPARENT',
            'BSDF_TRANSLUCENT', 'BSDF_SHEEN', 'SUBSURFACE_SCATTERING', 'BSDF_TOON', 'BSDF_HAIR', 'BSDF_HAIR_PRINCIPLED', 'EMISSION', 'HOLDOUT', 'BSDF_RAY_PORTAL'}
def surface(m):
    """The output node Cycles renders the material through."""
    outs = [n for n in m.node_tree.nodes if n.type == 'OUTPUT_MATERIAL'] if m and m.node_tree else []
    return next((n for n in outs if n.is_active_output and n.target in ('ALL', 'CYCLES')), None) or next((n for n in outs if n.target in ('ALL', 'CYCLES')), None)
def closures(m):
    """The shader closures feeding the surface through Mix and Add shaders and reroutes, and those mix nodes: (leaves, mixers). An empty shader
    socket is a None leaf (renders black). None when anything else stands in the way (a node group with a shader output, a muted node), so the
    caller falls back to the first Principled BSDF. Since 2026-10-18: the bake used to route only that Principled, which lost the emission strips
    the turbine mixes in (M_ARCH, M_MACH, M_PROPS, M_SHAFT), the screens added in the front end, and every transparency done with a Transparent BSDF."""
    out = surface(m)
    if out is None or not out.inputs['Surface'].is_linked: return None
    leaves, mixers = [], []
    def walk(sock):
        if not sock.is_linked: leaves.append(None); return True
        n = sock.links[0].from_node
        if n.mute: return False
        if n.type == 'REROUTE': return walk(n.inputs[0])
        if n.type in ('MIX_SHADER', 'ADD_SHADER'):
            mixers.append(n); return all([walk(i) for i in n.inputs if i.type == 'SHADER'])
        if n.type in CLOSURES: leaves.append(n); return True
        return False
    return (leaves, mixers) if walk(out.inputs['Surface']) else None
def see_through(n):
    """Can this closure let the background through (URP alpha blend)?"""
    if n is None: return False
    if n.type in ('BSDF_TRANSPARENT', 'BSDF_GLASS', 'BSDF_REFRACTION', 'BSDF_RAY_PORTAL'): return True
    if n.type == 'BSDF_PRINCIPLED':
        al, tw = n.inputs['Alpha'], n.inputs['Transmission Weight']
        return al.is_linked or al.default_value < 1.0 or tw.is_linked or tw.default_value > 0.0
    return False
def emits(n):
    if n is None: return False
    if n.type == 'EMISSION': col, st = n.inputs['Color'], n.inputs['Strength']
    elif n.type == 'BSDF_PRINCIPLED': col, st = n.inputs['Emission Color'], n.inputs['Emission Strength']
    else: return False
    return (col.is_linked or max(list(col.default_value)[:3]) > 0) and (st.is_linked or st.default_value > 0)
def leaf_metal(n):
    """A closure's constant metallic value (URP metallic workflow: glossy and metallic shaders are metal)."""
    if n is None: return 0.0
    if n.type == 'BSDF_PRINCIPLED': return float(n.inputs['Metallic'].default_value)
    return 1.0 if n.type in ('BSDF_GLOSSY', 'BSDF_ANISOTROPIC', 'BSDF_METALLIC') else 0.0

# Each closure becomes an Emission shader carrying one URP channel, and the Mix and Add shaders above it are rebuilt with the same factors, so the bake
# returns the closure-weighted sum. Every closure has an opacity o (Principled: Alpha x (1 - (1 - GLASS_ALPHA) Transmission); glass and refraction
# GLASS_ALPHA; transparent 0; the rest 1) and a reflective weight r (o for Principled and glass, 0 for transparent, emission and holdout, else 1).
# Channels: base = r x colour, rough = r x roughness, metal = r x metallic, emit = o x emission, mask = (1 - o, r, 1). The finish divides base and
# emission by alpha = 1 - mask.R and roughness and metallic by mask.G, which gives straight values for URP (alpha blend multiplies colour and emission
# by alpha); mask.B marks texels the bake covered. A plain opaque Principled bakes exactly as before (o = r = 1).
GLASS_ALPHA = 0.1      # clear glass in URP: 10 % diffuse with reflections kept whole (Preserve Specular); 25 % read as frosted (dock, 2026-10-18)
def glass_like(leaves):
    """Transmission glass with no cut-out transparency: URP's Preserve Specular blend (reflections not faded by alpha), emission not divided by alpha."""
    real = [n for n in leaves if n is not None]
    clear = any(n.type in ('BSDF_GLASS', 'BSDF_REFRACTION') or (n.type == 'BSDF_PRINCIPLED' and (n.inputs['Transmission Weight'].is_linked or
                n.inputs['Transmission Weight'].default_value > 0)) for n in real)
    cut = any(n.type in ('BSDF_TRANSPARENT', 'BSDF_RAY_PORTAL') or (n.type == 'BSDF_PRINCIPLED' and (n.inputs['Alpha'].is_linked or n.inputs['Alpha'].default_value < 1))
              for n in real)
    return clear and not cut
def _src(sock):
    return sock.links[0].from_socket if sock.is_linked else (list(sock.default_value)[:3] if hasattr(sock.default_value, '__len__') else float(sock.default_value))
def _set(nt, v, dst):
    if isinstance(v, bpy.types.NodeSocket): nt.links.new(v, dst)
    elif hasattr(dst.default_value, '__len__'): dst.default_value = (list(v)[:3] + [1.0]) if isinstance(v, (list, tuple)) else (v, v, v, 1.0)
    else: dst.default_value = v
def _math(nt, made, op, x, y, z=None):
    """x op y (op z), folded when every operand is a constant."""
    if not any(isinstance(v, bpy.types.NodeSocket) for v in (x, y, z)):
        return {'MULTIPLY': lambda: x * y, 'SUBTRACT': lambda: x - y, 'MULTIPLY_ADD': lambda: x * y + z}[op]()
    n = nt.nodes.new('ShaderNodeMath'); n.operation = op; made.append(n)
    for i, v in enumerate((x, y, z)):
        if v is not None: _set(nt, v, n.inputs[i])
    return n.outputs[0]
def _weights(nt, n, made):
    """(opacity, reflective weight) of a closure, as constants or sockets."""
    if n is None or n.type in ('EMISSION', 'HOLDOUT'): return 1.0, 0.0
    if n.type in ('BSDF_TRANSPARENT', 'BSDF_RAY_PORTAL'): return 0.0, 0.0
    if n.type in ('BSDF_GLASS', 'BSDF_REFRACTION'): return GLASS_ALPHA, GLASS_ALPHA
    if n.type == 'BSDF_PRINCIPLED':
        o = _math(nt, made, 'MULTIPLY', _src(n.inputs['Alpha']), _math(nt, made, 'MULTIPLY_ADD', _src(n.inputs['Transmission Weight']), GLASS_ALPHA - 1.0, 1.0))
        return o, o
    return 1.0, 1.0
def _leaf(nt, n, ch, made):
    e = nt.nodes.new('ShaderNodeEmission'); made.append(e); o, r = _weights(nt, n, made)
    ins = n.inputs if n is not None else {}
    if ch == 'mask':
        c = nt.nodes.new('ShaderNodeCombineColor'); made.append(c)
        _set(nt, _math(nt, made, 'SUBTRACT', 1.0, o), c.inputs[0]); _set(nt, r, c.inputs[1]); c.inputs[2].default_value = 1.0
        nt.links.new(c.outputs[0], e.inputs['Color']); e.inputs['Strength'].default_value = 1.0
    elif ch == 'emit':
        if n is not None and n.type == 'EMISSION': col, st = _src(n.inputs['Color']), _src(n.inputs['Strength'])
        elif n is not None and n.type == 'BSDF_PRINCIPLED': col, st = _src(n.inputs['Emission Color']), _math(nt, made, 'MULTIPLY', _src(n.inputs['Emission Strength']), o)
        else: col, st = [0.0, 0.0, 0.0], 0.0
        _set(nt, col, e.inputs['Color']); _set(nt, st, e.inputs['Strength'])
    else:
        if ch == 'base':                                         # transmission has no diffuse: clear glass is black under alpha (reflections only)
            v = next((_src(ins[k]) for k in ('Base Color', 'Color') if k in ins), [0.8, 0.8, 0.8])
            if n is not None and n.type in ('BSDF_GLASS', 'BSDF_REFRACTION'): r = 0.0
            elif n is not None and n.type == 'BSDF_PRINCIPLED':
                r = _math(nt, made, 'MULTIPLY', _src(n.inputs['Alpha']), _math(nt, made, 'SUBTRACT', 1.0, _src(n.inputs['Transmission Weight'])))
        elif ch == 'rough': v = _src(ins['Roughness']) if 'Roughness' in ins and n.type != 'BSDF_DIFFUSE' else 1.0
        else: v = _src(ins['Metallic']) if n is not None and n.type == 'BSDF_PRINCIPLED' else leaf_metal(n)
        _set(nt, v, e.inputs['Color']); _set(nt, r, e.inputs['Strength'])
    return e.outputs[0]
def channel_tree(nt, sock, ch, made):
    """The closure tree feeding input `sock`, rebuilt from Emission shaders carrying channel `ch` (closures() has checked it is routable)."""
    if not sock.is_linked: return _leaf(nt, None, ch, made)
    n = sock.links[0].from_node
    if n.type == 'REROUTE': return channel_tree(nt, n.inputs[0], ch, made)
    if n.type not in ('MIX_SHADER', 'ADD_SHADER'): return _leaf(nt, n, ch, made)
    x = nt.nodes.new('ShaderNode' + ('MixShader' if n.type == 'MIX_SHADER' else 'AddShader')); made.append(x)
    if n.type == 'MIX_SHADER': _set(nt, _src(n.inputs[0]), x.inputs[0])
    for i, j in zip([i for i in n.inputs if i.type == 'SHADER'], [j for j in x.inputs if j.type == 'SHADER']): nt.links.new(channel_tree(nt, i, ch, made), j)
    return x.outputs[0]

def collect():
    objs = [o for o in coll.all_objects if o.type == 'MESH' and not o.hide_render and o.name not in skipped and len(o.data.polygons)]   # no faces: nothing to bake or draw
    mats = []
    for o in objs:
        for s_ in o.material_slots:
            if s_.material and s_.material not in mats: mats.append(s_.material)
    return objs, mats

_FN = {}
def fname(name):
    """A material name as a file name: Windows forbids < > : " / \\ | ? * (the fuel corridor's 'FC | bed' failed to save, 2026-10-17). Each one
    character becomes '_', so names that were already safe keep their old file names; clashes (Windows ignores case) get a number."""
    if not _FN:
        used = set()
        for n in sorted(plan):
            s = b = re.sub(r'[<>:"/\\|?*\s]', '_', n); i = 2
            while s.lower() in used: s = '%s_%d' % (b, i); i += 1
            used.add(s.lower()); _FN[n] = s
    return _FN.get(name) or re.sub(r'[<>:"/\\|?*\s]', '_', name)
def saved(im):
    """Save an image and stop the run if the file is not there: a failed save used to pass silently and only broke the finish stage."""
    im.save()
    if not os.path.isfile(bpy.path.abspath(im.filepath_raw)): raise SystemExit('could not write %s' % im.filepath_raw)
    return im

GEN_DEFAULT = ('TEX_NOISE', 'TEX_VORONOI', 'TEX_WAVE', 'TEX_MAGIC', 'TEX_BRICK', 'TEX_CHECKER', 'TEX_GRADIENT', 'TEX_GABOR')   # unlinked Vector = generated coords
def merge_for_bake(objs, mats):
    """Join the room into a few meshes for the bake, in memory only (the bake stage never saves _work.blend), and return them.

    Why: Blender bakes the selected objects one at a time, and each one pays for its whole atlas (a 4K atlas is 16.7 M pixels, copied and margin-filled
    again per object). With 1,570 objects the cooling plant's base pass took about 2.5 h on the owner's GPU (2026-10-17), CPU-bound; joined, each atlas is
    baked a few times instead of once per object. What the shaders read per object is written onto the meshes first, so the look does not change:
      * object coordinates -> point attribute _cs_obj; generated coordinates (also the default vector of the procedural textures) -> _cs_gen;
      * each object's own render UV (image textures and normal maps with no UV named) -> UV layer _cs_render_uv, the merged mesh's render UV.
    Bevel and local-AO shader nodes only see their own object, so an object whose materials use them never shares a mesh with an object its bounds touch.
    A room survey (2026-10-17) found no Object Info, object-space transform or object-attribute nodes and no mirrored objects in any of the twelve rooms."""
    t = time.time()
    trees, seen, info = [], set(), {}
    def walk(nt, acc):
        if nt is None: return
        if nt.as_pointer() not in seen: seen.add(nt.as_pointer()); trees.append(nt)
        for n in nt.nodes:
            if n.type == 'BEVEL' or (n.type == 'AMBIENT_OCCLUSION' and n.only_local):
                acc['local'] = True
                r = n.inputs.get('Radius') or n.inputs.get('Distance')
                acc['radius'] = max(acc['radius'], 0.1 if (r is None or r.is_linked) else float(r.default_value))
            elif n.type in ('UVMAP', 'NORMAL_MAP', 'TANGENT') and n.uv_map: acc['uv'].add(n.uv_map)
            elif n.type == 'ATTRIBUTE' and n.attribute_name and n.attribute_type == 'GEOMETRY': acc['uv'].add(n.attribute_name)
            if ((n.type == 'TEX_COORD' and n.outputs['Normal'].is_linked) or (n.type == 'TANGENT' and n.direction_type == 'RADIAL') or
                    n.type == 'OBJECT_INFO' or (n.type == 'ATTRIBUTE' and n.attribute_type != 'GEOMETRY') or
                    (n.type == 'VERTEX_COLOR' and not n.layer_name) or (n.type == 'NORMAL_MAP' and n.space in ('OBJECT', 'BLENDER_OBJECT'))):
                acc['solo'] = True                               # reads the object itself (object-space normal, radial tangent, object info): not merged
            if n.type == 'GROUP': walk(n.node_tree, acc)
    for m in mats:
        info[m.name] = dict(local=False, radius=0.0, uv=set(), solo=False); walk(m.node_tree, info[m.name])
    # shaders: object and generated coordinates read from the stored attributes (node groups are shared, so every object gets the attributes)
    for nt in trees:
        cache = {}
        def attr(name, near):
            if name not in cache:
                a = nt.nodes.new('ShaderNodeAttribute'); a.attribute_type = 'GEOMETRY'; a.attribute_name = name; a.location = near.location; cache[name] = a
            return cache[name].outputs['Vector']
        for n in list(nt.nodes):
            if n.type == 'TEX_COORD':                            # Generated never depends on the node's object; Object does when one is set
                for out, name in (('Object', '_cs_obj'), ('Generated', '_cs_gen')):
                    if out == 'Object' and n.object is not None: continue
                    for l in list(n.outputs[out].links): nt.links.new(attr(name, n), l.to_socket)
            elif n.type in GEN_DEFAULT and n.inputs.get('Vector') is not None and not n.inputs['Vector'].is_linked:
                nt.links.new(attr('_cs_gen', n), n.inputs['Vector'])
    # meshes: the attributes, the render UV copy, and only the UV layers a shader names (a mesh holds at most 8)
    flags, uvsets = [], []
    for o in objs:
        me = o.data; ms = [s.material for s in o.material_slots if s.material and s.material.name in info]
        refs = set().union(*[info[m.name]['uv'] for m in ms]) if ms else set()
        flags.append((any(info[m.name]['local'] for m in ms), max([info[m.name]['radius'] for m in ms] + [0.0]), any(info[m.name]['solo'] for m in ms)))
        co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        loc, size = np.array(me.texspace_location, np.float32), np.array(me.texspace_size, np.float32); size[size == 0] = 1.0
        for name, arr in (('_cs_obj', co), ('_cs_gen', (co - loc) / (2 * size) + 0.5)):
            a = me.attributes.get(name) or me.attributes.new(name, 'FLOAT_VECTOR', 'POINT'); a.data.foreach_set('vector', arr.astype(np.float32).ravel())
        src = o.get('_cs_render_uv') or next((u.name for u in me.uv_layers if u.name != 'UVBake'), None)
        for u in [u.name for u in me.uv_layers]:
            if u not in refs and u not in ('UVBake', '_cs_render_uv', src): me.uv_layers.remove(me.uv_layers[u])
        if src and me.uv_layers.get(src) is not None:
            buf = np.empty(len(me.loops) * 2, np.float32); me.uv_layers[src].uv.foreach_get('vector', buf)
            if src not in refs: me.uv_layers.remove(me.uv_layers[src])
            rl = me.uv_layers.get('_cs_render_uv') or me.uv_layers.new(name='_cs_render_uv', do_init=False)
            rl.uv.foreach_set('vector', buf); rl.active_render = True
        me.uv_layers.active = me.uv_layers['UVBake']
        uvsets.append({u.name for u in me.uv_layers} - {'UVBake', '_cs_render_uv'})
    # groups: greedy colouring of the bounds-overlap graph, edges only where one side has bevel or local AO; at most 8 UV layers per merged mesh
    N = len(objs); lo = np.empty((N, 3)); hi = np.empty((N, 3))
    for i, o in enumerate(objs):
        c = np.array([o.matrix_world @ Vector(b) for b in o.bound_box]); lo[i], hi[i] = c.min(0), c.max(0)
    local = np.array([f[0] for f in flags]); solo = [f[2] for f in flags]; pad = max([f[1] for f in flags] + [0.0]) + 0.01
    lo -= pad; hi += pad
    order = sorted(range(N), key=lambda i: (not local[i], -float(np.prod(hi[i] - lo[i]))))
    col = np.full(N, -1); groups = []
    for i in order:
        near = np.all((lo[i] <= hi) & (hi[i] >= lo), axis=1) & (col >= 0) & (local | local[i])
        banned = set(col[near].tolist())
        g = None if solo[i] else next((k for k, gr in enumerate(groups) if k not in banned and not gr['solo'] and len(gr['uv'] | uvsets[i]) <= 6), None)
        if g is None: g = len(groups); groups.append(dict(members=[], uv=set(), solo=solo[i]))
        col[i] = g; groups[g]['members'].append(i); groups[g]['uv'] |= uvsets[i]
    for o in list(vl.objects):                                   # in memory: no animation or constraint may move a mesh once joined (the ore cart is animated)
        if o.animation_data: o.animation_data_clear()
        for c_ in list(getattr(o, 'constraints', [])): o.constraints.remove(c_)
    for o in list(vl.objects):                                   # unparent (keeping place) anything whose parent may be joined away
        if o.parent is not None and o.parent.type == 'MESH':
            mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    out = []
    for gr in groups:
        ms = [objs[i] for i in gr['members']]
        if len(ms) > 1:
            for o in bpy.data.objects: o.select_set(False)
            for o in ms: o.select_set(True)
            vl.objects.active = ms[0]; bpy.ops.object.join()
        j = vl.objects.active if len(ms) > 1 else ms[0]; me = j.data
        me.uv_layers.active = me.uv_layers['UVBake']
        if me.uv_layers.get('_cs_render_uv') is not None: me.uv_layers['_cs_render_uv'].active_render = True
        out.append(j)
    step('merged for bake', objects=N, meshes=len(out), objects_with_bevel_or_local_ao=int(local.sum()), not_merged=sum(solo), largest=max(len(g['members']) for g in groups),
         seconds=round(time.time() - t, 1))
    return out

PLAN_VERSION = 2              # 2 (2026-10-18): closure-tree routing, mask pass, HDR emission; older plans and _work files cannot be resumed
ISOLATE = '--isolate' in a     # map mode (bake_all.ps1 -Map): bake the room collections alone, e.g. the map's ROOM_<room>_members
def _layer(name):
    """The view layer's LayerCollection for a collection, looked up fresh: changing exclude rebuilds the tree and leaves older references stale."""
    def walk(lc):
        if lc.collection.name == name: return lc
        for ch in lc.children:
            f = walk(ch)
            if f is not None: return f
    return walk(vl.layer_collection)

def isolate():
    """Link the room collections to the scene if they are not in it (the map instances ROOM_<room>_members rather than linking it) and exclude every
    other collection, so the map's other rooms and instancers neither bake nor shade this one. Members sit in their room's own frame.
    Each exclude is applied through a fresh lookup (2026-10-18: holding LayerCollection references across excludes silently kept the whole map,
    7.9 M triangles of other rooms, in every map bake), then checked."""
    def names(lc):
        yield lc.collection.name
        for ch in lc.children: yield from names(ch)
    present = set(names(vl.layer_collection))
    for n in coll.names:
        if n not in present: sc.collection.children.link(bpy.data.collections[n])
    def plan(lc, out):                                           # collections off every path to a room collection, outermost only
        if lc.collection.name in coll.names: return True         # a room collection keeps all its children (lights-only ones too)
        keep = False
        sub = []
        for ch in lc.children: keep = plan(ch, sub) or keep
        if keep: out.extend(sub)
        else: out.append(lc.collection.name)
        return keep
    drop = []
    for ch in vl.layer_collection.children: plan(ch, drop)
    for n in drop: _layer(n).exclude = True
    keep = set(coll.all_objects)
    for o in list(sc.collection.objects):                        # loose objects at the scene root leave the bake
        if o not in keep: sc.collection.objects.unlink(o)
    for o in list(vl.objects):                                   # what is left visible but is not the room (the map's room instancers above the
        if o not in keep and o.type != 'CAMERA':                 # connector collections) is hidden from the bake
            try: o.hide_render = True; o.hide_viewport = True
            except Exception: pass
    left = [n for n in drop if not _layer(n).exclude]
    if left: raise SystemExit('isolate: collections still in the view layer: %s' % left)

def assert_isolated(where):
    """Everything that renders must be the room (2026-10-18: the whole map rendered inside every map bake and nothing said so). Cameras are allowed.
    Room mode only warns: a room file may hold other things the room scene always rendered with."""
    keep = set()                                                 # everything under the room collections, render-hidden ones too (they do not render)
    def under(c):
        keep.update(c.objects)
        for ch in c.children: under(ch)
    for n in coll.names: under(bpy.data.collections[n])
    foreign = set()
    for o in vl.objects:                                         # render visibility (hidden from the viewport still renders)
        if o not in keep and o.type != 'CAMERA' and not o.hide_render: foreign.add(o.name)
    for inst in bpy.context.evaluated_depsgraph_get().object_instances:
        if not inst.is_instance: continue                        # and nothing instanced from outside the room
        o = inst.object.original; src = inst.parent.original if inst.parent else o
        if src not in keep or (o.type != 'CAMERA' and o not in keep and src.instance_type == 'COLLECTION'): foreign.add('%s (instanced by %s)' % (o.name, src.name))
    if foreign and ISOLATE: raise SystemExit('%s: %d objects render that are not in %s: %s' % (where, len(foreign), coll.names, sorted(foreign)[:20]))
    if foreign: print('BAKE warning (room mode) %s: %d objects outside %s render: %s' % (where, len(foreign), coll.names, sorted(foreign)[:20]))
    step('isolation checked', where=where, foreign=len(foreign))

def check_images(mats):
    """Stop when an image a material uses has no pixels: Cycles bakes a missing image as magenta and nothing else notices (review 2026-10-18:
    the turbine rebuild's 23 PNGs are external LFS files, left as pointers by a pull of .blend files only)."""
    imgs = {}
    def walk(starts, mname, seen):                              # back along the links from the outputs: an unconnected image node does not bake
        stack = list(starts)
        while stack:
            n = stack.pop()
            if n.as_pointer() in seen: continue
            seen.add(n.as_pointer())
            if n.type in ('TEX_IMAGE', 'TEX_ENVIRONMENT') and n.image: imgs.setdefault(n.image, mname)
            if n.type == 'GROUP' and n.node_tree: stack.extend(x for x in n.node_tree.nodes if x.type == 'GROUP_OUTPUT')
            stack.extend(l.from_node for i in n.inputs for l in i.links)
    for m in mats:
        if m.node_tree: walk([x for x in m.node_tree.nodes if x.type == 'OUTPUT_MATERIAL'], m.name, set())
    bad = []
    for im, mname in imgs.items():
        if im.source not in ('FILE', 'TILED', 'SEQUENCE', 'MOVIE') or im.packed_file: continue
        try: im.reload(); ok = im.size[0] > 0 and im.size[1] > 0
        except Exception: ok = False
        if not ok: bad.append('%s (%s, used by %s)' % (im.name, bpy.path.abspath(im.filepath, library=im.library), mname))
    if bad: raise SystemExit('%d images have no pixels (missing file or an LFS pointer: git lfs pull --include the file):\n  %s' % (len(bad), '\n  '.join(sorted(bad))))
    step('images checked', images=len(imgs))

def localise_node_groups(mats):
    """Node groups stay linked when objects, meshes and materials are made local; the merge rewires them, so make them local too."""
    seen = set()
    def walk(nt):
        if nt is None or nt.as_pointer() in seen: return
        seen.add(nt.as_pointer())
        for n in nt.nodes:
            if n.type == 'GROUP' and n.node_tree is not None:
                g = n.node_tree
                if g.library is not None:
                    local = g.make_local()
                    if local is not None and local != g: g.user_remap(local)
                walk(n.node_tree)
    for m in mats: walk(m.node_tree if m else None)

if STAGE in ('prep', 'all'):
    for f in os.listdir(RAW): os.remove(os.path.join(RAW, f))     # maps of an older UV layout must never reach the finish
    if ISOLATE: isolate(); step('isolated', collections=coll.names)
    # collection instances (the spawn room's four PPE hero suits, linked from hero_suit.blend) become real local objects, or the bake would miss them
    inst = [o for o in coll.all_objects if o.instance_type == 'COLLECTION' and o.instance_collection and not o.hide_render]
    if inst:
        coll.show(inst)
        for o in bpy.data.objects: o.select_set(False)
        for o in inst: o.hide_set(False); o.hide_viewport = False; o.hide_select = False; o.select_set(True)
        vl.objects.active = inst[0]
        bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=True)
        for o in inst: o.instance_type = 'NONE'                  # the instancer would otherwise still draw its collection over the real copies
        step('instances made real', instancers=len(inst))
    ext = [o for o in coll.all_objects if o.library or (o.data and o.data.library) or any(s.material and s.material.library for s in o.material_slots)]
    if ext:
        coll.show(ext)
        for o in bpy.data.objects: o.select_set(False)
        for o in ext: o.hide_set(False); o.hide_viewport = False; o.hide_select = False; o.select_set(True)
        vl.objects.active = ext[0]
        bpy.ops.object.make_local(type='SELECT_OBDATA_MATERIAL')   # linked meshes and materials cannot be converted, unwrapped or rewired
        localise_node_groups({s_.material for o in coll.all_objects for s_ in getattr(o, 'material_slots', []) if s_.material})
        step('linked data made local', objects=len(ext))
    objs = [o for o in coll.all_objects if o.type in ('MESH', 'CURVE', 'FONT') and not o.hide_render]
    check_images({s_.material for o in objs for s_ in o.material_slots if s_.material})
    coll.show(objs)
    skipped = [o.name for o in objs if any(VOLUME(s.material) for s in o.material_slots)]
    objs = [o for o in objs if o.name not in skipped]
    for o in bpy.data.objects: o.select_set(False)
    for o in objs: o.hide_set(False); o.hide_viewport = False; o.hide_select = False; o.select_set(True)
    vl.objects.active = objs[0]
    bpy.ops.object.convert(target='MESH')                        # applies modifiers, turns curves and text into meshes
    objs = [o for o in coll.all_objects if o.type == 'MESH' and not o.hide_render and o.name not in skipped]
    for o in objs:
        if o.data.users > 1: o.data = o.data.copy()              # every object its own UVs (object-coordinate shaders differ per object)
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs)
    step('converted', objects=len(objs), triangles=tris, skipped_volume=skipped)

    # objects without a material (or with empty slots) get a neutral constant one, so every face has a material to bake and export
    grey = None
    for o in objs:
        if not o.material_slots or any(s.material is None for s in o.material_slots):
            if grey is None:
                grey = bpy.data.materials.new('unassigned grey'); grey.use_nodes = True
            if not o.material_slots: o.data.materials.append(grey)
            for s in o.material_slots:
                if s.material is None: s.material = grey


    objs, mats = collect()
    plan = {}
    for m in mats:
        b = bsdf(m); tree = closures(m)
        if tree is not None: leaves, mixers = tree; route = 'tree'
        elif b is not None: leaves, mixers = [b], []; route = 'principled'     # a node group or muted node in the shader chain: the old route
        else: leaves, mixers = [], []; route = None
        real = [n for n in leaves if n is not None]
        procedural = (any(i.is_linked for n in real + mixers for i in n.inputs if i.type != 'SHADER') or
                      bool(m.node_tree and any(n.type in ('TEX_NOISE', 'TEX_VORONOI', 'AMBIENT_OCCLUSION', 'BEVEL') for n in m.node_tree.nodes)))
        # constants only for one plain Principled; any other routable surface bakes, even with constant inputs (a constant mix with an Emission or
        # Transparent shader cannot be expressed as one URP constant set). Unroutable ones fall back to the first Principled, else to non_principled().
        bake = route is not None and bool(real) and (procedural or len(leaves) > 1 or real[0].type != 'BSDF_PRINCIPLED')
        # mask pass: alpha and the reflective weight, wherever several closures mix or one is not plainly reflective (emission, holdout, glass,
        # transparent): without it a pure Emission shader bakes roughness 0 (r = 0) and comes out glossy black in Unity
        mask = bake and (len(leaves) > 1 or any(n is None or see_through(n) or n.type in ('EMISSION', 'HOLDOUT') for n in leaves))
        plan[m.name] = dict(bake=bake, route=route, closures=sorted({n.type for n in real}), mask=mask,
                            metallic_map=bake and (len(leaves) > 1 or any(n.type == 'BSDF_PRINCIPLED' and n.inputs['Metallic'].is_linked for n in real)),
                            metal_const=leaf_metal(real[0]) if len(real) == 1 else 0.0, emission=any(emits(n) for n in leaves), principled=b is not None,
                            glass=glass_like(leaves))
    # view-dependent nodes (Layer Weight, Fresnel, Light Path, Camera Data) bake as seen head-on: a texture cannot hold them and URP Lit has no such
    # term. The turbine's rim glow (M_ARCH, M_MACH, M_PROPS, M_SHAFT: Emission mixed in by Layer Weight Facing) bakes to nothing. Listed, not fixed.
    def view_dep(nt, seen):
        if nt is None or nt.as_pointer() in seen: return False
        seen.add(nt.as_pointer())
        return any(n.type in ('LAYER_WEIGHT', 'FRESNEL', 'LIGHT_PATH', 'CAMERA') or (n.type == 'GROUP' and view_dep(n.node_tree, seen)) for n in nt.nodes)
    for m in mats: plan[m.name]['view_dependent'] = bool(plan[m.name]['bake'] and view_dep(m.node_tree, set()))
    step('materials planned', baked=sum(p['bake'] for p in plan.values()), masked=sorted(n for n, p in plan.items() if p['mask']),
         view_dependent_baked_head_on=sorted(n for n, p in plan.items() if p['view_dependent']),
         constant_multi_closure=sorted(n for n, p in plan.items() if not p['bake'] and len(p['closures']) > 1))

    # --- UVs: one atlas per material ---------------------------------------------------------------------------------------------------------------------
    for o in objs:
        r = next((u.name for u in o.data.uv_layers if u.active_render), None)
        if r and r != 'UVBake': o['_cs_render_uv'] = r      # the shaders' default UV (image textures, normal maps with no UV named); stays the render UV
        uv = o.data.uv_layers.get('UVBake') or o.data.uv_layers.new(name='UVBake')
        o.data.uv_layers.active = uv                         # the bake writes through the active layer
    for o in bpy.data.objects: o.select_set(False)
    for o in objs: o.select_set(True)
    vl.objects.active = objs[0]
    bpy.ops.object.mode_set(mode='EDIT')
    sc.tool_settings.use_uv_select_sync = True
    area = {}
    for m in mats:
        if not plan[m.name]['bake']: continue
        tot = 0.0
        for o in objs:
            bm = bmesh.from_edit_mesh(o.data); idx = {i for i, s in enumerate(o.material_slots) if s.material is m}
            sx = o.matrix_world.to_scale(); k = abs(sx.x * sx.y * sx.z) ** (2 / 3)
            for f in bm.faces:
                f.select = f.material_index in idx
                if f.select: tot += f.calc_area() * k
            bmesh.update_edit_mesh(o.data)
        area[m.name] = tot
        if tot <= 0: plan[m.name]['bake'] = False; continue
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
        bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=0.002)                 # smart project leaves up to 40 % of the square empty
    bpy.ops.object.mode_set(mode='OBJECT')
    for n, p in plan.items():
        if p['bake']:
            s = 2 ** math.ceil(math.log2(max(1.0, math.sqrt(area[n]) * DENSITY))); p['size'] = int(min(MAXSZ, max(256, s)))
            p['area_m2'] = round(area[n], 2); p['px_per_m'] = round(p['size'] * 0.75 / math.sqrt(area[n]), 1)      # 0.75: typical packing efficiency
    step('unwrapped', atlases={n: p.get('size') for n, p in plan.items() if p['bake']})


    for m in mats: m.use_fake_user = True
    assert_isolated('prep')
    json.dump(dict(version=PLAN_VERSION, plan=plan, skipped=skipped, triangles=tris, objects=len(objs), log=log), open(PLAN, 'w'), indent=1)
    bpy.ops.wm.save_as_mainfile(filepath=WORK, relative_remap=True, copy=True)
    step('prep saved', work=os.path.basename(WORK))
    if STAGE == 'prep': raise SystemExit(0)
else:
    _p = json.load(open(PLAN))
    if _p.get('version') != PLAN_VERSION: raise SystemExit('%s was written by an older bake_room.py (plan version %s, need %s): rerun from prep' % (PLAN, _p.get('version'), PLAN_VERSION))
    plan, skipped, tris = _p['plan'], _p['skipped'], _p['triangles']; log['steps'] = _p['log']['steps']
    objs, mats = collect()
    assert_isolated(STAGE)

if STAGE in ('bake', 'all'):
    # --- bake -------------------------------------------------------------------------------------------------------------------------------------------
    sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = False
    step('device', **blender_device.apply(sc))     # the owner's GPU or CPU; stops if unset, never falls back
    if NODE_SAMPLES:
        def cap(nt, seen):
            if nt is None or nt.as_pointer() in seen: return
            seen.add(nt.as_pointer())
            for n_ in nt.nodes:
                if n_.type in ('AMBIENT_OCCLUSION', 'BEVEL'): n_.samples = min(n_.samples, NODE_SAMPLES)
                elif n_.type == 'GROUP': cap(n_.node_tree, seen)
        _seen = set()
        for m in mats: cap(m.node_tree, _seen)
    bake_objs = merge_for_bake(objs, mats) if arg('--merge', 'on') != 'off' else objs   # objs stays the unmerged list for --stage all's finish
    bk = sc.render.bake; bk.margin = 8; bk.margin_type = 'EXTEND'; bk.use_clear = True; bk.use_selected_to_active = False
    dummy = bpy.data.images.new('_bake_dummy', 8, 8)
    imgs = {}
    def image(mname, kind, colour):
        """Emission (HDR: lamps reach 45) and every pass of a masked material (divided by alpha or the reflective weight in the finish) bake
        to float images saved as EXR, scene linear; the rest to 8-bit PNG as before."""
        s = plan[mname]['size']; fl = kind == 'emit' or (plan[mname]['mask'] and kind != 'normal')
        im = bpy.data.images.new('%s_%s' % (mname, kind), s, s, alpha=False, float_buffer=fl)
        if not fl: im.colorspace_settings.name = 'sRGB' if colour else 'Non-Color'
        elif not colour: im.colorspace_settings.name = 'Non-Color'
        imgs[(mname, kind)] = im; return im
    def target(kind, colour, wanted):
        """Point every material's active image node at its `kind` image (materials not baking this pass at a dummy, so the bake does not stop)."""
        for m in mats:
            nt = m.node_tree
            if nt is None: m.use_nodes = True; nt = m.node_tree
            node = nt.nodes.get('_bake_target') or nt.nodes.new('ShaderNodeTexImage'); node.name = '_bake_target'
            node.image = image(m.name, kind, colour) if (plan[m.name]['bake'] and wanted(m) and (ONLY is None or m.name in ONLY)) else dummy
            nt.nodes.active = node
    def run(kind, btype, colour=True, wanted=lambda m: True, **kw):
        target(kind, colour, wanted); t = time.time()
        bpy.ops.object.bake(type=btype, uv_layer='UVBake', **kw); step('baked ' + kind, seconds=round(time.time() - t, 1))
    for o in bpy.data.objects: o.select_set(False)
    for o in bake_objs: o.select_set(True)
    vl.objects.active = bake_objs[0]
    def save_raw(kind):
        for (mn, k), im in imgs.items():
            if k != kind: continue
            ext, im.file_format = ('.exr', 'OPEN_EXR') if im.is_float else ('.png', 'PNG')
            for old in ('.exr', '.png'):                            # a rerun must not leave the other format behind for the finish to pick up
                f = os.path.join(RAW, '%s_%s%s' % (fname(mn), k, old))
                if old != ext and os.path.exists(f): os.remove(f)
            im.filepath_raw = os.path.join(RAW, '%s_%s%s' % (fname(mn), k, ext)); saved(im)
    def want(p): return STAGE == 'all' or PASS == p
    # base colour, roughness, metallic, emission and the mask through the material output: the closure tree is rebuilt from Emission shaders carrying
    # the channel (channel_tree) and baked as EMIT. Not the DIFFUSE colour pass for base colour: Cycles scales that pass by (1 - metallic), so metal
    # surfaces came out darker and Unity then applied metallic again (pilot 2026-10-16: baked renders 8 to 19 % darker; after the fix within 1.5 %).
    def via_channel(ch, colour, wanted):
        made_by = {}
        for m in mats:
            p = plan[m.name]
            if not (p['bake'] and wanted(m)): continue
            nt = m.node_tree; out = surface(m); old = out.inputs['Surface'].links[0].from_socket if out.inputs['Surface'].is_linked else None
            made = []
            root = channel_tree(nt, out.inputs['Surface'], ch, made) if p['route'] == 'tree' else _leaf(nt, bsdf(m), ch, made)
            nt.links.new(root, out.inputs['Surface']); made_by[m.name] = (out, old, made)
        if made_by: run(ch, 'EMIT', colour=colour, wanted=lambda m: m.name in made_by)
        for n, (out, old, made) in made_by.items():
            nt = bpy.data.materials[n].node_tree
            if old is not None: nt.links.new(old, out.inputs['Surface'])
            for x in made: nt.nodes.remove(x)
    if want('base'): via_channel('base', True, lambda m: True); save_raw('base')
    if want('rough'): via_channel('rough', False, lambda m: True); save_raw('rough')
    if want('normal'): run('normal', 'NORMAL', colour=False, normal_space='TANGENT', normal_r='POS_X', normal_g='POS_Y', normal_b='POS_Z'); save_raw('normal')
    if want('metal'): via_channel('metal', False, lambda m: plan[m.name]['metallic_map']); save_raw('metal')
    if want('emit'): via_channel('emit', True, lambda m: plan[m.name]['emission']); save_raw('emit')
    if want('mask'): via_channel('mask', False, lambda m: plan[m.name]['mask']); save_raw('mask')


    if STAGE == 'bake':                                          # this pass's steps (times) for the finish to put in bake_report.json
        json.dump(log['steps'], open(os.path.join(RAW, '_steps_%s.json' % PASS), 'w')); raise SystemExit(0)

# --- write the URP map set ---------------------------------------------------------------------------------------------------------------------------
TEX = os.path.join(OUT, 'textures')
PASSES = ('base', 'rough', 'normal', 'metal', 'emit', 'mask')
def needs(p, k):
    return p['bake'] and (k in ('base', 'rough', 'normal') or (k == 'metal' and p['metallic_map']) or (k == 'emit' and p['emission']) or (k == 'mask' and p['mask']))
if STAGE == 'finish':
    imgs, missing = {}, []
    for m in mats:
        for k in PASSES:
            f = next((f for f in (os.path.join(RAW, '%s_%s%s' % (fname(m.name), k, x)) for x in ('.exr', '.png')) if os.path.exists(f)), None)
            if not needs(plan[m.name], k): continue
            if f is None: missing.append('%s_%s' % (fname(m.name), k)); continue
            im = bpy.data.images.load(f)
            if not im.is_float: im.colorspace_settings.name = 'sRGB' if k == 'base' else 'Non-Color'
            imgs[(m.name, k)] = im
    for k in PASSES:
        f = os.path.join(RAW, '_steps_%s.json' % k)
        if os.path.exists(f): log['steps'] += [x for x in json.load(open(f)) if x not in log['steps']]
    if missing: raise SystemExit('finish: %d baked maps missing from %s (a bake pass did not run or failed): %s' % (len(missing), RAW, missing[:20]))
    dummy = bpy.data.images.new('_bake_dummy', 8, 8)
    for m in mats:
        n_ = m.node_tree.nodes.get('_bake_target') if m.node_tree else None
        if n_: m.node_tree.nodes.remove(n_)
for f in os.listdir(TEX): os.remove(os.path.join(TEX, f))           # the finish writes every map: nothing from an older run may stay behind
def px(im): a_ = np.empty(len(im.pixels), np.float32); im.pixels.foreach_get(a_); return a_.reshape(im.size[1], im.size[0], 4)
def to_lin(c): return np.where(c <= 0.04045, c / 12.92, ((np.maximum(c, 0.04045) + 0.055) / 1.055) ** 2.4)
def to_srgb(c): c = np.clip(c, 0.0, 1.0); return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.maximum(c, 0.0031308) ** (1 / 2.4) - 0.055)
def lin(im):
    """A colour map as scene-linear RGB: float bakes are linear already, 8-bit ones are sRGB-encoded."""
    a_ = px(im)[..., :3]; return a_ if im.is_float else to_lin(a_)
def bleed(rgb, ok, n=16):
    """Give texels that are not ok their neighbours' colour, n texels deep: under alpha 0 a straight-alpha map still needs the edge colour,
    or texture filtering pulls black into the edges of decals."""
    rgb = rgb.copy(); ok = ok.copy()
    for _ in range(n):
        if ok.all(): break
        acc = np.zeros_like(rgb); cnt = np.zeros(ok.shape, np.float32)
        for sh in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            k_ = np.roll(ok, sh, (0, 1)); acc += np.roll(rgb, sh, (0, 1)) * k_[..., None]; cnt += k_
        new = ~ok & (cnt > 0)
        if not new.any(): break
        rgb[new] = acc[new] / cnt[new][:, None]; ok |= new
    return rgb
def save(arr, name, colour):
    """Write an 8-bit PNG; `arr` holds the values as stored (sRGB-encoded for colour maps)."""
    h, w = arr.shape[:2]; im = bpy.data.images.new(name, w, h, alpha=True); im.colorspace_settings.name = 'sRGB' if colour else 'Non-Color'
    im.pixels.foreach_set(np.clip(arr, 0.0, 1.0).astype(np.float32).ravel()); im.filepath_raw = os.path.join(TEX, name + '.png'); im.file_format = 'PNG'; return saved(im)
manifest = {}
for m in mats:
    p = plan[m.name]; safe = fname(m.name); e = dict(source_material=m.name, urp_shader='Universal Render Pipeline/Lit')
    if p['bake']:
        rough = px(imgs[(m.name, 'rough')])[..., 0]
        metal = px(imgs[(m.name, 'metal')])[..., 0] if (m.name, 'metal') in imgs else np.full(rough.shape, float(p['metal_const']), np.float32)
        base = np.ones(rough.shape + (4,), np.float32)
        if p['mask']:
            # straight values for URP from the closure-weighted bake (see channel_tree): colour and emission over alpha, roughness and metallic over
            # the reflective weight; where a texel has no reflective closure (a pure emission strip) it is matte dielectric
            mk = px(imgs[(m.name, 'mask')]); alpha = np.clip(1.0 - mk[..., 0], 0.0, 1.0); refl = mk[..., 1]; cov = mk[..., 2] > 0.5
            seen = alpha > 1 / 255
            base[..., :3] = to_srgb(bleed(np.where(seen[..., None], lin(imgs[(m.name, 'base')]) / np.maximum(alpha, 1e-6)[..., None], 0.0), seen | ~cov))
            ok = refl > 1e-3
            rough = np.where(ok, rough / np.maximum(refl, 1e-3), 1.0); metal = np.where(ok, metal / np.maximum(refl, 1e-3), 0.0) if (m.name, 'metal') in imgs else metal
            see = float((alpha[cov] < 0.98).mean()) if cov.any() else 0.0
            e.update(alpha_below_098_fraction=round(see, 4))
            if see > 0.001:
                base[..., 3] = np.where(cov, alpha, 1.0); e.update(_Surface='Transparent', _Alpha_source='BaseMap alpha')
                if p.get('glass'): e['_PreserveSpecular'] = True
        else:
            alpha = None; im = imgs[(m.name, 'base')]
            base[..., :3] = px(im)[..., :3] if not im.is_float else to_srgb(px(im)[..., :3])
        save(base, safe + '_BaseMap', True)
        mg = np.zeros(base.shape, np.float32); mg[..., 0] = mg[..., 1] = mg[..., 2] = np.clip(metal, 0, 1); mg[..., 3] = 1.0 - np.clip(rough, 0, 1)
        save(mg, safe + '_MetallicGlossMap', False)
        nrm = px(imgs[(m.name, 'normal')]); nrm[..., 3] = 1.0; save(nrm, safe + '_BumpMap', False)
        e.update(_BaseMap='textures/%s_BaseMap.png' % safe, _MetallicGlossMap='textures/%s_MetallicGlossMap.png' % safe, _BumpMap='textures/%s_BumpMap.png' % safe,
                 _Smoothness_source='MetallicGlossMap alpha', size=p['size'], area_m2=p['area_m2'], approx_px_per_m=p['px_per_m'])
        if (m.name, 'emit') in imgs:
            # HDR: the bake is linear and unclipped (lamps reach 45); the map holds colour / peak, sRGB-encoded, and the intensity is the linear peak
            em = lin(imgs[(m.name, 'emit')])
            if alpha is not None and not e.get('_PreserveSpecular'):    # alpha blend multiplies emission by alpha; Preserve Specular does not
                em = np.where(alpha[..., None] > 1 / 255, em / np.maximum(alpha, 1e-6)[..., None], 0.0)
            peak = float(em.max())
            if peak > 1e-4:
                out_ = np.ones(base.shape, np.float32); out_[..., :3] = to_srgb(em / peak)
                save(out_, safe + '_EmissionMap', True); e.update(_EmissionMap='textures/%s_EmissionMap.png' % safe, _EmissionColor_intensity=round(peak, 4))
    elif not p['principled']:
        e.update(non_principled(m))
    else:
        e.update(_BaseColor=const(m, 'Base Color', [0.8, 0.8, 0.8]), _Metallic=const(m, 'Metallic', 0.0), _Smoothness=round(1 - const(m, 'Roughness', 0.5), 3))
        if p['emission']: e.update(_EmissionColor=const(m, 'Emission Color', [0, 0, 0]), _EmissionColor_intensity=const(m, 'Emission Strength', 0.0))
        tw = bsdf(m).inputs['Transmission Weight'].default_value if bsdf(m) else 0.0
        if const(m, 'Alpha', 1.0) < 1.0 or tw > 0:
            e['_Surface'] = 'Transparent'; e['_Alpha'] = round(const(m, 'Alpha', 1.0) * (1 - (1 - GLASS_ALPHA) * tw), 3)
            k = (1 - tw) / max(1 - (1 - GLASS_ALPHA) * tw, 1e-3)    # transmission has no diffuse (as in the baked branch): clear glass is black
            e['_BaseColor'] = [round(c * k, 4) for c in e['_BaseColor']]
            if tw > 0 and const(m, 'Alpha', 1.0) >= 1.0: e['_PreserveSpecular'] = True
    manifest[m.name] = e
step('maps written', materials=len(manifest), textures=len(os.listdir(TEX)))

# --- swap to the image materials (what Unity gets), keep only UVBake, save and export -------------------------------------------------------------------
def unity_mat(m):
    e = manifest[m.name]; u = bpy.data.materials.new('U_' + m.name); u.use_nodes = True; nt = u.node_tree; b = nt.nodes['Principled BSDF']
    def tex(path, colour):
        n = nt.nodes.new('ShaderNodeTexImage'); n.image = bpy.data.images.load(os.path.join(OUT, path)); n.image.colorspace_settings.name = 'sRGB' if colour else 'Non-Color'
        uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'UVBake'; nt.links.new(uvn.outputs[0], n.inputs[0]); return n
    if '_BaseMap' in e:
        bm = tex(e['_BaseMap'], True); nt.links.new(bm.outputs['Color'], b.inputs['Base Color'])
        if e.get('_Surface') == 'Transparent': nt.links.new(bm.outputs['Alpha'], b.inputs['Alpha'])
        mg = tex(e['_MetallicGlossMap'], False); sep = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(mg.outputs['Color'], sep.inputs[0])
        nt.links.new(sep.outputs[0], b.inputs['Metallic']); inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
        nt.links.new(mg.outputs['Alpha'], inv.inputs[1]); nt.links.new(inv.outputs[0], b.inputs['Roughness'])
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.uv_map = 'UVBake'; nt.links.new(tex(e['_BumpMap'], False).outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs[0], b.inputs['Normal'])
        if '_EmissionMap' in e:
            nt.links.new(tex(e['_EmissionMap'], True).outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = e['_EmissionColor_intensity']
    else:
        b.inputs['Base Color'].default_value = list(e['_BaseColor']) + [1.0]; b.inputs['Metallic'].default_value = e['_Metallic']; b.inputs['Roughness'].default_value = 1 - e['_Smoothness']
        if '_EmissionColor' in e: b.inputs['Emission Color'].default_value = list(e['_EmissionColor']) + [1.0]; b.inputs['Emission Strength'].default_value = e['_EmissionColor_intensity']
        if e.get('_Surface') == 'Transparent': b.inputs['Alpha'].default_value = e.get('_Alpha', 0.25)   # what URP gets: alpha blend, not transmission
    if e.get('_PreserveSpecular'):
        # URP Preserve Specular: background x (1 - a) + diffuse x a + full specular. In Cycles: Add(Transparent coloured 1 - a, opaque Principled with base x a)
        a_ = b.inputs['Alpha'].links[0].from_socket if b.inputs['Alpha'].is_linked else b.inputs['Alpha'].default_value
        for l in list(b.inputs['Alpha'].links): nt.links.remove(l)
        b.inputs['Alpha'].default_value = 1.0
        out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'); add = nt.nodes.new('ShaderNodeAddShader'); tr = nt.nodes.new('ShaderNodeBsdfTransparent')
        inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; _set(nt, a_, inv.inputs[1]); nt.links.new(inv.outputs[0], tr.inputs['Color'])
        mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs[0].default_value = 1.0
        src = b.inputs['Base Color'].links[0].from_socket if b.inputs['Base Color'].is_linked else list(b.inputs['Base Color'].default_value)[:3]
        _set(nt, src, mul.inputs[6]); _set(nt, a_, mul.inputs[7]); nt.links.new(mul.outputs[2], b.inputs['Base Color'])
        nt.links.new(tr.outputs[0], add.inputs[0]); nt.links.new(b.outputs[0], add.inputs[1]); nt.links.new(add.outputs[0], out.inputs['Surface'])
    return u
swap = {m.name: unity_mat(m) for m in mats}
for o in objs:
    for s in o.material_slots:
        if s.material and s.material.name in swap: s.material = swap[s.material.name]
    for uv in [u for u in o.data.uv_layers if u.name != 'UVBake']: o.data.uv_layers.remove(uv)
for o in list(coll.all_objects):
    if o.name in skipped: bpy.data.objects.remove(o)
for im in list(imgs.values()) + [dummy]: bpy.data.images.remove(im)
lights = []
for o in coll.all_objects:
    if o.type != 'LIGHT' or o.hide_render: continue          # a light switched off for render is not part of the room's lighting
    d = o.data; l = dict(name=o.name, type=d.type, location=[round(v, 4) for v in o.matrix_world.translation], rotation_euler_deg=[round(math.degrees(v), 2) for v in o.matrix_world.to_euler()],
                         color=[round(v, 4) for v in d.color], energy_blender=round(d.energy, 3), shadow=d.use_shadow)
    if d.type == 'SPOT': l.update(spot_angle_deg=round(math.degrees(d.spot_size), 2), spot_blend=round(d.spot_blend, 3))
    if d.type == 'AREA':                                          # the object's scale is part of an area light's size
        sx, sy = abs(o.matrix_world.to_scale().x), abs(o.matrix_world.to_scale().y)
        l.update(shape=d.shape, size=[round(d.size * sx, 3), round((d.size_y if d.shape in ('RECTANGLE', 'ELLIPSE') else d.size) * sy, 3)])
    l['urp_mode'] = {'AREA': 'Area light, Baked only (URP has no realtime area lights): bake into lightmaps', 'SUN': 'Directional, Mixed',
                     'POINT': 'Point, Mixed (realtime for players, baked indirect)', 'SPOT': 'Spot, Mixed'}[d.type]
    l['note'] = 'Blender watts are not URP intensities: retune in Unity against the reference renders'
    lights.append(l)
json.dump(dict(room=ROOM, frame='module frame (metres, +Z up); FBX converts to Unity Y up', lights=lights), open(os.path.join(OUT, 'lights.json'), 'w'), indent=1)
json.dump(dict(room=ROOM, pipeline='URP 17 (Unity 6) Lit', uv='UVBake is the only UV layer (uv0); generate lightmap UVs on import',
               normal_maps='tangent space, OpenGL (+Y), as Unity', materials=manifest), open(os.path.join(OUT, 'materials.json'), 'w'), indent=1)
for m in mats: m.use_fake_user = False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, ROOM + '_unity.blend'), relative_remap=True)
for o in bpy.data.objects: o.select_set(False)
for o in objs: o.select_set(True)
fbx = os.path.join(OUT, ROOM + '.fbx')
bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, object_types={'MESH'}, apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
                         mesh_smooth_type='FACE', use_mesh_modifiers=True, add_leaf_bones=False, bake_anim=False, path_mode='RELATIVE', use_custom_props=False)
log.update(objects=len(objs), triangles=tris, materials={n: dict(plan[n]) for n in plan}, lights=len(lights), fbx=os.path.basename(fbx), fbx_bytes=os.path.getsize(fbx),
           seconds=round(time.time() - t0, 1))
json.dump(log, open(os.path.join(OUT, 'bake_report.json'), 'w'), indent=1)
step('done', fbx_bytes=os.path.getsize(fbx))
