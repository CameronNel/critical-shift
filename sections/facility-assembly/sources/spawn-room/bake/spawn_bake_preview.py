"""Stage 3 of the spawn-room material bake: baked-only materials and a preview.

Blender 5.2.2 LTS, on the stage 1 derivative:
  blender --background --disable-autoexec -noaudio PREP.blend --python-exit-code 1 \
    --python spawn_bake_preview.py -- --maps DIR --out DIR2 --cams REFERENCE_HALL,REFERENCE_BRIEFING,REFERENCE_LOCKER --samples 64 [--save PREVIEW.blend]

Every opaque, non-emissive procedural or image-driven material slot is replaced by one material
per atlas that reads only the baked maps (albedo; packed roughness R, metallic G, specular level B;
tangent normal) through the 'BAKE' UVs, the way a game engine material would. Emissive, glass,
special-shader and plain single-colour slots, and objects outside the bake, are left as they are. Lights are the room's authored lights, standing in for the
lighting a game engine scene would recreate. This is a Blender render of baked-only materials,
a stand-in for an engine view: it is not an engine screenshot and does not model engine
lighting, post-processing or shader differences.
"""
import argparse
import sys
import time
from pathlib import Path

import bpy

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument('--maps', type=Path, required=True)
ap.add_argument('--out', type=Path, required=True)
ap.add_argument('--cams', default='REFERENCE_HALL,REFERENCE_BRIEFING,REFERENCE_LOCKER')
ap.add_argument('--samples', type=int, default=64)
ap.add_argument('--save', type=Path)
ap.add_argument('--tag', default='spawn_baked')
args = ap.parse_args(argv)
args.out.mkdir(parents=True, exist_ok=True)

PROC = ('TEX_NOISE', 'TEX_VORONOI', 'TEX_WAVE', 'TEX_MUSGRAVE', 'TEX_BRICK', 'TEX_CHECKER',
        'TEX_GRADIENT', 'BEVEL', 'AMBIENT_OCCLUSION', 'TEX_MAGIC', 'TEX_IMAGE', 'BUMP', 'NORMAL_MAP')


def is_procedural(mat):
    """Same rule as spawn_bake_prep.py: opaque, non-emissive Principled root with procedural or image inputs."""
    if not (mat and mat.use_nodes):
        return False
    nodes = mat.node_tree.nodes
    bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
    out = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output), None)
    root = out.inputs['Surface'].links[0].from_node if out and out.inputs['Surface'].links else None
    if bsdf is None or root is None or root.type != 'BSDF_PRINCIPLED':
        return False
    ec, es = bsdf.inputs['Emission Color'], bsdf.inputs['Emission Strength']
    if es.default_value > 0.001 and (es.is_linked or ec.is_linked or sum(ec.default_value[:3]) > 0.001):
        return False
    t, a = bsdf.inputs['Transmission Weight'], bsdf.inputs['Alpha']
    if t.is_linked or t.default_value > 0.01 or a.is_linked or a.default_value < 0.999:
        return False
    return any(n.type in PROC for n in nodes)


def load(name, colorspace):
    path = args.maps / f'{name}.png'
    assert path.exists(), f'missing bake {path}'
    img = bpy.data.images.load(str(path), check_existing=False)
    img.colorspace_settings.name = colorspace
    img.pack()
    return img


def baked_material(k):
    mat = bpy.data.materials.new(f'SPAWN_BAKED_A{k}')
    mat.use_nodes = True
    t = mat.node_tree
    t.nodes.clear()
    out = t.nodes.new('ShaderNodeOutputMaterial')
    bsdf = t.nodes.new('ShaderNodeBsdfPrincipled')
    uv = t.nodes.new('ShaderNodeUVMap')
    uv.uv_map = 'BAKE'

    def tex(img):
        n = t.nodes.new('ShaderNodeTexImage')
        n.image = img
        n.interpolation = 'Linear'
        n.extension = 'EXTEND'
        t.links.new(uv.outputs['UV'], n.inputs['Vector'])
        return n

    albedo = tex(load(f'spawn_a{k}_albedo', 'sRGB'))
    rm = tex(load(f'spawn_a{k}_rm', 'Non-Color'))
    nrm = tex(load(f'spawn_a{k}_normal', 'Non-Color'))
    sep = t.nodes.new('ShaderNodeSeparateColor')
    nmap = t.nodes.new('ShaderNodeNormalMap')
    nmap.space = 'TANGENT'
    nmap.uv_map = 'BAKE'
    t.links.new(albedo.outputs['Color'], bsdf.inputs['Base Color'])
    t.links.new(rm.outputs['Color'], sep.inputs['Color'])
    t.links.new(sep.outputs['Red'], bsdf.inputs['Roughness'])
    t.links.new(sep.outputs['Green'], bsdf.inputs['Metallic'])
    t.links.new(sep.outputs['Blue'], bsdf.inputs['Specular IOR Level'])
    t.links.new(nrm.outputs['Color'], nmap.inputs['Color'])
    t.links.new(nmap.outputs['Normal'], bsdf.inputs['Normal'])
    t.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


materials = {}
replaced = slots = 0
for o in bpy.data.objects:
    if o.type != 'MESH' or 'bake_atlas' not in o:
        continue
    k = int(o['bake_atlas'])
    mat = materials.get(k) or materials.setdefault(k, baked_material(k))
    for slot in o.material_slots:
        slots += 1
        if is_procedural(slot.material):
            slot.material = mat
            replaced += 1
print('BAKED_MATERIALS', len(materials), 'slots replaced', replaced, 'of', slots)

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = args.samples
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 960, 540, 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
if args.save:
    bpy.ops.wm.save_as_mainfile(filepath=str(args.save), compress=True)
    print('SAVED', args.save)
for cam in args.cams.split(','):
    t0 = time.time()
    scene.camera = bpy.data.objects[cam]
    scene.render.filepath = str(args.out / f'{args.tag}_{cam}.png')
    bpy.ops.render.render(write_still=True)
    print('RENDERED', cam, round(time.time() - t0), 's', scene.render.filepath)
print('PREVIEW_DONE')
