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
 'Astra ivory painted steel': ((.40, .395, .364), .41),
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

def mineral(name, color, refined=False):
    s = Surface(bpy.data.materials[name], color, 0.0, .88)
    v = s.image('mineral_grain', .24)
    tone = s.image('mineral_tone', .24) if refined else v
    s.color_variation(tone, color, .055)
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

def floor(name, color, refined=False):
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
    wear = s.math('MULTIPLY', mask, s.rng(scuff, .26 if refined else .055, .035 if refined else .012))
    n = s.node('ShaderNodeMixRGB', 'Traffic only: slight polished coat wear')
    n.blend_type = 'MULTIPLY'
    n.inputs[1].default_value = (*color, 1)
    n.inputs[2].default_value = (.78, .79, .79, 1)
    s.link(wear, n.inputs[0])
    s.link(n.outputs[0], s.bs.inputs['Base Color'])
    rough = s.math('SUBTRACT', s.rng(grain, .63, .69), s.math('MULTIPLY', wear, .75))
    s.link(rough, s.bs.inputs['Roughness'])
    s.bump(grain, .00022, .20)

def contact_wear(refined=False):
    reused = {}
    touched = []
    for o in bpy.context.scene.objects:
        words = ('handrail', 'manway', 'handwheel', 'kick plate', 'rail top', 'rail mid', 'manhole', 'hatch rim')
        if o.type not in {'MESH', 'CURVE'} or not any(w in o.name.lower() for w in words):
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
                gain = s.nodes.new('ShaderNodeMath'); gain.operation = 'MULTIPLY'; gain.inputs[1].default_value = 1.1 if refined else .16; gain.use_clamp = True
                s.links.new(inv.outputs[0], gain.inputs[0])
                mix = s.nodes.new('ShaderNodeMixRGB'); mix.inputs[2].default_value = (.25, .27, .28, 1)
                s.links.new(gain.outputs[0], mix.inputs[0]); s.links.new(prior, mix.inputs[1]); s.links.new(mix.outputs[0], bs.inputs['Base Color'])
                for n in (bev, geo, dot, inv, gain, mix):n.label = 'A2 | Local handled-edge wear, no rust'
                reused[source.name] = mat
            slot.link = 'OBJECT'
            slot.material = reused[source.name]
            touched.append(o.name)
    return sorted(set(touched))

def lighting(refined=False):
    result = {}
    for o in bpy.context.scene.objects:
        if o.type != 'LIGHT':
            continue
        before = o.data.energy
        # Restore the inherited R34 rig; practical/task hierarchy, not global darkness.
        if o.name.startswith('batten'):
            o.data.color = (1, .97, .91)
            o.data.energy *= (.60 if o.name in {'batten0', 'batten1', 'batten3', 'batten6', 'batten7'} else .80) if refined else .90
        elif o.name.startswith(('task ', 'Astra practical task')):
            o.data.color = (1, .91, .77)
        elif o.name.startswith(('cw wall wash', 'gallery', 'neck wash', 'chest well')):
            o.data.color = (1, .96, .87)
            o.data.energy *= 1.10
        if o.name.startswith('gallery inspection light'):
            # Source light remains named for the map's additional -0.12m patch.
            o.location.z = 5.54
            if refined:
                o.location.x, o.location.y = (6.245, 4.1) if o.name == 'gallery inspection light' else (3.2, 6.19)
                o.data.shape = 'SQUARE'; o.data.size = .12
        if refined:
            boost = {'task CD south': .78, 'task CD east': .88, 'task pumps': 1.05, 'task operator': 1.15, 'gallery task': 1.60, 'neck wash': 1.40}
            o.data.energy *= boost.get(o.name, 1)
            if o.location.z > 5.55:
                o.location.z = 5.53
        result[o.name] = {'r34_watts': before, 'a2_watts': o.data.energy, 'position': list(o.location), 'color': list(o.data.color)}
    # Lower fixture bodies alongside their lights; source names and x/y stay fixed.
    for o in bpy.context.scene.objects:
        if not refined and o.name.startswith(('gallery inspection fixture', 'gallery inspection lens')):
            index = 1 if o.name.endswith('.001') else 0
            o.location.z -= .175 if index == 0 else .125
    return result

def blocks_mesh(obj, boxes):
    """Manufactured frame/lens parts, in world metres; preserve object transforms."""
    vertices, faces = [], []
    inv = obj.matrix_world.inverted()
    sides = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    for centre, dimensions in boxes:
        x, y, z = centre; a, b, c = [v / 2 for v in dimensions]
        points = [(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x-a,y+b,z-c), (x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]
        offset = len(vertices)
        vertices.extend(inv @ Vector(p) for p in points)
        faces.extend(tuple(offset + i for i in f) for f in sides)
    mesh = bpy.data.meshes.new(obj.name + ' | A2 manufactured channel')
    mesh.from_pydata(vertices, [], faces); mesh.update()
    for mat in obj.data.materials:mesh.materials.append(mat)
    obj.data = mesh
    for mod in obj.modifiers:
        if mod.type == 'BEVEL':mod.width = .0015; mod.segments = 1

def gallery_luminaires():
    # The unchanged map drops only the LIGHT objects by 0.12m. The open optical
    # channel admits both the standalone and assembled source positions, unlike
    # a solid housing that would block the assembled uplight. Clamp onto the
    # inherited structural suspension; do not introduce a floating lamp.
    registry = json.loads(bpy.context.scene.get('support_registry', '[]'))
    result = []
    for suffix, cx, cy, target, anchor, direction in [
        ('', 6.245, 4.1, 'gallery edge suspension', (6.324,4.1,5.47), (1,0,0)),
        ('.001', 3.2, 6.19, 'gallery edge suspension.004', (3.2,6.269,5.47), (0,1,0)),
    ]:
        ob = bpy.data.objects['gallery inspection fixture' + suffix]
        lens = bpy.data.objects['gallery inspection lens' + suffix]
        boxes = []
        for dx in (-.064, .064):
            for dy in (-.064, .064):boxes.append(((cx+dx,cy+dy,5.47),(.012,.012,.14)))
        for z in (5.404, 5.536):
            for dy in (-.064, .064):boxes.append(((cx,cy+dy,z),(.14,.012,.008)))
            for dx in (-.064, .064):boxes.append(((cx+dx,cy,z),(.012,.116,.008)))
        if not suffix:boxes.append(((6.32,cy,5.47),(.012,.030,.030)))
        else:boxes.append(((cx,6.265,5.47),(.030,.012,.030)))
        blocks_mesh(ob, boxes)
        glazing = []
        for dx in (-.058, .058):glazing.append(((cx+dx,cy,5.47),(.004,.112,.112)))
        for dy in (-.058, .058):glazing.append(((cx,cy+dy,5.47),(.112,.004,.112)))
        blocks_mesh(lens, glazing)
        name = 'A2 gallery luminaire support' + suffix
        empty = bpy.data.objects.new(name, None); empty.location = anchor
        bpy.data.collections['04 Ceiling services'].objects.link(empty)
        registry.append({'anchor':name, 'target':target, 'direction':list(direction), 'max_gap':.005, 'max_penetration':.002, 'angle_tolerance_degrees':12, 'prop':ob.name, 'scope':'Manufactured luminaire frame and diffuser assembly, clamped to inherited gallery suspension.'})
        result.append({'fixture':ob.name, 'support':target, 'bounds':bounds(ob), 'standalone_light_z':5.54, 'assembled_light_z':5.42, 'open_channel':True})
    bpy.context.scene['support_registry'] = json.dumps(registry)
    return result

def wall_tie_holes():
    """Actual shallow formwork sockets; no stain texture or camouflage field."""
    result = []
    for name, inner, sign in [('WestWall', -1.8, -1), ('EastWall', 9.6, 1)]:
        wall = bpy.data.objects[name]
        bpy.ops.object.select_all(action='DESELECT'); wall.select_set(True); bpy.context.view_layer.objects.active = wall
        # Preserve the original architectural edge finish before introducing the
        # small sockets, which must not inherit a centimetre-wide wall bevel.
        for mod in list(wall.modifiers):
            if mod.type == 'BEVEL':bpy.ops.object.modifier_apply(modifier=mod.name)
        vertices, faces = [], []
        segments = 16
        for y in (.95, 3.0, 5.15, 7.2):
            for z in (1.55, 3.15, 4.8):
                offset = len(vertices)
                for x in sorted((inner - sign*.004, inner + sign*.008)):
                    vertices.extend((x,y+.012*math.cos(2*math.pi*i/segments),z+.012*math.sin(2*math.pi*i/segments)) for i in range(segments))
                faces.append(tuple(offset+i for i in reversed(range(segments))))
                faces.append(tuple(offset+segments+i for i in range(segments)))
                faces.extend((offset+i,offset+(i+1)%segments,offset+segments+(i+1)%segments,offset+segments+i) for i in range(segments))
        mesh = bpy.data.meshes.new('A2 temporary formwork cutters'); mesh.from_pydata(vertices, [], faces); mesh.update()
        cutter = bpy.data.objects.new('A2 temporary formwork cutters', mesh); bpy.context.scene.collection.objects.link(cutter)
        boolean = wall.modifiers.new('A2 shallow formwork sockets', 'BOOLEAN'); boolean.operation = 'DIFFERENCE'; boolean.solver = 'EXACT'; boolean.object = cutter
        bpy.ops.object.modifier_apply(modifier=boolean.name)
        bpy.data.objects.remove(cutter, do_unlink=True); bpy.data.meshes.remove(mesh)
        result.append({'wall':name,'count':12,'radius_m':.012,'depth_m':.008,'maximum_y':7.2,'escape_door_untouched':True})
    return result

def reserve_map_budget():
    # A1's published map count is 422,140 despite its source being 386,490.
    # Reserve for evaluated instancing / local patches. Restrict reductions to
    # tiny round washer/shank geometry; keep large silhouettes and the eight
    # independently audited steam-chest seating stacks intact.
    adjusted = []
    if triangles() > 355000:
        for ob in bpy.context.scene.objects:
            if ob.type != 'MESH' or max(ob.dimensions) > .12 or ob.name.startswith('chest bolt'):
                continue
            if not any(word in ob.name.lower() for word in ('washer','shank')):
                continue
            mod = ob.modifiers.new('A2 small fastener budget reserve', 'DECIMATE'); mod.ratio = .72
            adjusted.append(ob.name)
        for ratio in (.72, .68, .64, .60, .56, .52, .48, .44, .40):
            for name in adjusted:bpy.data.objects[name].modifiers['A2 small fastener budget reserve'].ratio = ratio
            bpy.context.view_layer.update()
            if triangles() <= 355000:break
    return adjusted

def fit_roof_footprint():
    """Trim only pre-existing exterior overhangs, retaining every inner plane,
    object transform, port marker, D01 stub and map-patched object name."""
    changes = []
    for o in bpy.context.scene.objects:
        if o.type != 'MESH':continue
        before = bounds(o)
        lo, hi = before
        allow_stub = o.name.startswith(('D01 stub', 'D01 local blanking', 'D01 blanking'))
        if lo[0] >= -2.08001 and hi[0] <= 9.88001 and hi[1] <= 9.54001 and (lo[1] >= -.14001 or allow_stub):continue
        inv = o.matrix_world.inverted()
        for v in o.data.vertices:
            p = o.matrix_world @ v.co
            p.x = max(-2.08, min(9.88, p.x)); p.y = min(9.54, p.y)
            if not allow_stub:p.y = max(-.14, p.y)
            # A top at exactly z6 is coplanar with the turbine floor. After the
            # exterior trim its triangulation made floor_audit pick this wall
            # instead of that floor in four ray samples. Retain a 1mm erection
            # joint below the slab; no interior plane or object transform moves.
            if o.name == 'NorthWall':p.z = min(p.z, 5.999)
            v.co = inv @ p
        o.data.update()
        bpy.context.view_layer.update()
        changes.append({'object':o.name,'before':before,'after':bounds(o),'transform_unchanged':True})
    return changes

def apply(cycle, output_path=None):
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
    refined = cycle != 'R1'
    for name, (color, rough) in PAINT.items():paint(name, color, rough)
    for name, (color, metallic, rough) in METAL.items():bare_metal(name, color, metallic, rough)
    refined_tone = cycle not in {'R1','R2','R2b'}
    mineral('Warm mineral plaster', (.40, .392, .37) if refined_tone else (.45, .435, .40), refined_tone)
    mineral('Dense cast concrete', (.27, .265, .245), refined_tone)
    for ob in sc.objects:
        if ob.type in {'MESH','CURVE','FONT'} and hasattr(ob.data,'materials'):
            for i, material in enumerate(ob.data.materials):
                if material is None:ob.data.materials[i] = bpy.data.materials['Dense cast concrete']
    floor_uv()
    floor('Basement coated concrete', (.172, .180, .181), refined)
    floor('Replacement floor patch', (.198, .203, .197), refined)
    rubber = Surface(bpy.data.materials['Matte vulcanized rubber'], (.015, .019, .022), 0, .90)
    v = rubber.image('cast_grain', .24); rubber.link(rubber.rng(v, .87, .93), rubber.bs.inputs['Roughness']); rubber.bump(v, .00006, .15)
    # Existing fabric and worktop stay authored R34 surfaces; keep their numeric
    # texture features below 0.3m rather than inheriting the coarse 2.8 scale.
    for mat in bpy.data.materials:
        if mat.name in {'Cotton rag', 'Worn beech work surface'}:
            for n in mat.node_tree.nodes:
                if n.type == 'TEX_NOISE' and n.inputs['Scale'].default_value < 4:
                    n.inputs['Scale'].default_value = 7
    touched = contact_wear(refined)
    lights = lighting(refined)
    fixtures = gallery_luminaires() if refined else []
    tie_holes = wall_tie_holes() if refined else []
    footprint = fit_roof_footprint() if refined else []
    fasteners = reserve_map_budget() if refined else []
    sc.view_settings.exposure = -.10
    world_strength = .12 if refined else .20
    sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = world_strength
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
    output = Path(output_path).resolve() if output_path else HERE / 'module_aaa_A2.blend'
    assert output.is_relative_to(HERE) and output.name not in {'module.blend','module_aaa_A1.blend','accepted.blend'} and 'contracts' not in output.relative_to(HERE).parts
    if output_path:assert not output.exists(), 'A checkpoint label is immutable; choose a new path'
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output))
    assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    result = {'revision': 'A2-' + cycle, 'source': 'module.blend', 'source_sha256': source_hash, 'builder_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'output_sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'blender': bpy.app.version_string, 'triangles_before': before, 'triangles_after': count, 'budget': BUDGET, 'bevel_segments_trimmed': trimmed, 'bevel_limit_metres': limit, 'changed_nonlight_matrices': matrix_changes, 'contact_wear_objects': touched, 'lights': lights, 'gallery_fixtures':fixtures, 'wall_tie_holes':tie_holes, 'small_fasteners_reduced':fasteners, 'packed_images': [{'name': im.name, 'packed': bool(im.packed_file)} for im in bpy.data.images], 'original_cameras': [o.name for o in sc.objects if o.type == 'CAMERA'], 'world_strength': world_strength, 'exposure': sc.view_settings.exposure, 'status': 'BUILT; independent visual review pending'}
    result['output'] = str(output.relative_to(HERE))
    result['exterior_footprint_trims'] = footprint
    receipt = output.with_suffix('.json') if output_path else HERE / 'finish-A2-build.json'
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    (HERE / 'renders-A2').mkdir(exist_ok=True)
    print('CONDENSER_A2_BUILT', count, 'triangles', 'R34 preserved', flush=True)

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--finish-pass', default='R1'); ap.add_argument('--output')
    p = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    apply(p.finish_pass, p.output)
