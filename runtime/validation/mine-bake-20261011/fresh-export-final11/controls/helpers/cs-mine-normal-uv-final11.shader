Shader "CriticalShift/DiagnosticNormalUV" { Properties { _BumpMap("Source normal",2D)="bump"{} _CsMask("Mask",Float)=1 _CsDiagnostic("Mode",Float)=1 } SubShader { Tags {"RenderType"="Opaque"} Cull Off Pass { CGPROGRAM
#pragma target 3.0
#pragma vertex vert
#pragma fragment frag
#include "UnityCG.cginc"
sampler2D _BumpMap;float4 _BumpMap_ST,_BumpMap_TexelSize;float _CsMask,_CsDiagnostic;struct Input{float4 vertex:POSITION;float2 uv:TEXCOORD0;};struct Output{float4 pos:SV_POSITION;float2 uv:TEXCOORD0;};Output vert(Input v){Output o;o.pos=UnityObjectToClipPos(v.vertex);o.uv=TRANSFORM_TEX(v.uv,_BumpMap);return o;}float4 frag(Output i):SV_Target{if(_CsMask<.5)return float4(0,0,0,0);float2 dx=ddx(i.uv)*_BumpMap_TexelSize.zw,dy=ddy(i.uv)*_BumpMap_TexelSize.zw;if(_CsDiagnostic==1)return float4(i.uv,.5*log2(max(max(dot(dx,dx),dot(dy,dy)),1e-12)),1);return tex2D(_BumpMap,i.uv);}
ENDCG } } }