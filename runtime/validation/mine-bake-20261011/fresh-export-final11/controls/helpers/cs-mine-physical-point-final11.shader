Shader "CriticalShift/DiagnosticPhysicalPoint" { Properties { _Color("Albedo",Color)=(.461,.461,.461,1) _DielectricSpecular("F0",Float)=0 _Metallic("Metallic",Float)=0 _Glossiness("Smoothness",Float)=.5 } SubShader { Tags {"RenderType"="Opaque"} CGPROGRAM
#pragma target 3.0
#pragma surface surf StandardSpecular fullforwardshadows addshadow
#include "CsMinePhysicalPointFinal11.cginc"
fixed4 _Color;struct Input{float2 uv_MainTex;};void surf(Input i,inout SurfaceOutputStandardSpecular o){o.Albedo=_Color.rgb;o.Specular=0;o.Smoothness=0;o.Alpha=1;}
ENDCG } }