Shader "CriticalShift/DiagnosticSourceAOV"
{
 Properties
 {
  _Color ("Source multiplier", Color)=(1,1,1,1)
  _MainTex ("Source colour",2D)="white" {}
  _MetallicGlossMap ("Source numeric channels",2D)="white" {}
  _Glossiness ("Smoothness",Float)=.5
  _GlossMapScale ("Smoothness scale",Float)=1
  _SmoothnessFromMap ("Smoothness map weight",Float)=1
  _WoodDiffuse ("Authored wood colour",2D)="white" {}
  _WoodHigh ("Authored wood coefficient",2D)="white" {}
  _WoodSignal ("Source grain parameters",Vector)=(1,0,1,1)
  _WoodBump ("Source UV rotation",Vector)=(0,0,0,0)
  _WoodUV ("Source UV mapping",Vector)=(1,1,0,0)
  _CsDiagnostic ("Diagnostic mode",Float)=1
  _CsMask ("Supported source shader",Float)=1
 }
 SubShader
 {
  Tags {"RenderType"="Opaque"} Cull Off
  Pass
  {
   CGPROGRAM
   #pragma target 3.0
   #pragma vertex vert
   #pragma fragment frag
   #pragma shader_feature_local _SOURCE_WOOD
   #pragma shader_feature_local _METALLICGLOSSMAP
   #include "UnityCG.cginc"
   sampler2D _MainTex,_MetallicGlossMap,_WoodDiffuse,_WoodHigh;
   float4 _MainTex_ST,_WoodSignal,_WoodBump,_WoodUV;
   fixed4 _Color;
   float _CsDiagnostic,_CsMask;
   half _Glossiness,_GlossMapScale,_SmoothnessFromMap;
   struct Input {float4 vertex:POSITION;float2 uv:TEXCOORD0;float2 woodUV:TEXCOORD2;};
   struct Output {float4 position:SV_POSITION;float2 uv:TEXCOORD0;float2 woodUV:TEXCOORD1;};
   Output vert(Input v){Output o;o.position=UnityObjectToClipPos(v.vertex);o.uv=TRANSFORM_TEX(v.uv,_MainTex);o.woodUV=v.woodUV;return o;}
   float4 frag(Output input):SV_Target
   {
    if(_CsMask<.5)return float4(0,0,0,1);
    if(_CsDiagnostic==3)return float4(1,1,1,1);
    if(_CsDiagnostic==2)
    {
     half smoothness=_Glossiness;
     #if defined(_METALLICGLOSSMAP)
      half4 metal=tex2D(_MetallicGlossMap,input.uv);
      smoothness=lerp(_Glossiness,metal.a*_GlossMapScale,_SmoothnessFromMap);
     #endif
     return float4(1-smoothness,1-smoothness,1-smoothness,1);
    }
    fixed4 colour=tex2D(_MainTex,input.uv)*_Color;
    #if defined(_SOURCE_WOOD)
     float2 sourceUV=input.woodUV*_WoodUV.xy;
     float s,c;sincos(_WoodBump.z,s,c);
     sourceUV=float2(c*sourceUV.x-s*sourceUV.y,s*sourceUV.x+c*sourceUV.y)+_WoodUV.zw;
     float2 uvDx=ddx(sourceUV),uvDy=ddy(sourceUV);
     float grain=clamp(dot(tex2Dgrad(_WoodDiffuse,sourceUV,uvDx,uvDy).rgb,float3(.2126,.7152,.0722))/_WoodSignal.x,_WoodSignal.y,_WoodSignal.z);
     colour.rgb=lerp(colour.rgb,tex2D(_WoodHigh,input.uv).rgb*_Color.rgb,grain);
    #endif
    return float4(colour.rgb,1);
   }
   ENDCG
  }
 }
}
