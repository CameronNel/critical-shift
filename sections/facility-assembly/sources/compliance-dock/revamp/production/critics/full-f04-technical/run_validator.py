import bpy, importlib.util, json
from pathlib import Path
from types import SimpleNamespace
root=Path('/workspace/critical-shift/sections/facility-assembly/sources/compliance-dock')
out=root/'revamp/production/critics/full-f04-technical'
bpy.context.window.scene=bpy.data.scenes['COMPLIANCE_EDIT_LOCAL']
spec=importlib.util.spec_from_file_location('dock_validator',root/'validate_dock.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
v=mod.Validator(SimpleNamespace(expected_stage='full',interface=str(root/'contracts/interface.json')))
v.run();r=v.report;r['passed']=not r['errors'];r['summary']={'failures':len(r['errors']),'passed_checks':sum(c['status']=='pass' for c in r['checks']),'failed_checks':sum(c['status']=='fail' for c in r['checks'])}
(out/'validator.json').write_text(json.dumps(mod.json_safe(r),indent=2,allow_nan=False))
records=[dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,properties={k:str(o[k]) for k in o.keys()},matrix=[list(x) for x in o.matrix_world],materials=[m.name if m else None for m in o.data.materials] if hasattr(o.data,'materials') else []) for o in bpy.context.scene.objects]
(out/'objects.json').write_text(json.dumps(records,indent=2))
print('F04_VALIDATOR',r['summary'],flush=True)
print('F04_ERRORS',json.dumps(r['errors']),flush=True)
