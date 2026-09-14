"""Run all saved-scene CPU audits in one read-only Blender process."""
import hashlib,json,runpy,sys
from pathlib import Path
import bpy
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here))
checks=[]
for name in ['validate.py','astra_audit.py','astra_inlet_audit.py','astra_joint_audit.py','astra_fastener_audit.py','astra_measure.py']:
    try:
        runpy.run_path(str(here/name),run_name='__main__')
    except SystemExit as result:
        if result.code not in (None,0):raise
    checks.append(name)
report={'status':'PASS','revision':bpy.context.scene.get('source_revision'),
        'blend_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
        'checks':checks,'process_id':__import__('os').getpid(),
        'scope':'CPU saved-geometry and dependency checks; no render, game-engine or remote integration certification.'}
out=here.parent/'production/validation'/str(report['revision'])/'cpu-validation-summary.json'
out.write_text(json.dumps(report,indent=2)+'\n')
print('ALL_SAVED_CPU_AUDITS_PASS',json.dumps(report),flush=True)
