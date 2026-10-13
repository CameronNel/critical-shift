from pathlib import Path
import subprocess,time,json,hashlib
root=Path('/workspace/critical-shift-spawn-runtime');audit=root/'runtime/out/mine-bake-audit';python='/home/agent/.local/share/critical-shift/venv/bin/python';blender='/home/agent/.local/bin/blender'
state=audit/'fresh-export-final12-state.json'
while True:
 status=json.loads(state.read_text())
 if status['state']=='Failed':raise RuntimeError('Full source export failed; followup controls not launched')
 if status['state']=='Finished':break
 time.sleep(2)
print('CS_FINAL12_CURRENT_SOURCE_EXPORT_READY_FOR_FOLLOWUP',flush=True)
def source(script,label):
 with (audit/(label+'.source.log')).open('w') as log:subprocess.run([blender,'-b',str(root/'runtime/out/spawn-export-source/combined-runtime-source.blend'),'--disable-autoexec','--python-exit-code','1','--threads','4','--python',script],stdout=log,stderr=subprocess.STDOUT,check=True)
source('/tmp/cs-mine-source-stable-board-final12.py','source-stable-board-final12')
print('CS_FINAL12_STABLE_SOURCE_REFERENCE_READY',flush=True)
subprocess.run([python,'/tmp/cs-mine-source-hybrid-lambert-probe-final12.native.py'],cwd=root,check=True)
print('CS_FINAL12_LAMBERT_PROBE_CAPTURE_READY_FOR_REVIEW',flush=True)
with (audit/'probe-uniform-preflight-final12.source.log').open('w') as log:subprocess.run([blender,'-b','--factory-startup','--disable-autoexec','--python-exit-code','1','--threads','4','--python','/tmp/cs-mine-probe-uniform-preflight-final12.py'],stdout=log,stderr=subprocess.STDOUT,check=True)
assert json.loads(Path('/tmp/cs-mine-probe-uniform-preflight-final12/provenance.json').read_text())['status']=='PassedUniformWorldBakePreflightOnly'
print('CS_FINAL12_INVISIBLE_PROBE_UNIFORM_PREFLIGHT_READY',flush=True)
source('/tmp/cs-mine-source-probe-field-final12.py','source-probe-field-final12')
print('CS_FINAL12_SOURCE_ONE_PROBE_FIELD_READY_FOR_FIT',flush=True)
subprocess.run([python,'/tmp/cs-mine-sh-basis-final12.native.py'],cwd=root,check=True)
print('CS_FINAL12_ACTUAL_GPU_CPU_SH_BASIS_READY_FOR_FIT',flush=True)
