"""Launch-only setup for the separate, gravity-free Blender walkthrough copy."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
master=ROOT/'blender/facility_master_A05_exteriors.blend'
output=next((ROOT/'blender'/n for n in ['facility_walkthrough_A13_roof_services.blend','facility_walkthrough_A12_complete.blend','facility_walkthrough_A11_map_finish.blend','facility_walkthrough_A08_access.blend','facility_walkthrough_A07_horizontal_network.blend','facility_walkthrough_A06_connections.blend','facility_walkthrough.blend'] if (ROOT/'blender'/n).exists()),ROOT/'blender/facility_walkthrough.blend')
source=output if output.exists() else master
original_hash=hashlib.sha256(master.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
walk=bpy.context.preferences.inputs.walk_navigation
walk.use_gravity=False
walk.walk_speed=3.0
walk.walk_speed_factor=3.0
walk.view_height=1.7
bpy.context.preferences.inputs.navigation_mode='WALK'
eye=Vector((31.1,46,1.7)) if any(v in output.name for v in ('A08','A11','A12','A13')) else Vector((-35,28,1.7))
target=Vector((31.1,40,-2)) if any(v in output.name for v in ('A08','A11','A12','A13')) else Vector((-10,28,1.7))
rotation=(target-eye).to_track_quat('-Z','Y')
views=0
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type!='VIEW_3D': continue
  space=area.spaces.active
  space.shading.type='SOLID'
  space.shading.color_type='MATERIAL'
  space.shading.light='STUDIO'
  space.overlay.show_overlays=False
  space.clip_start=.05
  space.clip_end=1000
  space.lens=28
  rv=space.region_3d
  rv.view_perspective='PERSP'
  rv.view_rotation=rotation
  rv.view_distance=1.0
  rv.view_location=eye+rotation@Vector((0,0,-1))
  views+=1
assert views and not walk.use_gravity
bpy.utils.refresh_script_paths()
for module in ['bl_ext.user_default.blender_mcp','facility_walkthrough_tools','facility_access_tools']:
 bpy.ops.preferences.addon_enable(module=module)
import facility_walkthrough_tools
facility_walkthrough_tools.apply_display(bpy.context.scene)
bpy.context.scene.blendermcp_allow_ai_control=True
bpy.ops.blendermcp.start_server()
bpy.context.scene['walkthrough_controls']='Shift+F to start; WASD move, mouse look; E/Q up/down; left click confirm, Esc cancel. Gravity OFF. N > Walkthrough for fast/original display.'
bpy.ops.wm.save_as_mainfile(filepath=str(output),compress=True,relative_remap=True)
assert hashlib.sha256(master.read_bytes()).hexdigest()==original_hash
(ROOT/'production/WALKTHROUGH_READY.json').write_text(json.dumps({'file':str(output),'gravity':walk.use_gravity,'viewports':views,'eye':list(eye),'mode':'Solid material colors for responsive navigation','master_unchanged':True,'controls':'Shift+F then WASD/mouse. E up, Q down. Left click confirms; Esc cancels.','limits':'Free navigation across reserved gaps; no game collision or navmesh.'},indent=2))
print('WALKTHROUGH_READY',str(output),flush=True)
