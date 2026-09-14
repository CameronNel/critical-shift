import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'connections/network'
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(OUT/'network-R03.blend'),link=False) as (src,dst):dst.collections=['09_FINISHED_HORIZONTAL_CONNECTIONS']
col=dst.collections[0];bpy.context.scene.collection.children.link(col)
cache=bpy.data.collections.new('10_NETWORK_VIEWPORT_CACHE');bpy.context.scene.collection.children.link(cache)
items=[]
for o in list(col.objects):
 if o.type not in {'MESH','CURVE','FONT'}:continue
 cp=o.copy();cp.data=o.data.copy();cache.objects.link(cp);cp.select_set(True);items.append(cp)
bpy.context.view_layer.objects.active=items[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();ob=bpy.context.view_layer.objects.active;ob.name='WALK_PROXY_HORIZONTAL_NETWORK';ob.hide_render=True
cache.hide_render=True
bpy.data.libraries.write(str(OUT/'network-viewport-R03.blend'),{cache},compress=True,path_remap='RELATIVE')
(OUT/'VIEWPORT_CACHE.json').write_text(json.dumps({'objects':len(cache.objects),'vertices':len(ob.data.vertices),'faces':len(ob.data.polygons),'scope':'Disposable geometry batch for solid viewport; original authoring retained.'},indent=2));print('NETWORK_CACHE_READY',flush=True)
