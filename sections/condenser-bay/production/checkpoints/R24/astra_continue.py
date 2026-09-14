"""Reapply the replayable polish to the immutable, hash-checked Grok R21 baseline.

This avoids rebuilding the untouched 2325-object room for each correction cycle.
build_condenser.py remains the factory-source replay alternative.
"""
import ast
import hashlib
import json
import shutil
import sys
from pathlib import Path
import bpy

HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(HERE))
import kit as k
rev=sys.argv[sys.argv.index('--')+1]
baseline=ROOT/'production/checkpoints/R21/grok-baseline.blend'
expected='ff361817176958680f4d80c35fcae54a9acb04b5a75ea176148ad51c440c23e2'
assert hashlib.sha256(baseline.read_bytes()).hexdigest()==expected,'Baseline changed'
bpy.ops.wm.open_mainfile(filepath=str(baseline))
S=bpy.context.scene; k.S=S
# Bind original named materials without creating variants of the baseline palette.
module=ast.parse((HERE/'kit.py').read_text())
palette=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='palette')
mapping=next(n.value for n in palette.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Dict))
k.M={}
for key,value in zip(mapping.keys,mapping.values):
    material=bpy.data.materials.get(value.args[0].value)
    if material is None:
        material=k.material(*[ast.literal_eval(a) for a in value.args],
                            **{a.arg:ast.literal_eval(a.value) for a in value.keywords})
    k.M[key.value]=material
k.SUPPORT=json.loads(S.get('support_registry','[]')); k.HOOKS=json.loads(S.get('interaction_hooks','[]'))
from astra_polish import apply_polish
print('ASTRA_BASELINE_LOADED',len(S.objects),flush=True)
apply_polish()
S['source_revision']=rev
S['astra_baseline_sha256']=expected
S['support_registry']=json.dumps(k.SUPPORT)
S['interaction_hooks']=json.dumps(k.HOOKS)
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob('*.py'))}
S['authoring_source_sha256']=json.dumps(hashes)
interface=json.loads((ROOT/'interface.json').read_text()); interface['revision']=rev
interface['circulation']['west_cart_lane']={'min':[-.35,.05,0],'max':[.45,6.25,2.2],
    'note':'Measured usable strip within broader equipment aisle; straight approach only.'}
interface['circulation']['gallery_deck_z']=float(S.get('astra_gallery_deck_z',4.18))
(ROOT/'interface.json').write_text(json.dumps(interface,indent=2))
ckpt=ROOT/'production/checkpoints'/rev; ckpt.mkdir(parents=True,exist_ok=True)
for p in HERE.glob('*.py'): shutil.copy2(p,ckpt/p.name)
blend=HERE/'condenser_bay.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
sha=hashlib.sha256(blend.read_bytes()).hexdigest()
manifest={'revision':rev,'baseline_sha256':expected,'blend_sha256':sha,'source_sha256':hashes,
          'counts':{'objects':len(S.objects),'cameras':sum(o.type=='CAMERA' for o in S.objects)},
          'method':'Documented R21 saved-baseline continuation; camera corrections recorded in production/CAMERA_CORRECTIONS.md.'}
out=ROOT/'production/renders/review'/rev;out.mkdir(parents=True,exist_ok=True)
(out/'build_manifest.json').write_text(json.dumps(manifest,indent=2))
(ckpt/'build_manifest.json').write_text(json.dumps(manifest,indent=2))
shutil.copy2(blend,ckpt/'condenser_bay.blend')
print('ASTRA_CONTINUATION_SAVED',rev,sha,flush=True)
from validate import main
sys.exit(main())
