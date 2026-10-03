import pathlib,hashlib,json,subprocess,sys,time
OUT=pathlib.Path(__file__).resolve().parent;ROOM=OUT.parents[3];REPO=ROOM.parents[3]
expected=json.loads((ROOM/'revamp/production/protected-inputs.json').read_text())
expected.update({str((ROOM/'module_overhaul_R1.blend').relative_to(REPO)):'6838d604ac4586da057a652e98e9c694f754a84e9f38ba70b83f1046e9ae6e9a'})
expected.update({str((ROOM/n).relative_to(REPO)):h for n,h in {'overhaul_dock.py':'347c84da9e72547935adc50b755c1b95ff3b161ddf5019d689bf0ef86ba7cd6c','full_detail.py':'1521449b1c6eee88689cadb6e43ae911e909f200655b335cd273b9a030a3ef0e','full_repairs.py':'5edc8c94dcc4e6c17ac5af60815136f02b41cdd64afee381f8505d3df16c1657','render_dock.py':'38d50f5ec2f64755c9f1f2fe35d4e46e98f74dc71c3df327c9d32a18012e28ce'}.items()})
def hashes():
 return {n:hashlib.sha256((REPO/n).read_bytes()).hexdigest() for n in expected}
mode=sys.argv[1];before=hashes();assert before==expected, 'Hash guard rejected changed source'
binary='/workspace/tools/blender-5.2.2-linux-x64/blender'
cmd=[binary,'--background','--disable-autoexec',str(ROOM/'module_overhaul_R1.blend'),'--threads','1','--python-exit-code','1','--python']
if mode=='probe':cmd += [str(OUT/'probe.py')]
elif mode=='intersections':cmd += [str(OUT/'intersections_probe.py')]
elif mode=='crossing-area':cmd += [str(OUT/'crossing_area_probe.py')]
elif mode=='validator':cmd += [str(ROOM/'validate_dock.py'),'--','--output',str(OUT/'existing-validator.json'),'--interface',str(ROOM/'contracts/interface.json'),'--expected-stage','full']
else:raise ValueError(mode)
start=time.time()
with (OUT/(mode+'.log')).open('w') as log:r=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
after=hashes();record={'command':cmd,'exit_status':r.returncode,'elapsed_s':time.time()-start,'before':before,'after':after,'expected':expected,'hash_guard_pass':before==after==expected}
(OUT/(mode+'-process.json')).write_text(json.dumps(record,indent=2));assert after==expected,'Post-process hash mismatch';sys.exit(r.returncode)
