"""Read-only master inspection cameras: actual gaps and exterior faces."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'blender/facility_master.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
scene=bpy.context.scene
views=[
 ('J01_MINE_REFINERY','Mine to refinery',(-5,-39,3),(-5,-27,1.5),24),
 ('J02_REFINERY_FUEL','Refinery to fuel corridor',(12,-4,3),(0,-4,1.6),24),
 ('J03_FUEL_REACTOR','Fuel corridor to reactor',(27,28,3),(14.2,28,2),24),
 ('J04_REACTOR_TURBINE','Reactor to turbine',(34,32,3),(34,46.5,2),24),
 ('J05_TURBINE_ELECTRICAL','Turbine to electrical',(80,37,3),(66,37,2),23),
 ('J06_ELECTRICAL_WASTE','Electrical to waste',(80,6.5,3),(66,6.5,1.6),24),
 ('J07_COOLING_REACTOR','Cooling to reactor',(-12,53,3),(.1,60.3,2),24),
 ('J08_CLEAN_HEADER','Spawn / medical clean header',(-42,28,2.2),(-21,28,1.8),24),
 ('J09_CONDENSER_ACCESS','Reserved condenser stair / lift',(26,36,3),(40,43,-2),23),
 ('J10_COMPLIANCE_HEADER','Compliance to clean header',(-41,8,2.5),(-41,23,1.7),24),
 ('E01_DOCK_EXTERIOR','Outside compliance arrival',(-82,16,2.2),(-64,16,2),28),
 ('E02_FACILITY_EXTERIOR','Outside the power wing',(92,-10,15),(45,36,4),29),
]
scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH'
scene.view_settings.view_transform='Standard';scene.view_settings.exposure=.35
scene.display.shading.background_type='WORLD';scene.world.color=(.12,.14,.16)
# High floating master-plan annotations obstruct eye-level inspection. Only their
# dedicated planning collection is hidden in this unsaved render session.
bpy.data.collections['04_PLANNING_LABELS'].hide_render=True
out=ROOT/'production/connection-views';out.mkdir(exist_ok=True)
manifest={'source_sha256':before,'master_saved':False,'geometry_hidden':False,'planning_labels_hidden':True,'mode':'Workbench solid/material-color layout preview; not final room lighting','views':[]}
for name,caption,loc,target,lens in views:
 data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.clip_start=.05;data.clip_end=500;scene.camera=ob
 scene.render.filepath=str(out/f'{name}.png');bpy.ops.render.render(write_still=True)
 manifest['views'].append({'id':name,'caption':caption,'location':loc,'target':target,'lens_mm':lens,'sha256':hashlib.sha256((out/f'{name}.png').read_bytes()).hexdigest()})
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2));print('CONNECTION_VIEW_DONE',name,flush=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
print('CONNECTION_VIEWS_COMPLETE_MASTER_UNCHANGED',flush=True)
