bl_info={'name':'Critical Shift Distance Detail','author':'Critical Shift','version':(1,0,0),'blender':(5,2,0),'category':'3D View'}
"""Optional distance-based viewport detail for the assembled map. Render geometry is untouched."""
import bpy
from mathutils import Vector
from bpy.app.handlers import persistent
ROOMS={'spawn-room','refinery','fuel-corridor','reactor-room','cooling-plant','turbine-room','condenser-bay','electrical-room','waste-storage','medical-reanimation','compliance-dock'}
# Mine source includes the outdoor cliff silhouette, so it must never be culled.
_original={}
def distance_squared(point,lo,hi):
 return sum(max(lo[i]-point[i],0,point[i]-hi[i])**2 for i in range(3))
def restore():
 for name,hidden in list(_original.items()):
  ob=bpy.data.objects.get(name)
  if ob:ob.hide_set(hidden)
 _original.clear()
def tick():
 try:
  s=bpy.context.scene
  enabled=getattr(s,'facility_distance_detail',False) and getattr(s,'facility_fast_walkthrough',False)
  eyes=[]
  for win in bpy.context.window_manager.windows:
   for area in win.screen.areas:
    if area.type=='VIEW_3D':
     rv=area.spaces.active.region_3d
     if rv.view_perspective!='PERSP':enabled=False
     eyes.append(rv.view_location+rv.view_rotation@Vector((0,0,rv.view_distance)))
  if not enabled or not eyes:restore();return .5
  for sid in ROOMS:
   ob=bpy.data.objects.get('WALK_PROXY_'+sid)
   if not ob:continue
   if ob.name not in _original:_original[ob.name]=ob.hide_get()
   if _original[ob.name]:continue
   points=[ob.matrix_world@Vector(v) for v in ob.bound_box]
   lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
   near=min(distance_squared(eye,lo,hi) for eye in eyes)
   # Wider hide threshold avoids flicker when walking along the boundary.
   radius=s.facility_detail_radius+(0 if ob.hide_get() else 5)
   hidden=near>radius*radius
   if ob.hide_get()!=hidden:ob.hide_set(hidden)
 except (ReferenceError,RuntimeError,AttributeError):_original.clear()
 return .5
@persistent
def before_load(_):restore()
class FACILITY_PT_distance(bpy.types.Panel):
 bl_label='Distant interior detail';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Walkthrough'
 def draw(self,context):
  self.layout.prop(context.scene,'facility_distance_detail',text='Hide distant interior detail')
  self.layout.prop(context.scene,'facility_detail_radius',text='Detail distance')
  self.layout.label(text='Exteriors and mine remain visible')
def register():
 bpy.types.Scene.facility_distance_detail=bpy.props.BoolProperty(default=True)
 bpy.types.Scene.facility_detail_radius=bpy.props.FloatProperty(default=25,min=20,max=150,subtype='DISTANCE')
 bpy.utils.register_class(FACILITY_PT_distance)
 bpy.app.handlers.load_pre.append(before_load)
 bpy.app.handlers.save_pre.append(before_load)
 bpy.app.timers.register(tick,persistent=True)
def unregister():
 if bpy.app.timers.is_registered(tick):bpy.app.timers.unregister(tick)
 restore()
 if before_load in bpy.app.handlers.load_pre:bpy.app.handlers.load_pre.remove(before_load)
 if before_load in bpy.app.handlers.save_pre:bpy.app.handlers.save_pre.remove(before_load)
 bpy.utils.unregister_class(FACILITY_PT_distance)
 del bpy.types.Scene.facility_distance_detail
 del bpy.types.Scene.facility_detail_radius
