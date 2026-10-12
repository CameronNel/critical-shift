from pathlib import Path
import subprocess,shutil
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';folder=project/'Assets/CriticalShift/Bootstrap/Player/Editor';editor='/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity'
with (audit/'cs-mine-duct-inspect-final11.log').open('w') as log:subprocess.run(['/home/agent/.local/bin/blender','--background',str(root/'runtime/out/spawn-export-source/combined-runtime-source.blend'),'--disable-autoexec','--python-exit-code','1','--python','/tmp/cs-mine-duct-inspect-final11.py'],stdout=log,stderr=subprocess.STDOUT,check=True)
# Exercise actual production shader with corrected radius in the same near/far controls.
s=Path('/tmp/cs-mine-physical-point-native-final11.cs.txt').read_text().replace('CsMinePhysicalPointFinal11','CsMineRadiusCorrectedFinal11').replace('MinePhysicalPointFinal11','MineRadiusCorrectedFinal11').replace('/tmp/cs-mine-physical-point-native-final11/','/tmp/cs-mine-radius-corrected-final11/').replace('CriticalShift/DiagnosticPhysicalPoint','CriticalShift/BlenderSurface')
s=s.replace('foreach(int distance in new[]{1,2,4})','point.cookie=Cookie(.12f,1,true);point.shapeRadius=.12f;point.intensity=280/(4*Mathf.PI*Mathf.PI);\n   foreach(float distance in new[]{.06f,.12f,.24f})').replace('Native-baked-noRange-tagged-cookie-distance','Native-baked-radius012-power280-distance')
Path('/tmp/cs-mine-radius-corrected-final11.cs.txt').write_text(s)
csfile=folder/'CsMineRadiusCorrectedFinal11.cs'
if (project/'Temp/UnityLockfile').exists() or csfile.exists():raise RuntimeError('Busy editor')
try:
 shutil.copyfile('/tmp/cs-mine-radius-corrected-final11.cs.txt',csfile)
 with (audit/'cs-mine-radius-corrected-final11.wrapper.log').open('w') as log:subprocess.run(['xvfb-run','-a','-s','-screen 0 640x360x24',editor,'-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CsMineRadiusCorrectedFinal11.Render','-logFile',str(audit/'cs-mine-radius-corrected-final11.native.log')],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
 print('CS_RADIUS_CORRECTED_DONE',flush=True)
finally:
 for p in [csfile,csfile.with_suffix('.cs.meta')]:p.unlink(missing_ok=True)
