from pathlib import Path
import shutil,subprocess
root=Path('/workspace/critical-shift-spawn-runtime');editor=root/'runtime/unity/Assets/CriticalShift/Bootstrap/Player/Editor';features=root/'runtime/unity/Assets/CriticalShift/Features/Player';helper=editor/'CsMineSoftRadiusFinal12.cs';shader=features/'CsMineSoftRadiusFinal12.shader'
code=Path('/tmp/cs-mine-radius-corrected-final11.cs.txt').read_text().replace('CsMineRadiusCorrectedFinal11','CsMineSoftRadiusFinal12').replace('/tmp/cs-mine-radius-corrected-final11/','/tmp/cs-mine-soft-radius-control-final12/').replace('MineRadiusCorrectedFinal11','MineSoftRadiusFinal12')
# Inspect actual extracted shape in the unchanged delegate diagnostic. Crucial
# difference: soft shadow mode must be restored before the finite emitter bake.
code=code.replace('point.cookie=Cookie(.12f,1,true);point.shapeRadius=.12f;point.intensity=280/(4*Mathf.PI*Mathf.PI);','point.cookie=Cookie(.12f,1,true);point.shapeRadius=.12f;point.shadows=LightShadows.Soft;point.shadowNearPlane=.01f;point.intensity=280/(4*Mathf.PI*Mathf.PI);')
code=code.replace('new[]{.06f,.12f,.24f})\n   {','new[]{.06f,.12f,.24f,1f,2f})\n   {')
code=code.replace('CS_NATIVE_PHYSICAL_POINT_CONTROL_OK','CS_NATIVE_SOFT_RADIUS_CONTROL_OK')
Path('/tmp/cs-mine-soft-radius-control-final12.cs.txt').write_text(code)
shaderCode=(features/'BlenderSurface.shader').read_text().replace('Shader "CriticalShift/BlenderSurface"','Shader "CriticalShift/DiagnosticPhysicalPoint"');Path('/tmp/cs-mine-soft-radius-control-final12.shader').write_text(shaderCode)
assert not helper.exists() and not shader.exists();helper.write_text(code);shader.write_text(shaderCode)
try:subprocess.run(['xvfb-run','-a','-s','-screen 0 1440x810x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(root/'runtime/unity'),'-executeMethod','CsMineSoftRadiusFinal12.Render','-logFile',str(root/'runtime/out/mine-bake-audit/soft-radius-control-final12.native.log')],cwd=root,check=True)
finally:
 for p in [helper,shader]:p.unlink(missing_ok=True);Path(str(p)+'.meta').unlink(missing_ok=True)
