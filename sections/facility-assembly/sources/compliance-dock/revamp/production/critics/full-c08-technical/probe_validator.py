import bpy,runpy,sys,hashlib
from pathlib import Path
R=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock');S=R/'module_overhaul_R1.blend';H='d2514e668ea2b24e8b4ede6bde870e12f10c1afd6d6e1892b12c016266bd7b35'
assert hashlib.sha256(S.read_bytes()).hexdigest()==H
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False);bpy.context.window.scene=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL']
sys.argv=['probe_validator.py','--','--output',str(R/'revamp/production/critics/full-c08-technical/existing-validator.json'),'--interface',str(R/'contracts/interface.json'),'--expected-stage','full']
try:runpy.run_path(str(R/'validate_dock.py'),run_name='__main__')
finally:assert hashlib.sha256(S.read_bytes()).hexdigest()==H
