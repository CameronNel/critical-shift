"""Preview renders of the turbine room cameras.
blender -b FILE.blend --python preview.py -- OUTDIR MODE [CAM_PREFIXES...]   MODE: wb (Workbench albedo) | baked (Cycles emission of albedo*lightmap) | lit (Cycles, real lights)
"""
import sys, os, bpy
a = sys.argv[sys.argv.index('--') + 1:]; out, mode = a[0], a[1]; only = a[2:]
os.makedirs(out, exist_ok=True); sc = bpy.context.scene
import os as _o
_r = _o.environ.get('PREVIEW_RES', '1280x720' if mode == 'wb' else '960x540').split('x')
sc.render.resolution_x, sc.render.resolution_y = int(_r[0]), int(_r[1])
sc.view_settings.exposure = float(_o.environ.get('PREVIEW_EXPOSURE', '0.5'))
if mode == 'wb':
    sc.render.engine = 'BLENDER_WORKBENCH'; sh = sc.display.shading
    sh.light = 'STUDIO'; sh.color_type = 'TEXTURE'; sh.show_cavity = True; sh.cavity_type = 'BOTH'; sh.show_shadows = True; sh.shadow_intensity = .5
    for m in bpy.data.materials:
        if m.node_tree and 'ALBEDO' in m.node_tree.nodes: m.node_tree.nodes.active = m.node_tree.nodes['ALBEDO']
elif mode in ('baked', 'lit'):
    sc.render.engine = 'CYCLES'; sc.cycles.samples = 24 if mode == "baked" else 32; sc.cycles.use_denoising = True
for o in bpy.data.objects:
    if o.type == 'CAMERA' and (not only or any(o.name.startswith(p) for p in only)):
        sc.camera = o; sc.render.filepath = os.path.join(out, o.name + '.png'); bpy.ops.render.render(write_still=True)
