bl_info={'name':'Critical Shift Material Preview','author':'Critical Shift','version':(1,0,0),'blender':(5,2,0),'category':'3D View'}
import bpy
from mathutils import Vector
from bpy.app.handlers import persistent
SOURCES=['01_LINKED_ROOMS','06_LINKED_EXTERIORS','CONNECTION_C01_RESCUE_COURTYARD','09_FINISHED_HORIZONTAL_CONNECTIONS','13_FINISHED_ACCESS_SCENERY','15_FINISHED_NETWORK_SCENERY','17_REACTOR_EXTERIOR_FINISH','20_ROOF_SERVICE_GEOMETRY','22_EXTERIOR_FINISH_GEOMETRY']
CACHES=['07_FAST_WALKTHROUGH_PROXIES','10_NETWORK_VIEWPORT_CACHE','14_ACCESS_FINISH_VIEWPORT_CACHE','16_NETWORK_FINISH_VIEWPORT_CACHE','18_REACTOR_FINISH_VIEWPORT_CACHE','21_ROOF_SERVICE_VIEWPORT_CACHE','23_EXTERIOR_FINISH_VIEWPORT_CACHE']
ROOMS={'spawn-room','refinery','fuel-corridor','reactor-room','cooling-plant','turbine-room','condenser-bay','electrical-room','waste-storage','medical-reanimation','compliance-dock'}
_hidden=set()
def restore():
 for name in list(_hidden):
  o=bpy.data.objects.get(name)
  if o:o.hide_set(False)
 _hidden.clear()
def tick():
 try:
  s=bpy.context.scene
  if not s.get('material_preview'):return .5
  for n in SOURCES+CACHES:
   c=bpy.data.collections.get(n)
   if c and not c.hide_viewport:c.hide_viewport=True
  eyes=[];ortho=False
  for w in bpy.context.window_manager.windows:
   for a in w.screen.areas:
    if a.type=='VIEW_3D':
     r=a.spaces.active.region_3d;ortho|=r.view_perspective!='PERSP';eyes.append(r.view_location+r.view_rotation@Vector((0,0,r.view_distance)))
  if not eyes or ortho:restore();return .5
  col=bpy.data.collections.get('27_MATERIAL_PREVIEW');room_distance={}
  if col:
   for o in col.objects:
    if o.get('preview_source') not in ROOMS|{'mine'}:continue
    pts=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
    near=min(sum(max(lo[i]-e[i],0,e[i]-hi[i])**2 for i in range(3)) for e in eyes)
    room_distance[o.get('preview_source')]=near
    if o.get('preview_source')=='mine':continue
    hide=near>(12 if o.hide_get() else 17)**2
    if o.hide_get()!=hide:o.hide_set(hide)
    if hide:_hidden.add(o.name)
    else:_hidden.discard(o.name)
  col=bpy.data.collections.get('28_MATERIAL_PREVIEW_LIGHTS')
  if col:
   for o in col.objects:
    if o.type!='LIGHT' or o.data.type=='SUN':continue
    hide=min((o.matrix_world.translation-e).length_squared for e in eyes)>28**2
    library=o.data.library.filepath.replace('\\','/') if o.data.library else ''
    if '/sources/' in library:
     sid=library.split('/sources/')[1].split('/')[0]
     hide|=room_distance.get(sid,0)>5**2
    if hide!=o.hide_get():o.hide_set(hide)
    if hide:_hidden.add(o.name)
    else:_hidden.discard(o.name)
 except (ReferenceError,RuntimeError):pass
 return .5
@persistent
def before_save(_):restore()
def register():
 bpy.app.handlers.save_pre.append(before_save);bpy.app.handlers.load_pre.append(before_save)
 bpy.app.timers.register(tick,persistent=True)
def unregister():
 if bpy.app.timers.is_registered(tick):bpy.app.timers.unregister(tick)
 for h in [bpy.app.handlers.save_pre,bpy.app.handlers.load_pre]:
  if before_save in h:h.remove(before_save)
 restore()
