from pathlib import Path
import subprocess,shutil
root=Path('/workspace/critical-shift-spawn-runtime');project=root/'runtime/unity';audit=root/'runtime/out/mine-bake-audit';folder=project/'Assets/CriticalShift/Bootstrap/Player/Editor';editor='/home/agent/.local/share/critical-shift/toolchain/unity-6000.4.3f1/Editor/Unity'
shader='''Shader "CriticalShift/DiagnosticNormalUV" { Properties { _BumpMap("Source normal",2D)="bump"{} _CsMask("Mask",Float)=1 _CsDiagnostic("Mode",Float)=1 } SubShader { Tags {"RenderType"="Opaque"} Cull Off Pass { CGPROGRAM
#pragma target 3.0
#pragma vertex vert
#pragma fragment frag
#include "UnityCG.cginc"
sampler2D _BumpMap;float4 _BumpMap_ST,_BumpMap_TexelSize;float _CsMask,_CsDiagnostic;struct Input{float4 vertex:POSITION;float2 uv:TEXCOORD0;};struct Output{float4 pos:SV_POSITION;float2 uv:TEXCOORD0;};Output vert(Input v){Output o;o.pos=UnityObjectToClipPos(v.vertex);o.uv=TRANSFORM_TEX(v.uv,_BumpMap);return o;}float4 frag(Output i):SV_Target{if(_CsMask<.5)return float4(0,0,0,0);float2 dx=ddx(i.uv)*_BumpMap_TexelSize.zw,dy=ddy(i.uv)*_BumpMap_TexelSize.zw;if(_CsDiagnostic==1)return float4(i.uv,.5*log2(max(max(dot(dx,dx),dot(dy,dy)),1e-12)),1);return tex2D(_BumpMap,i.uv);}
ENDCG } } }'''
Path('/tmp/cs-mine-normal-uv-final11.shader').write_text(shader)
cs=Path('/tmp/cs-mine-aov-native-final11.cs.txt').read_text().replace('CsMineAovFinal11','CsMineNormalUvFinal11').replace('/tmp/cs-mine-aov-native-final11/','/tmp/cs-mine-normal-uv-native-final11/').replace('CriticalShift/DiagnosticSourceAOV','CriticalShift/DiagnosticNormalUV').replace('foreach(int mode in new[]{1,2,3})','foreach(int mode in new[]{1,2})').replace('(mode==1 ? "BaseColor":mode==2 ? "Roughness":"SupportedMask")','(mode==1 ? "NormalAtlasUV":"NormalAtlasSample")').replace('  foreach(var view in views)\n  {','  foreach(var view in views)\n  {\n   if(view.name!="R39_02_TUNNEL")continue;')
cs=cs.replace('bool supported=original.shader.name=="CriticalShift/BlenderSurface";', 'bool supported=original.shader.name=="CriticalShift/BlenderSurface" && original.IsKeywordEnabled("_NORMALMAP") && original.GetTexture("_BumpMap")!=null;')
Path('/tmp/cs-mine-normal-uv-native-final11.cs.txt').write_text(cs)
for c,sh,method in [('cs-mine-sun-caster-final11.cs.txt',None,'CsMineSunCasterFinal11.Render'),('cs-mine-normal-uv-native-final11.cs.txt','cs-mine-normal-uv-final11.shader','CsMineNormalUvFinal11.Render')]:
 csfile=folder/'CsMineAdditionalControlFinal11.cs';shaderfile=folder/'CsMineAdditionalControlFinal11.shader'
 if (project/'Temp/UnityLockfile').exists() or csfile.exists() or shaderfile.exists():raise RuntimeError('Busy editor')
 try:
  shutil.copyfile('/tmp/'+c,csfile)
  if sh:shutil.copyfile('/tmp/'+sh,shaderfile)
  with (audit/(method+'.wrapper.log')).open('w') as log:subprocess.run(['xvfb-run','-a','-s','-screen 0 640x360x24',editor,'-batchmode','-force-glcore','-quit','-projectPath',str(project),'-executeMethod',method,'-logFile',str(audit/(method+'.native.log'))],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
  print('CS_ADDITIONAL_CONTROL_DONE',method,flush=True)
 finally:
  for p in [csfile,shaderfile,csfile.with_suffix('.cs.meta'),shaderfile.with_suffix('.shader.meta')]:p.unlink(missing_ok=True)
