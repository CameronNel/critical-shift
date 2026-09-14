"""Open the current authored-art preview, not the Solid-mode cache."""
import bpy,os,sys,importlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'blender'/os.environ.get('PREVIEW_SOURCE','facility_spawn_material_preview_R17.blend')),load_ui=False)
sys.path.insert(0,str(R/'blender'))
for module in ['facility_walkthrough_tools','facility_access_tools','facility_material_preview']:
 loaded=importlib.import_module(module)
 if not getattr(loaded,'_map_registered',False):
  loaded.register();loaded._map_registered=True
import facility_material_preview
s=bpy.context.scene;s['material_preview']=True
if hasattr(s,'facility_distance_detail'):s.facility_distance_detail=False
facility_material_preview.tick()
bpy.context.preferences.inputs.navigation_mode='WALK';bpy.context.preferences.inputs.walk_navigation.use_gravity=False
for w in bpy.context.window_manager.windows:
 for a in w.screen.areas:
  if a.type!='VIEW_3D':continue
  v=a.spaces.active;r=v.region_3d;eye=Vector((-28,14,1.7));rot=(Vector((-20,28,1.7))-eye).to_track_quat('-Z','Y')
  r.view_perspective='PERSP';r.view_rotation=rot;r.view_distance=1;r.view_location=eye+rot@Vector((0,0,-1))
  v.shading.type='RENDERED';v.overlay.show_overlays=False;v.clip_start=.05;v.clip_end=220
if os.environ.get('MAP_ENABLE_MCP')=='1':
 try:
  bpy.ops.preferences.addon_enable(module='bl_ext.user_default.blender_mcp')
  s.blendermcp_allow_ai_control=True;bpy.ops.blendermcp.start_server()
 except Exception as exc:print('Optional Blender MCP unavailable:',exc)
