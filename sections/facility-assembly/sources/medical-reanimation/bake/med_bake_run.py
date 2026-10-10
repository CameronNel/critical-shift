"""Stage 2 of the medical-reanimation material bake: bake PBR maps per atlas.

Blender 5.2.2 LTS, CPU Cycles:
  blender --background --disable-autoexec -noaudio PREP.blend --python-exit-code 1 \
    --python med_bake_run.py -- --out DIR --atlas 0 1 --maps albedo rough metal normal --samples 128 --seed 1

Each map is a deterministic channel bake, not a lighting bake: base colour, roughness and
metallic are routed through a temporary Emission shader and baked with EMIT; the tangent
normal is baked from the shader normal (bump included). No light, shadow or AO is baked.
Bevel and ambient-occlusion nodes in the edge-wear shaders are stochastic, so albedo and
roughness use many samples; the seed is fixed so a bake is repeatable.
"""
import argparse
import sys
import time
from pathlib import Path

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument('--out', type=Path, required=True)
ap.add_argument('--atlas', type=int, nargs='+', required=True)
ap.add_argument('--maps', nargs='+', default=['albedo', 'rm', 'normal'])
ap.add_argument('--samples', type=int, default=128)
ap.add_argument('--seed', type=int, default=1)
ap.add_argument('--size', type=int, default=2048)
ap.add_argument('--suffix', default='')
ap.add_argument('--prune', type=float, default=0.1, help='hide objects farther than this (m) from the atlas group; 0 keeps everything')
args = ap.parse_args(argv)
args.out.mkdir(parents=True, exist_ok=True)

scene = bpy.context.scene
view_layer = bpy.context.view_layer
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = args.samples
scene.cycles.seed = args.seed
scene.cycles.use_denoising = False
scene.render.bake.margin = 4
scene.render.bake.margin_type = 'EXTEND'
scene.render.bake.use_clear = True
scene.render.bake.normal_space = 'TANGENT'
scene.render.bake.target = 'IMAGE_TEXTURES'

COLOR_SPACE = {'albedo': 'sRGB', 'rough': 'Non-Color', 'metal': 'Non-Color', 'rm': 'Non-Color', 'normal': 'Non-Color'}
FALLBACK = {'albedo': (0.5, 0.5, 0.5, 1.0), 'rough': 0.5, 'metal': 0.0}
SOCKET = {'albedo': 'Base Color', 'rough': 'Roughness', 'metal': 'Metallic'}
non_principled = set()


def surface_bsdf(mat):
    out = next((n for n in mat.node_tree.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output), None)
    if out and out.inputs['Surface'].links:
        node = out.inputs['Surface'].links[0].from_node
        if node.type == 'BSDF_PRINCIPLED':
            return out, node
    non_principled.add(mat.name)
    return out, None


def prepare(mat):
    nodes = mat.node_tree.nodes
    tex = nodes.get('BAKE_TEX') or nodes.new('ShaderNodeTexImage')
    tex.name = 'BAKE_TEX'
    emit = nodes.get('BAKE_EMIT') or nodes.new('ShaderNodeEmission')
    emit.name = 'BAKE_EMIT'
    return tex, emit


def route(mat, emit, channel):
    out, bsdf = surface_bsdf(mat)
    tree = mat.node_tree
    for link in list(emit.inputs['Color'].links):
        tree.links.remove(link)
    emit.inputs['Strength'].default_value = 1.0
    if channel == 'rm':                       # packed: R roughness, G metallic
        comb = tree.nodes.get('BAKE_RM') or tree.nodes.new('ShaderNodeCombineColor')
        comb.name = 'BAKE_RM'
        for link in list(comb.inputs['Red'].links) + list(comb.inputs['Green'].links):
            tree.links.remove(link)
        for chan, sock_name, default in (('Red', 'Roughness', 0.5), ('Green', 'Metallic', 0.0)):
            if bsdf is not None and bsdf.inputs[sock_name].links:
                tree.links.new(bsdf.inputs[sock_name].links[0].from_socket, comb.inputs[chan])
            else:
                comb.inputs[chan].default_value = bsdf.inputs[sock_name].default_value if bsdf is not None else default
        comb.inputs['Blue'].default_value = 0.0
        tree.links.new(comb.outputs['Color'], emit.inputs['Color'])
        tree.links.new(emit.outputs['Emission'], out.inputs['Surface'])
        return out, bsdf
    if bsdf is None:
        v = FALLBACK[channel]
        emit.inputs['Color'].default_value = v if channel == 'albedo' else (v, v, v, 1.0)
    else:
        sock = bsdf.inputs[SOCKET[channel]]
        if sock.links:
            tree.links.new(sock.links[0].from_socket, emit.inputs['Color'])
        else:
            v = sock.default_value
            emit.inputs['Color'].default_value = tuple(v) if channel == 'albedo' else (v, v, v, 1.0)
    tree.links.new(emit.outputs['Emission'], out.inputs['Surface'])
    return out, bsdf


def restore(mat, out, bsdf):
    if bsdf is not None:
        mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])


groups = {}
for o in bpy.data.objects:
    if o.type == 'MESH' and 'bake_atlas' in o:
        groups.setdefault(int(o['bake_atlas']), []).append(o)

def world_box(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts),
            max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))


def near(a, b, d):
    return all(a[i] - d <= b[i + 3] and b[i] - d <= a[i + 3] for i in range(3))


all_meshes = [o for o in bpy.data.objects if o.type == 'MESH']
boxes = {o.name: world_box(o) for o in all_meshes}
orig_hide = {o.name: o.hide_render for o in bpy.data.objects}
log = []
for k in args.atlas:
    objs = groups[k]
    shell_group = any(o.get('bake_shell') for o in objs)
    for o in bpy.data.objects:                       # restore, then prune for this atlas
        o.hide_render = orig_hide[o.name]
    if args.prune > 0 and not shell_group:
        gboxes = [boxes[o.name] for o in objs]
        keep = {o.name for o in objs}
        for o in all_meshes:
            if o.name not in keep and any(near(boxes[o.name], g, args.prune) for g in gboxes):
                keep.add(o.name)
        for o in all_meshes:
            if o.name not in keep:
                o.hide_render = True
        for o in bpy.data.objects:
            if o.type == 'LIGHT':
                o.hide_render = True
        print('PRUNE atlas', k, 'visible meshes', len(keep), 'of', len(all_meshes))
    mats = {s.material for o in objs for s in o.material_slots if s.material and s.material.use_nodes}
    prepared = {m: prepare(m) for m in mats}
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    view_layer.objects.active = objs[0]
    for channel in args.maps:
        t0 = time.time()
        name = f'med_a{k}_{channel}{args.suffix}'
        img = bpy.data.images.new(name, args.size, args.size, alpha=False, float_buffer=False)
        img.colorspace_settings.name = COLOR_SPACE[channel]
        samples = args.samples
        scene.cycles.samples = samples
        saved = []
        for m, (tex, emit) in prepared.items():
            tex.image = img
            m.node_tree.nodes.active = tex
            tex.select = True
            saved.append((m, *(route(m, emit, channel) if channel != 'normal' else (None, None))))
        if channel == 'normal':
            bpy.ops.object.bake(type='NORMAL', margin=4, margin_type='EXTEND', use_clear=True, normal_space='TANGENT')
        else:
            bpy.ops.object.bake(type='EMIT', margin=4, margin_type='EXTEND', use_clear=True)
            for m, out, bsdf in saved:
                restore(m, out, bsdf)
        path = args.out / f'{name}.png'
        img.filepath_raw = str(path)
        img.file_format = 'PNG'
        img.save()
        print('BAKED', name, 'samples', samples, 'seconds', round(time.time() - t0), path)
        log.append((name, samples, round(time.time() - t0)))
        bpy.data.images.remove(img)
    for m, (tex, emit) in prepared.items():
        tex.image = None
print('NON_PRINCIPLED', sorted(non_principled))
print('DONE', log)
