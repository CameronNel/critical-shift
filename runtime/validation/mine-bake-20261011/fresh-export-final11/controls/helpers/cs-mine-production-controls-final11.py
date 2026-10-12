from pathlib import Path
import subprocess,shutil
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';editor='/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity';blender='/home/agent/.local/bin/blender';folder=project/'Assets/CriticalShift/Bootstrap/Player/Editor'
source=Path('/tmp/cs-mine-point-control-final11.py').read_text().replace('/tmp/cs-mine-point-control-final11','/tmp/cs-mine-near-source-final11')
source=source.replace('for distance in (1,2,4):','light.data.energy=280;light.data.shadow_soft_size=.12\nfor distance in (.06,.12,.24):').replace('Blender-100W-distance','Blender-radius012-power280-distance').replace("'powerWatts':100,'sourceRadius':.001,'distancesMetres':[1,2,4]", "'powerWatts':280,'sourceRadius':.12,'distancesMetres':[.06,.12,.24]").replace("for d in (1,2,4)","for d in (.06,.12,.24)").replace('100/(4*math.pi**2*d*d)','280/(4*math.pi**2*max(d*d,.12*.12))')
Path('/tmp/cs-mine-near-source-final11.py').write_text(source)
with (audit/'cs-mine-near-source-final11.log').open('w') as log:subprocess.run([blender,'--background','--factory-startup','--python-exit-code','1','--python','/tmp/cs-mine-near-source-final11.py'],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
geometry=Path('/tmp/cs-mine-aov-linked-context-final11.py').read_text().replace('/tmp/cs-mine-aov-linked-context-final11','/tmp/cs-mine-geometric-source-final11')
start=geometry.index(' normal=nt.nodes.new');end=geometry.index(' diagnostic_one=',start)
geometry=geometry[:start]+''' normal=nt.nodes.new('ShaderNodeOutputAOV');normal.aov_name='ShadingNormal'
 for link in list(bsdf.inputs['Normal'].links):nt.links.remove(link)
 geometric=nt.nodes.new('ShaderNodeNewGeometry');scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs['Scale'].default_value=.5;nt.links.new(geometric.outputs['Normal'],scale.inputs[0]);add=nt.nodes.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=(.5,.5,.5);nt.links.new(scale.outputs[0],add.inputs[0]);nt.links.new(add.outputs[0],normal.inputs['Color'])
''' +geometry[end:]
geometry=geometry.replace("for name,(eye,target,lens) in views.items():", "for name,(eye,target,lens) in views.items():\n if name!='R39_02_TUNNEL':continue")
Path('/tmp/cs-mine-geometric-source-final11.py').write_text(geometry)
with (audit/'cs-mine-geometric-source-final11.log').open('w') as log:subprocess.run([blender,'--background',str(root/'runtime/out/spawn-export-source/combined-runtime-source.blend'),'--disable-autoexec','--python-exit-code','1','--python','/tmp/cs-mine-geometric-source-final11.py'],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
control=Path('/tmp/cs-mine-physical-point-native-final11.cs.txt').read_text().replace('CsMinePhysicalPointFinal11','CsMineProductionPointFinal11').replace('/tmp/cs-mine-physical-point-native-final11/','/tmp/cs-mine-production-point-native-final11/').replace('MinePhysicalPointFinal11','MineProductionPointFinal11').replace('CriticalShift/DiagnosticPhysicalPoint','CriticalShift/BlenderSurface')
control=control.replace('foreach(int distance in new[]{1,2,4})','foreach(float distance in new[]{1f,2f,4f,12.1f,16f})')
start=control.index('   var taggedCookie=Cookie(')
control=control[:start]+'''   foreach(string family in new[]{"BlenderSurface","BlenderHood","BlenderGlass","BlenderDecal","BlenderThinVisor"}){material.shader=Shader.Find("CriticalShift/"+family);if(material.shader==null)throw new Exception("Missing actual shader "+family);point.cookie=Cookie(.12f,1,true);point.intensity=100/(4*Mathf.PI*Mathf.PI);point.range=12;point.lightmapBakeType=LightmapBakeType.Realtime;foreach(int distance in new[]{1,2,4}){point.transform.position=new Vector3(0,0,-distance);Save("ActualShader-"+family+"-distance"+distance);}}
   material.shader=Shader.Find("CriticalShift/BlenderSurface");
''' +control[start:]
Path('/tmp/cs-mine-production-point-native-final11.cs.txt').write_text(control)
normal=Path('/tmp/cs-mine-normal-native-final11.cs.txt').read_text().replace('CsMineNormalFinal11','CsMineGeometricFinal11').replace('/tmp/cs-mine-normal-native-final11/','/tmp/cs-mine-geometric-native-final11/').replace('material.shader=supported ? shader : Shader.Find("Unlit/Color");','material.shader=supported ? shader : Shader.Find("Unlit/Color");').replace('if(!supported)material.color=Color.black;', 'if(!supported)material.color=Color.black;else {material.DisableKeyword("_NORMALMAP");material.DisableKeyword("_SOURCE_WOOD");}')
# Only tunnel is needed for the geometric baseline; actual material flags are explicitly cleared.
normal=normal.replace('  foreach(var view in views)\n  {','  foreach(var view in views)\n  {\n   if(view.name!="R39_02_TUNNEL")continue;')
Path('/tmp/cs-mine-geometric-native-final11.cs.txt').write_text(normal)
for c,sh,method in [('cs-mine-production-point-native-final11.cs.txt',None,'CsMineProductionPointFinal11.Render'),('cs-mine-geometric-native-final11.cs.txt','cs-mine-normal-corrected-final11.shader','CsMineGeometricFinal11.Render')]:
 csfile=folder/'CsMineProductionDiagnosticFinal11.cs';shaderfile=folder/'CsMineProductionDiagnosticFinal11.shader'
 if (project/'Temp/UnityLockfile').exists() or csfile.exists() or shaderfile.exists():raise RuntimeError('Busy editor')
 try:
  shutil.copyfile('/tmp/'+c,csfile)
  if sh:shutil.copyfile('/tmp/'+sh,shaderfile)
  with (audit/(method+'.wrapper.log')).open('w') as log:subprocess.run(['xvfb-run','-a','-s','-screen 0 640x360x24',editor,'-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod',method,'-logFile',str(audit/(method+'.native.log'))],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
  print('CS_PRODUCTION_CONTROL_DONE',method,flush=True)
 finally:
  for p in [csfile,shaderfile,csfile.with_suffix('.cs.meta'),shaderfile.with_suffix('.shader.meta')]:p.unlink(missing_ok=True)
