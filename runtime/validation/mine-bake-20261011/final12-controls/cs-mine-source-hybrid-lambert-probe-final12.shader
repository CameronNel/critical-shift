Shader "CriticalShift/DiagnosticSourceHybridLambertProbeFinal12"
{
 Properties {
  _MainTex("Source colour",2D)="white"{}
  _BumpMap("Source tangent normal",2D)="bump"{}
  _Roughness("Source roughness",2D)="white"{}
  _MetallicMap("Source metallic",2D)="black"{}
  _SourceIndirect("Source colour-included indirect radiance",2D)="black"{}
  _SourceNonExplicitDirect("Source colour-included non-explicit direct",2D)="black"{}
  _SourceAllDirect("Source direct diagnostic reference",2D)="black"{}
  _DielectricSpecular("Source F0",Float)=.02
  _DiagnosticMode("Diagnostic mode",Float)=0
  _CsLambertDiffuse("Lambert direct control",Float)=0
 }
 SubShader {
  Tags {"RenderType"="Opaque"} Cull Off
  CGPROGRAM
  #pragma target 3.0
  #pragma surface surf SourceHybrid fullforwardshadows addshadow
  #include "UnityPBSLighting.cginc"
  #include "BlenderPointLighting.cginc"
  sampler2D _MainTex,_BumpMap,_Roughness,_MetallicMap;
  sampler2D _SourceIndirect,_SourceNonExplicitDirect,_SourceAllDirect;
  float _DielectricSpecular,_DiagnosticMode,_CsLambertDiffuse;
  struct Input {float2 uv_MainTex;float facing:VFACE;};
  half4 LightingSourceHybrid(SurfaceOutputStandardSpecular s,half3 viewDir,UnityGI gi)
  {
   half4 total=LightingStandardSpecular(s,viewDir,gi);
   float3 h=Unity_SafeNormalize(gi.light.dir+viewDir);
   float nv=abs(dot(s.Normal,viewDir)),nl=saturate(dot(s.Normal,gi.light.dir)),lh=saturate(dot(gi.light.dir,h));
   half3 direct=s.Albedo*(1-SpecularStrength(s.Specular))*gi.light.color*(DisneyDiffuse(nv,nl,lh,1-s.Smoothness)*nl);
   half3 lambert=s.Albedo*(1-SpecularStrength(s.Specular))*gi.light.color*nl;
   half3 chosenDirect=lerp(direct,lambert,_CsLambertDiffuse);
   half3 rgb=_DiagnosticMode<.5 ? total.rgb-direct+chosenDirect : _DiagnosticMode<1.5 ? chosenDirect : _DiagnosticMode<2.5 ? total.rgb-direct : half3(0,0,0);
   #if !defined(UNITY_PASS_FORWARDADD)
   if(_DiagnosticMode>5.5 && _DiagnosticMode<6.5)rgb=normalize(s.Normal)*.5+.5;
   #endif
   return half4(rgb,1);
  }
  void LightingSourceHybrid_GI(SurfaceOutputStandardSpecular s,UnityGIInput data,inout UnityGI gi)
  {
   LightingStandardSpecular_GI(s,data,gi);
   // Source fields already include diffuse colour. Remove native SH/lightmap
   // diffuse only; retain independent native direct lighting and specular.
   gi.indirect.diffuse=0;
  }
  void surf(Input i,inout SurfaceOutputStandardSpecular s)
  {
   half3 colour=tex2D(_MainTex,i.uv_MainTex).rgb;
   half metallic=tex2D(_MetallicMap,i.uv_MainTex).r;
   s.Specular=lerp(_DielectricSpecular.xxx,colour,metallic);
   half reflectivity=max(max(s.Specular.r,s.Specular.g),s.Specular.b);
   s.Albedo=colour*(1-metallic)*(1-_DielectricSpecular)/max(1-reflectivity,.0001h);
   s.Smoothness=1-tex2D(_Roughness,i.uv_MainTex).r;
   s.Normal=normalize(tex2D(_BumpMap,i.uv_MainTex).rgb*2-1)*(i.facing>=0 ? 1:-1);
   s.Alpha=1;
   if(_DiagnosticMode<.5 || (_DiagnosticMode>2.5 && _DiagnosticMode<3.5))
    s.Emission=tex2D(_SourceIndirect,i.uv_MainTex).rgb+tex2D(_SourceNonExplicitDirect,i.uv_MainTex).rgb;
   else if(_DiagnosticMode>3.5 && _DiagnosticMode<4.5)
    s.Emission=tex2D(_SourceIndirect,i.uv_MainTex).rgb+tex2D(_SourceAllDirect,i.uv_MainTex).rgb;
   else if(_DiagnosticMode>4.5 && _DiagnosticMode<5.5)s.Emission=1;
   else if(_DiagnosticMode>6.5)s.Emission=colour;
  }
  ENDCG
 }
}
