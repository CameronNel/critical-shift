bl_info={'name':'Critical Shift Access Controls','author':'Critical Shift','version':(1,0,0),'blender':(5,2,0),'category':'3D View'}
import bpy,time
from mathutils import Vector
from bpy.app.handlers import persistent
_last=0.;_cache=[];_scene=None;_leaves={}
def doors():
 global _cache,_scene,_leaves
 if _scene!=bpy.context.scene or not _cache:
  col=bpy.data.collections.get('12_ACCESS_MOVING_PARTS');_cache=[o for o in col.objects if o.get('access_door')] if col else [];_scene=bpy.context.scene
  _leaves={o.parent.name:o for o in col.objects if o.get('door_leaf') and o.parent} if col else {}
 return _cache
def views():
 for screen in bpy.data.screens:
  for a in screen.areas:
   if a.type=='VIEW_3D':
    rv=a.spaces.active.region_3d
    if rv.view_perspective=='PERSP':yield rv
def eye(rv):return rv.view_location+rv.view_rotation@Vector((0,0,rv.view_distance))
def prop(o,key,value):
 if o.get(key)!=value:o[key]=value
def request_door(o,opened):
 if o.get('cabin_gate'):
  lift=bpy.data.objects.get('ACCESS_CART_LIFT')
  if opened and (abs(lift['target_z']-lift.location.z)>.015 or min(abs(lift.location.z),abs(lift.location.z+6))>.015):return False
 if 'lift_gate_z' in o:
  lift=bpy.data.objects.get('ACCESS_CART_LIFT')
  if opened and (abs(lift.location.z-o['lift_gate_z'])>.015 or abs(lift['target_z']-lift.location.z)>.015):return False
 if opened and o.get('group'):
  for other in doors():
   if other!=o and other.get('group')==o['group'] and other.get('side')!=o['side']:prop(other,'target',0.)
 prop(o,'target',float(opened));return True
def request_lift(z):
 lift=bpy.data.objects.get('ACCESS_CART_LIFT')
 if not lift:return False
 lift['target_z']=min(0.,max(-6.,float(z)))
 for o in doors():
  if 'lift_gate_z' in o or o.get('cabin_gate'):prop(o,'target',0.)
 return True
def step(dt,rv=None,auto=False):
 ds=doors();lift=bpy.data.objects.get('ACCESS_CART_LIFT');p=eye(rv) if rv else None
 if auto and p is not None:
  near=[]
  for o in ds:
   if 'lift_gate_z' in o or o.get('cabin_gate'):continue
   q=o.matrix_world.inverted()@p
   # Test against the width of the portal, not merely its centre point.
   distance=max(abs(q.x)-o['width']/max(.001,o.scale.x)/2,0)**2+q.y*q.y
   if -.2<q.z<2.5 and distance<3.2**2:near.append((distance,o))
   elif distance>4**2 or q.z<-.5 or q.z>3:prop(o,'target',0.)
  # One side per interlock per tick, stable until the observer leaves that side.
  groups=set()
  for dist,o in sorted(near,key=lambda x:x[0]):
   g=o.get('group')
   if g and g in groups:continue
   request_door(o,True)
   if g:groups.add(g)
 for o in ds:
  target=float(o['target'])
  if target and o.get('group') and any(other.get('group')==o['group'] and other.get('side')!=o['side'] and other['open']>.001 for other in ds):target=0.
  val=float(o['open']);new=val+max(-dt*1.5,min(dt*1.5,target-val))
  if new!=val:
   o['open']=new
   ch=_leaves.get(o.name)
   if ch:ch.scale.z=1-.985*new
 if lift:
  z=lift.location.z;t=lift['target_z'];gates=[o for o in ds if 'lift_gate_z' in o or o.get('cabin_gate')]
  if abs(t-z)>.001 and all(o['open']<.001 for o in gates):
   dz=max(-dt*lift['speed'],min(dt*lift['speed'],t-z));lift.location.z+=dz
   if p is not None and 28.98<p.x<31.12 and 33.4<p.y<36.3 and z+.1<p.z<z+2.35:rv.view_location.z+=dz
  if abs(t-lift.location.z)<.001:
   prop(lift,'floor_z',t)
   for o in gates:prop(o,'target',float(o.get('cabin_gate') or abs(o.get('lift_gate_z',99)-t)<.001))
def tick():
 global _last
 now=time.monotonic();dt=min(.10,now-_last) if _last else .04;_last=now
 try:
  if doors():step(dt,next(views(),None),bpy.context.scene.facility_auto_doors)
 except (ReferenceError,AttributeError):reset(None)
 return .04
@persistent
def reset(_):
 global _cache,_scene,_last,_leaves
 _cache=[];_scene=None;_last=0;_leaves={}
class ACCESS_OT_door(bpy.types.Operator):
 bl_idname='facility.toggle_nearest_door';bl_label='Toggle nearest door'
 def execute(self,context):
  rv=context.space_data.region_3d if context.area.type=='VIEW_3D' else next(views(),None)
  ds=doors()
  if not rv or not ds:return {'CANCELLED'}
  p=eye(rv);o=min(ds,key=lambda x:(x.matrix_world.translation-p).length);request_door(o,not o['target']);return {'FINISHED'}
class ACCESS_OT_lift(bpy.types.Operator):
 bl_idname='facility.move_cart_lift';bl_label='Move cart lift'
 floor:bpy.props.FloatProperty(default=0)
 def execute(self,context):request_lift(self.floor);return {'FINISHED'}
class ACCESS_PT_panel(bpy.types.Panel):
 bl_label='Doors and Cart Lift';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Walkthrough'
 def draw(self,context):
  l=self.layout;l.prop(context.scene,'facility_auto_doors',text='Automatic proximity doors');l.operator('facility.toggle_nearest_door')
  row=l.row();row.operator('facility.move_cart_lift',text='Lift to ground').floor=0;row.operator('facility.move_cart_lift',text='Lift to condenser').floor=-6
  lift=bpy.data.objects.get('ACCESS_CART_LIFT')
  if lift:l.label(text=f'Lift: {lift.location.z:.2f} m')
  l.label(text='Step inside before sending the lift.')
  l.label(text='Shift F walk; E/Q changes elevation.')
def register():
 for cls in [ACCESS_OT_door,ACCESS_OT_lift,ACCESS_PT_panel]:bpy.utils.register_class(cls)
 bpy.types.Scene.facility_auto_doors=bpy.props.BoolProperty(default=True)
 bpy.app.handlers.load_post.append(reset);bpy.app.timers.register(tick,first_interval=.2,persistent=True)
def unregister():
 if bpy.app.timers.is_registered(tick):bpy.app.timers.unregister(tick)
 if reset in bpy.app.handlers.load_post:bpy.app.handlers.load_post.remove(reset)
 for cls in reversed([ACCESS_OT_door,ACCESS_OT_lift,ACCESS_PT_panel]):bpy.utils.unregister_class(cls)
 del bpy.types.Scene.facility_auto_doors
