from pathlib import Path
import subprocess,shutil
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit'
source=Path('/tmp/cs-mine-point-control-final11.cs.txt').read_text()
source=source.replace('CsMinePointControlFinal11','CsMineTransportControlFinal11').replace('/tmp/cs-mine-point-native-final11/','/tmp/cs-mine-transport-native-final11/').replace('MinePointRadiometryFinal11','MineTransportRadiometryFinal11')
source=source.replace('using UnityEngine.Rendering;','using UnityEngine.Rendering;using GiMapping=UnityEngine.Experimental.GlobalIllumination.Lightmapping;using GiFalloff=UnityEngine.Experimental.GlobalIllumination.FalloffType;')
source=source.replace('try\n  {','var previousGi=GiMapping.GetDelegate();\n  try\n  {')
start=source.index('   foreach(float range')
end=source.index('   Debug.Log("CS_NATIVE_POINT_CONTROL_OK')
source=source[:start]+'''   Debug.Log("CS_GI_FALLOFF_ENUMS "+string.Join(",",Enum.GetNames(typeof(GiFalloff))));
   GiMapping.SetDelegate((requests,output)=>{previousGi(requests,output);for(int i=0;i<requests.Length;i++){if(requests[i]==point){var data=output[i];Debug.Log("CS_GI_BEFORE "+data.falloff+" direct="+data.color.intensity+" indirect="+data.indirectColor.intensity);data.falloff=GiFalloff.InverseSquared;output[i]=data;}}});
   var settings=new LightingSettings {bakedGI=true,realtimeGI=false,lightmapper=LightingSettings.Lightmapper.ProgressiveCPU,lightmapResolution=64,lightmapMaxSize=256,lightmapPadding=4,directSampleCount=256,indirectSampleCount=16,environmentSampleCount=128,maxBounces=1,lightmapCompression=LightmapCompression.None};AssetDatabase.CreateAsset(settings,folder+"/Lighting.lighting");Lightmapping.lightingSettings=settings;point.range=12;point.lightmapBakeType=LightmapBakeType.Baked;point.intensity=100/(4*Mathf.PI*Mathf.PI);
   foreach(int distance in new[]{1,2,4})
   {point.transform.position=new Vector3(0,0,-distance);EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),folder+"/Scene.unity");if(!Lightmapping.Bake() || renderer.lightmapIndex<0 || renderer.lightmapIndex>=LightmapSettings.lightmaps.Length)throw new Exception("Inverse-square point control bake failed");Save("Native-baked-inverseSquared-distance"+distance);Lightmapping.Clear();}
   GiMapping.SetDelegate(previousGi);point.enabled=false;
   foreach(var world in new[]{new Color(1,1,1),new Color(.045f,.055f,.09f)})
   {string label=world.r>.5 ? "white" : "assembly";RenderSettings.ambientIntensity=1;RenderSettings.ambientLight=world.gamma;GameObjectUtility.SetStaticEditorFlags(quad,0);renderer.receiveGI=ReceiveGI.LightProbes;Save("Native-world-runtime-"+label);GameObjectUtility.SetStaticEditorFlags(quad,StaticEditorFlags.ContributeGI);renderer.receiveGI=ReceiveGI.Lightmaps;EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(),folder+"/Scene.unity");if(!Lightmapping.Bake())throw new Exception("Ambient control bake failed");Save("Native-world-baked-"+label);Lightmapping.Clear();}
''' +source[end:]
source=source.replace('CS_NATIVE_POINT_CONTROL_OK','CS_NATIVE_TRANSPORT_CONTROL_OK').replace('finally{EditorSceneManager','finally{GiMapping.SetDelegate(previousGi);EditorSceneManager')
Path('/tmp/cs-mine-transport-control-final11.cs.txt').write_text(source)
world=Path('/tmp/cs-mine-point-control-final11.py').read_text();world=world.replace('/tmp/cs-mine-point-control-final11','/tmp/cs-mine-world-control-final11')
world=world[:world.index('for distance in (1,2,4):')]+'''light.data.energy=0
for label,color in [('white',(1,1,1)),('assembly',(.045,.055,.09))]:
 scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(*color,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=1;scene.render.filepath=str(out/('Blender-world-'+label+'.exr'));bpy.ops.render.render(write_still=True)
(out/'source.json').write_text(json.dumps({'albedoLinear':.18,'BSDF':'Diffuse roughness0','worldColors':{'white':[1,1,1],'assembly':[.045,.055,.09]},'worldStrength':1,'pointPower':0,'samples':128},indent=2)+'\\n');print('CS_BLENDER_WORLD_CONTROL_OK',flush=True)
'''
Path('/tmp/cs-mine-world-control-final11.py').write_text(world)
with (audit/'cs-mine-world-control-final11.log').open('w') as log:subprocess.run(['/home/agent/.local/bin/blender','--background','--factory-startup','--python-exit-code','1','--python','/tmp/cs-mine-world-control-final11.py'],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
csfile=project/'Assets/CriticalShift/Bootstrap/Player/Editor/CsMineTransportControlFinal11.cs'
if csfile.exists() or (project/'Temp/UnityLockfile').exists():raise RuntimeError('Busy editor or existing helper')
try:
 shutil.copyfile('/tmp/cs-mine-transport-control-final11.cs.txt',csfile)
 with (audit/'cs-mine-transport-control-final11.wrapper.log').open('w') as log:subprocess.run(['xvfb-run','-a','-s','-screen 0 640x360x24','/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity','-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod','CsMineTransportControlFinal11.Render','-logFile',str(audit/'cs-mine-transport-control-final11.native.log')],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
 print('CS_NATIVE_TRANSPORT_AND_WORLD_CONTROLS_DONE',flush=True)
finally:
 csfile.unlink(missing_ok=True);csfile.with_suffix('.cs.meta').unlink(missing_ok=True)
