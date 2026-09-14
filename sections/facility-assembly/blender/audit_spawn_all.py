"""Run revision-matched delivery/contact/route checks with one cold load."""
import bpy,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];rev=os.environ.get('SPAWN_REV','R07')
os.environ['MAP_AUDIT_FILE']='facility_spawn_concept02_'+rev+'.blend'
for index,name in enumerate(['audit_spawn_delivery.py','audit_spawn_concept02.py','audit_map_routes.py']):
 source=(R/'blender'/name).read_text()
 if index:
  source='\n'.join(line for line in source.splitlines() if not line.startswith('bpy.ops.wm.open_mainfile('))
 if index==2:
  bpy.data.collections['29_SPAWN_APPROVED_EXTERIOR'].hide_viewport=False
 exec(compile(source,str(R/'blender'/name),'exec'),{'__file__':str(R/'blender'/name),'__name__':'__main__'})
print('COMBINED_AUDIT_COMPLETE',rev,flush=True)
