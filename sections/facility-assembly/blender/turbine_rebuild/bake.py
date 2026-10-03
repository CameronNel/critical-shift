"""FINAL STEP ONLY - not part of authoring and not run for the current rebuild.
Baking lighting is the last production step: run this only after geometry, UV0 materials and live lighting are accepted,
and re-run it after any later change to them.

Unwrap lightmap UVs, bake direct+indirect lighting to float lightmaps, denoise, and build the baked-preview materials.

blender -b IN.blend --python-exit-code 1 --python bake.py -- OUT_DIR [--samples N] [--scale S] [--skip-bake]
Outputs: OUT_DIR/lightmaps/LM_<GROUP>.exr (+ _preview.png), turbine_room_v2_baked.blend, bake_report.json
"""
import sys, os, json, math, time
import bpy, bmesh
import numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
OUT = os.path.abspath(a[0]); os.makedirs(os.path.join(OUT, 'lightmaps'), exist_ok=True)
SAMPLES = int(a[a.index('--samples') + 1]) if '--samples' in a else 128
SCALE = float(a[a.index('--scale') + 1]) if '--scale' in a else 1.0
SKIP = '--skip-bake' in a
sc = bpy.context.scene
RES = {'TURBINE_ARCH': 2048, 'TURBINE_MACH': 2048, 'TURBINE_PROPS': 1024, 'ANIM_TURBINE_SHAFT': 256}
report = dict(samples=SAMPLES, groups={})

PAD = 3
def unwrap(ob, res):
    """Deterministic lightmap layout: every face is its own island (edge-aligned planar basis) at one uniform
    texel density, shelf-packed into the square; the largest density that fits is used. Big faces are capped."""
    from mathutils import Vector
    me = ob.data
    if 'LightmapUV' in me.uv_layers: me.uv_layers.remove(me.uv_layers['LightmapUV'])
    lm = me.uv_layers.new(name='LightmapUV')
    items = []
    for p in me.polygons:
        vs = [me.vertices[i].co for i in p.vertices]; n = p.normal
        e = None
        for k in range(len(vs)):
            d = vs[(k + 1) % len(vs)] - vs[k]; d = d - n * d.dot(n)
            if d.length > 1e-6: e = d.normalized(); break
        if e is None: e = Vector((1, 0, 0)) if abs(n.x) < .9 else Vector((0, 1, 0))
        v = n.cross(e); us = [x.dot(e) for x in vs]; vv = [x.dot(v) for x in vs]
        items.append((p.index, max(us) - min(us), max(vv) - min(vv), e, v, min(us), min(vv)))
    cap = res * 0.40
    def layout(D):
        sizes = []
        for it in items:
            m = max(it[1], it[2], 1e-6); dp = min(D, cap / m)
            sizes.append((it[0], dp, int(math.ceil(it[1] * dp)) + 2 * PAD, int(math.ceil(it[2] * dp)) + 2 * PAD))
        sizes.sort(key=lambda s: -s[3])
        x = y = rowh = 0; pos = {}
        for idx, dp, w, h in sizes:
            if x + w > res: x = 0; y += rowh; rowh = 0
            if y + h > res: return None
            pos[idx] = (x, y, dp); x += w; rowh = max(rowh, h)
        return pos
    lo, hi, best = 2.0, 600.0, None
    for _ in range(16):
        mid = (lo * hi) ** .5; got = layout(mid)
        if got: lo, best = mid, got
        else: hi = mid
    pos = best or layout(lo)
    used = 0
    for it in items:
        idx, w, h, e, v, u0, v0 = it; x, y, dp = pos[idx]; p = me.polygons[idx]
        used += (int(math.ceil(w * dp)) + 2 * PAD) * (int(math.ceil(h * dp)) + 2 * PAD)
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            lm.data[li].uv = ((x + PAD + (co.dot(e) - u0) * dp) / res, (y + PAD + (co.dot(v) - v0) * dp) / res)
    me.uv_layers.active = lm
    return dict(faces=len(me.polygons), world_area_m2=round(sum(p.area for p in me.polygons), 1), texels_per_m=round(lo, 1), packing_utilisation=round(used / (res * res), 3))

def add_bake_node(mat, img):
    nt = mat.node_tree; n = nt.nodes.get('LIGHTMAP') or nt.nodes.new('ShaderNodeTexImage')
    n.name = 'LIGHTMAP'; n.image = img; n.location = (-250, -400); nt.nodes.active = n; n.select = True

t0 = time.time()
objs = {o.name: o for o in bpy.data.objects if o.name in RES}
occ = bpy.data.objects.get('OCCLUDER_ONLY')
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = False
sc.cycles.max_bounces = 6; sc.cycles.diffuse_bounces = 5; sc.cycles.sample_clamp_indirect = 8.0
sc.view_settings.view_transform = 'Standard'
imgs = {}
for name, ob in objs.items():
    res = int(RES[name] * SCALE)
    report['groups'][name] = unwrap(ob, RES[name])
    img = bpy.data.images.new('LM_' + name, res, res, alpha=False, float_buffer=True); img.colorspace_settings.name = 'Linear Rec.709'
    img.generated_color = (0, 0, 0, 1); imgs[name] = img
    for slot in ob.material_slots: add_bake_node(slot.material, img)
    report['groups'][name]['lightmap_px'] = res
print('UNWRAP', json.dumps(report['groups']), round(time.time() - t0))

if not SKIP:
    for name, ob in objs.items():
        t1 = time.time()
        bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active = ob
        ob.data.uv_layers.active = ob.data.uv_layers['LightmapUV']
        for slot in ob.material_slots: add_bake_node(slot.material, imgs[name])
        bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, margin=PAD, margin_type='EXTEND', use_clear=True)
        report['groups'][name]['bake_seconds'] = round(time.time() - t1)
        print('BAKED', name, report['groups'][name]['bake_seconds'], 's')
        p = os.path.join(OUT, 'lightmaps', f'RAW_{name}.exr'); imgs[name].filepath_raw = p; imgs[name].file_format = 'OPEN_EXR'; imgs[name].save()

# ---- denoise through a throwaway compositor scene (OIDN), then save runtime EXR + preview PNG ----
def denoise(name):
    raw = os.path.join(OUT, 'lightmaps', f'RAW_{name}.exr'); res = imgs[name].size[0]
    ds = bpy.data.scenes.new('dn'); ds.render.engine = 'CYCLES'; ds.cycles.samples = 1; ds.cycles.device = 'CPU'; ds.render.resolution_x = ds.render.resolution_y = res; ds.render.resolution_percentage = 100
    cd = bpy.data.cameras.new('c'); co = bpy.data.objects.new('c', cd); ds.collection.objects.link(co); ds.camera = co
    ng = bpy.data.node_groups.new('dn', 'CompositorNodeTree'); ds.compositing_node_group = ng
    ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    src = bpy.data.images.load(raw); src.colorspace_settings.name = 'Linear Rec.709'
    i = ng.nodes.new('CompositorNodeImage'); i.image = src
    d = ng.nodes.new('CompositorNodeDenoise'); o = ng.nodes.new('NodeGroupOutput')
    ng.links.new(i.outputs[0], d.inputs[0]); ng.links.new(d.outputs[0], o.inputs[0])
    ds.render.image_settings.file_format = 'OPEN_EXR'; ds.render.image_settings.color_depth = '16'; ds.render.image_settings.color_mode = 'RGB'
    path = os.path.join(OUT, 'lightmaps', f'LM_{name}.exr'); ds.render.filepath = path[:-4]; ds.render.use_file_extension = True
    bpy.ops.render.render(scene='dn', write_still=True)
    return path
final = {}
for name in objs:
    try:
        final[name] = denoise(name)
    except Exception as e:
        print('DENOISE FAILED', name, e); final[name] = os.path.join(OUT, 'lightmaps', f'RAW_{name}.exr')
    if not os.path.exists(final[name]):
        for cand in os.listdir(os.path.join(OUT, 'lightmaps')):
            if cand.startswith(f'LM_{name}') and cand.endswith('.exr'): final[name] = os.path.join(OUT, 'lightmaps', cand)
    print('FINAL', name, final[name], os.path.exists(final[name]))

# ---- baked-preview materials: albedo(UV0) x lightmap(UV1) as emission ----
for name, ob in objs.items():
    lmimg = bpy.data.images.load(final[name]); lmimg.colorspace_settings.name = 'Linear Rec.709'
    for slot in ob.material_slots:
        m = slot.material; nt = m.node_tree; emis = m.name.endswith('_emissive')
        for n in list(nt.nodes):
            if n.type in {'BSDF_PRINCIPLED', 'EMISSION', 'OUTPUT_MATERIAL', 'TEX_IMAGE', 'UVMAP', 'MIX_RGB', 'MATH'}: nt.nodes.remove(n)
        out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
        uv0 = nt.nodes.new('ShaderNodeUVMap'); uv0.uv_map = 'UVMap'; uv0.location = (-600, 100)
        uv1 = nt.nodes.new('ShaderNodeUVMap'); uv1.uv_map = 'LightmapUV'; uv1.location = (-600, -200)
        alb = nt.nodes.new('ShaderNodeTexImage'); alb.image = bpy.data.images['turbine_atlas']; alb.name = 'ALBEDO'; alb.location = (-350, 100)
        nt.links.new(uv0.outputs[0], alb.inputs[0])
        e = nt.nodes.new('ShaderNodeEmission'); e.location = (550, 0)
        if emis:
            e.inputs['Strength'].default_value = 1.0; nt.links.new(alb.outputs[0], e.inputs['Color'])
        else:
            lm = nt.nodes.new('ShaderNodeTexImage'); lm.image = lmimg; lm.name = 'LIGHTMAP'; lm.interpolation = 'Linear'; lm.location = (-350, -250)
            nt.links.new(uv1.outputs[0], lm.inputs[0])
            mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.location = (200, 0); mx.inputs['Factor'].default_value = 1.0
            nt.links.new(alb.outputs[0], mx.inputs['A']); nt.links.new(lm.outputs[0], mx.inputs['B']); nt.links.new(mx.outputs['Result'], e.inputs['Color'])
        nt.links.new(e.outputs[0], out.inputs['Surface'])
        nt.nodes.active = alb
if occ: bpy.data.objects.remove(occ, do_unlink=True)
# lights are baked in: hide the rig from the preview renders
for o in bpy.data.objects:
    if o.type == 'LIGHT': o.hide_render = True
bpy.data.worlds['W'].node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
report['total_seconds'] = round(time.time() - t0)
json.dump(report, open(os.path.join(OUT, 'bake_report.json'), 'w'), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'turbine_room_v2_baked.blend'), compress=True)
print('DONE', json.dumps(report))
