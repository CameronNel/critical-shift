"""Apply pending root repair code to exact published F17 recipes; does not build/save Blender."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[3]
P=R/'revamp/production'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(R/'module_overhaul_R1.blend')=='6838d604ac4586da057a652e98e9c694f754a84e9f38ba70b83f1046e9ae6e9a'
expected={'overhaul_dock.py':'347c84da9e72547935adc50b755c1b95ff3b161ddf5019d689bf0ef86ba7cd6c','full_detail.py':'1521449b1c6eee88689cadb6e43ae911e909f200655b335cd273b9a030a3ef0e','full_repairs.py':'5edc8c94dcc4e6c17ac5af60815136f02b41cdd64afee381f8505d3df16c1657','render_dock.py':'38d50f5ec2f64755c9f1f2fe35d4e46e98f74dc71c3df327c9d32a18012e28ce'}
for name,h in expected.items():assert sha(R/name)==h,('Unexpected current recipe; reconcile deliberately',name)
assert json.loads((P/'FULL_CYCLE_09.json').read_text())['all_six_readers_explicitly_released']
functions=Path(__file__).with_name('F18_FUNCTIONS_PENDING.py').read_text()
updates={}
for name,before,after in [
 ('full_detail.py','    ninth_review_repairs()\n','    ninth_review_repairs()\n    tenth_review_repairs()\n'),
 ('overhaul_dock.py','    ninth_review_lighting()\n','    ninth_review_lighting()\n    tenth_review_lighting()\n'),
 ('full_repairs.py','    verify_fifth_review_interfaces()\n','    finish_tenth_review_uv()\n    verify_fifth_review_interfaces()\n')]:
 s=(R/name).read_text();assert s.count(before)==1,(name,s.count(before));s=s.replace(before,after)
 if name=='full_repairs.py':s+='\n\n'+functions
 compile(s,str(R/name),'exec');updates[name]=s
for name,s in updates.items():(R/name).write_text(s)
out={'pending_revision':'f18','native_still_f17':True,'native_sha256':sha(R/'module_overhaul_R1.blend'),'recipe_sha256':{n:sha(R/n) for n in expected},'full_build_executed':False,'native_written':False,'rendered':False,'accepted':False}
(P/'F18_APPLIED_PENDING_BUILD.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
