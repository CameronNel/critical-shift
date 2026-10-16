"""Bake a room module's procedural materials into texture sets a Unity URP Lit material can use, and export the room as FBX (pilot, owner 2026-10-15:
"Importing this into unity will look like shit"; target URP, one room first). Run on the room's source file; the source is never saved:

    B=blender; U=sections/facility-assembly/unity; O=$U/cooling-plant
    $B -b sections/facility-assembly/sources/cooling-plant/module_aaa_A1.blend --python $U/bake_room.py -- --stage prep --room cooling-plant --out $O [--density 256] [--max 4096]
    $B -b $O/_work.blend --python $U/bake_room.py -- --stage bake --pass base --room cooling-plant --out $O [--samples 4]     # then rough, normal, metal, emit
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
import bpy, bmesh, sys, os, json, math, time
import numpy as np

a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
def arg(k, d=None): return a[a.index(k) + 1] if k in a else d
ROOM = arg('--room'); OUT = os.path.abspath(arg('--out')); COLL = arg('--collection', 'MODULE_' + ROOM)
PROFILE = arg('--profile', 'default')     # 'home': the owner's PC (Ryzen 7 5800X, 32 GB, Radeon RX 9070 XT 16 GB): 4K atlases, 8 samples, AO/bevel nodes uncapped
_home = PROFILE == 'home'
DENSITY = float(arg('--density', 256)); MAXSZ = int(arg('--max', 4096 if _home else 2048)); SAMPLES = int(arg('--samples', 8 if _home else 1))
DEVICE = arg('--device', 'auto')          # auto: the first GPU backend Blender finds (HIP for AMD, OptiX/CUDA for NVIDIA, oneAPI, Metal), else the CPU
STAGE = arg('--stage', 'all'); PASS = arg('--pass')
ONLY = set(arg('--materials').split(',')) if arg('--materials') else None      # bake only these materials in this run (batches that fit a job limit)
NODE_SAMPLES = int(arg('--node-samples', 0 if _home else 4))   # >0: cap the AO and bevel shader nodes' own ray samples (they dominate bake time on a CPU)
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
    def all_objects(self): return list(dict.fromkeys(o for n in self.names for o in bpy.data.collections[n].all_objects))
coll = _Rooms()
VOLUME = lambda m: m and m.node_tree and any(n.type == 'OUTPUT_MATERIAL' and n.inputs['Volume'].is_linked for n in m.node_tree.nodes)
def bsdf(m): return next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if m and m.node_tree else None
def linked(m, name): b = bsdf(m); return bool(b and b.inputs[name].is_linked)
def const(m, name, default):
    b = bsdf(m)
    if not b: return default
    v = b.inputs[name].default_value
    return list(v)[:3] if hasattr(v, '__len__') else float(v)
def collect():
    objs = [o for o in coll.all_objects if o.type == 'MESH' and not o.hide_render and o.name not in skipped]
    mats = []
    for o in objs:
        for s_ in o.material_slots:
            if s_.material and s_.material not in mats: mats.append(s_.material)
    return objs, mats

if STAGE in ('prep', 'all'):
    objs = [o for o in coll.all_objects if o.type in ('MESH', 'CURVE', 'FONT') and not o.hide_render]
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
        b = bsdf(m)
        procedural = bool(b and any(i.is_linked for i in b.inputs)) or (m.node_tree and any(n.type in ('TEX_NOISE', 'TEX_VORONOI', 'AMBIENT_OCCLUSION', 'BEVEL') for n in m.node_tree.nodes))
        emits = bool(b and (b.inputs['Emission Color'].is_linked or b.inputs['Emission Strength'].is_linked or
                            (b.inputs['Emission Strength'].default_value > 0 and max(list(b.inputs['Emission Color'].default_value)[:3]) > 0)))
        plan[m.name] = dict(bake=procedural, metallic_map=linked(m, 'Metallic'), emission=emits, principled=b is not None)

    # --- UVs: one atlas per material ---------------------------------------------------------------------------------------------------------------------
    for o in objs:
        uv = o.data.uv_layers.get('UVBake') or o.data.uv_layers.new(name='UVBake')
        o.data.uv_layers.active = uv; uv.active_render = True
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
    json.dump(dict(plan=plan, skipped=skipped, triangles=tris, objects=len(objs), log=log), open(PLAN, 'w'), indent=1)
    bpy.ops.wm.save_as_mainfile(filepath=WORK, relative_remap=True, copy=True)
    step('prep saved', work=os.path.basename(WORK))
    if STAGE == 'prep': raise SystemExit(0)
else:
    _p = json.load(open(PLAN)); plan, skipped, tris = _p['plan'], _p['skipped'], _p['triangles']; log['steps'] = _p['log']['steps']
    objs, mats = collect()

if STAGE in ('bake', 'all'):
    # --- bake -------------------------------------------------------------------------------------------------------------------------------------------
    sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = False; sc.cycles.device = 'CPU'
    if DEVICE in ('auto', 'GPU'):
        cp = bpy.context.preferences.addons['cycles'].preferences
        for backend in ('HIP', 'OPTIX', 'CUDA', 'ONEAPI', 'METAL'):
            try: cp.compute_device_type = backend
            except TypeError: continue
            cp.get_devices(); gpus = [d for d in cp.devices if d.type == backend]
            if gpus:
                for d in cp.devices: d.use = d.type == backend
                sc.cycles.device = 'GPU'; step('device', backend=backend, gpus=[d.name for d in gpus]); break
        if sc.cycles.device != 'GPU':
            step('device', backend='CPU', note='no GPU backend found' + ('' if DEVICE == 'auto' else ': GPU was asked for'))
    if NODE_SAMPLES:
        for m in mats:
            for n_ in (m.node_tree.nodes if m.node_tree else []):
                if n_.type in ('AMBIENT_OCCLUSION', 'BEVEL'): n_.samples = min(n_.samples, NODE_SAMPLES)
    bk = sc.render.bake; bk.margin = 8; bk.margin_type = 'EXTEND'; bk.use_clear = True; bk.use_selected_to_active = False
    dummy = bpy.data.images.new('_bake_dummy', 8, 8)
    imgs = {}
    def image(mname, kind, colour):
        s = plan[mname]['size']; im = bpy.data.images.new('%s_%s' % (mname, kind), s, s, alpha=False, float_buffer=False)
        im.colorspace_settings.name = 'sRGB' if colour else 'Non-Color'; imgs[(mname, kind)] = im; return im
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
        bpy.ops.object.bake(type=btype, **kw); step('baked ' + kind, seconds=round(time.time() - t, 1))
    for o in bpy.data.objects: o.select_set(False)
    for o in objs: o.select_set(True)
    vl.objects.active = objs[0]
    def save_raw(kind):
        for (mn, k), im in imgs.items():
            if k == kind: im.filepath_raw = os.path.join(RAW, '%s_%s.png' % (mn.replace(' ', '_').replace('/', '_'), k)); im.file_format = 'PNG'; im.save()
    def want(p): return STAGE == 'all' or PASS == p
    # base colour, roughness, metallic and emission through the material output: temporarily route the socket's source into an Emission shader and bake EMIT.
    # Not the DIFFUSE colour pass for base colour: Cycles scales that pass by (1 - metallic), so metal surfaces came out darker and Unity then applied metallic
    # again (pilot 2026-10-16: baked renders 8 to 19 % darker, worst on the pump motor; after the fix within 1.5 %).
    def via_emission(socket_name, kind, colour, wanted):
        saved = {}
        for m in mats:
            b = bsdf(m)
            if not (plan[m.name]['bake'] and wanted(m) and b): continue
            nt = m.node_tree; out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output)
            old = out.inputs['Surface'].links[0].from_socket if out.inputs['Surface'].is_linked else None
            e = nt.nodes.new('ShaderNodeEmission'); e.name = '_bake_emit'; e.inputs['Strength'].default_value = 1.0
            if socket_name in ('Metallic', 'Base Color', 'Roughness'):
                i_ = b.inputs[socket_name]
                if i_.is_linked: nt.links.new(i_.links[0].from_socket, e.inputs['Color'])
                else: v_ = i_.default_value; e.inputs['Color'].default_value = (list(v_)[:3] + [1.0]) if hasattr(v_, '__len__') else (v_, v_, v_, 1.0)
            else:
                if b.inputs['Emission Color'].is_linked: nt.links.new(b.inputs['Emission Color'].links[0].from_socket, e.inputs['Color'])
                else: e.inputs['Color'].default_value = b.inputs['Emission Color'].default_value
                if b.inputs['Emission Strength'].is_linked: nt.links.new(b.inputs['Emission Strength'].links[0].from_socket, e.inputs['Strength'])
                else: e.inputs['Strength'].default_value = b.inputs['Emission Strength'].default_value
            nt.links.new(e.outputs[0], out.inputs['Surface']); saved[m.name] = (out, old, e)
        if saved: run(kind, 'EMIT', colour=colour, wanted=lambda m: m.name in saved)
        for n, (out, old, e) in saved.items():
            nt = bpy.data.materials[n].node_tree
            if old is not None: nt.links.new(old, out.inputs['Surface'])
            nt.nodes.remove(e)
    if want('base'): via_emission('Base Color', 'base', True, lambda m: True); save_raw('base')
    if want('rough'): via_emission('Roughness', 'rough', False, lambda m: True); save_raw('rough')
    if want('normal'): run('normal', 'NORMAL', colour=False, normal_space='TANGENT', normal_r='POS_X', normal_g='POS_Y', normal_b='POS_Z'); save_raw('normal')
    if want('metal'): via_emission('Metallic', 'metal', False, lambda m: plan[m.name]['metallic_map']); save_raw('metal')
    if want('emit'): via_emission('Emission', 'emit', True, lambda m: plan[m.name]['emission']); save_raw('emit')


    if STAGE == 'bake': raise SystemExit(0)

# --- write the URP map set ---------------------------------------------------------------------------------------------------------------------------
TEX = os.path.join(OUT, 'textures')
if STAGE == 'finish':
    imgs = {}
    for m in mats:
        for k in ('base', 'rough', 'normal', 'metal', 'emit'):
            f = os.path.join(RAW, '%s_%s.png' % (m.name.replace(' ', '_').replace('/', '_'), k))
            if plan[m.name]['bake'] and os.path.exists(f):
                im = bpy.data.images.load(f); im.colorspace_settings.name = 'sRGB' if k in ('base', 'emit') else 'Non-Color'; imgs[(m.name, k)] = im
    dummy = bpy.data.images.new('_bake_dummy', 8, 8)
    for m in mats:
        n_ = m.node_tree.nodes.get('_bake_target') if m.node_tree else None
        if n_: m.node_tree.nodes.remove(n_)
def px(im): a_ = np.empty(len(im.pixels), np.float32); im.pixels.foreach_get(a_); return a_.reshape(im.size[1], im.size[0], 4)
def save(arr, name, colour):
    h, w = arr.shape[:2]; im = bpy.data.images.new(name, w, h, alpha=True); im.colorspace_settings.name = 'sRGB' if colour else 'Non-Color'
    im.pixels.foreach_set(arr.astype(np.float32).ravel()); im.filepath_raw = os.path.join(TEX, name + '.png'); im.file_format = 'PNG'; im.save(); return im
manifest = {}
for m in mats:
    p = plan[m.name]; safe = m.name.replace(' ', '_').replace('/', '_'); e = dict(source_material=m.name, urp_shader='Universal Render Pipeline/Lit')
    if p['bake']:
        base = px(imgs[(m.name, 'base')]); rough = px(imgs[(m.name, 'rough')])[..., 0]
        metal = px(imgs[(m.name, 'metal')])[..., 0] if (m.name, 'metal') in imgs else np.full(rough.shape, float(const(m, 'Metallic', 0.0)), np.float32)
        base[..., 3] = 1.0; save(base, safe + '_BaseMap', True)
        mg = np.zeros(base.shape, np.float32); mg[..., 0] = metal; mg[..., 1] = metal; mg[..., 2] = metal; mg[..., 3] = 1.0 - rough; save(mg, safe + '_MetallicGlossMap', False)
        nrm = px(imgs[(m.name, 'normal')]); nrm[..., 3] = 1.0; save(nrm, safe + '_BumpMap', False)
        e.update(_BaseMap='textures/%s_BaseMap.png' % safe, _MetallicGlossMap='textures/%s_MetallicGlossMap.png' % safe, _BumpMap='textures/%s_BumpMap.png' % safe,
                 _Smoothness_source='MetallicGlossMap alpha', size=p['size'], area_m2=p['area_m2'], approx_px_per_m=p['px_per_m'])
        if (m.name, 'emit') in imgs:
            em = px(imgs[(m.name, 'emit')]); peak = float(em[..., :3].max()) or 1.0; em[..., :3] /= max(peak, 1e-6); em[..., 3] = 1.0
            save(em, safe + '_EmissionMap', True); e.update(_EmissionMap='textures/%s_EmissionMap.png' % safe, _EmissionColor_intensity=round(peak, 3))
    else:
        e.update(_BaseColor=const(m, 'Base Color', [0.8, 0.8, 0.8]), _Metallic=const(m, 'Metallic', 0.0), _Smoothness=round(1 - const(m, 'Roughness', 0.5), 3))
        if p['emission']: e.update(_EmissionColor=const(m, 'Emission Color', [0, 0, 0]), _EmissionColor_intensity=const(m, 'Emission Strength', 0.0))
        if const(m, 'Alpha', 1.0) < 1.0 or (bsdf(m) and bsdf(m).inputs['Transmission Weight'].default_value > 0): e['_Surface'] = 'Transparent'
    manifest[m.name] = e
step('maps written', materials=len(manifest), textures=len(os.listdir(TEX)))

# --- swap to the image materials (what Unity gets), keep only UVBake, save and export -------------------------------------------------------------------
def unity_mat(m):
    e = manifest[m.name]; u = bpy.data.materials.new('U_' + m.name); u.use_nodes = True; nt = u.node_tree; b = nt.nodes['Principled BSDF']
    def tex(path, colour):
        n = nt.nodes.new('ShaderNodeTexImage'); n.image = bpy.data.images.load(os.path.join(OUT, path)); n.image.colorspace_settings.name = 'sRGB' if colour else 'Non-Color'
        uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'UVBake'; nt.links.new(uvn.outputs[0], n.inputs[0]); return n
    if '_BaseMap' in e:
        nt.links.new(tex(e['_BaseMap'], True).outputs['Color'], b.inputs['Base Color'])
        mg = tex(e['_MetallicGlossMap'], False); sep = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(mg.outputs['Color'], sep.inputs[0])
        nt.links.new(sep.outputs[0], b.inputs['Metallic']); inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
        nt.links.new(mg.outputs['Alpha'], inv.inputs[1]); nt.links.new(inv.outputs[0], b.inputs['Roughness'])
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.uv_map = 'UVBake'; nt.links.new(tex(e['_BumpMap'], False).outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs[0], b.inputs['Normal'])
        if '_EmissionMap' in e:
            nt.links.new(tex(e['_EmissionMap'], True).outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = e['_EmissionColor_intensity']
    else:
        b.inputs['Base Color'].default_value = list(e['_BaseColor']) + [1.0]; b.inputs['Metallic'].default_value = e['_Metallic']; b.inputs['Roughness'].default_value = 1 - e['_Smoothness']
        if '_EmissionColor' in e: b.inputs['Emission Color'].default_value = list(e['_EmissionColor']) + [1.0]; b.inputs['Emission Strength'].default_value = e['_EmissionColor_intensity']
        src = bsdf(m)
        if src: b.inputs['Alpha'].default_value = src.inputs['Alpha'].default_value; b.inputs['Transmission Weight'].default_value = src.inputs['Transmission Weight'].default_value
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
    if o.type != 'LIGHT': continue
    d = o.data; l = dict(name=o.name, type=d.type, location=[round(v, 4) for v in o.matrix_world.translation], rotation_euler_deg=[round(math.degrees(v), 2) for v in o.matrix_world.to_euler()],
                         color=[round(v, 4) for v in d.color], energy_blender=round(d.energy, 3), shadow=d.use_shadow)
    if d.type == 'SPOT': l.update(spot_angle_deg=round(math.degrees(d.spot_size), 2), spot_blend=round(d.spot_blend, 3))
    if d.type == 'AREA': l.update(shape=d.shape, size=[round(d.size, 3), round(getattr(d, 'size_y', d.size), 3)])
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
