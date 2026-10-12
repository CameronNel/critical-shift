from pathlib import Path
import time,subprocess,shutil,json,hashlib,os
root=Path('/workspace/critical-shift-spawn-runtime');audit=root/'runtime/out/mine-bake-audit';project=root/'runtime/unity';editor='/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity';blender='/home/agent/.local/bin/blender';seq=audit/'final10-sequence.log'
deadline=time.monotonic()+7200
while True:
 text=seq.read_text(errors='replace')
 if 'CS_FINAL10_NATIVE_IMAGES_AND_TESTS_READY_FOR_STRICT_REVIEW' in text:break
 if 'Traceback' in text:raise RuntimeError('Final10 failed, diagnostics not run')
 if time.monotonic()>deadline:raise TimeoutError('Final10 diagnostics dependency timeout')
 time.sleep(2)
if (project/'Temp/UnityLockfile').exists():raise RuntimeError('Current native editor remains open')
subprocess.run(['python','/tmp/cs-mine-hdr-independent-final10.py'],cwd=root,check=True)
archive=root/'runtime/validation/mine-bake-20261011/fresh-export-final10';capture=archive/'native-final10';capture.mkdir(exist_ok=True)
for folder in ['unity-source-wood-final10','unity-spawn-source-wood-final10','comparison-source-wood-final10']:
 shutil.copytree(audit/folder,capture/folder,dirs_exist_ok=True)
for name in ['native-playmode-source-wood-final10.xml','native-playmode-source-wood-final10.log','native-mine-render-source-wood-final10.log','native-bake-source-wood-final10.log','independent-hdr-source-wood-final10.json','spawn-regression-source-wood-final10.json','comparisons-source-wood-final10.json','final10-sequence.log']:
 p=audit/name
 if p.exists():shutil.copyfile(p,capture/name)
shutil.copyfile(project/'Assets/CriticalShift/Generated/Spawn/prepared-scene.json',capture/'prepared-scene.json')
print('CS_FINAL10_NATIVE_EVIDENCE_ARCHIVED; reviewer visual rejection pending; no Player or98 claim',flush=True)
source=root/'runtime/out/spawn-export-source/combined-runtime-source.blend'
for script in ['cs-mine-aov-final11.py','cs-mine-point-control-final11.py']:
 with (audit/(script+'.log')).open('w') as log:
  subprocess.run([blender,'--background',str(source),'--disable-autoexec','--python-exit-code','1','--python','/tmp/'+script],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
 marker='CS_SOURCE_AOV_DIAGNOSTIC_OK' if 'aov' in script else 'CS_BLENDER_POINT_CONTROL_OK'
 if marker not in (audit/(script+'.log')).read_text(errors='replace'):raise RuntimeError('Missing Blender completion marker: '+script)
 print('CS_BLENDER_DIAGNOSTIC_DONE',script,flush=True)
editorfolder=project/'Assets/CriticalShift/Bootstrap/Player/Editor'
shaderfile=editorfolder/'CsMineSourceAovFinal11.shader';csfile=editorfolder/'CsMineAovFinal11.cs'
for helper,method,shader in [('cs-mine-aov-native-final11.cs.txt','CsMineAovFinal11.Render',True),('cs-mine-point-control-final11.cs.txt','CsMinePointControlFinal11.Render',False)]:
 if csfile.exists() or shaderfile.exists():raise RuntimeError('Diagnostic helpers already exist')
 try:
  shutil.copyfile('/tmp/'+helper,csfile)
  if shader:shutil.copyfile('/tmp/cs-mine-aov-final11.shader',shaderfile)
  with (audit/(helper+'.log')).open('w') as log:
   subprocess.run(['xvfb-run','-a','-s','-screen 0 640x360x24',editor,'-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod',method,'-logFile',str(audit/(helper+'.native.log'))],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
  print('CS_NATIVE_DIAGNOSTIC_DONE',method,flush=True)
 finally:
  for p in [csfile,shaderfile,csfile.with_suffix('.cs.meta'),shaderfile.with_suffix('.shader.meta')]:p.unlink(missing_ok=True)
print('CS_FINAL11_SOURCE_AOV_AND_POINT_DIAGNOSTICS_READY; source/assembly files unchanged, no visual acceptance',flush=True)
