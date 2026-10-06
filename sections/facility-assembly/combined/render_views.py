"""Render named camera views of combined_map.blend headlessly (Cycles, CPU). Usage:

    blender --background combined_map.blend --python render_views.py -- views.json

views.json: {"out": "dir", "res": [768, 432], "samples": 28, "hide": ["ROOM_mine"],
             "views": {"name": [[eye x, y, z], [target x, y, z], lens_mm], ...}}
Plan metres (+x east, +y north). "hide" lists objects to hide for speed (ROOM_mine has 4.08M triangles, hide it for views that do not look into the mine).
A view whose camera lands inside geometry renders as a wall: check the image, move the eye. Keeps the scene's own dusk lighting unless "world" is given.
"""
import bpy, sys, os, json
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:]; cfg=json.load(open(a[0]))
out=cfg['out']; os.makedirs(out,exist_ok=True)
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=cfg.get('samples',28); sc.cycles.use_denoising=True
sc.render.resolution_x, sc.render.resolution_y = cfg.get('res',[768,432])
if 'world' in cfg:
    w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs['Color'].default_value=tuple(cfg['world'])+(1,)
else: sc.view_settings.exposure=cfg.get('exposure',sc.view_settings.exposure)
for n in cfg.get('hide',[]):
    o=bpy.data.objects.get(n)
    if o: o.hide_render=True; o.hide_viewport=True
for name,(eye,tgt,lens,*rest) in cfg['views'].items():
    c=bpy.data.cameras.new(name); c.lens=lens; c.clip_start=0.05; c.clip_end=800
    o=bpy.data.objects.new(name,c); sc.collection.objects.link(o); o.location=eye
    o.rotation_euler=(Vector(tgt)-Vector(eye)).to_track_quat('-Z','Y').to_euler()
    sc.camera=o; sc.render.filepath=os.path.join(out,name+'.png'); bpy.ops.render.render(write_still=True)
