"""Meaningful negative check: a missing wall-prop registration must be rejected.

Open the completed candidate, then run this script with -- /path/to/report.json.
The scene is modified only in memory and never saved.
"""
import bpy
import json
import runpy
import sys
from pathlib import Path

field='cafeteria_revamp_supports'
original=bpy.context.scene[field]
registrations=json.loads(original)
assert any(r['object']=='rules_game' for r in registrations)
bpy.context.scene[field]=json.dumps([r for r in registrations if r['object']!='rules_game'])
report=Path(sys.argv[sys.argv.index('--')+1])
try:
    runpy.run_path(str(Path(__file__).resolve().parent.parent/'validate_front_end.py'),run_name='__main__')
except RuntimeError as exc:
    assert 'support_registration_coverage' in str(exc),str(exc)
    data=json.loads(report.read_text())
    assert data['cafeteria_revamp']['support_coverage']['missing']==['rules_game']
    data['negative_check']={'pass':True,'removed_registration':'rules_game','validator_rejected':True,'scene_saved':False}
    report.write_text(json.dumps(data,indent=2)+'\n')
    print('NEGATIVE_SUPPORT_GATE_PASS',flush=True)
else:
    raise AssertionError('Validator accepted an independently mounted unregistered prop')
finally:
    bpy.context.scene[field]=original
