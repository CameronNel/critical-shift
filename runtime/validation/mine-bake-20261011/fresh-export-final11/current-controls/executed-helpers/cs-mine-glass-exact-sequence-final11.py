from pathlib import Path
import subprocess,shutil,time,json,os
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';folder=project/'Assets/CriticalShift/Bootstrap/Player/Editor';editor='/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity';state=audit/'glass-exact-sequence-final11-state.json'
state.write_text(json.dumps({'state':'Waiting','pid':os.getpid()}));deadline=time.monotonic()+21600
# The full diffuse sequence must have exited, whether it passes or rejects a
# guard. Glass is an independent bounded diagnostic, never a concurrent bake.
while Path('/proc/146455').exists() and Path('/proc/146455/stat').read_text().split(') ',1)[1].split()[0]!='Z':
 if time.monotonic()>deadline:raise TimeoutError('Diffuse sequence still active; glass not run')
 time.sleep(2)
if 'CS_FINAL11_ACTUAL_CONFIGURE_AND_SCOPE_CHECKS_READY' not in (audit/'native-after-export-final11-wrapper.log').read_text():raise RuntimeError('Current native import/preflight incomplete; glass not run')
if (project/'Temp/UnityLockfile').exists():raise RuntimeError('Native editor busy; glass not run')
state.write_text(json.dumps({'state':'Running','pid':os.getpid()}))
with (audit/'cs-mine-glass-exact-final11.source.log').open('w') as log:subprocess.run(['/home/agent/.local/bin/blender','--background',str(root/'runtime/out/spawn-export-source/combined-runtime-source.blend'),'--disable-autoexec','--python-exit-code','1','--python','/tmp/cs-mine-glass-exact-source-final11.py'],stdout=log,stderr=subprocess.STDOUT,check=True)
cs=folder/'CsMineGlassExactFinal11.cs';shader=folder/'CsMineGlassExactFinal11.shader'
if cs.exists() or shader.exists():raise RuntimeError('Glass helper already exists')
try:
 shutil.copyfile('/tmp/cs-mine-glass-exact-native-final11.cs.txt',cs);shutil.copyfile('/tmp/cs-mine-glass-exact-final11.shader',shader)
 with (audit/'cs-mine-glass-exact-final11.wrapper.log').open('w') as log:subprocess.run(['xvfb-run','-a','-s','-screen 0 640x360x24',editor,'-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CsMineGlassExactFinal11.Render','-logFile',str(audit/'cs-mine-glass-exact-final11.native.log')],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
 state.write_text(json.dumps({'state':'Finished','exitCode':0}));print('CS_FINAL11_EXACT_GLASS_REFLECTION_AND_COLOUR_CONTROLS_READY_FOR_REVIEW',flush=True)
finally:
 for p in [cs,shader,cs.with_suffix('.cs.meta'),shader.with_suffix('.shader.meta')]:p.unlink(missing_ok=True)
