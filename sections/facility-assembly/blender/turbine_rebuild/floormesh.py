"""One floor slab (14 x 24 x 0.3 m) with real holes cut through it, one planar UV across the whole top surface."""
import math
import bpy, bmesh
from mathutils import Vector

def _cutter(name, verts_fn, coll):
    bm = bmesh.new(); verts_fn(bm)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob); return ob

def _box(cx, cy, sx, sy, z0=-.6, z1=.4):
    def f(bm):
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(sx, sy, z1 - z0), verts=bm.verts); bmesh.ops.translate(bm, vec=(cx, cy, (z0 + z1) / 2), verts=bm.verts)
    return f

def _cyl(cx, cy, r, z0=-.6, z1=.4, seg=36):
    def f(bm):
        bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=z1 - z0)
        bmesh.ops.translate(bm, vec=(cx, cy, (z0 + z1) / 2), verts=bm.verts)
    return f

def make_floor(coll, layout, mats, hole):
    """mats: (top_material, wall_material). hole: (x0, x1, y0, y1) exhaust opening."""
    sm = bpy.data.meshes.new('FLOOR_SLAB'); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=(14, 24, .3), verts=bm.verts); bmesh.ops.translate(bm, vec=(3, 12, -.15), verts=bm.verts)
    bm.to_mesh(sm); bm.free()
    slab = bpy.data.objects.new('TURBINE_FLOOR', sm); coll.objects.link(slab)
    cutters = []
    for (x, y0, y1, w) in layout['channels']: cutters.append(_cutter('c_ch', _box(x, (y0 + y1) / 2, w, y1 - y0), coll))
    for (x, y, s) in layout['sumps']: cutters.append(_cutter('c_sump', _box(x, y, s + .02, s + .02), coll))
    for (x, y, r) in layout['drains']: cutters.append(_cutter('c_drain', _cyl(x, y, r + .01), coll))
    x0, x1, y0, y1 = hole; cutters.append(_cutter('c_exhaust', _box((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0), coll))
    bpy.context.view_layer.objects.active = slab
    for i, c in enumerate(cutters):
        md = slab.modifiers.new(f'cut{i}', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.solver = 'EXACT'; md.object = c
        bpy.ops.object.modifier_apply(modifier=md.name)
        bpy.data.objects.remove(c, do_unlink=True)
    me = slab.data; bm = bmesh.new(); bm.from_mesh(me)
    uv = bm.loops.layers.uv.new('UVMap'); tops = 0
    for f in bm.faces:
        top = f.normal.z > .9 and f.calc_center_median().z > -.02
        f.material_index = 0 if top else 1; f.smooth = False; tops += top
        for l in f.loops:
            co = l.vert.co; l[uv].uv = ((co.x + 4.0) / 14.0, co.y / 24.0) if top else (.001, .001)
    bm.to_mesh(me); bm.free()
    me.materials.clear()
    for m in mats: me.materials.append(m)
    return slab, dict(top_faces=tops, faces=len(me.polygons), tris=sum(len(p.vertices) - 2 for p in me.polygons))

def make_materials(atlas_prefix, name='floor'):
    """Floor top material (albedo + ORM + normal on UV0) and a flat dark material for the hole walls / underside."""
    def img(path, cs):
        i = bpy.data.images.load(path); i.colorspace_settings.name = cs; return i
    a, o, n = img(atlas_prefix + '_albedo.png', 'sRGB'), img(atlas_prefix + '_orm.png', 'Non-Color'), img(atlas_prefix + '_normal.png', 'Non-Color')
    m = bpy.data.materials.new('M_' + name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    uvn = nt.nodes.new('ShaderNodeUVMap'); uvn.uv_map = 'UVMap'; uvn.location = (-700, 0)
    ta = nt.nodes.new('ShaderNodeTexImage'); ta.image = a; ta.name = 'ALBEDO'; ta.location = (-420, 250)
    to = nt.nodes.new('ShaderNodeTexImage'); to.image = o; to.name = 'ORM'; to.location = (-420, 0)
    tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = n; tn.name = 'NORMAL'; tn.location = (-420, -250)
    for t in (ta, to, tn): nt.links.new(uvn.outputs[0], t.inputs[0])
    sp = nt.nodes.new('ShaderNodeSeparateColor'); sp.location = (-150, 0); nt.links.new(to.outputs[0], sp.inputs[0])
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.location = (-150, -250); nm.inputs['Strength'].default_value = 1.0; nt.links.new(tn.outputs[0], nm.inputs['Color'])
    p = nt.nodes.new('ShaderNodeBsdfPrincipled'); p.location = (300, 0)
    nt.links.new(ta.outputs[0], p.inputs['Base Color']); nt.links.new(sp.outputs['Green'], p.inputs['Roughness']); nt.links.new(sp.outputs['Blue'], p.inputs['Metallic']); nt.links.new(nm.outputs[0], p.inputs['Normal'])
    nt.links.new(p.outputs[0], out.inputs['Surface'])
    w = bpy.data.materials.new('M_' + name + '_edges'); w.use_nodes = True; wn = w.node_tree.nodes['Principled BSDF']
    wn.inputs['Base Color'].default_value = (.03, .035, .042, 1); wn.inputs['Roughness'].default_value = .85
    return m, w
