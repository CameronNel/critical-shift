from pathlib import Path
import time,subprocess,shutil
root=Path('/workspace/critical-shift-spawn-runtime');audit=root/'runtime/out/mine-bake-audit';log=audit/'final11-diagnostic-sequence.log';deadline=time.monotonic()+3600
while 'CS_FINAL11_SOURCE_AOV_AND_POINT_DIAGNOSTICS_READY' not in log.read_text(errors='replace'):
 if 'Traceback' in log.read_text(errors='replace'):raise RuntimeError('Native diagnostics failed; source rerun deferred')
 if time.monotonic()>deadline:raise TimeoutError('Native diagnostics deadline')
 time.sleep(2)
old=Path('/tmp/cs-mine-aov-final11');rejected=Path('/tmp/cs-mine-aov-final11-rejected-zero-aov-attempt2');assert old.exists() and not rejected.exists();old.rename(rejected)
shutil.copyfile(audit/'cs-mine-aov-final11.py.log',audit/'final11-diagnostic-failures/cs-mine-aov-final11.py.log.zero-aov-attempt2')
with (audit/'cs-mine-aov-final11-fixed.py.log').open('w') as out:
 subprocess.run(['/home/agent/.local/bin/blender','--background',str(root/'runtime/out/spawn-export-source/combined-runtime-source.blend'),'--disable-autoexec','--python-exit-code','1','--python','/tmp/cs-mine-aov-final11.py'],cwd=root,stdout=out,stderr=subprocess.STDOUT,check=True)
print('CS_SOURCE_AOV_FIXED_CHANNELS_VALIDATED',flush=True)
