"""Render a gallery of prototypes for QA: python gallery.py -- out.png proto_module func1,func2 ..."""
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fe_common import *
import importlib
a = sys.argv[sys.argv.index('--') + 1:]
out, modname, funcs = a[0], a[1], a[2].split(',')
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
F = families(); P = collection('PROTOTYPES'); sc.collection.children.link(P) if P.name not in [c.name for c in sc.collection.children] else None
mod = importlib.import_module(modname)
x = 0.0; objs = []
for fn in funcs:
    o = getattr(mod, fn)(F, P)
    if isinstance(o, (list, tuple)):
        for oo in o: objs.append(oo)
    else: objs.append(o)
# lay out in a row by bbox width
from mathutils import Vector
cur = 0.0
tri = 0
for o in objs:
    bb = [Vector(c) for c in o.bound_box]; w = max(v.x for v in bb) - min(v.x for v in bb); cx = (max(v.x for v in bb) + min(v.x for v in bb)) / 2
    o.location.x = cur + w / 2 - cx + 0.0; cur += w + 0.5
    tri += sum(len(p.vertices) - 2 for p in o.data.polygons)
    print('ASSET', o.name, sum(len(p.vertices) - 2 for p in o.data.polygons), 'tris', round(w, 2), 'm wide')
print('GALLERY_TRIS', tri)
box('floor', -5, cur + 5, -4, 4, -0.1, 0.0, F['concrete_slab'], sc.collection) if False else None
bpy.ops.mesh.primitive_plane_add(size=200, location=(cur / 2, 0, 0)); fl = bpy.context.active_object; fl.data.materials.append(F['cafe_tile'])
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.75, 0.8, 0.9, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.2
sun = bpy.data.lights.new('s', 'SUN'); sun.energy = 3; so = bpy.data.objects.new('s', sun); so.rotation_euler = (0.9, 0.2, 0.6); sc.collection.objects.link(so)
cam = bpy.data.cameras.new('c'); cam.lens = 34; co = bpy.data.objects.new('c', cam); sc.collection.objects.link(co)
span = cur; co.location = (span * 0.25, span * 0.85 + 2.2, 2.0 + span * 0.1)
d = Vector((span / 2, 0, 0.7)) - co.location; co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
sc.render.engine = 'CYCLES'; sc.cycles.samples = 24; sc.cycles.device = 'CPU'; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1500, 600; sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.render.filepath = out; bpy.ops.render.render(write_still=True)
