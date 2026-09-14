import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:/Users/Camer/Games/critical-shift/worktrees/facility-assembly-astra/sections/facility-assembly/connections/rescue-courtyard/review-B04.blend')
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
  if hi[2]>15 or 'medic' in o.name.lower():print(o.name,lo,hi)
