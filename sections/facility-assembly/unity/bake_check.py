"""Check one baked room before the next one starts (bake_room.ps1 stage 'check', after finish). Opens <out>/<room>_unity.blend:

    blender -b --factory-startup <out>/<room>_unity.blend --python bake_check.py -- --out <out>

Exits non-zero, listing every problem, when any of these fail (2026-10-18: a run of eight rooms went 12 hours before anyone saw that every map bake
held the whole map; nothing may pass silently again):
  * content: everything that renders in the scene is in the room's collections (bake_report.json), and the object and triangle counts match the plan;
  * materials.json: every exported material has an entry, every texture it names exists at the planned size and holds finite values, base colour
    is not black throughout, alpha below 1 only on materials marked Transparent, emission intensities finite and positive;
  * lights.json: exactly the render-visible lights of the room, with finite values;
  * the FBX, imported again: same meshes, triangles and bounds (within 1 cm) as the scene, UVBake its only UV layer, only U_ materials known to
    materials.json, no NaN positions.
Writes <out>/bake_check.json either way."""
import bpy, sys, os, json, math
import numpy as np
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = os.path.abspath(a[a.index('--out') + 1])
report = json.load(open(os.path.join(OUT, 'bake_report.json')))
mats_json = json.load(open(os.path.join(OUT, 'materials.json')))['materials']
lights_json = json.load(open(os.path.join(OUT, 'lights.json')))['lights']
plan = json.load(open(os.path.join(OUT, '_plan.json')))
room = report['room']; names = report['collection'].split(',')
bad, info = [], {}
def fail(msg): bad.append(msg); print('CHECK FAIL', msg, flush=True)

# --- content ----------------------------------------------------------------------------------------------------------------------------------------
def walk(c, out):
    if c.hide_render: return
    out.update(c.objects)
    for ch in c.children: walk(ch, out)
members = set()
for n in names:
    if bpy.data.collections.get(n) is None: fail('collection %s is not in %s' % (n, os.path.basename(bpy.data.filepath)))
    else: walk(bpy.data.collections[n], members)
vl = bpy.context.view_layer
room_all = set()                                                 # including render-hidden collections (the mine's CC0 sources): they do not render
def under(c):
    room_all.update(c.objects)
    for ch in c.children: under(ch)
for n in names:
    if bpy.data.collections.get(n) is not None: under(bpy.data.collections[n])
foreign = sorted(o.name for o in vl.objects if o not in room_all and o.type != 'CAMERA' and not o.hide_render)
if foreign: fail('%d objects render that are not in the room collections (the map leaking into the bake?): %s' % (len(foreign), foreign[:12]))
dg = bpy.context.evaluated_depsgraph_get()
# real instancing only: another object drawn by a render-visible instancer (a curve or text object's own geometry is listed as an instance of itself)
inst = sorted({'%s by %s' % (i.object.name, i.parent.name) for i in dg.object_instances
               if i.is_instance and i.parent and i.parent.original is not i.object.original and not i.parent.original.hide_render})
if inst: fail('instances still render (instancers not made real?): %s' % inst[:8])
meshes = [o for o in members if o.type == 'MESH' and not o.hide_render and len(o.data.polygons)]
tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes)
info.update(meshes=len(meshes), triangles=tris)
if len(meshes) != report['objects']: fail('mesh objects %d, plan %d' % (len(meshes), report['objects']))
if tris != report['triangles']: fail('triangles %d, plan %d' % (tris, report['triangles']))

# --- materials and textures -------------------------------------------------------------------------------------------------------------------------
used = {s.material.name for o in meshes for s in o.material_slots if s.material}
known = {'U_' + k for k in mats_json}
if used - known: fail('materials without a materials.json entry: %s' % sorted(used - known)[:12])
if any(not n.startswith('U_') for n in used): fail('procedural materials left on meshes: %s' % sorted(n for n in used if not n.startswith('U_'))[:12])
def px(path):
    im = bpy.data.images.load(path); arr = np.empty(len(im.pixels), np.float32); im.pixels.foreach_get(arr)
    arr = arr.reshape(im.size[1], im.size[0], 4); size = tuple(im.size); bpy.data.images.remove(im); return arr, size
texs = 0; transparent = 0
for name, e in mats_json.items():
    p = plan['plan'][name]
    if p['bake']:
        for k in ('_BaseMap', '_MetallicGlossMap', '_BumpMap'):
            if k not in e: fail('%s: baked but no %s' % (name, k))
    for k in ('_BaseMap', '_MetallicGlossMap', '_BumpMap', '_EmissionMap'):
        if k not in e: continue
        f = os.path.join(OUT, e[k])
        if not os.path.isfile(f): fail('%s: %s missing (%s)' % (name, k, e[k])); continue
        arr, size = px(f); texs += 1
        if size != (p['size'], p['size']): fail('%s: %s is %s, planned %d' % (name, k, size, p['size']))
        if not np.isfinite(arr).all(): fail('%s: %s has NaN or Inf' % (name, k))
        if k == '_BaseMap':
            see = float((arr[..., 3] < 0.98).mean())
            if see > 0 and e.get('_Surface') != 'Transparent': fail('%s: base map alpha below 1 on an opaque material' % name)
            if e.get('_Surface') == 'Transparent' and see == 0: fail('%s: marked Transparent but its base map alpha is 1 throughout' % name)
            if float(arr[..., :3].max()) < 0.002 and not e.get('_PreserveSpecular') and any(c not in ('EMISSION', 'BSDF_TRANSPARENT', 'HOLDOUT') for c in p['closures']):   # clear glass is black by design
                fail('%s: base colour is black throughout' % name)
        if k == '_BumpMap' and abs(float(arr[..., 2].mean()) - 1.0) > 0.5: fail('%s: normal map blue channel averages %.2f (not a tangent-space normal map?)' % (name, float(arr[..., 2].mean())))
    if e.get('_Surface') == 'Transparent': transparent += 1
    for k in ('_EmissionColor_intensity',):
        if k in e and not (math.isfinite(e[k]) and 0 <= e[k] < 1e4): fail('%s: %s = %r' % (name, k, e[k]))
    if '_EmissionMap' in e and not e.get('_EmissionColor_intensity', 0) > 0: fail('%s: emission map with no intensity' % name)
    if p['bake'] and p['emission'] and '_EmissionMap' not in e: print('CHECK note %s: planned emission baked to black (no map written)' % name)
info.update(materials=len(mats_json), textures_checked=texs, transparent=transparent)

# --- lights -----------------------------------------------------------------------------------------------------------------------------------------
want_lights = sorted(o.name for o in members if o.type == 'LIGHT' and not o.hide_render)
got_lights = sorted(l['name'] for l in lights_json)
if want_lights != got_lights: fail('lights.json has %d lights, the room renders %d (missing %s, extra %s)' % (len(got_lights), len(want_lights),
                                   sorted(set(want_lights) - set(got_lights))[:6], sorted(set(got_lights) - set(want_lights))[:6]))
for l in lights_json:
    vals = l['location'] + l['rotation_euler_deg'] + l['color'] + [l['energy_blender']]
    if not all(math.isfinite(v) for v in vals): fail('light %s has a non-finite value' % l['name'])
info.update(lights=len(lights_json))

# --- FBX round trip -----------------------------------------------------------------------------------------------------------------------------------
def bounds(objs):
    lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
    for o in objs:
        me = o.data; co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        if not len(co): continue
        m = np.array(o.matrix_world); w = co @ m[:3, :3].T + m[:3, 3]
        lo = np.minimum(lo, w.min(0)); hi = np.maximum(hi, w.max(0))
    return lo, hi
blo, bhi = bounds(meshes)
fbx = os.path.join(OUT, report['fbx'])
sc = bpy.data.scenes.new('_fbx_check'); bpy.context.window.scene = sc if bpy.context.window else None
with bpy.context.temp_override(scene=sc, view_layer=sc.view_layers[0]):
    bpy.ops.import_scene.fbx(filepath=fbx)
imp = [o for o in sc.objects if o.type == 'MESH']
itris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in imp)
if len(imp) != len(meshes): fail('FBX holds %d meshes, the scene %d' % (len(imp), len(meshes)))
if itris != tris: fail('FBX holds %d triangles, the scene %d' % (itris, tris))
uvs = {tuple(u.name for u in o.data.uv_layers) for o in imp}
if uvs != {('UVBake',)}: fail('FBX UV layers %s (want UVBake only)' % sorted(uvs)[:4])
import re                                                         # the importer may add .001 to a name it already holds; a dot inside a name is kept
fm = {s.material.name if s.material.name in known else re.sub(r'\.\d{3}$', '', s.material.name) for o in imp for s in o.material_slots if s.material}
stripped = {re.sub(r'\.\d+$', '', k) for k in known}             # Blender's FBX importer drops a trailing .5 ('lens -1.5'); the FBX itself keeps it
if fm - known - stripped: fail('FBX materials not in materials.json: %s' % sorted(fm - known - stripped)[:8])
nan = [o.name for o in imp if len(o.data.vertices) and not np.isfinite(np.array([v.co[:] for v in o.data.vertices[:1000]])).all()]
if nan: fail('FBX meshes with NaN positions: %s' % nan[:6])
ilo, ihi = bounds(imp)
if len(imp) and (np.abs(ilo - blo).max() > 0.01 or np.abs(ihi - bhi).max() > 0.01):
    fail('FBX bounds %s..%s differ from the scene %s..%s by more than 1 cm' % (np.round(ilo, 3).tolist(), np.round(ihi, 3).tolist(), np.round(blo, 3).tolist(), np.round(bhi, 3).tolist()))
info.update(fbx_meshes=len(imp), fbx_triangles=itris, bounds=[np.round(blo, 3).tolist(), np.round(bhi, 3).tolist()])

json.dump(dict(room=room, ok=not bad, problems=bad, **info), open(os.path.join(OUT, 'bake_check.json'), 'w'), indent=1)
print('CHECK', room, 'OK' if not bad else 'FAILED (%d problems)' % len(bad), info, flush=True)
if bad: raise SystemExit(1)
