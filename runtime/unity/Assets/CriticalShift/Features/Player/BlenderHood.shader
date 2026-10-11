Shader "CriticalShift/BlenderHood"
{
    Properties
    {
        _Color ("Tint", Color) = (1,1,1,1)
        _MainTex ("Source colour", 2D) = "white" {}
        _BumpMap ("Source normal", 2D) = "bump" {}
        _BumpScale ("Normal strength", Float) = 1
        _MetallicGlossMap ("Metallic / smoothness", 2D) = "white" {}
        _Metallic ("Metallic", Range(0,1)) = 0
        _DielectricSpecular ("Source dielectric reflectivity", Range(0,1)) = 0.04
        _Glossiness ("Smoothness", Range(0,1)) = 0.5
        _GlossMapScale ("Smoothness scale", Range(0,1)) = 1
        _MetallicFromMap ("Use metallic map", Float) = 1
        _SmoothnessFromMap ("Use smoothness map", Float) = 1
        _VertexOcclusion ("Use source geometry occlusion", Float) = 0
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
        #pragma surface surf BlenderSurface fullforwardshadows addshadow
        #pragma shader_feature_local _NORMALMAP
        #pragma shader_feature_local _METALLICGLOSSMAP
        #pragma shader_feature_local _EMISSION
        #include "UnityStandardUtils.cginc"
        #include "UnityPBSLighting.cginc"
        sampler2D _MainTex, _BumpMap, _MetallicGlossMap, _EmissionMap;
        fixed4 _Color;
        half _BumpScale, _Metallic, _DielectricSpecular, _Glossiness, _GlossMapScale, _MetallicFromMap, _SmoothnessFromMap, _VertexOcclusion;
        half4 _EmissionColor;
        struct Input { float2 uv_MainTex; float facing : VFACE; float4 colour : COLOR; };
        half4 LightingBlenderSurface(SurfaceOutputStandardSpecular surface, half3 viewDir, UnityGI gi)
        { return LightingStandardSpecular(surface,viewDir,gi); }
        void LightingBlenderSurface_GI(SurfaceOutputStandardSpecular surface, UnityGIInput data, inout UnityGI gi)
        {
            LightingStandardSpecular_GI(surface,data,gi);
            // Colour-dependent multiple-bounce AO approximates light reflected
            // inside the yellow hood. AO=1 is exactly the existing room shader.
            half ao=surface.Occlusion;
            half3 a=2.0404h*surface.Albedo-0.3324h;
            half3 b=-4.7951h*surface.Albedo+0.6417h;
            half3 c=2.7552h*surface.Albedo+0.6903h;
            half3 bounce=saturate(max(ao,((a*ao+b)*ao+c)*ao));
            gi.indirect.diffuse*=bounce/max(ao,0.0001h);
        }
        void surf(Input input, inout SurfaceOutputStandardSpecular output)
        {
            fixed4 colour=tex2D(_MainTex,input.uv_MainTex)*_Color;
            output.Alpha=colour.a;
            half metallic;
            #if defined(_METALLICGLOSSMAP)
                half4 metal=tex2D(_MetallicGlossMap,input.uv_MainTex);
                metallic=lerp(_Metallic,metal.r,_MetallicFromMap);
                output.Smoothness=lerp(_Glossiness,metal.a*_GlossMapScale,_SmoothnessFromMap);
            #else
                metallic=_Metallic; output.Smoothness=_Glossiness;
            #endif
            output.Specular=lerp(half3(_DielectricSpecular,_DielectricSpecular,_DielectricSpecular),colour.rgb,metallic);
            // StandardSpecular applies (1-max(specular)) itself. Retain the
            // metallic workflow's diffuse energy while replacing dielectric F0.
            half reflectivity=max(max(output.Specular.r,output.Specular.g),output.Specular.b);
            output.Albedo=colour.rgb*(1-metallic)*(1-_DielectricSpecular)/max(1-reflectivity,0.0001h);
            half3 normal=half3(0,0,1);
            #if defined(_NORMALMAP)
                normal=UnpackScaleNormal(tex2D(_BumpMap,input.uv_MainTex),_BumpScale);
            #endif
            output.Normal=normal*(input.facing>=0 ? 1 : -1);
            output.Occlusion=lerp(1,input.facing>=0 ? input.colour.r : input.colour.g,_VertexOcclusion);
            #if defined(_EMISSION)
                output.Emission=tex2D(_EmissionMap,input.uv_MainTex).rgb*_EmissionColor.rgb;
            #endif
        }
        ENDCG
    }
    FallBack "Diffuse"
}
