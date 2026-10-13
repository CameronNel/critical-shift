Shader "CriticalShift/BlenderThinVisor"
{
    Properties
    {
        _ReflectionMap ("Source reflection falloff (B)", 2D) = "white" {}
        _ReflectionIOR ("Source Fresnel IOR", Float) = 1.45
        _ReflectionColor ("Source glossy colour", Color) = (0.8,0.8,0.8,1)
        _Glossiness ("Source glossy smoothness", Range(0,1)) = 0.935
    }
    SubShader
    {
        Tags { "RenderType"="Transparent" "Queue"="Transparent" "IgnoreProjector"="True" }
        Cull Off
        CGPROGRAM
        #pragma target 3.0
        #pragma surface surf ThinVisor alpha:premul fullforwardshadows
        #include "UnityPBSLighting.cginc"
        #include "BlenderPointLighting.cginc"
        sampler2D _ReflectionMap;
        half _ReflectionIOR, _Glossiness;
        half4 _ReflectionColor;
        struct Input { float2 uv_ReflectionMap; float3 viewDir; float facing : VFACE; };
        half Fresnel(half cosine, half ior)
        {
            half transmitted=sqrt(max(0,1-(1-cosine*cosine)/(ior*ior)));
            half parallel=(ior*cosine-transmitted)/max(ior*cosine+transmitted,0.0001h);
            half perpendicular=(cosine-ior*transmitted)/max(cosine+ior*transmitted,0.0001h);
            return saturate((parallel*parallel+perpendicular*perpendicular)*0.5h);
        }
        void surf(Input input, inout SurfaceOutputStandardSpecular output)
        {
            // A clear sheet plus a spatially weighted Fresnel glossy lobe. No
            // diffuse paint or refraction: the source keeps the face readable.
            output.Albedo=0; output.Specular=1; output.Smoothness=_Glossiness;
            output.Normal=half3(0,0,input.facing>=0 ? 1 : -1);
            output.Occlusion=1;
            output.Alpha=Fresnel(abs(normalize(input.viewDir).z),_ReflectionIOR)*tex2D(_ReflectionMap,input.uv_ReflectionMap).b;
        }
        half4 LightingThinVisor(SurfaceOutputStandardSpecular surface, half3 viewDir, UnityGI gi)
        {
            half4 colour=LightingStandardSpecular(surface,viewDir,gi);
            colour.rgb*=_ReflectionColor.rgb*surface.Alpha;
            colour.a=surface.Alpha;
            return colour;
        }
        void LightingThinVisor_GI(SurfaceOutputStandardSpecular surface, UnityGIInput data, inout UnityGI gi)
        { LightingStandardSpecular_GI(surface,data,gi); }
        ENDCG
    }
    FallBack Off
}
