Shader "CriticalShift/BlenderSurface"
{
    Properties
    {
        _Color ("Tint", Color) = (1,1,1,1)
        _MainTex ("Source colour", 2D) = "white" {}
        _BumpMap ("Source normal", 2D) = "bump" {}
        _BumpScale ("Normal strength", Float) = 1
        _MetallicGlossMap ("Metallic / smoothness", 2D) = "white" {}
        _Metallic ("Metallic", Range(0,1)) = 0
        _Glossiness ("Smoothness", Range(0,1)) = 0.5
        _GlossMapScale ("Smoothness scale", Range(0,1)) = 1
        _MetallicFromMap ("Use metallic map", Float) = 1
        _SmoothnessFromMap ("Use smoothness map", Float) = 1
        _EmissionMap ("Source emission", 2D) = "white" {}
        [HDR] _EmissionColor ("Emission", Color) = (0,0,0,1)
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 300
        // Cycles shades both sides and reverses the shading normal for back faces.
        Cull Off
        CGPROGRAM
        #pragma target 3.0
        #pragma surface surf Standard fullforwardshadows addshadow
        #pragma shader_feature_local _NORMALMAP
        #pragma shader_feature_local _METALLICGLOSSMAP
        #pragma shader_feature_local _EMISSION
        #include "UnityStandardUtils.cginc"
        sampler2D _MainTex, _BumpMap, _MetallicGlossMap, _EmissionMap;
        fixed4 _Color;
        half _BumpScale, _Metallic, _Glossiness, _GlossMapScale, _MetallicFromMap, _SmoothnessFromMap;
        half4 _EmissionColor;
        struct Input { float2 uv_MainTex; float facing : VFACE; };
        void surf(Input input, inout SurfaceOutputStandard output)
        {
            fixed4 colour=tex2D(_MainTex,input.uv_MainTex)*_Color;
            output.Albedo=colour.rgb; output.Alpha=colour.a;
            #if defined(_METALLICGLOSSMAP)
                half4 metal=tex2D(_MetallicGlossMap,input.uv_MainTex);
                output.Metallic=lerp(_Metallic,metal.r,_MetallicFromMap);
                output.Smoothness=lerp(_Glossiness,metal.a*_GlossMapScale,_SmoothnessFromMap);
            #else
                output.Metallic=_Metallic; output.Smoothness=_Glossiness;
            #endif
            half3 normal=half3(0,0,1);
            #if defined(_NORMALMAP)
                normal=UnpackScaleNormal(tex2D(_BumpMap,input.uv_MainTex),_BumpScale);
            #endif
            output.Normal=normal*(input.facing>=0 ? 1 : -1);
            #if defined(_EMISSION)
                output.Emission=tex2D(_EmissionMap,input.uv_MainTex).rgb*_EmissionColor.rgb;
            #endif
        }
        ENDCG
    }
    FallBack "Diffuse"
}
