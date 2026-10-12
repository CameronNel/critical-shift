from pathlib import Path
import subprocess,shutil
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';folder=project/'Assets/CriticalShift/Bootstrap/Player/Editor';editor='/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity'
old=Path('/tmp/cs-mine-normal-native-final11');rejected=old.with_name(old.name+'-rejected-additive-offset')
if rejected.exists():raise RuntimeError('Rejected normal AOV archive exists')
old.rename(rejected)
normal=Path('/tmp/cs-mine-normal-final11.shader').read_text().replace('surf CsDiagnosticNormal fullforwardshadows','surf CsDiagnosticNormal noforwardadd fullforwardshadows').replace('            output.Normal=normal*', '            output.Emission=0;\n            output.Normal=normal*')
# Emission is assigned after Normal in original surf; clear it at the actual function end.
normal=normal.replace('        }\n        ENDCG','            output.Emission=0;\n        }\n        ENDCG')
Path('/tmp/cs-mine-normal-corrected-final11.shader').write_text(normal)
control=Path('/tmp/cs-mine-transport-control-final11.cs.txt').read_text().replace('CsMineTransportControlFinal11','CsMineDirectionalityFinal11').replace('/tmp/cs-mine-transport-native-final11/','/tmp/cs-mine-directionality-native-final11/').replace('MineTransportRadiometryFinal11','MineDirectionalityFinal11')
start=control.index('   Debug.Log("CS_GI_FALLOFF_ENUMS');end=control.index('   Debug.Log("CS_NATIVE_TRANSPORT_CONTROL_OK',start)
control=control[:start]+'''   var normal=new Texture2D(64,64,TextureFormat.RGBA32,false,true);for(int y=0;y<64;y++)for(int x=0;x<64;x++)normal.SetPixel(x,y,new Color(x%8<4 ? .146447f:.853553f,.5f,.853553f,1));normal.Apply();material.SetTexture("_BumpMap",normal);material.EnableKeyword("_NORMALMAP");AssetDatabase.CreateAsset(normal,folder+"/CheckerNormal.asset");
   point.range=12;point.transform.position=new Vector3(1,0,-2);point.intensity=1;point.lightmapBakeType=LightmapBakeType.Realtime;Save("Native-normal-realtime");
   var settings=new LightingSettings {bakedGI=true,realtimeGI=false,lightmapper=LightingSettings.Lightmapper.ProgressiveCPU,lightmapResolution=64,lightmapMaxSize=256,lightmapPadding=4,directSampleCount=128,indirectSampleCount=16,environmentSampleCount=16,maxBounces=1,lightmapCompression=LightmapCompression.None};AssetDatabase.CreateAsset(settings,folder+"/Lighting.lighting");Lightmapping.lightingSettings=settings;point.lightmapBakeType=LightmapBakeType.Baked;
   foreach(var mode in new[]{LightmapsMode.NonDirectional,LightmapsMode.CombinedDirectional}){settings.directionalityMode=mode;EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),folder+"/Scene.unity");if(!Lightmapping.Bake())throw new Exception("Directionality control failed");Debug.Log("CS_DIRECTIONALITY_MODE "+LightmapSettings.lightmapsMode);Save("Native-normal-baked-"+mode);material.DisableKeyword("_NORMALMAP");Save("Native-flat-baked-"+mode);material.EnableKeyword("_NORMALMAP");Lightmapping.Clear();}
''' +control[end:]
control=control.replace('CS_NATIVE_TRANSPORT_CONTROL_OK','CS_NATIVE_DIRECTIONALITY_CONTROL_OK');Path('/tmp/cs-mine-directionality-native-final11.cs.txt').write_text(control)
for c,sh,method in [('cs-mine-normal-native-final11.cs.txt','cs-mine-normal-corrected-final11.shader','CsMineNormalFinal11.Render'),('cs-mine-directionality-native-final11.cs.txt',None,'CsMineDirectionalityFinal11.Render')]:
 csfile=folder/'CsMineNormalDirectionalityFinal11.cs';shaderfile=folder/'CsMineNormalDirectionalityFinal11.shader'
 if (project/'Temp/UnityLockfile').exists() or csfile.exists() or shaderfile.exists():raise RuntimeError('Busy editor')
 try:
  shutil.copyfile('/tmp/'+c,csfile)
  if sh:shutil.copyfile('/tmp/'+sh,shaderfile)
  with (audit/(method+'.wrapper.log')).open('w') as log:subprocess.run(['xvfb-run','-a','-s','-screen 0 640x360x24',editor,'-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod',method,'-logFile',str(audit/(method+'.corrected.native.log'))],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
  print('CS_DIAGNOSTIC_DONE',method,flush=True)
 finally:
  for p in [csfile,shaderfile,csfile.with_suffix('.cs.meta'),shaderfile.with_suffix('.shader.meta')]:p.unlink(missing_ok=True)
