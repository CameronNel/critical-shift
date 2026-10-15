"""Additive, maintained-facility finish authored directly from the frozen R34 module.

blender -b --factory-startup --disable-autoexec --python condenser_finish_A2.py -- --finish-pass R1
Only the triangle-trimming functions are reproduced from A1. No A1 shader or light code is used.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
BUDGET = 400000
PAINT = {
 'Astra ivory painted steel': ((.48, .475, .438), .41),
 'Service ochre enamel': ((.50, .30, .045), .43),
 'Structural painted steel': ((.055, .064, .079), .46),
 'Oxide orange enamel': ((.40, .115, .032), .43),
 'Light oxide enamel': ((.48, .205, .064), .45),
 'Safety burgundy': ((.135, .024, .025), .43),
 'Charcoal impact dado': ((.062, .071, .085), .58),
}
METAL = {
 'Astra brushed fastener steel': ((.29, .31, .33), .88, .29),
 'Astra formed stainless bellows': ((.22, .235, .25), .90, .36),
 'Oiled iron': ((.050, .060, .072), .82, .34),
 'Machined cast iron': ((.13, .142, .154), .86, .44),
 'Service brass': ((.36, .22, .073), .85, .34),
}

def triangles():
    dg = bpy.context.evaluated_depsgraph_get()
    total = 0
    for o in bpy.data.objects:
        if o.type not in ('MESH', 'CURVE', 'FONT'):
            continue
        ev = o.evaluated_get(dg)
        m = ev.to_mesh()
        total += sum(len(p.vertices) - 2 for p in m.polygons)
        ev.to_mesh_clear()
    return total

def trim_geometry():
    # A1's permitted geometry-only step, unchanged.
    for o in bpy.data.objects:
        if o.type in ('CURVE', 'FONT'):
            d = o.data
            d.resolution_u = max(1, min(d.resolution_u, 2))
            d.render_resolution_u = 0
            d.bevel_resolution = 0
    n = 0
    for limit in (1.0, 1.5, 2.5, 99):
        for o in bpy.data.objects:
            if o.type == 'MESH' and max(o.dimensions) < limit:
                for m in o.modifiers:
                    if m.type == 'BEVEL' and m.segments > 1:
                        m.segments = 1
                        n += 1
        if triangles() <= BUDGET - 8000:
            return n, limit
    return n, 99

def bounds(o):
    pts = [o.matrix_world @ Vector(v) for v in o.bound_box]
    return [[min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]]

class Surface:
    def __init__(self, material, color, metal, roughness):
        self.mat = material
        self.nt = material.node_tree
        self.nt.nodes.clear()
        self.bs = self.node('ShaderNodeBsdfPrincipled', 'Manufactured surface')
        self.bs.inputs['Base Color'].default_value = (*color, 1)
        self.bs.inputs['Metallic'].default_value = metal
        self.bs.inputs['Roughness'].default_value = roughness
        out = self.node('ShaderNodeOutputMaterial', 'Surface output')
        self.link(self.bs.outputs['BSDF'], out.inputs['Surface'])
        material.diffuse_color = (*color, 1)
        self.geo = self.node('ShaderNodeNewGeometry', 'Physical metre coordinates')

    def node(self, kind, label):
        n = self.nt.nodes.new(kind)
        n.label = 'A2 | ' + label
        return n

    def link(self, a, b):
        self.nt.links.new(a, b)

    def image(self, name, metres):
        im = bpy.data.images.load(str(HERE / 'textures-A2' / (name + '.png')), check_existing=True)
        im.colorspace_settings.name = 'Non-Color'
        im.pack()
        tex = self.node('ShaderNodeTexImage', name + ' / ' + str(metres) + ' metre tile')
        tex.image = im
        tex.projection = 'BOX'
        tex.projection_blend = .18
        tex.extension = 'REPEAT'
        scale = self.node('ShaderNodeVectorMath', 'Metres to tile coordinates')
        scale.operation = 'SCALE'
        scale.inputs['Scale'].default_value = 1 / metres
        self.link(self.geo.outputs['Position'], scale.inputs[0])
        self.link(scale.outputs['Vector'], tex.inputs['Vector'])
        return tex.outputs['Color']

    def math(self, op, a, b):
        n = self.node('ShaderNodeMath', op)
        n.operation = op
        for i, x in enumerate((a, b)):
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                self.link(x, n.inputs[i])
        return n.outputs[0]

    def rng(self, a, lo, hi):
        n = self.node('ShaderNodeMapRange', 'Controlled numeric range')
        n.inputs['To Min'].default_value = lo
        n.inputs['To Max'].default_value = hi
        self.link(a, n.inputs['Value'])
        return n.outputs['Result']

    def color_variation(self, value, color, amount):
        n = self.node('ShaderNodeMixRGB', 'Restrained mineral / finish variation')
        n.blend_type = 'MULTIPLY'
        n.inputs[0].default_value = 1
        n.inputs[1].default_value = (*color, 1)
        self.link(self.rng(value, 1 - amount, 1 + amount), n.inputs[2])
        self.link(n.outputs[0], self.bs.inputs['Base Color'])

    def bump(self, value, distance, strength):
        n = self.node('ShaderNodeBump', 'Real-scale surface relief')
        n.inputs['Distance'].default_value = distance
        n.inputs['Strength'].default_value = strength
        self.link(value, n.inputs['Height'])
        self.link(n.outputs['Normal'], self.bs.inputs['Normal'])

def paint(name, color, roughness):
    s = Surface(bpy.data.materials[name], color, 0.0, roughness)
    v = s.image('paint_peel', .12)
    s.color_variation(v, color, .018)
    s.link(s.rng(v, roughness - .035, roughness + .035), s.bs.inputs['Roughness'])
    s.bs.inputs['Coat Weight'].default_value = .12
    s.bs.inputs['Coat Roughness'].default_value = .35
    s.bump(v, .00009, .22)

def bare_metal(name, color, metallic, roughness):
    s = Surface(bpy.data.materials[name], color, metallic, roughness)
    v = s.image('cast_grain' if 'cast' in name.lower() or name == 'Oiled iron' else 'metal_brush', .24)
    s.color_variation(v, color, .035)
    s.link(s.rng(v, roughness - .045, roughness + .045), s.bs.inputs['Roughness'])
    s.bump(v, .00013 if 'cast' in name.lower() else .000025, .18)
    if name == 'Oiled iron':
        s.bs.inputs['Coat Weight'].default_value = .10
        s.bs.inputs['Coat Roughness'].default_value = .26

def mineral(name, color):
    s = Surface(bpy.data.materials[name], color, 0.0, .88)
    v = s.image('mineral_grain', .24)
    s.color_variation(v, color, .055)
    s.link(s.rng(v, .84, .92), s.bs.inputs['Roughness'])
    s.bump(v, .00065, .30)

def floor_uv():
    names = {'Basement coated concrete', 'Replacement floor patch'}
    for o in bpy.context.scene.objects:
        if o.type != 'MESH' or not any(m and m.name in names for m in o.data.materials):
            continue
        uv = o.data.uv_layers.new(name='A2 floor metres')
        for p in o.data.polygons:
            for li in p.loop_indices:
                v = o.matrix_world @ o.data.vertices[o.data.loops[li].vertex_index].co
                uv.data[li].uv = (v.x, v.y)
        uv.active_render = False

def floor(name, color):
    s = Surface(bpy.data.materials[name], color, 0.0, .65)
    grain = s.image('mineral_grain', .24)
    s.color_variation(grain, color, .022)
    uv = s.node('ShaderNodeUVMap', 'Module-metre floor UV / stable under map placement')
    uv.uv_map = 'A2 floor metres'
    split = s.node('ShaderNodeSeparateXYZ', 'Measured traffic coordinates')
    s.link(uv.outputs['UV'], split.inputs[0])
    x, y = split.outputs['X'], split.outputs['Y']
    def rect(x0, x1, y0, y1):
        return s.math('MULTIPLY', s.math('MULTIPLY', s.math('GREATER_THAN', x, x0), s.math('LESS_THAN', x, x1)), s.math('MULTIPLY', s.math('GREATER_THAN', y, y0), s.math('LESS_THAN', y, y1)))
    mask = rect(-.34, .44, .15, 6.25)
    for r in [(.75, 5.1, 1.42, 2.13), (.75, 5.0, 5.74, 6.40), (6.7, 8.5, 2.05, 6.7)]:
        mask = s.math('MAXIMUM', mask, rect(*r))
    scuff = s.image('traffic_scuff', .24)
    wear = s.math('MULTIPLY', mask, s.rng(scuff, .055, .012))
    n = s.node('ShaderNodeMixRGB', 'Traffic only: slight polished coat wear')
    n.blend_type = 'MULTIPLY'
    n.inputs[1].default_value = (*color, 1)
    n.inputs[2].default_value = (.78, .79, .79, 1)
    s.link(wear, n.inputs[0])
    s.link(n.outputs[0], s.bs.inputs['Base Color'])
    rough = s.math('SUBTRACT', s.rng(grain, .63, .69), s.math('MULTIPLY', wear, .75))
    s.link(rough, s.bs.inputs['Roughness'])
    s.bump(grain, .00022, .20)

def contact_wear():
    reused = {}
    touched = []
    for o in bpy.context.scene.objects:
        if o.type != 'MESH' or not any(w in o.name.lower() for w in ('handrail', 'manway', 'handwheel', 'kick plate')):
            continue
        for slot in o.material_slots:
            if not slot.material or slot.material.name not in PAINT:
                continue
            source = slot.material
            if source.name not in reused:
                mat = source.copy()
                mat.name = source.name + ' | handled contact edges'
                s = mat.node_tree
                bs = next(n for n in s.nodes if n.type == 'BSDF_PRINCIPLED')
                prior = bs.inputs['Base Color'].links[0].from_socket
                bev = s.nodes.new('ShaderNodeBevel'); bev.inputs['Radius'].default_value = .0012; bev.samples = 2
                geo = s.nodes.new('ShaderNodeNewGeometry')
                dot = s.nodes.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'
                s.links.new(bev.outputs['Normal'], dot.inputs[0]); s.links.new(geo.outputs['Normal'], dot.inputs[1])
                inv = s.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1
                s.links.new(dot.outputs['Value'], inv.inputs[1])
                gain = s.nodes.new('ShaderNodeMath'); gain.operation = 'MULTIPLY'; gain.inputs[1].default_value = .16
                s.links.new(inv.outputs[0], gain.inputs[0])
                mix = s.nodes.new('ShaderNodeMixRGB'); mix.inputs[2].default_value = (.25, .27, .28, 1)
                s.links.new(gain.outputs[0], mix.inputs[0]); s.links.new(prior, mix.inputs[1]); s.links.new(mix.outputs[0], bs.inputs['Base Color'])
                for n in (bev, geo, dot, inv, gain, mix):n.label = 'A2 | Local handled-edge wear, no rust'
                reused[source.name] = mat
            slot.link = 'OBJECT'
            slot.material = reused[source.name]
            touched.append(o.name)
    return sorted(set(touched))

def lighting():
    result = {}
    for o in bpy.context.scene.objects:
        if o.type != 'LIGHT':
            continue
        before = o.data.energy
        # Restore the inherited R34 rig; practical/task hierarchy, not global darkness.
        if o.name.startswith('batten'):
            o.data.color = (1, .97, .91)
            o.data.energy *= .90
        elif o.name.startswith(('task ', 'Astra practical task')):
            o.data.color = (1, .91, .77)
        elif o.name.startswith(('cw wall wash', 'gallery', 'neck wash', 'chest well')):
            o.data.color = (1, .96, .87)
            o.data.energy *= 1.10
        if o.name.startswith('gallery inspection light'):
            # Source light remains named for the map's additional -0.12m patch.
            o.location.z = 5.54
        result[o.name] = {'r34_watts': before, 'a2_watts': o.data.energy, 'position': list(o.location), 'color': list(o.data.color)}
    # Lower fixture bodies alongside their lights; source names and x/y stay fixed.
    for o in bpy.context.scene.objects:
        if o.name.startswith(('gallery inspection fixture', 'gallery inspection lens')):
            index = 1 if o.name.endswith('.001') else 0
            o.location.z -= .175 if index == 0 else .125
    return result

def apply(cycle):
    source = HERE / 'module.blend'
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source))
    sc = bpy.context.scene
    assert bpy.app.version[:3] == (5, 2, 2), 'Use the task-authorized Blender 5.2.2'
    assert 'MODULE_condenser-bay' in bpy.data.collections
    assert not sc.get('condenser_aaa_revision'), 'R34 input required, never A1'
    matrices = {o.name: [list(row) for row in o.matrix_world] for o in sc.objects if o.type not in {'LIGHT', 'CAMERA'}}
    before = triangles()
    trimmed, limit = trim_geometry()
    for name, (color, rough) in PAINT.items():paint(name, color, rough)
    for name, (color, metallic, rough) in METAL.items():bare_metal(name, color, metallic, rough)
    mineral('Warm mineral plaster', (.45, .435, .40))
    mineral('Dense cast concrete', (.27, .265, .245))
    floor_uv()
    floor('Basement coated concrete', (.172, .180, .181))
    floor('Replacement floor patch', (.198, .203, .197))
    rubber = Surface(bpy.data.materials['Matte vulcanized rubber'], (.015, .019, .022), 0, .90)
    v = rubber.image('cast_grain', .24); rubber.link(rubber.rng(v, .87, .93), rubber.bs.inputs['Roughness']); rubber.bump(v, .00006, .15)
    # Existing fabric and worktop stay authored R34 surfaces; keep their numeric
    # texture features below 0.3m rather than inheriting the coarse 2.8 scale.
    for mat in bpy.data.materials:
        if mat.name in {'Cotton rag', 'Worn beech work surface'}:
            for n in mat.node_tree.nodes:
                if n.type == 'TEX_NOISE' and n.inputs['Scale'].default_value < 4:
                    n.inputs['Scale'].default_value = 7
    touched = contact_wear()
    lights = lighting()
    sc.view_settings.exposure = -.10
    sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .20
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.use_denoising = True
    sc.render.resolution_x = 1920; sc.render.resolution_y = 1080; sc.render.resolution_percentage = 100
    sc.cycles.samples = 32
    sc['source_revision'] = 'A2-' + cycle
    sc['condenser_finish_revision'] = 'A2-' + cycle
    sc['condenser_finish_source_sha256'] = source_hash
    sc['condenser_finish_scope'] = 'R34 additive finish; source geometry layout and named map interfaces retained; no facility cooling-loop or Unity acceptance claim.'
    sc.camera = sc.objects['C02_HERO']
    bpy.context.view_layer.update()
    matrix_changes = [n for n, m in matrices.items() if any(abs(m[i][j] - sc.objects[n].matrix_world[i][j]) > .00001 for i in range(4) for j in range(4))]
    assert all(n.startswith(('gallery inspection fixture', 'gallery inspection lens')) for n in matrix_changes), matrix_changes
    count = triangles()
    assert count <= BUDGET, count
    output = HERE / 'module_aaa_A2.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    result = {'revision': 'A2-' + cycle, 'source': 'module.blend', 'source_sha256': source_hash, 'output_sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'blender': bpy.app.version_string, 'triangles_before': before, 'triangles_after': count, 'budget': BUDGET, 'bevel_segments_trimmed': trimmed, 'bevel_limit_metres': limit, 'changed_nonlight_matrices': matrix_changes, 'contact_wear_objects': touched, 'lights': lights, 'packed_images': [{'name': im.name, 'packed': bool(im.packed_file)} for im in bpy.data.images], 'original_cameras': [o.name for o in sc.objects if o.type == 'CAMERA'], 'world_strength': .20, 'exposure': sc.view_settings.exposure, 'status': 'BUILT; independent visual review pending'}
    (HERE / 'finish-A2-build.json').write_text(json.dumps(result, indent=2) + '\n')
    print('CONDENSER_A2_BUILT', count, 'triangles', 'R34 preserved', flush=True)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--finish-pass', default='R1')
    p = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    apply(p.finish_pass)
