import bpy,shutil
from pathlib import Path
R=Path(r'C:/Users/Camer/Games/critical-shift/worktrees/facility-assembly-astra/sections/facility-assembly/blender')
p=R/'facility_master_A06_connections.blend'
shutil.copy2(p,R/'facility_master_A06_before_floor.blend')
with bpy.data.libraries.load(str(p),link=False) as (src,dst):dst.scenes=src.scenes
scenes=dst.scenes
with bpy.data.libraries.load(str(R/'whole_map_floor.blend'),link=False) as (src,dst):dst.collections=['08_WHOLE_MAP_FLOOR']
for s in scenes:s.collection.children.link(dst.collections[0])
bpy.data.libraries.write(str(p),set(scenes),path_remap='RELATIVE',compress=True)
print('MASTER_FLOOR_SAVED',len(scenes))
