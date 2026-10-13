from pathlib import Path
import subprocess,shutil
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';editor='/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity';folder=project/'Assets/CriticalShift/Bootstrap/Player/Editor'
normal=(project/'Assets/CriticalShift/Features/Player/BlenderSurface.shader').read_text().replace('CriticalShift/BlenderSurface','CriticalShift/DiagnosticProductionNormal').replace('surf StandardSpecular','surf CsDiagnosticNormal')
normal=normal.replace('        sampler2D _MainTex,','        #include "UnityPBSLighting.cginc"\n        half4 LightingCsDiagnosticNormal(SurfaceOutputStandardSpecular s,half3 viewDir,UnityGI gi) { return half4(s.Normal*.5+.5,1); }\n        void LightingCsDiagnosticNormal_GI(SurfaceOutputStandardSpecular s,UnityGIInput data,inout UnityGI gi) {}\n        sampler2D _MainTex,')
Path('/tmp/cs-mine-normal-final11.shader').write_text(normal)
cs=Path('/tmp/cs-mine-aov-native-final11.cs.txt').read_text().replace('CsMineAovFinal11','CsMineNormalFinal11').replace('/tmp/cs-mine-aov-native-final11/','/tmp/cs-mine-normal-native-final11/').replace('CriticalShift/DiagnosticSourceAOV','CriticalShift/DiagnosticProductionNormal').replace('foreach(int mode in new[]{1,2,3})','foreach(int mode in new[]{4})').replace('(mode==1 ? "BaseColor":mode==2 ? "Roughness":"SupportedMask")','"ProductionNormal"')
# unsupported surfaces must remain opaque black, preserving visibility occlusion.
cs=cs.replace('material.shader=shader;material.CopyPropertiesFromMaterial(original);material.SetFloat("_CsMask",supported ? 1 : 0);','material.shader=supported ? shader : Shader.Find("Unlit/Color");material.CopyPropertiesFromMaterial(original);if(!supported)material.color=Color.black;')
cs=cs.replace('CS_MINE_DIAGNOSTIC_AOV_OK','CS_MINE_PRODUCTION_NORMAL_AOV_OK')
Path('/tmp/cs-mine-normal-native-final11.cs.txt').write_text(cs)
control=Path('/tmp/cs-mine-transport-control-final11.cs.txt').read_text().replace('CsMineTransportControlFinal11','CsMinePhysicalPointFinal11').replace('/tmp/cs-mine-transport-native-final11/','/tmp/cs-mine-physical-point-native-final11/').replace('MineTransportRadiometryFinal11','MinePhysicalPointFinal11').replace('CriticalShift/BlenderSurface','CriticalShift/DiagnosticPhysicalPoint')
control=control.replace('GiFalloff.InverseSquared;','GiFalloff.InverseSquaredNoRangeAttenuation;')
start=control.index('   Debug.Log("CS_GI_FALLOFF_ENUMS')
control=control[:start]+'''   Cubemap Cookie(float radius,float alpha,bool tagged){var cube=new Cubemap(1,TextureFormat.RGBAHalf,false);foreach(CubemapFace face in new[]{CubemapFace.PositiveX,CubemapFace.NegativeX,CubemapFace.PositiveY,CubemapFace.NegativeY,CubemapFace.PositiveZ,CubemapFace.NegativeZ})cube.SetPixels(new[]{tagged ? new Color(.9375f,.03125f,radius,alpha) : new Color(1,1,1,alpha)},face);cube.Apply(false,false);return cube;}
   var taggedCookie=Cookie(.001f,1,true);AssetDatabase.CreateAsset(taggedCookie,folder+"/IdentityCookie.asset");point.cookie=taggedCookie;point.lightmapBakeType=LightmapBakeType.Realtime;point.intensity=100/(4*Mathf.PI*Mathf.PI);point.range=12;
   foreach(float distance in new[]{1f,2f,4f,11.9f,12.1f}){point.transform.position=new Vector3(0,0,-distance);Save("Physical-direct-range12-distance"+distance);}
   point.range=128;foreach(float distance in new[]{127.9f,128.1f}){point.transform.position=new Vector3(0,0,-distance);Save("Physical-direct-range128-distance"+distance);}
   point.range=12;point.transform.position=new Vector3(0,0,-2);point.cookie=Cookie(.001f,.5f,true);Save("Physical-half-cookie-distance2");point.cookie=Cookie(.001f,.25f,false);point.intensity=1;Save("Legacy-white-cookie-quarter-distance2");point.cookie=null;Save("Legacy-no-cookie-distance2");point.cookie=Cookie(.12f,1,true);point.intensity=280/(4*Mathf.PI*Mathf.PI);foreach(float distance in new[]{.06f,.12f,.24f}){point.transform.position=new Vector3(0,0,-distance);Save("Physical-radius012-power280-distance"+distance);}
   point.cookie=taggedCookie;point.range=12;point.intensity=100/(4*Mathf.PI*Mathf.PI);point.transform.position=new Vector3(0,0,-2);point.shadows=LightShadows.Hard;QualitySettings.shadows=ShadowQuality.All;QualitySettings.shadowDistance=100;var blocker=GameObject.CreatePrimitive(PrimitiveType.Cube);blocker.transform.position=new Vector3(0,0,-1);blocker.transform.localScale=new Vector3(.3f,.3f,.1f);Save("Physical-shadow-blocked-distance2");UnityEngine.Object.DestroyImmediate(blocker);point.shadows=LightShadows.None;point.cookie=taggedCookie;
''' +control[start:]
control=control.replace('if(requests[i]==point){var data=output[i];','if(requests[i]==point){var data=output[i];foreach(var field in data.GetType().GetFields())Debug.Log("CS_LIGHTDATA_FIELD "+field.Name+"="+field.GetValue(data));')
control=control.replace('Native-baked-inverseSquared-distance','Native-baked-noRange-tagged-cookie-distance')
start=control.index('   GiMapping.SetDelegate(previousGi);point.enabled=false;');end=control.index('   Debug.Log("CS_NATIVE_TRANSPORT_CONTROL_OK',start);control=control[:start]+control[end:]
control=control.replace('CS_NATIVE_TRANSPORT_CONTROL_OK','CS_NATIVE_PHYSICAL_POINT_CONTROL_OK')
Path('/tmp/cs-mine-physical-point-native-final11.cs.txt').write_text(control)
physical='''Shader "CriticalShift/DiagnosticPhysicalPoint" { Properties { _Color("Albedo",Color)=(.461,.461,.461,1) _DielectricSpecular("F0",Float)=0 _Metallic("Metallic",Float)=0 _Glossiness("Smoothness",Float)=.5 } SubShader { Tags {"RenderType"="Opaque"} CGPROGRAM
#pragma target 3.0
#pragma surface surf StandardSpecular fullforwardshadows addshadow
#include "CsMinePhysicalPointFinal11.cginc"
fixed4 _Color;struct Input{float2 uv_MainTex;};void surf(Input i,inout SurfaceOutputStandardSpecular o){o.Albedo=_Color.rgb;o.Specular=0;o.Smoothness=0;o.Alpha=1;}
ENDCG } }'''
Path('/tmp/cs-mine-physical-point-final11.shader').write_text(physical)
for c,sh,method,include in [('cs-mine-normal-native-final11.cs.txt','cs-mine-normal-final11.shader','CsMineNormalFinal11.Render',False),('cs-mine-physical-point-native-final11.cs.txt','cs-mine-physical-point-final11.shader','CsMinePhysicalPointFinal11.Render',True)]:
 csfile=folder/'CsMineDiagnosticFinal11.cs';shaderfile=folder/'CsMineDiagnosticFinal11.shader';inc=folder/'CsMinePhysicalPointFinal11.cginc'
 if (project/'Temp/UnityLockfile').exists() or any(p.exists() for p in [csfile,shaderfile,inc]):raise RuntimeError('Busy editor or existing helper')
 try:
  shutil.copyfile('/tmp/'+c,csfile);shutil.copyfile('/tmp/'+sh,shaderfile)
  if include:shutil.copyfile('/tmp/cs-mine-physical-point-final11.cginc',inc)
  with (audit/(c+'.wrapper.log')).open('w') as log:subprocess.run(['xvfb-run','-a','-s','-screen 0 640x360x24',editor,'-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod',method,'-logFile',str(audit/(c+'.native.log'))],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
  print('CS_DIAGNOSTIC_DONE',method,flush=True)
 finally:
  for p in [csfile,shaderfile,inc,csfile.with_suffix('.cs.meta'),shaderfile.with_suffix('.shader.meta'),inc.with_suffix('.cginc.meta')]:p.unlink(missing_ok=True)
