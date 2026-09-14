bl_info={'name':'Critical Shift Walkthrough','author':'Critical Shift','version':(1,0,0),'blender':(5,2,0),'category':'3D View'}
import bpy
from bpy.app.handlers import persistent

_keys=[]

def apply_display(scene,context=None):
 proxy=bpy.data.collections.get('07_FAST_WALKTHROUGH_PROXIES')
 if not proxy:return
 fast=scene.facility_fast_walkthrough
 proxy.hide_viewport=not fast
 proxy.hide_render=True
 network=bpy.data.collections.get('10_NETWORK_VIEWPORT_CACHE')
 if network:network.hide_viewport=not fast;network.hide_render=True
 for cache_name,source_name in [('23_EXTERIOR_FINISH_VIEWPORT_CACHE','22_EXTERIOR_FINISH_GEOMETRY'),('21_ROOF_SERVICE_VIEWPORT_CACHE','20_ROOF_SERVICE_GEOMETRY'),('14_ACCESS_FINISH_VIEWPORT_CACHE','13_FINISHED_ACCESS_SCENERY'),('16_NETWORK_FINISH_VIEWPORT_CACHE','15_FINISHED_NETWORK_SCENERY'),('18_REACTOR_FINISH_VIEWPORT_CACHE','17_REACTOR_EXTERIOR_FINISH')]:
  cache=bpy.data.collections.get(cache_name);source=bpy.data.collections.get(source_name)
  if cache:cache.hide_viewport=not fast;cache.hide_render=True
  if source:source.hide_viewport=fast
 if '09_FINISHED_HORIZONTAL_CONNECTIONS' in bpy.data.collections:
  old=bpy.data.collections.get('CONNECTIONS_ALL_ROUTES_GREYBOX')
  if old:old.hide_viewport=True;old.hide_render=True
  oldmesh=bpy.data.objects.get('WALK_PROXY_CONNECTIONS_ALL_ROUTES_GREYBOX')
  if oldmesh:oldmesh.hide_viewport=True;oldmesh.hide_render=True
 for name in ['01_LINKED_ROOMS','06_LINKED_EXTERIORS','CONNECTION_C01_RESCUE_COURTYARD','09_FINISHED_HORIZONTAL_CONNECTIONS']:
  col=bpy.data.collections.get(name)
  if col:col.hide_viewport=fast
 for name in ['02_UNBUILT_CONNECTION_RESERVATIONS','03_RESERVED_VOLUMES','04_PLANNING_LABELS']:
  col=bpy.data.collections.get(name)
  if col:col.hide_viewport=not scene.facility_show_guides

@persistent
def on_load(_):
 if '07_FAST_WALKTHROUGH_PROXIES' in bpy.data.collections:
  bpy.context.preferences.inputs.walk_navigation.use_gravity=False
  apply_display(bpy.context.scene)
  # The installed MCP add-on owns endpoint allocation and registration.
  if hasattr(bpy.context.scene,'blendermcp_allow_ai_control'):
   bpy.context.scene.blendermcp_allow_ai_control=True
   bpy.ops.blendermcp.start_server()

class FACILITY_OT_walk(bpy.types.Operator):
 bl_idname='view3d.facility_safe_walk'
 bl_label='Walk (Shift F)'
 bl_description='WASD and mouse navigation with gravity disabled across unfinished gaps'
 @classmethod
 def poll(cls,context):return context.area and context.area.type=='VIEW_3D'
 def invoke(self,context,event):
  context.preferences.inputs.walk_navigation.use_gravity=False
  context.scene['safe_walk_invocations']=context.scene.get('safe_walk_invocations',0)+1
  bpy.ops.view3d.walk('INVOKE_DEFAULT')
  return {'FINISHED'}

class FACILITY_PT_walk(bpy.types.Panel):
 bl_label='Critical Shift Walkthrough'
 bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Walkthrough'
 def draw(self,context):
  layout=self.layout
  layout.operator('view3d.facility_safe_walk',icon='VIEW_PAN')
  layout.prop(context.scene,'facility_fast_walkthrough',text='Fast walkthrough meshes')
  layout.prop(context.scene,'facility_show_guides',text='Show reserved connection guides')
  layout.label(text='WASD: move | E/Q: up/down')
  layout.label(text='Gravity off; no game collision')
  layout.label(text='Original assets retained for editing')

def register():
 bpy.utils.register_class(FACILITY_OT_walk);bpy.utils.register_class(FACILITY_PT_walk)
 bpy.types.Scene.facility_fast_walkthrough=bpy.props.BoolProperty(default=True,update=apply_display)
 bpy.types.Scene.facility_show_guides=bpy.props.BoolProperty(default=False,update=apply_display)
 kc=bpy.context.window_manager.keyconfigs.addon
 if kc:
  km=kc.keymaps.new(name='3D View',space_type='VIEW_3D')
  kmi=km.keymap_items.new('view3d.facility_safe_walk','F','PRESS',shift=True)
  _keys.append((km,kmi))
 bpy.app.handlers.load_post.append(on_load)

def unregister():
 for km,kmi in _keys:km.keymap_items.remove(kmi)
 _keys.clear()
 if on_load in bpy.app.handlers.load_post:bpy.app.handlers.load_post.remove(on_load)
 del bpy.types.Scene.facility_fast_walkthrough
 del bpy.types.Scene.facility_show_guides
 bpy.utils.unregister_class(FACILITY_PT_walk);bpy.utils.unregister_class(FACILITY_OT_walk)

