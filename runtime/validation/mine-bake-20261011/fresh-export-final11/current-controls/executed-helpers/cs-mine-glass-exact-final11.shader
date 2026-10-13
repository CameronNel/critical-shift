Shader "CriticalShift/DiagnosticGlassExact" {
 Properties { _Color("Source glass tint",Color)=(.82,.92,.95,1) _SourceIOR("Source IOR",Float)=1.45 _Glossiness("Source smoothness",Float)=.97 }
 SubShader {
  Tags {"RenderType"="Transparent" "Queue"="Transparent"} Cull Off ZWrite Off
  CGINCLUDE
  #include "UnityCG.cginc"
  float4 _Color;float _SourceIOR,_Glossiness;
  float ExactFresnel(float cosine,float eta) {
   cosine=saturate(abs(cosine));float sin2=(1-cosine*cosine)/(eta*eta);
   if(sin2>=1)return 1;
   float transmitted=sqrt(max(0,1-sin2));
   float rs=(cosine-eta*transmitted)/max(cosine+eta*transmitted,1e-8);
   float rp=(eta*cosine-transmitted)/max(eta*cosine+transmitted,1e-8);
   return .5*(rs*rs+rp*rp);
  }
  float3 GlassView(float3 position) {return normalize(lerp(UnityWorldSpaceViewDir(position),UNITY_MATRIX_V[2].xyz,unity_OrthoParams.w));}
  ENDCG
  // Bounded thin-interface transmission prototype: preserve RGB destination
  // transmission separately from additive reflection. Actual source controls
  // must establish this model; thickness/refraction/sorting remain unapproved.
  Pass {
   Blend DstColor Zero
   CGPROGRAM
   #pragma vertex vert
   #pragma fragment frag
   #pragma target 3.0
   struct V {float4 position:SV_POSITION;float3 normal:TEXCOORD0;float3 world:TEXCOORD1;};
   V vert(appdata_base input){V o;o.position=UnityObjectToClipPos(input.vertex);o.normal=UnityObjectToWorldNormal(input.normal);o.world=mul(unity_ObjectToWorld,input.vertex).xyz;return o;}
   float4 frag(V input,float facing:VFACE):SV_Target {float eta=facing>=0?_SourceIOR:rcp(_SourceIOR);float f=ExactFresnel(dot(normalize(input.normal),GlassView(input.world)),eta);return float4(_Color.rgb*(1-f),1);}
   ENDCG
  }
  CGPROGRAM
  #pragma target 3.0
  #pragma surface surf DiagnosticGlass alpha:premul fullforwardshadows
  #include "UnityPBSLighting.cginc"
  struct Input {float facing:VFACE;};
  half4 LightingDiagnosticGlass(SurfaceOutputStandardSpecular surface,float3 viewDir,UnityGI gi) {
   viewDir=normalize(lerp(viewDir,UNITY_MATRIX_V[2].xyz,unity_OrthoParams.w));
   float eta=surface.Alpha>=0?_SourceIOR:rcp(_SourceIOR);
   float f=ExactFresnel(dot(normalize(surface.Normal),viewDir),eta);
   return half4(_Color.rgb*f*gi.indirect.specular,0);
  }
  void LightingDiagnosticGlass_GI(SurfaceOutputStandardSpecular surface,UnityGIInput data,inout UnityGI gi){
   data.worldViewDir=normalize(lerp(data.worldViewDir,UNITY_MATRIX_V[2].xyz,unity_OrthoParams.w));
   Unity_GlossyEnvironmentData g=UnityGlossyEnvironmentSetup(surface.Smoothness,data.worldViewDir,surface.Normal,surface.Specular);
   gi=UnityGlobalIllumination(data,1,surface.Normal,g);
  }
  void surf(Input input,inout SurfaceOutputStandardSpecular surface){surface.Albedo=0;surface.Specular=_Color.rgb;surface.Smoothness=_Glossiness;surface.Alpha=input.facing>=0?1:-1;surface.Occlusion=1;}
  ENDCG
 }
}
