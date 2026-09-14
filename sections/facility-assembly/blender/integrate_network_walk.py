import bpy,json,hashlib
from pathlib import Path
ROOT=Path(r'C:/Users/Camer/Games/critical-shift/worktrees/facility-assembly-astra/sections/facility-assembly');OUT=ROOT/'connections/network'
assert '09_FINISHED_HORIZONTAL_CONNECTIONS' not in bpy.data.collections
previous=bpy.data.filepath
for file,colname in [('network-R03.blend','09_FINISHED_HORIZONTAL_CONNECTIONS'),('network-viewport-R03.blend','10_NETWORK_VIEWPORT_CACHE')]:
 with bpy.data.libraries.load(str(OUT/file),link=False) as (src,dst):dst.collections=[colname]
 bpy.context.scene.collection.children.link(dst.collections[0])
bpy.data.collections['09_FINISHED_HORIZONTAL_CONNECTIONS'].hide_viewport=True
bpy.data.collections['10_NETWORK_VIEWPORT_CACHE'].hide_render=True
for name in ['CONNECTIONS_ALL_ROUTES_GREYBOX','02_UNBUILT_CONNECTION_RESERVATIONS']:
 c=bpy.data.collections.get(name)
 if c:c.hide_render=True;c.hide_viewport=True
ob=bpy.data.objects.get('WALK_PROXY_CONNECTIONS_ALL_ROUTES_GREYBOX')
if ob:ob.hide_viewport=True;ob.hide_render=True
bpy.context.preferences.inputs.walk_navigation.use_gravity=False
bpy.context.scene.name='FACILITY_A07_HORIZONTAL_NETWORK'
bpy.context.scene['connection_scope']='All 21 horizontal routes built; vertical R19 and source door bindings remain step 2.'
dest=ROOT/'blender/facility_walkthrough_A07_horizontal_network.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
(ROOT/'production/NETWORK_A07_WALK.json').write_text(json.dumps({'file':str(dest),'previous_preserved':previous,'network_batch_objects':1,'network_authoring_objects':len(bpy.data.collections['09_FINISHED_HORIZONTAL_CONNECTIONS'].objects),'gravity':False},indent=2))
print('A07_WALK_SAVED')
